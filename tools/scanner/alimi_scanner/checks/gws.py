"""Google Workspace checks, one function per gws.* id in config/checks.yaml.

Same contract as the Microsoft 365 checks: read the snapshot, never call an
API, report "error" with the missing scope when a field is None.
"""

from __future__ import annotations

from ..engine import check
from ..schema import CheckDefinition, CheckOutcome, Status
from ..snapshot import GWSSnapshot, GWSUser, OAuthApp
from ._email_auth import evaluate_email_auth

SCOPE_USERS = "admin.directory.user.readonly"
SCOPE_REPORTS = "admin.reports.audit.readonly"
SCOPE_POLICIES = "cloud-identity.policies.readonly"
SCOPE_GMAIL = "gmail.readonly (through domain-wide delegation)"

# OAuth scopes that let a third-party app read mail or files. drive.file and drive.appdata are
# per-file or app-private, so they are left out on purpose.
RISKY_SCOPE_MARKERS = (
    "mail.google.com",
    "auth/gmail.",
    "auth/drive",
    "auth/admin.directory",
    "auth/contacts",
    "auth/calendar",
)
LOW_RISK_SCOPES = {
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.appdata",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.metadata",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.readonly",
}


def _missing(what: str, scope: str) -> CheckOutcome:
    return CheckOutcome(
        status=Status.error,
        summary=f"Could not read {what}. Add the {scope} scope to the service account's domain-wide delegation and run again.",
        notes=[f"missing data: {what}"],
    )


def _active_users(snapshot: GWSSnapshot) -> list[GWSUser]:
    return [u for u in snapshot.users or [] if u.active]


def risky_scopes(app: OAuthApp) -> list[str]:
    out = []
    for scope in app.scopes:
        if scope in LOW_RISK_SCOPES:
            continue
        if any(marker in scope for marker in RISKY_SCOPE_MARKERS):
            out.append(scope)
    return out


