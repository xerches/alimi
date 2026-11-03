"""The policy module: the library adopted per company with the names filled in, the full text
behind sign-in only, the approve and acknowledge flows, versions, and isolation."""

from __future__ import annotations

import re

from sqlalchemy import text

from alimi_platform.db import org_scope
from alimi_platform.policies import placeholders_left, render

STRIP = re.compile(r'<nav class="strip".*?</nav>', re.S)
COLUMN = re.compile(r'<aside class="column".*?</aside>', re.S)
DOC = re.compile(r'<article class="doc card">(.*?)</article>', re.S)


def test_the_library_is_adopted_for_every_company_with_its_names_filled(signed_in, orgs, app_engine):
    for slug, org in orgs.items():
        with org_scope(app_engine, org.id) as conn:
            rows = conn.execute(text("SELECT template_id, slug, status FROM policies ORDER BY template_id")).all()
            assert len(rows) == 23 and rows[0][0] == "POL-01" and rows[0][1] == "information-security-policy", slug
            bodies = conn.execute(text("SELECT body FROM policy_versions")).scalars().all()
            assert len(bodies) == 23
            for body in bodies:
                assert placeholders_left(body) == [], slug
                assert "TEMPLATE. Adapt before adopting" not in body
            # The Decide task on the Tasks page points at a real page.
            assert any(r[0] == "POL-01" and r[2] == "in_review" for r in rows)
    r = signed_in("saltmarsh").get("/policies")
    assert r.status_code == 200 and "Information Security Policy" in r.text and "Approved of 23" in r.text
    assert r.text.count('class="badge q-approved"') == 10 and r.text.count('class="badge q-in_review"') == 1


