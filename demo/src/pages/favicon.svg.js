// The favicon is generated from brand.yaml so the mark changes with the palette and no SVG file
// carries a hex value of its own.
import { brand } from "../lib/config.js";

export function GET() {
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">` +
    `<rect x="7" y="2" width="15" height="15" rx="3" fill="${brand.colors.secondary}"/>` +
    `<rect x="2" y="7" width="15" height="15" rx="3" fill="${brand.colors.primary}"/>` +
    `</svg>`;
  return new Response(svg, { headers: { "Content-Type": "image/svg+xml" } });
}
