"""The two themes are served from config/brand.yaml, and app.css types no color of its own."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from alimi_platform.config import REPO_ROOT, ConfigError
from alimi_platform.theme import DARK_SELECTORS, VARIABLES, theme_css

CSS = Path(__file__).resolve().parents[1] / "alimi_platform" / "static" / "app.css"
BRAND = yaml.safe_load((REPO_ROOT / "config" / "brand.yaml").read_text())
DECL = re.compile(r"--([a-z-]+):(#[0-9A-Fa-f]{6})")


def _blocks(css: str) -> tuple[str, str, str]:
    """The light block, the device-query dark block and the chosen-dark block, in that order."""
    light_end = css.index("}")
    light = css[: light_end + 1]
    rest = css[light_end + 1 :]
    assert rest.startswith(DARK_SELECTORS[0]), "the device query comes first"
    device_end = rest.index("}}") + 2
    device = rest[:device_end]
    chosen = rest[device_end:]
    assert chosen.startswith(DARK_SELECTORS[1]) and chosen.endswith("}")
    return light, device, chosen


def test_theme_css_carries_both_themes_from_brand_yaml():
    css = theme_css(BRAND)
    light, device, chosen = _blocks(css)
    assert light.startswith(":root{") and "color-scheme:light" in light
    assert "color-scheme:dark" in device and "color-scheme:dark" in chosen
    for block, colors in ((light, BRAND["colors"]), (device, BRAND["colors_dark"]), (chosen, BRAND["colors_dark"])):
        declared = dict(DECL.findall(block))
        assert set(declared) == set(VARIABLES), sorted(set(declared) ^ set(VARIABLES))
        for var, key in VARIABLES.items():
            assert declared[var].upper() == str(colors[key]).upper(), f"--{var} is {declared[var]}, brand.yaml {key} is {colors[key]}"
    # The chosen-dark block repeats the device block's declarations exactly.
    assert DECL.findall(device) == DECL.findall(chosen)


def test_dark_keys_must_mirror_the_light_keys():
    broken = {"colors": BRAND["colors"], "colors_dark": {k: v for k, v in BRAND["colors_dark"].items() if k != "primary"}}
    with pytest.raises(ConfigError, match="missing: primary"):
        theme_css(broken)
    reordered = {"colors": BRAND["colors"], "colors_dark": dict(reversed(list(BRAND["colors_dark"].items())))}
    with pytest.raises(ConfigError, match="same order"):
        theme_css(reordered)


def test_light_only_brand_still_works():
    css = theme_css({"colors": BRAND["colors"]})
    assert css.startswith(":root{") and "color-scheme:light" in css and "data-theme" not in css


def test_app_css_types_no_color():
    assert not re.search(r"#[0-9A-Fa-f]{3,6}\b|rgb\(|hsl\(", CSS.read_text()), "a color is typed in app.css; it belongs in config/brand.yaml"


def test_stylesheet_is_served_before_app_css(client):
    r = client.get("/theme.css")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/css")
    assert r.text == theme_css(BRAND)
    page = client.get("/login").text
    assert page.index('href="/theme.css"') < page.index('href="/static/app.css"')
    assert '<script src="/static/theme.js"></script>' in page  # no defer: runs before the first paint
