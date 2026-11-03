"""The two themes, generated from config/brand.yaml when the app starts.

Why generate rather than type: the site builds its CSS variables from brand.yaml and the demo
copies the same helper, so the brand file is the one place a color lives. The platform used to
type the values in app.css and test them for drift; serving them from the yaml removes the
copy. `colors` is the light theme and the default; `colors_dark` (same keys, same order, Nov 3,
2026) applies when the device asks for a dark scheme and the person has not chosen light, or
when the person chose dark with the toggle in the top bar (static/theme.js sets data-theme).

app.css never types a color: it uses the variables below, and tests/test_theme.py fails if a hex
value appears in it.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .config import ConfigError

# CSS variable -> key under colors: (and colors_dark:) in config/brand.yaml. Only what the app uses.
VARIABLES: dict[str, str] = {
    "primary": "primary",
    "primary-hover": "primary_hover",
    "primary-soft": "primary_soft",
    "primary-contrast": "primary_contrast",
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

# The same selectors the site uses (site/src/lib/theme.js), so a choice behaves the same on both.
DARK_SELECTORS = ('@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){', ':root[data-theme="dark"]{')


def load_brand(repo_root: Path) -> dict:
    return yaml.safe_load((repo_root / "config" / "brand.yaml").read_text(encoding="utf-8"))


def _declarations(colors: dict, theme: str) -> str:
    out = []
    for var, key in VARIABLES.items():
        if key not in colors:
            raise ConfigError(f"config/brand.yaml {theme} has no '{key}' (needed for --{var})")
        out.append(f"--{var}:{colors[key]}")
    return ";".join(out)


def theme_css(brand: dict) -> str:
    """One stylesheet: the light variables on :root, the dark ones under the device query and the choice."""
    light = brand["colors"]
    dark = brand.get("colors_dark")
    if not dark:
        return f":root{{{_declarations(light, 'colors')};color-scheme:light}}"
    if list(light) != list(dark):
        missing = [k for k in light if k not in dark]
        extra = [k for k in dark if k not in light]
        raise ConfigError(
            "config/brand.yaml colors_dark must list the same keys as colors, in the same order "
            f"(missing: {', '.join(missing) or 'none'}; extra: {', '.join(extra) or 'none'})"
        )
    light_block = f":root{{{_declarations(light, 'colors')};color-scheme:light}}"
    dark_block = f"{_declarations(dark, 'colors_dark')};color-scheme:dark}}"
    return light_block + DARK_SELECTORS[0] + dark_block + "}" + DARK_SELECTORS[1] + dark_block
