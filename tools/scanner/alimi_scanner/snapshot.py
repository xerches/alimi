"""The normalized picture of a tenant that checks run against.

A connector (Graph, Admin SDK or mock) fills one of these in. Checks never
call an API; they only read the snapshot. That is what makes every check
testable from a JSON fixture, and what lets the platform run the same checks
from stored data.

A field set to None means the connector could not read it, usually because
the credentials lack a permission or scope. Checks turn None into an "error"
finding with a note saying which permission is missing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BaseSnapshot(BaseModel):
    tenant_display_name: str | None = None
    verified_domains: list[str] = Field(default_factory=list)
    collected_at: datetime
    notes: list[str] = Field(default_factory=list)

    def custom_domains(self) -> list[str]:
        """Domains the company actually sends mail from, not the provider's default one."""
        return [d for d in self.verified_domains if not _is_provider_domain(d)]

    def primary_domain(self) -> str | None:
        custom = self.custom_domains()
        if custom:
            return custom[0]
        return self.verified_domains[0] if self.verified_domains else None

    def is_internal_address(self, address: str) -> bool:
        domain = address.rsplit("@", 1)[-1].lower()
        return domain in {d.lower() for d in self.verified_domains}


def _is_provider_domain(domain: str) -> bool:
    lowered = domain.lower()
    return lowered.endswith(".onmicrosoft.com") or lowered.endswith(".test-google-a.com")


# --------------------------------------------------------------------------- Microsoft 365


class User(BaseModel):
    id: str
    upn: str  # userPrincipalName
    display_name: str | None = None
    enabled: bool = True
    user_type: Literal["Member", "Guest"] = "Member"
    created: datetime | None = None
    last_sign_in: datetime | None = None
    has_mailbox: bool = False
    mfa_registered: bool | None = None
    mfa_methods: list[str] = Field(default_factory=list)


class ConditionalAccessPolicy(BaseModel):
    id: str
    display_name: str
    state: str  # enabled | disabled | enabledForReportingButNotEnforced
    include_users: list[str] = Field(default_factory=list)  # "All" or object ids
    exclude_users: list[str] = Field(default_factory=list)
    include_applications: list[str] = Field(default_factory=list)  # "All" or app ids
    client_app_types: list[str] = Field(default_factory=lambda: ["all"])
    grant_controls: list[str] = Field(default_factory=list)  # mfa | block | compliantDevice | ...

    @property
    def enabled(self) -> bool:
        return self.state == "enabled"

    @property
    def covers_all_users(self) -> bool:
        return "All" in self.include_users

    @property
    def covers_all_apps(self) -> bool:
        return "All" in self.include_applications

    @property
    def requires_mfa(self) -> bool:
        return "mfa" in self.grant_controls or "authenticationStrength" in self.grant_controls

    @property
    def blocks_legacy_auth(self) -> bool:
        legacy = {"exchangeActiveSync", "other"}
        return "block" in self.grant_controls and legacy.issubset(set(self.client_app_types))


class RoleAssignment(BaseModel):
    role_template_id: str
    role_name: str
    member_ids: list[str] = Field(default_factory=list)


class InboxRule(BaseModel):
    user_upn: str
    name: str
    enabled: bool = True
    forward_to: list[str] = Field(default_factory=list)
    redirect_to: list[str] = Field(default_factory=list)


class DomainEmailAuth(BaseModel):
    domain: str
    spf: str | None = None  # the TXT record, or None if absent / not looked up
    dkim_enabled: bool | None = None  # the provider's DKIM selector records are present
    dmarc: str | None = None  # the _dmarc TXT record


class SharingSettings(BaseModel):
    # Graph sharepointSettings.sharingCapability:
    # disabled | externalUserSharingOnly | externalUserAndGuestSharing | existingExternalUserSharingOnly
    sharing_capability: str | None = None
    anonymous_link_expiration_days: int | None = None  # not readable through Graph; SPO PowerShell only


