from __future__ import annotations

import alimi_scanner.engine as engine
from alimi_scanner.schema import CheckOutcome, Platform, Status


def test_a_raising_check_becomes_an_error_finding(pass_snapshot, catalog, tenant, monkeypatch):
    engine.registered_ids()  # make sure the registry is loaded before we patch it

    def boom(snapshot, definition):
        raise RuntimeError("kaboom")

    monkeypatch.setitem(engine._REGISTRY, "m365.secure_score", boom)
    result = engine.run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    f = next(x for x in result.findings if x.check_id == "m365.secure_score")
    assert f.status == Status.error
    assert "kaboom" in f.summary
    assert result.summary.errors == 1


def test_score_is_severity_weighted(pass_snapshot, catalog, tenant, monkeypatch):
    engine.registered_ids()

    def fail(snapshot, definition):
        return CheckOutcome(status=Status.failed, summary="forced")

    # secure_score is "low" (weight 1); the 12 m365 checks weigh 4+3+4+2+3+4+3+3+2+1+3+1 = 33
    monkeypatch.setitem(engine._REGISTRY, "m365.secure_score", fail)
    result = engine.run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    assert result.summary.score_percent == round(100 * 32 / 33, 1)


def test_insurer_answer_rollup_prefers_fail_then_unknown(pass_snapshot, catalog, tenant, monkeypatch):
    engine.registered_ids()
    monkeypatch.setitem(
        engine._REGISTRY, "m365.secure_score", lambda s, d: CheckOutcome(status=Status.error, summary="x")
    )
    result = engine.run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    answers = {a.question_id: a for a in result.insurer_answers}
    # mfa has several passing checks and one error -> unknown, because we won't claim a pass we can't prove
    assert answers["mfa"].status == "unknown"
    assert "m365.secure_score" in answers["mfa"].check_ids
    assert answers["backups"].status == "attestation_needed"


def test_result_round_trips_through_json(pass_snapshot, catalog, tenant):
    from alimi_scanner.schema import ScanResult

    result = engine.run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    again = ScanResult.model_validate_json(result.model_dump_json())
    assert again == result
    assert again.tenant.source == "test"
