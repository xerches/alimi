"""Control and requirement status, computed from test results and evidence. Never typed in.

Rules (the same ones config/controls.yaml states at the top):
  A control with tests is Ok when every linked test that ran passed. Attestation tests
  (EDR, backups, incident response) count as passed while a current attestation is on file.
  A control without tests is Ok when it has evidence that has not passed its renewal date.
  A requirement takes the worst status among its controls.

Every query here runs inside org_scope, so "the results" always means this organization's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import Connection, text

# Worst first. The label is what the page shows.
STATUSES: dict[str, str] = {
    "failing": "Failing",
    "could_not_test": "Could not test",
    "evidence_expired": "Evidence expired",
    "needs_evidence": "Needs evidence",
    "not_tested": "Not tested yet",
    "ok": "Ok",
}
_RANK = {key: i for i, key in enumerate(STATUSES)}


def worst(statuses: list[str]) -> str:
    return min(statuses, key=_RANK.__getitem__) if statuses else "not_tested"


@dataclass
class ControlStatus:
    id: str
    name: str
    domain: str
    frequency: str
    status: str
    tests: list[dict] = field(default_factory=list)      # latest result per linked test that ran here
    evidence: list[dict] = field(default_factory=list)

    @property
    def label(self) -> str:
        return STATUSES[self.status]


def latest_results(conn: Connection) -> dict[str, dict]:
    rows = conn.execute(
        text(
            "SELECT DISTINCT ON (r.test_id) r.test_id, r.status, r.summary, r.collected_at, r.check_version, "
            "t.title, t.kind, t.severity "
            "FROM test_results r JOIN tests t ON t.id = r.test_id "
            "ORDER BY r.test_id, r.collected_at DESC"
        )
    ).mappings()
    return {row["test_id"]: dict(row) for row in rows}


def control_statuses(conn: Connection, today: date | None = None) -> list[ControlStatus]:
    today = today or date.today()
    results = latest_results(conn)
    links: dict[str, list[str]] = {}
    for control_id, test_id in conn.execute(text("SELECT control_id, test_id FROM control_tests")):
        links.setdefault(control_id, []).append(test_id)
    evidence: dict[str, list[dict]] = {}
    for row in conn.execute(
        text("SELECT id, control_id, kind, evidence_type, title, collected_on, renews_on FROM evidence ORDER BY collected_on DESC")
    ).mappings():
        item = dict(row)
        item["current"] = item["renews_on"] is None or item["renews_on"] >= today
        evidence.setdefault(row["control_id"], []).append(item)

    out: list[ControlStatus] = []
    for ctl in conn.execute(text("SELECT id, name, domain, frequency FROM controls ORDER BY id")).mappings():
        ctl_evidence = evidence.get(ctl["id"], [])
        has_current = any(e["current"] for e in ctl_evidence)
        ran = [results[t] for t in links.get(ctl["id"], []) if t in results]
        parts: list[str] = []
        for result in ran:
            if result["kind"] == "attestation":
                if has_current:
                    parts.append("ok")
                elif ctl_evidence:
                    parts.append("evidence_expired")
                else:
                    parts.append("needs_evidence")
            elif result["status"] == "fail":
                parts.append("failing")
            elif result["status"] == "error":
                parts.append("could_not_test")
            else:  # pass or not_applicable
                parts.append("ok")
        if ran:
            status = worst(parts)
        elif links.get(ctl["id"]):
            # Tests exist, but none applies to the connected platform yet; evidence can still carry it.
            status = "ok" if has_current else "not_tested"
        elif has_current:
            status = "ok"
        elif ctl_evidence:
            status = "evidence_expired"
        else:
            status = "needs_evidence"
        out.append(
            ControlStatus(
                id=ctl["id"],
                name=ctl["name"],
                domain=ctl["domain"],
                frequency=ctl["frequency"],
                status=status,
                tests=ran,
                evidence=ctl_evidence,
            )
        )
    return out


def requirement_statuses(conn: Connection, framework_id: str, controls: list[ControlStatus]) -> list[dict]:
    by_id = {c.id: c for c in controls}
    links: dict[str, list[str]] = {}
    for req_id, control_id in conn.execute(
        text(
            "SELECT cr.requirement_id, cr.control_id FROM control_requirements cr "
            "JOIN requirements r ON r.id = cr.requirement_id WHERE r.framework_id = :fw"
        ),
        {"fw": framework_id},
    ):
        links.setdefault(req_id, []).append(control_id)
    out = []
    for req in conn.execute(
        text("SELECT id, code, summary FROM requirements WHERE framework_id = :fw ORDER BY position, code"),
        {"fw": framework_id},
    ).mappings():
        req_controls = [by_id[c] for c in sorted(links.get(req["id"], [])) if c in by_id]
        status = worst([c.status for c in req_controls]) if req_controls else "not_tested"
        out.append({**req, "status": status, "label": STATUSES[status], "controls": req_controls})
    return out
