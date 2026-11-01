"""render(): findings in, HTML (and optionally PDF) out. The platform calls this; the CLI wraps it."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from alimi_scanner.catalog import Catalog, load_catalog
from alimi_scanner.schema import ScanResult
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .brand import Brand, Offer, Reseller, load_brand, load_offer
from .model import ReportModel, build_model

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "j2"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass
class Report:
    html: str
    model: ReportModel


@dataclass
class ReportPaths:
    html: Path
    pdf: Path | None = None


def load_result(source: ScanResult | dict[str, Any] | str | Path) -> ScanResult:
    """Accept a ScanResult, a dict, a JSON string, or a path to a findings file."""
    if isinstance(source, ScanResult):
        return source
    if isinstance(source, dict):
        return ScanResult.model_validate(source)
    if isinstance(source, Path) or (isinstance(source, str) and not source.lstrip().startswith("{")):
        return ScanResult.model_validate_json(Path(source).read_text(encoding="utf-8"))
    return ScanResult.model_validate_json(source)


def _catalog(catalog: Catalog | Path | None) -> Catalog | None:
    if isinstance(catalog, Catalog):
        return catalog
    try:
        return load_catalog(catalog)
    except FileNotFoundError:
        return None  # the report still renders; "why it matters" lines are left out


def render(
    source: ScanResult | dict[str, Any] | str | Path,
    *,
    free: bool = False,
    reseller: Reseller | None = None,
    brand: Brand | Path | None = None,
    offer: Offer | Path | None = None,
    catalog: Catalog | Path | None = None,
    now: datetime | None = None,
) -> Report:
    result = load_result(source)
    brand_obj = brand if isinstance(brand, Brand) else load_brand(brand)
    offer_obj = offer if isinstance(offer, Offer) else load_offer(offer)
    model = build_model(
        result,
        brand=brand_obj,
        offer=offer_obj,
        catalog=_catalog(catalog),
        reseller=reseller,
        free=free,
        now=now,
    )
    html = _env.get_template("report.html.j2").render(m=model)
    return Report(html=html, model=model)


def render_html(source: ScanResult | dict[str, Any] | str | Path, **options: Any) -> str:
    return render(source, **options).html


def write_report(
    source: ScanResult | dict[str, Any] | str | Path,
    out_dir: Path,
    *,
    basename: str | None = None,
    pdf: bool = True,
    **options: Any,
) -> ReportPaths:
    """Write <basename>.html and, when a PDF backend is available, <basename>.pdf into out_dir."""
    report = render(source, **options)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = basename or _default_basename(report.model)
    html_path = out_dir / f"{stem}.html"
    html_path.write_text(report.html, encoding="utf-8")
    pdf_path = None
    if pdf:
        from .pdf import html_to_pdf

        pdf_path = out_dir / f"{stem}.pdf"
        html_to_pdf(report.html, pdf_path)
    return ReportPaths(html=html_path, pdf=pdf_path)


def _default_basename(model: ReportModel) -> str:
    safe = re.sub(r"-+", "-", "".join(ch if ch.isalnum() else "-" for ch in model.tenant_name.lower())).strip("-") or "tenant"
    kind = "summary" if model.free else "report"
    return f"{safe}-{model.platform_label.lower().replace(' ', '')}-{kind}-{model.collected_at:%Y%m%d}"


__all__ = ["Report", "ReportPaths", "load_result", "render", "render_html", "write_report", "json"]
