import test from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MENUS, FOOTER, MAIN_PAGES, siteMapPaths } from "../src/lib/nav.js";

const pagesDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../src/pages");

/** The source file that renders an internal path: /x -> src/pages/x.astro, / -> index.astro, /frameworks/<slug> -> the dynamic route. */
function pageFor(href) {
  if (href === "/") return path.join(pagesDir, "index.astro");
  if (href.startsWith("/frameworks/")) return path.join(pagesDir, "frameworks", "[slug].astro");
  return path.join(pagesDir, `${href.slice(1)}.astro`);
}

test("every path in the site map has a page", () => {
  const paths = siteMapPaths();
  assert.ok(paths.length >= 25, `the site map is short: ${paths.length} paths`);
  for (const p of paths) assert.ok(existsSync(pageFor(p)), `${p} has no page under src/pages`);
});

test("the header has the menus the founder asked for, and the Resources menu mirrors the reference layout", () => {
  const labels = MENUS.map((m) => m.label);
  assert.deepEqual(labels, ["Platform", "Solutions", "Frameworks", "Pricing", "Compare", "Partners", "Resources", "Contact"]);
  const resources = MENUS.find((m) => m.label === "Resources");
  assert.ok(resources.wide, "the Resources menu is the wide one");
  assert.deepEqual(resources.groups.map((g) => g.title), ["Customers", "Company", "Compliance resources", "All resources"]);
  const customers = resources.groups[0].items.map((i) => i.label);
  for (const expected of ["Customer stories", "Help center", "Alimi Academy", "Alimi Community", "Instructor-led training"]) assert.ok(customers.includes(expected), `Customers group lacks ${expected}`);
  const company = resources.groups[1].items.map((i) => i.label);
  assert.deepEqual(company, ["About", "Security", "Press", "Careers"]);
  const compliance = resources.groups[2].items.map((i) => i.label);
  for (const expected of ["SOC 2", "ISO 27001", "HIPAA", "ISO 42001", "GDPR", "HITRUST", "CMMC", "FedRAMP", "Cyber Essentials", "TPRM", "Trust", "GRC"]) assert.ok(compliance.includes(expected), `Compliance resources lacks ${expected}`);
  assert.ok(MENUS.find((m) => m.label === "Contact").button, "Contact is the button");
});

test("every menu item and footer link has a label and an href; external links are marked", () => {
  const items = [...MENUS.flatMap((m) => (m.groups ?? []).flatMap((g) => g.items)), ...FOOTER.flatMap((c) => c.items), ...MAIN_PAGES];
  for (const item of items) {
    assert.ok(item.label && item.label.length > 1, `item without a label: ${JSON.stringify(item)}`);
    assert.ok(typeof item.href === "string" && item.href.length > 0, `${item.label} has no href`);
    if (item.href.startsWith("http")) assert.ok(item.external, `${item.label} points off-site and is not marked external`);
    else assert.ok(item.href.startsWith("/"), `${item.label} has a relative href`);
  }
  assert.deepEqual(FOOTER.map((c) => c.title), ["Platform", "Solutions", "Resources", "Partners", "Company"]);
});
