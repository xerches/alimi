"""The kit's five documents have front matter, only known placeholders, defined terms, sane length, and they build."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "build"))

from build import ALLOWED_PLACEHOLDERS, load_docs, to_html  # noqa: E402

DOCS = load_docs()
BY_ID = {d.id: d for d in DOCS}
PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
EXPECTED = {
    "PFK-01": ("payment-verification-procedure", "procedure"),
    "PFK-02": ("callback-scripts", "scripts"),
    "PFK-03": ("staff-poster", "poster"),
    "PFK-04": ("closing-day-checklist", "checklist"),
    "PFK-05": ("training-video-script", "script"),
}
WORDS = {"PFK-01": (1200, 2500), "PFK-02": (800, 2000), "PFK-03": (120, 400), "PFK-04": (900, 2200), "PFK-05": (1800, 3500)}
pandoc_needed = pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")


def test_the_five_documents_exist():
    assert {d.id: (d.slug, d.kind) for d in DOCS} == EXPECTED


@pytest.mark.parametrize("doc", DOCS, ids=[d.id for d in DOCS])
def test_front_matter_and_title(doc):
    for key in ("id", "slug", "title", "kind"):
        assert key in doc.meta, f"{doc.path.name} lacks {key}"
    assert doc.body.count("\n# ") == 1, "exactly one top-level heading"


@pytest.mark.parametrize("doc", DOCS, ids=[d.id for d in DOCS])
def test_only_known_placeholders(doc):
    used = set(PLACEHOLDER.findall(doc.body))
    assert used <= ALLOWED_PLACEHOLDERS, used - ALLOWED_PLACEHOLDERS


@pytest.mark.parametrize("doc", DOCS, ids=[d.id for d in DOCS])
def test_length(doc):
    low, high = WORDS[doc.id]
    words = len(doc.body.split())
    assert low <= words <= high, f"{doc.path.name} has {words} words"


def test_every_document_but_the_poster_carries_the_kit_note():
    for doc in DOCS:
        if doc.kind == "poster":
            continue
        first = doc.body.lstrip().splitlines()[0]
        assert first.startswith("> Part of the alimi Payment Fraud Protection Kit"), doc.path.name


def test_procedure_states_the_three_rules():
    body = BY_ID["PFK-01"].body
    assert "**Rule 1. Verified callback.**" in body
    assert "**Rule 2. Two people.**" in body
    assert "**Rule 3. Twenty-four-hour hold.**" in body
    assert "{{Threshold}}" in body
    assert "already had on file" in body
    assert "24 hours" in body


def test_terms_are_defined_before_the_acronym():
    procedure = BY_ID["PFK-01"].body
    assert procedure.find("business email compromise (BEC)") < procedure.find("BEC)") + 1
    assert "ACH (the US bank-to-bank network" in procedure
    checklist = BY_ID["PFK-04"].body
    assert "IOLTA** account, short for Interest on Lawyers' Trust Accounts" in checklist
    video = BY_ID["PFK-05"].body
    assert "Business email compromise (BEC)" in video


def test_closing_checklist_is_not_legal_advice_and_names_the_fbi_boston_number():
    body = BY_ID["PFK-04"].body
    assert "not legal advice" in body
    assert "857-386-2000" in body
    assert "ic3.gov" in body
    assert "M.G.L. c. 183 §63B" in body


def test_statistics_name_their_source_and_year():
    for doc in (BY_ID["PFK-04"], BY_ID["PFK-05"]):
        if "$" in doc.body and "billion" in doc.body or "million" in doc.body:
            assert "2025 Internet Crime Report" in doc.body, f"{doc.path.name} quotes a figure without naming the FBI report year"


def test_poster_has_the_boss_rule_and_the_first_hour():
    body = BY_ID["PFK-03"].body
    assert "The boss rule" in body
    assert "{{Bank Fraud Line}}" in body
    assert "ic3.gov" in body


@pandoc_needed
def test_fill_replaces_every_placeholder_in_the_procedure():
    html = to_html(
        BY_ID["PFK-01"],
        {"Company": "Acme Inc", "Finance Lead": "Dana Lee", "CEO": "Sam Ortiz", "Security Lead": "Lee Park", "Bank Fraud Line": "555-0100", "Effective Date": "2027-01-15"},
    )
    assert "Acme Inc" in html and "$10,000" in html  # Threshold has a default
    assert "{{" not in html


@pandoc_needed
def test_poster_fits_one_page():
    weasyprint = pytest.importorskip("weasyprint")
    html = to_html(BY_ID["PFK-03"], {"Company": "Acme Inc", "Finance Lead": "Dana Lee", "CEO": "Sam Ortiz", "Security Lead": "Lee Park", "Bank Fraud Line": "555-0100", "Effective Date": "2027-01-15"})
    pages = weasyprint.HTML(string=html, base_url=str(KIT / "build")).render().pages
    assert len(pages) == 1, f"poster renders to {len(pages)} pages"


@pandoc_needed
def test_build_script_writes_docx_for_every_document(tmp_path):
    result = subprocess.run(
        [sys.executable, str(KIT / "build" / "build.py"), "--fill", "Acme Inc", "--docx-only", "--out", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    for slug, _ in EXPECTED.values():
        assert (tmp_path / f"{slug}.docx").is_file(), slug
