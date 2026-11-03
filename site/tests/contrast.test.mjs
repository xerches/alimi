// Proves the pairings the stylesheet relies on, in both themes. Text needs 4.5:1 (WCAG AA); controls,
// focus rings and large decorative marks need 3:1. If a token changes in brand.yaml and breaks a
// pairing, the build fails here before the page ships.
import test from "node:test";
import assert from "node:assert/strict";
import { brand } from "../src/lib/config.js";
import { contrast } from "../src/lib/contrast.js";

const text = [
  // [foreground, background, where]
  ["text", "background", "body text on the page"],
  ["text", "background_alt", "body text on alternate sections"],
  ["text", "surface", "body text on cards"],
  ["text_secondary", "background", "secondary text on the page"],
  ["text_secondary", "surface", "secondary text on cards"],
  ["text_secondary", "background_alt", "the theme toggle label"],
  ["text_muted", "background", "muted text on the page"],
  ["text_muted", "background_alt", "muted text on alternate sections"],
  ["text_muted", "surface", "muted text on cards"],
  ["primary", "background", "links and eyebrows on the page"],
  ["primary", "background_alt", "links on alternate sections"],
  ["primary", "surface", "links on cards"],
  ["primary_hover", "background", "hovered links"],
  ["primary_active", "background", "active links"],
  ["primary", "primary_soft", "service badge, brand callout label and the pressed theme toggle"],
  ["text", "primary_soft", "text in brand callouts"],
  ["primary_contrast", "primary", "primary button label and list counters"],
  ["primary_contrast", "primary_hover", "hovered primary button label"],
  ["primary_contrast", "primary_active", "pressed primary button label"],
  ["text_secondary", "secondary_soft", "product badge and framework tags"],
  ["text_inverse", "secondary", "text on dark bands and the count block"],
  ["text_inverse_muted", "secondary", "muted text on dark bands"],
  ["text_inverse", "surface_dark", "text on dark cards"],
  ["text_inverse_muted", "surface_dark", "muted text on dark cards"],
  ["primary_on_dark", "secondary", "links on dark bands"],
  ["primary_on_dark_hover", "secondary", "hovered links on dark bands"],
  ["primary_on_dark", "surface_dark", "links on dark cards"],
  ["primary_on_dark_contrast", "primary_on_dark", "button label on dark bands and the Contact item"],
  ["primary_on_dark_contrast", "primary_on_dark_hover", "hovered button label on dark bands"],
  ["accent", "secondary", "eyebrow and the accent line on dark bands"],
  ["text_inverse", "background_dark", "footer headings, the brand and the frame bar"],
  ["text_inverse_muted", "background_dark", "footer text and the strip's captions"],
  ["primary_on_dark_hover", "background_dark", "hovered footer links"],
  ["primary_on_dark", "background_dark", "links and the brand mark on the header strip"],
  ["background_dark", "primary_on_dark", "the letter in the brand mark"],
  ["text_inverse", "surface_dark", "the current menu item on the header strip"],
  ["text_inverse_muted", "surface_dark", "muted text on the active strip surface"],
  ["primary", "primary_soft", "the current page in an open menu"],
  ["success", "success_soft", "success callout label and Ok pills"],
  ["warning", "warning_soft", "warning callout label, TODO markers and warning pills"],
  ["danger", "danger_soft", "error callout label and failing pills"],
  ["info", "info_soft", "info callout label and info pills"],
  ["text", "success_soft", "text in success callouts"],
  ["text", "warning_soft", "text in warning callouts"],
  ["text", "danger_soft", "text in error callouts"],
  ["text", "info_soft", "text in info callouts"],
  ["success", "surface", "check marks in lists"],
  ["warning", "background", "warning text on the page"],
  ["danger", "surface", "error text on cards"],
];
const nonText = [
  ["border_strong", "surface", "form field edges and the theme toggle's edge"],
  ["focus_ring", "background", "focus ring on the page"],
  ["focus_ring", "surface", "focus ring on cards"],
  ["focus_ring", "background_alt", "focus ring on alternate sections"],
  ["focus_ring_on_dark", "secondary", "focus ring on dark bands"],
  ["focus_ring_on_dark", "background_dark", "focus ring in the footer"],
  ["accent", "secondary", "current-page underline in the header"],
  ["primary_on_dark", "background_dark", "current-page bar on the header strip"],
  ["primary_on_dark", "surface_dark", "current-page bar on the active strip item"],
  ["accent_deep", "surface", "colored top edge of a score tile"],
  ["primary", "surface", "colored top edge of a score tile and the readiness bar"],
  ["primary", "primary_soft", "the readiness bar on its track"],
  ["border_strong", "surface", "breadcrumb separators"],
  ["primary", "surface", "hovered card border"],
  ["accent_deep", "background", "gold decoration on the page"],
];

const themes = [
  ["light", brand.colors],
  ["dark", brand.colors_dark],
];

test("both themes list the same tokens", () => {
  assert.deepEqual(Object.keys(brand.colors_dark), Object.keys(brand.colors));
});

for (const [theme, c] of themes) {
  for (const [fg, bg, where] of text) {
    test(`${theme}: ${where}: ${fg} on ${bg} is at least 4.5:1`, () => {
      assert.ok(c[fg] && c[bg], `missing token ${fg} or ${bg}`);
      const ratio = contrast(c[fg], c[bg]);
      assert.ok(ratio >= 4.5, `${fg} on ${bg} is ${ratio.toFixed(2)}:1`);
    });
  }

  for (const [fg, bg, where] of nonText) {
    test(`${theme}: ${where}: ${fg} on ${bg} is at least 3:1`, () => {
      const ratio = contrast(c[fg], c[bg]);
      assert.ok(ratio >= 3, `${fg} on ${bg} is ${ratio.toFixed(2)}:1`);
    });
  }

  test(`${theme}: the error color is distinct from the brand color`, () => {
    assert.notEqual(c.danger.toUpperCase(), c.primary.toUpperCase());
    assert.ok(contrast(c.danger, c.primary) < 1.6, "they should be close in lightness but different in hue");
  });

  test(`${theme}: cards sit a step apart from the canvas and dark bands a step apart from the page`, () => {
    assert.notEqual(c.surface.toUpperCase(), c.background_alt.toUpperCase());
    assert.notEqual(c.secondary.toUpperCase(), c.background_alt.toUpperCase());
    assert.notEqual(c.background_dark.toUpperCase(), c.background_alt.toUpperCase());
  });
}
