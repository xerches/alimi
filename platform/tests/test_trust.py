"""The trust center: the public page shows only what is marked public, the access request flow
with the agreement, auto-approve and blocked domains, the once-shown access key and its expiry,
the admin pages, and that one company's trust center is invisible to another."""

from __future__ import annotations

import re
from datetime import date, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from alimi_platform.db import org_scope

STRIP = re.compile(r'<nav class="strip".*?</nav>', re.S)
COLUMN = re.compile(r'<aside class="column".*?</aside>', re.S)
KEY_LINK = re.compile(r"/trust/[a-z0-9-]+\?key=([A-Za-z0-9_-]+)")


def test_public_page_shows_public_items_only(client):
    r = client.get("/trust/saltmarsh")
    assert r.status_code == 200
    assert 'class="shell" data-bare' in r.text   # no strip, no top bar: a visitor has no account
    assert "Security at Saltmarsh Payroll" in r.text and "How we protect the payroll data" in r.text
    assert "Cyber insurance certificate" in r.text and "Open ↗" in r.text
    assert "Latest insurer-ready report" in r.text and "Request" in r.text       # on request: listed, not linked
    assert "insurer-report.pdf" not in r.text and "Penetration test" not in r.text and "pentest" not in r.text
    assert "Acceptable Use Policy" in r.text and "Version 1" in r.text            # a policy on request: title only
    assert "Do you require multi-factor authentication?" in r.text and "Microsoft 365" in r.text
    assert "Trust page published" in r.text and "Monitored by Alimi:" in r.text and "40 controls" in r.text
    assert "Request access" in r.text and "I agree" in r.text
    assert "failing" not in r.text.lower()   # the page never says which controls fail
    assert client.get("/trust/no-such-company").status_code == 404
    assert client.get("/trust/settings", follow_redirects=False).status_code == 303   # reserved: the admin side, behind the session


def test_public_document_links_open_and_private_ones_do_not(client, orgs, app_engine):
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        docs = {r["title"]: r for r in conn.execute(text("SELECT id, title, visibility FROM trust_documents")).mappings()}
    r = client.get(f"/trust/saltmarsh/documents/{docs['Cyber insurance certificate']['id']}", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].endswith("certificate-of-insurance.pdf")
    assert client.get(f"/trust/saltmarsh/documents/{docs['Latest insurer-ready report']['id']}").status_code == 404
    assert client.get(f"/trust/saltmarsh/documents/{docs['Penetration test summary']['id']}").status_code == 404
    assert client.get(f"/trust/saltmarsh/documents/{docs['Acceptable Use Policy']['id']}").status_code == 404
    # Harbor Dental's document ids do not exist under Saltmarsh's page.
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        harbor_doc = conn.execute(text("SELECT id FROM trust_documents WHERE visibility = 'public' LIMIT 1")).scalar()
    assert client.get(f"/trust/saltmarsh/documents/{harbor_doc}").status_code == 404


