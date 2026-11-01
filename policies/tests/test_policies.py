"""Every policy has the header, the front matter, the sections and only known requirement IDs; coverage.md is current."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

BUILD = Path(__file__).resolve().parents[1] / "build"
sys.path.insert(0, str(BUILD))

from coverage import (  # noqa: E402
    ALLOWED_PLACEHOLDERS,
    COVERAGE_FILE,
    HEADER,
    REQUIRED_KEYS,
    REQUIRED_SECTIONS,
    build_coverage,
    load_policies,
    load_requirements,
    render_coverage,
)

POLICIES = load_policies()
FRAMEWORKS = load_requirements()
PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")


def test_there_are_twenty_three_policies():
    assert len(POLICIES) == 23


@pytest.mark.parametrize("policy", POLICIES, ids=[p.path.name for p in POLICIES])
def test_front_matter_is_complete(policy):
    for key in REQUIRED_KEYS:
        assert key in policy.meta, f"{policy.path.name} lacks {key}"
    number = int(policy.path.name[:2])
    assert policy.id == f"POL-{number:02d}"
    assert policy.path.name == f"{number:02d}-{policy.meta['slug']}.md"
    assert policy.meta["status"] == "template"
    assert set(policy.requirements) <= set(FRAMEWORKS), policy.requirements.keys()


@pytest.mark.parametrize("policy", POLICIES, ids=[p.path.name for p in POLICIES])
def test_header_title_and_sections(policy):
    first_lines = "\n".join(policy.body.lstrip().splitlines()[:2])
    assert HEADER in first_lines, f"{policy.path.name} must start with the TEMPLATE header"
    assert f"# {{{{Company}}}} {policy.title}" in policy.body
    positions = [policy.body.find(section) for section in REQUIRED_SECTIONS]
    assert all(p >= 0 for p in positions), [s for s, p in zip(REQUIRED_SECTIONS, positions) if p < 0]
    assert positions == sorted(positions), "sections out of order"
    assert f"| Policy ID | {policy.id} |" in policy.body
    assert "| 1.0 | {{Effective Date}} |" in policy.body


@pytest.mark.parametrize("policy", POLICIES, ids=[p.path.name for p in POLICIES])
def test_only_known_placeholders(policy):
    used = set(PLACEHOLDER.findall(policy.body)) | set(PLACEHOLDER.findall(str(policy.meta)))
    assert used <= ALLOWED_PLACEHOLDERS, used - ALLOWED_PLACEHOLDERS
    assert "{{Company}}" in policy.body


@pytest.mark.parametrize("policy", POLICIES, ids=[p.path.name for p in POLICIES])
def test_policy_is_two_to_four_pages(policy):
    words = len(policy.body.split())
    assert 700 <= words <= 2200, f"{policy.path.name} has {words} words"


@pytest.mark.parametrize("policy", POLICIES, ids=[p.path.name for p in POLICIES])
def test_policy_has_numbered_statements(policy):
    statements = re.findall(r"^\d+\. ", policy.body, flags=re.MULTILINE)
    assert len(statements) >= 10, f"{policy.path.name} has only {len(statements)} numbered statements"


def test_every_policy_cites_only_known_requirements():
    coverage = build_coverage(FRAMEWORKS, POLICIES)
    assert coverage.unknown == [], coverage.unknown


def test_every_policy_maps_to_something():
    for policy in POLICIES:
        assert any(policy.requirements.values()), f"{policy.id} maps to no requirement"


def test_core_frameworks_are_fully_covered():
    coverage = build_coverage(FRAMEWORKS, POLICIES)
    for framework in ("soc2", "iso27001", "iso42001", "hipaa", "insurer"):
        assert coverage.uncovered(framework) == [], (framework, coverage.uncovered(framework))


def test_coverage_matrix_is_current():
    expected = render_coverage(build_coverage(FRAMEWORKS, POLICIES))
    assert COVERAGE_FILE.exists(), "run python policies/build/coverage.py"
    assert COVERAGE_FILE.read_text(encoding="utf-8") == expected, "coverage.md is stale; run python policies/build/coverage.py"


def test_hr_and_legal_sections_are_marked():
    marked = [p.id for p in POLICIES if "[HR or legal review]" in p.body]
    assert {"POL-02", "POL-13", "POL-16", "POL-20", "POL-21"} <= set(marked)


def test_no_framework_text_markers():
    # The standards are copyrighted; the library carries IDs and our own words only. A crude tripwire:
    for policy in POLICIES:
        lowered = policy.body.lower()
        assert "trust services criteria state" not in lowered
        assert "iso/iec 27001:2022 states" not in lowered
        assert "© iso" not in lowered and "copyright aicpa" not in lowered


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_build_one_policy_to_docx_with_fill(tmp_path):
    result = subprocess.run(
        [sys.executable, str(BUILD / "build.py"), "--only", "POL-13", "--fill", "Acme Inc", "--docx-only", "--out", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "incident-response-policy.docx").is_file()


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_final_build_refuses_unfilled_placeholders(tmp_path):
    result = subprocess.run(
        [sys.executable, str(BUILD / "build.py"), "--only", "POL-01", "--fill", "Acme Inc", "--final", "--docx-only", "--out", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "placeholders still unfilled" in result.stderr or "markers remain" in result.stderr
