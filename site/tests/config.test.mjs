import test from "node:test";
import assert from "node:assert/strict";
import { brand, pricing, tierPrice, tierNote, product, products, freeTier, resellerTiers, partners, retainer, decided, PRODUCT_PAGES } from "../src/lib/config.js";
import { cssVariables, tokenNames } from "../src/lib/tokens.js";
import { insurerQuestions, checkCounts, policies, formatDate } from "../src/lib/content.js";

test("tierPrice renders list, range, free and quoted", () => {
  assert.equal(tierPrice({ list: 0 }), "Free");
  assert.equal(tierPrice({ list: 499 }), "$499");
  assert.equal(tierPrice({ range: [500, 1500] }), "$500 to $1,500");
  assert.equal(tierPrice({ list: 99, range: [49, 99] }), "$99");
  assert.equal(tierPrice({}), "Quoted");
});

test("tierNote tells products from services", () => {
  assert.match(tierNote({ type: "service" }), /Fixed fee/);
  assert.match(tierNote({ type: "product", list: 0 }), /No card/);
  assert.equal(tierNote({ type: "product", list: 499 }), "One-time purchase");
});

test("every product in pricing.yaml has a page and a free or entry tier", () => {
  for (const key of Object.keys(pricing.products)) {
    assert.ok(PRODUCT_PAGES[key], `${key} has no page`);
    const p = product(key);
    assert.ok(p.tiers.length >= 2, `${key} has fewer than two tiers`);
    assert.ok(p.tiers.every((t) => t.price && t.note && Array.isArray(t.includes) && t.includes.length > 0));
  }
  assert.equal(products().length, Object.keys(pricing.products).length);
});

test("a status that still says confirm keeps the draft banner", () => {
  assert.ok(product("policy_pack").draft === null || /confirm/i.test(product("policy_pack").draft));
  assert.equal(product("workspace_scan").draft, null);
});

test("freeTier finds the zero-price tier", () => {
  assert.equal(freeTier("workspace_scan").list, 0);
  assert.equal(freeTier("payment_fraud_kit"), null);
});

test("reseller tiers and referral fee come from pricing.yaml", () => {
  const tiers = resellerTiers();
  assert.deepEqual(tiers.map((t) => t.name), ["Starter", "Growth", "Scale"]);
  assert.deepEqual(tiers.map((t) => t.discount), ["10%", "15%", "20%"]);
  assert.equal(tiers[2].clients, "151 or more");
  assert.equal(partners().referral.feeText, "10%");
  assert.match(retainer().price, /^\$3,000 to \$6,000 a month$/);
});

test("decided treats TODO and blanks as absent", () => {
  assert.equal(decided("TODO"), null);
  assert.equal(decided(" "), null);
  assert.equal(decided("hello@example.com"), "hello@example.com");
});

test("brand tokens cover every purpose group and render as CSS variables", () => {
  const names = tokenNames(brand);
  const required = [
    "--color-primary", "--color-primary-hover", "--color-primary-active", "--color-primary-on-dark",
    "--color-secondary", "--color-accent",
    "--color-background", "--color-background-alt", "--color-background-dark", "--color-surface", "--color-surface-dark",
    "--color-text", "--color-text-secondary", "--color-text-muted", "--color-text-inverse", "--color-text-inverse-muted",
    "--color-border", "--color-border-strong", "--color-border-dark",
    "--color-success", "--color-warning", "--color-danger", "--color-info",
    "--color-focus-ring", "--color-focus-ring-on-dark",
  ];
  for (const name of required) assert.ok(names.includes(name), `${name} missing from brand.yaml`);
  const css = cssVariables(brand);
  assert.match(css, /^:root\{--color-primary:#[0-9A-F]{6};/);
  assert.match(css, /--font-body:/);
  assert.equal(new Set(Object.values(brand.colors).map((v) => String(v).toUpperCase())).size > 20, true);
});

test("cssVariables rejects anything but six-digit hex", () => {
  assert.throws(() => cssVariables({ colors: { primary: "red" } }), /six-digit hex/);
  assert.throws(() => cssVariables({ colors: { primary: "#FFF" } }), /six-digit hex/);
});

test("content: insurer questions, check counts and policies read from the repo", () => {
  const questions = insurerQuestions();
  assert.ok(questions.length >= 6);
  assert.ok(questions.some((q) => q.automated) && questions.some((q) => !q.automated));
  const counts = checkCounts();
  assert.equal(counts.m365 + counts.gws + counts.attestation, counts.total);
  assert.ok(counts.m365 >= 10 && counts.gws >= 5 && counts.attestation >= 3);
  const list = policies();
  assert.ok(list.length >= 20);
  assert.ok(list.every((p) => /^POL-\d{2}$/.test(p.id) && p.title.length > 5));
  assert.equal(formatDate(new Date("2026-11-01T00:00:00Z")), "Nov 1, 2026");
});