def test_request_then_approve_opens_the_documents_until_expiry(client, signed_in, orgs, app_engine):
    r = client.post("/trust/saltmarsh/request", data={"name": "Jo Park", "email": "jo.park@northstar.example", "company": "Northstar Credit Union", "reason": "Vendor review.", "nda": "on"})
    assert r.status_code == 200 and "Request sent" in r.text and "?key=" not in r.text
    # Without the agreement box, or without a real address, nothing is recorded.
    assert client.post("/trust/saltmarsh/request", data={"name": "Jo", "email": "jo@northstar.example"}).status_code == 400
    assert client.post("/trust/saltmarsh/request", data={"name": "Jo", "email": "not-an-address", "nda": "on"}).status_code == 400

    dana = signed_in("saltmarsh", 0)
    tasks = dana.get("/tasks").text
    assert "Trust center: access request from Jo Park (Northstar Credit Union)" in tasks
    requests_page = dana.get("/trust/requests")
    assert "Jo Park" in requests_page.text and "Vendor review." in requests_page.text and ">Approve<" in requests_page.text
    strip = STRIP.search(requests_page.text).group(0)
    assert re.search(r'strip-badge" data-tone="neutral" aria-label="\d+ access requests waiting"', strip)
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        req_id = conn.execute(text("SELECT id FROM trust_access_requests WHERE email = 'jo.park@northstar.example'")).scalar()
        assert conn.execute(text("SELECT token_hash FROM trust_access_requests WHERE id = :id"), {"id": req_id}).scalar() is None

    approved = dana.post(f"/trust/requests/{req_id}/approve")
    assert approved.status_code == 200 and "shown once" in approved.text
    key = KEY_LINK.search(approved.text).group(1)
    assert key not in dana.get("/trust/requests").text   # never shown again, never stored
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        stored = conn.execute(text("SELECT token_hash, status, expires_on FROM trust_access_requests WHERE id = :id"), {"id": req_id}).one()
        assert stored.status == "approved" and stored.token_hash != key and stored.expires_on == date.today() + timedelta(days=365)
        assert conn.execute(text("SELECT status FROM tasks WHERE source_kind = 'trust_request' AND source_id = :id"), {"id": str(req_id)}).scalar() == "done"
    assert dana.post(f"/trust/requests/{req_id}/approve").status_code == 409

    opened = client.get(f"/trust/saltmarsh?key={key}")
    assert "Shared with Jo Park, Northstar Credit Union" in opened.text and "insurer-report.pdf" not in opened.text
    assert "Latest insurer-ready report" in opened.text and f"?key={key}" in opened.text and "Penetration test" not in opened.text
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        policy_doc = conn.execute(text("SELECT id FROM trust_documents WHERE kind = 'policy' ORDER BY position LIMIT 1")).scalar()
        link_doc = conn.execute(text("SELECT id FROM trust_documents WHERE title = 'Latest insurer-ready report'")).scalar()
    doc = client.get(f"/trust/saltmarsh/documents/{policy_doc}?key={key}")
    assert doc.status_code == 200 and "Saltmarsh Payroll Acceptable Use Policy" in doc.text and "Not for further distribution" in doc.text
    r = client.get(f"/trust/saltmarsh/documents/{link_doc}?key={key}", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].endswith("insurer-report.pdf")
    assert client.get(f"/trust/saltmarsh?key=wrong-key").text.count("Shared with") == 0
    assert client.get(f"/trust/harbor-dental?key={key}").text.count("Shared with") == 0   # a key opens one company's page only

    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        conn.execute(text("UPDATE trust_access_requests SET expires_on = :d WHERE id = :id"), {"d": date.today() - timedelta(days=1), "id": req_id})
    assert "Shared with" not in client.get(f"/trust/saltmarsh?key={key}").text
    assert client.get(f"/trust/saltmarsh/documents/{policy_doc}?key={key}").status_code == 404
    audit = dana.get("/audit").text
    assert "trust.request" in audit and "trust.request.approve" in audit


def test_auto_approved_and_blocked_domains(client):
    r = client.post("/trust/saltmarsh/request", data={"name": "Sam Rivera", "email": "sam@saltmarsh.example", "nda": "on"})
    assert r.status_code == 200 and "Access granted" in r.text
    key = KEY_LINK.search(r.text).group(1)
    assert "Shared with Sam Rivera" in client.get(f"/trust/saltmarsh?key={key}").text
    r = client.post("/trust/saltmarsh/request", data={"name": "Nobody", "email": "x@mailinator.com", "nda": "on"})
    assert r.status_code == 403 and "not accepted" in r.text


def test_deny_closes_the_task(client, signed_in, orgs, app_engine):
    client.post("/trust/harbor-dental/request", data={"name": "Lee Chen", "email": "lee@example.org", "nda": "on"})
    priya = signed_in("harbor-dental", 0)
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        req_id = conn.execute(text("SELECT id FROM trust_access_requests WHERE email = 'lee@example.org'")).scalar()
    r = priya.post(f"/trust/requests/{req_id}/deny", follow_redirects=False)
    assert r.status_code == 303 and "Denied" in priya.get("/trust/requests?saved=denied").text
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        assert conn.execute(text("SELECT status FROM tasks WHERE source_kind = 'trust_request' AND source_id = :id"), {"id": str(req_id)}).scalar() == "done"


