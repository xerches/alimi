"""The policy module: a company's copies of the Alimi library, their versions, approvals and
acknowledgements, and the Markdown rendering of the text for signed-in readers.

Every function takes a connection already inside org_scope, so "the policies" always means this
organization's. Nothing here filters by organization in Python; the row policies do. The text is
rendered with raw HTML switched off, so a company's own edits cannot put script on the page.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text

from .markdown import MD

STATUSES: dict[str, str] = {"draft": "Draft", "in_review": "Awaiting approval", "approved": "Approved", "retired": "Retired"}
VIEWS: dict[str, str] = {"all": "All policies", "approved": "Approved", "in_review": "Awaiting approval", "draft": "Drafts", "mine": "Needs my acknowledgement"}
# Review cycle -> (label, days until the next review once approved).
CYCLES: dict[str, tuple[str, int]] = {"annual": ("Yearly", 365), "semiannual": ("Every six months", 182), "quarterly": ("Every quarter", 91)}
# The placeholders the library uses, in the order the Settings page will list them.
ROLES: tuple[str, ...] = ("CEO", "Security Lead", "IT Lead", "HR Lead", "Privacy Lead", "Finance Lead", "AI Lead")
REVIEW_MARKER = "[HR or legal review]"
PLACEHOLDER = re.compile(r"\{\{([^}]+)\}\}")
RENEWS_SOON_DAYS = 30
BODY_LIMIT = 200_000

# Roles that may do what. An auditor reads; a member acknowledges; the policy's owner and the
# company's owner or admin edit and submit; only the company's owner or admin approves.
CAN_ACKNOWLEDGE = ("owner", "admin", "member")
CAN_APPROVE = ("owner", "admin")


def fill(text_: str, values: dict[str, str]) -> str:
    """Replace {{Name}} with the company's value; a placeholder with no value stays as written."""
    return PLACEHOLDER.sub(lambda m: values.get(m.group(1).strip(), m.group(0)), text_)


def placeholders_left(text_: str) -> list[str]:
    return sorted({m.strip() for m in PLACEHOLDER.findall(text_)})


def markers_left(text_: str) -> int:
    return text_.count(REVIEW_MARKER)


