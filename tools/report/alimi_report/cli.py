"""alimi-report: render findings JSON into the insurer-ready report. Mock findings via `demo`."""

from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console

from . import __version__
from .brand import Reseller
from .pdf import PdfUnavailable, pdf_backend
from .render import write_report

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="alimi report: turn scanner findings into an insurer-ready HTML and PDF report.",
)
console = Console()

OUT = typer.Option(None, "--out", "-o", help="Output folder. Default: $ALIMI_OUTPUT_DIR or ./out (git-ignored).")
FREE = typer.Option(False, "--free", help="Render only the one-page summary (the free tier).")
RESELLER_NAME = typer.Option(None, "--reseller-name", help="Partner name for the cover of a white-label report.")
RESELLER_LOGO = typer.Option(None, "--reseller-logo", help="Path to the partner's logo (PNG or SVG), embedded in the HTML.")
RESELLER_CONTACT = typer.Option(None, "--reseller-contact", help="Partner contact line (email or phone) for the cover and the call to action.")
PDF = typer.Option(True, "--pdf/--no-pdf", help="Also write a PDF (needs WeasyPrint: pip install 'alimi-report[pdf]').")
BRAND = typer.Option(None, "--brand", help="Path to brand.yaml. Default: config/brand.yaml in the repo.")
CHECKS = typer.Option(None, "--checks", help="Path to checks.yaml, for the 'why it matters' lines. Default: config/checks.yaml.")
QUIET = typer.Option(False, "--quiet", "-q", help="Print only the output paths.")


def _output_dir(out: Path | None) -> Path:
    return out or Path(os.environ.get("ALIMI_OUTPUT_DIR", "out"))


def _reseller(name: str | None, logo: Path | None, contact: str | None) -> Reseller | None:
    if not name:
        if logo or contact:
            console.print("[red]--reseller-logo and --reseller-contact need --reseller-name.[/red]")
            raise typer.Exit(code=2)
        return None
    return Reseller(name=name, logo=logo, contact=contact)


def _write(source, out: Path | None, *, free: bool, reseller: Reseller | None, pdf: bool, brand: Path | None, checks: Path | None, quiet: bool, basename: str | None = None) -> None:
    try:
        paths = write_report(source, _output_dir(out), basename=basename, pdf=pdf, free=free, reseller=reseller, brand=brand, catalog=checks)
    except PdfUnavailable as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        paths = write_report(source, _output_dir(out), basename=basename, pdf=False, free=free, reseller=reseller, brand=brand, catalog=checks)
    if quiet:
        typer.echo(str(paths.html))
        if paths.pdf:
            typer.echo(str(paths.pdf))
        return
    console.print(f"Report written to [bold]{paths.html}[/bold]")
    if paths.pdf:
        console.print(f"PDF written to [bold]{paths.pdf}[/bold]")
    elif pdf:
        console.print("[dim]No PDF this time; the HTML prints to PDF from any browser.[/dim]")


@app.command()
def render(
    findings: Path = typer.Argument(..., help="A *.findings.json file written by alimi-scan.", exists=True, readable=True),
    out: Path | None = OUT,
    free: bool = FREE,
    reseller_name: str | None = RESELLER_NAME,
    reseller_logo: Path | None = RESELLER_LOGO,
    reseller_contact: str | None = RESELLER_CONTACT,
    pdf: bool = PDF,
    brand: Path | None = BRAND,
    checks: Path | None = CHECKS,
    basename: str | None = typer.Option(None, "--name", help="Output file name without extension. Default: tenant, platform, kind and date."),
    quiet: bool = QUIET,
) -> None:
    """Render one findings file into HTML (and PDF)."""
    _write(findings, out, free=free, reseller=_reseller(reseller_name, reseller_logo, reseller_contact), pdf=pdf, brand=brand, checks=checks, quiet=quiet, basename=basename)


@app.command()
def demo(
    platform: str = typer.Option("m365", "--platform", "-p", help="m365 or gws."),
    fixture: str = typer.Option("fail", "--fixture", "-f", help="Scanner fixture to run: pass or fail."),
    out: Path | None = OUT,
    free: bool = FREE,
    reseller_name: str | None = RESELLER_NAME,
    reseller_logo: Path | None = RESELLER_LOGO,
    reseller_contact: str | None = RESELLER_CONTACT,
    pdf: bool = PDF,
    brand: Path | None = BRAND,
    checks: Path | None = CHECKS,
    quiet: bool = QUIET,
) -> None:
    """Render a report from the scanner's mock fixtures, to see what a client gets."""
    from alimi_scanner.catalog import load_catalog
    from alimi_scanner.connectors.mock import MockConnector
    from alimi_scanner.engine import run_checks
    from alimi_scanner.schema import Platform, TenantInfo

    plat = Platform(platform)
    connector = MockConnector(plat, fixture=fixture)
    snapshot = connector.fetch()
    tenant = TenantInfo(display_name=snapshot.tenant_display_name, primary_domain=snapshot.primary_domain(), source=connector.source)
    result = run_checks(snapshot, load_catalog(checks), plat, tenant)
    _write(result, out, free=free, reseller=_reseller(reseller_name, reseller_logo, reseller_contact), pdf=pdf, brand=brand, checks=checks, quiet=quiet)


@app.command()
def backends() -> None:
    """Say whether a PDF backend is installed."""
    found = pdf_backend()
    typer.echo(f"PDF backend: {found or 'none (pip install alimi-report[pdf])'}")


@app.command()
def version() -> None:
    """Print the report version."""
    typer.echo(f"alimi-report {__version__}")


def _main() -> None:  # pragma: no cover - console entry point
    app()


if __name__ == "__main__":  # pragma: no cover
    _main()
