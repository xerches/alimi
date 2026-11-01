"""Every Google Workspace check passes on the pass fixture, fails on the fail fixture,
and fires on its own when one thing in the pass fixture goes wrong."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from alimi_scanner.engine import run_checks
from alimi_scanner.schema import CheckKind, Platform, Status
from alimi_scanner.snapshot import GWSSnapshot, OAuthApp

GWS_AUTOMATED = [
    "gws.2sv.enforced",
    "gws.admins.super_count",
    "gws.forwarding.external",
    "gws.email_auth.dmarc",
    "gws.oauth.third_party",
    "gws.drive.external_sharing",
    "gws.lsa.disabled",
    "gws.audit.available",
]


def statuses(result) -> dict[str, Status]:
    return {f.check_id: f.status for f in result.findings}


def finding(result, check_id):
    return next(f for f in result.findings if f.check_id == check_id)


def test_pass_fixture_passes_every_automated_check(gws_pass_snapshot, catalog, tenant):
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    got = statuses(result)
    for check_id in GWS_AUTOMATED:
        assert got[check_id] == Status.passed, (check_id, finding(result, check_id).summary)
    assert not any(check_id.startswith("m365.") for check_id in got)
    attestations = [f for f in result.findings if f.kind == CheckKind.attestation]
    assert len(attestations) == 3
    assert result.summary.score_percent == 100.0
    assert result.summary.failed == 0


def test_fail_fixture_fails_every_automated_check(gws_fail_snapshot, catalog, tenant):
    result = run_checks(gws_fail_snapshot, catalog, Platform.gws, tenant)
    got = statuses(result)
    for check_id in GWS_AUTOMATED:
        assert got[check_id] == Status.failed, (check_id, finding(result, check_id).summary)
    assert result.summary.score_percent == 0.0
    by_question = {a.question_id: a.status for a in result.insurer_answers}
    assert by_question["mfa"] == "fail"
    assert by_question["data_sharing"] == "fail"
    assert by_question["edr"] == "attestation_needed"


# ----- one thing wrong at a time -----


def _user(snapshot: GWSSnapshot, email: str):
    return next(u for u in snapshot.users if u.email == email)


def break_2sv_not_enrolled(s: GWSSnapshot) -> None:
    _user(s, "chloe@example.com").enrolled_2sv = False


def break_2sv_not_enforced(s: GWSSnapshot) -> None:
    _user(s, "dan@example.com").enforced_2sv = False


def break_2sv_policy(s: GWSSnapshot) -> None:
    s.policies.two_sv_enforced_everywhere = False
    s.policies.two_sv_unenforced_org_units = ["/Contractors"]


def break_super_admin_only_one(s: GWSSnapshot) -> None:
    _user(s, "adm-ben@example.com").suspended = True


def break_super_admin_too_many(s: GWSSnapshot) -> None:
    for email in ("ava@example.com", "ben@example.com", "chloe@example.com"):
        _user(s, email).is_super_admin = True


def break_super_admin_2sv(s: GWSSnapshot) -> None:
    _user(s, "adm-ava@example.com").enrolled_2sv = False


def break_forwarding_auto(s: GWSSnapshot) -> None:
    entry = next(f for f in s.forwarding if f.user_email == "ava@example.com")
    entry.auto_forwarding_enabled = True
    entry.auto_forward_to = "ava.personal@gmail.example"


def break_forwarding_filter(s: GWSSnapshot) -> None:
    next(f for f in s.forwarding if f.user_email == "ben@example.com").filter_forward_to.append("ben@outlook.example")


def break_forwarding_policy(s: GWSSnapshot) -> None:
    s.policies.auto_forwarding_allowed = True


def break_dmarc(s: GWSSnapshot) -> None:
    s.email_auth[0].dmarc = "v=DMARC1; p=none"


def break_oauth_unapproved(s: GWSSnapshot) -> None:
    s.approved_client_ids = []  # Team Chat holds drive.readonly


def break_oauth_unrestricted(s: GWSSnapshot) -> None:
    s.policies.third_party_access_restricted = False


def break_drive_publishing(s: GWSSnapshot) -> None:
    s.policies.allow_publishing_files = True


def break_drive_mode(s: GWSSnapshot) -> None:
    s.policies.external_sharing_mode = "ALLOWED"
    s.policies.warn_for_external_sharing = False


def break_lsa(s: GWSSnapshot) -> None:
    s.policies.less_secure_apps_allowed = True


def break_audit(s: GWSSnapshot) -> None:
    s.audit.admin_available = False


CASES: list[tuple[str, Callable[[GWSSnapshot], None], set[str]]] = [
    ("gws.2sv.enforced", break_2sv_not_enrolled, set()),
    ("gws.2sv.enforced", break_2sv_not_enforced, set()),
    ("gws.2sv.enforced", break_2sv_policy, set()),
    ("gws.admins.super_count", break_super_admin_only_one, set()),
    ("gws.admins.super_count", break_super_admin_too_many, set()),
    ("gws.admins.super_count", break_super_admin_2sv, {"gws.2sv.enforced"}),
    ("gws.forwarding.external", break_forwarding_auto, set()),
    ("gws.forwarding.external", break_forwarding_filter, set()),
    ("gws.forwarding.external", break_forwarding_policy, set()),
    ("gws.email_auth.dmarc", break_dmarc, set()),
    ("gws.oauth.third_party", break_oauth_unapproved, set()),
    ("gws.oauth.third_party", break_oauth_unrestricted, set()),
    ("gws.drive.external_sharing", break_drive_publishing, set()),
    ("gws.drive.external_sharing", break_drive_mode, set()),
    ("gws.lsa.disabled", break_lsa, set()),
    ("gws.audit.available", break_audit, set()),
]


@pytest.mark.parametrize("check_id, mutate, allowed_extra", CASES, ids=[f"{c[0]}:{c[1].__name__}" for c in CASES])
def test_each_check_fires_on_its_own(gws_pass_snapshot, catalog, tenant, check_id, mutate, allowed_extra):
    mutate(gws_pass_snapshot)
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    failed = {f.check_id for f in result.findings if f.status == Status.failed}
    assert check_id in failed, finding(result, check_id).summary
    assert failed - {check_id} <= allowed_extra, failed


# ----- missing data is an error with the scope named, not a guess -----


def test_missing_users_is_an_error_naming_the_scope(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.users = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.2sv.enforced")
    assert f.status == Status.error
    assert "admin.directory.user.readonly" in f.summary
    assert finding(result, "gws.admins.super_count").status == Status.error
    by_question = {a.question_id: a.status for a in result.insurer_answers}
    assert by_question["mfa"] == "unknown"


def test_missing_forwarding_is_an_error_naming_the_gmail_scope(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.forwarding = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.forwarding.external")
    assert f.status == Status.error
    assert "gmail.readonly" in f.summary


def test_missing_policies_errors_on_policy_checks_but_2sv_uses_user_flags(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.policies = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    assert "cloud-identity.policies.readonly" in finding(result, "gws.drive.external_sharing").summary
    assert finding(result, "gws.drive.external_sharing").status == Status.error
    assert finding(result, "gws.lsa.disabled").status == Status.error
    two_sv = finding(result, "gws.2sv.enforced")
    assert two_sv.status == Status.passed
    assert any("isEnforcedIn2Sv" in note for note in two_sv.notes)
    # forwarding and third-party apps fall back to asking for a screenshot of the setting
    assert finding(result, "gws.forwarding.external").status == Status.attestation_needed
    assert finding(result, "gws.oauth.third_party").status == Status.attestation_needed


def test_missing_token_events_is_an_error_naming_the_reports_scope(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.third_party_apps = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.oauth.third_party")
    assert f.status == Status.error
    assert "admin.reports.audit.readonly" in f.summary


def test_missing_audit_is_an_error(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.audit = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    assert finding(result, "gws.audit.available").status == Status.error


def test_unknown_auto_forwarding_setting_asks_for_attestation(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.policies.auto_forwarding_allowed = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.forwarding.external")
    assert f.status == Status.attestation_needed
    assert "screenshot" in f.summary


def test_unknown_api_controls_setting_asks_for_attestation(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.policies.third_party_access_restricted = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.oauth.third_party")
    assert f.status == Status.attestation_needed
    assert "API controls" in f.summary


def test_unknown_less_secure_apps_passes_with_a_note(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.policies.less_secure_apps_allowed = None
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.lsa.disabled")
    assert f.status == Status.passed
    assert any("2025" in note for note in f.notes)


def test_no_custom_domain_is_not_applicable(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.email_auth = []
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    assert finding(result, "gws.email_auth.dmarc").status == Status.not_applicable


def test_internal_forwarding_is_fine_whatever_the_case(gws_pass_snapshot, catalog, tenant):
    next(f for f in gws_pass_snapshot.forwarding if f.user_email == "ben@example.com").filter_forward_to.append("Team@EXAMPLE.com")
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    assert finding(result, "gws.forwarding.external").status == Status.passed


def test_low_risk_scopes_do_not_flag_an_unapproved_app(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.third_party_apps.append(
        OAuthApp(
            client_id="300000000003-notes.apps.googleusercontent.com",
            display_name="Notes Add-on",
            scopes=["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/gmail.labels", "openid"],
            user_count=1,
        )
    )
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.oauth.third_party")
    assert f.status == Status.passed
    assert f.evidence["apps_seen"] == 3


def test_external_sharing_allowed_with_warning_passes_with_a_note(gws_pass_snapshot, catalog, tenant):
    gws_pass_snapshot.policies.external_sharing_mode = "ALLOWED"
    gws_pass_snapshot.policies.warn_for_external_sharing = True
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.drive.external_sharing")
    assert f.status == Status.passed
    assert any("Allowlisting" in note for note in f.notes)


def test_suspended_users_do_not_count(gws_pass_snapshot, catalog, tenant):
    # "former" is suspended and not enrolled; the pass fixture passes, so suspension is already ignored.
    # Suspending a super admin, though, drops the count below two.
    _user(gws_pass_snapshot, "adm-ava@example.com").archived = True
    result = run_checks(gws_pass_snapshot, catalog, Platform.gws, tenant)
    f = finding(result, "gws.admins.super_count")
    assert f.status == Status.failed
    assert "only 1 super admin" in f.summary
