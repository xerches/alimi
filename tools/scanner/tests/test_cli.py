from __future__ import annotations

import json

from typer.testing import CliRunner

from alimi_scanner.cli import app
from alimi_scanner.schema import ScanResult

runner = CliRunner()


def test_mock_scan_writes_findings(tmp_path):
    result = runner.invoke(app, ["m365", "--out", str(tmp_path), "--save-snapshot"])
    assert result.exit_code == 0, result.output
    findings = list(tmp_path.glob("m365-*.findings.json"))
    snapshots = list(tmp_path.glob("m365-*.snapshot.json"))
    assert len(findings) == 1 and len(snapshots) == 1
    parsed = ScanResult.model_validate(json.loads(findings[0].read_text()))
    assert parsed.tenant.source == "mock:pass"
    assert parsed.summary.failed == 0
    assert "What your insurer will ask" in result.output


def test_fail_fixture_and_quiet(tmp_path):
    result = runner.invoke(app, ["m365", "--fixture", "fail", "--out", str(tmp_path), "--quiet"])
    assert result.exit_code == 0, result.output
    path = result.output.strip()
    parsed = ScanResult.model_validate(json.loads(open(path).read()))
    assert parsed.summary.failed == 12


def test_unknown_fixture_is_an_error(tmp_path):
    result = runner.invoke(app, ["m365", "--fixture", "nope", "--out", str(tmp_path)])
    assert result.exit_code != 0


def test_real_tenant_requires_authorization(tmp_path, monkeypatch):
    monkeypatch.setenv("M365_TENANT_ID", "x")
    result = runner.invoke(app, ["m365", "--tenant", "--out", str(tmp_path)])
    assert result.exit_code == 2
    assert "Refusing" in result.output


def test_real_tenant_without_env_explains(tmp_path, monkeypatch):
    for name in ("M365_TENANT_ID", "M365_CLIENT_ID", "M365_CLIENT_SECRET"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # no .env here
    result = runner.invoke(app, ["m365", "--tenant", "--authorized", "--out", str(tmp_path), "--checks", _checks_path()])
    assert result.exit_code == 2
    assert "missing environment variables" in result.output


def test_snapshot_file_option(tmp_path):
    from alimi_scanner.connectors.mock import load_fixture

    snap = load_fixture("m365", "pass")
    snap.secure_score.current = 10
    path = tmp_path / "snap.json"
    path.write_text(snap.model_dump_json())
    result = runner.invoke(app, ["m365", "--snapshot", str(path), "--out", str(tmp_path), "--quiet"])
    assert result.exit_code == 0, result.output
    parsed = ScanResult.model_validate(json.loads(open(result.output.strip()).read()))
    assert parsed.tenant.source == "mock:snap.json"
    assert parsed.summary.failed == 1


def test_listing_commands():
    assert runner.invoke(app, ["checks", "--platform", "m365"]).exit_code == 0
    fixtures = runner.invoke(app, ["fixtures"])
    assert fixtures.exit_code == 0 and "pass" in fixtures.output and "fail" in fixtures.output
    perms = runner.invoke(app, ["permissions"])
    assert perms.exit_code == 0 and "MailboxSettings.Read" in perms.output
    assert "alimi-scanner" in runner.invoke(app, ["version"]).output


def _checks_path() -> str:
    from alimi_scanner.catalog import find_checks_file

    return str(find_checks_file())
