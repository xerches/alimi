"""Tasks and projects: the sample month's list, the ticket lifecycle, projects, and that one
company's tickets are invisible to another."""

from __future__ import annotations

import re
from datetime import date, timedelta

from sqlalchemy import text

from alimi_platform.db import org_scope
from alimi_platform.status import control_statuses

TASK_LINK = re.compile(r'href="/tasks/([0-9a-f-]{36})"')
STRIP = re.compile(r'<nav class="strip".*?</nav>', re.S)
COLUMN = re.compile(r'<aside class="column".*?</aside>', re.S)


def test_seed_raises_a_fix_task_for_every_failing_control(signed_in, orgs, app_engine):
    client = signed_in("saltmarsh")
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        failing = [c for c in control_statuses(conn) if c.status == "failing"]
        fixes = conn.execute(text("SELECT source_id FROM tasks WHERE kind = 'fix' ORDER BY source_id")).scalars().all()
    assert failing and sorted(c.id for c in failing) == fixes
    r = client.get("/tasks")
    assert r.status_code == 200 and "Cyber insurance renewal" in r.text
    assert r.text.count('class="badge k-fix"') == len(failing) and 'class="badge k-decide"' in r.text
    # Alimi's sample tenant passes, so it has no Fix tasks; its Decide tasks still show.
    r = signed_in("alimi").get("/tasks")
    assert 'class="badge k-fix"' not in r.text and "Approve the Information Security Policy" in r.text


def test_tasks_section_sits_in_the_strip_and_the_menu(signed_in):
    client = signed_in("harbor-dental")
    r = client.get("/tasks")
    strip = STRIP.search(r.text).group(0)
    assert 'href="/tasks" aria-current="page"' in strip
    column = COLUMN.search(r.text).group(0)
    assert "My tasks" in column and "Projects" in column and "Cyber insurance renewal" in column and "New project" in column
    assert 'href="/tasks?view=open" aria-current="page"' in column
    assert 'href="/tasks?view=mine"' in r.text  # the account menu's My tasks
    assert client.get("/tasks?view=nope").status_code == 404
    mine = client.get("/tasks?view=mine")
    assert 'href="/tasks?view=mine" aria-current="page"' in COLUMN.search(mine.text).group(0)


def test_a_ticket_goes_from_new_to_done_with_a_comment(signed_in, orgs):
    client = signed_in("saltmarsh", 1)  # Theo
    theo = orgs["saltmarsh"].users[1]
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    r = client.post(
        "/tasks",
        data={"title": "  Order  the  laptop encryption report ", "kind": "custom", "priority": "high", "assignee": str(theo.id), "due_on": tomorrow,
              "detail": "Ask the IT provider.\nAttach it to CTL-20.", "external_system": "jira", "external_key": "SEC-12", "external_url": "https://example.atlassian.net/browse/SEC-12"},
        follow_redirects=False,
    )
    assert r.status_code == 303, r.text
    task_id = re.search(r"/tasks/([0-9a-f-]{36})", r.headers["location"]).group(1)
    detail = client.get(f"/tasks/{task_id}?created=1")
    assert detail.status_code == 200
    assert "Order the laptop encryption report" in detail.text and "Task created." in detail.text
    assert "Jira" in detail.text and "SEC-12 ↗" in detail.text and "This week" in detail.text
    assert "Ask the IT provider." in detail.text and 'class="badge t-open"' in detail.text and ">Start<" in detail.text

    assert task_id in client.get("/tasks?view=mine").text
    assert task_id not in signed_in("saltmarsh", 0).get("/tasks?view=mine").text  # Dana's list, not hers

    client = signed_in("saltmarsh", 1)
    r = client.post(f"/tasks/{task_id}/status", data={"status": "in_progress"}, follow_redirects=False)
    assert r.status_code == 303
    assert 'class="badge t-in_progress"' in client.get(f"/tasks/{task_id}").text
    r = client.post(f"/tasks/{task_id}/comments", data={"body": "Report requested from the provider."}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].endswith("#comments")
    page = client.get(f"/tasks/{task_id}")
    assert "Report requested from the provider." in page.text and "Theo Marsh" in page.text
    r = client.post(f"/tasks/{task_id}/status", data={"status": "done"}, follow_redirects=False)
    assert r.status_code == 303
    done = client.get(f"/tasks/{task_id}")
    assert 'class="badge t-done"' in done.text and ">Reopen<" in done.text and "<dt>Done</dt>" in done.text
    assert task_id in client.get("/tasks?view=done").text and task_id not in client.get("/tasks?view=open").text

    r = client.post(f"/tasks/{task_id}", data={"title": "Laptop encryption report, ordered", "kind": "renew", "priority": "normal", "due_on": "", "external_system": "", "external_key": "", "external_url": ""}, follow_redirects=False)
    assert r.status_code == 303
    edited = client.get(f"/tasks/{task_id}?saved=1")
    assert "Laptop encryption report, ordered" in edited.text and 'class="badge k-renew"' in edited.text and "Saved." in edited.text
    audit = client.get("/audit").text
    for action in ("task.create", "task.status", "task.comment", "task.update"):
        assert action in audit


