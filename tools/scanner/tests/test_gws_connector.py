"""The Google Workspace connector against a fake GoogleApi. No network, no credentials, no Google libraries."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

import alimi_scanner.connectors.gws as gws_module
from alimi_scanner.connectors.gws import (
    ApiDenied,
    GoogleError,
    GoogleWorkspaceConnector,
    aggregate_token_events,
    parse_policies,
)
from alimi_scanner.snapshot import GWSUser

NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _setting(kind: str, value: dict, org_unit: str = "orgUnits/root") -> dict:
    return {
        "name": f"policies/{kind}-{org_unit}",
        "type": "ADMIN",
        "policyQuery": {"orgUnit": org_unit},
        "setting": {"type": f"settings/{kind}", "value": value},
    }


class FakeGoogleApi:
    """Answers like a small tenant. `denied` names methods that raise ApiDenied, `gmail_missing` users with no mailbox."""

    def __init__(self, denied=(), gmail_missing=("c@fakeco.example",), token_events=None):
        self.denied = set(denied)
        self.gmail_missing = set(gmail_missing)
        self.calls: list[str] = []
        self.token_events = token_events

    def _check(self, name: str) -> None:
        self.calls.append(name)
        if name in self.denied:
            raise ApiDenied(f"{name}: HTTP 403")

    def get_customer(self):
        self._check("get_customer")
        return {"customerDomain": "fakeco.example", "postalAddress": {"organizationName": "Fake Co"}}

    def list_domains(self):
        self._check("list_domains")
        return [
            {"domainName": "fakeco-secondary.example", "isPrimary": False, "verified": True},
            {"domainName": "fakeco.example", "isPrimary": True, "verified": True},
            {"domainName": "unverified.example", "isPrimary": False, "verified": False},
        ]

    def list_users(self):
        self._check("list_users")
        return [
            {"id": "1", "primaryEmail": "a@fakeco.example", "name": {"fullName": "A"}, "isAdmin": False, "isEnrolledIn2Sv": True,
             "isEnforcedIn2Sv": True, "creationTime": "2024-01-01T00:00:00.000Z", "lastLoginTime": "2026-10-30T00:00:00.000Z", "orgUnitPath": "/"},
            {"id": "2", "primaryEmail": "adm@fakeco.example", "isAdmin": True, "isDelegatedAdmin": False, "isEnrolledIn2Sv": True,
             "isEnforcedIn2Sv": True, "orgUnitPath": "/"},
            {"id": "3", "primaryEmail": "s@fakeco.example", "suspended": True, "isEnrolledIn2Sv": False, "isEnforcedIn2Sv": False,
             "orgUnitPath": "/Sales"},
            {"id": "4", "primaryEmail": "c@fakeco.example", "isEnrolledIn2Sv": False, "isEnforcedIn2Sv": False,
             "lastLoginTime": "1970-01-01T00:00:00.000Z", "orgUnitPath": "/Contractors"},
        ]

    def list_policies(self):
        self._check("list_policies")
        return [
            _setting("security.two_step_verification_enforcement", {"enforcedFrom": "2024-01-01T00:00:00Z"}),
            _setting("security.two_step_verification_enforcement", {}, "orgUnits/contractors"),
            _setting("security.less_secure_apps", {"allowLessSecureApps": False}),
            _setting("gmail.auto_forwarding", {"enableAutoForwarding": True}),
            _setting("drive_and_docs.external_sharing",
                     {"externalSharingMode": "ALLOWLISTED_DOMAINS", "allowPublishingFiles": False, "warnForExternalSharing": True}),
            _setting("drive_and_docs.external_sharing",
                     {"externalSharingMode": "ALLOWED", "allowPublishingFiles": False, "warnForExternalSharing": False}, "orgUnits/sales"),
            _setting("workspace_marketplace.apps_access_options", {"accessLevel": "ALLOW_LISTED"}),
            _setting("chat.external_chat_restriction", {"allowExternalChat": True}),  # unrelated, ignored
        ]

    def list_activities(self, application, *, start, event_name=None, cap=5000):
        self._check("list_activities")
        assert start < NOW
        if application == "token":
            assert event_name == "authorize"
            events = self.token_events if self.token_events is not None else [
                {"id": {"time": "2026-10-01T10:00:00.000Z", "applicationName": "token"}, "actor": {"email": "a@fakeco.example"},
                 "events": [{"type": "auth", "name": "authorize", "parameters": [
                     {"name": "client_id", "value": "x.apps.googleusercontent.com"}, {"name": "app_name", "value": "PDF Tool"},
                     {"name": "client_type", "value": "WEB"}, {"name": "scope", "multiValue": ["https://mail.google.com/", "openid"]}]}]},
                {"id": {"time": "2026-10-05T10:00:00.000Z", "applicationName": "token"}, "actor": {"email": "C@fakeco.example"},
                 "events": [{"type": "auth", "name": "authorize", "parameters": [
                     {"name": "client_id", "value": "x.apps.googleusercontent.com"}, {"name": "app_name", "value": "PDF Tool"},
                     {"name": "scope", "multiValue": ["https://mail.google.com/"]}]}]},
                {"id": {"time": "2026-09-01T10:00:00.000Z", "applicationName": "token"}, "actor": {"email": "a@fakeco.example"},
                 "events": [{"type": "auth", "name": "authorize", "parameters": [
                     {"name": "client_id", "value": "y.apps.googleusercontent.com"}, {"name": "app_name", "value": "Calendar Thing"},
                     {"name": "scope", "value": "https://www.googleapis.com/auth/calendar.readonly"}]}]},
            ]
            return events[:cap]
        if application == "login":
            return [{"id": {"time": "2026-10-31T00:00:00.000Z"}}][:cap]
        if application == "admin":
            return []
        raise GoogleError(f"unknown application {application}")

    def get_auto_forwarding(self, user_email):
        self._check("get_auto_forwarding")
        if user_email in self.gmail_missing:
            raise GoogleError("getAutoForwarding: HTTP 400")
        if user_email == "a@fakeco.example":
            return {"enabled": True, "emailAddress": "a.home@gmail.example", "disposition": "leaveInInbox"}
        return {"enabled": False}

    def list_filters(self, user_email):
        self._check("list_filters")
        if user_email == "a@fakeco.example":
            return [{"id": "f1", "action": {"forward": "x@fakeco.example"}}, {"id": "f2", "action": {"addLabelIds": ["L"]}}]
        return []


def connector(api=None, **kwargs) -> GoogleWorkspaceConnector:
    return GoogleWorkspaceConnector(api or FakeGoogleApi(), dns=False, now=NOW, **kwargs)


def test_snapshot_is_built_from_api_payloads():
    snap = connector().fetch()
    assert snap.tenant_display_name == "Fake Co"
    assert snap.verified_domains == ["fakeco.example", "fakeco-secondary.example"]  # primary first, unverified dropped
    assert snap.primary_domain() == "fakeco.example"
    assert [u.email for u in snap.users] == ["a@fakeco.example", "adm@fakeco.example", "s@fakeco.example", "c@fakeco.example"]
    assert snap.user_by_email("S@fakeco.example").suspended is True
    assert snap.user_by_email("c@fakeco.example").last_login is None  # 1970 sentinel
    assert snap.user_by_email("a@fakeco.example").last_login.year == 2026
    assert snap.user_by_email("adm@fakeco.example").is_super_admin

    p = snap.policies
    assert p.two_sv_enforced_everywhere is False
    assert p.two_sv_unenforced_org_units == ["/Contractors"]  # from active users' flags; the suspended Sales user is ignored
    assert p.less_secure_apps_allowed is False
    assert p.auto_forwarding_allowed is True
    assert p.external_sharing_mode == "ALLOWED"  # the loosest org unit decides
    assert p.allow_publishing_files is False
    assert p.warn_for_external_sharing is False
    assert p.marketplace_access_level == "ALLOW_LISTED"
    assert p.third_party_access_restricted is None

    assert [f.user_email for f in snap.forwarding] == ["a@fakeco.example", "adm@fakeco.example"]  # suspended skipped, c@ has no Gmail
    assert snap.forwarding[0].auto_forwarding_enabled and snap.forwarding[0].auto_forward_to == "a.home@gmail.example"
    assert snap.forwarding[0].filter_forward_to == ["x@fakeco.example"]

    apps = {a.client_id: a for a in snap.third_party_apps}
    assert apps["x.apps.googleusercontent.com"].user_count == 2
    assert apps["x.apps.googleusercontent.com"].display_name == "PDF Tool"
    assert apps["x.apps.googleusercontent.com"].client_type == "WEB"
    assert apps["x.apps.googleusercontent.com"].scopes == ["https://mail.google.com/", "openid"]
    assert apps["x.apps.googleusercontent.com"].last_authorized == datetime(2026, 10, 5, 10, tzinfo=timezone.utc)
    assert apps["y.apps.googleusercontent.com"].scopes == ["https://www.googleapis.com/auth/calendar.readonly"]
    assert snap.third_party_apps[0].client_id == "x.apps.googleapis.com".replace("googleapis", "googleusercontent")  # most users first

    assert snap.audit.login_available is True and snap.audit.admin_available is True
    assert snap.email_auth is None  # dns=False
    assert any("API controls" in n for n in snap.notes)
    assert any("no Gmail mailbox" in n for n in snap.notes)
    assert any("180 days" in n for n in snap.notes)


def test_denied_users_scope_leaves_users_and_forwarding_empty_with_a_note():
    snap = connector(FakeGoogleApi(denied={"list_users"})).fetch()
    assert snap.users is None
    assert snap.forwarding is None
    assert snap.policies.two_sv_unenforced_org_units == []
    assert any("users: permission denied" in n for n in snap.notes)


def test_denied_gmail_scope_stops_forwarding_with_a_note():
    snap = connector(FakeGoogleApi(denied={"get_auto_forwarding"})).fetch()
    assert snap.forwarding is None
    assert any("gmail.readonly" in n for n in snap.notes)


def test_denied_reports_scope_leaves_apps_and_audit_unknown():
    snap = connector(FakeGoogleApi(denied={"list_activities"})).fetch()
    assert snap.third_party_apps is None
    assert snap.audit.login_available is None and snap.audit.admin_available is None
    assert any("admin.reports.audit.readonly" in n for n in snap.notes)


def test_denied_policies_scope_leaves_policies_empty():
    snap = connector(FakeGoogleApi(denied={"list_policies"})).fetch()
    assert snap.policies is None
    assert any("policies: permission denied" in n for n in snap.notes)


def test_denied_customer_call_falls_back_to_the_domain_list():
    snap = connector(FakeGoogleApi(denied={"get_customer"})).fetch()
    assert snap.tenant_display_name is None
    assert snap.verified_domains[0] == "fakeco.example"


def test_mailbox_cap_is_noted():
    snap = connector(max_mailbox_users=1).fetch()
    assert len(snap.forwarding) == 1
    assert any("first 1 of 3 mailboxes" in n for n in snap.notes)


def test_token_event_cap_is_noted():
    snap = connector(token_event_cap=2).fetch()
    assert any("stopped at 2" in n for n in snap.notes)


def test_approved_client_ids_travel_with_the_snapshot():
    snap = connector(approved_client_ids=["x.apps.googleusercontent.com", ""]).fetch()
    assert snap.approved_client_ids == ["x.apps.googleusercontent.com"]


def test_dns_lookups_use_the_google_selector_on_custom_domains_only(monkeypatch):
    seen = []

    def fake_lookup(domain, selectors):
        seen.append((domain, selectors))
        from alimi_scanner.snapshot import DomainEmailAuth

        return DomainEmailAuth(domain=domain, spf="v=spf1 include:_spf.google.com ~all", dkim_enabled=True, dmarc="v=DMARC1; p=reject")

    monkeypatch.setattr("alimi_scanner.connectors.dns_lookup.lookup_domain", fake_lookup)
    snap = GoogleWorkspaceConnector(FakeGoogleApi(), dns=True, now=NOW).fetch()
    assert [d for d, _ in seen] == ["fakeco.example", "fakeco-secondary.example"]
    assert all(selectors == ("google",) for _, selectors in seen)
    assert len(snap.email_auth) == 2


def test_from_env_requires_the_key_file_and_admin(tmp_path):
    with pytest.raises(GoogleError, match="GWS_DELEGATED_ADMIN"):
        GoogleWorkspaceConnector.from_env({"GWS_SERVICE_ACCOUNT_FILE": str(tmp_path / "k.json")})
    with pytest.raises(GoogleError, match="does not exist"):
        GoogleWorkspaceConnector.from_env({"GWS_SERVICE_ACCOUNT_FILE": str(tmp_path / "k.json"), "GWS_DELEGATED_ADMIN": "a@x"})


def test_from_env_builds_the_real_api_and_reads_approved_ids(tmp_path, monkeypatch):
    key = tmp_path / "k.json"
    key.write_text("{}")
    built = {}

    def fake_api(path, admin, customer):
        built.update(path=path, admin=admin, customer=customer)
        return FakeGoogleApi()

    monkeypatch.setattr(gws_module, "DiscoveryGoogleApi", fake_api)
    env = {"GWS_SERVICE_ACCOUNT_FILE": str(key), "GWS_DELEGATED_ADMIN": "adm@fakeco.example", "GWS_APPROVED_CLIENT_IDS": "x.apps.googleusercontent.com, y.apps.googleusercontent.com"}
    conn = GoogleWorkspaceConnector.from_env(env, dns=False, now=NOW)
    assert built == {"path": str(key), "admin": "adm@fakeco.example", "customer": "my_customer"}
    snap = conn.fetch()
    assert snap.approved_client_ids == ["x.apps.googleusercontent.com", "y.apps.googleusercontent.com"]


def test_parse_policies_accepts_snake_case_and_handles_absent_settings():
    users = [GWSUser(id="1", email="a@x", enforced_2sv=False, org_unit_path="/Ops")]
    policies = parse_policies(
        [
            _setting("security.two_step_verification_enforcement", {"enforced_from": "2030-01-01T00:00:00Z"}),  # future date: not yet enforced
            _setting("drive_and_docs.external_sharing", {"external_sharing_mode": "DISALLOWED", "allow_publishing_files": False, "warn_for_external_sharing": True}),
        ],
        now=NOW,
        users=users,
    )
    assert policies.two_sv_enforced_everywhere is False
    assert policies.two_sv_unenforced_org_units == ["/Ops"]
    assert policies.external_sharing_mode == "DISALLOWED"
    assert policies.less_secure_apps_allowed is None
    assert policies.auto_forwarding_allowed is None
    assert policies.marketplace_access_level is None


def test_parse_policies_marks_unenforced_users_even_without_a_2sv_policy():
    users = [GWSUser(id="1", email="a@x", enforced_2sv=False, org_unit_path="/")]
    policies = parse_policies([], now=NOW, users=users)
    assert policies.two_sv_enforced_everywhere is False
    assert policies.two_sv_unenforced_org_units == ["/"]


def test_aggregate_token_events_skips_other_events_and_missing_client_ids():
    apps = aggregate_token_events(
        [
            {"id": {"time": "2026-10-01T00:00:00Z"}, "actor": {"email": "a@x"},
             "events": [{"name": "revoke", "parameters": [{"name": "client_id", "value": "x"}]}]},
            {"id": {"time": "2026-10-01T00:00:00Z"}, "actor": {"email": "a@x"},
             "events": [{"name": "authorize", "parameters": [{"name": "app_name", "value": "no id"}]}]},
            {"id": {"time": "2026-10-02T00:00:00Z"}, "actor": {"profileId": "123"},
             "events": [{"name": "authorize", "parameters": [{"name": "client_id", "value": "z"}, {"name": "scope", "value": "openid"}]}]},
        ]
    )
    assert [(a.client_id, a.user_count, a.scopes) for a in apps] == [("z", 1, ["openid"])]


def test_snapshot_serializes_without_customer_id_or_key_path():
    snap = connector().fetch()
    dumped = json.dumps(snap.model_dump(mode="json"))
    assert "my_customer" not in dumped and "service_account" not in dumped
