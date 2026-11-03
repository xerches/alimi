"""The trust center: a company's public page and the admin side behind it.

Every function takes a connection already inside org_scope. The public route gets its
organization from trust_directory (the only table readable with no context) and then reads only
what is marked public, or on request when the visitor carries a valid access key. The key is
random, shown once at approval, and only its hash is stored.
"""

from __future__ import annotations

import hashlib
import re
import secrets
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Connection, text

from .markdown import to_html
from .tasks import create_task

VISIBILITIES: dict[str, str] = {"public": "Public", "on_request": "On request", "private": "Private"}
DOCUMENT_KINDS: dict[str, str] = {"link": "Link to a file", "policy": "One of our approved policies"}
REQUEST_STATUSES: dict[str, str] = {"pending": "Waiting", "approved": "Approved", "denied": "Denied"}
# Paths under /trust that belong to the admin side, so no company can take them as its public slug.
RESERVED_SLUGS: frozenset[str] = frozenset({"settings", "documents", "folders", "questions", "subprocessors", "updates", "requests", "subscribe", "request", "new"})
SLUG = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,60}[a-z0-9])?$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CAN_MANAGE = ("owner", "admin")
VIEWS_WINDOW_DAYS = 30


def key_hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def new_key() -> str:
    return secrets.token_urlsafe(24)


def domain_of(email: str) -> str:
    return email.rsplit("@", 1)[-1].lower()


def lines(text_: str | None) -> list[str]:
    """A textarea of one entry per line, cleaned: lowercase, trimmed, no blanks, no duplicates."""
    out: list[str] = []
    for raw in (text_ or "").replace(",", "\n").splitlines():
        item = raw.strip().lower().lstrip("@")
        if item and item not in out:
            out.append(item)
    return out


# ------------------------------------------------------------------ the page and its parts

def directory_entry(conn: Connection) -> dict | None:
    """This organization's row in the public directory (readable from any context, written only by its owner)."""
    return conn.execute(text("SELECT slug, enabled FROM trust_directory WHERE organization_id = app_org()")).mappings().first()


def resolve_slug(conn: Connection, slug: str) -> UUID | None:
    """From a public slug to the organization, with no context set: the one lookup a visitor needs."""
    row = conn.execute(text("SELECT organization_id FROM trust_directory WHERE slug = :slug AND enabled"), {"slug": slug}).first()
    return row[0] if row else None


def page_of(conn: Connection) -> dict:
    """The settings row, created with the defaults the first time it is asked for."""
    query = text("SELECT * FROM trust_pages WHERE organization_id = app_org()")
    row = conn.execute(query).mappings().first()
    if row is None:
        conn.execute(text("INSERT INTO trust_pages (organization_id) VALUES (app_org())"))
        row = conn.execute(query).mappings().first()
    return dict(row)


def folders_of(conn: Connection) -> list[dict]:
    return conn.execute(text("SELECT * FROM trust_folders ORDER BY position, name")).mappings().all()


def documents_of(conn: Connection, *, visible_to: tuple[str, ...] | None = None) -> list[dict]:
    """Documents with their folder and, for a policy document, the policy's title, version and approval date.

    visible_to limits the visibilities returned: the public page asks for ('public',) or
    ('public', 'on_request'); the admin side asks for everything.
    """
    where = "WHERE d.visibility = ANY(:vis)" if visible_to else ""
    rows = conn.execute(
        text(
            "SELECT d.*, f.name AS folder_name, f.position AS folder_position, p.slug AS policy_slug, p.title AS policy_title, "
            "p.current_version AS policy_version, p.status AS policy_status, p.approved_at AS policy_approved_at "
            f"FROM trust_documents d LEFT JOIN trust_folders f ON f.id = d.folder_id LEFT JOIN policies p ON p.id = d.policy_id {where} "
            "ORDER BY coalesce(f.position, 1000), f.name NULLS LAST, d.position, d.title"
        ),
        {"vis": list(visible_to)} if visible_to else {},
    ).mappings().all()
    return [dict(r) for r in rows]


