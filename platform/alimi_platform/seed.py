"""Sample organizations, users and integrations for mock mode.

Three organizations, all fictional sample data:
  Saltmarsh Payroll  the demo company (Microsoft 365, the scanner's "fail" fixture)
  Harbor Dental      a second company so the isolation tests mean something (Google Workspace, "fail")
  Alimi              our own organization, for dogfooding (Microsoft 365, the "pass" fixture)

IDs are fixed (uuid5 of a name), so the mock login picker can list the sample users from
this file without asking the database for every user, which the app role is not allowed
to do. The seed runs as the table owner, and because FORCE ROW LEVEL SECURITY applies to
the owner too, it writes each organization's rows inside that organization's context,
through the same policies the app uses.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import Engine, text

from .audit import record
from .config import Settings
from .crypto import TokenBox
from .db import org_scope
from .scans import run_scan
from .status import control_statuses
from .tasks import seed_tasks

NAMESPACE = uuid.UUID("5b1f2b8e-6a0c-4c55-9a36-0a11ce000000")


def sample_id(name: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, name)


@dataclass(frozen=True)
class SampleUser:
    email: str
    display_name: str
    role: str
    title: str = ""   # job title shown in the top bar; the person can change it on their Profile page

    @property
    def id(self) -> uuid.UUID:
        return sample_id(f"user:{self.email}")


@dataclass(frozen=True)
class SampleOrg:
    slug: str
    name: str
    platform: str
    integration_name: str
    fixture: str
    users: tuple[SampleUser, ...]

    @property
    def id(self) -> uuid.UUID:
        return sample_id(f"org:{self.slug}")

    @property
    def integration_id(self) -> uuid.UUID:
        return sample_id(f"integration:{self.slug}")


SAMPLE_ORGS: tuple[SampleOrg, ...] = (
    SampleOrg(
        slug="saltmarsh",
        name="Saltmarsh Payroll (sample)",
        platform="m365",
        integration_name="Microsoft 365 (sample tenant)",
        fixture="fail",
        users=(
            SampleUser("dana.whitcomb@saltmarsh.example", "Dana Whitcomb", "owner", "Owner and CEO"),
            SampleUser("theo.marsh@saltmarsh.example", "Theo Marsh", "member", "Operations lead"),
        ),
    ),
    SampleOrg(
        slug="harbor-dental",
        name="Harbor Dental (sample)",
        platform="gws",
        integration_name="Google Workspace (sample tenant)",
        fixture="fail",
        users=(
            SampleUser("priya.nair@harbordental.example", "Priya Nair", "owner", "Practice owner"),
            SampleUser("sam.okafor@harbordental.example", "Sam Okafor", "admin", "Office manager"),
        ),
    ),
    SampleOrg(
        slug="alimi",
        name="Alimi",
        platform="m365",
        integration_name="Microsoft 365 (sample tenant until our own is connected)",
        fixture="pass",
        users=(SampleUser("founder@alimi.example", "Alimi founder (sample)", "owner", "Founder"),),
    ),
)

READ_ONLY_SCOPES = {
    # Documented in tools/scanner/README.md; recorded here so the integration shows what it was granted.
    "m365": [
        "Organization.Read.All",
        "User.Read.All",
        "AuditLog.Read.All",
        "Policy.Read.All",
        "RoleManagement.Read.Directory",
        "MailboxSettings.Read",
        "SharePointTenantSettings.Read.All",
        "SecurityEvents.Read.All",
    ],
    "gws": [
        "admin.directory.customer.readonly",
        "admin.directory.domain.readonly",
        "admin.directory.user.readonly",
        "admin.reports.audit.readonly",
        "cloud-identity.policies.readonly",
        "gmail.readonly",
    ],
}


def _evidence_for(org: SampleOrg, today: date) -> list[dict]:
    """A few attestations per company: some current, one past its renewal date."""
    owner = org.users[0].id
    rows = [
        ("CTL-01", "attestation", "policy", "Information security policy approved by the CEO", today - timedelta(days=60), today + timedelta(days=305)),
        ("CTL-23", "attestation", "export", "EDR coverage export from the IT provider's console", today - timedelta(days=20), today + timedelta(days=70)),
    ]
    if org.slug != "alimi":
        rows.append(
            ("CTL-31", "attestation", "record", "Backup restore test", today - timedelta(days=200), today - timedelta(days=110))
        )
    return [
        {
            "id": sample_id(f"evidence:{org.slug}:{control}"),
            "org": org.id,
            "control": control,
            "kind": kind,
            "etype": etype,
            "title": title,
            "by": owner,
            "collected": collected,
            "renews": renews,
        }
        for control, kind, etype, title, collected, renews in rows
    ]


def seed(owner_engine: Engine, settings: Settings, run_scans: bool = True) -> None:
    """Create the sample data if it is not there yet. Safe to run on every start."""
    box = TokenBox(settings.token_key)
    today = date.today()
    for org in SAMPLE_ORGS:
        with org_scope(owner_engine, org.id) as conn:
            exists = conn.execute(text("SELECT 1 FROM organizations WHERE id = :id"), {"id": org.id}).first()
            if exists:
                continue
            conn.execute(
                text("INSERT INTO organizations (id, name, slug, is_sample) VALUES (:id, :name, :slug, true)"),
                {"id": org.id, "name": org.name, "slug": org.slug},
            )
            for user in org.users:
                conn.execute(
                    # No ON CONFLICT: Postgres would also check the row against the SELECT policy,
                    # and a user is not visible until their membership exists.
                    text("INSERT INTO users (id, email, display_name, job_title) VALUES (:id, :email, :name, :title)"),
                    {"id": user.id, "email": user.email, "name": user.display_name, "title": user.title or None},
                )
                conn.execute(
                    text("INSERT INTO memberships (organization_id, user_id, role) VALUES (:org, :user, :role)"),
                    {"org": org.id, "user": user.id, "role": user.role},
                )
            conn.execute(
                text(
                    "INSERT INTO integrations (id, organization_id, platform, display_name, mode, fixture, scopes, token_ciphertext) "
                    "VALUES (:id, :org, :platform, :name, 'mock', :fixture, :scopes, :token)"
                ),
                {
                    "id": org.integration_id,
                    "org": org.id,
                    "platform": org.platform,
                    "name": org.integration_name,
                    "fixture": org.fixture,
                    "scopes": READ_ONLY_SCOPES[org.platform],
                    # A placeholder, encrypted the same way a real token will be.
                    "token": box.encrypt(f"mock-token-for-{org.slug}"),
                },
            )
            conn.execute(
                text(
                    "INSERT INTO evidence (id, organization_id, control_id, kind, evidence_type, title, attested_by, collected_on, renews_on) "
                    "VALUES (:id, :org, :control, :kind, :etype, :title, :by, :collected, :renews)"
                ),
                _evidence_for(org, today),
            )
            record(conn, org.id, None, "seed.sample_data", f"organization:{org.slug}", {"users": len(org.users)})
            if run_scans:
                run_scan(conn, settings, org.integration_id, None)
                # The month's list: a renewal project and the tasks the first scan raises.
                seed_tasks(conn, org.id, org.users[0].id, org.users[1].id if len(org.users) > 1 else None, control_statuses(conn), today)
