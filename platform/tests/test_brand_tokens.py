"""static/app.css types the brand colors once, in :root. This test keeps them equal to config/brand.yaml,
the same rule the site and the demo enforce at build time."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from alimi_platform.config import REPO_ROOT

CSS = Path(__file__).resolve().parents[1] / "alimi_platform" / "static" / "app.css"

# CSS variable -> key under colors: in config/brand.yaml
TOKENS = {
    "primary": "primary",
    "primary-hover": "primary_hover",
    "primary-soft": "primary_soft",
    "on-dark": "primary_on_dark",
    "secondary": "secondary",
    "secondary-soft": "secondary_soft",
    "bg": "background",
    "bg-alt": "background_alt",
    "bg-dark": "background_dark",
    "surface": "surface",
    "surface-dark": "surface_dark",
    "text": "text",
    "text-secondary": "text_secondary",
    "muted": "text_muted",
    "inverse": "text_inverse",
    "inverse-muted": "text_inverse_muted",
    "border": "border",
    "border-strong": "border_strong",
    "border-dark": "border_dark",
    "accent": "accent",
    "accent-deep": "accent_deep",
    "success": "success",
    "success-soft": "success_soft",
    "warning": "warning",
    "warning-soft": "warning_soft",
    "danger": "danger",
    "danger-soft": "danger_soft",
    "info": "info",
    "info-soft": "info_soft",
    "focus-ring": "focus_ring",
    "focus-ring-on-dark": "focus_ring_on_dark",
}


def test_css_tokens_match_brand_yaml():
    css = CSS.read_text()
    root = css[css.index(":root {") : css.index("}", css.index(":root {"))]
    declared = dict(re.findall(r"--([a-z-]+):\s*(#[0-9A-Fa-f]{6})", root))
    brand = yaml.safe_load((REPO_ROOT / "config" / "brand.yaml").read_text())["colors"]
    unknown = set(declared) - set(TOKENS)
    assert not unknown, f"map these variables to brand.yaml keys in TOKENS: {sorted(unknown)}"
    for var, key in TOKENS.items():
        assert var in declared, f"--{var} missing from :root"
        assert declared[var].upper() == str(brand[key]).upper(), f"--{var} is {declared[var]}, brand.yaml {key} is {brand[key]}"


def test_no_color_is_typed_outside_the_token_block():
    css = CSS.read_text()
    after_root = css[css.index("}", css.index(":root {")) :]
    assert not re.search(r"#[0-9A-Fa-f]{3,6}\b|rgb\(|hsl\(", after_root), "a color is typed outside :root"
