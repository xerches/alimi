"""Loads Alimi's own catalog from the repo into the reference tables.

Sources, all already in the repo and shared with the site, the demo and the scanner:
  config/frameworks.yaml       the 23-entry framework catalog (IDs, names, our summaries)
  policies/requirements.yaml   criterion IDs with our own one-line summaries (never framework text)
  config/controls.yaml         40 controls, the requirement IDs each satisfies and the tests behind it
  config/checks.yaml           the scanner checks, which become Tests

The first framework built end to end is the insurer questionnaire: its requirements are the
underwriting questions (mfa, admin_access, ...), and controls map to them through the
`insurer:` entries in controls.yaml.

Re-running the sync updates rows in place (upsert), so editing a YAML file and restarting
the app is enough to change the catalog.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml
from alimi_scanner import __version__ as SCANNER_VERSION
from alimi_scanner.catalog import load_catalog
from alimi_scanner.schema import CheckDefinition
from sqlalchemy import Connection, text


def check_version(definition: CheckDefinition) -> str:
    """Scanner version plus a short digest of the check's definition in checks.yaml.

    A per-check version number arrives with the changelog in 12c; until then the digest
    changes whenever the rule, severity or wording changes, which is what an auditor asks.
    """
    digest = hashlib.sha256(json.dumps(definition.model_dump(mode="json"), sort_keys=True).encode()).hexdigest()
    return f"{SCANNER_VERSION}+{digest[:12]}"


@dataclass
class CatalogData:
    frameworks: list[dict] = field(default_factory=list)
    requirements: dict[str, dict] = field(default_factory=dict)  # id -> row
    controls: list[dict] = field(default_factory=list)
    control_requirements: set[tuple[str, str]] = field(default_factory=set)
    tests: list[dict] = field(default_factory=list)
    control_tests: set[tuple[str, str]] = field(default_factory=set)


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load(repo_root: Path) -> CatalogData:
    data = CatalogData()

    frameworks_yaml = _read_yaml(repo_root / "config" / "frameworks.yaml")["frameworks"]
    for position, fw in enumerate(frameworks_yaml):
        data.frameworks.append(
            {
                "id": fw["id"],
                "name": fw["name"],
                "short_name": fw.get("short", fw["name"]),
                "summary": fw.get("summary", ""),
                "mapped": bool(fw.get("mapped", False)),
                "always_included": bool(fw.get("always_included", False)),
                "position": position,
            }
        )
    known_frameworks = {fw["id"] for fw in data.frameworks}

    summaries = _read_yaml(repo_root / "policies" / "requirements.yaml")["frameworks"]
    for fw_id, fw in summaries.items():
        if fw_id not in known_frameworks:
            continue
        for position, (code, summary) in enumerate(fw.get("requirements", {}).items()):
            req_id = f"{fw_id}:{code}"
            data.requirements[req_id] = {
                "id": req_id,
                "framework_id": fw_id,
                "code": str(code),
                "summary": summary,
                "position": position,
            }

    scanner_catalog = load_catalog(repo_root / "config" / "checks.yaml")
    for definition in scanner_catalog.checks:
        data.tests.append(
            {
                "id": definition.id,
                "platform": definition.platform.value,
                "kind": definition.kind.value,
                "title": definition.title,
                "severity": definition.severity.value,
                "insurer_question": definition.insurer_question,
                "rule": definition.pass_when or definition.evidence or definition.explain,
                "explain": definition.explain,
                "remediation": definition.remediation,
                "version": check_version(definition),
            }
        )
    known_tests = {t["id"] for t in data.tests}

    controls_yaml = _read_yaml(repo_root / "config" / "controls.yaml")["controls"]
    for ctl in controls_yaml:
        data.controls.append(
            {
                "id": ctl["id"],
                "name": ctl["name"],
                "domain": ctl["domain"],
                "description": ctl["description"],
                "implementation": ctl.get("implementation"),
                "owner_role": ctl.get("owner_role"),
                "frequency": ctl["frequency"],
                "evidence_types": list(ctl.get("evidence", [])),
            }
        )
        for fw_id, codes in (ctl.get("requirements") or {}).items():
            if fw_id not in known_frameworks:
                continue
            for code in codes:
                req_id = f"{fw_id}:{code}"
                # A control may cite an ID we have not summarised yet; keep the ID, leave the summary empty.
                data.requirements.setdefault(
                    req_id,
                    {"id": req_id, "framework_id": fw_id, "code": str(code), "summary": None, "position": 1000},
                )
                data.control_requirements.add((ctl["id"], req_id))
        for test_id in ctl.get("tests") or []:
            if test_id not in known_tests:
                raise ValueError(f"{ctl['id']} lists test {test_id}, which is not in config/checks.yaml")
            data.control_tests.add((ctl["id"], test_id))

    return data


@lru_cache(maxsize=4)
def domain_labels(repo_root: Path) -> dict[str, str]:
    """Plain-English names of the control domains, from the top of controls.yaml."""
    return dict(_read_yaml(repo_root / "config" / "controls.yaml").get("domains", {}))


def _upsert(conn: Connection, table: str, key: str, rows: list[dict]) -> None:
    if not rows:
        return
    cols = list(rows[0])
    updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != key)
    sql = (
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)}) "
        f"ON CONFLICT ({key}) DO UPDATE SET {updates}"
    )
    conn.execute(text(sql), rows)


def sync(conn: Connection, data: CatalogData) -> None:
    """Write the catalog into the reference tables. Runs as the table owner."""
    _upsert(conn, "frameworks", "id", data.frameworks)
    _upsert(conn, "requirements", "id", list(data.requirements.values()))
    _upsert(conn, "controls", "id", data.controls)
    _upsert(conn, "tests", "id", data.tests)
    # Link tables are small: replace them wholesale so a removed mapping disappears.
    conn.execute(text("DELETE FROM control_requirements"))
    conn.execute(text("DELETE FROM control_tests"))
    if data.control_requirements:
        conn.execute(
            text("INSERT INTO control_requirements (control_id, requirement_id) VALUES (:c, :r)"),
            [{"c": c, "r": r} for c, r in sorted(data.control_requirements)],
        )
    if data.control_tests:
        conn.execute(
            text("INSERT INTO control_tests (control_id, test_id) VALUES (:c, :t)"),
            [{"c": c, "t": t} for c, t in sorted(data.control_tests)],
        )