def _anchor(title: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
    anchor, n = base, 2
    while anchor in used:
        anchor, n = f"{base}-{n}", n + 1
    used.add(anchor)
    return anchor


def render(body: str) -> tuple[str, list[dict[str, str]]]:
    """The document as HTML plus its outline (the "## 1. Purpose" headings, with anchors).

    Headings move down one level because the page already has an h1 (the policy's title), so the
    document's own title becomes an h2 and its sections h3.
    """
    tokens = MD.parse(body)
    outline: list[dict[str, str]] = []
    used: set[str] = set()
    for i, tok in enumerate(tokens):
        if tok.type != "heading_open":
            continue
        level = int(tok.tag[1])
        title = tokens[i + 1].content
        anchor = _anchor(title, used)
        tok.attrSet("id", anchor)
        tok.tag = tokens[i + 2].tag = f"h{min(level + 1, 6)}"
        if level == 2:
            outline.append({"id": anchor, "text": title})
    return MD.renderer.render(tokens, MD.options, {}), outline


# ------------------------------------------------------------------ queries

SELECT_POLICY = (
    "SELECT p.*, t.position, t.version AS template_version, t.related, "
    "o.display_name AS owner_name, a.display_name AS approver_name, "
    "(SELECT count(*) FROM policy_acknowledgements k WHERE k.policy_id = p.id AND k.version_number = p.current_version) AS acknowledged, "
    "EXISTS (SELECT 1 FROM policy_acknowledgements k WHERE k.policy_id = p.id AND k.version_number = p.current_version AND k.user_id = :me) AS acknowledged_by_me, "
    "(SELECT count(*) FROM policy_requirements r WHERE r.policy_id = p.template_id) AS requirement_count, "
    "(SELECT count(*) FROM control_policies c WHERE c.policy_id = p.template_id) AS control_count "
    "FROM policies p LEFT JOIN policy_templates t ON t.id = p.template_id "
    "LEFT JOIN users o ON o.id = p.owner_user_id LEFT JOIN users a ON a.id = p.approver_user_id "
)
ORDER = " ORDER BY coalesce(t.position, 1000), p.title"


def audience(conn: Connection) -> list[dict]:
    """Who has to acknowledge: every member except an auditor, who only reads."""
    return conn.execute(
        text(
            "SELECT u.id, u.display_name, u.job_title, m.role FROM memberships m JOIN users u ON u.id = m.user_id "
            "WHERE m.role <> 'auditor' ORDER BY u.display_name"
        )
    ).mappings().all()


def decorate(row: dict, today: date, audience_size: int) -> dict:
    item = dict(row)
    item["audience"] = audience_size
    item["percent"] = round(100 * item["acknowledged"] / audience_size) if audience_size and item["status"] == "approved" else 0
    due = item["next_review_on"]
    item["past_due"] = bool(due and item["status"] == "approved" and due < today)
    item["renews_soon"] = bool(due and item["status"] == "approved" and today <= due <= today + timedelta(days=RENEWS_SOON_DAYS))
    item["cycle_label"] = CYCLES.get(item["review_cycle"], (item["review_cycle"].capitalize(), 365))[0]
    item["label"] = item["template_id"] or "Own"
    return item


def list_policies(conn: Connection, *, view: str = "all", user_id: UUID | str | None = None, today: date | None = None) -> list[dict]:
    today = today or date.today()
    rows = conn.execute(text(SELECT_POLICY + ORDER), {"me": str(user_id) if user_id else None}).mappings().all()
    size = len(audience(conn))
    items = [decorate(r, today, size) for r in rows]
    if view == "mine":
        return [p for p in items if p["status"] == "approved" and not p["acknowledged_by_me"]]
    if view in STATUSES:
        return [p for p in items if p["status"] == view]
    return items


def get_policy(conn: Connection, slug: str, user_id: UUID | str | None = None, today: date | None = None) -> dict | None:
    row = conn.execute(text(SELECT_POLICY + "WHERE p.slug = :slug"), {"slug": slug, "me": str(user_id) if user_id else None}).mappings().first()
    return decorate(row, today or date.today(), len(audience(conn))) if row else None


def version_of(conn: Connection, policy_id: UUID | str, number: int) -> dict | None:
    return conn.execute(
        text("SELECT * FROM policy_versions WHERE policy_id = :id AND number = :n"), {"id": str(policy_id), "n": number}
    ).mappings().first()


def versions_of(conn: Connection, policy_id: UUID | str) -> list[dict]:
    return conn.execute(
        text(
            "SELECT v.number, v.change_note, v.created_at, v.approved_at, au.display_name AS author, ap.display_name AS approver, "
            "(SELECT count(*) FROM policy_acknowledgements k WHERE k.policy_id = v.policy_id AND k.version_number = v.number) AS acknowledged "
            "FROM policy_versions v LEFT JOIN users au ON au.id = v.author_user_id LEFT JOIN users ap ON ap.id = v.approved_by "
            "WHERE v.policy_id = :id ORDER BY v.number DESC"
        ),
        {"id": str(policy_id)},
    ).mappings().all()


def acknowledgements_of(conn: Connection, policy: dict) -> list[dict]:
    """Every person in the audience, with when they acknowledged the current version, or None."""
    acked = {
        r["user_id"]: r["acknowledged_at"]
        for r in conn.execute(
            text("SELECT user_id, acknowledged_at FROM policy_acknowledgements WHERE policy_id = :id AND version_number = :n"),
            {"id": str(policy["id"]), "n": policy["current_version"]},
        ).mappings()
    }
    return [{**person, "acknowledged_at": acked.get(person["id"])} for person in audience(conn)]


def requirements_of(conn: Connection, template_id: str | None) -> list[dict]:
    """Requirement IDs by framework, each with our own one-line summary and never the framework's text."""
    if not template_id:
        return []
    rows = conn.execute(
        text(
            "SELECT f.id AS framework_id, f.short_name, r.code, r.summary FROM policy_requirements pr "
            "JOIN requirements r ON r.id = pr.requirement_id JOIN frameworks f ON f.id = r.framework_id "
            "WHERE pr.policy_id = :id ORDER BY f.position, r.position, r.code"
        ),
        {"id": template_id},
    ).mappings().all()
    groups: list[dict] = []
    for r in rows:
        if not groups or groups[-1]["framework_id"] != r["framework_id"]:
            groups.append({"framework_id": r["framework_id"], "short_name": r["short_name"], "items": []})
        groups[-1]["items"].append(r)
    return groups


def control_ids_of(conn: Connection, template_id: str | None) -> list[str]:
    if not template_id:
        return []
    return conn.execute(text("SELECT control_id FROM control_policies WHERE policy_id = :id ORDER BY control_id"), {"id": template_id}).scalars().all()


def counts(conn: Connection, user_id: UUID | str | None = None, today: date | None = None) -> dict[str, int]:
    items = list_policies(conn, user_id=user_id, today=today)
    return {
        "total": len(items),
        "approved": sum(1 for p in items if p["status"] == "approved"),
        "in_review": sum(1 for p in items if p["status"] == "in_review"),
        "draft": sum(1 for p in items if p["status"] == "draft"),
        "mine": sum(1 for p in items if p["status"] == "approved" and not p["acknowledged_by_me"]),
        "past_due": sum(1 for p in items if p["past_due"]),
        "renews_soon": sum(1 for p in items if p["renews_soon"]),
    }


# ------------------------------------------------------------------ changes

def adopt(conn: Connection, org_id: UUID | str, template: dict, values: dict[str, str], role_users: dict[str, UUID | str | None], author: UUID | str | None, created_at: datetime | None = None) -> UUID:
    """Copy one library policy into the company: a policy row and its version 1 with the placeholders filled."""
    owner = role_users.get(_role(template.get("owner_role")))
    approver = role_users.get(_role(template.get("approver_role")))
    policy_id = conn.execute(
        text(
            "INSERT INTO policies (organization_id, template_id, slug, title, status, owner_user_id, approver_user_id, review_cycle, applies_to, created_at, updated_at) "
            "VALUES (:org, :template, :slug, :title, 'draft', :owner, :approver, :cycle, :applies, coalesce(:at, now()), coalesce(:at, now())) RETURNING id"
        ),
        {
            "org": str(org_id), "template": template["id"], "slug": template["slug"], "title": template["title"],
            "owner": str(owner) if owner else None, "approver": str(approver) if approver else None,
            "cycle": template.get("review_cycle") or "annual", "applies": fill(template.get("applies_to") or "", values) or None, "at": created_at,
        },
    ).scalar()
    conn.execute(
        text(
            "INSERT INTO policy_versions (organization_id, policy_id, number, body, change_note, author_user_id, created_at) "
            "VALUES (:org, :policy, 1, :body, :note, :by, coalesce(:at, now()))"
        ),
        {"org": str(org_id), "policy": str(policy_id), "body": fill(template["body"], values), "note": f"Adopted from the Alimi library, template {template['id']} v{template.get('version', '1.0')}.", "by": str(author) if author else None, "at": created_at},
    )
    return policy_id


def _role(placeholder: str | None) -> str:
    return (placeholder or "").strip("{} ")


def adopt_library(conn: Connection, org_id: UUID | str, values: dict[str, str], role_users: dict[str, UUID | str | None], author: UUID | str | None, created_at: datetime | None = None) -> list[UUID]:
    """Every library policy the company does not have yet, in library order."""
    have = set(conn.execute(text("SELECT template_id FROM policies WHERE template_id IS NOT NULL")).scalars())
    templates = conn.execute(text("SELECT * FROM policy_templates ORDER BY position")).mappings().all()
    return [adopt(conn, org_id, dict(t), values, role_users, author, created_at) for t in templates if t["id"] not in have]


def submit(conn: Connection, policy: dict) -> None:
    conn.execute(text("UPDATE policies SET status = 'in_review', updated_at = now() WHERE id = :id"), {"id": str(policy["id"])})


def approve(conn: Connection, policy: dict, by: UUID | str, when: datetime | None = None, today: date | None = None) -> None:
    """Approve the current version: refused while a placeholder is unfilled, because the text is not the company's yet."""
    when = when or datetime.now(timezone.utc)
    today = today or when.date()
    version = version_of(conn, policy["id"], policy["current_version"])
    left = placeholders_left(version["body"]) if version else []
    if left:
        raise ValueError("Fill these placeholders before approving: " + ", ".join(left) + ".")
    days = CYCLES.get(policy["review_cycle"], ("", 365))[1]
    conn.execute(
        text("UPDATE policy_versions SET approved_by = :by, approved_at = :at WHERE policy_id = :id AND number = :n"),
        {"by": str(by), "at": when, "id": str(policy["id"]), "n": policy["current_version"]},
    )
    conn.execute(
        text("UPDATE policies SET status = 'approved', approved_at = :at, next_review_on = :due, updated_at = now() WHERE id = :id"),
        {"at": when, "due": today + timedelta(days=days), "id": str(policy["id"])},
    )


def acknowledge(conn: Connection, policy: dict, user_id: UUID | str, when: datetime | None = None) -> bool:
    """Record that this person accepted the current version; False if they already had."""
    exists = conn.execute(
        text("SELECT 1 FROM policy_acknowledgements WHERE policy_id = :id AND version_number = :n AND user_id = :u"),
        {"id": str(policy["id"]), "n": policy["current_version"], "u": str(user_id)},
    ).first()
    if exists:
        return False
    conn.execute(
        text(
            "INSERT INTO policy_acknowledgements (organization_id, policy_id, version_number, user_id, acknowledged_at) "
            "VALUES (:org, :id, :n, :u, coalesce(:at, now()))"
        ),
        {"org": str(policy["organization_id"]), "id": str(policy["id"]), "n": policy["current_version"], "u": str(user_id), "at": when},
    )
    return True


def new_version(conn: Connection, policy: dict, body: str, note: str | None, author: UUID | str) -> int:
    """Save edited text as the next version. The policy goes back to draft: approval and acknowledgements start again."""
    number = policy["current_version"] + 1
    conn.execute(
        text(
            "INSERT INTO policy_versions (organization_id, policy_id, number, body, change_note, author_user_id) "
            "VALUES (:org, :id, :n, :body, :note, :by)"
        ),
        {"org": str(policy["organization_id"]), "id": str(policy["id"]), "n": number, "body": body, "note": note, "by": str(author)},
    )
    conn.execute(
        text("UPDATE policies SET current_version = :n, status = 'draft', approved_at = NULL, next_review_on = NULL, updated_at = now() WHERE id = :id"),
        {"n": number, "id": str(policy["id"])},
    )
    return number


# ------------------------------------------------------------------ sample data

def seed_policies(conn: Connection, org_id: UUID, company: str, users: list[Any], today: date | None = None) -> None:
    """The library adopted by a sample company, part way through the work a real one would be doing.

    `users` are the sample users in order: the first is the CEO and holds the people-side roles,
    the last the Security, IT and AI roles (the same person in a one-person company). Most policies
    are approved and acknowledged; the Information Security Policy waits for the CEO, which is the
    Decide task on the Tasks page; the rest are drafts. Dates are relative to today.
    """
    today = today or date.today()
    if conn.execute(text("SELECT 1 FROM policies LIMIT 1")).first():
        return
    first, last = users[0], users[-1]
    adopted_on = today - timedelta(days=60)
    at = datetime(adopted_on.year, adopted_on.month, adopted_on.day, 14, 0, tzinfo=timezone.utc)
    values = {
        "Company": company,
        "CEO": first.display_name, "HR Lead": first.display_name, "Privacy Lead": first.display_name, "Finance Lead": first.display_name,
        "Security Lead": last.display_name, "IT Lead": last.display_name, "AI Lead": last.display_name,
        "Effective Date": adopted_on.strftime("%B %d, %Y"),
    }
    role_users = {"CEO": first.id, "HR Lead": first.id, "Privacy Lead": first.id, "Finance Lead": first.id, "Security Lead": last.id, "IT Lead": last.id, "AI Lead": last.id}
    adopt_library(conn, org_id, values, role_users, first.id, at)
    policies = {p["template_id"]: p for p in list_policies(conn, today=today)}
    # Which policies are approved so far depends on the company: Alimi dogfoods the whole library.
    approved = {"POL-02", "POL-03", "POL-04", "POL-06", "POL-09", "POL-10", "POL-11", "POL-13", "POL-18", "POL-19"}
    if company.startswith("Harbor"):
        approved = {"POL-02", "POL-03", "POL-04", "POL-13"}
    elif company == "Alimi":
        approved = set(policies) - {"POL-01"}
    partial = {"POL-02", "POL-03", "POL-04", "POL-06", "POL-13", "POL-18"}  # what the second person has accepted so far
    approved_at = at + timedelta(days=3)
    for template_id, p in policies.items():
        if template_id == "POL-01":
            submit(conn, p)
            continue
        if template_id not in approved:
            continue
        approve(conn, p, first.id, approved_at, approved_at.date())
        acknowledge(conn, p, first.id, approved_at + timedelta(hours=1))
        if last.id != first.id and (template_id in partial or company == "Alimi"):
            acknowledge(conn, p, last.id, approved_at + timedelta(days=2))
