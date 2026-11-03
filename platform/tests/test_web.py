"""The pages, through the HTTP layer, as each sample user."""

from __future__ import annotations

import re

from sqlalchemy import text

from alimi_platform.db import org_scope


def test_pages_need_a_session(client):
    for path in ("/dashboard", "/controls", "/frameworks/insurer", "/monitoring", "/settings", "/audit"):
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 303 and r.headers["location"] == "/login"


def test_picker_lists_the_three_sample_orgs(client):
    r = client.get("/login")
    assert r.status_code == 200
    for name in ("Saltmarsh Payroll", "Harbor Dental", "Alimi"):
        assert name in r.text
    assert "Mock mode" in r.text


def test_picker_rejects_made_up_users(client, orgs):
    r = client.post("/login", data={"org_id": str(orgs["saltmarsh"].id), "user_id": str(orgs["harbor-dental"].users[0].id)})
    assert r.status_code == 400


def test_dashboard_shows_only_own_company(signed_in):
    client = signed_in("saltmarsh")
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Saltmarsh Payroll" in r.text
    assert "Harbor Dental" not in r.text and "harbordental" not in r.text
    assert "mock-token" not in r.text and "gAAAAA" not in r.text


def test_insurer_page_and_controls(signed_in):
    client = signed_in("harbor-dental")
    r = client.get("/frameworks/insurer")
    assert r.status_code == 200 and "Multi-factor authentication" in r.text
    r = client.get("/controls/CTL-09")
    assert r.status_code == 200 and "Rule" in r.text
    assert client.get("/controls/NOPE").status_code == 404


def test_frameworks_page_lists_the_catalog(signed_in):
    r = signed_in("alimi").get("/frameworks")
    assert r.status_code == 200
    assert "Posture Score" in r.text and "not an accredited framework" in r.text


def test_scan_button_runs_and_returns_a_fragment(signed_in, orgs):
    client = signed_in("saltmarsh")
    org = orgs["saltmarsh"]
    r = client.post(f"/integrations/{org.integration_id}/scan", headers={"HX-Request": "true"})
    assert r.status_code == 200 and "Scan finished" in r.text
    run_id = re.search(r'/scans/([0-9a-f-]{36})', r.text).group(1)
    detail = client.get(f"/scans/{run_id}")
    assert detail.status_code == 200 and "What the check read" in detail.text


def test_cannot_scan_or_view_another_orgs_objects(signed_in, orgs, app_engine):
    client = signed_in("saltmarsh")
    harbor = orgs["harbor-dental"]
    assert client.post(f"/integrations/{harbor.integration_id}/scan").status_code == 404
    with org_scope(app_engine, harbor.id) as conn:
        harbor_run = conn.execute(text("SELECT id FROM scan_runs LIMIT 1")).scalar()
    assert client.get(f"/scans/{harbor_run}").status_code == 404


def test_tampered_session_org_is_rejected(signed_in, orgs, client):
    # Sign in as Saltmarsh, then forge a cookie claiming Harbor Dental with the same user.
    from itsdangerous import TimestampSigner
    import base64, json

    signed_in("saltmarsh")
    payload = {"user_id": str(orgs["saltmarsh"].users[0].id), "org_id": str(orgs["harbor-dental"].id)}
    data = base64.b64encode(json.dumps(payload).encode())
    cookie = TimestampSigner("test-session-secret").sign(data).decode()
    client.cookies.set("alimi_session", cookie)
    r = client.get("/dashboard", follow_redirects=False)
    # Validly signed, but the user is not a member of Harbor Dental: back to the picker.
    assert r.status_code == 303 and r.headers["location"] == "/login"


def test_audit_log_records_logins(signed_in):
    client = signed_in("alimi")
    r = client.get("/audit")
    assert r.status_code == 200 and "login.mock" in r.text
