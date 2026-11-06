import test from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MENUS, FOOTER, MAIN_PAGES, siteMapPaths, breadcrumbs } from "../src/lib/nav.js";
import { ICONS } from "../src/lib/icons.js";

const pagesDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../src/pages");

/** The source file that renders an internal path: /x -> src/pages/x.astro, / -> index.astro, /frameworks/<slug> -> the dynamic route. */
function pageFor(href) {
  if (href === "/") return path.join(pagesDir, "index.astro");
  if (href.startsWith("/frameworks/")) return path.join(pagesDir, "frameworks", "[slug].astro");
  if (href.startsWith("/platform/")) return path.join(pagesDir, "platform", "[module].astro");
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
  assert.deepEqual(FOOTER.map((c) => c.title), ["Platform", "Solutions", "Resources", "Partners", "Trust", "Company"]);
  const trust = FOOTER.find((c) => c.title === "Trust").items.map((i) => i.href);
  for (const expected of ["/security", "/trust", "/status", "/accessibility"]) assert.ok(trust.includes(expected), `Trust column lacks ${expected}`);
});

test("every top-level menu has an icon drawing for the header strip", () => {
  for (const menu of MENUS) assert.ok(menu.icon && ICONS[menu.icon], `${menu.label} has no icon`);
});

test("the breadcrumb trail is Home, the menu that lists the page, then the page", () => {
  assert.deepEqual(breadcrumbs("/", "Alimi").map((c) => c.label), ["Home"]);
  assert.deepEqual(breadcrumbs("/platform", "The platform").map((c) => c.label), ["Home", "The platform"]);
  assert.deepEqual(breadcrumbs("/security", "Security").map((c) => c.href), ["/", "/platform", "/security"]);
  assert.deepEqual(breadcrumbs("/frameworks/soc-2", "SOC 2").map((c) => c.label), ["Home", "Frameworks", "SOC 2"]);
  assert.deepEqual(breadcrumbs("/status", "Status").map((c) => c.label), ["Home", "Status"]);
  const last = breadcrumbs("/pricing", "Pricing").at(-1);
  assert.ok(last.current && last.href === "/pricing");
});
