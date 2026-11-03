// The two themes: the inlined token block carries both, the dark one under the device's preference
// and under the visitor's choice, and the small script that applies the choice stays small and plain.
import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { brand } from "../src/lib/config.js";
import { themeCss } from "../src/lib/theme.js";

const here = path.dirname(fileURLToPath(import.meta.url));

test("themeCss inlines the light tokens as the default and the dark tokens twice", () => {
  const css = themeCss(brand);
  assert.ok(css.startsWith(":root{--color-primary:#4338CA"), "the light theme comes first and is the default");
  assert.match(css, /:root\{[^}]*color-scheme:light\}/);
  assert.match(css, /@media \(prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)\{--color-primary:#A5B4FC[^}]*color-scheme:dark\}\}/);
  assert.match(css, /:root\[data-theme="dark"\]\{--color-primary:#A5B4FC[^}]*color-scheme:dark\}/);
  const darkBlocks = css.match(/--color-background-dark:#07091A/g) ?? [];
  assert.equal(darkBlocks.length, 2, "the dark tokens appear under the media query and under the data attribute");
  assert.ok(!/#[0-9A-Fa-f]{3}\b(?![0-9A-Fa-f])/.test(css.replace(/#[0-9A-Fa-f]{6}/g, "")), "only six-digit hex colors");
});

test("themeCss falls back to the light tokens alone when there is no dark map", () => {
  const { colors_dark, ...light } = brand;
  assert.equal(themeCss(light), `:root{${themeCss(brand).slice(":root{".length).split(";color-scheme:light}")[0]}}`);
});

test("themeCss refuses a dark map whose keys differ from the light map", () => {
  const { primary, ...rest } = brand.colors_dark;
  assert.throws(() => themeCss({ ...brand, colors_dark: rest }), /missing: primary/);
  assert.throws(() => themeCss({ ...brand, colors_dark: { ...brand.colors_dark, extra: "#000000" } }), /extra: extra/);
  const reordered = Object.fromEntries(Object.entries(brand.colors_dark).reverse());
  assert.throws(() => themeCss({ ...brand, colors_dark: reordered }), /same order/);
});

test("the theme script is small, plain and stores one key", () => {
  const js = readFileSync(path.join(here, "../src/scripts/theme.js"), "utf8");
  assert.ok(js.length < 3000, "it runs before first paint, so it stays tiny");
  assert.match(js, /"alimi-theme"/);
  assert.match(js, /prefers-color-scheme: dark/);
  assert.match(js, /data-theme-toggle/);
  for (const banned of ["eval(", "innerHTML", "fetch(", "XMLHttpRequest", "document.write", "cookie"]) {
    assert.ok(!js.includes(banned), `theme.js must not use ${banned}`);
  }
});

test("the layout inlines the theme script and the Content Security Policy allows exactly that text by hash", () => {
  const layout = readFileSync(path.join(here, "../src/layouts/Base.astro"), "utf8");
  assert.match(layout, /<script is:inline set:html=\{themeScript\}><\/script>/);
  assert.match(layout, /data-tokens/);
  const js = readFileSync(path.join(here, "../src/scripts/theme.js"), "utf8");
  const hash = createHash("sha256").update(js).digest("base64");
  const csp = readFileSync(path.join(here, "../../netlify.toml"), "utf8");
  assert.ok(csp.includes(`script-src 'self' 'sha256-${hash}';`), `netlify.toml must carry the hash of src/scripts/theme.js as it is now (sha256-${hash})`);
  assert.ok(!/script-src[^;]*'unsafe-inline'/.test(csp), "no other inline script is allowed");
});
