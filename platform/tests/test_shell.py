"""The app shell on every signed-in page: the strip, the column where a section has children, the
breadcrumbs, the phone bar, and that every link in them points at a page that answers."""

from __future__ import annotations

import re

from sqlalchemy import text

from alimi_platform.db import org_scope
from alimi_platform.nav import BOTTOM_BAR, PAGE_SECTIONS, SECTIONS

STRIP = re.compile(r'<nav class="strip".*?</nav>', re.S)
COLUMN = re.compile(r'<aside class="column".*?</aside>', re.S)
BOTTOM = re.compile(r'<nav class="bottombar".*?</nav>', re.S)
CURRENT = re.compile(r'<a[^>]*href="([^"]+)"[^>]*aria-current="page"')
HREFS = re.compile(r'href="([^"]+)"')


def test_the_picker_has_no_shell(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert not STRIP.search(r.text) and not COLUMN.search(r.text)
    assert 'class="shell" data-bare' in r.text


def test_every_page_marks_its_section_in_the_strip(signed_in):
    client = signed_in("saltmarsh")
    expected = {
        "/dashboard": "/dashboard",
        "/frameworks": "/frameworks",
        "/frameworks/insurer": "/frameworks",
        "/controls": "/controls",
        "/controls/CTL-09": "/controls",
        "/monitoring": "/monitoring",
        "/settings": "/settings",
        "/audit": "/settings",
    }
    for path, section_href in expected.items():
        r = client.get(path)
        assert r.status_code == 200, path
        strip = STRIP.search(r.text).group(0)
        current = CURRENT.findall(strip)
        assert current == [section_href], f"{path}: strip marks {current}"
        assert len(re.findall(r'class="strip-item"', strip)) == len(SECTIONS)
        bottom = BOTTOM.search(r.text).group(0)
        assert len(HREFS.findall(bottom)) == len(BOTTOM_BAR) + 1  # four sections and the menu


def test_columns_appear_only_where_a_section_has_children(signed_in):
    client = signed_in("saltmarsh")
    assert not COLUMN.search(client.get("/dashboard").text)
    assert not COLUMN.search(client.get("/monitoring").text)
    frameworks = COLUMN.search(client.get("/frameworks/insurer").text).group(0)
    assert "On this account" in frameworks and "Add a framework" in frameworks
    assert CURRENT.findall(frameworks) == ["/frameworks/insurer"]
    assert re.search(r"\d+ of \d+ controls Ok", frameworks)
    settings = COLUMN.search(client.get("/audit").text).group(0)
    assert CURRENT.findall(settings) == ["/audit"]
    assert CURRENT.findall(COLUMN.search(client.get("/settings").text).group(0)) == ["/settings"]


def test_controls_column_filters_by_area(signed_in, orgs, app_engine):
    client = signed_in("harbor-dental")
    with org_scope(app_engine, orgs["harbor-dental"].id) as conn:
        rows = conn.execute(text("SELECT id, domain FROM controls ORDER BY id")).all()
    by_domain: dict[str, list[str]] = {}
    for control_id, domain in rows:
        by_domain.setdefault(domain, []).append(control_id)
    domain, own = next(iter(sorted(by_domain.items())))
    other = next(ids for d, ids in by_domain.items() if d != domain)

    everything = client.get("/controls")
    column = COLUMN.search(everything.text).group(0)
    assert CURRENT.findall(column) == ["/controls"]
    assert f'href="/controls?domain={domain}"' in column

    filtered = client.get(f"/controls?domain={domain}")
    assert filtered.status_code == 200
    body = filtered.text.split("<main", 1)[1]
    assert all(f'id="{c}"' in body for c in own)
    assert not any(f'id="{c}"' in body for c in other)
    assert CURRENT.findall(COLUMN.search(filtered.text).group(0)) == [f"/controls?domain={domain}"]
    assert client.get("/controls?domain=nope").status_code == 404

    detail = client.get(f"/controls/{own[0]}")
    assert CURRENT.findall(COLUMN.search(detail.text).group(0)) == [f"/controls?domain={domain}"]
    crumbs = re.search(r'<nav class="crumbs".*?</nav>', detail.text, re.S).group(0)
    assert f'href="/controls?domain={domain}"' in crumbs and own[0] in crumbs


def test_every_strip_and_column_link_answers(signed_in):
    client = signed_in("alimi")
    seen: set[str] = set()
    for path in ("/dashboard", "/frameworks", "/controls", "/monitoring", "/settings"):
        r = client.get(path)
        assert r.status_code == 200
        chrome = STRIP.search(r.text).group(0) + (COLUMN.search(r.text).group(0) if COLUMN.search(r.text) else "")
        for href in HREFS.findall(chrome):
            target = href.split("#")[0]
            if not target or target in seen:
                continue
            seen.add(target)
            assert client.get(target).status_code == 200, f"{path} links to {href}"
    assert "/audit" in seen and "/frameworks/insurer" in seen


def test_badges_are_computed_from_this_companys_rows(signed_in):
    # Saltmarsh's sample tenant fails checks, so Monitoring carries a red badge; Alimi's passes.
    failing = STRIP.search(signed_in("saltmarsh").get("/dashboard").text).group(0)
    assert re.search(r'strip-badge" data-tone="danger" aria-label="\d+ failing tests"', failing)
    passing = STRIP.search(signed_in("alimi").get("/dashboard").text).group(0)
    assert "failing tests" not in passing


def test_page_keys_resolve_to_strip_sections():
    keys = {s.key for s in SECTIONS}
    for page, (section, _item) in PAGE_SECTIONS.items():
        assert section in keys, page
    assert set(BOTTOM_BAR) <= keys and len(BOTTOM_BAR) == 4
