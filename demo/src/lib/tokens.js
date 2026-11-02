// Turns brand.yaml into CSS custom properties. The layout inlines the result in <head>, so the
// whole site reads colors and fonts from one place and no component carries a hex value.
const HEX = /^#[0-9A-Fa-f]{6}$/;

export function cssVariables(brand) {
  const lines = [];
  for (const [key, value] of Object.entries(brand.colors ?? {})) {
    if (!HEX.test(String(value))) throw new Error(`brand.yaml colors.${key} is not a six-digit hex color: ${value}`);
    lines.push(`--color-${key.replaceAll("_", "-")}:${String(value).toUpperCase()}`);
  }
  for (const [key, value] of Object.entries(brand.typography ?? {})) {
    lines.push(`--font-${key}:${value}`);
  }
  return `:root{${lines.join(";")}}`;
}

export function tokenNames(brand) {
  return Object.keys(brand.colors ?? {}).map((key) => `--color-${key.replaceAll("_", "-")}`);
}
