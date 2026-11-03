// The navigation model and the pages agree: every page's section resolves to a strip section, every
// link in the strip and the columns points at a page that exists, and the phone bar names real sections.
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SECTIONS, BOTTOM_BAR, PAGE_SECTIONS, STATIC_COLUMNS, ICONS, resolveSection } from "../src/lib/nav.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(here, "../src/pages");

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (entry.endsWith(".astro")) out.push(full);
  }
  return out;
}
const pageExists = (href) => {
  const clean = href.split("#")[0].split("?")[0];
  const rel = clean === "/" ? "index" : clean.replace(/^\//, "");
  return existsSync(path.join(pagesDir, `${rel}.astro`)) || existsSync(path.join(pagesDir, rel, "index.astro"));
};

test("every page passes a section the model knows", () => {
  for (const file of walk(pagesDir)) {
    const match = readFileSync(file, "utf8").match(/<App[^>]*\bsection="([a-z]+)"/);
    if (!match) continue; // the favicon route has no layout
    assert.ok(PAGE_SECTIONS[match[1]], `${path.relative(pagesDir, file)} uses unknown section "${match[1]}"`);
    assert.ok(resolveSection(match[1]).section, `${match[1]} resolves to no strip section`);
  }
});

test("every strip, bottom-bar and column link points at a page, and every section has an icon", () => {
  for (const s of SECTIONS) {
    assert.ok(pageExists(s.href), `${s.key} links to ${s.href}, which is not a page`);
    assert.ok(ICONS[s.icon], `${s.key} has no icon`);
  }
  for (const key of BOTTOM_BAR) assert.ok(SECTIONS.some((s) => s.key === key), `bottom bar names unknown section ${key}`);
  for (const [key, column] of Object.entries(STATIC_COLUMNS)) {
    assert.ok(SECTIONS.find((s) => s.key === key)?.column, `${key} has a column but is not marked column: true`);
    for (const item of column.items) {
      assert.ok(pageExists(item.href), `${key} column links to ${item.href}, which is not a page`);
      assert.ok(Object.values(PAGE_SECTIONS).some(([section, i]) => section === key && i === item.key), `${key} column item ${item.key} is not a page section`);
    }
  }
  for (const [page, [section, item]] of Object.entries(PAGE_SECTIONS)) {
    const s = SECTIONS.find((x) => x.key === section);
    assert.ok(s, `${page} points at unknown section ${section}`);
    if (item && STATIC_COLUMNS[section]) assert.ok(STATIC_COLUMNS[section].items.some((i) => i.key === item), `${page}: ${item} is not in the ${section} column`);
  }
});

test("the strip holds twelve sections at most, so the captions stay readable", () => {
  assert.ok(SECTIONS.length <= 12, `${SECTIONS.length} sections`);
  assert.equal(BOTTOM_BAR.length, 4);
});
