// Post-build checks on dist/: every page has lang, one h1, a title and a description; Netlify form
// names are unique across the site; and no color is hardcoded anywhere outside the :root token block
// that the layout inlines from brand.yaml. Prints the TODO count for prompt 11. Exits 1 on a failure.
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dist = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../dist");
const pages = readdirSync(dist).filter((f) => f.endsWith(".html")).sort();
if (pages.length === 0) {
  console.error("check-dist: no HTML in dist/");
  process.exit(1);
}

const failures = [];
const forms = new Map();
let todos = 0;
const TOKEN_BLOCK = /<style>:root\{[^}]*\}<\/style>/;
// Hex colors, rgb()/hsl() functions and CSS named colors in style contexts.
const HARDCODED = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(|\b(?:color|background(?:-color)?|border(?:-color)?|fill|stroke|outline(?:-color)?)\s*:\s*(?!var\(|inherit|transparent|currentColor|currentcolor|none|initial|unset|\d|[a-z-]*\s*var\()/g;

for (const page of pages) {
  const html = readFileSync(path.join(dist, page), "utf8");
  const where = `dist/${page}`;
  if (!/<html lang="en">/.test(html)) failures.push(`${where}: missing <html lang="en">`);
  const h1s = (html.match(/<h1[\s>]/g) ?? []).length;
  if (h1s !== 1) failures.push(`${where}: expected one <h1>, found ${h1s}`);
  if (!/<title>[^<]+<\/title>/.test(html)) failures.push(`${where}: missing <title>`);
  if (!/<meta name="description" content="[^"]{20,}"/.test(html)) failures.push(`${where}: missing or short meta description`);
  if (!TOKEN_BLOCK.test(html)) failures.push(`${where}: brand token block not inlined`);
  todos += (html.match(/data-todo/g) ?? []).length;

  for (const match of html.matchAll(/<form\b[^>]*>/g)) {
    const tag = match[0];
    const name = /\bname="([^"]+)"/.exec(tag)?.[1];
    if (!name) {
      failures.push(`${where}: form without a name`);
      continue;
    }
    if (!/data-netlify="true"/.test(tag)) failures.push(`${where}: form ${name} is not a Netlify form`);
    if (!/netlify-honeypot="bot-field"/.test(tag)) failures.push(`${where}: form ${name} has no honeypot`);
    if (!/action="\/thank-you"/.test(tag)) failures.push(`${where}: form ${name} does not redirect to /thank-you`);
    const hidden = new RegExp(`<input type="hidden" name="form-name" value="${name}"`);
    if (!hidden.test(html)) failures.push(`${where}: form ${name} is missing its hidden form-name field`);
    if (forms.has(name)) failures.push(`${where}: form name ${name} already used in ${forms.get(name)}`);
    forms.set(name, where);
  }

  // Strip the token block and the favicon link, then look for colors typed anywhere else.
  const stripped = html
    .replace(TOKEN_BLOCK, "")
    .replace(/<meta name="theme-color" content="#[0-9A-Fa-f]{6}">/, "");
  // The CSS minifier rewrites the keyword `transparent` as #0000; it is the absence of a color.
  const found = [...stripped.matchAll(HARDCODED)].map((m) => m[0]).filter((m) => m.toLowerCase() !== "#0000");
  if (found.length) failures.push(`${where}: hardcoded color(s): ${[...new Set(found)].join(", ")}`);
}

const favicon = readFileSync(path.join(dist, "favicon.svg"), "utf8");
if ((favicon.match(/#[0-9A-Fa-f]{6}/g) ?? []).length !== 2) failures.push("dist/favicon.svg: expected exactly two brand colors");

console.log(`check-dist: ${pages.length} pages, ${forms.size} Netlify forms (${[...forms.keys()].join(", ")}), ${todos} TODO markers for prompt 11`);
if (failures.length) {
  for (const f of failures) console.error(`  FAIL ${f}`);
  process.exit(1);
}
