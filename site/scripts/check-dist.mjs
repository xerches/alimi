// Post-build checks on every page in dist/ (subfolders included): lang, one h1, a title and a description; Netlify form
// names are unique across the site; and no color is hardcoded anywhere outside the token block (light
// and dark themes) that the layout inlines from brand.yaml. Prints the TODO count for prompt 11. Exits 1 on a failure.
import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dist = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../dist");
// Every HTML file, including the generated document pages under dist/resources/.
const pages = readdirSync(dist, { recursive: true })
  .map(String)
  .filter((f) => f.endsWith(".html"))
  .sort();
if (pages.length === 0) {
  console.error("check-dist: no HTML in dist/");
  process.exit(1);
}

const failures = [];
const forms = new Map();
let todos = 0;
const TOKEN_BLOCK = /<style data-tokens>:root\{[\s\S]*?<\/style>/;
// The Content Security Policy allows scripts from the site's own origin and inline scripts by hash only,
// so every inline script the build writes (the theme script in <head>, and nothing else: Astro's
// component scripts are emitted as files, see astro.config.mjs) must have its hash in netlify.toml.
const SCRIPTS = /<script(\s[^>]*)?>([\s\S]*?)<\/script>/g;
const csp = /Content-Security-Policy = "([^"]+)"/.exec(readFileSync(path.resolve(dist, "../../netlify.toml"), "utf8"))?.[1] ?? "";
const allowedHashes = [...csp.matchAll(/'sha256-([^']+)'/g)].map((m) => m[1]);
const sha256 = (text) => createHash("sha256").update(text).digest("base64");
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
  if (!/\[data-theme="dark"\]/.test(html)) failures.push(`${where}: dark theme tokens not inlined`);
  const inlineScripts = [...html.matchAll(SCRIPTS)].filter((m) => !/\ssrc=/.test(m[1] ?? "")).map((m) => m[2]);
  if (!inlineScripts.some((js) => js.includes('"alimi-theme"'))) failures.push(`${where}: theme script not inlined`);
  for (const js of inlineScripts) {
    if (!allowedHashes.includes(sha256(js))) failures.push(`${where}: an inline script (sha256-${sha256(js)}, starts "${js.slice(0, 40)}") is not allowed by the Content-Security-Policy in netlify.toml; the theme script's hash goes there, any other script is emitted as a file`);
  }
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

  // Look for colors typed in any style context other than the token block: <style> blocks and
  // style/fill/stroke/color attributes. Prose is left alone, so "Form #519" in a document is fine.
  const styleContexts = [
    ...html.replace(TOKEN_BLOCK, "").matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g),
    ...html.matchAll(/\s(?:style|fill|stroke|color|bgcolor)="([^"]*)"/g),
  ].map((m) => m[1]);
  // The CSS minifier rewrites the keyword `transparent` as #0000; it is the absence of a color.
  const found = styleContexts
    .flatMap((css) => [...css.matchAll(HARDCODED)].map((m) => m[0]))
    .filter((m) => m.toLowerCase() !== "#0000");
  if (found.length) failures.push(`${where}: hardcoded color(s): ${[...new Set(found)].join(", ")}`);
}

const favicon = readFileSync(path.join(dist, "favicon.svg"), "utf8");
if ((favicon.match(/#[0-9A-Fa-f]{6}/g) ?? []).length !== 2) failures.push("dist/favicon.svg: expected exactly two brand colors");

// Every internal link resolves to a built page (and every fragment to an id on it). Added Nov 2, 2026
// with the menus and the new pages, so a renamed page cannot leave a dead link behind.
const built = new Set(pages.map((p) => "/" + p.replace(/\.html$/, "").replace(/\\/g, "/")).map((p) => (p === "/index" ? "/" : p)));
const idsByPage = new Map();
for (const page of pages) {
  const html = readFileSync(path.join(dist, page), "utf8");
  const where = `dist/${page}`;
  for (const match of html.matchAll(/href="(\/[^"]*)"/g)) {
    const href = match[1];
    if (href.startsWith("/_astro/") || href === "/favicon.svg") continue;
    const [target, fragment] = href.split("#");
    const pagePath = target === "" ? "/" + page.replace(/\.html$/, "").replace(/^index$/, "") : target.replace(/\/$/, "") || "/";
    if (!built.has(pagePath)) {
      failures.push(`${where}: link to ${href} but no page is built at ${pagePath}`);
      continue;
    }
    if (fragment) {
      const file = pagePath === "/" ? "index.html" : `${pagePath.slice(1)}.html`;
      if (!idsByPage.has(file)) idsByPage.set(file, new Set([...readFileSync(path.join(dist, file), "utf8").matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
      if (!idsByPage.get(file).has(fragment)) failures.push(`${where}: link to ${href} but ${file} has no id "${fragment}"`);
    }
  }
}

console.log(`check-dist: ${pages.length} pages, ${forms.size} Netlify forms (${[...forms.keys()].join(", ")}), ${todos} TODO markers for prompt 11, internal links checked`);
if (failures.length) {
  for (const f of failures) console.error(`  FAIL ${f}`);
  process.exit(1);
}