def grouped(documents: list[dict]) -> list[dict]:
    """Documents under their folder, in folder order; documents without a folder come last."""
    groups: list[dict] = []
    for d in documents:
        key = d["folder_id"]
        if not groups or groups[-1]["id"] != key:
            groups.append({"id": key, "name": d["folder_name"] or "Other documents", "items": []})
        groups[-1]["items"].append(d)
    return groups


def questions_of(conn: Connection, *, published_only: bool = False) -> list[dict]:
    where = "WHERE published" if published_only else ""
    rows = conn.execute(text(f"SELECT * FROM trust_questions {where} ORDER BY position, category NULLS LAST, question")).mappings().all()
    return [{**r, "answer_html": to_html(r["answer"])} for r in rows]


def subprocessors_of(conn: Connection) -> list[dict]:
    return conn.execute(text("SELECT * FROM trust_subprocessors ORDER BY position, name")).mappings().all()


def updates_of(conn: Connection, limit: int = 50) -> list[dict]:
    rows = conn.execute(text("SELECT * FROM trust_updates ORDER BY published_on DESC, created_at DESC LIMIT :n"), {"n": limit}).mappings().all()
    return [{**r, "body_html": to_html(r["body"])} for r in rows]


def subscriber_count(conn: Connection) -> int:
    return int(conn.execute(text("SELECT count(*) FROM trust_subscribers")).scalar())


def subscribe(conn: Connection, org_id: UUID | str, email: str) -> bool:
    if conn.execute(text("SELECT 1 FROM trust_subscribers WHERE email = :e"), {"e": email}).first():
        return False
    conn.execute(text("INSERT INTO trust_subscribers (organization_id, email) VALUES (:org, :e)"), {"org": str(org_id), "e": email})
    return True


def count_view(conn: Connection, org_id: UUID | str, today: date | None = None) -> None:
    today = today or date.today()
    updated = conn.execute(text("UPDATE trust_views SET views = views + 1 WHERE day = :d"), {"d": today}).rowcount
    if not updated:
        conn.execute(text("INSERT INTO trust_views (organization_id, day, views) VALUES (:org, :d, 1)"), {"org": str(org_id), "d": today})


def views_recent(conn: Connection, today: date | None = None, days: int = VIEWS_WINDOW_DAYS) -> dict:
    today = today or date.today()
    since = today - timedelta(days=days - 1)
    rows = conn.execute(text("SELECT day, views FROM trust_views WHERE day >= :since ORDER BY day"), {"since": since}).mappings().all()
    return {"total": sum(r["views"] for r in rows), "days": days, "by_day": rows, "peak": max((r["views"] for r in rows), default=0)}


# ------------------------------------------------------------------ access requests

def requests_of(conn: Connection, status: str | None = None) -> list[dict]:
    where = "WHERE r.status = :s" if status else ""
    return conn.execute(
        text(
            "SELECT r.*, u.display_name AS decided_by_name FROM trust_access_requests r LEFT JOIN users u ON u.id = r.decided_by "
            f"{where} ORDER BY (r.status = 'pending') DESC, r.created_at DESC"
        ),
        {"s": status} if status else {},
    ).mappings().all()


def get_request(conn: Connection, request_id: UUID | str) -> dict | None:
    return conn.execute(text("SELECT * FROM trust_access_requests WHERE id = :id"), {"id": str(request_id)}).mappings().first()


def access_for_key(conn: Connection, key: str | None, today: date | None = None) -> dict | None:
    """The approved, unexpired request a visitor's key belongs to, or None."""
    if not key:
        return None
    today = today or date.today()
    row = conn.execute(
        text("SELECT id, name, company, email, expires_on FROM trust_access_requests WHERE status = 'approved' AND token_hash = :h AND expires_on >= :today"),
        {"h": key_hash(key), "today": today},
    ).mappings().first()
    return dict(row) if row else None