def test_the_full_text_shows_only_signed_in(client, signed_in):
    r = client.get("/policies/information-security-policy", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/login"
    assert client.get("/policies/information-security-policy/download", follow_redirects=False).status_code == 303
    r = signed_in("saltmarsh").get("/policies/information-security-policy")
    assert r.status_code == 200
    doc = DOC.search(r.text).group(1)
    assert "Saltmarsh Payroll Information Security Policy" in doc and "{{" not in doc
    assert "Dana Whitcomb" in doc and "Theo Marsh" in doc  # CEO and Security Lead filled from the members
    assert 'id="1-purpose"' in doc and "<h3" in doc and "<h1" not in doc   # headings demoted under the page title
    assert "In this policy" in r.text and 'href="#4-policy-statements"' in r.text
    assert "Awaiting approval" in r.text and "Approve version 1" in r.text   # Dana is the owner: she can approve
    assert "Requirements this policy answers" in r.text and "CC1.1" in r.text and "SOC 2" in r.text
    assert "Controls that carry it out" in r.text and 'href="/controls/CTL-01"' in r.text
    assert "Download Markdown" in r.text


def test_download_is_the_markdown_in_force(signed_in):
    r = signed_in("alimi").get("/policies/acceptable-use-policy/download")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/markdown")
    assert 'filename="acceptable-use-policy-v1.md"' in r.headers["content-disposition"]
    assert "# Alimi Acceptable Use Policy" in r.text and "{{" not in r.text


def test_approve_then_acknowledge_then_a_new_version_starts_over(signed_in, orgs):
    dana = signed_in("saltmarsh", 0)
    slug = "information-security-policy"
    r = dana.post(f"/policies/{slug}/approve", follow_redirects=False)
    assert r.status_code == 303
    page = dana.get(f"/policies/{slug}?done=approved")
    assert 'class="badge q-approved"' in page.text and "next review" in page.text and "0 of 2" in page.text
    assert "Acknowledge: I have read this policy" in page.text
    r = dana.post(f"/policies/{slug}/acknowledge", follow_redirects=False)
    assert r.status_code == 303
    page = dana.get(f"/policies/{slug}")
    assert "You acknowledged version 1" in page.text and "1 of 2" in page.text
    assert dana.post(f"/policies/{slug}/acknowledge", follow_redirects=False).status_code == 303  # twice is harmless
    assert slug not in dana.get("/policies?view=mine").text.split("<table", 1)[-1]

    theo = signed_in("saltmarsh", 1)
    mine = theo.get("/policies?view=mine")
    assert f'href="/policies/{slug}"' in mine.text
    assert re.search(r'strip-badge" data-tone="neutral" aria-label="\d+ policies waiting for your acknowledgement"', STRIP.search(mine.text).group(0))
    assert theo.post(f"/policies/{slug}/approve", follow_redirects=False).status_code == 403   # a member does not approve
    assert theo.post(f"/policies/{slug}/acknowledge", follow_redirects=False).status_code == 303
    assert f'href="/policies/{slug}"' not in theo.get("/policies?view=mine").text.split("<table", 1)[-1]
    assert "2 of 2" in theo.get(f"/policies/{slug}").text

    # Theo is this policy's owner (the Security Lead), so he may edit it; saving makes version 2 and a draft again.
    edit = theo.get(f"/policies/{slug}/edit")
    assert edit.status_code == 200 and "Save as version 2" in edit.text and "# Saltmarsh Payroll Information Security Policy" in edit.text
    body = re.search(r'<textarea id="body"[^>]*>(.*?)</textarea>', edit.text, re.S).group(1)
    new_body = body.replace("## 1. Purpose", "## 1. Purpose\n\nOur IT provider is Harborline IT.")
    r = theo.post(f"/policies/{slug}/edit", data={"body": new_body, "change_note": "Named the IT provider"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].endswith("?done=saved")
    page = theo.get(f"/policies/{slug}")
    assert "version 2" in page.text and 'class="badge q-draft"' in page.text and "Our IT provider is Harborline IT." in page.text
    assert "Named the IT provider" in page.text and "Send for approval" in page.text
    assert "Acknowledgements start once the policy is approved" in page.text
    assert theo.post(f"/policies/{slug}/edit", data={"body": new_body}, follow_redirects=False).headers["location"].endswith("?done=unchanged")
    r = theo.post(f"/policies/{slug}/submit", follow_redirects=False)
    assert r.status_code == 303 and 'class="badge q-in_review"' in theo.get(f"/policies/{slug}").text
    audit = signed_in("saltmarsh", 0).get("/audit").text
    for action in ("policy.approve", "policy.acknowledge", "policy.version", "policy.submit"):
        assert action in audit


def test_approval_is_refused_while_a_placeholder_remains(signed_in):
    dana = signed_in("saltmarsh", 0)
    slug = "risk-management-policy"
    body = re.search(r'<textarea id="body"[^>]*>(.*?)</textarea>', dana.get(f"/policies/{slug}/edit").text, re.S).group(1)
    r = dana.post(f"/policies/{slug}/edit", data={"body": body + "\n\nThe {{Risk Committee}} meets quarterly.\n"}, follow_redirects=False)
    assert r.status_code == 303
    page = dana.get(f"/policies/{slug}")
    assert "Unfilled placeholders: Risk Committee" in page.text
    r = dana.post(f"/policies/{slug}/approve", follow_redirects=False)
    assert r.status_code == 400 and "Risk Committee" in r.text
    assert dana.post(f"/policies/{slug}/edit", data={"body": "   "}).status_code == 400


def test_rendering_keeps_html_out_and_demotes_headings():
    html, outline = render("# {{Company}} Policy\n\n## 1. Purpose\n\n<script>alert(1)</script>\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n\n## 1. Purpose\n")
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert '<h2 id="company-policy">' in html and '<h3 id="1-purpose">' in html and '<h3 id="1-purpose-2">' in html
    assert "<table>" in html
    assert [h["text"] for h in outline] == ["1. Purpose", "1. Purpose"]


def test_policies_section_sits_in_the_strip_and_the_column(signed_in):
    client = signed_in("harbor-dental")
    r = client.get("/policies")
    strip = STRIP.search(r.text).group(0)
    assert 'href="/policies" aria-current="page"' in strip
    column = COLUMN.search(r.text).group(0)
    for label in ("All policies", "Approved", "Awaiting approval", "Drafts", "Needs my acknowledgement"):
        assert label in column
    assert 'href="/policies" aria-current="page"' in column
    drafts = client.get("/policies?view=draft")
    assert 'href="/policies?view=draft" aria-current="page"' in COLUMN.search(drafts.text).group(0)
    assert drafts.text.count('class="badge q-draft"') == 18  # Harbor Dental: 4 approved, 1 awaiting, 18 drafts
    assert client.get("/policies?view=nope").status_code == 404
    assert client.get("/policies/no-such-policy").status_code == 404


def test_another_companys_copy_is_a_different_document(signed_in, orgs, app_engine):
    harbor = signed_in("harbor-dental").get("/policies/acceptable-use-policy")
    assert "Harbor Dental Acceptable Use Policy" in harbor.text and "Saltmarsh" not in harbor.text and "Dana Whitcomb" not in harbor.text
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        saltmarsh_policy = conn.execute(text("SELECT id FROM policies WHERE slug = 'acceptable-use-policy'")).scalar()
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        assert conn.execute(text("SELECT count(*) FROM policy_versions WHERE policy_id = :id"), {"id": saltmarsh_policy}).scalar() == 0
        assert conn.execute(text("SELECT count(*) FROM policy_acknowledgements WHERE policy_id = :id"), {"id": saltmarsh_policy}).scalar() == 0


def test_a_versions_text_cannot_be_changed_by_the_app(app_engine, orgs):
    """The approval stamp is the only thing the app may write on a version; the text is history."""
    from sqlalchemy.exc import ProgrammingError
    import pytest

    with pytest.raises(ProgrammingError, match="permission denied"):
        with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
            conn.execute(text("UPDATE policy_versions SET body = 'rewritten'"))
    with pytest.raises(ProgrammingError, match="permission denied"):
        with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
            conn.execute(text("DELETE FROM policy_acknowledgements"))
