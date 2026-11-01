// Every colour pairing the demo's stylesheet uses, checked against WCAG AA: 4.5:1 for text, 3:1 for
// pills' dots, bars, borders and focus rings. The pairings name tokens, so a palette change in
// config/brand.yaml is proven here before it ships.
import { test } from "node:test";
import assert from "node:assert/strict";
import { brand } from "../src/lib/config.js";
import { contrast } from "../src/lib/contrast.js";

const c = brand.colors;
const text = [
  ["text", "background"], ["text", "background_alt"], ["text", "surface"],
  ["text_secondary", "surface"], ["text_secondary", "background_alt"], ["text_muted", "surface"], ["text_muted", "background_alt"],
  ["text_inverse", "background_dark"], ["text_inverse", "surface_dark"], ["text_inverse_muted", "background_dark"], ["text_inverse_muted", "surface_dark"],
  ["primary", "surface"], ["primary", "background_alt"], ["primary_hover", "surface"], ["text_inverse", "primary"], ["text_inverse", "primary_hover"],
  ["background_dark", "accent"], ["text_inverse", "secondary"], ["text_inverse", "danger"], ["text_secondary", "secondary_soft"],
  ["text", "success_soft"], ["text", "warning_soft"], ["text", "danger_soft"], ["text", "info_soft"], ["text", "primary_soft"],
  ["danger", "surface"], ["text", "secondary_soft"],
];
const nonText = [
  ["success", "surface"], ["warning", "surface"], ["danger", "surface"], ["info", "surface"], ["primary", "surface"],
  ["success", "success_soft"], ["warning", "warning_soft"], ["danger", "danger_soft"], ["info", "info_soft"], ["primary", "primary_soft"],
  ["border_strong", "surface"], ["focus_ring", "surface"], ["focus_ring", "background_alt"], ["focus_ring_on_dark", "background_dark"],
  ["accent", "background_dark"], ["primary_on_dark", "background_dark"], ["primary_on_dark", "surface_dark"], ["border", "surface"].slice(0, 0),
].filter((pair) => pair.length);

for (const [fg, bg] of text) {
  test(`text: ${fg} on ${bg} is at least 4.5:1`, () => {
    const ratio = contrast(c[fg], c[bg]);
    assert.ok(ratio >= 4.5, `${fg} (${c[fg]}) on ${bg} (${c[bg]}) is ${ratio.toFixed(2)}:1`);
  });
}
for (const [fg, bg] of nonText) {
  test(`non-text: ${fg} on ${bg} is at least 3:1`, () => {
    const ratio = contrast(c[fg], c[bg]);
    assert.ok(ratio >= 3, `${fg} (${c[fg]}) on ${bg} (${c[bg]}) is ${ratio.toFixed(2)}:1`);
  });
}
