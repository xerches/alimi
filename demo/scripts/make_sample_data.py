"""Writes the sample company behind the Alimi platform demo into demo/data/*.json.

Saltmarsh Payroll, Inc. is fictional: every person, vendor, date and number here is invented so that
nothing on a demo screen implies a client. The policies, requirement IDs, controls and checks the
demo shows come from the repo (policies/, config/controls.yaml, config/checks.yaml); this script only
stages the company that uses them. Run it, then run the scanner on the snapshot it writes:

    python demo/scripts/make_sample_data.py
    alimi-scan m365 --snapshot demo/data/snapshot.json --no-dns -o /tmp/demo-scan -q

and copy the findings file to demo/data/scan.json (see demo/README.md). Deterministic: running it
twice gives the same files.
"""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "demo" / "data"
AS_OF = date(2026, 11, 1)  # the demo is frozen on this day; every "days left" counts from it
SCAN_AT = datetime(2026, 10, 30, 22, 15, tzinfo=timezone.utc)
DOMAIN = "saltmarsh.example"
rng = random.Random(20261101)


def iso(d: date | datetime | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")
    return d.isoformat()


def days_ago(n: int, hour: int = 14) -> datetime:
    return datetime.combine(AS_OF - timedelta(days=n), datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=hour)


def write(name: str, data) -> None:
    path = OUT / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


# --------------------------------------------------------------------------- people

FIRST = [
    "Jordan", "Maya", "Ethan", "Sofia", "Liam", "Aisha", "Noah", "Camila", "Owen", "Zara", "Caleb",
    "Leila", "Isaac", "Hana", "Miles", "Ingrid", "Theo", "Amara", "Felix", "Nina", "Declan", "Yara",
    "Bruno", "Keiko", "Omar", "Sienna", "Patrick", "Imani", "Victor", "Esme", "Ruben", "Tess", "Hugo",
    "Anya", "Sean", "Lucia", "Kofi", "Greta", "Mateo", "Rhea", "Connor", "Dalia", "Emeka", "Freya",
]
LAST = [
    "Ortiz", "Nguyen", "Doyle", "Petrov", "Okoro", "Flaherty", "Kim", "Rossi", "Adeyemi", "Lindgren",
    "Costa", "Byrne", "Tanaka", "Walsh", "Hernandez", "Moreau", "Osei", "Quinn", "Alvarez", "Sato",
    "Murphy", "Novak", "Castillo", "Reyes", "Keane", "Haddad", "Fischer", "Bello", "Larsen", "Ferreira",
    "Donnelly", "Cruz", "Iqbal", "Romano", "Sullivan", "Park", "Medina", "Gallagher", "Diallo", "Weber",
]

PEOPLE: list[dict] = []
_used: set[str] = set()


def _email(first: str, last: str) -> str:
    base = f"{first}.{last}".lower().replace("'", "")
    email = f"{base}@{DOMAIN}"
    n = 2
    while email in _used:
        email = f"{base}{n}@{DOMAIN}"
        n += 1
    _used.add(email)
    return email


def person(pid: str, name: str, title: str, dept: str, manager: str | None, start: date, **extra) -> dict:
    first, last = name.split(" ", 1)
    rec = {
        "id": pid,
        "name": name,
        "email": extra.pop("email", None) or _email(first, last),
        "title": title,
        "department": dept,
        "manager": manager,
        "start_date": iso(start),
        "status": "active",
        "employment": "employee",
        "external": False,
        "counted": True,
    }
    rec.update(extra)
    PEOPLE.append(rec)
    return rec


def staff(prefix_id: int, count: int, titles: list[str], dept: str, manager: str, year_from: int) -> list[str]:
    ids = []
    for i in range(count):
        pid = f"P-{prefix_id + i:02d}"
        first = FIRST[(prefix_id + i) % len(FIRST)]
        last = LAST[(prefix_id * 3 + i) % len(LAST)]
        start = date(rng.randint(year_from, 2025), rng.randint(1, 12), rng.randint(1, 28))
        person(pid, f"{first} {last}", titles[i % len(titles)], dept, manager, start)
        ids.append(pid)
    return ids


person("P-01", "Dana Whitcomb", "Chief Executive Officer", "Leadership", None, date(2014, 3, 3))
person("P-02", "Priya Natarajan", "Chief Operating Officer", "Leadership", "P-01", date(2018, 9, 10))
person("P-03", "Tom Brennan", "Chief Financial Officer", "Leadership", "P-01", date(2016, 1, 11))
person("P-04", "Grace Lindqvist", "General Counsel and Privacy Lead", "Leadership", "P-01", date(2021, 6, 1))
person("P-05", "Rosa Delgado", "Head of Payroll Operations", "Payroll operations", "P-02", date(2015, 5, 18))
staff(6, 15, ["Senior Payroll Specialist", "Payroll Specialist", "Payroll Specialist", "Implementation Specialist"], "Payroll operations", "P-05", 2016)
person("P-21", "Yara Castillo", "Payroll Specialist", "Payroll operations", "P-05", date(2026, 10, 19), status="onboarding")
person("P-22", "Omar Keane", "Payroll Specialist", "Payroll operations", "P-05", date(2026, 10, 26), status="onboarding")
person("P-23", "Kwame Mensah", "Head of Client Services", "Client services", "P-02", date(2017, 2, 6))
staff(24, 8, ["Client Success Manager", "Support Specialist", "Client Success Manager"], "Client services", "P-23", 2017)
person("P-32", "Esme Donnelly", "Support Specialist", "Client services", "P-23", date(2026, 10, 26), status="onboarding")
person("P-33", "Maureen Fitzgerald", "Controller", "Finance", "P-03", date(2019, 4, 1))
staff(34, 3, ["Staff Accountant", "Accounts Payable Specialist", "Staff Accountant"], "Finance", "P-33", 2019)
person("P-37", "Derek Sullivan", "Head of Sales", "Sales and marketing", "P-01", date(2020, 8, 17))
staff(38, 4, ["Account Executive", "Marketing Manager", "Account Executive", "Marketing Coordinator"], "Sales and marketing", "P-37", 2020)
person("P-42", "Elena Vasquez", "Head of People", "HR", "P-02", date(2019, 10, 7))
staff(43, 2, ["HR Generalist", "Recruiter"], "HR", "P-42", 2021)
person("P-45", "Lin Zhao", "Head of Product", "Product and engineering", "P-02", date(2020, 2, 3))
staff(46, 5, ["Software Engineer", "Senior Software Engineer", "Software Engineer", "QA Engineer", "Software Engineer"], "Product and engineering", "P-45", 2020)
person("P-51", "Nadia Haddad", "Compliance Analyst", "Compliance", "P-04", date(2022, 11, 14))
person("P-52", "Connor Byrne", "Compliance Associate", "Compliance", "P-04", date(2024, 7, 8))
assert len(PEOPLE) == 52, len(PEOPLE)

# People with accounts who are not Saltmarsh employees.
person("X-01", "Marcus Okafor", "Account Lead, Bay State IT Partners (outside IT provider)", "IT provider", "P-02", date(2022, 1, 10),
       employment="provider", external=True, counted=False)
person("X-02", "Alex Dennis", "Fractional Security Lead, Alimi", "Security (fractional)", "P-01", date(2026, 9, 22),
       email=f"alex.dennis_alimi.example#EXT#@{DOMAIN}", employment="provider", external=True, counted=False)
person("X-03", "Nora Gomez", "Systems Engineer, Bay State IT Partners", "IT provider", "X-01", date(2023, 5, 2),
       email=f"adm-ngomez@{DOMAIN}", employment="provider", external=True, counted=False)
person("X-04", "Sam Whitfield", "Account Manager, Harborline Insurance Brokers", "Broker (guest)", None, date(2026, 10, 1),
       email=f"sam.whitfield_harborline.example#EXT#@{DOMAIN}", employment="guest", external=True, counted=False)

ROLES = {
    "CEO": "P-01",
    "Security Lead": "X-02",
    "IT Lead": "X-01",
    "HR Lead": "P-42",
    "Finance Lead": "P-03",
    "Privacy Lead": "P-04",
    "AI Lead": "P-02",
}
GROUPS = {
    "All staff": [p["id"] for p in PEOPLE if p["counted"]],
    "Leadership": ["P-01", "P-02", "P-03", "P-04"],
    "Payroll operations": [p["id"] for p in PEOPLE if p["department"] == "Payroll operations"],
    "Finance": [p["id"] for p in PEOPLE if p["department"] in ("Finance",)] + ["P-03"],
    "Client services": [p["id"] for p in PEOPLE if p["department"] == "Client services"],
    "Engineering": [p["id"] for p in PEOPLE if p["department"] == "Product and engineering"],
    "Money movers": ["P-01", "P-02", "P-03", "P-05", "P-33", "P-34", "P-35", "P-36"]
    + [p["id"] for p in PEOPLE if p["department"] == "Payroll operations"],
}
GROUPS["Money movers"] = sorted(set(GROUPS["Money movers"]), key=lambda s: int(s.split("-")[1]))

NEW_HIRES = ["P-21", "P-22", "P-32"]
AI_POLICY_PENDING = ["P-09", "P-16", "P-27", "P-39", "P-48"]  # besides the new hires
TR02_OVERDUE = ["P-20", "P-34"]
TR03_DUE = ["P-07", "P-12", "P-19", "P-25", "P-31", "P-40", "P-44", "P-47"]  # besides AI-policy pending people
MFA_UNREGISTERED = set(NEW_HIRES)
DEVICE_NOT_COMPLIANT = {"P-14": "Windows update pending for 21 days", "P-27": "No check-in for 12 days"}

for p in PEOPLE:
    pid = p["id"]
    counted = p["counted"]
    pending = []
    if pid in NEW_HIRES:
        pending = "all"
    elif pid in AI_POLICY_PENDING:
        pending = ["POL-22"]
    p["policies_pending"] = pending if counted else []
    training = {}
    if counted:
        if pid in NEW_HIRES:
            start = date.fromisoformat(p["start_date"])
            training["TR-01"] = {"status": "due", "completed": None, "due": iso(start + timedelta(days=30))}
            training["TR-03"] = {"status": "due", "completed": None, "due": iso(start + timedelta(days=30))}
        else:
            done = AS_OF - timedelta(days=rng.randint(10, 45))
            training["TR-01"] = {"status": "completed", "completed": iso(done), "due": iso(done.replace(year=done.year + 1))}
            if pid in AI_POLICY_PENDING or pid in TR03_DUE:
                training["TR-03"] = {"status": "due", "completed": None, "due": "2026-11-10"}
            else:
                done3 = date(2026, 10, rng.randint(11, 30))
                training["TR-03"] = {"status": "completed", "completed": iso(done3), "due": "2027-10-10"}
        if pid in GROUPS["Money movers"]:
            if pid in TR02_OVERDUE:
                training["TR-02"] = {"status": "overdue", "completed": "2025-09-30", "due": "2026-09-30"}
            elif pid in NEW_HIRES:
                training["TR-02"] = {"status": "due", "completed": None, "due": iso(date.fromisoformat(p["start_date"]) + timedelta(days=30))}
            else:
                done2 = date(2026, rng.choice([8, 9]), rng.randint(1, 28))
                training["TR-02"] = {"status": "completed", "completed": iso(done2), "due": iso(done2.replace(year=2027))}
    p["training"] = training
    if counted:
        bg = {"status": "completed", "date": iso(date.fromisoformat(p["start_date"]) - timedelta(days=rng.randint(5, 20)))}
        if pid == "P-32":
            bg = {"status": "pending", "date": None}
        p["background_check"] = bg
    else:
        p["background_check"] = {"status": "not_required", "date": None}
    p["mfa_registered"] = pid not in MFA_UNREGISTERED
    p["device"] = None
    p["device_issue"] = DEVICE_NOT_COMPLIANT.get(pid)

# --------------------------------------------------------------------------- devices (assets)

DEVICES = []
for i, p in enumerate([p for p in PEOPLE if p["counted"]], start=1):
    mac = p["department"] in ("Product and engineering",) or p["title"] in ("Marketing Manager", "Marketing Coordinator")
    did = f"D-{i:02d}"
    p["device"] = did
    last = AS_OF - timedelta(days=0 if p["id"] not in DEVICE_NOT_COMPLIANT else 12)
    if p["id"] == "P-14":
        last = AS_OF - timedelta(days=1)
    DEVICES.append({
        "id": did,
        "name": f"SP-{'MBP' if mac else 'LT'}-{100 + i}",
        "type": "laptop",
        "assigned_to": p["id"],
        "os": "macOS 15.6" if mac else rng.choice(["Windows 11 24H2", "Windows 11 24H2", "Windows 11 23H2"]),
        "managed_by": "Intune",
        "encrypted": True,
        "encryption": "FileVault" if mac else "BitLocker",
        "edr": "Defender for Business",
        "edr_active": True,
        "screen_lock_minutes": 10,
        "auto_updates": True,
        "last_check_in": iso(datetime.combine(last, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=9)),
        "compliant": p["id"] not in DEVICE_NOT_COMPLIANT,
        "issue": DEVICE_NOT_COMPLIANT.get(p["id"]),
    })
DEVICES.append({"id": "D-53", "name": "SP-DT-201", "type": "desktop", "assigned_to": None, "shared_use": "Payroll operations print station",
                "os": "Windows 11 24H2", "managed_by": "Intune", "encrypted": True, "encryption": "BitLocker", "edr": "Defender for Business",
                "edr_active": True, "screen_lock_minutes": 10, "auto_updates": True, "last_check_in": iso(days_ago(0, 9)), "compliant": True, "issue": None})
DEVICES.append({"id": "D-54", "name": "SP-DT-202", "type": "desktop", "assigned_to": None, "shared_use": "Payroll operations print station",
                "os": "Windows 11 24H2", "managed_by": "Intune", "encrypted": True, "encryption": "BitLocker", "edr": "Defender for Business",
                "edr_active": True, "screen_lock_minutes": 10, "auto_updates": True, "last_check_in": iso(days_ago(0, 9)), "compliant": True, "issue": None})
DEVICES.append({"id": "D-55", "name": "SP-CONF-01", "type": "desktop", "assigned_to": None, "shared_use": "Conference room PC",
                "os": "Windows 11 23H2", "managed_by": "Intune", "encrypted": True, "encryption": "BitLocker", "edr": None,
                "edr_active": False, "screen_lock_minutes": 10, "auto_updates": True, "last_check_in": iso(days_ago(2, 9)), "compliant": False,
                "issue": "EDR not installed (the one device of 55 without it)"})

# --------------------------------------------------------------------------- Microsoft 365 snapshot

users = []
uid = {}


def add_user(key: str, upn: str, display: str, *, enabled=True, user_type="Member", created: date, last_sign_in: datetime | None,
             has_mailbox=True, mfa: bool | None, methods: list[str]):
    i = f"u-{len(users) + 1:03d}"
    uid[key] = i
    users.append({
        "id": i, "upn": upn, "display_name": display, "enabled": enabled, "user_type": user_type,
        "created": iso(datetime.combine(created, datetime.min.time(), tzinfo=timezone.utc)),
        "last_sign_in": iso(last_sign_in), "has_mailbox": has_mailbox, "mfa_registered": mfa, "mfa_methods": methods,
    })


for p in PEOPLE:
    if p["employment"] == "guest" or p["id"] == "X-02":
        continue
    start = date.fromisoformat(p["start_date"])
    if p["id"] in NEW_HIRES:
        last = days_ago(rng.randint(1, 3), 13)
    else:
        last = SCAN_AT - timedelta(hours=rng.randint(2, 70))
    methods = [] if not p["mfa_registered"] else rng.choice([["microsoftAuthenticatorPush"], ["microsoftAuthenticatorPush", "fido2"], ["microsoftAuthenticatorPush", "sms"]])
    # X-03 is an admin-only account at the IT provider: no mailbox, so it is never used for daily work.
    add_user(p["id"], p["email"], p["name"], created=start, last_sign_in=last, has_mailbox=p["id"] != "X-03",
             mfa=p["mfa_registered"], methods=["fido2", "microsoftAuthenticatorPush"] if p["id"] == "X-03" else methods)

add_user("adm-mokafor", f"adm-mokafor@{DOMAIN}", "Marcus Okafor (admin)", created=date(2022, 1, 10), last_sign_in=SCAN_AT - timedelta(hours=30),
         has_mailbox=False, mfa=True, methods=["fido2", "microsoftAuthenticatorPush"])
add_user("breakglass", f"breakglass@{DOMAIN}", "Emergency access", created=date(2022, 1, 10), last_sign_in=datetime(2026, 7, 14, 15, 0, tzinfo=timezone.utc),
         has_mailbox=False, mfa=True, methods=["fido2"])
add_user("payroll-shared", f"payroll@{DOMAIN}", "Payroll (shared mailbox)", created=date(2015, 6, 1), last_sign_in=None, has_mailbox=True, mfa=False, methods=[])
add_user("support-shared", f"support@{DOMAIN}", "Support (shared mailbox)", created=date(2017, 3, 1), last_sign_in=None, has_mailbox=True, mfa=False, methods=[])
add_user("X-02", f"alex.dennis_alimi.example#EXT#@{DOMAIN}", "Alex Dennis (Alimi)", user_type="Guest", created=date(2026, 9, 22),
         last_sign_in=SCAN_AT - timedelta(hours=26), has_mailbox=False, mfa=True, methods=["microsoftAuthenticatorPush"])
add_user("X-04", f"sam.whitfield_harborline.example#EXT#@{DOMAIN}", "Sam Whitfield (Harborline)", user_type="Guest", created=date(2026, 10, 1),
         last_sign_in=days_ago(20, 16), has_mailbox=False, mfa=True, methods=["sms"])
add_user("auditor-2025", f"r.chen_meridiancpa.example#EXT#@{DOMAIN}", "R. Chen (Meridian CPA, 2025 audit)", user_type="Guest", enabled=False,
         created=date(2025, 9, 1), last_sign_in=datetime(2025, 11, 20, 18, 0, tzinfo=timezone.utc), has_mailbox=False, mfa=True, methods=["sms"])

SNAPSHOT = {
    "tenant_display_name": "Saltmarsh Payroll",
    "verified_domains": [DOMAIN, "saltmarshpayroll.example", "saltmarshpayroll.onmicrosoft.com"],
    "collected_at": iso(SCAN_AT),
    "users": users,
    "conditional_access_policies": [
        {"id": "ca-001", "display_name": "Require MFA for all users", "state": "enabled", "include_users": ["All"],
         "exclude_users": [uid["breakglass"]], "include_applications": ["All"], "client_app_types": ["browser", "mobileAppsAndDesktopClients"],
         "grant_controls": ["mfa"]},
        {"id": "ca-002", "display_name": "Block legacy authentication", "state": "enabled", "include_users": ["All"],
         "exclude_users": [uid["breakglass"]], "include_applications": ["All"], "client_app_types": ["exchangeActiveSync", "other"],
         "grant_controls": ["block"]},
        {"id": "ca-003", "display_name": "Require a compliant device for Microsoft 365", "state": "enabled", "include_users": ["All"],
         "exclude_users": [uid["breakglass"], uid["X-02"], uid["X-04"]], "include_applications": ["Office365"],
         "client_app_types": ["browser", "mobileAppsAndDesktopClients"], "grant_controls": ["compliantDevice"]},
        {"id": "ca-004", "display_name": "Block sign-in from outside the United States (report only)", "state": "enabledForReportingButNotEnforced",
         "include_users": ["All"], "exclude_users": [uid["breakglass"]], "include_applications": ["All"], "client_app_types": ["all"],
         "grant_controls": ["block"]},
    ],
    "security_defaults_enabled": False,
    "legacy_auth_sign_ins_30d": 0,
    "role_assignments": [
        {"role_template_id": "62e90394-69f5-4237-9190-012177145e10", "role_name": "Global Administrator",
         "member_ids": [uid["adm-mokafor"], uid["X-03"], uid["breakglass"]]},
        {"role_template_id": "29232cdf-9323-42fd-ade2-1d097af3e4de", "role_name": "Exchange Administrator", "member_ids": [uid["adm-mokafor"]]},
        {"role_template_id": "fe930be7-5e62-47db-91af-98c3a49a38b1", "role_name": "User Administrator", "member_ids": [uid["X-03"]]},
        {"role_template_id": "f2ef992c-3afb-46b9-b7cf-a126ee74c451", "role_name": "Global Reader", "member_ids": [uid["P-02"], uid["X-02"]]},
        {"role_template_id": "5d6b6bb7-de71-4623-b4af-96380a352509", "role_name": "Security Reader", "member_ids": [uid["X-02"]]},
    ],
    "inbox_rules": [
        {"user_upn": f"jordan.ortiz@{DOMAIN}", "name": "Copy to home", "enabled": True, "forward_to": ["j.ortiz.home@gmail.example"], "redirect_to": []},
        {"user_upn": f"derek.sullivan@{DOMAIN}", "name": "Newsletters to folder", "enabled": True, "forward_to": [], "redirect_to": []},
        {"user_upn": f"rosa.delgado@{DOMAIN}", "name": "Vacation cover (off)", "enabled": False, "forward_to": [f"kwame.mensah@{DOMAIN}"], "redirect_to": []},
    ],
    "outbound_forwarding_blocked": False,
    "email_auth": [
        {"domain": DOMAIN, "spf": "v=spf1 include:spf.protection.outlook.com include:_spf.ledgerline.example -all", "dkim_enabled": True,
         "dmarc": "v=DMARC1; p=quarantine; rua=mailto:dmarc@saltmarsh.example; pct=100; adkim=s; aspf=s"},
        {"domain": "saltmarshpayroll.example", "spf": "v=spf1 -all", "dkim_enabled": True, "dmarc": "v=DMARC1; p=reject; rua=mailto:dmarc@saltmarsh.example"},
    ],
    "sharing": {"sharing_capability": "externalUserAndGuestSharing", "anonymous_link_expiration_days": None},
    "audit": {"unified_audit_log_enabled": True, "retention_days": 180, "directory_audit_available": True},
    "secure_score": {"current": 66.5, "max": 100, "created": iso(SCAN_AT - timedelta(hours=6))},
    "notes": ["Sample tenant for the Alimi demo. Fictional company; nothing here was read from a real tenant."],
}
assert len([u for u in users if u["user_type"] == "Member" and u["enabled"] and not u["mfa_registered"]]) == 5

# make P-14 the person with the forwarding rule
P14 = next(p for p in PEOPLE if p["id"] == "P-14")
SNAPSHOT["inbox_rules"][0]["user_upn"] = P14["email"]
SNAPSHOT["inbox_rules"][0]["forward_to"] = [f"{P14['name'].split()[0].lower()}.{P14['name'].split()[1].lower()}.home@gmail.example"]
P37 = next(p for p in PEOPLE if p["id"] == "P-37")
SNAPSHOT["inbox_rules"][1]["user_upn"] = P37["email"]

# --------------------------------------------------------------------------- company

COMPANY = {
    "sample": True,
    "name": "Saltmarsh Payroll, Inc.",
    "short_name": "Saltmarsh Payroll",
    "as_of": iso(AS_OF),
    "location": "Quincy, Massachusetts",
    "headcount": 52,
    "founded": 2014,
    "sector": "Payroll, tax filing and benefits administration for about 300 small employers in New England",
    "domain": DOMAIN,
    "workspace": "Microsoft 365 Business Premium",
    "it_provider": "Bay State IT Partners (outside provider, fictional)",
    "insurance": {
        "carrier": "Granite Harbor Mutual (fictional)",
        "broker": "Harborline Insurance Brokers (fictional)",
        "broker_contact": "X-04",
        "renewal": "2027-01-15",
        "questionnaire_due": "2026-12-15",
        "last_year_premium_note": "Renewal quote arrives after the questionnaire; the broker asked for the evidence pack by Dec 15.",
    },
    "customer_review": {
        "name": "First Quincy Savings Bank (fictional)",
        "kind": "Vendor security questionnaire from a client bank",
        "opened": "2026-10-06",
        "due": "2026-12-01",
        "questions": 30,
    },
    "pilot_letter": {"signed": "2026-09-22", "signed_by": "P-01", "scope": "Read-only Microsoft 365 scan, policy adoption, insurer evidence pack, quarterly reviews"},
    "scan": {"platform": "m365", "collected_at": iso(SCAN_AT), "schedule": "Weekly, Friday evening", "mode": "read-only"},
    "remediation_plan": [
        {"test": "m365.mfa.coverage", "owner": "X-01", "due": "2026-11-15", "action": "Register the three new hires during onboarding; convert payroll@ and support@ to sign-in-blocked shared mailboxes."},
        {"test": "m365.forwarding.external", "owner": "X-01", "due": "2026-11-07", "action": "Inbox rule removed Oct 31. Set the outbound anti-spam policy to Automatic forwarding: Off and attach the screenshot (EV-15)."},
        {"test": "m365.sharing.anonymous_links", "owner": "X-01", "due": "2026-11-08", "action": "Set anyone links to expire after 30 days, then move the tenant to existing guests only once client-file sites are checked."},
    ],
    "frameworks": ["insurer", "soc2", "iso27001", "hipaa", "iso42001"],
    "framework_targets": {
        "insurer": {"label": "Cyber insurance renewal", "date": "2027-01-15"},
        "soc2": {"label": "SOC 2 Type I readiness", "date": "2027-06-30"},
        "iso27001": {"label": "Gap check only", "date": None},
        "hipaa": {"label": "Benefits data for two clients", "date": None},
        "iso42001": {"label": "AI governance baseline", "date": "2027-03-31"},
    },
    "roles": ROLES,
    "groups": GROUPS,
}

# --------------------------------------------------------------------------- control assignments

ASSIGNMENTS = {}
for n in range(1, 41):
    cid = f"CTL-{n:02d}"
    ASSIGNMENTS[cid] = {"owner": None, "approver": "P-01", "note": None}
# owner from the role placeholder is resolved at build time; two controls deliberately have none
ASSIGNMENTS["CTL-21"] = {"owner": None, "approver": "P-01", "note": "Owner left in September; reassign (Privacy Lead or Head of Payroll Operations)", "unassigned": True}
ASSIGNMENTS["CTL-37"] = {"owner": None, "approver": "P-01", "note": "Office manager role is open after the move to Quincy", "unassigned": True}

# --------------------------------------------------------------------------- policies (adoption state)

POLICY_META = {
    "POL-01": ("2.1", "published", "2026-03-10", "X-02", "P-01", "all"),
    "POL-02": ("2.0", "published", "2026-03-10", "X-02", "P-01", "all"),
    "POL-03": ("2.0", "published", "2026-03-10", "X-02", "P-01", "all"),
    "POL-04": ("2.0", "published", "2026-03-10", "X-01", "P-01", "all"),
    "POL-05": ("1.2", "published", "2026-03-10", "X-01", "P-02", "all"),
    "POL-06": ("1.1", "published", "2026-03-10", "P-04", "P-01", "all"),
    "POL-07": ("1.0", "published", "2026-03-10", "X-01", "P-02", "all"),
    "POL-08": ("1.1", "published", "2026-05-05", "P-45", "P-02", "Engineering"),
    "POL-09": ("1.1", "published", "2026-03-10", "X-01", "P-02", "all"),
    "POL-10": ("1.0", "published", "2026-03-10", "X-01", "P-02", "all"),
    "POL-11": ("1.1", "renews_soon", "2025-11-20", "X-01", "P-02", "all"),
    "POL-12": ("1.3", "published", "2026-04-14", "P-02", "P-01", "all"),
    "POL-13": ("2.0", "published", "2026-03-10", "X-02", "P-01", "all"),
    "POL-14": ("1.1", "published", "2026-03-10", "P-02", "P-01", "all"),
    "POL-15": ("1.0", "past_due", "2025-09-18", "X-02", "P-01", "all"),
    "POL-16": ("1.2", "published", "2026-03-10", "P-42", "P-01", "all"),
    "POL-17": ("1.1", "draft", "2025-07-01", "P-02", "P-01", "all"),
    "POL-18": ("1.0", "published", "2026-03-10", "X-01", "P-02", "all"),
    "POL-19": ("1.0", "published", "2026-03-10", "X-01", "P-02", "all"),
    "POL-20": ("1.1", "needs_approval", "2025-10-22", "P-04", "P-01", "all"),
    "POL-21": ("1.0", "published", "2026-04-01", "P-04", "P-01", "all"),
    "POL-22": ("1.0", "published", "2026-10-10", "P-02", "P-01", "all"),
    "POL-23": ("0.9", "draft", None, "P-02", "P-01", "all"),
}
STATUS_LABEL = {"published": "Published", "renews_soon": "Renews soon", "past_due": "Past due", "needs_approval": "Needs approval", "draft": "Draft"}
POLICIES = []
for pid, (version, status, approved, owner, approver, applies) in POLICY_META.items():
    approved_d = date.fromisoformat(approved) if approved else None
    next_review = iso(approved_d.replace(year=approved_d.year + 1)) if approved_d else None
    history = []
    if approved_d:
        if version.startswith("2") or version == "1.1" and pid in ("POL-04", "POL-06", "POL-09", "POL-11", "POL-14"):
            history.append({"version": "1.0", "date": "2024-02-15", "summary": "First adoption, written in-house.", "approved_by": "P-01"})
        if version == "1.2" or version == "1.3":
            history.append({"version": "1.0", "date": "2024-02-15", "summary": "First adoption, written in-house.", "approved_by": "P-01"})
            history.append({"version": "1.1", "date": "2025-04-01", "summary": "Yearly review, minor wording.", "approved_by": "P-01"})
        history.append({"version": version, "date": approved, "summary": "Rewritten on the Alimi template, mapped to SOC 2, ISO 27001 and the insurer questions." if approved >= "2026-03-01" else "Yearly review.", "approved_by": approver})
    pending_note = None
    if status == "needs_approval":
        pending_note = "v1.1 submitted to the CEO on Oct 22, 2026: adds the retention schedule the bank asked for."
    if status == "draft" and pid == "POL-17":
        pending_note = "v1.1 in draft since the move to the Quincy office; v1.0 of Jul 1, 2025 is past its review date."
    if status == "draft" and pid == "POL-23":
        pending_note = "First version in draft; the AI Lead and the Privacy Lead are reviewing the impact-assessment section."
    if status == "renews_soon":
        pending_note = "Yearly review due Nov 20, 2026."
    if status == "past_due":
        pending_note = "Yearly review was due Sep 18, 2026; the risk workshop that feeds it is scheduled for Nov 18."
    POLICIES.append({
        "id": pid, "version": version, "status": status, "status_label": STATUS_LABEL[status], "approved": approved,
        "next_review": next_review, "owner": owner, "approver": approver, "applies_to": applies, "history": history, "note": pending_note,
    })

# --------------------------------------------------------------------------- evidence

E = []


def ev(eid, name, etype, controls, owner, created, renewal, artifact, description, **extra):
    rec = {"id": eid, "name": name, "type": etype, "controls": controls, "owner": owner, "created": created, "renewal": renewal,
           "artifact": artifact, "description": description}
    rec.update(extra)
    E.append(rec)


F = lambda name: {"kind": "file", "name": name}  # noqa: E731
L = lambda url, name: {"kind": "link", "name": name, "url": url}  # noqa: E731
SCAN = {"kind": "scan", "name": "Alimi scan, Oct 30, 2026", "ref": "scan.json"}

ev("EV-01", "Information Security Policy v2.1, approved", "policy", ["CTL-01"], "X-02", "2026-03-10", "2027-03-10", F("POL-01-v2.1-signed.pdf"),
   "The approved policy with the CEO's signature page and the version history.")
ev("EV-02", "Security roles and responsibilities (RACI)", "record", ["CTL-02"], "X-02", "2026-03-10", "2027-03-10", F("security-raci-2026.xlsx"),
   "Who owns what: CEO, COO, outside IT provider, fractional security lead, HR, Finance, Privacy.")
ev("EV-03", "Risk assessment workshop report, September 2025", "record", ["CTL-03"], "X-02", "2025-09-18", "2026-09-18", F("risk-assessment-2025-09.pdf"),
   "Last year's risk workshop and treatment plan. The 2026 workshop is scheduled for Nov 18.")
ev("EV-04", "Policy acknowledgement report", "export", ["CTL-04"], "P-42", "2026-10-01", "2027-10-01", L("#/policies", "Policies page, acknowledgements"),
   "Who has accepted which policy, exported from this platform.")
ev("EV-05", "Security awareness training completion export", "export", ["CTL-05"], "P-42", "2026-10-15", "2027-10-15", F("training-completion-2026-10.csv"),
   "49 of 52 completed the yearly course; 3 new hires are inside their 30-day window.")
ev("EV-06", "Phishing simulation results, Q3 2026", "report", ["CTL-05"], "X-01", "2026-09-30", "2026-12-30", F("phishing-sim-2026-q3.pdf"),
   "Click rate 4.1 percent, report rate 61 percent; two people retrained.")
ev("EV-07", "Background screening agreement and procedure", "contract", ["CTL-06"], "P-42", "2024-06-01", "2027-06-01", F("clearpath-msa-2024.pdf"),
   "Agreement with ClearPath Screening and the procedure that says which roles need which check.")
ev("EV-08", "Joiner, mover and leaver checklist with Q3 leaver sample", "record", ["CTL-07"], "P-42", "2026-10-05", "2027-01-05", F("jml-q3-2026.pdf"),
   "Three leavers in Q3; access removed the same day in each case, with the ticket numbers.")
ev("EV-09", "Payment verification procedure and callback log", "record", ["CTL-08"], "P-03", "2026-08-20", "2026-11-20", F("callback-log-2026-q3.xlsx"),
   "The verify-before-you-pay procedure from the Alimi kit and the quarter's callback log: 31 bank-detail changes, 31 callbacks.")
ev("EV-10", "Alimi scan report, Oct 30, 2026", "report", ["CTL-09", "CTL-10", "CTL-11", "CTL-12", "CTL-14", "CTL-15", "CTL-17", "CTL-27", "CTL-30"],
   "X-02", "2026-10-30", "2026-11-30", SCAN, "The weekly read-only scan of the Microsoft 365 tenant: 12 automated checks, 3 attestations.")
ev("EV-11", "Conditional Access policy export", "export", ["CTL-09", "CTL-10", "CTL-28"], "X-01", "2026-10-28", "2027-01-28", F("conditional-access-2026-10-28.json"),
   "The four policies as exported from Entra: MFA for all, block legacy auth, compliant device, geo block (report only).")
ev("EV-12", "Quarterly access review, Q3 2026", "record", ["CTL-12"], "P-02", "2026-10-02", "2027-01-02", F("access-review-2026-q3.pdf"),
   "Signed by the COO: all accounts, admin roles, guests and shared mailboxes reviewed; two guests removed.")
ev("EV-13", "Password manager rollout report", "export", ["CTL-13"], "X-01", "2026-07-15", "2027-07-15", F("password-manager-rollout.pdf"),
   "52 of 52 staff enrolled; shared secrets moved to team vaults.")
ev("EV-14", "DMARC monitoring report, October", "report", ["CTL-14"], "X-01", "2026-10-01", "2026-11-15", F("dmarc-report-2026-10.pdf"),
   "Both sending domains at p=quarantine or p=reject; 99.6 percent of mail aligned.")
ev("EV-15", "Outbound anti-spam policy: automatic forwarding off", "export", ["CTL-15"], "X-01", None, None, None,
   "Requested from the IT provider after the Oct 30 scan found forwarding still allowed. Screenshot of the Defender setting due Nov 7.",
   requested_on="2026-10-31", due="2026-11-07")
ev("EV-16", "Defender for Office 365 anti-phishing and Safe Links policies", "export", ["CTL-16"], "X-01", "2026-09-12", "2027-03-12", F("defender-o365-policies.pdf"),
   "Preset security policy: Standard, applied to every mailbox.")
ev("EV-17", "SharePoint and OneDrive sharing settings", "export", ["CTL-17"], "X-01", "2026-06-30", "2026-12-30", F("sharepoint-sharing-2026-06.png"),
   "Screenshot from the SharePoint admin center. The scan shows anyone links still allowed without expiry; change scheduled for Nov 8.")
ev("EV-18", "Data classification scheme", "policy", ["CTL-18"], "P-04", "2026-03-10", "2027-03-10", F("POL-06-appendix-classification.pdf"),
   "Four levels (Public, Internal, Confidential, Restricted) and the handling rules for each.")
ev("EV-19", "Intune encryption compliance report", "export", ["CTL-19", "CTL-22"], "X-01", "2026-10-27", "2026-11-27", F("intune-encryption-2026-10-27.csv"),
   "55 of 55 managed devices encrypted (BitLocker or FileVault).")
ev("EV-20", "Approved apps register and OAuth consent review", "register", ["CTL-20"], "P-02", "2026-10-15", "2027-01-15", F("approved-apps-2026-10.xlsx"),
   "Every third-party app connected to the tenant, with an owner and a decision; Dropbox flagged for review.")
ev("EV-21", "Retention schedule", "policy", ["CTL-21"], None, None, None, None,
   "No approved schedule yet; POL-20 v1.1 adds it and is waiting for the CEO's approval.", requested_on="2026-10-22", due="2026-11-30")
ev("EV-22", "Intune device compliance policy export", "export", ["CTL-22"], "X-01", "2026-10-27", "2027-01-27", F("intune-compliance-policy.json"),
   "Screen lock at 10 minutes, encryption required, OS minimum versions, EDR required.")
ev("EV-23", "EDR coverage export from the IT provider", "export", ["CTL-23"], "X-01", "2026-10-29", "2026-11-29", F("defender-devices-2026-10-29.csv"),
   "Defender for Business active on 54 of 55 devices (98 percent); the conference room PC is the exception.", attests=["att.edr.coverage"])
ev("EV-24", "Patch compliance report, October", "report", ["CTL-24"], "X-01", "2026-10-29", "2026-11-29", F("patch-compliance-2026-10.pdf"),
   "Critical updates installed within 14 days on 53 of 55 devices; two laptops pending.")
ev("EV-25", "Vulnerability scan report", "report", ["CTL-25"], "X-01", "2026-08-14", "2026-09-14", F("vuln-scan-2026-08.pdf"),
   "External and internal scan from August. The monthly cadence slipped in September and October.")
ev("EV-26", "Asset inventory export", "register", ["CTL-26"], "X-01", "2026-10-27", "2027-01-27", F("asset-inventory-2026-10-27.xlsx"),
   "55 devices, 21 SaaS applications, 3 data stores, each with an owner.")
ev("EV-27", "Microsoft Secure Score snapshot", "report", ["CTL-27"], "X-01", "2026-10-28", "2026-11-28", SCAN,
   "66.5 of 100 on Oct 30; up from 48 in June.")
ev("EV-28", "Remote access standard", "export", ["CTL-28"], "X-01", "2026-05-05", "2027-05-05", F("remote-access-standard-2026.pdf"),
   "VPN retired in May; access to Microsoft 365 requires MFA and a compliant device (Conditional Access).")
ev("EV-29", "Change log sample: client portal releases, Q3", "record", ["CTL-29"], "P-45", "2026-10-01", "2027-01-01", L("https://github.example/saltmarsh/portal/releases", "Portal releases"),
   "Eleven releases, each with a reviewer and a test record.")
ev("EV-30", "Purview audit retention and alert policies", "export", ["CTL-30"], "X-01", "2026-10-28", "2027-01-28", F("purview-audit-2026-10-28.png"),
   "Unified audit log on, 180-day retention, alerts on admin role changes and new forwarding rules.")
ev("EV-31", "Backup restore test record, September 2026", "record", ["CTL-31"], "X-01", "2026-09-26", "2026-12-26", F("restore-test-2026-09-26.pdf"),
   "Mailbox and SharePoint restore from Harborvault in 41 minutes; immutable copies confirmed.", attests=["att.backups.tested"])
ev("EV-32", "Business continuity plan v1.3", "policy", ["CTL-32"], "P-02", "2026-04-14", "2027-04-14", F("bcp-v1.3.pdf"),
   "Recovery targets: payroll runs within 4 hours from the backup region; reviewed yearly.")
ev("EV-33", "Incident response plan v2.0", "policy", ["CTL-33"], "X-02", "2026-03-10", "2027-03-10", F("POL-13-v2.0-signed.pdf"),
   "Roles, contacts (IT provider, counsel, broker, carrier hotline), severity levels and the first-hour checklist.")
ev("EV-34", "Incident response tabletop exercise record", "record", ["CTL-33"], "X-02", "2025-08-21", "2026-08-21", F("tabletop-2025-08.pdf"),
   "Last exercise: a ransomware scenario, August 2025. The 2026 tabletop is scheduled for Nov 20.", attests=["att.ir_plan.tested"])
ev("EV-35", "Breach notification procedure and Massachusetts checklist", "policy", ["CTL-34"], "P-04", "2026-03-10", "2027-03-10", F("breach-notification-procedure.pdf"),
   "Who decides, who notifies, the deadlines, and the regulator contacts. [Legal review on file]")
ev("EV-36", "Vendor register and review schedule", "register", ["CTL-35"], "P-02", "2026-10-20", "2027-01-20", L("#/vendors", "Vendors page"),
   "Every vendor with data or system access, its tier, owner and next review.")
ev("EV-37", "Ledgerline SOC 2 Type II report (period to Jun 30, 2026)", "report", ["CTL-35"], "P-05", "2026-08-15", "2027-08-15", F("ledgerline-soc2-type2-2026.pdf"),
   "Reviewed by the Head of Payroll Operations; no exceptions relevant to Saltmarsh.")
ev("EV-38", "Privacy notice and data map", "policy", ["CTL-36"], "P-04", "2026-04-01", "2027-04-01", L("https://www.saltmarsh.example/privacy", "Privacy notice"),
   "The published notice and the map of personal data by system.")
ev("EV-39", "Office access list and visitor log sample", "record", ["CTL-37"], None, "2026-07-01", "2026-10-01", F("office-access-2026-07.pdf"),
   "Badge list from the Quincy office and July's visitor log. Needs a quarterly refresh and an owner.")
ev("EV-40", "AI Acceptable Use Policy v1.0, approved", "policy", ["CTL-38"], "P-02", "2026-10-10", "2027-10-10", F("POL-22-v1.0-signed.pdf"),
   "Approved by the CEO on Oct 10; acknowledgements under way.")
ev("EV-41", "AI tool inventory", "register", ["CTL-39"], "P-02", "2026-10-25", "2027-01-25", L("#/ai", "AI governance page"),
   "Eleven tools and agents with owner, data allowed, risk level and status.")
ev("EV-42", "AI transparency notice to clients", "record", ["CTL-40"], "P-04", None, None, None,
   "Draft with counsel: how clients are told when AI touches their payroll data, and how to raise a concern.", requested_on="2026-10-25", due="2026-12-15")

# --------------------------------------------------------------------------- vendors

RUBRIC_KEYS = ["data_types", "business_criticality", "integration_access", "communication_scope"]


def tier(scores: dict) -> str:
    total = sum(scores.values())
    if total >= 13:
        return "Critical"
    if total >= 10:
        return "High"
    if total >= 7:
        return "Medium"
    return "Low"


V = []


def vendor(vid, name, category, discovered, data, users, scores, owner, status, last, next_, evidence, **extra):
    scores_d = dict(zip(RUBRIC_KEYS, scores))
    rec = {"id": vid, "name": name, "category": category, "discovered_via": discovered, "data_shared": data, "users": users,
           "rubric": scores_d, "inherent_risk": tier(scores_d), "owner": owner, "review_status": status, "last_review": last,
           "next_review": next_, "evidence": evidence, "findings": [], "alerts": [], "activity": [], "subprocessor": False,
           "fictional": False, "ai": False}
    rec.update(extra)
    V.append(rec)
    return rec


vendor("V-01", "Microsoft 365", "Productivity, identity and email", "Microsoft 365 tenant", ["All company data", "Email", "Identities"], 58,
       [4, 4, 4, 4], "X-01", "Reviewed", "2026-09-15", "2027-09-15",
       [{"kind": "report", "name": "SOC 2 Type II (Service Trust Portal)", "date": "2026-09-15"}, {"kind": "contract", "name": "Microsoft Products and Services DPA", "date": "2022-01-10"}],
       subprocessor=True, activity=[{"date": "2026-09-15", "text": "Yearly review completed by Marcus Okafor; SOC 2 reviewed, no action."}])
vendor("V-02", "Ledgerline Payroll Engine", "Payroll processing platform", "Accounts payable", ["Employee personal data", "Social Security numbers", "Bank details", "Pay data"], 30,
       [4, 4, 3, 3], "P-05", "Reviewed", "2026-08-15", "2027-08-15",
       [{"kind": "report", "name": "SOC 2 Type II, period to Jun 30, 2026", "date": "2026-08-15", "evidence_id": "EV-37"}, {"kind": "contract", "name": "DPA signed", "date": "2024-01-05"}],
       subprocessor=True, fictional=True, ai=True,
       activity=[{"date": "2026-10-20", "text": "Vendor enabled Ledgerline Assist (AI) for all customers; added to the AI inventory as Under review."},
                 {"date": "2026-08-15", "text": "SOC 2 Type II received and reviewed by Rosa Delgado."}])
vendor("V-03", "TaxBridge e-File", "Federal and state tax filing", "Accounts payable", ["Employer identification numbers", "Social Security numbers", "Wage data"], 8,
       [4, 4, 3, 2], "P-03", "Due", "2025-10-30", "2026-10-30",
       [{"kind": "report", "name": "SOC 1 Type II (2025)", "date": "2025-10-30", "expired": True}, {"kind": "questionnaire", "name": "Security questionnaire sent", "date": "2026-10-20", "awaiting": True}],
       subprocessor=True, fictional=True,
       activity=[{"date": "2026-10-20", "text": "Questionnaire sent; reminder scheduled for Nov 3."}, {"date": "2026-10-30", "text": "Yearly review date passed; status Due."}])
vendor("V-04", "First Quincy Savings Bank", "ACH origination and banking", "Accounts payable", ["Bank account numbers", "Payment files"], 4,
       [4, 4, 2, 2], "P-03", "Reviewed", "2026-06-01", "2027-06-01",
       [{"kind": "report", "name": "Bank SOC 1 Type II", "date": "2026-06-01"}, {"kind": "contract", "name": "Treasury services agreement", "date": "2016-02-01"}],
       fictional=True, activity=[{"date": "2026-10-06", "text": "The bank opened its own vendor security review of Saltmarsh (see Questionnaires)."}])
vendor("V-05", "Bay State IT Partners", "Managed IT provider", "Manual", ["Administrative access to all systems"], 2,
       [4, 4, 4, 2], "P-02", "Reviewed", "2026-09-01", "2027-09-01",
       [{"kind": "contract", "name": "MSA with security addendum", "date": "2025-09-01"}, {"kind": "certificate", "name": "Cyber insurance certificate ($2M)", "date": "2026-09-01"}],
       fictional=True)
vendor("V-06", "Brightfile Client Portal", "Document exchange with clients", "Microsoft 365 app consent", ["Client payroll files", "Employee personal data"], 22,
       [4, 3, 3, 3], "P-45", "In progress", "2025-11-12", "2026-11-12",
       [{"kind": "report", "name": "SOC 2 Type II (2025)", "date": "2025-11-12"}, {"kind": "request", "name": "Incident report requested", "date": "2026-10-24", "awaiting": True}],
       subprocessor=True, fictional=True,
       alerts=[{"kind": "breach", "date": "2026-10-24", "text": "Brightfile disclosed unauthorized access to a support system between Oct 18 and Oct 22. The vendor says customer files were not affected. Incident report requested.", "flagged_as_finding": "VF-01"}],
       findings=[{"id": "VF-01", "date": "2026-10-24", "text": "Confirm no Saltmarsh files were in the affected support system; obtain the incident report by Nov 15; decide on continued use.", "owner": "P-45", "status": "Open", "risk": "R-05"}],
       activity=[{"date": "2026-10-24", "text": "Breach notice received; flagged as finding VF-01 and risk R-05 opened."}, {"date": "2026-10-25", "text": "Incident report requested from the vendor; clients informed that no Saltmarsh data was reported affected."}])
vendor("V-07", "DocuSign", "Electronic signature", "Microsoft 365 app consent", ["Client contracts", "Employee onboarding forms"], 12,
       [3, 3, 2, 3], "P-04", "Reviewed", "2026-05-20", "2027-05-20",
       [{"kind": "report", "name": "SOC 2 Type II (from the vendor's trust center)", "date": "2026-05-20"}], ai=True,
       activity=[{"date": "2026-10-12", "text": "Vendor added AI contract summaries; confirm the setting is off for Saltmarsh envelopes (AI feed)."}])
vendor("V-08", "QuickBooks Online", "Accounting", "Accounts payable", ["Company financials", "Vendor bank details"], 5,
       [3, 3, 2, 1], "P-03", "Reviewed", "2026-04-10", "2028-04-10", [{"kind": "report", "name": "SOC 2 (vendor trust page)", "date": "2026-04-10"}])
vendor("V-09", "HubSpot", "CRM and marketing", "Microsoft 365 app consent", ["Prospect and client contact details"], 9,
       [2, 2, 2, 3], "P-37", "Reviewed", "2026-03-02", "2028-03-02", [{"kind": "report", "name": "SOC 2 (vendor trust page)", "date": "2026-03-02"}], ai=True)
vendor("V-10", "Zoom", "Video meetings", "Microsoft 365 app consent", ["Meeting content"], 55,
       [2, 2, 1, 3], "X-01", "Reviewed", "2026-03-02", "2028-03-02", [{"kind": "report", "name": "SOC 2 (vendor trust page)", "date": "2026-03-02"}])
vendor("V-11", "Dropbox", "File sharing (not approved)", "Microsoft 365 app consent", ["Client files (6 people sharing)"], 6,
       [4, 2, 3, 3], None, "Under review", None, None, [],
       findings=[{"id": "VF-02", "date": "2026-10-28", "text": "Six staff connected personal Dropbox accounts and shared client files. Decide: approve with a business account and a DPA, or block and move files to SharePoint.", "owner": "P-02", "status": "Open", "risk": "R-06"}],
       activity=[{"date": "2026-10-28", "text": "Found by the Oct 28 OAuth consent review; no owner yet."}])
vendor("V-12", "ClearPath Screening", "Background checks", "Accounts payable", ["Social Security numbers", "Dates of birth", "Addresses"], 3,
       [4, 2, 1, 2], "P-42", "Reviewed", "2026-06-01", "2027-06-01",
       [{"kind": "report", "name": "SOC 2 Type II", "date": "2026-06-01"}, {"kind": "contract", "name": "MSA and DPA", "date": "2024-06-01", "evidence_id": "EV-07"}], fictional=True)
vendor("V-13", "Harborvault Backup", "SaaS backup for Microsoft 365", "Accounts payable", ["Copies of mailboxes and SharePoint"], 2,
       [4, 4, 4, 1], "X-01", "Reviewed", "2026-09-15", "2027-09-15",
       [{"kind": "report", "name": "SOC 2 Type II", "date": "2026-09-15"}, {"kind": "record", "name": "Restore test, Sep 26, 2026", "date": "2026-09-26", "evidence_id": "EV-31"}], subprocessor=True, fictional=True)
vendor("V-14", "Grammarly", "Writing assistant (AI)", "Microsoft 365 app consent", ["Text typed in email and documents"], 9,
       [3, 1, 2, 2], "P-02", "Reviewed", "2026-10-10", "2027-10-10", [{"kind": "record", "name": "AI tool review (POL-22)", "date": "2026-10-10"}], ai=True)
vendor("V-15", "OpenAI (ChatGPT Team)", "AI assistant", "Entra sign-in logs", ["Whatever staff paste; client data prohibited by policy"], 14,
       [3, 1, 1, 2], "P-02", "Reviewed", "2026-10-10", "2027-10-10",
       [{"kind": "record", "name": "AI tool review (POL-22)", "date": "2026-10-10"}, {"kind": "contract", "name": "Team plan terms: no training on business data", "date": "2026-10-10"}], ai=True)
vendor("V-16", "Otter.ai", "Meeting transcription (AI)", "Entra sign-in logs", ["Client call recordings"], 3,
       [4, 1, 2, 3], "P-23", "Blocked", "2026-10-10", None, [{"kind": "record", "name": "AI tool review: blocked", "date": "2026-10-10"}], ai=True,
       activity=[{"date": "2026-10-10", "text": "Blocked: records client calls without a consent step or a retention rule."}])
vendor("V-17", "Zapier", "Automation, including AI agents", "Microsoft 365 app consent", ["Payroll mailbox contents", "Ticket data"], 2,
       [3, 2, 3, 2], "P-05", "Under review", None, None, [{"kind": "request", "name": "DPA and agent scope requested", "date": "2026-10-28", "awaiting": True}], ai=True,
       activity=[{"date": "2026-10-28", "text": "Zapier turned on Agents for the Team plan; review opened (AI feed)."}])
vendor("V-18", "Mailchimp", "Client newsletters", "Accounts payable", ["Client contact emails"], 2,
       [2, 1, 1, 3], "P-37", "Reviewed", "2026-02-14", "2028-02-14", [{"kind": "report", "name": "SOC 2 (vendor trust page)", "date": "2026-02-14"}])
vendor("V-19", "Calendly", "Scheduling", "Microsoft 365 app consent", ["Calendar availability"], 6,
       [1, 1, 1, 3], "P-37", "Not required", None, None, [])
vendor("V-20", "Canva", "Design", "Microsoft 365 app consent", ["Marketing images"], 4,
       [1, 1, 1, 2], "P-37", "Not required", None, None, [], ai=True)
vendor("V-21", "Shred-Right Document Destruction", "Paper records disposal", "Accounts payable", ["Paper payroll records"], 1,
       [3, 1, 1, 1], None, "Not required", None, None, [{"kind": "contract", "name": "Service agreement and certificates of destruction", "date": "2025-01-15"}], fictional=True)

# --------------------------------------------------------------------------- AI tools and agents

AI = {
    "policy": "POL-22",
    "governance_policy": "POL-23",
    "controls": ["CTL-38", "CTL-39", "CTL-40"],
    "tools": [
        {"id": "AI-01", "name": "Microsoft 365 Copilot", "vendor": "Microsoft", "vendor_id": "V-01", "model": "GPT-4-class models run inside Microsoft's service boundary", "kind": "assistant",
         "discovered_via": "Microsoft 365 licence list", "users": 31, "data_allowed": ["Internal documents", "Email and Teams inside the tenant"],
         "data_prohibited": ["Client Social Security numbers outside Ledgerline"], "risk": "Medium", "status": "Approved", "owner": "P-02", "reviewed": "2026-10-10",
         "rule": "Approved. Client data stays inside the tenant and the vendor does not train on it (contract terms).", "iso42001": ["CTL-38", "CTL-39"]},
        {"id": "AI-02", "name": "ChatGPT (Team plan)", "vendor": "OpenAI", "vendor_id": "V-15", "model": "GPT-5 family", "kind": "assistant",
         "discovered_via": "Entra sign-in logs (Sign in with Microsoft)", "users": 14, "data_allowed": ["Drafting", "General research", "Public information"],
         "data_prohibited": ["Client or employee personal data", "Payroll files", "Anything classified Confidential or Restricted"], "risk": "Medium", "status": "Approved",
         "owner": "P-02", "reviewed": "2026-10-10", "rule": "Approved on the Team plan only; personal accounts are blocked at sign-in.", "iso42001": ["CTL-38", "CTL-39"]},
        {"id": "AI-03", "name": "Claude", "vendor": "Anthropic", "vendor_id": None, "model": "Claude", "kind": "assistant",
         "discovered_via": "Entra sign-in logs", "users": 4, "data_allowed": ["Code and documentation without client data"], "data_prohibited": ["Client data", "Production credentials"],
         "risk": "Medium", "status": "Under review", "owner": "P-45", "reviewed": None, "rule": "Engineering asked for a team plan; contract terms under review by the Privacy Lead.", "iso42001": ["CTL-38", "CTL-39"]},
        {"id": "AI-04", "name": "GitHub Copilot", "vendor": "GitHub (Microsoft)", "vendor_id": None, "model": "Mixed", "kind": "assistant",
         "discovered_via": "Engineering licence list", "users": 5, "data_allowed": ["Client portal source code"], "data_prohibited": ["Secrets", "Production data"],
         "risk": "Low", "status": "Approved", "owner": "P-45", "reviewed": "2026-10-10", "rule": "Approved for the portal repositories; secret scanning stays on.", "iso42001": ["CTL-38", "CTL-39"]},
        {"id": "AI-05", "name": "Grammarly", "vendor": "Grammarly", "vendor_id": "V-14", "model": "Vendor models", "kind": "assistant",
         "discovered_via": "Microsoft 365 app consent", "users": 9, "data_allowed": ["Email and document text classified Public or Internal"], "data_prohibited": ["Documents classified Confidential or Restricted"],
         "risk": "Medium", "status": "Approved", "owner": "P-02", "reviewed": "2026-10-10", "rule": "Approved; disabled in the payroll operations SharePoint site.", "iso42001": ["CTL-38", "CTL-39"]},
        {"id": "AI-06", "name": "Otter.ai", "vendor": "Otter.ai", "vendor_id": "V-16", "model": "Vendor models", "kind": "assistant",
         "discovered_via": "Entra sign-in logs", "users": 3, "data_allowed": [], "data_prohibited": ["Client call recordings"],
         "risk": "High", "status": "Blocked", "owner": "P-23", "reviewed": "2026-10-10", "rule": "Blocked Oct 10: records client calls with no consent step and no retention rule. Teams recap is the approved alternative.", "iso42001": ["CTL-38"]},
        {"id": "AI-07", "name": "Zapier Agents", "vendor": "Zapier", "vendor_id": "V-17", "model": "Vendor-selected models", "kind": "agent",
         "discovered_via": "Microsoft 365 app consent", "users": 2, "data_allowed": ["Ticket creation from the payroll mailbox (proposed)"], "data_prohibited": ["Reading mail beyond the payroll@ mailbox", "Sending mail to clients"],
         "risk": "High", "status": "Under review", "owner": "P-05", "reviewed": None, "rule": "An agent reads the payroll inbox and creates tickets. Needs a scoped mailbox, a DPA addendum and a log of its actions before approval.", "iso42001": ["CTL-38", "CTL-39", "CTL-40"]},
        {"id": "AI-08", "name": "Ledgerline Assist", "vendor": "Ledgerline (fictional)", "vendor_id": "V-02", "model": "Vendor models", "kind": "feature",
         "discovered_via": "Vendor change notice", "users": 30, "data_allowed": ["Summaries of payroll runs (vendor default)"], "data_prohibited": [],
         "risk": "High", "status": "Under review", "owner": "P-05", "reviewed": None, "rule": "Vendor turned it on for all customers on Oct 20. Ask for the AI addendum to the DPA and confirm no training on client data; clients are told through the transparency notice (CTL-40).", "iso42001": ["CTL-38", "CTL-39", "CTL-40"]},
        {"id": "AI-09", "name": "Fireflies.ai", "vendor": "Fireflies", "vendor_id": None, "model": "Vendor models", "kind": "assistant",
         "discovered_via": "Entra sign-in logs", "users": 1, "data_allowed": [], "data_prohibited": ["Meeting recordings"],
         "risk": "High", "status": "Blocked", "owner": "P-23", "reviewed": "2026-10-10", "rule": "Blocked for the same reasons as Otter.ai.", "iso42001": ["CTL-38"]},
        {"id": "AI-10", "name": "Canva Magic Studio", "vendor": "Canva", "vendor_id": "V-20", "model": "Vendor models", "kind": "feature",
         "discovered_via": "Microsoft 365 app consent", "users": 4, "data_allowed": ["Marketing images and copy"], "data_prohibited": ["Client names without consent"],
         "risk": "Low", "status": "Approved", "owner": "P-37", "reviewed": "2026-10-10", "rule": "Approved for marketing material.", "iso42001": ["CTL-39"]},
        {"id": "AI-11", "name": "HubSpot Breeze", "vendor": "HubSpot", "vendor_id": "V-09", "model": "Vendor models", "kind": "feature",
         "discovered_via": "Vendor change notice", "users": 9, "data_allowed": ["Prospect contact details", "Sales notes"], "data_prohibited": ["Client payroll data (never in the CRM)"],
         "risk": "Medium", "status": "Approved", "owner": "P-37", "reviewed": "2026-10-10", "rule": "Approved; the CRM holds no payroll data by policy.", "iso42001": ["CTL-38", "CTL-39"]},
    ],
    "vendor_changes": [
        {"date": "2026-10-28", "vendor": "Zapier", "vendor_id": "V-17", "change": "Agents turned on by default for the Team plan.", "affects": ["AI-07"],
         "recommendation": "Restrict the feature to the two payroll automation owners and finish the review before any agent touches the payroll mailbox."},
        {"date": "2026-10-20", "vendor": "Ledgerline (fictional)", "vendor_id": "V-02", "change": "Ledgerline Assist (AI summaries of client payroll runs) enabled for all customers.", "affects": ["AI-08"],
         "recommendation": "Request the AI addendum to the DPA, confirm no training on client data, and add the feature to the client transparency notice."},
        {"date": "2026-10-12", "vendor": "DocuSign", "vendor_id": "V-07", "change": "AI contract summaries added to envelopes.", "affects": [],
         "recommendation": "Confirm the setting is off for Saltmarsh envelopes, or add DocuSign to the AI inventory as a feature."},
        {"date": "2026-10-03", "vendor": "Grammarly", "vendor_id": "V-14", "change": "Updated data retention terms (text deleted after processing by default).", "affects": ["AI-05"],
         "recommendation": "No action; the new terms still meet the AI Acceptable Use Policy."},
    ],
}

# --------------------------------------------------------------------------- risks


def risk(rid, title, source, likelihood, impact, treatment, owner, controls, status, identified, next_review, description, **extra):
    score = likelihood * impact
    rating = "Critical" if score >= 12 else "High" if score >= 8 else "Medium" if score >= 4 else "Low"
    rec = {"id": rid, "title": title, "description": description, "source": source, "likelihood": likelihood, "impact": impact, "score": score,
           "rating": rating, "treatment": treatment, "owner": owner, "controls": controls, "status": status, "identified": identified, "next_review": next_review}
    rec.update(extra)
    return rec


RISKS = [
    risk("R-01", "A spoofed bank-detail change redirects a client payroll payment", "Risk workshop", 3, 4, "Reduce", "P-03", ["CTL-08", "CTL-14", "CTL-16"], "Treating", "2025-09-18", "2027-03-18",
         "Business email compromise is the top loss for payroll firms. Treatment: the callback procedure with two approvers (CTL-08), DMARC enforcement and phishing filtering."),
    risk("R-02", "A payroll specialist's mailbox is taken over before MFA is registered", "Scan: m365.mfa.coverage", 3, 4, "Reduce", "X-01", ["CTL-09", "CTL-10"], "Treating", "2026-10-30", "2026-11-30",
         "Five accounts have no second factor: three new hires inside their first week and two shared mailboxes that should be sign-in blocked."),
    risk("R-03", "Client payroll files reachable through anyone-with-the-link sharing", "Scan: m365.sharing.anonymous_links", 2, 3, "Reduce", "X-01", ["CTL-17"], "Treating", "2026-10-30", "2026-12-30",
         "Anyone links are allowed without expiry. Change scheduled for Nov 8: expire after 30 days, then restrict to existing guests."),
    risk("R-04", "Company mail forwarded automatically to a personal mailbox", "Scan: m365.forwarding.external", 3, 3, "Reduce", "X-01", ["CTL-15"], "Treating", "2026-10-30", "2026-11-30",
         "One inbox rule copies mail to a personal Gmail address and the tenant still allows outbound forwarding. Rule removed Oct 31; the tenant setting is due Nov 7."),
    risk("R-05", "The Brightfile portal breach exposes client documents", "Vendor review: Brightfile alert", 3, 4, "Reduce", "P-45", ["CTL-35", "CTL-34"], "Treating", "2026-10-24", "2026-11-15",
         "Brightfile reported unauthorized access to a support system. Awaiting its incident report; the breach notification procedure is on standby."),
    risk("R-06", "Client files shared through personal Dropbox accounts", "Vendor discovery: OAuth consent review", 3, 3, "Reduce", "P-02", ["CTL-20", "CTL-17"], "Open", "2026-10-28", "2026-11-28",
         "Six staff connected personal Dropbox accounts. Decision due: approve a business account with a DPA, or block and move the files to SharePoint."),
    risk("R-07", "Staff paste client personal data into unapproved AI tools", "AI inventory", 3, 3, "Reduce", "P-02", ["CTL-38", "CTL-39"], "Treating", "2026-10-10", "2027-01-10",
         "Eleven AI tools found in use. Treatment: the AI Acceptable Use Policy, the 15-minute course, approved tools with rules, blocked tools at sign-in."),
    risk("R-08", "An automation agent reads the payroll inbox beyond its purpose", "AI inventory: Zapier Agents", 2, 3, "Reduce", "P-05", ["CTL-38", "CTL-40"], "Open", "2026-10-28", "2026-11-28",
         "Zapier Agents can read the whole payroll@ mailbox. Treatment under review: a scoped mailbox, an action log and a DPA addendum before approval."),
    risk("R-09", "Ransomware on the file store with backups that cannot be restored", "Risk workshop", 2, 4, "Reduce", "X-01", ["CTL-23", "CTL-31"], "Treating", "2025-09-18", "2027-03-18",
         "EDR on 54 of 55 devices and immutable backups restore-tested in September reduce both likelihood and impact."),
    risk("R-10", "The incident response plan has not been exercised in 14 months", "Evidence review", 2, 3, "Reduce", "X-02", ["CTL-33"], "Treating", "2026-10-15", "2026-11-20",
         "Last tabletop August 2025. The 2026 exercise (a payroll-day outage plus a BEC attempt) is scheduled for Nov 20 with the IT provider and counsel."),
    risk("R-11", "Loss of the IT provider's account lead delays incident handling", "Risk workshop", 2, 2, "Accept", "P-02", ["CTL-02", "CTL-33"], "Accepted", "2025-09-18", "2027-03-18",
         "Bay State names a second engineer in the contract; accepted with that cover."),
    risk("R-12", "Paper payroll records in the Quincy office are not shredded on schedule", "Risk workshop", 2, 2, "Reduce", None, ["CTL-21", "CTL-37"], "Open", "2026-07-01", "2026-11-30",
         "The retention schedule is unapproved and the office manager role is open, so the shredding cadence has no owner."),
    risk("R-13", "The Massachusetts written information security program is not documented as 201 CMR 17.00 expects", "Compliance review", 2, 3, "Reduce", "P-04", ["CTL-01", "CTL-36"], "Treating", "2026-04-01", "2027-04-01",
         "Massachusetts requires a written program for businesses holding residents' personal information. The policy set covers it; counsel is assembling the single document that points to it."),
]

# --------------------------------------------------------------------------- questionnaires

INSURER_ANSWERS = {
    "mfa": ("Partial", ["CTL-09", "CTL-10"], ["m365.conditional_access.present", "m365.mfa.coverage", "m365.legacy_auth.blocked"], ["EV-11", "EV-10"], "High",
            "Conditional Access requires MFA for every user and blocks legacy sign-in. 53 of 58 accounts have a second factor registered; the five without are three new hires and two shared mailboxes being converted to sign-in blocked by Nov 15."),
    "admin_access": ("Yes", ["CTL-11", "CTL-12"], ["m365.admins.global_count", "m365.admins.mfa"], ["EV-10", "EV-12"], "High",
                     "Three Global Administrator accounts, none with a mailbox, all with hardware keys; quarterly access review signed Oct 2."),
    "email_security": ("Partial", ["CTL-14", "CTL-15", "CTL-16"], ["m365.email_auth.dmarc", "m365.forwarding.external"], ["EV-14", "EV-16", "EV-15"], "High",
                       "SPF, DKIM and DMARC (quarantine or reject) on both domains; Defender anti-phishing on every mailbox. External auto-forwarding is not yet blocked at the tenant; change due Nov 7."),
    "data_sharing": ("Partial", ["CTL-17", "CTL-20"], ["m365.sharing.anonymous_links", "m365.guests.review"], ["EV-17", "EV-20"], "Medium",
                     "Guest access is reviewed quarterly and third-party apps are approved. Anyone links are still allowed without expiry; change scheduled for Nov 8."),
    "logging": ("Yes", ["CTL-30"], ["m365.audit.enabled"], ["EV-30"], "High", "Unified audit log on with 180-day retention and alerts on admin role changes and new forwarding rules."),
    "edr": ("Yes", ["CTL-23"], ["att.edr.coverage"], ["EV-23"], "High", "Defender for Business on 54 of 55 devices (98 percent); the conference room PC is being enrolled."),
    "backups": ("Yes", ["CTL-31"], ["att.backups.tested"], ["EV-31"], "High", "Immutable SaaS backups of mail and SharePoint; restore tested Sep 26, 2026 in 41 minutes."),
    "incident_response": ("Partial", ["CTL-33", "CTL-34"], ["att.ir_plan.tested"], ["EV-33", "EV-34"], "High",
                          "Written plan v2.0 with roles, contacts and the carrier hotline. Last exercised August 2025; the 2026 tabletop is scheduled for Nov 20."),
    "training": ("Yes", ["CTL-05"], [], ["EV-05", "EV-06"], "High", "49 of 52 completed the yearly course; the other three started in the last two weeks. Phishing simulation each quarter."),
    "patching": ("Yes", ["CTL-24"], [], ["EV-24"], "Medium", "Critical updates within 14 days on 53 of 55 devices; two laptops pending."),
    "encryption": ("Yes", ["CTL-19"], [], ["EV-19"], "High", "All 55 managed devices encrypted; Microsoft 365 and Ledgerline encrypt data at rest and in transit."),
    "vendor_risk": ("Partial", ["CTL-35"], [], ["EV-36", "EV-37"], "Medium",
                    "21 vendors in the register with tiers and owners; critical vendors under contract with SOC 2 reports on file. TaxBridge's yearly review is overdue and the Brightfile incident is open."),
    "remote_access": ("Yes", ["CTL-28"], ["m365.conditional_access.present"], ["EV-28", "EV-11"], "High", "No VPN; access requires MFA and a compliant, company-managed device."),
}

BANK_QUESTIONS = [
    ("B-01", "Organization", "Do you have a written information security program approved by management and reviewed at least annually?", "Yes", ["CTL-01"], ["EV-01"], "High", "Information Security Policy v2.1, approved Mar 10, 2026; reviewed yearly."),
    ("B-02", "Organization", "Is there a named individual responsible for information security?", "Yes", ["CTL-02"], ["EV-02"], "High", "A fractional security lead (Alimi) reports to the CEO; the RACI names every role."),
    ("B-03", "Organization", "Do you perform a formal risk assessment at least annually?", "Partial", ["CTL-03"], ["EV-03"], "Medium", "Last workshop September 2025; the 2026 workshop is scheduled for Nov 18."),
    ("B-04", "People", "Are background checks performed on employees with access to customer data?", "Yes", ["CTL-06"], ["EV-07"], "High", "Every hire is screened before access, proportionate to the role."),
    ("B-05", "People", "Do all employees complete security awareness training at least annually?", "Yes", ["CTL-05"], ["EV-05"], "High", "49 of 52 complete; 3 new hires within their 30-day window."),
    ("B-06", "People", "Do employees acknowledge your acceptable use and confidentiality policies?", "Yes", ["CTL-04"], ["EV-04"], "High", "Acknowledgement tracked per policy; 49 of 52 on the latest versions."),
    ("B-07", "Access", "Is multi-factor authentication required for all access to systems holding customer data?", "Yes", ["CTL-09"], ["EV-11"], "High", "Conditional Access requires MFA for all users; legacy protocols are blocked."),
    ("B-08", "Access", "Are user access rights reviewed periodically?", "Yes", ["CTL-12"], ["EV-12"], "High", "Quarterly review signed by the COO; last on Oct 2, 2026."),
    ("B-09", "Access", "Is access removed promptly when employment ends?", "Yes", ["CTL-07"], ["EV-08"], "High", "Same-day removal, with ticket evidence for Q3 leavers."),
    ("B-10", "Access", "Are privileged accounts separate from day-to-day accounts?", "Yes", ["CTL-11"], ["EV-10"], "High", "Admin roles are held by dedicated accounts without mailboxes."),
    ("B-11", "Data", "Is customer data encrypted at rest and in transit?", "Yes", ["CTL-19"], ["EV-19"], "High", "Platform encryption in Microsoft 365 and Ledgerline; every laptop encrypted."),
    ("B-12", "Data", "Do you have a data classification and handling standard?", "Yes", ["CTL-18"], ["EV-18"], "High", "Four levels with handling rules."),
    ("B-13", "Data", "Do you have a documented data retention and destruction schedule?", "No", ["CTL-21"], [], "High", "The schedule is in POL-20 v1.1, awaiting approval; paper destruction is contracted."),
    ("B-14", "Systems", "Is endpoint protection deployed on all workstations and servers?", "Yes", ["CTL-23"], ["EV-23"], "High", "54 of 55 devices; the exception is being enrolled."),
    ("B-15", "Systems", "Are security patches applied within a defined timeframe?", "Yes", ["CTL-24"], ["EV-24"], "Medium", "Critical within 14 days; October report attached."),
    ("B-16", "Systems", "Do you perform vulnerability scanning and penetration testing?", "Partial", ["CTL-25"], ["EV-25"], "Medium", "Monthly scans; the last was August. No penetration test yet."),
    ("B-17", "Systems", "Are system changes authorized, tested and documented?", None, ["CTL-29"], ["EV-29"], None, None),
    ("B-18", "Systems", "Are audit logs collected and retained? For how long?", None, ["CTL-30"], ["EV-30"], None, None),
    ("B-19", "Email", "Do you enforce SPF, DKIM and DMARC on your sending domains?", None, ["CTL-14"], ["EV-14"], None, None),
    ("B-20", "Email", "Do you have controls against business email compromise and payment fraud?", None, ["CTL-08", "CTL-16"], ["EV-09"], None, None),
    ("B-21", "Resilience", "Do you have a business continuity plan with defined recovery objectives?", None, ["CTL-32"], ["EV-32"], None, None),
    ("B-22", "Resilience", "Are backups performed, protected from tampering and tested?", None, ["CTL-31"], ["EV-31"], None, None),
    ("B-23", "Incidents", "Do you have an incident response plan, and when was it last tested?", None, ["CTL-33"], ["EV-33", "EV-34"], None, None),
    ("B-24", "Incidents", "Will you notify us of a security incident affecting our data, and within what timeframe?", None, ["CTL-34"], ["EV-35"], None, None),
    ("B-25", "Vendors", "Do you assess the security of your own vendors and subprocessors?", None, ["CTL-35"], ["EV-36"], None, None),
    ("B-26", "Vendors", "Please list subprocessors that handle our employees' data.", None, ["CTL-35"], [], None, None),
    ("B-27", "Privacy", "Do you have a privacy notice and a process for data subject requests?", None, ["CTL-36"], ["EV-38"], None, None),
    ("B-28", "Privacy", "Do you comply with Massachusetts 201 CMR 17.00?", None, ["CTL-01", "CTL-36"], [], None, None),
    ("B-29", "Assurance", "Do you hold a SOC 2 report or ISO 27001 certificate? If not, what is your plan?", None, [], [], None, None),
    ("B-30", "Insurance", "Do you carry cyber liability insurance? Please state the limit.", None, [], [], None, None),
]

QUESTIONNAIRES = {
    "insurer": {
        "id": "Q-INSURER-2027",
        "name": "Cyber insurance renewal questionnaire",
        "from": "Granite Harbor Mutual via Harborline Insurance Brokers (fictional)",
        "due": "2026-12-15",
        "status": "In progress",
        "answered_by": "Controls and evidence",
        "answers": [
            {"question_id": qid, "answer": a, "controls": c, "tests": t, "evidence": e, "confidence": conf, "note": note}
            for qid, (a, c, t, e, conf, note) in INSURER_ANSWERS.items()
        ],
    },
    "bank": {
        "id": "Q-BANK-2026",
        "name": "Vendor security questionnaire",
        "from": "First Quincy Savings Bank (fictional), vendor management",
        "opened": "2026-10-06",
        "due": "2026-12-01",
        "status": "Draft",
        "answered_by": "Assistant (preview) from the controls and evidence; 16 of 30 drafted, 14 open",
        "questions": [
            {"id": qid, "section": sec, "text": text, "answer": a, "controls": c, "evidence": e, "confidence": conf, "note": note, "drafted_by": "assistant" if a else None}
            for qid, sec, text, a, c, e, conf, note in BANK_QUESTIONS
        ],
    },
}

# --------------------------------------------------------------------------- training

TRAINING = {
    "courses": [
        {"id": "TR-01", "name": "Security awareness", "minutes": 35, "frequency": "Yearly, plus a phishing simulation each quarter", "source": "Alimi",
         "assigned_to": "All staff", "description": "Phishing, passwords and MFA, handling client data, reporting an incident. Written for a payroll office, not an IT team."},
        {"id": "TR-02", "name": "Verify before you pay", "minutes": 20, "frequency": "Yearly, with a drill", "source": "Alimi payment fraud kit",
         "assigned_to": "Money movers", "description": "The callback procedure for bank-detail changes and wires, the scripts, and the closing-day checklist."},
        {"id": "TR-03", "name": "AI acceptable use", "minutes": 15, "frequency": "Yearly", "source": "Alimi AI policy kit",
         "assigned_to": "All staff", "description": "Which AI tools are approved, what may never be pasted into one, and how to ask for a new tool."},
    ]
}

# --------------------------------------------------------------------------- integrations

INTEGRATIONS = {
    "connected": [
        {"id": "m365", "name": "Microsoft 365", "status": "Connected", "mode": "Read-only", "connected_on": "2026-09-29", "connected_by": "X-01",
         "last_run": iso(SCAN_AT), "schedule": "Weekly, Friday 18:00", "runs": 5,
         "permissions": ["Organization.Read.All", "User.Read.All", "AuditLog.Read.All", "Policy.Read.All", "RoleManagement.Read.Directory", "MailboxSettings.Read", "SharePointTenantSettings.Read.All"],
         "reads": ["Users and MFA registration", "Conditional Access policies and Security Defaults", "Directory roles", "Inbox rules", "Sharing settings", "Audit settings", "Secure Score", "Sign-in logs (legacy authentication, guest activity)"],
         "never_reads": ["Mail content", "Files", "Passwords or tokens"], "proves": ["CTL-09", "CTL-10", "CTL-11", "CTL-12", "CTL-14", "CTL-15", "CTL-17", "CTL-20", "CTL-27", "CTL-30"]},
    ],
    "available": [
        {"id": "gws", "name": "Google Workspace", "status": "Available", "would_prove": ["CTL-09", "CTL-11", "CTL-14", "CTL-15", "CTL-17", "CTL-20", "CTL-30"], "note": "Same checks for Google tenants; read-only Admin SDK scopes."},
        {"id": "intune", "name": "Microsoft Intune", "status": "Available", "would_prove": ["CTL-19", "CTL-22", "CTL-23", "CTL-24", "CTL-26"], "note": "Device encryption, compliance, EDR and patch state straight from the device record, replacing the monthly exports."},
        {"id": "jamf", "name": "Jamf", "status": "Available", "would_prove": ["CTL-19", "CTL-22", "CTL-24"], "note": "The same for Macs managed outside Intune."},
        {"id": "hr", "name": "HR system (Gusto, BambooHR, Rippling)", "status": "Available", "would_prove": ["CTL-06", "CTL-07", "CTL-04"], "note": "The people list, start and end dates, so joiners and leavers never need a spreadsheet."},
        {"id": "quickbooks", "name": "QuickBooks Online", "status": "Available", "would_prove": ["CTL-35"], "note": "Vendor discovery from accounts payable."},
        {"id": "github", "name": "GitHub", "status": "Available", "would_prove": ["CTL-29", "CTL-25"], "note": "Branch protection, reviews and secret scanning as change-management evidence."},
        {"id": "aws", "name": "AWS", "status": "Available", "would_prove": ["CTL-19", "CTL-30", "CTL-31"], "note": "For the client portal's hosting account."},
    ],
    "later": [
        {"name": "AI agent activity monitoring", "note": "Endpoint and gateway hooks that watch what an agent does, as Vanta describes. The inventory and the rules come first."},
        {"name": "On-premises systems", "note": "A collector for file servers and domain controllers, when a customer has them."},
        {"name": "Auditor portal", "note": "A read-only login for the CPA firm, when a customer goes for SOC 2."},
    ],
}

# --------------------------------------------------------------------------- monitoring history

RUN_DATES = ["2026-10-02", "2026-10-09", "2026-10-16", "2026-10-23", "2026-10-30"]
HISTORY = {
    "m365.mfa.coverage": ["pass", "pass", "pass", "fail", "fail"],
    "m365.conditional_access.present": ["pass"] * 5,
    "m365.legacy_auth.blocked": ["fail", "pass", "pass", "pass", "pass"],
    "m365.security_defaults": ["fail", "pass", "pass", "pass", "pass"],
    "m365.admins.global_count": ["fail", "fail", "pass", "pass", "pass"],
    "m365.admins.mfa": ["pass"] * 5,
    "m365.forwarding.external": ["fail"] * 5,
    "m365.email_auth.dmarc": ["fail", "pass", "pass", "pass", "pass"],
    "m365.sharing.anonymous_links": ["fail"] * 5,
    "m365.guests.review": ["fail", "fail", "pass", "pass", "pass"],
    "m365.audit.enabled": ["pass"] * 5,
    "m365.secure_score": ["fail", "pass", "pass", "pass", "pass"],
    "att.edr.coverage": ["attestation_needed"] * 5,
    "att.backups.tested": ["attestation_needed"] * 5,
    "att.ir_plan.tested": ["attestation_needed"] * 5,
}
HISTORY_NOTES = {
    "2026-10-02": "First scan after the pilot letter: 7 of 12 automated checks failing.",
    "2026-10-09": "Legacy authentication blocked, DMARC moved to quarantine, Secure Score up to 61.",
    "2026-10-16": "Two daily-use Global Administrator accounts replaced by admin-only accounts; two stale guests removed.",
    "2026-10-23": "Three new hires started without MFA registration; coverage check turned red.",
    "2026-10-30": "No change; forwarding and sharing fixes scheduled for the first week of November.",
}
MONITORING = {"runs": [{"date": d, "note": HISTORY_NOTES[d]} for d in RUN_DATES],
              "history": {cid: [{"date": d, "status": s} for d, s in zip(RUN_DATES, statuses)] for cid, statuses in HISTORY.items()}}

# --------------------------------------------------------------------------- write

OUT.mkdir(parents=True, exist_ok=True)
write("company.json", COMPANY)
write("people.json", {"as_of": iso(AS_OF), "people": PEOPLE})
write("assignments.json", ASSIGNMENTS)
write("policies.json", {"policies": POLICIES})
write("evidence.json", {"evidence": E})
write("vendors.json", {"rubric": {
    "data_types": "What data the vendor holds: 1 public, 2 internal, 3 personal, 4 Social Security numbers, bank details or health data",
    "business_criticality": "What stops if the vendor is down: 1 nothing, 2 an inconvenience, 3 a team, 4 payroll runs",
    "integration_access": "What the vendor can reach: 1 nothing, 2 one app, 3 several systems, 4 administrative access",
    "communication_scope": "Who the vendor talks to: 1 one person, 2 a team, 3 the company, 4 clients on our behalf",
    "tiers": {"Critical": "13 to 16", "High": "10 to 12", "Medium": "7 to 9", "Low": "4 to 6"},
    "review_rule": "Critical and High vendors are reviewed yearly with a SOC 2 or ISO 27001 report or a questionnaire; Medium every two years; Low need a contract only."},
    "vendors": V})
write("ai-tools.json", AI)
write("risks.json", {"scale": {"likelihood": "1 rare to 4 likely within a year", "impact": "1 minor to 4 severe (payroll stops, client data exposed, regulator involved)",
                              "rating": "Likelihood x impact: Critical 12 or more, High 8 to 11, Medium 4 to 7, Low under 4"}, "risks": RISKS})
write("questionnaires.json", QUESTIONNAIRES)
write("assets.json", {"devices": DEVICES, "data_stores": [
    {"id": "DS-01", "name": "SharePoint: Client files", "owner": "P-05", "classification": "Restricted", "contains": ["Client payroll files", "Employee personal data"]},
    {"id": "DS-02", "name": "SharePoint: People (HR)", "owner": "P-42", "classification": "Restricted", "contains": ["Employee records", "Background check results"]},
    {"id": "DS-03", "name": "SharePoint: Finance", "owner": "P-03", "classification": "Confidential", "contains": ["Company financials", "Vendor bank details"]},
    {"id": "DS-04", "name": "Ledgerline Payroll Engine (vendor)", "owner": "P-05", "classification": "Restricted", "contains": ["Pay data", "Social Security numbers", "Bank details"]},
    {"id": "DS-05", "name": "Brightfile Client Portal (vendor)", "owner": "P-45", "classification": "Restricted", "contains": ["Client document exchange"]},
], "domains": SNAPSHOT["email_auth"], "tenant": {"name": SNAPSHOT["tenant_display_name"], "domains": SNAPSHOT["verified_domains"], "licence": "Microsoft 365 Business Premium", "users": len(users)}})
write("training.json", TRAINING)
write("integrations.json", INTEGRATIONS)
write("snapshot.json", SNAPSHOT)
write("monitoring-history.json", MONITORING)
print(f"{len(PEOPLE)} people ({sum(1 for p in PEOPLE if p['counted'])} counted), {len(users)} tenant accounts, {len(E)} evidence items, {len(V)} vendors, {len(AI['tools'])} AI tools, {len(RISKS)} risks, {len(DEVICES)} devices")