@check("gws.2sv.enforced")
def two_step_enforced(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    if snapshot.users is None:
        return _missing("the user list", SCOPE_USERS)
    users = _active_users(snapshot)
    not_enrolled = [u for u in users if u.enrolled_2sv is False]
    not_enforced = [u for u in users if u.enforced_2sv is False]
    policies = snapshot.policies
    evidence = {
        "active_users": len(users),
        "not_enrolled": len(not_enrolled),
        "not_enforced": len(not_enforced),
        "not_enrolled_sample": [u.email for u in not_enrolled[:10]],
        "not_enforced_sample": [u.email for u in not_enforced[:10]],
        "policy_enforced_everywhere": policies.two_sv_enforced_everywhere if policies else None,
        "unenforced_org_units": policies.two_sv_unenforced_org_units if policies else [],
    }
    notes = []
    if policies is None or policies.two_sv_enforced_everywhere is None:
        notes.append("The organizational-unit policy could not be read; enforcement is judged from each user's isEnforcedIn2Sv flag.")
    problems = []
    if not_enforced:
        problems.append(f"{len(not_enforced)} active users are not under 2-Step Verification enforcement")
    if policies and policies.two_sv_enforced_everywhere is False:
        problems.append(f"enforcement is off for organizational units: {', '.join(policies.two_sv_unenforced_org_units) or 'some'}")
    if not_enrolled:
        problems.append(f"{len(not_enrolled)} active users have not enrolled")
    if problems:
        return CheckOutcome(status=Status.failed, summary="; ".join(problems).capitalize() + ".", evidence=evidence, notes=notes)
    return CheckOutcome(
        status=Status.passed,
        summary=f"2-Step Verification is enforced for all {len(users)} active users and every one of them is enrolled.",
        evidence=evidence,
        notes=notes,
    )


@check("gws.admins.super_count")
def super_admin_count(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    if snapshot.users is None:
        return _missing("the user list", SCOPE_USERS)
    supers = [u for u in _active_users(snapshot) if u.is_super_admin]
    without_2sv = [u for u in supers if not u.enrolled_2sv]
    evidence = {
        "super_admins": len(supers),
        "accounts": [u.email for u in supers],
        "without_2sv": [u.email for u in without_2sv],
    }
    problems = []
    if len(supers) < 2:
        problems.append(f"only {len(supers)} super admin (no second break-glass account)")
    if len(supers) > 4:
        problems.append(f"{len(supers)} super admins (target is 2 to 4)")
    if without_2sv:
        problems.append(f"{len(without_2sv)} super admin(s) not enrolled in 2-Step Verification")
    if problems:
        return CheckOutcome(status=Status.failed, summary="Found " + "; ".join(problems) + ".", evidence=evidence)
    return CheckOutcome(
        status=Status.passed,
        summary=f"{len(supers)} super admins, all enrolled in 2-Step Verification.",
        evidence=evidence,
    )


@check("gws.forwarding.external")
def forwarding_external(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    forwarding = snapshot.forwarding
    if forwarding is None:
        return _missing("Gmail forwarding settings", SCOPE_GMAIL)
    external = []
    for entry in forwarding:
        targets = []
        if entry.auto_forwarding_enabled and entry.auto_forward_to and not snapshot.is_internal_address(entry.auto_forward_to):
            targets.append(entry.auto_forward_to)
        targets.extend(t for t in entry.filter_forward_to if not snapshot.is_internal_address(t))
        if targets:
            external.append({"user": entry.user_email, "to": targets})
    allowed = snapshot.policies.auto_forwarding_allowed if snapshot.policies else None
    evidence = {"mailboxes_reviewed": len(forwarding), "external_forwarding": external, "auto_forwarding_allowed": allowed}
    if external:
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(external)} mailbox(es) forward mail to addresses outside the company.",
            evidence=evidence,
        )
    if allowed is True:
        return CheckOutcome(
            status=Status.failed,
            summary="No mailbox forwards externally today, but the Gmail setting still lets users turn automatic forwarding on.",
            evidence=evidence,
        )
    if allowed is None:
        return CheckOutcome(
            status=Status.attestation_needed,
            summary=(
                "No mailbox forwards externally. The tenant-wide automatic forwarding setting could not be read; "
                "confirm it is off under Admin console > Apps > Gmail > End user access and attach a screenshot."
            ),
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.passed,
        summary="Automatic forwarding is disabled for users and no filter forwards mail outside the company.",
        evidence=evidence,
    )


@check("gws.email_auth.dmarc")
def email_auth(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    return evaluate_email_auth(snapshot.email_auth, provider_default="a Google test domain")


@check("gws.oauth.third_party")
def oauth_third_party(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    apps = snapshot.third_party_apps
    if apps is None:
        return _missing("OAuth app authorizations", SCOPE_REPORTS)
    approved = set(snapshot.approved_client_ids)
    unapproved = []
    for app in apps:
        if app.client_id in approved:
            continue
        risky = risky_scopes(app)
        if risky:
            unapproved.append(
                {"app": app.display_name or app.client_id, "client_id": app.client_id, "users": app.user_count, "scopes": risky}
            )
    restricted = snapshot.policies.third_party_access_restricted if snapshot.policies else None
    evidence = {
        "apps_seen": len(apps),
        "approved_client_ids": sorted(approved),
        "unapproved_with_mail_or_drive_access": unapproved,
        "third_party_access_restricted": restricted,
    }
    if unapproved:
        names = ", ".join(a["app"] for a in unapproved[:5])
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(unapproved)} third-party app(s) hold mail, Drive, calendar, contacts or directory access without being approved: {names}.",
            evidence=evidence,
        )
    if restricted is False:
        return CheckOutcome(
            status=Status.failed,
            summary="No unapproved app has sensitive access yet, but any user can still grant it: third-party app access is not restricted.",
            evidence=evidence,
        )
    if restricted is None:
        return CheckOutcome(
            status=Status.attestation_needed,
            summary=(
                "No unapproved app has sensitive access. Whether unconfigured third-party apps are restricted could not be read; "
                "confirm it under Admin console > Security > API controls and attach a screenshot."
            ),
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.passed,
        summary="Third-party app access is restricted and no unapproved app holds mail or Drive access.",
        evidence=evidence,
    )


@check("gws.drive.external_sharing")
def drive_external_sharing(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    policies = snapshot.policies
    if policies is None or policies.external_sharing_mode is None:
        return _missing("the Drive external sharing policy", SCOPE_POLICIES)
    mode = policies.external_sharing_mode
    evidence = {
        "external_sharing_mode": mode,
        "allow_publishing_files": policies.allow_publishing_files,
        "warn_for_external_sharing": policies.warn_for_external_sharing,
    }
    problems = []
    if policies.allow_publishing_files:
        problems.append("files can be published to anyone on the web")
    if mode == "ALLOWED" and not policies.warn_for_external_sharing:
        problems.append("sharing outside the company is allowed without even a warning")
    if problems:
        return CheckOutcome(status=Status.failed, summary="Drive sharing is too open: " + "; ".join(problems) + ".", evidence=evidence)
    notes = []
    if mode == "ALLOWED":
        notes.append("External sharing is allowed with a warning. Allowlisting trusted domains would be tighter.")
    return CheckOutcome(
        status=Status.passed,
        summary=f"Drive external sharing is controlled (mode {mode}) and files cannot be published to anyone on the web.",
        evidence=evidence,
        notes=notes,
    )


@check("gws.lsa.disabled")
def less_secure_apps(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    policies = snapshot.policies
    if policies is None:
        return _missing("the less secure apps policy", SCOPE_POLICIES)
    allowed = policies.less_secure_apps_allowed
    evidence = {"less_secure_apps_allowed": allowed}
    if allowed:
        return CheckOutcome(
            status=Status.failed,
            summary="Less secure app access is still allowed for at least one organizational unit.",
            evidence=evidence,
        )
    notes = []
    if allowed is None:
        notes.append("Google removed less secure app access from Workspace in 2025 and the policy returned no value; nothing is left to configure.")
    return CheckOutcome(status=Status.passed, summary="Less secure app access is off.", evidence=evidence, notes=notes)


@check("gws.audit.available")
def audit_available(snapshot: GWSSnapshot, definition: CheckDefinition) -> CheckOutcome:
    audit = snapshot.audit
    if audit is None or (audit.login_available is None and audit.admin_available is None):
        return _missing("the login and admin audit logs", SCOPE_REPORTS)
    evidence = audit.model_dump()
    missing = [name for name, ok in (("login", audit.login_available), ("admin", audit.admin_available)) if not ok]
    if missing:
        return CheckOutcome(
            status=Status.failed,
            summary=f"The {' and '.join(missing)} audit log(s) are not available through the Reports API.",
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.passed,
        summary=f"Login and admin audit logs are available; Google retains them for {audit.retention_days} days.",
        evidence=evidence,
    )
