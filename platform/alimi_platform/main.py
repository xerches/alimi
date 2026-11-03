"""The web app: FastAPI routes rendering Jinja templates, with HTMX for the in-page buttons.

Why this shape: FastAPI gives typed routes and a test client; server-rendered HTML keeps
every page working without a JavaScript build, and HTMX (one vendored file) swaps a part of
the page when a button is pressed, which is all a compliance dashboard needs. Every route
that touches customer data goes through `scope()`, which opens a transaction acting for the
signed-in organization; Postgres row-level security does the filtering.
"""

from __future__ import annotations

import logging
from collections import Counter
from contextlib import contextmanager
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError
from starlette.middleware.sessions import SessionMiddleware

from .audit import record
from .catalog import domain_labels
from .config import ConfigError, Settings, load_settings
from .crypto import install_log_redaction
from .db import make_engine, org_scope
from .scans import ScanRefused, run_scan
from .seed import SAMPLE_ORGS
from .nav import shell
from .policies import (
    BODY_LIMIT,
    CAN_ACKNOWLEDGE,
    CAN_APPROVE,
    acknowledge,
    acknowledgements_of,
    approve,
    control_ids_of,
    get_policy,
    list_policies,
    markers_left,
    new_version,
    placeholders_left,
    render as render_policy,
    requirements_of,
    submit,
    version_of,
    versions_of,
)
from .policies import STATUSES as POLICY_STATUSES
from .policies import VIEWS as POLICY_VIEWS
from .policies import counts as policy_counts
from .status import STATUSES, control_statuses, latest_results, requirement_statuses
from .markdown import to_html
from .trust import (
    CAN_MANAGE,
    DOCUMENT_KINDS,
    EMAIL,
    REQUEST_STATUSES,
    RESERVED_SLUGS,
    SLUG,
    VISIBILITIES,
    access_for_key,
    decide_request,
    directory_entry,
    documents_of,
    folders_of,
    get_request,
    grouped,
    lines,
    page_of,
    questions_of,
    requests_of,
    resolve_slug,
    submit_request,
    subprocessors_of,
    subscribe,
    updates_of,
    views_recent,
)
from .trust import count_view as count_trust_view
from .trust import counts as trust_counts
from .tasks import (
    EXTERNAL,
    KINDS,
    PRIORITIES,
    TRANSITIONS,
    VIEWS,
    comments_of,
    create_task,
    get_task,
    list_tasks,
    projects_with_counts,
)
from .tasks import STATUSES as TASK_STATUSES
from .tasks import counts as task_counts
from .theme import load_brand, theme_css

HERE = Path(__file__).parent
log = logging.getLogger("alimi.platform")

# The time zones the Profile page offers. A short list on purpose: the sample companies are in the US,
# and the full IANA list arrives with real sign-in.
TIME_ZONES: tuple[str, ...] = (
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Phoenix",
    "America/Los_Angeles",
    "America/Anchorage",
    "Pacific/Honolulu",
    "America/Toronto",
    "Europe/London",
    "Europe/Paris",
    "UTC",
)
NOTIFICATION_KEYS: tuple[str, ...] = (
    "notify_failed_tests",
    "notify_renewals",
    "notify_policy_acknowledgements",
    "notify_access_requests",
    "notify_weekly_digest",
)


def initials(name: str) -> str:
    parts = [p for p in name.replace("(", " ").replace(")", " ").split() if p[0].isalnum()]
    return "".join(p[0].upper() for p in parts[:2]) or "?"


class NotSignedIn(Exception):
    pass


