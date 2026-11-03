"""The person's own pages: profile, security, notifications. Each one shows and changes the signed-in
person's rows only."""

from __future__ import annotations

from sqlalchemy import text

from alimi_platform.db import org_scope


def test_profile_shows_and_saves_name_title_and_time_zone(signed_in, orgs, app_engine):
    client = signed_in("saltmarsh", 1)  # Theo Marsh
    r = client.get("/account")
    assert r.status_code == 200
    assert 'value="Theo Marsh"' in r.text and 'value="Operations lead"' in r.text
    assert 'value="theo.marsh@saltmarsh.example" readonly' in r.text
    assert "Saved." not in r.text

    r = client.post("/account", data={"display_name": "  Theo  Marsh-Whitcomb ", "job_title": "Head of operations", "time_zone": "America/Chicago"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/account?saved=1"
    r = client.get("/account?saved=1")
    assert "Saved." in r.text and 'value="Theo Marsh-Whitcomb"' in r.text and 'value="Head of operations"' in r.text
    assert 'value="America/Chicago" selected' in r.text
    assert "Viewing as Theo Marsh-Whitcomb, Head of operations" in r.text and ">TM<" in r.text

    # Only Theo changed; Dana's row is as it was.
    with org_scope(app_engine, orgs["saltmarsh"].id, orgs["saltmarsh"].users[0].id) as conn:
        names = dict(conn.execute(text("SELECT email, display_name FROM users ORDER BY email")).all())
    assert names["dana.whitcomb@saltmarsh.example"] == "Dana Whitcomb"
    assert names["theo.marsh@saltmarsh.example"] == "Theo Marsh-Whitcomb"
    assert "account.profile" in client.get("/audit").text


def test_profile_rejects_bad_input(signed_in):
    client = signed_in("harbor-dental")
    assert client.post("/account", data={"display_name": "   ", "job_title": "", "time_zone": "America/New_York"}).status_code == 400
    assert client.post("/account", data={"display_name": "Priya", "job_title": "", "time_zone": "Mars/Olympus"}).status_code == 400
    assert client.post("/account", data={"display_name": "x" * 81, "job_title": "", "time_zone": "America/New_York"}).status_code == 400


def test_notifications_are_kept_per_person(signed_in, orgs, app_engine):
    client = signed_in("harbor-dental", 1)  # Sam Okafor
    r = client.get("/account/notifications")
    assert r.status_code == 200 and r.text.count("checked") == 5

    r = client.post("/account/notifications", data={"notify_failed_tests": "on", "notify_weekly_digest": "on"}, follow_redirects=False)
    assert r.status_code == 303
    r = client.get("/account/notifications?saved=1")
    assert "Saved." in r.text and r.text.count("checked") == 2
    assert 'name="notify_failed_tests" checked' in r.text and 'name="notify_renewals">' in r.text

    sam, priya = orgs["harbor-dental"].users[1], orgs["harbor-dental"].users[0]
    # Sam sees one settings row: their own. Priya, in the same company, sees none of Sam's.
    with org_scope(app_engine, orgs["harbor-dental"].id, sam.id) as conn:
        rows = conn.execute(text("SELECT user_id, notify_renewals FROM user_settings")).all()
    assert rows == [(sam.id, False)]
    with org_scope(app_engine, orgs["harbor-dental"].id, priya.id) as conn:
        assert conn.execute(text("SELECT count(*) FROM user_settings")).scalar() == 0
    assert "account.notifications" in client.get("/audit").text


def test_security_page_reads_the_tenant_mfa_check(signed_in):
    client = signed_in("saltmarsh")
    r = client.get("/account/security")
    assert r.status_code == 200
    assert "Multi-factor authentication" in r.text and "Signed in" in r.text
    assert "mfa" in r.text.lower() and 'action="/logout"' in r.text
