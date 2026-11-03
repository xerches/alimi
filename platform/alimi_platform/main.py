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
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Engine, text
from starlette.middleware.sessions import SessionMiddleware

from .audit import record
from .catalog import domain_labels
from .config import ConfigError, Settings, load_settings
from .crypto import install_log_redaction
from .db import make_engine, org_scope
from .scans import ScanRefused, run_scan
from .seed import SAMPLE_ORGS
from .nav import shell
from .status import STATUSES, control_statuses, latest_results, requirement_statuses

HERE = Path(__file__).parent
log = logging.getLogger("alimi.platform")


class NotSignedIn(Exception):
    pass


def create_app(settings: Settings | None = None, engine: Engine | None = None) -> FastAPI:
    settings = settings or load_settings()
    if not settings.is_mock:  # load_settings already refuses; this guards a hand-built Settings
        raise ConfigError("The mock-mode user picker only loads when ALIMI_MODE=mock.")
    install_log_redaction()
    engine = engine or make_engine(settings.database_url)

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
                    "SELECT u.id, u.display_name, m.role, o.id AS org_id, o.name AS org_name "
                    "FROM memberships m JOIN users u ON u.id = m.user_id JOIN organizations o ON o.id = m.organization_id "
                    "WHERE m.user_id = :u"
                ),
                {"u": user_id},
            ).mappings().first()
            if me is None:
                # The membership is gone (or the cookie names an org the user is not in).
                request.session.clear()
                raise NotSignedIn()
            yield conn, dict(me)

    def render(request: Request, name: str, **context) -> HTMLResponse:
        return templates.TemplateResponse(request, name, context)

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
        request.session.update({"user_id": user_id, "org_id": org_id})
        return RedirectResponse("/dashboard", status_code=303)

    @app.post("/logout")
    def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    # ------------------------------------------------------------------ pages

    def page(request: Request, name: str, conn, me: dict, key: str, *, item: str | None = None, crumbs=(), controls=None, **context) -> HTMLResponse:
        """Render a page inside the shell: strip badges, the column and the current item come from this org's rows."""
        if controls is None:
            controls = control_statuses(conn)
        context.setdefault("controls", controls)
        return render(request, name, me=me, shell=shell(conn, settings, key, item, controls), crumbs=list(crumbs), **context)

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

    @app.get("/healthz", include_in_schema=False)
    def healthz():
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True, "mode": settings.mode}

    return app
