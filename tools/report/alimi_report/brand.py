"""Brand tokens from config/brand.yaml, and the optional reseller block for white-label reports."""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

ENV_BRAND = "ALIMI_BRAND"
ENV_PRICING = "ALIMI_PRICING"

# Keys match config/brand.yaml. The cover uses the dark "secondary" band tokens; highlights use primary.
DEFAULT_COLORS = {
    "primary": "#9A3B1E",
    "secondary": "#15302E",
    "text_inverse": "#FAF7F1",
    "text_inverse_muted": "#B7C0BE",
    "warning": "#8A5A00",
    "danger": "#B01E2B",
    "success": "#1F6B43",
}


class Brand(BaseModel):
    name: str = "Alimi"
    display_name: str = "Alimi"
    tagline: str = ""
    founder: str | None = None
    location: str | None = None
    domain: str | None = None
    contact_email: str | None = None
    colors: dict[str, str] = Field(default_factory=lambda: dict(DEFAULT_COLORS))
    typography: dict[str, str] = Field(default_factory=dict)

    def color(self, key: str) -> str:
        return self.colors.get(key) or DEFAULT_COLORS[key]

    @property
    def font(self) -> str:
        return self.typography.get("body") or "Inter, system-ui, sans-serif"

    @property
    def heading_font(self) -> str:
        return self.typography.get("heading") or self.font


class Reseller(BaseModel):
    """A partner's name and logo on the cover, with a "powered by Alimi" line underneath."""

    name: str
    logo: Path | None = None
    contact: str | None = None
    powered_by: bool = True

    def logo_data_uri(self) -> str | None:
        if self.logo is None:
            return None
        path = Path(self.logo)
        if not path.is_file():
            raise FileNotFoundError(f"reseller logo not found: {path}")
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _walk_up_for(relative: str, start: Path | None = None) -> Path | None:
    here = (start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        candidate = folder / relative
        if candidate.is_file():
            return candidate
    package_root = Path(__file__).resolve().parents[3]  # tools/report/alimi_report -> repo root
    candidate = package_root / relative
    return candidate if candidate.is_file() else None


def find_brand_file(path: Path | None = None) -> Path | None:
    if path is not None:
        if not Path(path).is_file():
            raise FileNotFoundError(f"brand file not found: {path}")
        return Path(path)
    env = os.environ.get(ENV_BRAND)
    if env:
        return find_brand_file(Path(env))
    return _walk_up_for("config/brand.yaml")


def _clean(value: Any) -> Any:
    """TODO placeholders in brand.yaml mean "not decided yet"; treat them as absent."""
    if isinstance(value, str) and value.strip().upper() == "TODO":
        return None
    return value


def load_brand(path: Path | None = None) -> Brand:
    source = find_brand_file(path)
    if source is None:
        return Brand()
    raw = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    colors = dict(DEFAULT_COLORS)
    colors.update({k: v for k, v in (raw.get("colors") or {}).items() if isinstance(v, str)})
    return Brand(
        name=_clean(raw.get("name")) or "Alimi",
        display_name=_clean(raw.get("display_name")) or _clean(raw.get("name")) or "Alimi",
        tagline=_clean(raw.get("tagline")) or "",
        founder=_clean(raw.get("founder")),
        location=_clean(raw.get("location")),
        domain=_clean(raw.get("domain")),
        contact_email=_clean(raw.get("contact_email")),
        colors=colors,
        typography={k: v for k, v in (raw.get("typography") or {}).items() if isinstance(v, str)},
    )


def find_pricing_file(path: Path | None = None) -> Path | None:
    if path is not None:
        return Path(path) if Path(path).is_file() else None
    env = os.environ.get(ENV_PRICING)
    if env:
        return find_pricing_file(Path(env))
    return _walk_up_for("config/pricing.yaml")


class Offer(BaseModel):
    """What the free summary points to: the paid assessment (the full report) and the service, with their starting prices."""

    report_name: str = "Security assessment and insurer report"
    report_from: int | None = None
    report_includes: list[str] = Field(default_factory=list)
    service_name: str = "Insurance-ready in 30 days"
    service_from: int | None = None
    currency: str = "USD"


def load_offer(path: Path | None = None) -> Offer:
    source = find_pricing_file(path)
    if source is None:
        return Offer()
    raw = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    offer = Offer(currency=raw.get("currency") or "USD")
    # pricing.yaml v2 (Nov 1, 2026): the paid report is the "assessment" service and the fix-it
    # engagement is "insurance_ready_30", both under products.services.
    tiers = ((raw.get("products") or {}).get("services") or {}).get("tiers") or []
    for tier in tiers:
        low = (tier.get("range") or [None])[0]
        if tier.get("id") == "assessment":
            offer.report_name = tier.get("name") or offer.report_name
            offer.report_from = low
            offer.report_includes = list(tier.get("includes") or [])
        elif tier.get("id") == "insurance_ready_30":
            offer.service_name = tier.get("name") or offer.service_name
            offer.service_from = low
    return offer