def submit_request(conn: Connection, org_id: UUID | str, page: dict, *, name: str, email: str, company: str | None, reason: str | None, nda_accepted: bool, today: date | None = None, owner_id: UUID | str | None = None) -> tuple[dict, str | None]:
    """Record a visitor's request. Returns the row and, when the domain is auto-approved, the key to show once.

    A blocked domain raises PermissionError; the route turns that into a refusal page. Every other
    request becomes a Decide task for the company, so it shows on Home and in the overdue count.
    """
    today = today or date.today()
    domain = domain_of(email)
    if domain in (page.get("blocked_domains") or []):
        raise PermissionError("Requests from this email domain are not accepted.")
    auto = domain in (page.get("auto_approve_domains") or [])
    key = new_key() if auto else None
    row = conn.execute(
        text(
            "INSERT INTO trust_access_requests (organization_id, name, email, company, reason, nda_accepted, status, token_hash, expires_on, decided_at) "
            "VALUES (:org, :name, :email, :company, :reason, :nda, :status, :hash, :expires, :decided) RETURNING *"
        ),
        {
            "org": str(org_id), "name": name, "email": email, "company": company, "reason": reason, "nda": nda_accepted,
            "status": "approved" if auto else "pending", "hash": key_hash(key) if key else None,
            "expires": today + timedelta(days=int(page.get("access_days") or 365)) if auto else None,
            "decided": datetime.now(timezone.utc) if auto else None,
        },
    ).mappings().first()
    if not auto:
        create_task(
            conn, org_id, None, title=f"Trust center: access request from {name}" + (f" ({company})" if company else ""),
            kind="decide", source_kind="trust_request", source_id=str(row["id"]), priority="normal", assignee_user_id=owner_id,
            due_on=today + timedelta(days=2),
            detail=(f"{name} <{email}> asks for the on-request documents" + (f": {reason}" if reason else ".") + " Approve or deny it under Trust, Access requests."),
        )
    return dict(row), key


def decide_request(conn: Connection, req: dict, *, approve: bool, by: UUID | str, page: dict, today: date | None = None) -> str | None:
    """Approve (returns the key to show once) or deny a pending request; the request's task closes either way."""
    today = today or date.today()
    key = new_key() if approve else None
    conn.execute(
        text(
            "UPDATE trust_access_requests SET status = :status, token_hash = :hash, expires_on = :expires, decided_by = :by, decided_at = now() WHERE id = :id"
        ),
        {
            "status": "approved" if approve else "denied", "hash": key_hash(key) if key else None,
            "expires": today + timedelta(days=int(page.get("access_days") or 365)) if approve else None, "by": str(by), "id": str(req["id"]),
        },
    )
    conn.execute(
        text("UPDATE tasks SET status = 'done', done_at = now(), updated_at = now() WHERE source_kind = 'trust_request' AND source_id = :id AND status <> 'done'"),
        {"id": str(req["id"])},
    )
    return key


def counts(conn: Connection) -> dict[str, int]:
    docs = conn.execute(
        text(
            "SELECT count(*) FILTER (WHERE visibility = 'public') AS public, count(*) FILTER (WHERE visibility = 'on_request') AS on_request, "
            "count(*) FILTER (WHERE visibility = 'private') AS private FROM trust_documents"
        )
    ).mappings().one()
    return {
        **dict(docs),
        "folders": int(conn.execute(text("SELECT count(*) FROM trust_folders")).scalar()),
        "questions": int(conn.execute(text("SELECT count(*) FROM trust_questions WHERE published")).scalar()),
        "subprocessors": int(conn.execute(text("SELECT count(*) FROM trust_subprocessors")).scalar()),
        "updates": int(conn.execute(text("SELECT count(*) FROM trust_updates")).scalar()),
        "subscribers": subscriber_count(conn),
        "pending": int(conn.execute(text("SELECT count(*) FROM trust_access_requests WHERE status = 'pending'")).scalar()),
        "approved": int(conn.execute(text("SELECT count(*) FROM trust_access_requests WHERE status = 'approved'")).scalar()),
    }


# ------------------------------------------------------------------ sample data