def test_subscribe_and_views(client, signed_in, orgs, app_engine):
    before = signed_in("alimi").get("/trust").text
    n = int(re.search(r'<p class="big">(\d+)</p>', before).group(1))
    r = client.post("/trust/alimi/subscribe", data={"email": "watch@example.org"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/trust/alimi?subscribed=1#updates"
    assert "Thank you" in client.get("/trust/alimi?subscribed=1").text
    client.post("/trust/alimi/subscribe", data={"email": "watch@example.org"})   # twice is one subscriber
    assert client.post("/trust/alimi/subscribe", data={"email": "nope"}).status_code == 400
    client.get("/trust/alimi")
    after = signed_in("alimi").get("/trust").text
    assert int(re.search(r'<p class="big">(\d+)</p>', after).group(1)) >= n + 3
    with org_scope(app_engine, orgs["alimi"].id) as conn:
        assert conn.execute(text("SELECT count(*) FROM trust_subscribers WHERE email = 'watch@example.org'")).scalar() == 1


def test_admin_settings_switch_the_page_off_and_rename_it(signed_in, client):
    priya = signed_in("harbor-dental", 0)
    settings = priya.get("/trust/settings")
    assert settings.status_code == 200 and 'value="harbor-dental"' in settings.text
    form = {"slug": "harbor-dental-smiles", "headline": "Patient data, kept private", "statement": "We **care**.", "contact_name": "Sam", "contact_email": "sam.okafor@harbordental.example", "nda_text": "", "access_days": "90", "auto_approve_domains": "Partners.example\n\nother.example", "blocked_domains": ""}
    r = priya.post("/trust/settings", data=form, follow_redirects=False)   # no "enabled": the page goes off
    assert r.status_code == 303
    assert client.get("/trust/harbor-dental").status_code == 404 and client.get("/trust/harbor-dental-smiles").status_code == 404
    r = priya.post("/trust/settings", data={**form, "enabled": "on", "show_controls": "on"}, follow_redirects=False)
    assert r.status_code == 303
    public = client.get("/trust/harbor-dental-smiles")
    assert public.status_code == 200 and "Patient data, kept private" in public.text and "<strong>care</strong>" in public.text and "I agree" not in public.text
    assert client.get("/trust/harbor-dental").status_code == 404
    # A request now needs no agreement box, and partners.example is approved at once for 90 days.
    r = client.post("/trust/harbor-dental-smiles/request", data={"name": "Pat", "email": "pat@partners.example"})
    assert r.status_code == 200 and "Access granted" in r.text and (date.today() + timedelta(days=90)).strftime("%b %d, %Y") in r.text
    assert priya.post("/trust/settings", data={**form, "slug": "settings"}).status_code == 400
    assert priya.post("/trust/settings", data={**form, "slug": "saltmarsh"}).status_code == 409   # taken by another company
    assert priya.post("/trust/settings", data={**form, "slug": "Harbor Dental"}).status_code == 400
    r = priya.post("/trust/settings", data={**form, "slug": "harbor-dental", "enabled": "on"}, follow_redirects=False)
    assert r.status_code == 303 and client.get("/trust/harbor-dental").status_code == 200


def test_admin_documents_questions_subprocessors_updates(signed_in, client, orgs, app_engine):
    dana = signed_in("saltmarsh", 0)
    r = dana.post("/trust/folders", data={"name": "Certificates"}, follow_redirects=False)
    assert r.status_code == 303
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        folder = conn.execute(text("SELECT id FROM trust_folders WHERE name = 'Certificates'")).scalar()
        policy = conn.execute(text("SELECT id FROM policies WHERE status = 'approved' AND template_id = 'POL-10'")).scalar()
    r = dana.post("/trust/documents", data={"title": "SOC 2 bridge letter", "kind": "link", "visibility": "public", "url": "https://example.com/bridge.pdf", "folder": str(folder)}, follow_redirects=False)
    assert r.status_code == 303
    assert dana.post("/trust/documents", data={"title": "x", "kind": "link", "visibility": "public", "url": "javascript:alert(1)"}).status_code == 400
    assert dana.post("/trust/documents", data={"title": "x", "kind": "link", "visibility": "public"}).status_code == 400
    assert dana.post("/trust/documents", data={"title": "Logging policy", "kind": "policy", "visibility": "public", "policy": str(policy)}).status_code == 400   # never public
    r = dana.post("/trust/documents", data={"title": "Logging policy", "kind": "policy", "visibility": "on_request", "policy": str(policy)}, follow_redirects=False)
    assert r.status_code == 303
    page = dana.get("/trust/documents")
    assert "Certificates" in page.text and "SOC 2 bridge letter" in page.text and "Logging policy" in page.text
    public = client.get("/trust/saltmarsh")
    assert "SOC 2 bridge letter" in public.text and "Certificates" in public.text and "Logging policy" in public.text
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        doc = conn.execute(text("SELECT id FROM trust_documents WHERE title = 'SOC 2 bridge letter'")).scalar()
    r = dana.post(f"/trust/documents/{doc}", data={"title": "SOC 2 bridge letter (2026)", "visibility": "private", "url": "https://example.com/bridge.pdf", "folder": str(folder)}, follow_redirects=False)
    assert r.status_code == 303 and "SOC 2 bridge letter" not in client.get("/trust/saltmarsh").text
    r = dana.post("/trust/documents/policies", follow_redirects=False)
    assert r.status_code == 303
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        approved = conn.execute(text("SELECT count(*) FROM policies WHERE status = 'approved'")).scalar()
        on_page = conn.execute(text("SELECT count(DISTINCT policy_id) FROM trust_documents WHERE kind = 'policy'")).scalar()
    assert on_page == approved

    r = dana.post("/trust/questions", data={"category": "Data", "question": "Where is our data stored?", "answer": "In the **United States**.", "published": "on"}, follow_redirects=False)
    assert r.status_code == 303 and "Where is our data stored?" in client.get("/trust/saltmarsh").text
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        q = conn.execute(text("SELECT id FROM trust_questions WHERE question = 'Where is our data stored?'")).scalar()
    r = dana.post(f"/trust/questions/{q}", data={"category": "Data", "question": "Where is our data stored?", "answer": "Here."}, follow_redirects=False)   # unpublished
    assert r.status_code == 303 and "Where is our data stored?" not in client.get("/trust/saltmarsh").text
    assert dana.post("/trust/questions", data={"question": "no answer"}).status_code == 400

    r = dana.post("/trust/subprocessors", data={"name": "Backup Co (fictional)", "purpose": "Off-site backups", "location": "Canada", "url": "https://example.com/backupco"}, follow_redirects=False)
    assert r.status_code == 303 and "Backup Co (fictional)" in client.get("/trust/saltmarsh").text
    r = dana.post("/trust/updates", data={"title": "Backup vendor added", "body": "Off-site copies now go to *Backup Co*.", "published_on": date.today().isoformat()}, follow_redirects=False)
    assert r.status_code == 303 and "<em>Backup Co</em>" in client.get("/trust/saltmarsh").text
    for action in ("trust.folder", "trust.document", "trust.question", "trust.subprocessor", "trust.update"):
        assert action in dana.get("/audit").text


def test_a_member_reads_but_does_not_change_the_trust_center(signed_in):
    theo = signed_in("saltmarsh", 1)
    for path in ("/trust", "/trust/settings", "/trust/documents", "/trust/questions", "/trust/subprocessors", "/trust/updates", "/trust/requests"):
        r = theo.get(path)
        assert r.status_code == 200 and "a company owner or admin changes it" in r.text, path
    assert theo.post("/trust/folders", data={"name": "x"}).status_code == 403
    assert theo.post("/trust/questions", data={"question": "x", "answer": "y"}).status_code == 403
    assert theo.post("/trust/settings", data={"slug": "saltmarsh", "access_days": "365"}).status_code == 403


def test_trust_section_sits_in_the_strip_and_the_column(signed_in):
    client = signed_in("saltmarsh")
    r = client.get("/trust/documents")
    assert 'href="/trust" aria-current="page"' in STRIP.search(r.text).group(0)
    column = COLUMN.search(r.text).group(0)
    for label in ("Overview", "Documents", "Questions", "Subprocessors", "Updates", "Access requests", "Settings", "View the public page"):
        assert label in column
    assert 'href="/trust/documents" aria-current="page"' in column and 'href="/trust/saltmarsh"' in column


def test_another_companys_trust_center_is_invisible(signed_in, orgs, app_engine):
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        harbor_req = conn.execute(text("SELECT id FROM trust_access_requests LIMIT 1")).scalar()
        harbor_doc = conn.execute(text("SELECT id FROM trust_documents LIMIT 1")).scalar()
        harbor_q = conn.execute(text("SELECT id FROM trust_questions LIMIT 1")).scalar()
    dana = signed_in("saltmarsh", 0)
    assert dana.post(f"/trust/requests/{harbor_req}/approve").status_code == 404
    assert dana.post(f"/trust/documents/{harbor_doc}", data={"title": "x", "visibility": "public", "url": "https://example.com/x"}).status_code == 404
    assert dana.post(f"/trust/questions/{harbor_q}", data={"question": "x", "answer": "y"}).status_code == 404
    client = dana  # the same test client, now signed in elsewhere
    client.post("/trust/saltmarsh/request", data={"name": "Only At Saltmarsh", "email": "only@unique.example", "nda": "on"})
    assert "Only At Saltmarsh" in signed_in("saltmarsh", 0).get("/trust/requests").text
    assert "Only At Saltmarsh" not in signed_in("harbor-dental").get("/trust/requests").text
    # The public directory is readable from any context, but a company writes only its own row.
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        assert conn.execute(text("SELECT count(*) FROM trust_directory")).scalar() == 3
        assert conn.execute(text("UPDATE trust_directory SET enabled = false WHERE slug = 'harbor-dental'")).rowcount == 0
    with pytest.raises(DBAPIError, match="row-level security"):
        with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
            conn.execute(text("INSERT INTO trust_directory (slug, organization_id, enabled) VALUES ('planted', :org, true)"), {"org": orgs["harbor-dental"].id})
