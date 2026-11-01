"""Microsoft 365 checks, one function per m365.* id in config/checks.yaml.

Each function reads the snapshot and returns a CheckOutcome. It never calls
Graph. A None field in the snapshot means the connector could not read it,
and the check reports an error that names the missing permission instead of
guessing.
"""

from __future__ import annotations

import re
from datetime import timedelta

from ..engine import check
from ..schema import CheckDefinition, CheckOutcome, Status
from ..snapshot import M365Snapshot, User

GLOBAL_ADMIN_TEMPLATE = "62e90394-69f5-4237-9190-012177145e10"

# Entra directory role template ids that can change the tenant's security posture.
PRIVILEGED_ROLE_TEMPLATES: dict[str, str] = {
    GLOBAL_ADMIN_TEMPLATE: "Global Administrator",
    "e8611ab8-c189-46e8-94e1-60213ab1f814": "Privileged Role Administrator",
    "194ae4cb-b126-40b2-bd5b-6091b380977d": "Security Administrator",
    "29232cdf-9323-42fd-ade2-1d097af3e4de": "Exchange Administrator",
    "f28a1f50-f6e7-4571-818b-6a12f2af6b6c": "SharePoint Administrator",
    "fe930be7-5e62-47db-91af-98c3a49a38b1": "User Administrator",
    "b1be1c3e-b65d-4f19-8427-f6fa0d97feb9": "Conditional Access Administrator",
    "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3": "Application Administrator",
    "158c047a-c907-4556-b7ef-446551a6b5f7": "Cloud Application Administrator",
    "c4e39bd9-1100-46d3-8c65-fb160da0071f": "Authentication Administrator",
    "7be44c8a-adaf-4e2a-84d6-ab2649e08a13": "Privileged Authentication Administrator",
    "729827e3-9c14-49f7-bb1b-9608f156bbb8": "Helpdesk Administrator",
    "966707d0-3269-4727-9be2-8c3a10f19b9d": "Password Administrator",
    "3a2c62db-5318-420d-8d74-23affee5d9d5": "Intune Administrator",
    "69091246-20e8-4a56-aa4d-066075b2a7a8": "Teams Administrator",
}
PRIVILEGED_ROLE_NAMES = set(PRIVILEGED_ROLE_TEMPLATES.values())

GUEST_INACTIVE_DAYS = 90
ANONYMOUS_LINK_MAX_DAYS = 30
SECURE_SCORE_PASS_PERCENT = 60.0


def _missing(what: str, permission: str) -> CheckOutcome:
    return CheckOutcome(
        status=Status.error,
        summary=f"Could not read {what}. Grant the {permission} application permission, consent as admin, and run again.",
        notes=[f"missing data: {what}"],
    )


def _active_members(snapshot: M365Snapshot) -> list[User]:
    return [u for u in snapshot.users or [] if u.enabled and u.user_type == "Member"]


def _is_global_admin_role(role_template_id: str, role_name: str) -> bool:
    return role_template_id == GLOBAL_ADMIN_TEMPLATE or role_name == "Global Administrator"


def _is_privileged_role(role_template_id: str, role_name: str) -> bool:
    return role_template_id in PRIVILEGED_ROLE_TEMPLATES or role_name in PRIVILEGED_ROLE_NAMES


@check("m365.mfa.coverage")
def mfa_coverage(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    if snapshot.users is None:
        return _missing("the user list", "User.Read.All")
    members = _active_members(snapshot)
    known = [u for u in members if u.mfa_registered is not None]
    if members and not known:
        return _missing("MFA registration details", "AuditLog.Read.All (userRegistrationDetails report)")
    unregistered = [u for u in known if not u.mfa_registered]
    registered = len(known) - len(unregistered)
    coverage = round(100.0 * registered / len(known), 1) if known else 100.0
    evidence = {
        "enabled_users": len(members),
        "registered": registered,
        "unregistered": len(unregistered),
        "coverage_percent": coverage,
        "unregistered_sample": [u.upn for u in unregistered[:10]],
    }
    notes = []
    if len(known) < len(members):
        notes.append(f"{len(members) - len(known)} enabled user(s) had no registration record and were left out of the count.")
    if unregistered:
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(unregistered)} of {len(known)} enabled users ({round(100 - coverage, 1)}%) have no second sign-in factor registered.",
            evidence=evidence,
            notes=notes,
        )
    return CheckOutcome(
        status=Status.passed,
        summary=f"All {len(known)} enabled users are registered for MFA.",
        evidence=evidence,
        notes=notes,
    )


