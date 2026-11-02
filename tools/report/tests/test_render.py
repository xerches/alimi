"""Rendering: the HTML says what the model decided, the flags change the right parts, and files land where asked."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import pytest

from alimi_report import Reseller, render, render_html, write_report
from alimi_report.brand import Brand, find_brand_file, load_brand, load_offer

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


class _Balanced(HTMLParser):
    VOID = {"meta", "img", "br", "hr", "link", "input"}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append((tag, list(self.stack[-3:])))
        else:
            self.stack.pop()


def assert_well_formed(html: str) -> None:
    parser = _Balanced()
    parser.feed(html)
    assert not parser.errors, parser.errors[:3]
    assert not parser.stack, parser.stack


def test_full_report_has_every_section(m365_fail, brand, offer):
    html = render_html(m365_fail, brand=brand, offer=offer, now=NOW)
    assert_well_formed(html)
    for heading in ("What your insurer will ask", "Top 5 fixes, in order", "Every finding", "Evidence pack", "Terms used", "How to read this report"):
        assert f">{heading}</h2>" in html, heading
    assert "Risky Co (mock)" in html
    assert "Microsoft 365 security report" in html
    assert "This is the free summary" not in html
    assert "Full report" in html
    assert "no settings were changed" in html


def test_free_summary_is_only_the_first_page(m365_fail, brand, offer):
    html = render_html(m365_fail, brand=brand, offer=offer, free=True, now=NOW)
    assert_well_formed(html)
    assert "What your insurer will ask" in html
    assert "Top 5 fixes" in html
    assert "This is the free summary" in html
    assert "$500" in html and "$4,000" in html
    assert ">Every finding</h2>" not in html
    assert ">Evidence pack</h2>" not in html
    assert "Free summary" in html


def test_reseller_cover_and_powered_by(gws_fail, brand, offer, tmp_path):
    logo = tmp_path / "logo.png"
    logo.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    reseller = Reseller(name="Northside IT", logo=logo, contact="help@northside.example")
    html = render_html(gws_fail, brand=brand, offer=offer, reseller=reseller, free=True, now=NOW)
    assert 'alt="Northside IT"' in html
    assert "data:image/png;base64," in html
    assert "powered by Alimi" in html
    assert "by Northside IT (help@northside.example)" in html
    assert "Contact Northside IT: help@northside.example" in html


def test_reseller_without_logo_shows_the_name(gws_fail, brand, offer):
    html = render_html(gws_fail, brand=brand, offer=offer, reseller=Reseller(name="Northside IT", powered_by=False), now=NOW)
    assert ">Northside IT<" in html
    assert "powered by" not in html


def test_reseller_logo_must_exist(gws_fail, brand, offer, tmp_path):
    with pytest.raises(FileNotFoundError):
        render_html(gws_fail, brand=brand, offer=offer, reseller=Reseller(name="X", logo=tmp_path / "missing.png"))


def test_brand_colors_reach_the_stylesheet(m365_pass, offer):
    brand = Brand(display_name="Acme Security", colors={"primary": "#123456"})
    html = render_html(m365_pass, brand=brand, offer=offer, now=NOW)
    assert "--accent: #123456" in html
    assert "Acme Security" in html


def test_pass_report_says_nothing_to_fix(gws_pass, brand, offer):
    html = render_html(gws_pass, brand=brand, offer=offer, now=NOW)
    assert "No automated check failed" in html
    assert "Strong" in html


def test_accepts_dict_json_and_path(m365_fail, brand, offer, tmp_path):
    as_dict = json.loads(m365_fail.model_dump_json())
    as_json = m365_fail.model_dump_json()
    path = tmp_path / "x.findings.json"
    path.write_text(as_json)
    reference = render_html(m365_fail, brand=brand, offer=offer, now=NOW)
    assert render_html(as_dict, brand=brand, offer=offer, now=NOW) == reference
    assert render_html(as_json, brand=brand, offer=offer, now=NOW) == reference
    assert render_html(path, brand=brand, offer=offer, now=NOW) == reference
    assert render_html(str(path), brand=brand, offer=offer, now=NOW) == reference


def test_html_escapes_tenant_content(m365_fail, brand, offer):
    result = m365_fail.model_copy(deep=True)
    result.tenant.display_name = "<script>alert(1)</script> Co"
    html = render_html(result, brand=brand, offer=offer, now=NOW)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_write_report_html_only(m365_fail, brand, offer, tmp_path):
    paths = write_report(m365_fail, tmp_path, pdf=False, brand=brand, offer=offer, now=NOW)
    assert paths.html.name == "risky-co-mock-microsoft365-report-20261101.html"
    assert paths.pdf is None
    assert "Every finding" in paths.html.read_text(encoding="utf-8")
    summary = write_report(m365_fail, tmp_path, pdf=False, free=True, brand=brand, offer=offer, now=NOW)
    assert summary.html.name.endswith("-summary-20261101.html")


def test_write_report_pdf(m365_fail, brand, offer, tmp_path):
    pytest.importorskip("weasyprint")
    paths = write_report(m365_fail, tmp_path, pdf=True, brand=brand, offer=offer, now=NOW)
    assert paths.pdf is not None and paths.pdf.is_file()
    assert paths.pdf.read_bytes().startswith(b"%PDF")


def test_free_summary_prints_on_one_page(m365_fail, gws_fail, m365_pass, brand, offer):
    weasyprint = pytest.importorskip("weasyprint")
    for result in (m365_fail, gws_fail, m365_pass):
        html = render_html(result, free=True, brand=brand, offer=offer, now=NOW)
        pages = len(weasyprint.HTML(string=html).render().pages)
        assert pages == 1, (result.platform, pages)


def test_pdf_unavailable_is_a_clear_error(monkeypatch, m365_fail, brand, offer, tmp_path):
    import alimi_report.pdf as pdf

    monkeypatch.setattr(pdf, "pdf_backend", lambda: None)
    with pytest.raises(pdf.PdfUnavailable, match="alimi-report\\[pdf\\]"):
        write_report(m365_fail, tmp_path, pdf=True, brand=brand, offer=offer, now=NOW)


def test_brand_and_offer_load_from_the_repo_config():
    assert find_brand_file() is not None
    brand = load_brand()
    assert brand.display_name == "Alimi"
    assert brand.color("primary").startswith("#")
    assert brand.domain is None  # TODO in brand.yaml means not decided
    offer = load_offer()
    assert offer.report_from == 500
    assert offer.service_from == 4000
    assert offer.report_includes


def test_render_returns_the_model_too(gws_fail, brand, offer):
    report = render(gws_fail, brand=brand, offer=offer, now=NOW)
    assert report.model.platform_label == "Google Workspace"
    assert report.model.generated_at == NOW
    assert "Google Workspace security report" in report.html


def test_report_never_contains_a_tenant_id(m365_fail, brand, offer):
    html = render_html(m365_fail, brand=brand, offer=offer, now=NOW)
    assert "tenant_id" not in html and "M365_TENANT_ID" not in html
    assert Path(__file__).exists()
