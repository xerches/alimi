// The site's two themes as one inlined style block (Nov 3, 2026). `colors` in brand.yaml is the light
// theme and the default; `colors_dark` is applied when the device asks for a dark scheme and the visitor
// has not chosen light, or when the visitor has chosen dark (public/theme.js sets data-theme on <html>).
// tokens.js stays the shared helper the demo copies byte for byte; this file is the site's own.
import { cssVariables } from "./tokens.js";

const DARK_SELECTORS = ['@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){', ':root[data-theme="dark"]{'];

export function themeCss(brand) {
  const light = cssVariables(brand);
  const dark = brand.colors_dark;
  if (!dark) return light;
  const lightKeys = Object.keys(brand.colors ?? {});
  const darkKeys = Object.keys(dark);
  const missing = lightKeys.filter((k) => !darkKeys.includes(k));
  const extra = darkKeys.filter((k) => !lightKeys.includes(k));
  if (missing.length || extra.length) {
    throw new Error(`brand.yaml colors_dark must list the same keys as colors (missing: ${missing.join(", ") || "none"}; extra: ${extra.join(", ") || "none"})`);
  }
  if (lightKeys.join() !== darkKeys.join()) throw new Error("brand.yaml colors_dark must list its keys in the same order as colors");
  const darkVars = cssVariables({ colors: dark }).slice(":root{".length, -1);
  const lightBlock = `${light.slice(0, -1)};color-scheme:light}`;
  const darkBlock = `${darkVars};color-scheme:dark}`;
  return lightBlock + DARK_SELECTORS[0] + darkBlock + "}" + DARK_SELECTORS[1] + darkBlock;
}
