"""The normalized picture of a Microsoft 365 tenant that checks run against.

A connector (Graph or mock) fills this in. Checks never call an API; they only
read the snapshot. That is what makes every check testable from a JSON
fixture, and what lets the platform run the same checks from stored data.

A field set to None means the connector could not read it, usually because
the app registration lacks the permission. Checks turn None into an "error"
finding with a note saying which permission is missing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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
    dkim_enabled: bool | None = None  # selector1/selector2 CNAMEs present
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


class M365Snapshot(BaseModel):
    tenant_display_name: str | None = None
    verified_domains: list[str] = Field(default_factory=list)
    collected_at: datetime
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
    notes: list[str] = Field(default_factory=list)

    def user_by_id(self, user_id: str) -> User | None:
        for user in self.users or []:
            if user.id == user_id:
                return user
        return None

    def custom_domains(self) -> list[str]:
        """Verified domains the company actually sends mail from, not the *.onmicrosoft.com default."""
        return [d for d in self.verified_domains if not d.lower().endswith(".onmicrosoft.com")]

    def primary_domain(self) -> str | None:
        custom = self.custom_domains()
        if custom:
            return custom[0]
        return self.verified_domains[0] if self.verified_domains else None

    def is_internal_address(self, address: str) -> bool:
        domain = address.rsplit("@", 1)[-1].lower()
        return domain in {d.lower() for d in self.verified_domains}
