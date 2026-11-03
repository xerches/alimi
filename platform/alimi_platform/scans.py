"""Run the scanner for one integration and store what it found.

The scanner is imported as a library (alimi_scanner), exactly as prompt 3 intended: the
platform picks a connector, calls run_checks, and turns each Finding into a TestResult with
the raw evidence the check read, the rule in plain English, the criterion IDs and the version
of the check. Mock mode is the only mode in 12a; a live integration is refused here as well
as at startup, so nothing reaches a real tenant by accident.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from alimi_scanner import __version__ as SCANNER_VERSION
from alimi_scanner.catalog import load_catalog
from alimi_scanner.connectors.mock import MockConnector
from alimi_scanner.engine import run_checks
from alimi_scanner.schema import Platform, TenantInfo
from sqlalchemy import Connection, text

from .audit import record
from .catalog import check_version
from .config import Settings
from .crypto import TokenBox


class ScanRefused(RuntimeError):
    pass


def run_scan(conn: Connection, settings: Settings, integration_id: UUID | str, actor_user_id: UUID | str | None) -> UUID:
    """Scan one integration of the organization the connection is scoped to. Returns the run id."""
    row = conn.execute(
        text(
            "SELECT i.id, i.organization_id, i.platform, i.mode, i.fixture, i.token_ciphertext, o.name AS org_name "
            "FROM integrations i JOIN organizations o ON o.id = i.organization_id WHERE i.id = :id"
        ),
        {"id": str(integration_id)},
    ).mappings().first()
    if row is None:
        # Either it does not exist or it belongs to another organization; RLS makes those look the same.
        raise LookupError("integration not found")
    if row["mode"] != "mock" or not settings.is_mock:
        raise ScanRefused("Only mock integrations can be scanned until real login and the customer-data gate.")

    if row["token_ciphertext"] is not None:
        # Prove the stored token decrypts with the current key, the same step a live connector needs.
        # The value itself is not used in mock mode and is never logged.
        TokenBox(settings.token_key).decrypt(row["token_ciphertext"])

    catalog = load_catalog(settings.repo_root / "config" / "checks.yaml")
    connector = MockConnector(Platform(row["platform"]), fixture=row["fixture"] or "pass")
    snapshot = connector.fetch()
    result = run_checks(
        snapshot,
        catalog,
        Platform(row["platform"]),
        TenantInfo(display_name=row["org_name"], source=connector.source),
    )

    control_map: dict[str, list[str]] = {}
    for test_id, control_id in conn.execute(text("SELECT test_id, control_id FROM control_tests")):
        control_map.setdefault(test_id, []).append(control_id)
    criteria_map: dict[str, list[str]] = {}
    for control_id, requirement_id in conn.execute(text("SELECT control_id, requirement_id FROM control_requirements")):
        criteria_map.setdefault(control_id, []).append(requirement_id)

    org_id = row["organization_id"]
    run_id = uuid4()
    started = datetime.now(timezone.utc)
    conn.execute(
        text(
            "INSERT INTO scan_runs (id, organization_id, integration_id, started_by, started_at, scanner_version, source) "
            "VALUES (:id, :org, :integration, :actor, :started, :version, :source)"
        ),
        {
            "id": run_id,
            "org": org_id,
            "integration": row["id"],
            "actor": str(actor_user_id) if actor_user_id else None,
            "started": started,
            "version": SCANNER_VERSION,
            "source": connector.source,
        },
    )

    rows = []
    for finding in result.findings:
        definition = catalog.by_id(finding.check_id)
        controls = sorted(control_map.get(finding.check_id, []))
        criteria = {f"insurer:{finding.insurer_question}"}
        for control_id in controls:
            criteria.update(criteria_map.get(control_id, []))
        rows.append(
            {
                "org": org_id,
                "run": run_id,
                "test": finding.check_id,
                "controls": controls,
                "status": finding.status.value,
                "summary": finding.summary,
                "evidence": json.dumps(finding.evidence, default=str),
                "rule": definition.pass_when or definition.evidence or definition.explain,
                "criteria": sorted(criteria),
                "version": check_version(definition),
                "collected": result.collected_at,
            }
        )
    conn.execute(
        text(
            "INSERT INTO test_results (organization_id, scan_run_id, test_id, control_ids, status, summary, "
            "raw_evidence, rule, criterion_ids, check_version, collected_at) VALUES "
            "(:org, :run, :test, :controls, :status, :summary, CAST(:evidence AS jsonb), :rule, :criteria, :version, :collected)"
        ),
        rows,
    )

    finished = datetime.now(timezone.utc)
    conn.execute(
        text("UPDATE scan_runs SET finished_at = :finished, score_percent = :score WHERE id = :id"),
        {"finished": finished, "score": result.summary.score_percent, "id": run_id},
    )
    conn.execute(
        text("UPDATE integrations SET last_sync_at = :finished, last_sync_status = 'ok' WHERE id = :id"),
        {"finished": finished, "id": row["id"]},
    )
    record(
        conn,
        org_id,
        actor_user_id,
        "scan.run",
        f"integration:{row['id']}",
        {
            "run_id": str(run_id),
            "source": connector.source,
            "passed": result.summary.passed,
            "failed": result.summary.failed,
            "score_percent": result.summary.score_percent,
        },
    )
    return run_id
