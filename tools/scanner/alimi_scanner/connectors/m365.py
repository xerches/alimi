"""Microsoft 365 connector: reads a tenant through Microsoft Graph with application permissions.

Read-only by construction. Every call is a GET. A 403 on any call is recorded
as a note and leaves that part of the snapshot empty, so a scan with partial
permissions still produces a result that says exactly what it could not see.

Never log or store the client secret or the tenant id. The snapshot carries
the tenant's display name and verified domains only.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from ..schema import Platform
from ..snapshot import (
    AuditSettings,
    ConditionalAccessPolicy,
    InboxRule,
    M365Snapshot,
    RoleAssignment,
    SecureScore,
    SharingSettings,
    User,
)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"

# Application permissions the app registration needs, all read-only. The README is generated from this list.
PERMISSIONS: list[tuple[str, str, str]] = [
    ("Organization.Read.All", "tenant name and verified domains", "GET /organization"),
    ("User.Read.All", "user list: member or guest, enabled, mailbox present, sign-in activity", "GET /users"),
    (
        "AuditLog.Read.All",
        "MFA registration report, last sign-in dates, legacy-auth sign-ins, audit log availability",
        "GET /reports/authenticationMethods/userRegistrationDetails, /auditLogs/signIns, /auditLogs/directoryAudits",
    ),
    (
        "Policy.Read.All",
        "Conditional Access policies and the Security Defaults switch",
        "GET /identity/conditionalAccess/policies, /policies/identitySecurityDefaultsEnforcementPolicy",
    ),
    ("RoleManagement.Read.Directory", "who holds Global Administrator and other privileged roles", "GET /directoryRoles?$expand=members"),
    ("MailboxSettings.Read", "inbox rules that forward or redirect mail", "GET /users/{id}/mailFolders/inbox/messageRules"),
    ("SharePointTenantSettings.Read.All", "tenant sharing level (anyone links)", "GET /admin/sharepoint/settings"),
    ("SecurityEvents.Read.All", "Microsoft Secure Score", "GET /security/secureScores"),
]

# clientAppUsed values in sign-in logs that mean a legacy protocol that cannot do MFA.
LEGACY_CLIENT_APPS = [
    "Exchange ActiveSync",
    "IMAP4",
    "POP3",
    "SMTP",
    "Authenticated SMTP",
    "Other clients",
    "Outlook Anywhere (RPC over HTTP)",
    "Offline Address Book",
    "Reporting Web Services",
]

ENV_TENANT = "M365_TENANT_ID"
ENV_CLIENT = "M365_CLIENT_ID"
ENV_SECRET = "M365_CLIENT_SECRET"


class GraphError(RuntimeError):
    pass


class GraphConnector:
    platform = Platform.m365
    source = "graph"

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        *,
        client: httpx.Client | None = None,
        token_provider: Callable[[], str] | None = None,
        dns: bool = True,
        max_inbox_users: int = 500,
        legacy_sign_in_cap: int = 5000,
        now: datetime | None = None,
    ):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._client = client or httpx.Client(base_url=GRAPH_BASE, timeout=30.0)
        self._token_provider = token_provider or self._msal_token
        self._dns = dns
        self._max_inbox_users = max_inbox_users
        self._legacy_sign_in_cap = legacy_sign_in_cap
        self._now = now
        self._notes: list[str] = []
        self._token: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None, **kwargs: Any) -> GraphConnector:
        env = env if env is not None else os.environ
        missing = [name for name in (ENV_TENANT, ENV_CLIENT, ENV_SECRET) if not env.get(name)]
        if missing:
            raise GraphError(f"missing environment variables: {', '.join(missing)} (copy .env.example to .env and fill them in)")
        return cls(env[ENV_TENANT], env[ENV_CLIENT], env[ENV_SECRET], **kwargs)

    # ----- transport -----

    def _msal_token(self) -> str:
        import msal  # imported here so the mock path never needs it

        app = msal.ConfidentialClientApplication(
            self._client_id,
            authority=f"https://login.microsoftonline.com/{self._tenant_id}",
            client_credential=self._client_secret,
        )
        result = app.acquire_token_for_client(scopes=[GRAPH_SCOPE])
        if "access_token" not in result:
            raise GraphError(f"token request failed: {result.get('error')}: {result.get('error_description')}")
        return result["access_token"]

    def _headers(self) -> dict[str, str]:
        if self._token is None:
            self._token = self._token_provider()
        return {"Authorization": f"Bearer {self._token}", "ConsistencyLevel": "eventual"}

    def _request(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        refreshed = False
        for attempt in range(4):
            response = self._client.get(url, params=params, headers=self._headers())
            if response.status_code in (429, 503) and attempt < 3:
                wait = float(response.headers.get("Retry-After", 2 ** attempt))
                time.sleep(min(wait, 30))
                continue
            if response.status_code == 401 and not refreshed:
                # A token lasts about an hour; a scan over hundreds of mailboxes can outlive it. Get a new one
                # once, so an expired token is not reported as a missing permission.
                self._token = None
                refreshed = True
                continue
            return response
        return response  # pragma: no cover - loop always returns

    def _get(self, path: str, params: dict[str, Any] | None = None, *, what: str) -> dict[str, Any] | None:
        response = self._request(path, params)
        if response.status_code in (401, 403):
            self._notes.append(f"{what}: permission denied (HTTP {response.status_code}); grant and consent the permission listed in the README.")
            return None
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            self._notes.append(f"{what}: Graph returned HTTP {response.status_code}: {response.text[:200]}")
            return None
        return response.json()

    def _get_all(self, path: str, params: dict[str, Any] | None = None, *, what: str, cap: int | None = None) -> list[dict[str, Any]] | None:
        items: list[dict[str, Any]] = []
        page = self._get(path, params, what=what)
        if page is None:
            return None
        while True:
            items.extend(page.get("value", []))
            next_link = page.get("@odata.nextLink")
            if not next_link or (cap is not None and len(items) >= cap):
                break
            page = self._get(next_link, what=what)
            if page is None:
                break
        return items

    # ----- snapshot -----

    def fetch(self) -> M365Snapshot:
        now = self._now or datetime.now(timezone.utc)
        org = self._get("/organization", what="organization")
        tenant_name = None
        domains: list[str] = []
        if org and org.get("value"):
            record = org["value"][0]
            tenant_name = record.get("displayName")
            domains = [d["name"] for d in record.get("verifiedDomains", []) if d.get("name")]
            # the default domain first, so TenantInfo.primary_domain picks it
            default = [d["name"] for d in record.get("verifiedDomains", []) if d.get("isDefault")]
            if default:
                domains = default + [d for d in domains if d not in default]
        snapshot = M365Snapshot(tenant_display_name=tenant_name, verified_domains=domains, collected_at=now)

        self._fetch_users(snapshot)
        self._fetch_mfa_registration(snapshot)
        self._fetch_conditional_access(snapshot)
        self._fetch_security_defaults(snapshot)
        self._fetch_legacy_sign_ins(snapshot, now)
        self._fetch_roles(snapshot)
        self._fetch_inbox_rules(snapshot)
        snapshot.outbound_forwarding_blocked = None
        self._notes.append(
            "Tenant-wide automatic forwarding (outbound spam policy) is not exposed by Graph; the forwarding check asks for a screenshot."
        )
        self._fetch_email_auth(snapshot)
        self._fetch_sharing(snapshot)
        self._fetch_audit(snapshot)
        self._fetch_secure_score(snapshot)
        snapshot.notes = list(dict.fromkeys(self._notes))
        return snapshot

    def _fetch_users(self, snapshot: M365Snapshot) -> None:
        select = "id,userPrincipalName,displayName,accountEnabled,userType,createdDateTime,mail,signInActivity"
        rows = self._get_all("/users", {"$select": select, "$top": 999}, what="users")
        if rows is None:
            # signInActivity needs Entra ID P1; without it Graph refuses the whole query. Try again without it.
            select = select.replace(",signInActivity", "")
            rows = self._get_all("/users", {"$select": select, "$top": 999}, what="users")
            if rows is not None:
                self._notes.append("Sign-in activity was not available (needs Entra ID P1 and AuditLog.Read.All).")
        if rows is None:
            return
        users = []
        for row in rows:
            activity = row.get("signInActivity") or {}
            users.append(
                User(
                    id=row["id"],
                    upn=row.get("userPrincipalName") or row["id"],
                    display_name=row.get("displayName"),
                    enabled=bool(row.get("accountEnabled", True)),
                    user_type="Guest" if row.get("userType") == "Guest" else "Member",
                    created=_dt(row.get("createdDateTime")),
                    last_sign_in=_dt(activity.get("lastSignInDateTime")),
                    has_mailbox=bool(row.get("mail")),
                )
            )
        snapshot.users = users

    def _fetch_mfa_registration(self, snapshot: M365Snapshot) -> None:
        if snapshot.users is None:
            return
        rows = self._get_all(
            "/reports/authenticationMethods/userRegistrationDetails", {"$top": 999}, what="MFA registration report"
        )
        if rows is None:
            return
        by_id = {row["id"]: row for row in rows}
        for user in snapshot.users:
            row = by_id.get(user.id)
            if row is None:
                continue
            user.mfa_registered = bool(row.get("isMfaRegistered"))
            user.mfa_methods = list(row.get("methodsRegistered") or [])

    def _fetch_conditional_access(self, snapshot: M365Snapshot) -> None:
        rows = self._get_all("/identity/conditionalAccess/policies", what="Conditional Access policies")
        if rows is None:
            return
        policies = []
        for row in rows:
            conditions = row.get("conditions") or {}
            grant = row.get("grantControls") or {}
            controls = list(grant.get("builtInControls") or [])
            if grant.get("authenticationStrength"):
                controls.append("authenticationStrength")
            policies.append(
                ConditionalAccessPolicy(
                    id=row["id"],
                    display_name=row.get("displayName", row["id"]),
                    state=row.get("state", "disabled"),
                    include_users=list((conditions.get("users") or {}).get("includeUsers") or []),
                    exclude_users=list((conditions.get("users") or {}).get("excludeUsers") or []),
                    include_applications=list((conditions.get("applications") or {}).get("includeApplications") or []),
                    client_app_types=list(conditions.get("clientAppTypes") or ["all"]),
                    grant_controls=controls,
                )
            )
        snapshot.conditional_access_policies = policies

    def _fetch_security_defaults(self, snapshot: M365Snapshot) -> None:
        row = self._get("/policies/identitySecurityDefaultsEnforcementPolicy", what="Security Defaults")
        if row is not None:
            snapshot.security_defaults_enabled = bool(row.get("isEnabled"))

    def _fetch_legacy_sign_ins(self, snapshot: M365Snapshot, now: datetime) -> None:
        since = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        apps = " or ".join(f"clientAppUsed eq '{app}'" for app in LEGACY_CLIENT_APPS)
        params = {
            "$filter": f"createdDateTime ge {since} and status/errorCode eq 0 and ({apps})",
            "$select": "id,clientAppUsed",
            "$top": 999,
        }
        rows = self._get_all("/auditLogs/signIns", params, what="sign-in logs", cap=self._legacy_sign_in_cap)
        if rows is None:
            self._notes.append("Legacy-auth sign-ins could not be counted (sign-in logs need Entra ID P1 and AuditLog.Read.All).")
            return
        snapshot.legacy_auth_sign_ins_30d = len(rows)
        if len(rows) >= self._legacy_sign_in_cap:
            self._notes.append(f"Legacy sign-in count stopped at {self._legacy_sign_in_cap}; the real number is higher.")

    def _fetch_roles(self, snapshot: M365Snapshot) -> None:
        rows = self._get_all("/directoryRoles", {"$expand": "members($select=id)"}, what="directory roles")
        if rows is None:
            return
        snapshot.role_assignments = [
            RoleAssignment(
                role_template_id=row.get("roleTemplateId", ""),
                role_name=row.get("displayName", ""),
                member_ids=[m["id"] for m in row.get("members", []) if m.get("id")],
            )
            for row in rows
        ]
        self._notes.append("Role members are active assignments only; PIM-eligible assignments are not included.")

    def _fetch_inbox_rules(self, snapshot: M365Snapshot) -> None:
        if snapshot.users is None:
            return
        candidates = [u for u in snapshot.users if u.enabled and u.user_type == "Member" and u.has_mailbox]
        if len(candidates) > self._max_inbox_users:
            self._notes.append(f"Inbox rules were read for the first {self._max_inbox_users} of {len(candidates)} mailboxes.")
            candidates = candidates[: self._max_inbox_users]
        rules: list[InboxRule] = []
        for user in candidates:
            response = self._request(f"/users/{user.id}/mailFolders/inbox/messageRules")
            if response.status_code in (401, 403):
                self._notes.append("inbox rules: permission denied; grant MailboxSettings.Read to read forwarding rules.")
                return
            if response.status_code >= 400:
                continue  # no mailbox, or a mailbox Graph cannot open; skip it
            for row in response.json().get("value", []):
                actions = row.get("actions") or {}
                rules.append(
                    InboxRule(
                        user_upn=user.upn,
                        name=row.get("displayName") or "(unnamed rule)",
                        enabled=bool(row.get("isEnabled", True)),
                        forward_to=_addresses(actions.get("forwardTo")) + _addresses(actions.get("forwardAsAttachmentTo")),
                        redirect_to=_addresses(actions.get("redirectTo")),
                    )
                )
        snapshot.inbox_rules = rules

    def _fetch_email_auth(self, snapshot: M365Snapshot) -> None:
        if not self._dns:
            self._notes.append("DNS lookups were skipped (--no-dns), so SPF, DKIM and DMARC were not checked.")
            return
        from . import dns_lookup

        results = []
        for domain in snapshot.custom_domains():
            try:
                results.append(dns_lookup.lookup_domain(domain))
            except dns_lookup.DNSError as exc:
                self._notes.append(f"DNS lookup failed for {domain}: {exc}")
                return
        snapshot.email_auth = results

    def _fetch_sharing(self, snapshot: M365Snapshot) -> None:
        row = self._get("/admin/sharepoint/settings", what="SharePoint settings")
        if row is None:
            return
        snapshot.sharing = SharingSettings(sharing_capability=row.get("sharingCapability"), anonymous_link_expiration_days=None)
        if row.get("sharingCapability") == "externalUserAndGuestSharing":
            self._notes.append(
                "Anyone-link expiry is only visible in SharePoint PowerShell (Get-SPOTenant RequireAnonymousLinksExpireInDays)."
            )

    def _fetch_audit(self, snapshot: M365Snapshot) -> None:
        row = self._get("/auditLogs/directoryAudits", {"$top": 1}, what="directory audit logs")
        snapshot.audit = AuditSettings(
            unified_audit_log_enabled=None,
            retention_days=None,
            directory_audit_available=row is not None,
        )
        self._notes.append("Unified audit log state and retention are only visible in Microsoft Purview; the audit check asks for a screenshot.")

    def _fetch_secure_score(self, snapshot: M365Snapshot) -> None:
        row = self._get("/security/secureScores", {"$top": 1}, what="Secure Score")
        if not row or not row.get("value"):
            return
        latest = row["value"][0]
        snapshot.secure_score = SecureScore(
            current=float(latest.get("currentScore", 0)),
            max=float(latest.get("maxScore", 0)),
            created=_dt(latest.get("createdDateTime")),
        )


def _dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _addresses(recipients: list[dict[str, Any]] | None) -> list[str]:
    out = []
    for recipient in recipients or []:
        address = (recipient.get("emailAddress") or {}).get("address")
        if address:
            out.append(address)
    return out