def test_bad_task_input_is_refused(signed_in, orgs):
    client = signed_in("harbor-dental")
    assert client.post("/tasks", data={"title": "   "}).status_code == 400
    assert client.post("/tasks", data={"title": "x", "kind": "wish"}).status_code == 400
    assert client.post("/tasks", data={"title": "x", "due_on": "soon"}).status_code == 400
    assert client.post("/tasks", data={"title": "x", "external_url": "javascript:alert(1)"}).status_code == 400
    assert client.post("/tasks", data={"title": "x", "assignee": str(orgs["saltmarsh"].users[0].id)}).status_code == 404  # not a member here
    assert client.post("/tasks", data={"title": "x", "assignee": "not-an-id"}).status_code == 400


def test_projects_group_tasks_and_show_progress(signed_in):
    client = signed_in("saltmarsh")
    r = client.get("/projects")
    assert r.status_code == 200 and "Cyber insurance renewal" in r.text and re.search(r"\d+ of \d+ done", r.text)
    r = client.post("/projects", data={"name": "SOC 2 readiness", "description": "Type I by spring.", "status": "active", "external_system": "monday", "external_key": "Board 44", "external_url": "https://example.monday.com/boards/44"}, follow_redirects=False)
    assert r.status_code == 303
    project_id = re.search(r"/projects/([0-9a-f-]{36})", r.headers["location"]).group(1)
    page = client.get(f"/projects/{project_id}?created=1")
    assert "SOC 2 readiness" in page.text and "Project created." in page.text and "Monday.com" in page.text and "0 of 0 done" in page.text
    r = client.post("/tasks", data={"title": "Pick the audit window", "project": project_id, "kind": "decide"}, follow_redirects=False)
    assert r.status_code == 303
    page = client.get(f"/projects/{project_id}")
    assert "Pick the audit window" in page.text and "0 of 1 done" in page.text
    assert f'href="/projects/{project_id}"' in COLUMN.search(page.text).group(0)
    filtered = client.get(f"/tasks?project={project_id}")
    table = filtered.text.split("<table", 1)[1].split("</table>", 1)[0]
    assert "Pick the audit window" in table and "Cyber insurance renewal" not in table
    r = client.post(f"/projects/{project_id}", data={"name": "SOC 2 readiness", "status": "done"}, follow_redirects=False)
    assert r.status_code == 303 and 'class="badge p-done"' in client.get(f"/projects/{project_id}").text


def test_overdue_tasks_show_a_badge_on_the_strip(signed_in):
    client = signed_in("harbor-dental")
    assert "overdue tasks" not in STRIP.search(client.get("/dashboard").text).group(0)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    assert client.post("/tasks", data={"title": "Late already", "due_on": yesterday}, follow_redirects=False).status_code == 303
    home = client.get("/dashboard")
    assert re.search(r'strip-badge" data-tone="danger" aria-label="1 overdue tasks"', STRIP.search(home.text).group(0))
    assert "1 overdue" in home.text and "Overdue" in client.get("/tasks").text


def test_another_companys_tickets_do_not_exist_here(signed_in, orgs, app_engine):
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        harbor_task = conn.execute(text("SELECT id FROM tasks LIMIT 1")).scalar()
        harbor_project = conn.execute(text("SELECT id FROM projects LIMIT 1")).scalar()
    client = signed_in("saltmarsh")
    assert client.get(f"/tasks/{harbor_task}").status_code == 404
    assert client.post(f"/tasks/{harbor_task}/status", data={"status": "done"}).status_code == 404
    assert client.post(f"/tasks/{harbor_task}/comments", data={"body": "hi"}).status_code == 404
    assert client.get(f"/projects/{harbor_project}").status_code == 404
    assert client.get(f"/tasks?project={harbor_project}").status_code == 404
    assert client.post("/tasks", data={"title": "x", "project": str(harbor_project)}).status_code == 404
