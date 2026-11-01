"""The decisions the report makes, tested without rendering any HTML."""

from __future__ import annotations

from alimi_scanner.schema import Severity, Status

from alimi_report.model import build_model, glossary_for, grade_for, rank_fixes


def test_grade_bands():
    assert grade_for(100)[0] == "Strong"
    assert grade_for(90)[0] == "Strong"
    assert grade_for(89.9)[0] == "Good"
    assert grade_for(75)[0] == "Good"
    assert grade_for(50)[0] == "Needs work"
    assert grade_for(0)[0] == "At risk"
    assert grade_for(None)[0] == "Not scored"


def test_top_fixes_are_failures_ranked_by_severity(m365_fail, brand, offer):
    model = build_model(m365_fail, brand=brand, offer=offer)
    assert len(model.top_fixes) == 5
    weights = {Severity.critical: 4, Severity.high: 3, Severity.medium: 2, Severity.low: 1}
    ranks = [weights[f.severity] for f in model.top_fixes]
    assert ranks == sorted(ranks, reverse=True)
    assert model.top_fixes[0].severity == Severity.critical
    assert [f.rank for f in model.top_fixes] == [1, 2, 3, 4, 5]
    assert all(f.what_to_do for f in model.top_fixes)


def test_a_clean_tenant_has_no_fixes_and_a_strong_grade(m365_pass, brand, offer):
    model = build_model(m365_pass, brand=brand, offer=offer)
    assert model.top_fixes == []
    assert model.grade == "Strong"
    assert model.score == 100.0
    assert model.counts.failed == 0


def test_insurer_rows_use_plain_words(m365_fail, m365_pass, brand, offer):
    failing = {q.question_id: q for q in build_model(m365_fail, brand=brand, offer=offer).questions}
    assert failing["mfa"].label == "No"
    assert failing["backups"].label == "You confirm"
    assert len(failing) == 8
    passing = {q.question_id: q for q in build_model(m365_pass, brand=brand, offer=offer).questions}
    assert passing["mfa"].label == "Yes"
    assert "MFA registration coverage" in passing["mfa"].checks


def test_evidence_pack_lists_attestations_and_screenshot_asks(gws_pass, brand, offer):
    model = build_model(gws_pass, brand=brand, offer=offer)
    ids = [e.check_id for e in model.evidence_pack]
    assert {"att.edr.coverage", "att.backups.tested", "att.ir_plan.tested"} <= set(ids)
    edr = next(e for e in model.evidence_pack if e.check_id == "att.edr.coverage")
    assert "coverage" in edr.attach.lower()
    assert edr.answers.startswith("Is endpoint detection")


def test_evidence_pack_includes_errors_and_attestation_needed_findings(m365_pass, brand, offer):
    result = m365_pass.model_copy(deep=True)
    fwd = next(f for f in result.findings if f.check_id == "m365.forwarding.external")
    fwd.status = Status.attestation_needed
    fwd.summary = "Confirm the outbound policy and attach a screenshot."
    err = next(f for f in result.findings if f.check_id == "m365.secure_score")
    err.status = Status.error
    model = build_model(result, brand=brand, offer=offer)
    by_id = {e.check_id: e for e in model.evidence_pack}
    assert "screenshot" in by_id["m365.forwarding.external"].attach
    assert by_id["m365.secure_score"].attach.startswith("Nothing to attach yet")


def test_sections_follow_the_what_to_do_next_order(gws_fail, brand, offer):
    model = build_model(gws_fail, brand=brand, offer=offer)
    assert [s.status for s in model.sections] == [Status.failed, Status.attestation_needed]
    assert model.sections[0].title == "What needs fixing"
    assert len(model.sections[0].findings) == 8
    first = model.sections[0].findings[0]
    assert first.severity == Severity.critical
    assert first.evidence  # key/value rows rendered from the finding's evidence dict


def test_glossary_only_includes_terms_that_appear():
    assert glossary_for(["Enable MFA for everyone"])[0][0] == "MFA"
    assert glossary_for(["nothing relevant"]) == []
    terms = [t for t, _ in glossary_for(["publish DMARC and turn on DKIM", "deploy EDR"])]
    assert terms == ["DKIM", "DMARC", "EDR"]


def test_why_it_matters_comes_from_the_catalog(m365_fail, brand, offer):
    from alimi_scanner.catalog import load_catalog

    with_catalog = build_model(m365_fail, brand=brand, offer=offer, catalog=load_catalog())
    without = build_model(m365_fail, brand=brand, offer=offer, catalog=None)
    assert with_catalog.top_fixes[0].why
    assert without.top_fixes[0].why == ""


def test_rank_fixes_limit(m365_fail):
    assert len(rank_fixes(m365_fail.findings, {}, limit=3)) == 3
