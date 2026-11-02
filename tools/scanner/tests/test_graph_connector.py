"""The Graph connector against a fake Graph. No network, no credentials, no msal."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from alimi_scanner.connectors.m365 import GRAPH_BASE, GraphConnector

NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _json(payload, status=200):
    return httpx.Response(status, json=payload)


def fake_graph(overrides=None, denied=()):
    """Return an httpx transport that answers like a small tenant."""
    overrides = overrides or {}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path.removeprefix("/v1.0")
        if any(path.startswith(d) for d in denied):
            return _json({"error": {"code": "Authorization_RequestDenied"}}, 403)
        if path in overrides:
            value = overrides[path]
            return value(request) if callable(value) else _json(value)
        if path == "/organization":
            return _json({"value": [{"displayName": "Fake Co", "verifiedDomains": [
                {"name": "fakeco.onmicrosoft.com", "isDefault": False},
                {"name": "fakeco.example", "isDefault": True},
            ]}]})
        if path == "/users":
            wants_activity = "signInActivity" in request.url.params.get("$select", "")
            if wants_activity and overrides.get("no_p1"):
                return _json({"error": {"code": "Authentication_RequestFromNonPremiumTenantOrB2CTenant"}}, 403)
            if not wants_activity:
                return _json({"value": [
                    {"id": "u1", "userPrincipalName": "a@fakeco.example", "accountEnabled": True, "userType": "Member", "mail": "a@fakeco.example"},
                    {"id": "adm", "userPrincipalName": "adm@fakeco.example", "accountEnabled": True, "userType": "Member"},
                ]})
            return _json({"value": [
                {"id": "u1", "userPrincipalName": "a@fakeco.example", "displayName": "A", "accountEnabled": True,
                 "userType": "Member", "createdDateTime": "2024-01-01T00:00:00Z", "mail": "a@fakeco.example",
                 "signInActivity": {"lastSignInDateTime": "2026-10-30T00:00:00Z"}},
                {"id": "adm", "userPrincipalName": "adm@fakeco.example", "displayName": "Adm", "accountEnabled": True,
                 "userType": "Member", "createdDateTime": "2024-01-01T00:00:00Z", "mail": None},
                {"id": "g1", "userPrincipalName": "g_ext#EXT#@fakeco.onmicrosoft.com", "accountEnabled": True,
                 "userType": "Guest", "createdDateTime": "2023-01-01T00:00:00Z"},
            ]})
        if path == "/reports/authenticationMethods/userRegistrationDetails":
            return _json({"value": [
                {"id": "u1", "isMfaRegistered": True, "methodsRegistered": ["microsoftAuthenticatorPush"]},
                {"id": "adm", "isMfaRegistered": False, "methodsRegistered": []},
            ]})
        if path == "/identity/conditionalAccess/policies":
            return _json({"value": [{
                "id": "ca1", "displayName": "MFA all", "state": "enabled",
                "conditions": {"users": {"includeUsers": ["All"], "excludeUsers": []},
                               "applications": {"includeApplications": ["All"]},
                               "clientAppTypes": ["all"]},
                "grantControls": {"builtInControls": [], "authenticationStrength": {"id": "x"}},
            }]})
        if path == "/policies/identitySecurityDefaultsEnforcementPolicy":
            return _json({"isEnabled": False})
        if path == "/auditLogs/signIns":
            assert "clientAppUsed eq 'IMAP4'" in request.url.params["$filter"]
            return _json({"value": [{"id": "s1", "clientAppUsed": "IMAP4"}, {"id": "s2", "clientAppUsed": "POP3"}]})
        if path == "/directoryRoles":
            return _json({"value": [{"roleTemplateId": "62e90394-69f5-4237-9190-012177145e10",
                                     "displayName": "Global Administrator", "members": [{"id": "adm"}]}]})
        if path == "/users/u1/mailFolders/inbox/messageRules":
            return _json({"value": [{"displayName": "fwd", "isEnabled": True, "actions": {
                "forwardTo": [{"emailAddress": {"address": "me@gmail.example"}}],
                "redirectTo": []}}]})
        if path.startswith("/users/") and path.endswith("/messageRules"):
            return _json({"error": {"code": "MailboxNotEnabledForRESTAPI"}}, 404)
        if path == "/admin/sharepoint/settings":
            return _json({"sharingCapability": "externalUserAndGuestSharing"})
        if path == "/auditLogs/directoryAudits":
            return _json({"value": [{"id": "d1"}]})
        if path == "/security/secureScores":
            return _json({"value": [{"currentScore": 55, "maxScore": 100, "createdDateTime": "2026-10-31T00:00:00Z"}]})
        return _json({"error": {"code": "NotFound", "path": path}}, 404)

    return httpx.MockTransport(handler)


def connector(transport, **kwargs) -> GraphConnector:
    client = httpx.Client(base_url=GRAPH_BASE, transport=transport)
    return GraphConnector("tenant", "client", "secret", client=client, token_provider=lambda: "t", dns=False, now=NOW, **kwargs)


def test_snapshot_is_built_from_graph_payloads():
    snap = connector(fake_graph()).fetch()
    assert snap.tenant_display_name == "Fake Co"
    assert snap.verified_domains[0] == "fakeco.example"
    assert snap.primary_domain() == "fakeco.example"
    assert {u.id: u.mfa_registered for u in snap.users} == {"u1": True, "adm": False, "g1": None}
    assert snap.user_by_id("u1").has_mailbox and not snap.user_by_id("adm").has_mailbox
    assert snap.user_by_id("u1").last_sign_in.year == 2026
    assert snap.conditional_access_policies[0].requires_mfa
    assert snap.security_defaults_enabled is False
    assert snap.legacy_auth_sign_ins_30d == 2
    assert snap.role_assignments[0].member_ids == ["adm"]
    assert [r.forward_to for r in snap.inbox_rules] == [["me@gmail.example"]]
    assert snap.outbound_forwarding_blocked is None
    assert snap.email_auth is None  # dns=False
    assert snap.sharing.sharing_capability == "externalUserAndGuestSharing"
    assert snap.audit.directory_audit_available is True and snap.audit.unified_audit_log_enabled is None
    assert snap.secure_score.percent == 55.0
    assert any("Purview" in n for n in snap.notes)


def test_denied_permission_leaves_field_empty_with_a_note():
    snap = connector(fake_graph(denied=("/users/u1/mailFolders", "/security/secureScores"))).fetch()
    assert snap.inbox_rules is None
    assert snap.secure_score is None
    assert any("MailboxSettings.Read" in n for n in snap.notes)
    assert any("Secure Score" in n and "permission denied" in n for n in snap.notes)


def test_users_retry_without_sign_in_activity_when_no_p1():
    snap = connector(fake_graph(overrides={"no_p1": True})).fetch()
    assert snap.users is not None
    assert all(u.last_sign_in is None for u in snap.users)
    assert any("Entra ID P1" in n for n in snap.notes)


def test_pagination_follows_next_link():
    page2 = GRAPH_BASE + "/users?$skiptoken=abc"

    def users(request: httpx.Request):
        if request.url.params.get("$skiptoken") == "abc":
            return _json({"value": [{"id": "u2", "userPrincipalName": "b@fakeco.example", "accountEnabled": True, "userType": "Member"}]})
        return _json({"value": [{"id": "u1", "userPrincipalName": "a@fakeco.example", "accountEnabled": True, "userType": "Member"}],
                      "@odata.nextLink": page2})

    snap = connector(fake_graph(overrides={"/users": users, "/reports/authenticationMethods/userRegistrationDetails": {"value": []}})).fetch()
    assert [u.id for u in snap.users] == ["u1", "u2"]


def test_throttling_is_retried(monkeypatch):
    calls = {"n": 0}

    def flaky(request: httpx.Request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={})
        return _json({"value": [{"currentScore": 80, "maxScore": 100}]})

    monkeypatch.setattr("alimi_scanner.connectors.m365.time.sleep", lambda s: None)
    snap = connector(fake_graph(overrides={"/security/secureScores": flaky})).fetch()
    assert snap.secure_score.percent == 80.0
    assert calls["n"] == 2


def test_expired_token_is_refreshed_once_not_reported_as_denied():
    tokens = iter(["old", "new"])
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        auth = request.headers["Authorization"]
        seen.append(auth)
        if request.url.path.endswith("/organization") and auth == "Bearer old":
            return _json({"error": {"code": "InvalidAuthenticationToken"}}, 401)
        return fake_graph().handler(request)

    connector = GraphConnector(
        "t", "c", "s",
        client=httpx.Client(base_url=GRAPH_BASE, transport=httpx.MockTransport(handler)),
        token_provider=lambda: next(tokens),
        dns=False,
        now=NOW,
    )
    snapshot = connector.fetch()
    assert snapshot.tenant_display_name == "Fake Co"
    assert seen[:2] == ["Bearer old", "Bearer new"]
    assert not any("permission denied" in note for note in snapshot.notes)


def test_from_env_requires_all_three_variables():
    import pytest

    from alimi_scanner.connectors.m365 import GraphError

    with pytest.raises(GraphError, match="M365_CLIENT_SECRET"):
        GraphConnector.from_env({"M365_TENANT_ID": "t", "M365_CLIENT_ID": "c"})


def test_snapshot_serializes_without_tenant_id():
    snap = connector(fake_graph()).fetch()
    assert "tenant" not in json.dumps(snap.model_dump(mode="json")).replace("tenant_display_name", "")