@check("m365.conditional_access.present")
def conditional_access_present(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    policies = snapshot.conditional_access_policies
    if policies is None:
        return _missing("Conditional Access policies", "Policy.Read.All")
    enforcing = [p for p in policies if p.enabled and p.covers_all_users and p.covers_all_apps and p.requires_mfa]
    report_only = [p for p in policies if p.state == "enabledForReportingButNotEnforced" and p.requires_mfa]
    evidence = {
        "policies_total": len(policies),
        "mfa_for_all_users": [p.display_name for p in enforcing],
        "mfa_report_only": [p.display_name for p in report_only],
    }
    notes = []
    if report_only:
        notes.append("A report-only policy requires MFA but does not enforce it. Switch it on once the sign-in report looks clean.")
    if snapshot.security_defaults_enabled:
        notes.append("Security Defaults is on, which requires MFA without Conditional Access. See m365.security_defaults.")
    if enforcing:
        return CheckOutcome(
            status=Status.passed,
            summary=f"Conditional Access requires MFA for all users and all apps ({', '.join(evidence['mfa_for_all_users'])}).",
            evidence=evidence,
            notes=notes,
        )
    return CheckOutcome(
        status=Status.failed,
        summary="No enabled Conditional Access policy requires MFA for all users and all cloud apps.",
        evidence=evidence,
        notes=notes,
    )


@check("m365.legacy_auth.blocked")
def legacy_auth_blocked(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    policies = snapshot.conditional_access_policies
    if policies is None and snapshot.security_defaults_enabled is None:
        return _missing("Conditional Access policies", "Policy.Read.All")
    blocked_by: list[str] = []
    if snapshot.security_defaults_enabled:
        blocked_by.append("Security Defaults")
    for policy in policies or []:
        if policy.enabled and policy.covers_all_users and policy.blocks_legacy_auth:
            blocked_by.append(policy.display_name)
    count = snapshot.legacy_auth_sign_ins_30d
    evidence = {"blocked_by": blocked_by, "legacy_sign_ins_30d": count}
    notes = []
    if count is None:
        notes.append(
            "Sign-in logs were not available (they need Entra ID P1 and AuditLog.Read.All), so this relies on the policy alone."
        )
    if not blocked_by:
        tail = f" {count} legacy sign-ins succeeded in the last 30 days." if count else ""
        return CheckOutcome(
            status=Status.failed,
            summary="Nothing blocks legacy authentication (POP, IMAP, SMTP AUTH and other clients that skip MFA)." + tail,
            evidence=evidence,
            notes=notes,
        )
    if count:
        return CheckOutcome(
            status=Status.failed,
            summary=(
                f"Legacy authentication is blocked by {', '.join(blocked_by)}, but {count} legacy sign-ins still "
                "succeeded in the last 30 days. Check the policy's exclusions."
            ),
            evidence=evidence,
            notes=notes,
        )
    return CheckOutcome(
        status=Status.passed,
        summary=f"Legacy authentication is blocked by {', '.join(blocked_by)}"
        + (" and no legacy sign-ins succeeded in the last 30 days." if count == 0 else "."),
        evidence=evidence,
        notes=notes,
    )


@check("m365.security_defaults")
def security_defaults(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    enabled = snapshot.security_defaults_enabled
    policies = snapshot.conditional_access_policies
    if enabled is None and policies is None:
        return _missing("the Security Defaults setting", "Policy.Read.All")
    if enabled:
        return CheckOutcome(
            status=Status.passed,
            summary="Security Defaults is enabled, which requires MFA and blocks legacy authentication for everyone.",
            evidence={"security_defaults_enabled": True},
        )
    ca_mfa = any(p.enabled and p.covers_all_users and p.covers_all_apps and p.requires_mfa for p in policies or [])
    ca_legacy = any(p.enabled and p.covers_all_users and p.blocks_legacy_auth for p in policies or [])
    evidence = {
        "security_defaults_enabled": bool(enabled),
        "conditional_access_requires_mfa": ca_mfa,
        "conditional_access_blocks_legacy_auth": ca_legacy,
    }
    if ca_mfa and ca_legacy:
        return CheckOutcome(
            status=Status.passed,
            summary="Security Defaults is off, but Conditional Access requires MFA for everyone and blocks legacy authentication.",
            evidence=evidence,
        )
    gaps = []
    if not ca_mfa:
        gaps.append("require MFA for all users")
    if not ca_legacy:
        gaps.append("block legacy authentication")
    return CheckOutcome(
        status=Status.failed,
        summary="Security Defaults is off and Conditional Access does not " + " or ".join(gaps) + ".",
        evidence=evidence,
    )


@check("m365.admins.global_count")
def admins_global_count(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    roles = snapshot.role_assignments
    if roles is None:
        return _missing("directory role members", "RoleManagement.Read.Directory")
    member_ids: list[str] = []
    for role in roles:
        if _is_global_admin_role(role.role_template_id, role.role_name):
            member_ids.extend(role.member_ids)
    member_ids = list(dict.fromkeys(member_ids))
    admins = [(member_id, snapshot.user_by_id(member_id)) for member_id in member_ids]
    accounts = [user.upn if user else f"object {member_id}" for member_id, user in admins]
    with_mailbox = [user.upn for _, user in admins if user and user.has_mailbox]
    count = len(member_ids)
    evidence = {"global_admins": count, "accounts": accounts, "with_mailbox": with_mailbox}
    problems = []
    if count < 2:
        problems.append(f"only {count} Global Administrator (no second break-glass account)")
    if count > 4:
        problems.append(f"{count} Global Administrators (target is 2 to 4)")
    if with_mailbox:
        problems.append(
            f"{len(with_mailbox)} Global Administrator account(s) also hold a mailbox, which means they are used for daily work"
        )
    if problems:
        return CheckOutcome(status=Status.failed, summary="Found " + "; ".join(problems) + ".", evidence=evidence)
    return CheckOutcome(
        status=Status.passed,
        summary=f"{count} Global Administrators, all on dedicated accounts without a mailbox.",
        evidence=evidence,
    )


@check("m365.admins.mfa")
def admins_mfa(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    roles = snapshot.role_assignments
    if roles is None:
        return _missing("directory role members", "RoleManagement.Read.Directory")
    if snapshot.users is None:
        return _missing("the user list", "User.Read.All")
    member_ids: list[str] = []
    for role in roles:
        if _is_privileged_role(role.role_template_id, role.role_name):
            member_ids.extend(role.member_ids)
    member_ids = list(dict.fromkeys(member_ids))
    users = [snapshot.user_by_id(member_id) for member_id in member_ids]
    people = [u for u in users if u is not None]
    non_user_members = len(users) - len(people)
    unknown = [u for u in people if u.mfa_registered is None]
    if people and len(unknown) == len(people):
        return _missing("MFA registration details for admins", "AuditLog.Read.All (userRegistrationDetails report)")
    unprotected = [u for u in people if u.mfa_registered is False]
    evidence = {
        "privileged_accounts": len(people),
        "unprotected": [u.upn for u in unprotected],
        "unknown_status": [u.upn for u in unknown],
        "non_user_members": non_user_members,
    }
    notes = []
    if unknown:
        notes.append(f"{len(unknown)} privileged account(s) had no registration record.")
    if non_user_members:
        notes.append(f"{non_user_members} role member(s) are groups or service principals and were not evaluated.")
    if unprotected:
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(unprotected)} of {len(people)} privileged accounts have no MFA registered: {', '.join(evidence['unprotected'])}.",
            evidence=evidence,
            notes=notes,
        )
    return CheckOutcome(
        status=Status.passed,
        summary=f"All {len(people)} privileged accounts are registered for MFA.",
        evidence=evidence,
        notes=notes,
    )


@check("m365.forwarding.external")
def forwarding_external(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    rules = snapshot.inbox_rules
    if rules is None:
        return _missing("inbox rules", "MailboxSettings.Read")
    external = []
    for rule in rules:
        if not rule.enabled:
            continue
        targets = [t for t in rule.forward_to + rule.redirect_to if not snapshot.is_internal_address(t)]
        if targets:
            external.append({"user": rule.user_upn, "rule": rule.name, "to": targets})
    blocked = snapshot.outbound_forwarding_blocked
    evidence = {
        "rules_reviewed": len(rules),
        "external_forwarding_rules": external,
        "outbound_forwarding_blocked": blocked,
    }
    if external:
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(external)} inbox rule(s) forward or redirect mail to addresses outside the company.",
            evidence=evidence,
        )
    if blocked is False:
        return CheckOutcome(
            status=Status.failed,
            summary="No external forwarding rules were found, but the tenant still allows automatic external forwarding.",
            evidence=evidence,
        )
    if blocked is None:
        return CheckOutcome(
            status=Status.attestation_needed,
            summary=(
                "No external forwarding rules were found. Whether the tenant blocks automatic external forwarding "
                "is only visible in the Defender portal (Anti-spam outbound policy, Automatic forwarding: Off); "
                "confirm it there and attach a screenshot."
            ),
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.passed,
        summary="Automatic external forwarding is blocked and no inbox rule forwards mail outside the company.",
        evidence=evidence,
    )


_DMARC_POLICY = re.compile(r"(?:^|;)\s*p\s*=\s*(none|quarantine|reject)", re.IGNORECASE)


@check("m365.email_auth.dmarc")
def email_auth(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    records = snapshot.email_auth
    if records is None:
        return CheckOutcome(
            status=Status.error,
            summary="DNS lookups for SPF, DKIM and DMARC did not run, so the sending domains could not be checked.",
            notes=["missing data: DNS records for the verified domains"],
        )
    if not records:
        return CheckOutcome(
            status=Status.not_applicable,
            summary="The tenant has no custom domain; mail only uses the onmicrosoft.com address.",
        )
    per_domain = []
    failing = []
    for record in records:
        spf_ok = bool(record.spf and record.spf.lower().startswith("v=spf1"))
        policy_match = _DMARC_POLICY.search(record.dmarc or "")
        dmarc_policy = policy_match.group(1).lower() if policy_match else None
        dmarc_ok = dmarc_policy in ("quarantine", "reject")
        dkim_ok = record.dkim_enabled is True
        per_domain.append(
            {"domain": record.domain, "spf": spf_ok, "dkim": record.dkim_enabled, "dmarc_policy": dmarc_policy}
        )
        gaps = []
        if not spf_ok:
            gaps.append("no SPF")
        if not dkim_ok:
            gaps.append("DKIM not enabled")
        if not dmarc_ok:
            gaps.append(f"DMARC {dmarc_policy or 'missing'}")
        if gaps:
            failing.append(f"{record.domain} ({', '.join(gaps)})")
    evidence = {"domains": per_domain}
    if failing:
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(failing)} of {len(records)} sending domains are not fully protected: {'; '.join(failing)}.",
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.passed,
        summary=f"SPF, DKIM and an enforcing DMARC policy are in place on all {len(records)} sending domains.",
        evidence=evidence,
    )


@check("m365.sharing.anonymous_links")
def sharing_anonymous_links(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    sharing = snapshot.sharing
    if sharing is None or sharing.sharing_capability is None:
        return _missing("SharePoint sharing settings", "SharePointTenantSettings.Read.All")
    capability = sharing.sharing_capability
    expiry = sharing.anonymous_link_expiration_days
    evidence = {"sharing_capability": capability, "anonymous_link_expiration_days": expiry}
    if capability != "externalUserAndGuestSharing":
        return CheckOutcome(
            status=Status.passed,
            summary=f"Anyone-with-the-link sharing is off (tenant sharing level: {capability}).",
            evidence=evidence,
        )
    if expiry is not None and expiry <= ANONYMOUS_LINK_MAX_DAYS:
        return CheckOutcome(
            status=Status.passed,
            summary=f"Anyone links are allowed but expire after {expiry} days.",
            evidence=evidence,
        )
    detail = (
        f" and links expire after {expiry} days"
        if expiry is not None
        else " and link expiry could not be confirmed (that setting is only visible in SharePoint PowerShell)"
    )
    return CheckOutcome(
        status=Status.failed,
        summary="Anyone-with-the-link sharing is on for SharePoint and OneDrive" + detail + ".",
        evidence=evidence,
    )


@check("m365.guests.review")
def guests_review(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    if snapshot.users is None:
        return _missing("the user list", "User.Read.All")
    guests = [u for u in snapshot.users if u.user_type == "Guest" and u.enabled]
    if not guests:
        return CheckOutcome(status=Status.passed, summary="No guest accounts.", evidence={"guests": 0})
    cutoff = snapshot.collected_at - timedelta(days=GUEST_INACTIVE_DAYS)
    stale = []
    for guest in guests:
        reference = guest.last_sign_in or guest.created
        if reference is None or reference < cutoff:
            stale.append(guest)
    evidence = {
        "guests": len(guests),
        "inactive_90d": len(stale),
        "inactive_sample": [g.upn for g in stale[:10]],
    }
    notes = []
    if not any(g.last_sign_in for g in guests):
        notes.append("No sign-in activity was available (needs Entra ID P1); inactivity is measured from account creation.")
    if stale:
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(stale)} of {len(guests)} guest accounts have been inactive for more than {GUEST_INACTIVE_DAYS} days.",
            evidence=evidence,
            notes=notes,
        )
    return CheckOutcome(
        status=Status.passed,
        summary=f"All {len(guests)} guest accounts were active in the last {GUEST_INACTIVE_DAYS} days.",
        evidence=evidence,
        notes=notes,
    )


@check("m365.audit.enabled")
def audit_enabled(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    audit = snapshot.audit
    if audit is None:
        return _missing("audit log settings", "AuditLog.Read.All")
    evidence = audit.model_dump()
    if audit.unified_audit_log_enabled is False:
        return CheckOutcome(status=Status.failed, summary="The unified audit log is turned off.", evidence=evidence)
    if audit.unified_audit_log_enabled is True:
        if audit.retention_days is None:
            return CheckOutcome(
                status=Status.attestation_needed,
                summary="The unified audit log is on; confirm retention is 90 days or more and attach the Purview retention policy.",
                evidence=evidence,
            )
        if audit.retention_days < 90:
            return CheckOutcome(
                status=Status.failed,
                summary=f"The unified audit log is on but keeps only {audit.retention_days} days; insurers expect 90 or more.",
                evidence=evidence,
            )
        return CheckOutcome(
            status=Status.passed,
            summary=f"The unified audit log is on with {audit.retention_days} days of retention.",
            evidence=evidence,
        )
    if audit.directory_audit_available:
        return CheckOutcome(
            status=Status.attestation_needed,
            summary=(
                "Entra audit logs are available through Graph, but the unified audit log state is only visible in "
                "Microsoft Purview. Confirm it is on with 90 days or more of retention and attach a screenshot of Purview > Audit."
            ),
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.error,
        summary="Audit logs could not be read through Graph.",
        evidence=evidence,
        notes=["missing data: directory audit logs"],
    )


@check("m365.secure_score")
def secure_score(snapshot: M365Snapshot, definition: CheckDefinition) -> CheckOutcome:
    score = snapshot.secure_score
    if score is None:
        return _missing("Microsoft Secure Score", "SecurityEvents.Read.All")
    evidence = {"current": score.current, "max": score.max, "percent": score.percent}
    if score.percent > SECURE_SCORE_PASS_PERCENT:
        return CheckOutcome(
            status=Status.passed,
            summary=f"Secure Score is {score.current:g} of {score.max:g} ({score.percent}%).",
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.failed,
        summary=f"Secure Score is {score.current:g} of {score.max:g} ({score.percent}%), under the {SECURE_SCORE_PASS_PERCENT:g}% bar.",
        evidence=evidence,
    )
