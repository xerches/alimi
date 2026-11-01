"""Google Workspace connector: reads a tenant through the Admin SDK, the Cloud
Identity Policy API and the Gmail API, using a service account with
domain-wide delegation.

Read-only by construction. Every call is a GET or a list. A denied scope is
recorded as a note and leaves that part of the snapshot empty, so a scan with
partial delegation still produces a result that says exactly what it could not
see.

Never log or store the service account key or the customer id. The snapshot
carries the organization's name and verified domains only.

The connector talks to Google through the small GoogleApi protocol below, so
the normalizing logic is tested against a fake and the real wrapper
(DiscoveryGoogleApi) stays a thin shell around google-api-python-client.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol, TypeVar

from ..schema import Platform
from ..snapshot import GmailForwarding, GWSAudit, GWSPolicies, GWSSnapshot, GWSUser, OAuthApp

# OAuth scopes the service account needs delegated, all read-only. The README is generated from this list.
SCOPES: list[tuple[str, str, str]] = [
    (
        "https://www.googleapis.com/auth/admin.directory.customer.readonly",
        "organization name and primary domain",
        "Directory API customers.get",
    ),
    (
        "https://www.googleapis.com/auth/admin.directory.domain.readonly",
        "verified domains, for the SPF, DKIM and DMARC lookups",
        "Directory API domains.list",
    ),
    (
        "https://www.googleapis.com/auth/admin.directory.user.readonly",
        "user list: suspended, super admin, 2-Step Verification enrolled and enforced, org unit, last login",
        "Directory API users.list",
    ),
    (
        "https://www.googleapis.com/auth/admin.reports.audit.readonly",
        "third-party OAuth grants (token events) and login and admin audit log availability",
        "Reports API activities.list for token, login, admin",
    ),
    (
        "https://www.googleapis.com/auth/cloud-identity.policies.readonly",
        "2-Step Verification enforcement, less secure apps, Gmail auto-forwarding, Drive external sharing, Marketplace access",
        "Cloud Identity Policy API policies.list",
    ),
    (
        "https://www.googleapis.com/auth/gmail.readonly",
        "each user's automatic forwarding address and filters that forward mail",
        "Gmail API users.settings.getAutoForwarding, users.settings.filters.list (as each user)",
    ),
]
SCOPE_URLS = [scope for scope, _, _ in SCOPES]

ENV_KEY_FILE = "GWS_SERVICE_ACCOUNT_FILE"
ENV_ADMIN = "GWS_DELEGATED_ADMIN"
ENV_CUSTOMER = "GWS_CUSTOMER_ID"
ENV_APPROVED = "GWS_APPROVED_CLIENT_IDS"

# Policy API setting types, matched by suffix so a future "settings/" prefix change does not matter.
SETTING_2SV = "security.two_step_verification_enforcement"
SETTING_LSA = "security.less_secure_apps"
SETTING_AUTO_FORWARDING = "gmail.auto_forwarding"
SETTING_DRIVE_SHARING = "drive_and_docs.external_sharing"
SETTING_MARKETPLACE = "workspace_marketplace.apps_access_options"

SHARING_MODES_MOST_OPEN_FIRST = ("ALLOWED", "ALLOWLISTED_DOMAINS", "DISALLOWED")
MARKETPLACE_LEVELS_MOST_OPEN_FIRST = ("ALLOW_ALL", "ALLOW_LISTED", "ALLOW_NONE")

T = TypeVar("T")


class GoogleError(RuntimeError):
    """Configuration or transport problem that stops a call (not a denied scope)."""


class ApiDenied(GoogleError):
    """The API refused the call: scope not delegated, admin privilege missing, or API not enabled."""


class GoogleApi(Protocol):
    """The handful of read-only calls the connector makes. Each raises ApiDenied on 401/403."""

    def get_customer(self) -> dict[str, Any]: ...

    def list_domains(self) -> list[dict[str, Any]]: ...

    def list_users(self) -> list[dict[str, Any]]: ...

    def list_activities(self, application: str, *, start: datetime, event_name: str | None = None, cap: int = 5000) -> list[dict[str, Any]]: ...

    def list_policies(self) -> list[dict[str, Any]]: ...

    def get_auto_forwarding(self, user_email: str) -> dict[str, Any]: ...

    def list_filters(self, user_email: str) -> list[dict[str, Any]]: ...


class GoogleWorkspaceConnector:
    platform = Platform.gws
    source = "admin-sdk"

    def __init__(
        self,
        api: GoogleApi,
        *,
        dns: bool = True,
        approved_client_ids: Iterable[str] = (),
        max_mailbox_users: int = 500,
        token_event_cap: int = 5000,
        oauth_lookback_days: int = 180,
        audit_lookback_days: int = 90,
        now: datetime | None = None,
    ):
        self._api = api
        self._dns = dns
        self._approved = [c for c in approved_client_ids if c]
        self._max_mailbox_users = max_mailbox_users
        self._token_event_cap = token_event_cap
        self._oauth_lookback = timedelta(days=oauth_lookback_days)
        self._audit_lookback = timedelta(days=audit_lookback_days)
        self._now = now
        self._notes: list[str] = []

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None, **kwargs: Any) -> GoogleWorkspaceConnector:
        env = env if env is not None else os.environ
        missing = [name for name in (ENV_KEY_FILE, ENV_ADMIN) if not env.get(name)]
        if missing:
            raise GoogleError(f"missing environment variables: {', '.join(missing)} (copy .env.example to .env and fill them in)")
        key_file = env[ENV_KEY_FILE]
        if not os.path.isfile(key_file):
            raise GoogleError(f"{ENV_KEY_FILE} points to a file that does not exist. Keep the key outside the repo; it is git-ignored anyway.")
        approved = kwargs.pop("approved_client_ids", None)
        if not approved:
            approved = [c.strip() for c in env.get(ENV_APPROVED, "").split(",") if c.strip()]
        api = DiscoveryGoogleApi(key_file, env[ENV_ADMIN], env.get(ENV_CUSTOMER) or "my_customer")
        return cls(api, approved_client_ids=approved, **kwargs)

    # ----- helpers -----

    def _try(self, what: str, call: Callable[[], T]) -> T | None:
        try:
            return call()
        except ApiDenied as exc:
            self._notes.append(f"{what}: permission denied ({exc}); delegate the scope listed in the README to the service account.")
        except GoogleError as exc:
            self._notes.append(f"{what}: Google returned an error: {exc}")
        return None

    # ----- snapshot -----

    def fetch(self) -> GWSSnapshot:
        now = self._now or datetime.now(timezone.utc)
        snapshot = GWSSnapshot(collected_at=now, approved_client_ids=list(self._approved))
        self._fetch_customer(snapshot)
        self._fetch_domains(snapshot)
        self._fetch_users(snapshot)
        self._fetch_policies(snapshot)
        self._fetch_forwarding(snapshot)
        self._fetch_email_auth(snapshot)
        self._fetch_oauth_apps(snapshot, now)
        self._fetch_audit(snapshot, now)
        snapshot.notes = list(dict.fromkeys(self._notes))
        return snapshot

    def _fetch_customer(self, snapshot: GWSSnapshot) -> None:
        customer = self._try("organization", self._api.get_customer)
        if not customer:
            return
        name = (customer.get("postalAddress") or {}).get("organizationName")
        snapshot.tenant_display_name = name or customer.get("customerDomain")
        if customer.get("customerDomain"):
            snapshot.verified_domains = [customer["customerDomain"]]

    def _fetch_domains(self, snapshot: GWSSnapshot) -> None:
        rows = self._try("domains", self._api.list_domains)
        if rows is None:
            return
        verified = [d["domainName"] for d in rows if d.get("domainName") and d.get("verified", True)]
        primary = [d["domainName"] for d in rows if d.get("isPrimary") and d.get("domainName")]
        ordered = primary + [d for d in verified if d not in primary]
        for existing in snapshot.verified_domains:
            if existing not in ordered:
                ordered.append(existing)
        snapshot.verified_domains = ordered

    def _fetch_users(self, snapshot: GWSSnapshot) -> None:
        rows = self._try("users", self._api.list_users)
        if rows is None:
            return
        snapshot.users = [
            GWSUser(
                id=str(row.get("id") or row["primaryEmail"]),
                email=row["primaryEmail"],
                display_name=(row.get("name") or {}).get("fullName"),
                suspended=bool(row.get("suspended", False)),
                archived=bool(row.get("archived", False)),
                is_super_admin=bool(row.get("isAdmin", False)),
                is_delegated_admin=bool(row.get("isDelegatedAdmin", False)),
                enrolled_2sv=_opt_bool(row.get("isEnrolledIn2Sv")),
                enforced_2sv=_opt_bool(row.get("isEnforcedIn2Sv")),
                created=_dt(row.get("creationTime")),
                last_login=_dt(row.get("lastLoginTime")),
                org_unit_path=row.get("orgUnitPath") or "/",
            )
            for row in rows
            if row.get("primaryEmail")
        ]

    def _fetch_policies(self, snapshot: GWSSnapshot) -> None:
        rows = self._try("policies", self._api.list_policies)
        if rows is None:
            return
        snapshot.policies = parse_policies(rows, now=snapshot.collected_at, users=snapshot.users or [])
        # The API controls setting for unconfigured third-party apps is not a Policy API setting.
        self._notes.append(
            "Whether unconfigured third-party apps are restricted (Admin console > Security > API controls) is not readable "
            "through an API; the third-party app check asks for a screenshot."
        )

    def _fetch_forwarding(self, snapshot: GWSSnapshot) -> None:
        if snapshot.users is None:
            return
        candidates = [u for u in snapshot.users if u.active]
        if len(candidates) > self._max_mailbox_users:
            self._notes.append(f"Forwarding settings were read for the first {self._max_mailbox_users} of {len(candidates)} mailboxes.")
            candidates = candidates[: self._max_mailbox_users]
        results: list[GmailForwarding] = []
        skipped = 0
        for user in candidates:
            try:
                auto = self._api.get_auto_forwarding(user.email)
                filters = self._api.list_filters(user.email)
            except ApiDenied as exc:
                self._notes.append(
                    f"Gmail settings: permission denied for {user.email} ({exc}); delegate the gmail.readonly scope to read forwarding."
                )
                return
            except GoogleError:
                skipped += 1  # no Gmail licence (Cloud Identity user) or a mailbox the API cannot open
                continue
            results.append(
                GmailForwarding(
                    user_email=user.email,
                    auto_forwarding_enabled=bool(auto.get("enabled", False)),
                    auto_forward_to=auto.get("emailAddress") or None,
                    filter_forward_to=[f["action"]["forward"] for f in filters if (f.get("action") or {}).get("forward")],
                )
            )
        if skipped:
            self._notes.append(f"{skipped} user(s) have no Gmail mailbox the API could open; their forwarding settings were skipped.")
        snapshot.forwarding = results

    def _fetch_email_auth(self, snapshot: GWSSnapshot) -> None:
        if not self._dns:
            self._notes.append("DNS lookups were skipped (--no-dns), so SPF, DKIM and DMARC were not checked.")
            return
        from . import dns_lookup

        results = []
        for domain in snapshot.custom_domains():
            try:
                results.append(dns_lookup.lookup_domain(domain, dns_lookup.GOOGLE_DKIM_SELECTORS))
            except dns_lookup.DNSError as exc:
                self._notes.append(f"DNS lookup failed for {domain}: {exc}")
                return
        snapshot.email_auth = results

    def _fetch_oauth_apps(self, snapshot: GWSSnapshot, now: datetime) -> None:
        start = now - self._oauth_lookback
        rows = self._try(
            "OAuth token events",
            lambda: self._api.list_activities("token", start=start, event_name="authorize", cap=self._token_event_cap),
        )
        if rows is None:
            return
        snapshot.third_party_apps = aggregate_token_events(rows)
        if len(rows) >= self._token_event_cap:
            self._notes.append(f"OAuth grant events stopped at {self._token_event_cap}; apps authorized earlier in the window may be missing.")
        self._notes.append(
            f"Third-party apps are those authorized in the last {self._oauth_lookback.days} days (the Reports API retention); "
            "older grants that are still active do not appear."
        )

    def _fetch_audit(self, snapshot: GWSSnapshot, now: datetime) -> None:
        start = now - self._audit_lookback
        audit = GWSAudit()
        for application, field in (("login", "login_available"), ("admin", "admin_available")):
            try:
                self._api.list_activities(application, start=start, cap=1)
                setattr(audit, field, True)
            except ApiDenied as exc:
                self._notes.append(f"{application} audit log: permission denied ({exc}); delegate admin.reports.audit.readonly.")
            except GoogleError as exc:
                self._notes.append(f"{application} audit log: Google returned an error: {exc}")
                setattr(audit, field, False)
        snapshot.audit = audit


# --------------------------------------------------------------------------- pure parsing helpers


def parse_policies(rows: list[dict[str, Any]], *, now: datetime, users: list[GWSUser]) -> GWSPolicies:
    """Fold the Policy API list into one GWSPolicies, taking the most permissive value across org units.

    A setting can appear once per org unit (and per group). An insurer asks whether the whole company is
    protected, so the loosest org unit decides. Unenforced org units are named from the users' isEnforcedIn2Sv
    flag, because the Policy API refers to org units by id and the paths need another scope.
    """
    policies = GWSPolicies()
    by_setting: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        setting = row.get("setting") or {}
        setting_type = str(setting.get("type") or "")
        value = setting.get("value") or {}
        for key in (SETTING_2SV, SETTING_LSA, SETTING_AUTO_FORWARDING, SETTING_DRIVE_SHARING, SETTING_MARKETPLACE):
            if setting_type.endswith(key):
                by_setting.setdefault(key, []).append(value)

    if SETTING_2SV in by_setting:
        enforced = []
        for value in by_setting[SETTING_2SV]:
            enforced_from = _dt(_v(value, "enforcedFrom", "enforced_from"))
            enforced.append(enforced_from is not None and enforced_from <= now)
        policies.two_sv_enforced_everywhere = all(enforced)
    policies.two_sv_unenforced_org_units = sorted({u.org_unit_path for u in users if u.active and u.enforced_2sv is False})
    if policies.two_sv_unenforced_org_units and policies.two_sv_enforced_everywhere is None:
        policies.two_sv_enforced_everywhere = False

    if SETTING_LSA in by_setting:
        policies.less_secure_apps_allowed = any(bool(_v(v, "allowLessSecureApps", "allow_less_secure_apps")) for v in by_setting[SETTING_LSA])

    if SETTING_AUTO_FORWARDING in by_setting:
        policies.auto_forwarding_allowed = any(bool(_v(v, "enableAutoForwarding", "enable_auto_forwarding")) for v in by_setting[SETTING_AUTO_FORWARDING])

    if SETTING_DRIVE_SHARING in by_setting:
        values = by_setting[SETTING_DRIVE_SHARING]
        modes = {str(_v(v, "externalSharingMode", "external_sharing_mode") or "ALLOWED") for v in values}
        policies.external_sharing_mode = next((m for m in SHARING_MODES_MOST_OPEN_FIRST if m in modes), sorted(modes)[0])
        policies.allow_publishing_files = any(bool(_v(v, "allowPublishingFiles", "allow_publishing_files")) for v in values)
        policies.warn_for_external_sharing = all(bool(_v(v, "warnForExternalSharing", "warn_for_external_sharing")) for v in values)

    if SETTING_MARKETPLACE in by_setting:
        levels = {str(_v(v, "accessLevel", "access_level") or "ALLOW_ALL") for v in by_setting[SETTING_MARKETPLACE]}
        policies.marketplace_access_level = next((m for m in MARKETPLACE_LEVELS_MOST_OPEN_FIRST if m in levels), sorted(levels)[0])

    policies.third_party_access_restricted = None  # not exposed by any API; the check asks for a screenshot
    return policies


def aggregate_token_events(rows: list[dict[str, Any]]) -> list[OAuthApp]:
    """Turn Reports API token/authorize events into one OAuthApp per client id."""
    apps: dict[str, OAuthApp] = {}
    users: dict[str, set[str]] = {}
    for row in rows:
        when = _dt((row.get("id") or {}).get("time"))
        actor = (row.get("actor") or {}).get("email") or (row.get("actor") or {}).get("profileId") or ""
        for event in row.get("events") or []:
            if event.get("name") not in (None, "authorize"):
                continue
            params = _params(event.get("parameters") or [])
            client_id = str(params.get("client_id") or "")
            if not client_id:
                continue
            app = apps.get(client_id)
            if app is None:
                app = OAuthApp(client_id=client_id)
                apps[client_id] = app
                users[client_id] = set()
            app.display_name = app.display_name or params.get("app_name")
            app.client_type = app.client_type or params.get("client_type")
            scopes = params.get("scope") or []
            if isinstance(scopes, str):
                scopes = [scopes]
            app.scopes = sorted(set(app.scopes) | set(scopes))
            if actor:
                users[client_id].add(actor.lower())
            if when and (app.last_authorized is None or when > app.last_authorized):
                app.last_authorized = when
    for client_id, app in apps.items():
        app.user_count = len(users[client_id])
    return sorted(apps.values(), key=lambda a: (-a.user_count, a.display_name or a.client_id))


def _params(parameters: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for param in parameters:
        name = param.get("name")
        if not name:
            continue
        if "multiValue" in param:
            out[name] = list(param["multiValue"])
        elif "boolValue" in param:
            out[name] = bool(param["boolValue"])
        elif "intValue" in param:
            out[name] = param["intValue"]
        else:
            out[name] = param.get("value")
    return out


def _v(value: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in value:
            return value[key]
    return None


def _opt_bool(value: Any) -> bool | None:
    return None if value is None else bool(value)


def _dt(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    if parsed.year <= 1970:  # Google's "never logged in" sentinel
        return None
    return parsed


# --------------------------------------------------------------------------- the real wrapper


class DiscoveryGoogleApi:
    """GoogleApi backed by google-api-python-client. Imported lazily so mock mode never needs the Google libraries."""

    def __init__(self, service_account_file: str, delegated_admin: str, customer_id: str = "my_customer"):
        from google.oauth2 import service_account

        self._base = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPE_URLS)
        self._admin = self._base.with_subject(delegated_admin)
        self._customer = customer_id
        self._services: dict[tuple[str, str, str], Any] = {}

    def _service(self, name: str, version: str, subject: str | None = None) -> Any:
        from googleapiclient.discovery import build

        key = (name, version, subject or "")
        if key not in self._services:
            creds = self._base.with_subject(subject) if subject else self._admin
            self._services[key] = build(name, version, credentials=creds, cache_discovery=False)
        return self._services[key]

    @staticmethod
    def _call(what: str, request: Callable[[], Any]) -> Any:
        from google.auth.exceptions import RefreshError
        from googleapiclient.errors import HttpError

        try:
            return request()
        except HttpError as exc:
            status = int(getattr(exc.resp, "status", 0) or 0)
            if status in (401, 403):
                raise ApiDenied(f"{what}: HTTP {status}") from exc
            raise GoogleError(f"{what}: HTTP {status}") from exc
        except RefreshError as exc:
            raise ApiDenied(f"{what}: token refused, the scope is probably not delegated") from exc

    def _pages(self, what: str, make_request: Callable[[str | None], Any], key: str, cap: int | None = None) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        token: str | None = None
        while True:
            page = self._call(what, lambda: make_request(token).execute()) or {}
            items.extend(page.get(key) or [])
            token = page.get("nextPageToken")
            if not token or (cap is not None and len(items) >= cap):
                return items

    def get_customer(self) -> dict[str, Any]:
        directory = self._service("admin", "directory_v1")
        return self._call("customers.get", lambda: directory.customers().get(customerKey=self._customer).execute())

    def list_domains(self) -> list[dict[str, Any]]:
        directory = self._service("admin", "directory_v1")
        return self._call("domains.list", lambda: directory.domains().list(customer=self._customer).execute()).get("domains") or []

    def list_users(self) -> list[dict[str, Any]]:
        directory = self._service("admin", "directory_v1")
        fields = (
            "nextPageToken,users(id,primaryEmail,name/fullName,suspended,archived,isAdmin,isDelegatedAdmin,"
            "isEnrolledIn2Sv,isEnforcedIn2Sv,creationTime,lastLoginTime,orgUnitPath)"
        )
        return self._pages(
            "users.list",
            lambda token: directory.users().list(customer=self._customer, maxResults=500, pageToken=token, fields=fields),
            "users",
        )

    def list_activities(self, application: str, *, start: datetime, event_name: str | None = None, cap: int = 5000) -> list[dict[str, Any]]:
        reports = self._service("admin", "reports_v1")
        params: dict[str, Any] = {
            "userKey": "all",
            "applicationName": application,
            "startTime": start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "maxResults": min(cap, 1000),
        }
        if event_name:
            params["eventName"] = event_name
        return self._pages(
            f"activities.list({application})",
            lambda token: reports.activities().list(pageToken=token, **params),
            "items",
            cap=cap,
        )

    def list_policies(self) -> list[dict[str, Any]]:
        identity = self._service("cloudidentity", "v1")
        return self._pages("policies.list", lambda token: identity.policies().list(pageSize=100, pageToken=token), "policies")

    def get_auto_forwarding(self, user_email: str) -> dict[str, Any]:
        gmail = self._service("gmail", "v1", subject=user_email)
        return self._call("getAutoForwarding", lambda: gmail.users().settings().getAutoForwarding(userId="me").execute())

    def list_filters(self, user_email: str) -> list[dict[str, Any]]:
        gmail = self._service("gmail", "v1", subject=user_email)
        return self._call("filters.list", lambda: gmail.users().settings().filters().list(userId="me").execute()).get("filter") or []
