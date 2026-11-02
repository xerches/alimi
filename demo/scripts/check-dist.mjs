// Post-build checks on dist/: every page has lang, one h1, a title, a description, the noindex meta,
// the sample-company banner and the inlined token block; no color is hardcoded outside that block;
// no form posts anywhere; and every internal link points at a page that was built. Exits 1 on failure.
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dist = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../dist");

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

const pages = walk(dist).filter((f) => f.endsWith(".html")).sort();
if (pages.length === 0) {
  console.error("check-dist: no HTML in dist/");
  process.exit(1);
}

const failures = [];
const TOKEN_BLOCK = /<style>:root\{[^}]*\}<\/style>/;
const HARDCODED = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(|\b(?:color|background(?:-color)?|border(?:-color)?|fill|stroke|outline(?:-color)?)\s*:\s*(?!var\(|inherit|transparent|currentColor|currentcolor|none|initial|unset|\d|[a-z-]*\s*var\()/g;
let links = 0;

function targetExists(href) {
  const clean = href.split("#")[0].split("?")[0];
  if (clean === "" || clean === "/") return existsSync(path.join(dist, "index.html"));
  const rel = clean.replace(/^\//, "");
  return existsSync(path.join(dist, `${rel}.html`)) || existsSync(path.join(dist, rel)) || existsSync(path.join(dist, rel, "index.html"));
}

for (const page of pages) {
  const html = readFileSync(page, "utf8");
  const where = path.relative(dist, page);
  if (!/<html lang="en">/.test(html)) failures.push(`${where}: missing <html lang="en">`);
  const h1s = (html.match(/<h1[\s>]/g) ?? []).length;
  if (h1s !== 1) failures.push(`${where}: expected one <h1>, found ${h1s}`);
  if (!/<title>[^<]+<\/title>/.test(html)) failures.push(`${where}: missing <title>`);
  if (!/<meta name="description" content="[^"]{20,}"/.test(html)) failures.push(`${where}: missing or short meta description`);
  if (!/<meta name="robots" content="noindex, nofollow">/.test(html)) failures.push(`${where}: missing noindex`);
  if (!/data-sample-banner/.test(html)) failures.push(`${where}: sample-company banner missing`);
  if (!TOKEN_BLOCK.test(html)) failures.push(`${where}: brand token block not inlined`);
  if (/<form\b[^>]*\baction=/.test(html)) failures.push(`${where}: a form posts somewhere; the demo saves nothing`);

  // Anchors and ids such as #add or #cafe are not colours, so attribute values are dropped before the scan.
  const stripped = html
    .replace(TOKEN_BLOCK, "")
    .replace(/<meta name="theme-color" content="#[0-9A-Fa-f]{6}">/, "")
    .replace(/\b(?:href|id|aria-controls|data-filter|data-chips)="[^"]*"/g, "");
  const found = [...stripped.matchAll(HARDCODED)].map((m) => m[0]).filter((m) => m.toLowerCase() !== "#0000");
  if (found.length) failures.push(`${where}: hardcoded color(s): ${[...new Set(found)].join(", ")}`);

  for (const match of html.matchAll(/href="(\/[^"]*)"/g)) {
    links += 1;
    if (!targetExists(match[1])) failures.push(`${where}: link to ${match[1]} has no page`);
  }
}

const favicon = readFileSync(path.join(dist, "favicon.svg"), "utf8");
if ((favicon.match(/#[0-9A-Fa-f]{6}/g) ?? []).length !== 2) failures.push("dist/favicon.svg: expected exactly two brand colors");
if (!readFileSync(path.join(dist, "robots.txt"), "utf8").includes("Disallow: /")) failures.push("robots.txt does not disallow crawling");

console.log(`check-dist: ${pages.length} pages, ${links} internal links checked`);
if (failures.length) {
  for (const f of [...new Set(failures)]) console.error(`  FAIL ${f}`);
  process.exit(1);
}
