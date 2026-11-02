from __future__ import annotations

from typer.testing import CliRunner

from alimi_report.cli import app

runner = CliRunner()


def test_demo_writes_html(tmp_path):
    result = runner.invoke(app, ["demo", "--out", str(tmp_path), "--no-pdf", "--quiet"])
    assert result.exit_code == 0, result.output
    html = tmp_path / result.output.strip().splitlines()[0].split("/")[-1]
    assert html.is_file()
    assert ">Every finding</h2>" in html.read_text(encoding="utf-8")


def test_demo_gws_free_with_reseller(tmp_path):
    result = runner.invoke(
        app,
        ["demo", "-p", "gws", "-f", "pass", "--free", "--reseller-name", "Northside IT", "--out", str(tmp_path), "--no-pdf", "--quiet"],
    )
    assert result.exit_code == 0, result.output
    html = list(tmp_path.glob("*-summary-*.html"))[0].read_text(encoding="utf-8")
    assert "Northside IT" in html and "powered by Alimi" in html and ">Every finding</h2>" not in html


def test_render_from_a_findings_file(tmp_path):
    from typer.testing import CliRunner as ScanRunner

    from alimi_scanner.cli import app as scan_app

    scan = ScanRunner().invoke(scan_app, ["gws", "--fixture", "fail", "--out", str(tmp_path), "--quiet"])
    findings = scan.output.strip()
    result = runner.invoke(app, ["render", findings, "--out", str(tmp_path), "--no-pdf", "--name", "client", "--quiet"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "client.html").is_file()
    assert "Risky Co (mock)" in (tmp_path / "client.html").read_text(encoding="utf-8")


def test_reseller_logo_needs_a_name(tmp_path):
    result = runner.invoke(app, ["demo", "--reseller-contact", "x@y", "--out", str(tmp_path), "--no-pdf"])
    assert result.exit_code == 2
    assert "--reseller-name" in result.output


def test_missing_findings_file_is_an_error(tmp_path):
    result = runner.invoke(app, ["render", str(tmp_path / "nope.json"), "--out", str(tmp_path)])
    assert result.exit_code != 0


def test_backends_and_version():
    assert "PDF backend" in runner.invoke(app, ["backends"]).output
    assert "alimi-report" in runner.invoke(app, ["version"]).output