def seed_trust(conn: Connection, org_id: UUID, slug: str, company: str, users: list, today: date | None = None) -> None:
    """A trust page per sample company, part way through: documents in two folders, questions,
    subprocessors, updates, two subscribers, a pending request (with its task) and an approved one."""
    today = today or date.today()
    if conn.execute(text("SELECT 1 FROM trust_pages LIMIT 1")).first():
        return
    first, last = users[0], users[-1]
    org = str(org_id)
    conn.execute(text("INSERT INTO trust_directory (slug, organization_id, enabled) VALUES (:slug, :org, true)"), {"slug": slug, "org": org})
    page = {
        "saltmarsh": (
            "How we protect the payroll data of the employers we serve",
            f"{company} runs a documented security program on the Alimi platform: written policies staff accept every year, controls tested against our Microsoft 365 environment on every scan, encrypted laptops, verified payment changes, and a named security lead who answers your questions.\n\nWe work toward the cyber insurance questionnaire first and SOC 2 after it. Documents marked *on request* are shared after a short non-disclosure agreement and the owner's approval, usually within one business day.",
            ["saltmarsh.example"], ["mailinator.com"],
        ),
        "harbor-dental": (
            "How we keep patient records private",
            f"{company} protects patient information under HIPAA with Google Workspace controls that Alimi checks on every scan, staff training every year, and written policies.\n\nOur business associate agreement and the policies that back it are available on request.",
            ["harbordental.example"], [],
        ),
        "alimi": (
            "Security at Alimi, the way we ask it of our customers",
            "Alimi runs on the Alimi platform: the same controls, policies and checks we monitor for customers, monitored for ourselves. Every policy here is approved and acknowledged by the team, and the trust page you are reading is the one each customer gets.",
            ["alimi.example"], [],
        ),
    }.get(slug, ("Security at " + company, f"{company} runs its security program on the Alimi platform.", [], []))
    conn.execute(
        text(
            "INSERT INTO trust_pages (organization_id, headline, statement, contact_name, contact_email, nda_text, auto_approve_domains, blocked_domains) "
            "VALUES (:org, :headline, :statement, :cname, :cemail, :nda, :auto, :blocked)"
        ),
        {
            "org": org, "headline": page[0], "statement": page[1], "cname": last.display_name, "cemail": last.email,
            "nda": f"By requesting access you agree to use the documents only to assess {company} as a supplier or partner, to share them only with the people who need them for that purpose, and to delete them when the assessment ends.",
            "auto": page[2], "blocked": page[3],
        },
    )
    folders = {}
    for i, name in enumerate(("Policies", "Reports and certificates")):
        folders[name] = conn.execute(
            text("INSERT INTO trust_folders (organization_id, name, position) VALUES (:org, :name, :pos) RETURNING id"), {"org": org, "name": name, "pos": i}
        ).scalar()
    approved = conn.execute(text("SELECT id, title FROM policies WHERE status = 'approved' ORDER BY template_id")).mappings().all()
    for i, p in enumerate(approved[:8]):
        conn.execute(
            text("INSERT INTO trust_documents (organization_id, folder_id, title, kind, policy_id, visibility, position) VALUES (:org, :folder, :title, 'policy', :policy, 'on_request', :pos)"),
            {"org": org, "folder": str(folders["Policies"]), "title": p["title"], "policy": str(p["id"]), "pos": i},
        )
    reports = [
        ("Cyber insurance certificate", "Our current certificate of insurance; the policy itself is shared on request.", "public", "https://example.com/" + slug + "/certificate-of-insurance.pdf"),
        ("Latest insurer-ready report", "The Alimi report from the latest scan: every control, its status and the evidence behind it.", "on_request", "https://example.com/" + slug + "/insurer-report.pdf"),
        ("Penetration test summary", "Shared with customers under contract only.", "private", "https://example.com/" + slug + "/pentest-summary.pdf"),
    ]
    for i, (title, desc, vis, url) in enumerate(reports):
        conn.execute(
            text("INSERT INTO trust_documents (organization_id, folder_id, title, description, kind, url, visibility, position) VALUES (:org, :folder, :title, :desc, 'link', :url, :vis, :pos)"),
            {"org": org, "folder": str(folders["Reports and certificates"]), "title": title, "desc": desc, "url": url, "vis": vis, "pos": i},
        )
    questions = [
        ("Access", "Do you require multi-factor authentication?", "Yes. Every account on our Microsoft 365 or Google Workspace tenant needs a second factor to sign in, and Alimi checks the coverage on every scan. Multi-factor authentication (MFA) means a password alone is never enough."),
        ("Access", "Who can see our data?", "Only the people whose job needs it. Access follows the role, is approved by a manager, and is removed the day someone leaves."),
        ("Data", "Is our data encrypted?", "Yes, in transit (TLS) and at rest, on laptops (full-disk encryption) and in the cloud services we use."),
        ("Resilience", "How do you back up data, and have you tested a restore?", "Cloud data is backed up daily and a restore is tested every quarter; the last test is recorded as evidence in Alimi."),
        ("Incidents", "What happens if there is a security incident?", "We follow a written incident response plan with named contacts. Affected customers are told within the deadlines in our contracts and the law."),
        ("Vendors", "Which third parties handle our data?", "The subprocessors listed on this page, each under contract and reviewed every year."),
    ]
    for i, (cat, q, a) in enumerate(questions[: 6 if slug == "saltmarsh" else 3]):
        conn.execute(
            text("INSERT INTO trust_questions (organization_id, category, question, answer, position) VALUES (:org, :cat, :q, :a, :pos)"),
            {"org": org, "cat": cat, "q": q, "a": a, "pos": i},
        )
    subs = {
        "saltmarsh": [("Microsoft 365", "Email, files and identity", "United States"), ("Alimi", "Compliance monitoring, read-only", "United States"), ("Harborline IT (fictional)", "Managed IT and device management", "United States")],
        "harbor-dental": [("Google Workspace", "Email, files and identity", "United States"), ("Alimi", "Compliance monitoring, read-only", "United States")],
        "alimi": [("Microsoft 365", "Email, files and identity", "United States"), ("Netlify", "Hosting of the marketing site", "United States")],
    }.get(slug, [("Alimi", "Compliance monitoring, read-only", "United States")])
    for i, (name, purpose, loc) in enumerate(subs):
        conn.execute(
            text("INSERT INTO trust_subprocessors (organization_id, name, purpose, location, position) VALUES (:org, :name, :purpose, :loc, :pos)"),
            {"org": org, "name": name, "purpose": purpose, "loc": loc, "pos": i},
        )
    updates = [
        ("Trust page published", "This page now answers the questions we are asked most, and documents are shared on request.", today - timedelta(days=45)),
        ("Policy set approved", "The core security policies were approved and acknowledged by the whole team.", today - timedelta(days=57)),
        ("Continuous monitoring switched on", "Alimi now checks our tenant on every scan with read-only access; nothing is changed by the checks.", today - timedelta(days=62)),
    ]
    for title, body, on in updates[: 3 if slug == "saltmarsh" else 1]:
        conn.execute(
            text("INSERT INTO trust_updates (organization_id, title, body, published_on, created_by) VALUES (:org, :title, :body, :on, :by)"),
            {"org": org, "title": title, "body": body, "on": on, "by": str(first.id)},
        )
    for email in ("security@coastalbank.example", "vendors@brightwave.example")[: 2 if slug == "saltmarsh" else 1]:
        conn.execute(text("INSERT INTO trust_subscribers (organization_id, email) VALUES (:org, :e)"), {"org": org, "e": email})
    page_row = page_of(conn)
    submit_request(
        conn, org_id, page_row, name="Noor Haddad", email="noor.haddad@coastalbank.example", company="Coastal Bank (fictional)",
        reason="Vendor due diligence before the account opens.", nda_accepted=True, today=today, owner_id=first.id,
    )
    decided, _key = submit_request(
        conn, org_id, page_row, name="Avery Lind", email="avery.lind@brightwave.example", company="Brightwave Insurance Brokers (fictional)",
        reason="Renewal file.", nda_accepted=True, today=today - timedelta(days=12), owner_id=first.id,
    )
    decide_request(conn, decided, approve=True, by=first.id, page=page_row, today=today - timedelta(days=11))
    for i in range(VIEWS_WINDOW_DAYS):
        day = today - timedelta(days=i)
        conn.execute(text("INSERT INTO trust_views (organization_id, day, views) VALUES (:org, :d, :n)"), {"org": org, "d": day, "n": 1 + (i * 7 + hash(slug) % 3) % 5})
