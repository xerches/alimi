"""alimi-scan: the command line on top of alimi_scanner. Mock mode is the default."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from . import __version__
from .catalog import load_catalog
from .connectors.base import Connector
from .connectors.mock import MockConnector, list_fixtures
from .engine import registered_ids, run_checks
from .schema import Platform, ScanResult, Status, TenantInfo
from .snapshot import GWSSnapshot

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Alimi scanner: read-only security checks for Microsoft 365 and Google Workspace. Mock mode is the default.",
)
console = Console()

STATUS_STYLE = {
    Status.passed: "green",
    Status.failed: "red",
    Status.attestation_needed: "yellow",
    Status.error: "magenta",
    Status.not_applicable: "dim",
}

AUTHORIZATION_REMINDER = (
    "Real tenants need --authorized. That flag is your statement that you own the tenant or hold a signed "
    "pilot authorization letter from /templates. No exceptions for friends."
)

# Options shared by the two platform commands.
MOCK = typer.Option(True, "--mock/--tenant", help="Use fixture data (default) or read a real tenant from the credentials in .env.")
FIXTURE = typer.Option("pass", "--fixture", "-f", help="Fixture under fixtures/<platform> to use in mock mode.")
SNAPSHOT = typer.Option(None, "--snapshot", help="Run the checks on a saved snapshot JSON instead.")
AUTHORIZED = typer.Option(False, "--authorized", help="Required with --tenant. You own the tenant or hold a signed pilot letter.")
OUT = typer.Option(None, "--out", "-o", help="Output folder. Default: $ALIMI_OUTPUT_DIR or ./out (git-ignored).")
CHECKS_FILE = typer.Option(None, "--checks", help="Path to checks.yaml. Default: config/checks.yaml in the repo.")
SAVE_SNAPSHOT = typer.Option(False, "--save-snapshot", help="Also save the raw snapshot JSON next to the findings.")
NO_DNS = typer.Option(False, "--no-dns", help="Skip the public DNS lookups for SPF, DKIM and DMARC.")
QUIET = typer.Option(False, "--quiet", "-q", help="Print only the output path.")


def _output_dir(out: Path | None) -> Path:
    return out or Path(os.environ.get("ALIMI_OUTPUT_DIR", "out"))


def _refuse_unauthorized(authorized: bool) -> None:
    if not authorized:
        console.print(f"[red]Refusing to scan a real tenant.[/red] {AUTHORIZATION_REMINDER}")
        raise typer.Exit(code=2)


def _scan(
    platform: Platform,
    connector: Connector,
    *,
    checks_file: Path | None,
    out: Path | None,
    save_snapshot: bool,
    quiet: bool,
    approved_client_ids: list[str] | None = None,
) -> None:
    catalog = load_catalog(checks_file)
    snapshot = connector.fetch()
    if approved_client_ids and isinstance(snapshot, GWSSnapshot):
        snapshot.approved_client_ids = sorted(set(snapshot.approved_client_ids) | set(approved_client_ids))
    tenant = TenantInfo(
        display_name=snapshot.tenant_display_name,
        primary_domain=snapshot.primary_domain(),
        source=connector.source,
    )
    result = run_checks(snapshot, catalog, platform, tenant)

    folder = _output_dir(out)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    findings_path = folder / f"{platform.value}-{stamp}.findings.json"
    snapshot_path = folder / f"{platform.value}-{stamp}.snapshot.json"
    findings_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    if save_snapshot:
        snapshot_path.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")

    if quiet:
        typer.echo(str(findings_path))
        return
    _print_result(result)
    console.print(f"\nFindings written to [bold]{findings_path}[/bold]")
    if save_snapshot:
        console.print(f"Snapshot written to [bold]{snapshot_path}[/bold]")


@app.command()
def m365(
    mock: bool = MOCK,
    fixture: str = FIXTURE,
    snapshot_file: Path | None = SNAPSHOT,
    authorized: bool = AUTHORIZED,
    out: Path | None = OUT,
    checks_file: Path | None = CHECKS_FILE,
    save_snapshot: bool = SAVE_SNAPSHOT,
    no_dns: bool = NO_DNS,
    quiet: bool = QUIET,
) -> None:
    """Scan a Microsoft 365 tenant (or a mock fixture) and write a findings file."""
    load_dotenv()
    connector: Connector
    if snapshot_file is not None:
        connector = MockConnector(Platform.m365, path=snapshot_file)
    elif mock:
        connector = MockConnector(Platform.m365, fixture=fixture)
    else:
        _refuse_unauthorized(authorized)
        from .connectors.m365 import GraphConnector, GraphError

        try:
            connector = GraphConnector.from_env(dns=not no_dns)
        except GraphError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=2) from exc
    _scan(Platform.m365, connector, checks_file=checks_file, out=out, save_snapshot=save_snapshot, quiet=quiet)


@app.command()
def gws(
    mock: bool = MOCK,
    fixture: str = FIXTURE,
    snapshot_file: Path | None = SNAPSHOT,
    authorized: bool = AUTHORIZED,
    out: Path | None = OUT,
    checks_file: Path | None = CHECKS_FILE,
    save_snapshot: bool = SAVE_SNAPSHOT,
    no_dns: bool = NO_DNS,
    approved_app: list[str] = typer.Option(
        [], "--approved-app", help="OAuth client id of a third-party app the company has approved. Repeatable; or GWS_APPROVED_CLIENT_IDS in .env."
    ),
    quiet: bool = QUIET,
) -> None:
    """Scan a Google Workspace tenant (or a mock fixture) and write a findings file."""
    load_dotenv()
    connector: Connector
    if snapshot_file is not None:
        connector = MockConnector(Platform.gws, path=snapshot_file)
    elif mock:
        connector = MockConnector(Platform.gws, fixture=fixture)
    else:
        _refuse_unauthorized(authorized)
        from .connectors.gws import GoogleError, GoogleWorkspaceConnector

        try:
            connector = GoogleWorkspaceConnector.from_env(dns=not no_dns, approved_client_ids=approved_app)
        except GoogleError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=2) from exc
    _scan(
        Platform.gws,
        connector,
        checks_file=checks_file,
        out=out,
        save_snapshot=save_snapshot,
        quiet=quiet,
        approved_client_ids=approved_app,
    )


def _print_result(result: ScanResult) -> None:
    title = result.tenant.display_name or result.tenant.primary_domain or "tenant"
    console.print(f"\n[bold]{title}[/bold]  source: {result.tenant.source}  collected: {result.collected_at:%Y-%m-%d %H:%M} UTC")
    table = Table(show_lines=False, pad_edge=False, expand=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Severity", no_wrap=True)
    table.add_column("Check", ratio=2)
    table.add_column("What we found", ratio=4)
    for finding in result.findings:
        style = STATUS_STYLE[finding.status]
        table.add_row(
            f"[{style}]{finding.status.value}[/{style}]",
            finding.severity.value,
            finding.title,
            finding.summary,
        )
    console.print(table)
    summary = result.summary
    score = f"{summary.score_percent}%" if summary.score_percent is not None else "n/a"
    console.print(
        f"Score {score}  pass {summary.passed}  fail {summary.failed}  "
        f"attestation needed {summary.attestation_needed}  error {summary.errors}"
    )
    answers = Table(title="What your insurer will ask", show_lines=False)
    answers.add_column("Answer", no_wrap=True)
    answers.add_column("Question")
    for answer in result.insurer_answers:
        style = {"pass": "green", "fail": "red", "attestation_needed": "yellow"}.get(answer.status, "magenta")
        answers.add_row(f"[{style}]{answer.status}[/{style}]", answer.question_text)
    console.print(answers)
    if result.notes:
        console.print("[dim]Notes:[/dim]")
        for note in result.notes:
            console.print(f"[dim]  - {note}[/dim]")


@app.command()
def checks(
    platform: str | None = typer.Option(None, "--platform", "-p", help="m365, gws or any."),
    checks_file: Path | None = CHECKS_FILE,
) -> None:
    """List the checks in config/checks.yaml and whether each has an implementation."""
    catalog = load_catalog(checks_file)
    implemented = set(registered_ids())
    table = Table(title=f"checks from {catalog.source}")
    for column in ("Id", "Platform", "Kind", "Severity", "Insurer question", "Implemented"):
        table.add_column(column)
    for check in catalog.checks:
        if platform and check.platform.value != platform:
            continue
        done = "yes" if check.id in implemented else ("n/a" if check.kind.value == "attestation" else "[red]no[/red]")
        table.add_row(check.id, check.platform.value, check.kind.value, check.severity.value, check.insurer_question, done)
    console.print(table)


@app.command()
def fixtures(platform: str = typer.Argument("m365", help="m365 or gws.")) -> None:
    """List the mock fixtures available for a platform."""
    names = list_fixtures(platform)
    if not names:
        console.print(f"No fixtures for {platform}.")
        return
    for name in names:
        typer.echo(name)


@app.command()
def permissions(platform: str = typer.Option("m365", "--platform", "-p", help="m365 or gws.")) -> None:
    """Print the read-only permissions (Graph) or OAuth scopes (Google) a real scan needs."""
    if Platform(platform) == Platform.gws:
        from .connectors.gws import SCOPES

        table = Table(
            title="Google OAuth scopes to delegate to the service account (all read-only), each under https://www.googleapis.com/auth/",
            expand=True,
        )
        table.add_column("Scope", overflow="fold", ratio=3)
        table.add_column("Used for", ratio=3)
        table.add_column("Calls", ratio=2)
        for scope, purpose, calls in SCOPES:
            table.add_row(scope.removeprefix("https://www.googleapis.com/auth/"), purpose, calls)
    else:
        from .connectors.m365 import PERMISSIONS

        table = Table(title="Microsoft Graph application permissions (all read-only)")
        table.add_column("Permission", no_wrap=True)
        table.add_column("Used for")
        table.add_column("Calls")
        for name, purpose, calls in PERMISSIONS:
            table.add_row(name, purpose, calls)
    console.print(table)


@app.command()
def version() -> None:
    """Print the scanner version."""
    typer.echo(f"alimi-scanner {__version__}")


def _main() -> None:  # pragma: no cover - console entry point
    app()


if __name__ == "__main__":  # pragma: no cover
    _main()


__all__ = ["app"]
