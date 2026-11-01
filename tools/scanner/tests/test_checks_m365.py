"""Every Microsoft 365 check passes on the pass fixture, fails on the fail fixture,
and fires on its own when one thing in the pass fixture goes wrong."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

import pytest

from alimi_scanner.engine import run_checks
from alimi_scanner.schema import CheckKind, Platform, Status
from alimi_scanner.snapshot import InboxRule, M365Snapshot

M365_AUTOMATED = [
    "m365.mfa.coverage",
    "m365.conditional_access.present",
    "m365.legacy_auth.blocked",
    "m365.security_defaults",
    "m365.admins.global_count",
    "m365.admins.mfa",
    "m365.forwarding.external",
    "m365.email_auth.dmarc",
    "m365.sharing.anonymous_links",
    "m365.guests.review",
    "m365.audit.enabled",
    "m365.secure_score",
]


def statuses(result) -> dict[str, Status]:
    return {f.check_id: f.status for f in result.findings}


def finding(result, check_id):
    return next(f for f in result.findings if f.check_id == check_id)


def test_pass_fixture_passes_every_automated_check(pass_snapshot, catalog, tenant):
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    got = statuses(result)
    for check_id in M365_AUTOMATED:
        assert got[check_id] == Status.passed, (check_id, finding(result, check_id).summary)
    attestations = [f for f in result.findings if f.kind == CheckKind.attestation]
    assert len(attestations) == 3
    assert all(f.status == Status.attestation_needed and f.evidence_requested for f in attestations)
    assert result.summary.score_percent == 100.0
    assert result.summary.failed == 0


def test_fail_fixture_fails_every_automated_check(fail_snapshot, catalog, tenant):
    result = run_checks(fail_snapshot, catalog, Platform.m365, tenant)
    got = statuses(result)
    for check_id in M365_AUTOMATED:
        assert got[check_id] == Status.failed, (check_id, finding(result, check_id).summary)
    assert result.summary.score_percent == 0.0
    by_question = {a.question_id: a.status for a in result.insurer_answers}
    assert by_question["mfa"] == "fail"
    assert by_question["edr"] == "attestation_needed"


# ----- one thing wrong at a time -----


def _user(snapshot: M365Snapshot, upn: str):
    return next(u for u in snapshot.users if u.upn == upn)


def break_mfa_coverage(s: M365Snapshot) -> None:
    _user(s, "chloe@example.com").mfa_registered = False


def break_conditional_access(s: M365Snapshot) -> None:
    s.conditional_access_policies = [p for p in s.conditional_access_policies if not p.requires_mfa]


def break_legacy_auth_sign_ins(s: M365Snapshot) -> None:
    s.legacy_auth_sign_ins_30d = 3


def break_legacy_auth_policy(s: M365Snapshot) -> None:
    s.conditional_access_policies = [p for p in s.conditional_access_policies if not p.blocks_legacy_auth]


def break_global_admin_count(s: M365Snapshot) -> None:
    _user(s, "adm-ava@example.com").has_mailbox = True


def break_admin_mfa(s: M365Snapshot) -> None:
    _user(s, "adm-ben@example.com").mfa_registered = False


def break_forwarding(s: M365Snapshot) -> None:
    s.inbox_rules.append(InboxRule(user_upn="dan@example.com", name="backup", forward_to=["dan.backup@gmail.example"]))


def break_dmarc(s: M365Snapshot) -> None:
    s.email_auth[0].dmarc = "v=DMARC1; p=none"


def break_sharing(s: M365Snapshot) -> None:
    s.sharing.sharing_capability = "externalUserAndGuestSharing"


def break_guests(s: M365Snapshot) -> None:
    guest = next(u for u in s.users if u.user_type == "Guest")
    guest.last_sign_in = None
    guest.created = datetime(2025, 1, 1, tzinfo=timezone.utc)


def break_audit(s: M365Snapshot) -> None:
    s.audit.unified_audit_log_enabled = False


def break_secure_score(s: M365Snapshot) -> None:
    s.secure_score.current = 40


CASES: list[tuple[str, Callable[[M365Snapshot], None], set[str]]] = [
    ("m365.mfa.coverage", break_mfa_coverage, set()),
    ("m365.conditional_access.present", break_conditional_access, {"m365.security_defaults"}),
    ("m365.legacy_auth.blocked", break_legacy_auth_sign_ins, set()),
    ("m365.legacy_auth.blocked", break_legacy_auth_policy, {"m365.security_defaults"}),
    ("m365.security_defaults", break_legacy_auth_policy, {"m365.legacy_auth.blocked"}),
    ("m365.admins.global_count", break_global_admin_count, set()),
    ("m365.admins.mfa", break_admin_mfa, {"m365.mfa.coverage"}),
    ("m365.forwarding.external", break_forwarding, set()),
    ("m365.email_auth.dmarc", break_dmarc, set()),
    ("m365.sharing.anonymous_links", break_sharing, set()),
    ("m365.guests.review", break_guests, set()),
    ("m365.audit.enabled", break_audit, set()),
    ("m365.secure_score", break_secure_score, set()),
]


@pytest.mark.parametrize("check_id, mutate, allowed_extra", CASES, ids=[f"{c[0]}:{c[1].__name__}" for c in CASES])
def test_each_check_fires_on_its_own(pass_snapshot, catalog, tenant, check_id, mutate, allowed_extra):
    mutate(pass_snapshot)
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    failed = {f.check_id for f in result.findings if f.status == Status.failed}
    assert check_id in failed, finding(result, check_id).summary
    assert failed - {check_id} <= allowed_extra, failed


# ----- missing data is an error with the permission named, not a guess -----


def test_missing_users_is_an_error_naming_the_permission(pass_snapshot, catalog, tenant):
    pass_snapshot.users = None
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    f = finding(result, "m365.mfa.coverage")
    assert f.status == Status.error
    assert "User.Read.All" in f.summary
    assert finding(result, "m365.guests.review").status == Status.error
    by_question = {a.question_id: a.status for a in result.insurer_answers}
    assert by_question["mfa"] == "unknown"


def test_missing_registration_report_is_an_error(pass_snapshot, catalog, tenant):
    for user in pass_snapshot.users:
        user.mfa_registered = None
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    assert finding(result, "m365.mfa.coverage").status == Status.error
    assert finding(result, "m365.admins.mfa").status == Status.error


def test_unknown_outbound_forwarding_asks_for_attestation(pass_snapshot, catalog, tenant):
    pass_snapshot.outbound_forwarding_blocked = None
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    f = finding(result, "m365.forwarding.external")
    assert f.status == Status.attestation_needed
    assert "screenshot" in f.summary


def test_unknown_unified_audit_log_asks_for_attestation(pass_snapshot, catalog, tenant):
    pass_snapshot.audit.unified_audit_log_enabled = None
    pass_snapshot.audit.retention_days = None
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    assert finding(result, "m365.audit.enabled").status == Status.attestation_needed


def test_security_defaults_alone_passes_mfa_baseline(pass_snapshot, catalog, tenant):
    pass_snapshot.conditional_access_policies = []
    pass_snapshot.security_defaults_enabled = True
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    assert finding(result, "m365.security_defaults").status == Status.passed
    assert finding(result, "m365.legacy_auth.blocked").status == Status.passed
    # Conditional Access is still absent, and the finding says so with a note about Security Defaults.
    ca = finding(result, "m365.conditional_access.present")
    assert ca.status == Status.failed
    assert any("Security Defaults" in note for note in ca.notes)


def test_no_custom_domain_is_not_applicable(pass_snapshot, catalog, tenant):
    pass_snapshot.email_auth = []
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    assert finding(result, "m365.email_auth.dmarc").status == Status.not_applicable


def test_internal_forwarding_rule_is_fine(pass_snapshot, catalog, tenant):
    pass_snapshot.inbox_rules.append(
        InboxRule(user_upn="ben@example.com", name="to team", redirect_to=["team@EXAMPLE.com"])
    )
    result = run_checks(pass_snapshot, catalog, Platform.m365, tenant)
    assert finding(result, "m365.forwarding.external").status == Status.passed