class AuditSettings(BaseModel):
    unified_audit_log_enabled: bool | None = None  # Purview / Exchange Online only
    retention_days: int | None = None
    directory_audit_available: bool | None = None  # Entra audit logs reachable through Graph


class SecureScore(BaseModel):
    current: float
    max: float
    created: datetime | None = None

    @property
    def percent(self) -> float:
        return round(100.0 * self.current / self.max, 1) if self.max else 0.0


class M365Snapshot(BaseSnapshot):
    users: list[User] | None = None
    conditional_access_policies: list[ConditionalAccessPolicy] | None = None
    security_defaults_enabled: bool | None = None
    legacy_auth_sign_ins_30d: int | None = None
    role_assignments: list[RoleAssignment] | None = None
    inbox_rules: list[InboxRule] | None = None
    outbound_forwarding_blocked: bool | None = None
    email_auth: list[DomainEmailAuth] | None = None
    sharing: SharingSettings | None = None
    audit: AuditSettings | None = None
    secure_score: SecureScore | None = None

    def user_by_id(self, user_id: str) -> User | None:
        for user in self.users or []:
            if user.id == user_id:
                return user
        return None


# --------------------------------------------------------------------------- Google Workspace


class GWSUser(BaseModel):
    id: str
    email: str  # primaryEmail
    display_name: str | None = None
    suspended: bool = False
    archived: bool = False
    is_super_admin: bool = False  # Directory API isAdmin
    is_delegated_admin: bool = False
    enrolled_2sv: bool | None = None  # isEnrolledIn2Sv
    enforced_2sv: bool | None = None  # isEnforcedIn2Sv
    created: datetime | None = None
    last_login: datetime | None = None
    org_unit_path: str = "/"

    @property
    def active(self) -> bool:
        return not self.suspended and not self.archived


class GmailForwarding(BaseModel):
    user_email: str
    auto_forwarding_enabled: bool = False
    auto_forward_to: str | None = None
    filter_forward_to: list[str] = Field(default_factory=list)  # filters whose action forwards mail


class OAuthApp(BaseModel):
    client_id: str
    display_name: str | None = None
    client_type: str | None = None  # WEB | NATIVE_ANDROID | ...
    scopes: list[str] = Field(default_factory=list)
    user_count: int = 0
    last_authorized: datetime | None = None


class GWSPolicies(BaseModel):
    """Tenant settings read through the Cloud Identity Policy API, one field per setting we care about."""

    two_sv_enforced_everywhere: bool | None = None
    two_sv_unenforced_org_units: list[str] = Field(default_factory=list)
    less_secure_apps_allowed: bool | None = None
    auto_forwarding_allowed: bool | None = None
    external_sharing_mode: str | None = None  # ALLOWED | ALLOWLISTED_DOMAINS | DISALLOWED (as Google names them)
    allow_publishing_files: bool | None = None  # "anyone on the web" links
    warn_for_external_sharing: bool | None = None
    marketplace_access_level: str | None = None  # ALLOW_ALL | ALLOW_LISTED | ALLOW_NONE
    third_party_access_restricted: bool | None = None


class GWSAudit(BaseModel):
    login_available: bool | None = None
    admin_available: bool | None = None
    retention_days: int = 180  # Google keeps audit logs for six months


class GWSSnapshot(BaseSnapshot):
    users: list[GWSUser] | None = None
    policies: GWSPolicies | None = None
    forwarding: list[GmailForwarding] | None = None
    email_auth: list[DomainEmailAuth] | None = None
    third_party_apps: list[OAuthApp] | None = None
    approved_client_ids: list[str] = Field(default_factory=list)  # operator-provided allowlist
    audit: GWSAudit | None = None

    def user_by_email(self, email: str) -> GWSUser | None:
        for user in self.users or []:
            if user.email.lower() == email.lower():
                return user
        return None


Snapshot = M365Snapshot | GWSSnapshot
