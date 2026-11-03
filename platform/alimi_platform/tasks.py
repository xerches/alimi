"""Tasks and projects: the queries the pages use, and the sample tasks the seed derives from a scan.

Every function takes a connection already inside org_scope, so "the tasks" always means this
organization's. Nothing here filters by organization in Python; the row policies do.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text

from .status import ControlStatus

STATUSES: dict[str, str] = {"open": "Open", "in_progress": "In progress", "blocked": "Blocked", "done": "Done"}
KINDS: dict[str, str] = {"fix": "Fix", "renew": "Renew", "decide": "Decide", "custom": "Task"}
PRIORITIES: dict[str, str] = {"low": "Low", "normal": "Normal", "high": "High", "urgent": "Urgent"}
EXTERNAL: dict[str, str] = {"jira": "Jira", "monday": "Monday.com"}
VIEWS: dict[str, str] = {"mine": "My tasks", "open": "Open", "done": "Done", "all": "All"}

# What a status button does, and what it reads on the page.
TRANSITIONS: dict[str, list[tuple[str, str]]] = {
    "open": [("in_progress", "Start"), ("blocked", "Mark blocked"), ("done", "Mark done")],
    "in_progress": [("done", "Mark done"), ("blocked", "Mark blocked"), ("open", "Back to open")],
    "blocked": [("in_progress", "Unblock"), ("done", "Mark done")],
    "done": [("open", "Reopen")],
}

SELECT_TASK = (
    "SELECT t.*, u.display_name AS assignee_name, p.name AS project_name, c.display_name AS creator_name "
    "FROM tasks t LEFT JOIN users u ON u.id = t.assignee_user_id "
    "LEFT JOIN projects p ON p.id = t.project_id LEFT JOIN users c ON c.id = t.created_by "
)


def source_href(kind: str | None, source_id: str | None) -> str | None:
    """Where the thing a task is about lives in the app."""
    if not kind or not source_id:
        return None
    return {
        "control": f"/controls/{source_id}",
        "test": "/monitoring",
        "evidence": f"/controls/{source_id}",
        "policy": f"/policies/{source_id}",
        "trust_request": "/trust/requests",
    }.get(kind)


def decorate(row: dict, today: date) -> dict:
    item = dict(row)
    item["overdue"] = bool(item["due_on"] and item["status"] != "done" and item["due_on"] < today)
    item["soon"] = bool(item["due_on"] and item["status"] != "done" and today <= item["due_on"] <= today + timedelta(days=7))
    item["source_href"] = source_href(item.get("source_kind"), item.get("source_id"))
    item["label"] = f"T-{item['number']}"
    return item


def list_tasks(conn: Connection, *, view: str = "open", user_id: UUID | str | None = None, project_id: UUID | None = None, today: date | None = None) -> list[dict]:
    today = today or date.today()
    where = ["true"]
    params: dict[str, Any] = {}
    if view == "mine":
        where.append("t.assignee_user_id = :me AND t.status <> 'done'")
        params["me"] = str(user_id)
    elif view == "open":
        where.append("t.status <> 'done'")
    elif view == "done":
        where.append("t.status = 'done'")
    if project_id is not None:
        where.append("t.project_id = :project")
        params["project"] = str(project_id)
    order = "t.done_at DESC NULLS LAST, t.number DESC" if view == "done" else "t.due_on ASC NULLS LAST, t.priority DESC, t.number"
    rows = conn.execute(text(SELECT_TASK + "WHERE " + " AND ".join(where) + " ORDER BY " + order), params).mappings().all()
    return [decorate(r, today) for r in rows]


def get_task(conn: Connection, task_id: UUID, today: date | None = None) -> dict | None:
    row = conn.execute(text(SELECT_TASK + "WHERE t.id = :id"), {"id": str(task_id)}).mappings().first()
    return decorate(row, today or date.today()) if row else None


def comments_of(conn: Connection, task_id: UUID) -> list[dict]:
    return conn.execute(
        text(
            "SELECT c.id, c.body, c.created_at, u.display_name AS author FROM task_comments c "
            "LEFT JOIN users u ON u.id = c.author_user_id WHERE c.task_id = :id ORDER BY c.created_at"
        ),
        {"id": str(task_id)},
    ).mappings().all()


def next_number(conn: Connection) -> int:
    return int(conn.execute(text("SELECT coalesce(max(number), 0) + 1 FROM tasks")).scalar())


def create_task(conn: Connection, org_id: UUID | str, created_by: UUID | str | None, **fields) -> UUID:
    cols = {
        "title": fields["title"],
        "detail": fields.get("detail") or None,
        "kind": fields.get("kind") or "custom",
        "source_kind": fields.get("source_kind"),
        "source_id": fields.get("source_id"),
        "status": fields.get("status") or "open",
        "priority": fields.get("priority") or "normal",
        "assignee": str(fields["assignee_user_id"]) if fields.get("assignee_user_id") else None,
        "due_on": fields.get("due_on"),
        "project": str(fields["project_id"]) if fields.get("project_id") else None,
        "external_system": fields.get("external_system") or None,
        "external_key": fields.get("external_key") or None,
        "external_url": fields.get("external_url") or None,
        "done_at": fields.get("done_at"),
        "created_at": fields.get("created_at"),
    }
    return conn.execute(
        text(
            "INSERT INTO tasks (organization_id, number, project_id, title, detail, kind, source_kind, source_id, status, priority, "
            "assignee_user_id, due_on, external_system, external_key, external_url, created_by, created_at, done_at) "
            "VALUES (:org, :number, :project, :title, :detail, :kind, :source_kind, :source_id, :status, :priority, "
            ":assignee, :due_on, :external_system, :external_key, :external_url, :by, coalesce(:created_at, now()), :done_at) RETURNING id"
        ),
        {**cols, "org": str(org_id), "number": next_number(conn), "by": str(created_by) if created_by else None},
    ).scalar()


def projects_with_counts(conn: Connection) -> list[dict]:
    rows = conn.execute(
        text(
            "SELECT p.*, u.display_name AS owner_name, "
            "count(t.id) FILTER (WHERE t.status <> 'done') AS open_count, "
            "count(t.id) FILTER (WHERE t.status = 'done') AS done_count, "
            "count(t.id) AS total "
            "FROM projects p LEFT JOIN users u ON u.id = p.owner_user_id LEFT JOIN tasks t ON t.project_id = p.id "
            "GROUP BY p.id, u.display_name ORDER BY p.status, p.due_on NULLS LAST, p.name"
        )
    ).mappings().all()
    out = []
    for r in rows:
        item = dict(r)
        item["percent"] = round(100 * item["done_count"] / item["total"]) if item["total"] else 0
        out.append(item)
    return out


def counts(conn: Connection, user_id: UUID | str | None = None, today: date | None = None) -> dict[str, int]:
    today = today or date.today()
    row = conn.execute(
        text(
            "SELECT count(*) FILTER (WHERE status <> 'done') AS open, "
            "count(*) FILTER (WHERE status <> 'done' AND due_on < :today) AS overdue, "
            "count(*) FILTER (WHERE status <> 'done' AND assignee_user_id = :me) AS mine, "
            "count(*) FILTER (WHERE status = 'done') AS done FROM tasks"
        ),
        {"today": today, "me": str(user_id) if user_id else None},
    ).mappings().one()
    return dict(row)


# ------------------------------------------------------------------ sample data

def seed_tasks(conn: Connection, org_id: UUID, owner: UUID, member: UUID | None, controls: list[ControlStatus], today: date | None = None) -> None:
    """A renewal project and the tasks a first scan would raise, so the sample company has a month's list.

    Fix tasks come from the controls the scan turned red, Renew tasks from evidence past its date or
    missing on tested controls, and two Decide tasks from the policy and owner work every new company
    faces. Dates are relative to today, so the list stays current however old the seed is.
    """
    today = today or date.today()
    if conn.execute(text("SELECT 1 FROM tasks LIMIT 1")).first():
        return
    project_id = conn.execute(
        text(
            "INSERT INTO projects (organization_id, name, description, owner_user_id, due_on, created_by) "
            "VALUES (:org, :name, :desc, :owner, :due, :owner) RETURNING id"
        ),
        {
            "org": str(org_id),
            "name": "Cyber insurance renewal",
            "desc": "Everything the broker's questionnaire asks for, fixed or evidenced before the renewal date.",
            "owner": str(owner),
            "due": today + timedelta(days=75),
        },
    ).scalar()
    failing = [c for c in controls if c.status == "failing"]
    attention = [c for c in controls if c.status in ("evidence_expired", "needs_evidence") and c.tests]
    people = [owner, member or owner]
    for i, c in enumerate(failing):
        create_task(
            conn, org_id, None, title=f"Fix: {c.name}", kind="fix", source_kind="control", source_id=c.id,
            detail="Raised by the scan: the test behind this control failed. The control page shows what the check read and the fix.",
            priority="high" if i < 3 else "normal", assignee_user_id=people[i % 2], due_on=today + timedelta(days=7 + 6 * i),
            project_id=project_id, created_at=today - timedelta(days=2),
        )
    for i, c in enumerate(attention):
        expired = c.status == "evidence_expired"
        create_task(
            conn, org_id, None, title=("Renew the evidence: " if expired else "Put evidence on file: ") + c.name,
            kind="renew", source_kind="evidence", source_id=c.id,
            detail="An attestation counts only while it is current. Upload the export or the record and set the next renewal date.",
            priority="high" if expired else "normal", assignee_user_id=people[(i + 1) % 2], due_on=today + timedelta(days=14 + 10 * i),
            project_id=project_id, created_at=today - timedelta(days=2),
        )
    create_task(
        conn, org_id, None, title="Approve the Information Security Policy", kind="decide", source_kind="policy", source_id="information-security-policy",
        detail="Staff cannot be asked to accept a policy nobody has approved. Read it, adapt the roles, approve it; the acknowledgement requests go out after.",
        priority="high", assignee_user_id=owner, due_on=today + timedelta(days=10), project_id=project_id, created_at=today - timedelta(days=2),
    )
    create_task(
        conn, org_id, None, title="Name an owner for every control", kind="decide", source_kind="control", source_id="CTL-01",
        detail="Nothing moves on a control nobody owns. Most small companies split them between the owner and the IT provider.",
        priority="normal", assignee_user_id=owner, due_on=today + timedelta(days=20), created_at=today - timedelta(days=2),
    )
    done_id = create_task(
        conn, org_id, None, title="Connect Microsoft 365 or Google Workspace read-only and run the first scan", kind="custom",
        detail="Done at sign-up. The scan reads the tenant with read-only permissions; nothing is changed.",
        status="done", assignee_user_id=owner, due_on=today - timedelta(days=1), project_id=project_id,
        created_at=today - timedelta(days=3), done_at=today - timedelta(days=2),
    )
    conn.execute(
        text("INSERT INTO task_comments (organization_id, task_id, author_user_id, body) VALUES (:org, :task, :by, :body)"),
        {"org": str(org_id), "task": str(done_id), "by": str(owner), "body": "Scan finished; the Fix tasks in this project come from it."},
    )