def create_app(settings: Settings | None = None, engine: Engine | None = None) -> FastAPI:
    settings = settings or load_settings()
    if not settings.is_mock:  # load_settings already refuses; this guards a hand-built Settings
        raise ConfigError("The mock-mode user picker only loads when ALIMI_MODE=mock.")
    install_log_redaction()
    engine = engine or make_engine(settings.database_url)
    brand = load_brand(settings.repo_root)
    if not settings.site_url:
        settings = replace(settings, site_url=str(brand.get("site_url", "")))
    # Both themes, built once from config/brand.yaml; served at /theme.css ahead of app.css.
    stylesheet = theme_css(brand)

    app = FastAPI(title="Alimi platform (mock mode)", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie="alimi_session",
        same_site="lax",       # the browser will not send the cookie on another site's form post
        https_only=False,      # local mock mode runs on http://localhost; 12b turns this on
        max_age=8 * 3600,
    )
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")
    templates.env.globals["STATUSES"] = STATUSES
    templates.env.globals["TASK_STATUSES"] = TASK_STATUSES
    templates.env.globals["TASK_KINDS"] = KINDS
    templates.env.globals["POLICY_STATUSES"] = POLICY_STATUSES
    templates.env.globals["VISIBILITIES"] = VISIBILITIES
    templates.env.globals["REQUEST_STATUSES"] = REQUEST_STATUSES
    app.state.settings = settings
    app.state.engine = engine

    @app.exception_handler(NotSignedIn)
    async def _not_signed_in(request: Request, exc: NotSignedIn):
        if request.headers.get("HX-Request"):
            return HTMLResponse("", status_code=401, headers={"HX-Redirect": "/login"})
        return RedirectResponse("/login", status_code=303)

    @contextmanager
    def scope(request: Request):
        """Open a transaction for the signed-in user and organization, or bounce to the picker."""
        user_id = request.session.get("user_id")
        org_id = request.session.get("org_id")
        if not user_id or not org_id:
            raise NotSignedIn()
        with org_scope(engine, org_id, user_id) as conn:
            me = conn.execute(
                text(
                    "SELECT u.id, u.display_name, u.email, u.job_title, m.role, o.id AS org_id, o.name AS org_name, o.slug AS org_slug "
                    "FROM memberships m JOIN users u ON u.id = m.user_id JOIN organizations o ON o.id = m.organization_id "
                    "WHERE m.user_id = :u"
                ),
                {"u": user_id},
            ).mappings().first()
            if me is None:
                # The membership is gone (or the cookie names an org the user is not in).
                request.session.clear()
                raise NotSignedIn()
            yield conn, {**me, "initials": initials(me["display_name"])}

    def render(request: Request, name: str, status_code: int = 200, **context) -> HTMLResponse:
        return templates.TemplateResponse(request, name, context, status_code=status_code)

    # ------------------------------------------------------------------ sign-in (mock only)

    @app.get("/", include_in_schema=False)
    def home(request: Request):
        return RedirectResponse("/dashboard" if request.session.get("user_id") else "/login", status_code=303)

    @app.get("/login", response_class=HTMLResponse)
    def login_page(request: Request):
        return render(request, "login.html", orgs=SAMPLE_ORGS)

    @app.post("/login")
    def login(request: Request, org_id: str = Form(...), user_id: str = Form(...)):
        # Only the sample users from seed.py can be picked. Real sign-in is prompt 12b.
        valid = {(str(o.id), str(u.id)) for o in SAMPLE_ORGS for u in o.users}
        if (org_id, user_id) not in valid:
            raise HTTPException(status_code=400, detail="Pick one of the sample users.")
        with org_scope(engine, org_id, user_id) as conn:
            member = conn.execute(
                text("SELECT 1 FROM memberships WHERE user_id = :u"), {"u": user_id}
            ).first()
            if member is None:
                raise HTTPException(status_code=400, detail="That sample user is not set up. Run the seed first.")
            record(conn, org_id, user_id, "login.mock", f"user:{user_id}")
        request.session.clear()
        request.session.update({"user_id": user_id, "org_id": org_id, "signed_in_at": datetime.now(timezone.utc).isoformat()})
        return RedirectResponse("/dashboard", status_code=303)

    @app.post("/logout")
    def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    @app.get("/theme.css", include_in_schema=False)
    def theme_stylesheet():
        return PlainTextResponse(stylesheet, media_type="text/css", headers={"Cache-Control": "public, max-age=3600"})

    # ------------------------------------------------------------------ pages

    def page(request: Request, name: str, conn, me: dict, key: str, *, item: str | None = None, crumbs=(), controls=None, **context) -> HTMLResponse:
        """Render a page inside the shell: strip badges, the column and the current item come from this org's rows."""
        if controls is None:
            controls = control_statuses(conn)
        context.setdefault("controls", controls)
        return render(request, name, me=me, shell=shell(conn, settings, key, item, controls, user_id=me["id"]), crumbs=list(crumbs), **context)

    def members_of(conn):
        return conn.execute(
            text("SELECT u.id, u.display_name, m.role FROM memberships m JOIN users u ON u.id = m.user_id ORDER BY u.display_name")
        ).mappings().all()

    def integrations_of(conn):
        return conn.execute(
            text(
                "SELECT id, platform, display_name, mode, fixture, scopes, last_sync_at, last_sync_status, "
                "(token_ciphertext IS NOT NULL) AS has_token FROM integrations ORDER BY created_at"
            )
        ).mappings().all()

    def runs_of(conn, limit: int = 20):
        return conn.execute(
            text(
                "SELECT r.id, r.started_at, r.source, r.score_percent, "
                "count(t.id) FILTER (WHERE t.status = 'pass') AS passed, "
                "count(t.id) FILTER (WHERE t.status = 'fail') AS failed, "
                "count(t.id) FILTER (WHERE t.status = 'attestation_needed') AS attest, "
                "count(t.id) FILTER (WHERE t.status = 'error') AS errors "
                "FROM scan_runs r LEFT JOIN test_results t ON t.scan_run_id = r.id "
                "GROUP BY r.id ORDER BY r.started_at DESC LIMIT :n"
            ),
            {"n": limit},
        ).mappings().all()

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard(request: Request):
        with scope(request) as (conn, me):
            integrations = integrations_of(conn)
            runs = runs_of(conn, 1)
            controls = control_statuses(conn)
            counts = Counter(c.status for c in controls)
            return page(
                request, "dashboard.html", conn, me, "dashboard", controls=controls,
                integrations=integrations, last_run=runs[0] if runs else None, counts=counts, total=len(controls),
                tasks=task_counts(conn, me["id"]), mine=list_tasks(conn, view="mine", user_id=me["id"])[:5],
                policies=policy_counts(conn, me["id"]),
            )

    @app.post("/integrations/{integration_id}/scan", response_class=HTMLResponse)
    def scan(request: Request, integration_id: UUID):
        with scope(request) as (conn, me):
            try:
                run_id = run_scan(conn, settings, integration_id, me["id"])
            except LookupError:
                raise HTTPException(status_code=404, detail="No such integration.") from None
            except ScanRefused as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from None
            run = conn.execute(
                text(
                    "SELECT r.id, r.started_at, r.source, r.score_percent, "
                    "count(*) FILTER (WHERE t.status = 'pass') AS passed, "
                    "count(*) FILTER (WHERE t.status = 'fail') AS failed, "
                    "count(*) FILTER (WHERE t.status = 'attestation_needed') AS attest, "
                    "count(*) FILTER (WHERE t.status = 'error') AS errors "
                    "FROM scan_runs r JOIN test_results t ON t.scan_run_id = r.id WHERE r.id = :id GROUP BY r.id"
                ),
                {"id": run_id},
            ).mappings().first()
        return render(request, "_scan_result.html", run=run)

    @app.get("/monitoring", response_class=HTMLResponse)
    def monitoring(request: Request):
        with scope(request) as (conn, me):
            integrations = integrations_of(conn)
            runs = runs_of(conn)
            latest = latest_results(conn)
            links: dict[str, list[str]] = {}
            for control_id, test_id in conn.execute(text("SELECT control_id, test_id FROM control_tests ORDER BY control_id")):
                links.setdefault(test_id, []).append(control_id)
            order = {"fail": 0, "error": 1, "attestation_needed": 2, "pass": 3, "not_applicable": 4}
            results = sorted(
                ({"id": test_id, **row, "controls": links.get(test_id, [])} for test_id, row in latest.items()),
                key=lambda r: (order.get(r["status"], 9), r["severity"], r["id"]),
            )
            return page(
                request, "monitoring.html", conn, me, "monitoring", crumbs=[{"label": "Monitoring"}],
                integrations=integrations, runs=runs, results=results,
            )

    @app.get("/scans/{run_id}", response_class=HTMLResponse)
    def scan_detail(request: Request, run_id: UUID):
        with scope(request) as (conn, me):
            run = conn.execute(
                text("SELECT id, started_at, finished_at, source, scanner_version, score_percent FROM scan_runs WHERE id = :id"),
                {"id": run_id},
            ).mappings().first()
            if run is None:
                raise HTTPException(status_code=404, detail="No such scan.")
            results = conn.execute(
                text(
                    "SELECT r.test_id, t.title, t.severity, r.status, r.summary, r.raw_evidence, r.rule, "
                    "r.criterion_ids, r.control_ids, r.check_version FROM test_results r JOIN tests t ON t.id = r.test_id "
                    "WHERE r.scan_run_id = :id ORDER BY r.status, t.severity, r.test_id"
                ),
                {"id": run_id},
            ).mappings().all()
            crumbs = [{"label": "Monitoring", "href": "/monitoring"}, {"label": run["started_at"].strftime("Scan of %b %d, %Y")}]
            return page(request, "scan.html", conn, me, "scan", crumbs=crumbs, run=run, results=results)

    @app.get("/controls", response_class=HTMLResponse)
    def controls(request: Request, domain: str | None = None):
        domains = domain_labels(settings.repo_root)
        if domain is not None and domain not in domains:
            raise HTTPException(status_code=404, detail="No such area.")
        with scope(request) as (conn, me):
            items = control_statuses(conn)
            shown = [c for c in items if domain is None or c.domain == domain]
            crumbs = [{"label": "Controls", "href": "/controls" if domain else None}]
            if domain:
                crumbs.append({"label": domains[domain]})
            return page(
                request, "controls.html", conn, me, "controls", item=domain, crumbs=crumbs, controls=items,
                shown=shown, domains=domains, domain=domain,
            )

    @app.get("/controls/{control_id}", response_class=HTMLResponse)
    def control_detail(request: Request, control_id: str):
        domains = domain_labels(settings.repo_root)
        with scope(request) as (conn, me):
            ctl = conn.execute(text("SELECT * FROM controls WHERE id = :id"), {"id": control_id}).mappings().first()
            if ctl is None:
                raise HTTPException(status_code=404, detail="No such control.")
            items = control_statuses(conn)
            status = next(c for c in items if c.id == control_id)
            results = conn.execute(
                text(
                    "SELECT DISTINCT ON (r.test_id) r.test_id, t.title, t.kind, r.status, r.summary, r.raw_evidence, "
                    "r.rule, r.criterion_ids, r.check_version, r.collected_at, r.scan_run_id "
                    "FROM test_results r JOIN tests t ON t.id = r.test_id WHERE :id = ANY (r.control_ids) "
                    "ORDER BY r.test_id, r.collected_at DESC"
                ),
                {"id": control_id},
            ).mappings().all()
            requirements = conn.execute(
                text(
                    "SELECT r.framework_id, r.code, r.summary FROM control_requirements cr "
                    "JOIN requirements r ON r.id = cr.requirement_id WHERE cr.control_id = :id ORDER BY r.framework_id, r.code"
                ),
                {"id": control_id},
            ).mappings().all()
            crumbs = [
                {"label": "Controls", "href": "/controls"},
                {"label": domains.get(ctl["domain"], ctl["domain"]), "href": f"/controls?domain={ctl['domain']}"},
                {"label": ctl["id"]},
            ]
            return page(
                request, "control.html", conn, me, "control", item=ctl["domain"], crumbs=crumbs, controls=items,
                ctl=ctl, status=status, results=results, requirements=requirements, domains=domains,
            )

    @app.get("/frameworks", response_class=HTMLResponse)
    def frameworks(request: Request):
        with scope(request) as (conn, me):
            items = conn.execute(text("SELECT * FROM frameworks ORDER BY position")).mappings().all()
            return page(request, "frameworks.html", conn, me, "frameworks", crumbs=[{"label": "Frameworks"}], frameworks=items)

    @app.get("/frameworks/insurer", response_class=HTMLResponse)
    def insurer(request: Request):
        with scope(request) as (conn, me):
            fw = conn.execute(text("SELECT * FROM frameworks WHERE id = 'insurer'")).mappings().first()
            items = control_statuses(conn)
            reqs = requirement_statuses(conn, "insurer", items)
            crumbs = [{"label": "Frameworks", "href": "/frameworks"}, {"label": fw["short_name"]}]
            return page(request, "insurer.html", conn, me, "insurer", crumbs=crumbs, controls=items, fw=fw, requirements=reqs)

    @app.get("/settings", response_class=HTMLResponse)
    def settings_page(request: Request):
        with scope(request) as (conn, me):
            members = conn.execute(
                text(
                    "SELECT u.id, u.display_name, m.role FROM memberships m JOIN users u ON u.id = m.user_id ORDER BY u.display_name"
                )
            ).mappings().all()
            integrations = integrations_of(conn)
            return page(
                request, "settings.html", conn, me, "settings", crumbs=[{"label": "Settings"}],
                members=members, integrations=integrations,
            )

    @app.get("/audit", response_class=HTMLResponse)
    def audit(request: Request):
        with scope(request) as (conn, me):
            entries = conn.execute(
                text(
                    "SELECT a.at, a.action, a.target, a.detail, u.display_name FROM audit_log a "
                    "LEFT JOIN users u ON u.id = a.actor_user_id ORDER BY a.at DESC LIMIT 200"
                )
            ).mappings().all()
            crumbs = [{"label": "Settings", "href": "/settings"}, {"label": "Audit log"}]
            return page(request, "audit.html", conn, me, "audit", crumbs=crumbs, entries=entries)

    # ------------------------------------------------------------------ tasks and projects

    def field(form, name: str, limit: int = 160) -> str:
        value = " ".join(str(form.get(name, "")).split()) if name != "detail" and name != "description" and name != "body" else str(form.get(name, "")).strip()
        if len(value) > limit:
            raise HTTPException(status_code=400, detail=f"{name} is longer than {limit} characters.")
        return value

    def choice(form, name: str, allowed, default: str = "") -> str:
        value = str(form.get(name, default) or default)
        if value and value not in allowed:
            raise HTTPException(status_code=400, detail=f"{name}: pick one of {', '.join(allowed)}.")
        return value

    def a_date(form, name: str):
        value = str(form.get(name, "") or "").strip()
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{name} must be a date, YYYY-MM-DD.") from None

    def an_id(form, name: str, allowed_ids) -> UUID | None:
        value = str(form.get(name, "") or "").strip()
        if not value:
            return None
        try:
            parsed = UUID(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{name} is not an id.") from None
        if parsed not in allowed_ids:
            raise HTTPException(status_code=404, detail=f"No such {name}.")
        return parsed

    def external_fields(form) -> dict:
        system = choice(form, "external_system", EXTERNAL)
        key = field(form, "external_key", 60)
        url = field(form, "external_url", 400)
        if url and not url.startswith(("https://", "http://")):
            raise HTTPException(status_code=400, detail="The ticket link must start with https://.")
        return {"external_system": system or None, "external_key": key or None, "external_url": url or None}

    def task_fields(form, conn) -> dict:
        title = field(form, "title")
        if not title:
            raise HTTPException(status_code=400, detail="A task needs a title.")
        members = {m["id"] for m in members_of(conn)}
        projects = {p["id"] for p in projects_with_counts(conn)}
        return {
            "title": title,
            "detail": field(form, "detail", 4000) or None,
            "kind": choice(form, "kind", KINDS, "custom"),
            "priority": choice(form, "priority", PRIORITIES, "normal"),
            "assignee_user_id": an_id(form, "assignee", members),
            "due_on": a_date(form, "due_on"),
            "project_id": an_id(form, "project", projects),
            **external_fields(form),
        }

    @app.get("/tasks", response_class=HTMLResponse)
    def tasks_page(request: Request, view: str = "open", project: str | None = None, created: str | None = None):
        if view not in VIEWS:
            raise HTTPException(status_code=404, detail="No such view.")
        with scope(request) as (conn, me):
            projects = projects_with_counts(conn)
            current = None
            if project:
                current = next((p for p in projects if str(p["id"]) == project), None)
                if current is None:
                    raise HTTPException(status_code=404, detail="No such project.")
            items = list_tasks(conn, view=view, user_id=me["id"], project_id=current["id"] if current else None)
            crumbs = [{"label": "Tasks", "href": "/tasks" if (view != "open" or current) else None}]
            if current:
                crumbs.append({"label": current["name"], "href": f"/projects/{current['id']}"})
            if view != "open" or current:
                crumbs.append({"label": VIEWS[view]})
            return page(
                request, "tasks.html", conn, me, "tasks", item=f"project:{current['id']}" if current else view, crumbs=crumbs,
                tasks=items, view=view, views=VIEWS, project=current, projects=projects, members=members_of(conn),
                kinds=KINDS, priorities=PRIORITIES, external=EXTERNAL, statuses=TASK_STATUSES, created=bool(created),
            )

    @app.post("/tasks")
    async def task_create(request: Request):
        form = await request.form()
        with scope(request) as (conn, me):
            fields = task_fields(form, conn)
            task_id = create_task(conn, me["org_id"], me["id"], **fields)
            number = conn.execute(text("SELECT number FROM tasks WHERE id = :id"), {"id": str(task_id)}).scalar()
            record(conn, me["org_id"], me["id"], "task.create", f"task:{task_id}", {"number": number, "title": fields["title"]})
        return RedirectResponse(f"/tasks/{task_id}?created=1", status_code=303)

    @app.get("/tasks/{task_id}", response_class=HTMLResponse)
    def task_detail(request: Request, task_id: UUID, saved: str | None = None, created: str | None = None):
        with scope(request) as (conn, me):
            t = get_task(conn, task_id)
            if t is None:
                raise HTTPException(status_code=404, detail="No such task.")
            crumbs = [{"label": "Tasks", "href": "/tasks"}]
            if t["project_id"]:
                crumbs.append({"label": t["project_name"], "href": f"/projects/{t['project_id']}"})
            crumbs.append({"label": t["label"]})
            return page(
                request, "task.html", conn, me, "task", item=f"project:{t['project_id']}" if t["project_id"] else "open", crumbs=crumbs,
                t=t, comments=comments_of(conn, task_id), transitions=TRANSITIONS[t["status"]], projects=projects_with_counts(conn),
                members=members_of(conn), kinds=KINDS, priorities=PRIORITIES, external=EXTERNAL, statuses=TASK_STATUSES,
                saved=bool(saved), created=bool(created),
            )

    @app.post("/tasks/{task_id}")
    async def task_edit(request: Request, task_id: UUID):
        form = await request.form()
        with scope(request) as (conn, me):
            if get_task(conn, task_id) is None:
                raise HTTPException(status_code=404, detail="No such task.")
            f = task_fields(form, conn)
            conn.execute(
                text(
                    "UPDATE tasks SET title = :title, detail = :detail, kind = :kind, priority = :priority, assignee_user_id = :assignee, "
                    "due_on = :due_on, project_id = :project, external_system = :external_system, external_key = :external_key, "
                    "external_url = :external_url, updated_at = now() WHERE id = :id"
                ),
                {**f, "assignee": str(f["assignee_user_id"]) if f["assignee_user_id"] else None, "project": str(f["project_id"]) if f["project_id"] else None, "id": str(task_id)},
            )
            record(conn, me["org_id"], me["id"], "task.update", f"task:{task_id}", {"title": f["title"]})
        return RedirectResponse(f"/tasks/{task_id}?saved=1", status_code=303)

    @app.post("/tasks/{task_id}/status")
    def task_status(request: Request, task_id: UUID, status: str = Form(...), back: str = Form("")):
        if status not in TASK_STATUSES:
            raise HTTPException(status_code=400, detail="No such status.")
        with scope(request) as (conn, me):
            t = get_task(conn, task_id)
            if t is None:
                raise HTTPException(status_code=404, detail="No such task.")
            conn.execute(
                text("UPDATE tasks SET status = :s, done_at = CASE WHEN :s = 'done' THEN now() ELSE NULL END, updated_at = now() WHERE id = :id"),
                {"s": status, "id": str(task_id)},
            )
            record(conn, me["org_id"], me["id"], "task.status", f"task:{task_id}", {"from": t["status"], "to": status})
        target = back if back.startswith("/") and not back.startswith("//") else f"/tasks/{task_id}"
        return RedirectResponse(target, status_code=303)

    @app.post("/tasks/{task_id}/comments")
    async def task_comment(request: Request, task_id: UUID):
        form = await request.form()
        body = field(form, "body", 4000)
        if not body:
            raise HTTPException(status_code=400, detail="An empty comment is not saved.")
        with scope(request) as (conn, me):
            if get_task(conn, task_id) is None:
                raise HTTPException(status_code=404, detail="No such task.")
            conn.execute(
                text("INSERT INTO task_comments (organization_id, task_id, author_user_id, body) VALUES (:org, :task, :by, :body)"),
                {"org": me["org_id"], "task": str(task_id), "by": me["id"], "body": body},
            )
            conn.execute(text("UPDATE tasks SET updated_at = now() WHERE id = :id"), {"id": str(task_id)})
            record(conn, me["org_id"], me["id"], "task.comment", f"task:{task_id}")
        return RedirectResponse(f"/tasks/{task_id}#comments", status_code=303)

    def project_fields(form, conn) -> dict:
        name = field(form, "name")
        if not name:
            raise HTTPException(status_code=400, detail="A project needs a name.")
        members = {m["id"] for m in members_of(conn)}
        return {
            "name": name,
            "description": field(form, "description", 2000) or None,
            "status": choice(form, "status", ("active", "done", "archived"), "active"),
            "owner": an_id(form, "owner", members),
            "due_on": a_date(form, "due_on"),
            **external_fields(form),
        }

    @app.get("/projects", response_class=HTMLResponse)
    def projects_page(request: Request):
        with scope(request) as (conn, me):
            crumbs = [{"label": "Tasks", "href": "/tasks"}, {"label": "Projects"}]
            return page(request, "projects.html", conn, me, "projects", crumbs=crumbs, projects=projects_with_counts(conn), members=members_of(conn), external=EXTERNAL)

    @app.post("/projects")
    async def project_create(request: Request):
        form = await request.form()
        with scope(request) as (conn, me):
            f = project_fields(form, conn)
            project_id = conn.execute(
                text(
                    "INSERT INTO projects (organization_id, name, description, status, owner_user_id, due_on, external_system, external_key, external_url, created_by) "
                    "VALUES (:org, :name, :description, :status, :owner, :due_on, :external_system, :external_key, :external_url, :by) RETURNING id"
                ),
                {**f, "owner": str(f["owner"]) if f["owner"] else None, "org": me["org_id"], "by": me["id"]},
            ).scalar()
            record(conn, me["org_id"], me["id"], "project.create", f"project:{project_id}", {"name": f["name"]})
        return RedirectResponse(f"/projects/{project_id}?created=1", status_code=303)

    @app.get("/projects/{project_id}", response_class=HTMLResponse)
    def project_detail(request: Request, project_id: UUID, saved: str | None = None, created: str | None = None):
        with scope(request) as (conn, me):
            p = next((p for p in projects_with_counts(conn) if p["id"] == project_id), None)
            if p is None:
                raise HTTPException(status_code=404, detail="No such project.")
            items = list_tasks(conn, view="all", project_id=project_id)
            columns = [(key, label, [t for t in items if t["status"] == key]) for key, label in TASK_STATUSES.items()]
            crumbs = [{"label": "Tasks", "href": "/tasks"}, {"label": "Projects", "href": "/projects"}, {"label": p["name"]}]
            return page(
                request, "project.html", conn, me, "project", item=f"project:{project_id}", crumbs=crumbs,
                p=p, columns=columns, members=members_of(conn), external=EXTERNAL, statuses=TASK_STATUSES, saved=bool(saved), created=bool(created),
            )

    @app.post("/projects/{project_id}")
    async def project_edit(request: Request, project_id: UUID):
        form = await request.form()
        with scope(request) as (conn, me):
            if conn.execute(text("SELECT 1 FROM projects WHERE id = :id"), {"id": str(project_id)}).first() is None:
                raise HTTPException(status_code=404, detail="No such project.")
            f = project_fields(form, conn)
            conn.execute(
                text(
                    "UPDATE projects SET name = :name, description = :description, status = :status, owner_user_id = :owner, due_on = :due_on, "
                    "external_system = :external_system, external_key = :external_key, external_url = :external_url, updated_at = now() WHERE id = :id"
                ),
                {**f, "owner": str(f["owner"]) if f["owner"] else None, "id": str(project_id)},
            )
            record(conn, me["org_id"], me["id"], "project.update", f"project:{project_id}", {"name": f["name"], "status": f["status"]})
        return RedirectResponse(f"/projects/{project_id}?saved=1", status_code=303)

    # ------------------------------------------------------------------ policies

    def policy_or_404(conn, slug: str, me: dict) -> dict:
        p = get_policy(conn, slug, me["id"])
        if p is None:
            raise HTTPException(status_code=404, detail="No such policy.")
        return p

    def may_edit(me: dict, p: dict) -> bool:
        return me["role"] in CAN_APPROVE or (p["owner_user_id"] == me["id"] and me["role"] in CAN_ACKNOWLEDGE)

    @app.get("/policies", response_class=HTMLResponse)
    def policies_page(request: Request, view: str = "all"):
        if view not in POLICY_VIEWS:
            raise HTTPException(status_code=404, detail="No such view.")
        with scope(request) as (conn, me):
            items = list_policies(conn, view=view, user_id=me["id"])
            crumbs = [{"label": "Policies", "href": "/policies" if view != "all" else None}]
            if view != "all":
                crumbs.append({"label": POLICY_VIEWS[view]})
            return page(
                request, "policies.html", conn, me, "policies", item=view, crumbs=crumbs,
                policies=items, view=view, views=POLICY_VIEWS, n=policy_counts(conn, me["id"]), today=date.today(),
            )

    @app.get("/policies/{slug}", response_class=HTMLResponse)
    def policy_page(request: Request, slug: str, done: str | None = None):
        with scope(request) as (conn, me):
            p = policy_or_404(conn, slug, me)
            version = version_of(conn, p["id"], p["current_version"])
            html, outline = render_policy(version["body"])
            items = control_statuses(conn)
            linked = control_ids_of(conn, p["template_id"])
            controls_linked = [c for c in items if c.id in linked]
            everything = list_policies(conn, user_id=me["id"])
            index = next((i for i, x in enumerate(everything) if x["id"] == p["id"]), 0)
            crumbs = [{"label": "Policies", "href": "/policies"}, {"label": p["label"] if p["template_id"] else p["title"]}]
            return page(
                request, "policy.html", conn, me, "policy", crumbs=crumbs, controls=items,
                p=p, version=version, document=html, outline=outline, placeholders=placeholders_left(version["body"]),
                markers=markers_left(version["body"]), requirements=requirements_of(conn, p["template_id"]), linked=controls_linked,
                people=acknowledgements_of(conn, p), versions=versions_of(conn, p["id"]), related=[x for x in everything if x["template_id"] in (p["related"] or [])],
                prev=everything[index - 1] if index > 0 else None, next=everything[index + 1] if index + 1 < len(everything) else None,
                can_edit=may_edit(me, p), can_approve=me["role"] in CAN_APPROVE, can_acknowledge=me["role"] in CAN_ACKNOWLEDGE, done=done,
            )

    @app.get("/policies/{slug}/download")
    def policy_download(request: Request, slug: str):
        with scope(request) as (conn, me):
            p = policy_or_404(conn, slug, me)
            version = version_of(conn, p["id"], p["current_version"])
            record(conn, me["org_id"], me["id"], "policy.download", f"policy:{p['id']}", {"version": p["current_version"]})
            head = f"<!-- {p['title']}, version {p['current_version']}, {POLICY_STATUSES[p['status']]}. Exported from Alimi for {me['org_name']}. -->\n\n"
            return PlainTextResponse(
                head + version["body"], media_type="text/markdown; charset=utf-8",
                headers={"Content-Disposition": f'attachment; filename="{slug}-v{p["current_version"]}.md"'},
            )

    @app.post("/policies/{slug}/submit")
    def policy_submit(request: Request, slug: str):
        with scope(request) as (conn, me):
            p = policy_or_404(conn, slug, me)
            if not may_edit(me, p):
                raise HTTPException(status_code=403, detail="Only the policy's owner or a company owner or admin sends a policy for approval.")
            if p["status"] != "draft":
                raise HTTPException(status_code=409, detail="Only a draft is sent for approval.")
            submit(conn, p)
            record(conn, me["org_id"], me["id"], "policy.submit", f"policy:{p['id']}", {"version": p["current_version"]})
        return RedirectResponse(f"/policies/{slug}?done=submitted", status_code=303)

    @app.post("/policies/{slug}/approve")
    def policy_approve(request: Request, slug: str):
        with scope(request) as (conn, me):
            p = policy_or_404(conn, slug, me)
            if me["role"] not in CAN_APPROVE:
                raise HTTPException(status_code=403, detail="Only a company owner or admin approves a policy.")
            if p["status"] not in ("draft", "in_review"):
                raise HTTPException(status_code=409, detail="This version is already approved.")
            try:
                approve(conn, p, me["id"])
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from None
            record(conn, me["org_id"], me["id"], "policy.approve", f"policy:{p['id']}", {"version": p["current_version"]})
        return RedirectResponse(f"/policies/{slug}?done=approved", status_code=303)

    @app.post("/policies/{slug}/acknowledge")
    def policy_acknowledge(request: Request, slug: str):
        with scope(request) as (conn, me):
            p = policy_or_404(conn, slug, me)
            if me["role"] not in CAN_ACKNOWLEDGE:
                raise HTTPException(status_code=403, detail="An auditor reads policies; staff acknowledge them.")
            if p["status"] != "approved":
                raise HTTPException(status_code=409, detail="A policy is acknowledged once it is approved.")
            if acknowledge(conn, p, me["id"]):
                record(conn, me["org_id"], me["id"], "policy.acknowledge", f"policy:{p['id']}", {"version": p["current_version"]})
        return RedirectResponse(f"/policies/{slug}?done=acknowledged", status_code=303)

    @app.get("/policies/{slug}/edit", response_class=HTMLResponse)
    def policy_edit(request: Request, slug: str):
        with scope(request) as (conn, me):
            p = policy_or_404(conn, slug, me)
            if not may_edit(me, p):
                raise HTTPException(status_code=403, detail="Only the policy's owner or a company owner or admin edits a policy.")
            version = version_of(conn, p["id"], p["current_version"])
            crumbs = [{"label": "Policies", "href": "/policies"}, {"label": p["label"], "href": f"/policies/{slug}"}, {"label": "Edit"}]
            return page(request, "policy_edit.html", conn, me, "policy_edit", crumbs=crumbs, p=p, version=version, limit=BODY_LIMIT)

    @app.post("/policies/{slug}/edit")
    async def policy_save(request: Request, slug: str):
        form = await request.form()
        body = str(form.get("body", "")).replace("\r\n", "\n").strip()
        note = field(form, "change_note", 300) or None
        if not body:
            raise HTTPException(status_code=400, detail="The policy text cannot be empty.")
        if len(body) > BODY_LIMIT:
            raise HTTPException(status_code=400, detail=f"The policy text is longer than {BODY_LIMIT} characters.")
        with scope(request) as (conn, me):
            p = policy_or_404(conn, slug, me)
            if not may_edit(me, p):
                raise HTTPException(status_code=403, detail="Only the policy's owner or a company owner or admin edits a policy.")
            current = version_of(conn, p["id"], p["current_version"])
            if current and current["body"].strip() == body:
                return RedirectResponse(f"/policies/{slug}?done=unchanged", status_code=303)
            number = new_version(conn, p, body + "\n", note, me["id"])
            record(conn, me["org_id"], me["id"], "policy.version", f"policy:{p['id']}", {"version": number, "note": note})
        return RedirectResponse(f"/policies/{slug}?done=saved", status_code=303)

    # ------------------------------------------------------------------ trust center, the admin side

    def manage_or_403(me: dict) -> None:
        if me["role"] not in CAN_MANAGE:
            raise HTTPException(status_code=403, detail="Only a company owner or admin changes the trust center.")

    def trust_crumbs(*rest):
        return [{"label": "Trust center", "href": "/trust" if rest else None}, *({"label": r} for r in rest)]

    @app.get("/trust", response_class=HTMLResponse)
    def trust_overview(request: Request):
        with scope(request) as (conn, me):
            return page(
                request, "trust.html", conn, me, "trust", crumbs=trust_crumbs(), tp=page_of(conn), entry=directory_entry(conn),
                n=trust_counts(conn), views=views_recent(conn), pending=requests_of(conn, "pending")[:5], can_manage=me["role"] in CAN_MANAGE,
            )

    @app.get("/trust/settings", response_class=HTMLResponse)
    def trust_settings(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            entry = directory_entry(conn)
            return page(
                request, "trust_settings.html", conn, me, "trust_settings", crumbs=trust_crumbs("Settings"), tp=page_of(conn), entry=entry,
                default_slug=me["org_slug"], saved=bool(saved), can_manage=me["role"] in CAN_MANAGE,
            )

    @app.post("/trust/settings")
    async def trust_settings_save(request: Request):
        form = await request.form()
        slug = field(form, "slug", 64).lower()
        if not SLUG.match(slug) or slug in RESERVED_SLUGS:
            raise HTTPException(status_code=400, detail="The public address is 3 to 62 lowercase letters, digits or hyphens, and not a word the app uses.")
        contact_email = field(form, "contact_email", 120)
        if contact_email and not EMAIL.match(contact_email):
            raise HTTPException(status_code=400, detail="The contact email does not look like an address.")
        try:
            access_days = int(str(form.get("access_days", "365")).strip() or 365)
        except ValueError:
            raise HTTPException(status_code=400, detail="Access days is a number.") from None
        if not 1 <= access_days <= 730:
            raise HTTPException(status_code=400, detail="Access lasts between 1 and 730 days.")
        values = {
            "headline": field(form, "headline", 160) or None, "statement": field(form, "statement", 8000) or None,
            "contact_name": field(form, "contact_name", 80) or None, "contact_email": contact_email or None,
            "show_controls": "show_controls" in form, "nda_text": field(form, "nda_text", 4000) or None, "access_days": access_days,
            "auto": lines(str(form.get("auto_approve_domains", ""))), "blocked": lines(str(form.get("blocked_domains", ""))),
        }
        enabled = "enabled" in form
        with scope(request) as (conn, me):
            manage_or_403(me)
            page_of(conn)
            try:
                if directory_entry(conn):
                    conn.execute(text("UPDATE trust_directory SET slug = :slug, enabled = :on WHERE organization_id = app_org()"), {"slug": slug, "on": enabled})
                else:
                    conn.execute(text("INSERT INTO trust_directory (slug, organization_id, enabled) VALUES (:slug, :org, :on)"), {"slug": slug, "org": me["org_id"], "on": enabled})
            except IntegrityError:
                raise HTTPException(status_code=409, detail="That public address is taken by another company. Pick another.") from None
            conn.execute(
                text(
                    "UPDATE trust_pages SET headline = :headline, statement = :statement, contact_name = :contact_name, contact_email = :contact_email, "
                    "show_controls = :show_controls, nda_text = :nda_text, access_days = :access_days, auto_approve_domains = :auto, blocked_domains = :blocked, "
                    "updated_at = now() WHERE organization_id = app_org()"
                ),
                values,
            )
            record(conn, me["org_id"], me["id"], "trust.settings", f"trust:{slug}", {"enabled": enabled, "slug": slug})
        return RedirectResponse("/trust/settings?saved=1", status_code=303)

    def approved_policies(conn):
        return conn.execute(text("SELECT id, title, template_id FROM policies WHERE status = 'approved' ORDER BY template_id, title")).mappings().all()

    @app.get("/trust/documents", response_class=HTMLResponse)
    def trust_documents(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            folders = folders_of(conn)
            return page(
                request, "trust_documents.html", conn, me, "trust_documents", crumbs=trust_crumbs("Documents"), folders=folders,
                groups=grouped(documents_of(conn)), policies=approved_policies(conn), kinds=DOCUMENT_KINDS, visibilities=VISIBILITIES,
                saved=saved, can_manage=me["role"] in CAN_MANAGE,
            )

    @app.post("/trust/folders")
    async def trust_folder_create(request: Request):
        form = await request.form()
        name = field(form, "name", 80)
        if not name:
            raise HTTPException(status_code=400, detail="A folder needs a name.")
        with scope(request) as (conn, me):
            manage_or_403(me)
            position = len(folders_of(conn))
            conn.execute(text("INSERT INTO trust_folders (organization_id, name, position) VALUES (:org, :name, :pos)"), {"org": me["org_id"], "name": name, "pos": position})
            record(conn, me["org_id"], me["id"], "trust.folder", "trust:folders", {"name": name})
        return RedirectResponse("/trust/documents?saved=folder", status_code=303)

    def document_fields(form, conn) -> dict:
        title = field(form, "title", 160)
        if not title:
            raise HTTPException(status_code=400, detail="A document needs a title.")
        kind = choice(form, "kind", DOCUMENT_KINDS, "link")
        visibility = choice(form, "visibility", VISIBILITIES, "private")
        url = field(form, "url", 400)
        if url and not url.startswith(("https://", "http://")):
            raise HTTPException(status_code=400, detail="The link must start with https://.")
        folder = an_id(form, "folder", {f["id"] for f in folders_of(conn)})
        policy = an_id(form, "policy", {p["id"] for p in approved_policies(conn)})
        if kind == "link" and not url:
            raise HTTPException(status_code=400, detail="A link document needs its address.")
        if kind == "policy":
            if policy is None:
                raise HTTPException(status_code=400, detail="Pick one of the approved policies.")
            if visibility == "public":
                raise HTTPException(status_code=400, detail="Policy text is shared on request, after the NDA and an approval, never publicly.")
        return {
            "title": title, "description": field(form, "description", 600) or None, "kind": kind, "visibility": visibility,
            "url": url if kind == "link" else None, "policy": str(policy) if kind == "policy" else None, "folder": str(folder) if folder else None,
        }

    @app.post("/trust/documents")
    async def trust_document_create(request: Request):
        form = await request.form()
        with scope(request) as (conn, me):
            manage_or_403(me)
            f = document_fields(form, conn)
            conn.execute(
                text(
                    "INSERT INTO trust_documents (organization_id, folder_id, title, description, visibility, kind, url, policy_id, position) "
                    "VALUES (:org, :folder, :title, :description, :visibility, :kind, :url, :policy, (SELECT count(*) FROM trust_documents))"
                ),
                {**f, "org": me["org_id"]},
            )
            record(conn, me["org_id"], me["id"], "trust.document", "trust:documents", {"title": f["title"], "visibility": f["visibility"]})
        return RedirectResponse("/trust/documents?saved=document", status_code=303)

    @app.post("/trust/documents/policies")
    def trust_documents_from_policies(request: Request):
        """Every approved policy that is not on the page yet, on request, in a Policies folder."""
        with scope(request) as (conn, me):
            manage_or_403(me)
            folder = next((f["id"] for f in folders_of(conn) if f["name"].lower() == "policies"), None)
            if folder is None:
                folder = conn.execute(
                    text("INSERT INTO trust_folders (organization_id, name, position) VALUES (:org, 'Policies', (SELECT count(*) FROM trust_folders)) RETURNING id"),
                    {"org": me["org_id"]},
                ).scalar()
            have = {d["policy_id"] for d in documents_of(conn) if d["policy_id"]}
            added = 0
            for p in approved_policies(conn):
                if p["id"] in have:
                    continue
                conn.execute(
                    text(
                        "INSERT INTO trust_documents (organization_id, folder_id, title, visibility, kind, policy_id, position) "
                        "VALUES (:org, :folder, :title, 'on_request', 'policy', :policy, (SELECT count(*) FROM trust_documents))"
                    ),
                    {"org": me["org_id"], "folder": str(folder), "title": p["title"], "policy": str(p["id"])},
                )
                added += 1
            record(conn, me["org_id"], me["id"], "trust.document", "trust:documents", {"policies_added": added})
        return RedirectResponse("/trust/documents?saved=policies", status_code=303)

    @app.post("/trust/documents/{document_id}")
    async def trust_document_edit(request: Request, document_id: UUID):
        form = await request.form()
        with scope(request) as (conn, me):
            manage_or_403(me)
            current = next((d for d in documents_of(conn) if d["id"] == document_id), None)
            if current is None:
                raise HTTPException(status_code=404, detail="No such document.")
            # The kind and, for a policy document, the policy do not change; make a new document instead.
            form = dict(form)
            form["kind"] = current["kind"]
            if current["kind"] == "policy":
                form["policy"] = str(current["policy_id"])
            f = document_fields(form, conn)
            conn.execute(
                text("UPDATE trust_documents SET folder_id = :folder, title = :title, description = :description, visibility = :visibility, url = :url, updated_at = now() WHERE id = :id"),
                {**f, "id": str(document_id)},
            )
            record(conn, me["org_id"], me["id"], "trust.document", f"trust_document:{document_id}", {"title": f["title"], "visibility": f["visibility"]})
        return RedirectResponse("/trust/documents?saved=document", status_code=303)

    @app.get("/trust/questions", response_class=HTMLResponse)
    def trust_questions(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            return page(request, "trust_questions.html", conn, me, "trust_questions", crumbs=trust_crumbs("Questions"), questions=questions_of(conn), saved=bool(saved), can_manage=me["role"] in CAN_MANAGE)

    def question_fields(form) -> dict:
        question, answer = field(form, "question", 300), field(form, "answer", 4000)
        if not question or not answer:
            raise HTTPException(status_code=400, detail="A question needs its text and an answer.")
        return {"category": field(form, "category", 60) or None, "question": question, "answer": answer, "published": "published" in form}

    @app.post("/trust/questions")
    async def trust_question_create(request: Request):
        form = await request.form()
        f = question_fields(form)
        with scope(request) as (conn, me):
            manage_or_403(me)
            conn.execute(
                text("INSERT INTO trust_questions (organization_id, category, question, answer, published, position) VALUES (:org, :category, :question, :answer, :published, (SELECT count(*) FROM trust_questions))"),
                {**f, "org": me["org_id"]},
            )
            record(conn, me["org_id"], me["id"], "trust.question", "trust:questions", {"question": f["question"]})
        return RedirectResponse("/trust/questions?saved=1", status_code=303)

    @app.post("/trust/questions/{question_id}")
    async def trust_question_edit(request: Request, question_id: UUID):
        form = await request.form()
        f = question_fields(form)
        with scope(request) as (conn, me):
            manage_or_403(me)
            result = conn.execute(
                text("UPDATE trust_questions SET category = :category, question = :question, answer = :answer, published = :published, updated_at = now() WHERE id = :id"),
                {**f, "id": str(question_id)},
            )
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="No such question.")
            record(conn, me["org_id"], me["id"], "trust.question", f"trust_question:{question_id}", {"published": f["published"]})
        return RedirectResponse("/trust/questions?saved=1", status_code=303)

    @app.get("/trust/subprocessors", response_class=HTMLResponse)
    def trust_subprocessors(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            return page(request, "trust_subprocessors.html", conn, me, "trust_subprocessors", crumbs=trust_crumbs("Subprocessors"), subprocessors=subprocessors_of(conn), saved=bool(saved), can_manage=me["role"] in CAN_MANAGE)

    def subprocessor_fields(form) -> dict:
        name, purpose = field(form, "name", 120), field(form, "purpose", 300)
        if not name or not purpose:
            raise HTTPException(status_code=400, detail="A subprocessor needs a name and what it does for you.")
        url = field(form, "url", 400)
        if url and not url.startswith(("https://", "http://")):
            raise HTTPException(status_code=400, detail="The link must start with https://.")
        return {"name": name, "purpose": purpose, "location": field(form, "location", 120) or None, "url": url or None}

    @app.post("/trust/subprocessors")
    async def trust_subprocessor_create(request: Request):
        form = await request.form()
        f = subprocessor_fields(form)
        with scope(request) as (conn, me):
            manage_or_403(me)
            conn.execute(
                text("INSERT INTO trust_subprocessors (organization_id, name, purpose, location, url, position) VALUES (:org, :name, :purpose, :location, :url, (SELECT count(*) FROM trust_subprocessors))"),
                {**f, "org": me["org_id"]},
            )
            record(conn, me["org_id"], me["id"], "trust.subprocessor", "trust:subprocessors", {"name": f["name"]})
        return RedirectResponse("/trust/subprocessors?saved=1", status_code=303)

    @app.post("/trust/subprocessors/{subprocessor_id}")
    async def trust_subprocessor_edit(request: Request, subprocessor_id: UUID):
        form = await request.form()
        f = subprocessor_fields(form)
        with scope(request) as (conn, me):
            manage_or_403(me)
            result = conn.execute(
                text("UPDATE trust_subprocessors SET name = :name, purpose = :purpose, location = :location, url = :url, updated_at = now() WHERE id = :id"),
                {**f, "id": str(subprocessor_id)},
            )
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="No such subprocessor.")
            record(conn, me["org_id"], me["id"], "trust.subprocessor", f"trust_subprocessor:{subprocessor_id}", {"name": f["name"]})
        return RedirectResponse("/trust/subprocessors?saved=1", status_code=303)

    @app.get("/trust/updates", response_class=HTMLResponse)
    def trust_updates(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            n = trust_counts(conn)
            return page(request, "trust_updates.html", conn, me, "trust_updates", crumbs=trust_crumbs("Updates"), updates=updates_of(conn), subscribers=n["subscribers"], today=date.today(), saved=bool(saved), can_manage=me["role"] in CAN_MANAGE)

    @app.post("/trust/updates")
    async def trust_update_create(request: Request):
        form = await request.form()
        title = field(form, "title", 160)
        if not title:
            raise HTTPException(status_code=400, detail="An update needs a title.")
        body = field(form, "body", 4000) or None
        published_on = a_date(form, "published_on") or date.today()
        with scope(request) as (conn, me):
            manage_or_403(me)
            conn.execute(
                text("INSERT INTO trust_updates (organization_id, title, body, published_on, created_by) VALUES (:org, :title, :body, :on, :by)"),
                {"org": me["org_id"], "title": title, "body": body, "on": published_on, "by": me["id"]},
            )
            record(conn, me["org_id"], me["id"], "trust.update", "trust:updates", {"title": title})
        return RedirectResponse("/trust/updates?saved=1", status_code=303)

    @app.get("/trust/requests", response_class=HTMLResponse)
    def trust_requests(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            return page(request, "trust_requests.html", conn, me, "trust_requests", crumbs=trust_crumbs("Access requests"), requests=requests_of(conn), tp=page_of(conn), saved=saved, can_manage=me["role"] in CAN_MANAGE, today=date.today())

    @app.post("/trust/requests/{request_id}/{decision}", response_class=HTMLResponse)
    def trust_request_decide(request: Request, request_id: UUID, decision: str):
        if decision not in ("approve", "deny"):
            raise HTTPException(status_code=404, detail="No such action.")
        with scope(request) as (conn, me):
            manage_or_403(me)
            req = get_request(conn, request_id)
            if req is None:
                raise HTTPException(status_code=404, detail="No such request.")
            if req["status"] != "pending":
                raise HTTPException(status_code=409, detail="This request was already decided.")
            key = decide_request(conn, req, approve=decision == "approve", by=me["id"], page=page_of(conn))
            record(conn, me["org_id"], me["id"], f"trust.request.{decision}", f"trust_request:{request_id}", {"email": req["email"]})
            if decision == "deny":
                return RedirectResponse("/trust/requests?saved=denied", status_code=303)
            # The key is shown once, on this response, and never put in a URL or a log.
            entry = directory_entry(conn)
            link = f"{str(request.base_url).rstrip('/')}/trust/{entry['slug']}?key={key}" if entry else None
            return page(
                request, "trust_requests.html", conn, me, "trust_requests", crumbs=trust_crumbs("Access requests"), requests=requests_of(conn), tp=page_of(conn),
                issued=get_request(conn, request_id), link=link, can_manage=True, today=date.today(),
            )

    # ------------------------------------------------------------------ trust center, the public page

    def public_org(slug: str) -> UUID:
        if slug in RESERVED_SLUGS:
            raise HTTPException(status_code=404, detail="No such page.")
        with engine.begin() as conn:  # no organization context: trust_directory is readable by design
            org_id = resolve_slug(conn, slug)
        if org_id is None:
            raise HTTPException(status_code=404, detail="No such page.")
        return org_id

    def public_context(conn, slug: str, key: str | None) -> dict:
        tp = conn.execute(text("SELECT * FROM trust_pages WHERE organization_id = app_org()")).mappings().first()
        if tp is None:
            raise HTTPException(status_code=404, detail="No such page.")
        org = conn.execute(text("SELECT name FROM organizations WHERE id = app_org()")).mappings().first()
        access = access_for_key(conn, key)
        # On-request documents are listed by title for everyone (that is what a visitor asks for);
        # only the link to open one needs the key. Private documents never leave the admin side.
        docs = documents_of(conn, visible_to=("public", "on_request"))
        on_request = sum(1 for d in docs if d["visibility"] == "on_request")
        summary = None
        if tp["show_controls"]:
            statuses = control_statuses(conn)
            runs = runs_of(conn, 1)
            summary = {"controls": len(statuses), "areas": len({c.domain for c in statuses}), "last_scan": runs[0]["started_at"] if runs else None}
        return {
            "slug": slug, "tp": {**tp, "statement_html": to_html(tp["statement"]), "nda_html": to_html(tp["nda_text"])}, "company": org["name"].replace(" (sample)", ""),
            "access": access, "key": key if access else None, "groups": grouped(docs), "on_request_count": on_request,
            "questions": questions_of(conn, published_only=True), "subprocessors": subprocessors_of(conn), "updates": updates_of(conn, 10), "summary": summary,
        }

    @app.get("/trust/{slug}", response_class=HTMLResponse)
    def trust_public(request: Request, slug: str, key: str | None = None, subscribed: str | None = None):
        org_id = public_org(slug)
        with org_scope(engine, org_id) as conn:
            context = public_context(conn, slug, key)
            count_trust_view(conn, org_id)
        return render(request, "trust_public.html", me=None, subscribed=bool(subscribed), **context)

    @app.get("/trust/{slug}/documents/{document_id}", response_class=HTMLResponse)
    def trust_public_document(request: Request, slug: str, document_id: UUID, key: str | None = None):
        org_id = public_org(slug)
        with org_scope(engine, org_id) as conn:
            access = access_for_key(conn, key)
            doc = next((d for d in documents_of(conn, visible_to=("public", "on_request") if access else ("public",)) if d["id"] == document_id), None)
            if doc is None:
                raise HTTPException(status_code=404, detail="No such document, or it needs an access key.")
            if doc["kind"] == "link":
                return RedirectResponse(doc["url"], status_code=303)
            version = version_of(conn, doc["policy_id"], doc["policy_version"]) if doc["policy_status"] == "approved" else None
            if version is None:
                raise HTTPException(status_code=404, detail="This policy is not approved right now.")
            html, outline = render_policy(version["body"])
            org = conn.execute(text("SELECT name FROM organizations WHERE id = app_org()")).mappings().first()
        return render(request, "trust_document.html", me=None, slug=slug, key=key, doc=doc, document=html, outline=outline, access=access, company=org["name"].replace(" (sample)", ""))

    @app.post("/trust/{slug}/request", response_class=HTMLResponse)
    async def trust_public_request(request: Request, slug: str):
        org_id = public_org(slug)
        form = await request.form()
        name, email = field(form, "name", 80), field(form, "email", 120).lower()
        company, reason = field(form, "company", 120) or None, field(form, "reason", 1000) or None
        nda_accepted = "nda" in form
        with org_scope(engine, org_id) as conn:
            tp = page_of(conn)
            errors = []
            if not name:
                errors.append("Your name.")
            if not EMAIL.match(email):
                errors.append("A working email address.")
            if tp["nda_text"] and not nda_accepted:
                errors.append("The agreement box has to be ticked.")
            org = conn.execute(text("SELECT name FROM organizations WHERE id = app_org()")).mappings().first()
            company_name = org["name"].replace(" (sample)", "")
            if errors:
                return render(request, "trust_requested.html", me=None, slug=slug, company=company_name, errors=errors, outcome=None, status_code=400)
            owner = conn.execute(text("SELECT user_id FROM memberships WHERE role = 'owner' ORDER BY created_at LIMIT 1")).scalar()
            try:
                req, key = submit_request(conn, org_id, tp, name=name, email=email, company=company, reason=reason, nda_accepted=nda_accepted, owner_id=owner)
            except PermissionError as exc:
                return render(request, "trust_requested.html", me=None, slug=slug, company=company_name, errors=[str(exc)], outcome="blocked", status_code=403)
            record(conn, org_id, None, "trust.request", f"trust_request:{req['id']}", {"email": email, "status": req["status"]})
            link = f"{str(request.base_url).rstrip('/')}/trust/{slug}?key={key}" if key else None
        return render(request, "trust_requested.html", me=None, slug=slug, company=company_name, errors=[], outcome=req["status"], link=link, expires_on=req["expires_on"], contact=tp["contact_email"])

    @app.post("/trust/{slug}/subscribe")
    async def trust_public_subscribe(request: Request, slug: str):
        org_id = public_org(slug)
        form = await request.form()
        email = field(form, "email", 120).lower()
        if not EMAIL.match(email):
            raise HTTPException(status_code=400, detail="That does not look like an email address.")
        with org_scope(engine, org_id) as conn:
            if subscribe(conn, org_id, email):
                record(conn, org_id, None, "trust.subscribe", "trust:subscribers")
        return RedirectResponse(f"/trust/{slug}?subscribed=1#updates", status_code=303)

    # ------------------------------------------------------------------ the person's own pages

    def preferences_of(conn, me: dict) -> dict:
        """The person's settings row, created with the defaults the first time it is asked for."""
        query = text("SELECT * FROM user_settings WHERE user_id = :u")
        row = conn.execute(query, {"u": me["id"]}).mappings().first()
        if row is None:
            conn.execute(text("INSERT INTO user_settings (user_id) VALUES (:u)"), {"u": me["id"]})
            row = conn.execute(query, {"u": me["id"]}).mappings().first()
        return dict(row)

    @app.get("/account", response_class=HTMLResponse)
    def account(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            prefs = preferences_of(conn, me)
            crumbs = [{"label": "Account", "href": "/account"}, {"label": "Profile"}]
            return page(request, "account.html", conn, me, "account", crumbs=crumbs, prefs=prefs, saved=bool(saved), time_zones=TIME_ZONES)

    @app.post("/account")
    def account_save(request: Request, display_name: str = Form(...), job_title: str = Form(""), time_zone: str = Form(...)):
        name, title = " ".join(display_name.split()), " ".join(job_title.split())
        if not 1 <= len(name) <= 80 or len(title) > 80:
            raise HTTPException(status_code=400, detail="A name is 1 to 80 characters; a title up to 80.")
        if time_zone not in TIME_ZONES:
            raise HTTPException(status_code=400, detail="Pick a time zone from the list.")
        with scope(request) as (conn, me):
            preferences_of(conn, me)
            # WHERE id = the signed-in user: the row policy would let a member rename a colleague, this route does not.
            conn.execute(text("UPDATE users SET display_name = :n, job_title = :t WHERE id = :u"), {"n": name, "t": title or None, "u": me["id"]})
            conn.execute(text("UPDATE user_settings SET time_zone = :tz, updated_at = now() WHERE user_id = :u"), {"tz": time_zone, "u": me["id"]})
            record(conn, me["org_id"], me["id"], "account.profile", f"user:{me['id']}", {"display_name": name, "job_title": title, "time_zone": time_zone})
        return RedirectResponse("/account?saved=1", status_code=303)

    @app.get("/account/security", response_class=HTMLResponse)
    def account_security(request: Request):
        with scope(request) as (conn, me):
            mfa = [{"id": test_id, **row} for test_id, row in latest_results(conn).items() if ".mfa." in test_id]
            signed_in_at = request.session.get("signed_in_at")
            crumbs = [{"label": "Account", "href": "/account"}, {"label": "Security"}]
            return page(
                request, "account_security.html", conn, me, "account_security", crumbs=crumbs,
                mfa=mfa, signed_in_at=datetime.fromisoformat(signed_in_at) if signed_in_at else None, session_hours=8,
            )

    @app.get("/account/notifications", response_class=HTMLResponse)
    def account_notifications(request: Request, saved: str | None = None):
        with scope(request) as (conn, me):
            prefs = preferences_of(conn, me)
            crumbs = [{"label": "Account", "href": "/account"}, {"label": "Notifications"}]
            return page(request, "account_notifications.html", conn, me, "account_notifications", crumbs=crumbs, prefs=prefs, saved=bool(saved))

    @app.post("/account/notifications")
    async def account_notifications_save(request: Request):
        form = await request.form()
        # A checkbox that is off is simply absent from the form, so "present" means on.
        choices = {key: key in form for key in NOTIFICATION_KEYS}
        with scope(request) as (conn, me):
            preferences_of(conn, me)
            sets = ", ".join(f"{key} = :{key}" for key in NOTIFICATION_KEYS)
            conn.execute(text(f"UPDATE user_settings SET {sets}, updated_at = now() WHERE user_id = :u"), {**choices, "u": me["id"]})
            record(conn, me["org_id"], me["id"], "account.notifications", f"user:{me['id']}", choices)
        return RedirectResponse("/account/notifications?saved=1", status_code=303)

    @app.get("/healthz", include_in_schema=False)
    def healthz():
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True, "mode": settings.mode}

    return app
