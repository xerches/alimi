"""Mock scans through the real scanner, stored with their evidence."""

from __future__ import annotations

from dataclasses import replace

import pytest
from sqlalchemy import text

from alimi_platform.db import org_scope
from alimi_platform.scans import ScanRefused, run_scan
from alimi_platform.status import control_statuses, requirement_statuses


def test_seed_ran_one_scan_per_org(app_engine, orgs):
    for org in orgs.values():
        with org_scope(app_engine, org.id) as conn:
            assert conn.execute(text("SELECT count(*) FROM scan_runs")).scalar() >= 1


def test_results_carry_evidence_rule_criteria_and_version(app_engine, orgs):
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        row = conn.execute(
            text("SELECT * FROM test_results WHERE test_id = 'm365.mfa.coverage' ORDER BY collected_at DESC LIMIT 1")
        ).mappings().one()
    assert row["status"] == "fail"  # the "fail" fixture trips every check
    assert row["raw_evidence"], "the raw evidence the check read is stored"
    assert row["rule"].startswith("100%")
    assert "insurer:mfa" in row["criterion_ids"]
    assert "CTL-09" in row["control_ids"]
    assert any(c.startswith("soc2:") for c in row["criterion_ids"])
    assert row["check_version"].count("+") == 1


def test_alimi_org_runs_on_the_passing_fixture(app_engine, orgs):
    with org_scope(app_engine, orgs["alimi"].id) as conn:
        statuses = {r[0] for r in conn.execute(text("SELECT DISTINCT status FROM test_results"))}
    assert "fail" not in statuses


def test_google_org_gets_google_checks_only(app_engine, orgs):
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        tests = {r[0] for r in conn.execute(text("SELECT DISTINCT test_id FROM test_results"))}
    assert tests and not any(t.startswith("m365.") for t in tests)


def test_on_demand_scan_adds_a_run_and_an_audit_entry(app_engine, settings, orgs):
    org = orgs["harbor-dental"]
    with org_scope(app_engine, org.id, org.users[0].id) as conn:
        before = conn.execute(text("SELECT count(*) FROM scan_runs")).scalar()
        run_scan(conn, settings, org.integration_id, org.users[0].id)
        assert conn.execute(text("SELECT count(*) FROM scan_runs")).scalar() == before + 1
        entry = conn.execute(text("SELECT action, actor_user_id FROM audit_log ORDER BY at DESC LIMIT 1")).one()
    assert entry.action == "scan.run" and entry.actor_user_id == org.users[0].id


def test_cannot_scan_another_orgs_integration(app_engine, settings, orgs):
    with pytest.raises(LookupError):
        with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
            run_scan(conn, settings, orgs["harbor-dental"].integration_id, None)


def test_live_integrations_are_refused(app_engine, settings, orgs):
    with pytest.raises(ScanRefused):
        with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
            conn.execute(text("UPDATE integrations SET mode = 'live'"))
            run_scan(conn, settings, orgs["saltmarsh"].integration_id, None)
    # The transaction rolled back: the integration is still mock.
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        assert conn.execute(text("SELECT mode FROM integrations")).scalar() == "mock"


def test_wrong_token_key_stops_the_scan(app_engine, settings, orgs):
    from cryptography.fernet import Fernet

    other = replace(settings, token_key=Fernet.generate_key().decode())
    with pytest.raises(ValueError, match="could not be decrypted"):
        with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
            run_scan(conn, other, orgs["saltmarsh"].integration_id, None)


def test_control_status_follows_results_and_evidence(app_engine, orgs):
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        by_id = {c.id: c for c in control_statuses(conn)}
    assert by_id["CTL-09"].status == "failing"            # MFA test failed
    assert by_id["CTL-01"].status == "ok"                 # policy attestation current
    assert by_id["CTL-23"].status == "ok"                 # EDR attestation current
    assert by_id["CTL-31"].status == "evidence_expired"   # restore test past renewal
    assert by_id["CTL-33"].status == "needs_evidence"     # IR plan: attestation test, nothing on file


def test_alimi_passes_its_tested_controls(app_engine, orgs):
    with org_scope(app_engine, orgs["alimi"].id) as conn:
        by_id = {c.id: c for c in control_statuses(conn)}
    assert by_id["CTL-09"].status == "ok"


def test_insurer_requirements_roll_up_worst_status(app_engine, orgs):
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        reqs = {r["code"]: r for r in requirement_statuses(conn, "insurer", control_statuses(conn))}
    assert set(reqs) >= {"mfa", "admin_access", "email_security", "edr", "backups"}
    assert reqs["mfa"]["status"] == "failing"
    assert all(r["summary"] for r in reqs.values()), "insurer questions use our own summaries"
