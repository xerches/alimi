// Proves the pairings the stylesheet relies on. Text needs 4.5:1 (WCAG AA); controls, focus rings
// and large decorative marks need 3:1. If a token changes in brand.yaml and breaks a pairing, the
// build fails here before the page ships.
import test from "node:test";
import assert from "node:assert/strict";
import { brand } from "../src/lib/config.js";
import { contrast } from "../src/lib/contrast.js";

const c = brand.colors;
const text = [
  // [foreground, background, where]
  ["text", "background", "body text on the page"],
  ["text", "background_alt", "body text on alternate sections"],
  ["text", "surface", "body text on cards"],
  ["text_secondary", "background", "secondary text on the page"],
  ["text_secondary", "surface", "secondary text on cards"],
  ["text_muted", "background", "muted text on the page"],
  ["text_muted", "background_alt", "muted text on alternate sections"],
  ["text_muted", "surface", "muted text on cards"],
  ["primary", "background", "links and eyebrows on the page"],
  ["primary", "background_alt", "links on alternate sections"],
  ["primary", "surface", "links on cards"],
  ["primary_hover", "background", "hovered links"],
  ["primary_active", "background", "active links"],
  ["primary", "primary_soft", "service badge and brand callout label"],
  ["text", "primary_soft", "text in brand callouts"],
  ["text_inverse", "primary", "primary button label"],
  ["text_inverse", "primary_hover", "hovered primary button label"],
  ["text_inverse", "primary_active", "pressed primary button label"],
  ["secondary", "secondary_soft", "product badge"],
  ["text_inverse", "secondary", "text on dark bands and the header"],
  ["text_inverse_muted", "secondary", "muted text on dark bands"],
  ["text_inverse", "surface_dark", "text on dark cards"],
  ["text_inverse_muted", "surface_dark", "muted text on dark cards"],
  ["primary_on_dark", "secondary", "links on dark bands"],
  ["primary_on_dark_hover", "secondary", "hovered links on dark bands"],
  ["primary_on_dark", "surface_dark", "links on dark cards"],
  ["text", "primary_on_dark", "button label on dark bands"],
  ["text", "primary_on_dark_hover", "hovered button label on dark bands"],
  ["accent", "secondary", "eyebrow on dark bands"],
  ["text_inverse", "background_dark", "footer headings and links"],
  ["text_inverse_muted", "background_dark", "footer text"],
  ["primary_on_dark_hover", "background_dark", "hovered footer links"],
  ["success", "success_soft", "success callout label"],
  ["warning", "warning_soft", "warning callout label and TODO markers"],
  ["danger", "danger_soft", "error callout label"],
  ["info", "info_soft", "info callout label"],
  ["text", "success_soft", "text in success callouts"],
  ["text", "warning_soft", "text in warning callouts"],
  ["text", "danger_soft", "text in error callouts"],
  ["text", "info_soft", "text in info callouts"],
  ["success", "surface", "check marks in lists"],
  ["warning", "background", "warning text on the page"],
  ["danger", "surface", "error text on cards"],
];
const nonText = [
  ["border_strong", "surface", "form field edges"],
  ["focus_ring", "background", "focus ring on the page"],
  ["focus_ring", "surface", "focus ring on cards"],
  ["focus_ring", "background_alt", "focus ring on alternate sections"],
  ["focus_ring_on_dark", "secondary", "focus ring on dark bands"],
  ["focus_ring_on_dark", "background_dark", "focus ring in the footer"],
  ["accent", "secondary", "current-page underline in the header"],
  ["primary", "surface", "hovered card border"],
  ["accent_deep", "background", "gold decoration on light surfaces"],
];

for (const [fg, bg, where] of text) {
  test(`${where}: ${fg} on ${bg} is at least 4.5:1`, () => {
    assert.ok(c[fg] && c[bg], `missing token ${fg} or ${bg}`);
    const ratio = contrast(c[fg], c[bg]);
    assert.ok(ratio >= 4.5, `${fg} on ${bg} is ${ratio.toFixed(2)}:1`);
  });
}

for (const [fg, bg, where] of nonText) {
  test(`${where}: ${fg} on ${bg} is at least 3:1`, () => {
    const ratio = contrast(c[fg], c[bg]);
    assert.ok(ratio >= 3, `${fg} on ${bg} is ${ratio.toFixed(2)}:1`);
  });
}

test("the error color is distinct from the brand color", () => {
  assert.notEqual(c.danger.toUpperCase(), c.primary.toUpperCase());
  assert.ok(contrast(c.danger, c.primary) < 1.6, "they should be close in lightness but different in hue");
});
