"""Every template carries the attorney-review header, uses only known placeholders, and every pricing token resolves."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEMPLATES / "build"))

from render import (  # noqa: E402
    ALLOWED_PLACEHOLDERS,
    ATTORNEY_MARKER,
    HEADER,
    TOKEN,
    fill_pricing,
    load_pricing,
    load_templates,
    render,
    resolve,
    to_html,
)

PRICING = load_pricing()
ALL = load_templates()
BY_SLUG = {t.slug: t for t in ALL}
PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
EXPECTED_SLUGS = {
    "pilot-authorization-letter",
    "master-services-agreement-outline",
    "sow-workspace-scan-and-report",
    "sow-insurance-ready-in-30-days",
    "sow-payment-fraud-workshop",
    "sow-policy-adoption-workshop",
    "sow-ai-policy-implementation",
    "sow-fractional-security-lead",
    "reseller-agreement-outline",
    "referral-agreement-outline",
    "case-study-template",
    "referral-partner-one-pager",
}
NEEDS_ATTORNEY_MARKERS = {
    "master-services-agreement-outline": 6,
    "reseller-agreement-outline": 4,
    "referral-agreement-outline": 3,
    "pilot-authorization-letter": 1,
}


def test_the_expected_templates_exist():
    assert {t.slug for t in ALL} == EXPECTED_SLUGS


@pytest.mark.parametrize("template", ALL, ids=[t.slug for t in ALL])
def test_header_is_the_first_line(template):
    first = template.body.lstrip().splitlines()[0]
    assert HEADER in first, f"{template.path.name} must start with the attorney-review header"
    assert "slug" in template.meta and "title" in template.meta
    assert template.path.name == f"{template.slug}.md"


@pytest.mark.parametrize("template", ALL, ids=[t.slug for t in ALL])
def test_only_known_placeholders(template):
    used = {p for p in PLACEHOLDER.findall(template.body) if not TOKEN.match(p)}
    assert used <= ALLOWED_PLACEHOLDERS, used - ALLOWED_PLACEHOLDERS


@pytest.mark.parametrize("template", ALL, ids=[t.slug for t in ALL])
def test_every_pricing_token_resolves(template):
    _, missing = fill_pricing(template.body, PRICING)
    assert missing == [], missing


@pytest.mark.parametrize("template", ALL, ids=[t.slug for t in ALL])
def test_rendered_text_has_no_pricing_tokens_and_no_literal_prices_outside_pricing(template):
    rendered = render(template, PRICING)
    assert "{{pricing." not in rendered
    # Dollar amounts come from pricing.yaml, never typed into a template, so the price list stays the single source.
    assert not re.search(r"\$\d", template.body), f"{template.path.name} hard-codes a dollar amount; use a {{{{pricing.*}}}} token"


def test_attorney_review_markers_are_present_where_a_lawyer_is_needed():
    for slug, minimum in NEEDS_ATTORNEY_MARKERS.items():
        count = BY_SLUG[slug].body.count(ATTORNEY_MARKER)
        assert count >= minimum, f"{slug} has {count} '{ATTORNEY_MARKER}' markers, expected at least {minimum}"


def test_pilot_letter_is_one_page_and_says_the_essentials():
    body = BY_SLUG["pilot-authorization-letter"].body
    assert len(body.split()) <= 500, "the pilot letter must fit one page"
    lowered = body.lower()
    for phrase in ("read-only", "no fee", "either side may stop", "{{tenant domain}}"):
        assert phrase in lowered, phrase


def test_sows_name_their_price_from_pricing():
    expected = {
        "sow-workspace-scan-and-report": "products.services.assessment.price",
        "sow-insurance-ready-in-30-days": "products.services.insurance_ready_30.price",
        "sow-payment-fraud-workshop": "products.services.fraud_workshop.price",
        "sow-policy-adoption-workshop": "products.services.policy_adoption.price",
        "sow-ai-policy-implementation": "products.services.ai_policy_implementation.price",
        "sow-fractional-security-lead": "retainers.fractional_security_lead.price",
    }
    for slug, token in expected.items():
        assert f"{{{{pricing.{token}}}}}" in BY_SLUG[slug].body, (slug, token)


def test_reseller_outline_uses_the_tier_table_and_the_channel_principle():
    body = BY_SLUG["reseller-agreement-outline"].body
    assert "{{pricing.partners.reseller.tiers_table}}" in body
    assert "{{pricing.partners.principle}}" in body
    rendered = render(BY_SLUG["reseller-agreement-outline"], PRICING)
    assert "| Starter | 1 to 50 | 10% |" in rendered
    assert "| Scale | 151 or more | 20% |" in rendered


def test_referral_outline_states_the_fee_and_disclosure():
    body = BY_SLUG["referral-agreement-outline"].body
    assert "{{pricing.partners.referral.fee}}" in body
    assert "disclos" in body.lower()


def test_case_study_has_a_permission_line_and_honest_claims_note():
    body = BY_SLUG["case-study-template"].body
    assert "permission" in body.lower()
    assert "employment" in body.lower() or "not from alimi clients" in body.lower()


def test_resolver_formats():
    assert resolve("products.platform.product_name", PRICING) == "alimi platform"
    assert resolve("products.platform.starter.price", PRICING) == "$3,900"
    assert resolve("products.services.assessment.price", PRICING) == "$500 to $1,500"
    assert resolve("products.free.scan_summary.price", PRICING) == "free"
    assert resolve("retainers.fractional_security_lead.price", PRICING) == "$3,000 to $6,000 a month"
    assert resolve("partners.referral.fee", PRICING) == "10%"
    assert resolve("terms.minimum_monthly_retainer", PRICING) == "$1,500 a month"
    with pytest.raises(KeyError):
        resolve("products.nope.free.price", PRICING)


def test_check_mode_passes():
    result = subprocess.run([sys.executable, str(TEMPLATES / "build" / "render.py"), "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_render_builds_docx(tmp_path):
    result = subprocess.run(
        [sys.executable, str(TEMPLATES / "build" / "render.py"), "--only", "pilot-authorization-letter", "--set", "Client=Acme Inc", "--out", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "pilot-authorization-letter.docx").is_file()
    assert "Acme Inc" in (tmp_path / "pilot-authorization-letter.md").read_text(encoding="utf-8")


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_pilot_letter_renders_to_one_page():
    weasyprint = pytest.importorskip("weasyprint")
    html = to_html(BY_SLUG["pilot-authorization-letter"], PRICING, {"Client": "Acme Inc", "Tenant": "Microsoft 365", "Tenant Domain": "acme.example"})
    pages = weasyprint.HTML(string=html, base_url=str(TEMPLATES / "build")).render().pages
    assert len(pages) == 1, f"pilot letter renders to {len(pages)} pages"


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_partner_one_pager_fits_one_page():
    weasyprint = pytest.importorskip("weasyprint")
    html = to_html(BY_SLUG["referral-partner-one-pager"], PRICING, {"Contact Email": "hello@example.com", "Contact Phone": "555-0100", "Website": "example.com"})
    pages = weasyprint.HTML(string=html, base_url=str(TEMPLATES / "build")).render().pages
    assert len(pages) == 1, f"one-pager renders to {len(pages)} pages"
