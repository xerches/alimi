from __future__ import annotations

import pytest

from alimi_scanner.catalog import find_checks_file, load_catalog
from alimi_scanner.engine import registered_ids
from alimi_scanner.schema import CheckKind, Platform


def test_catalog_loads_all_checks(catalog):
    assert catalog.source is not None
    assert len(catalog.checks) == 23
    assert set(catalog.insurer_questions) == {
        "mfa",
        "admin_access",
        "email_security",
        "data_sharing",
        "logging",
        "edr",
        "backups",
        "incident_response",
    }


def test_every_m365_automated_check_has_an_implementation(catalog):
    expected = {c.id for c in catalog.checks if c.platform == Platform.m365 and c.kind == CheckKind.automated}
    assert expected <= set(registered_ids())
    assert len(expected) == 12


def test_every_gws_automated_check_has_an_implementation(catalog):
    expected = {c.id for c in catalog.checks if c.platform == Platform.gws and c.kind == CheckKind.automated}
    assert expected <= set(registered_ids())
    assert len(expected) == 8


def test_for_platform_includes_attestations(catalog):
    ids = {c.id for c in catalog.for_platform(Platform.m365)}
    assert "att.edr.coverage" in ids
    assert "gws.2sv.enforced" not in ids
    gws_ids = {c.id for c in catalog.for_platform(Platform.gws)}
    assert "att.edr.coverage" in gws_ids and "m365.mfa.coverage" not in gws_ids


def test_explicit_missing_path_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_checks_file(tmp_path / "nope.yaml")


def test_env_override(monkeypatch, catalog, tmp_path):
    copy = tmp_path / "checks.yaml"
    copy.write_text(catalog.source.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setenv("ALIMI_CHECKS", str(copy))
    assert load_catalog().source == copy
