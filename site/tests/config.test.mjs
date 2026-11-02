import test from "node:test";
import assert from "node:assert/strict";
import { brand, pricing, tierPrice, tierNote, product, products, platform, services, service, freeResources, resellerTiers, partners, retainer, decided, PRODUCT_PAGES, PRODUCT_ORDER } from "../src/lib/config.js";
import { cssVariables } from "../src/lib/tokens.js";
import { insurerQuestions, checkCounts, policies, frameworks, controlSummary, freeDocs, fillPlaceholders, FREE_DOCS } from "../src/lib/content.js";

test("tierPrice renders list, range, free and quoted", () => {
  assert.equal(tierPrice({ list: 0 }), "Free");
  assert.equal(tierPrice({ list: 3900 }), "$3,900");
  assert.equal(tierPrice({ range: [500, 1500] }), "$500 to $1,500");
  assert.equal(tierPrice({ list: 99, range: [49, 99] }), "$99");
  assert.equal(tierPrice({}), "Quoted");
});

test("tierNote tells the platform, services and free resources apart", () => {
  assert.match(tierNote({ type: "service" }), /Fixed fee/);
  assert.match(tierNote({ type: "product", list: 0 }), /No card/);
  assert.match(tierNote({ type: "product", list: 3900 }), /monthly/);
});

test("one product: the platform, then services, then free resources, each with a page", () => {
  assert.deepEqual(PRODUCT_ORDER, ["platform", "services", "free"]);
  assert.deepEqual(Object.keys(pricing.products).sort(), [...PRODUCT_ORDER].sort());
  for (const p of products()) {
    assert.ok(PRODUCT_PAGES[p.key], `${p.key} has no page`);
    assert.ok(p.tiers.length >= 3, `${p.key} has too few tiers`);
  }
});

test("platform tiers rise with company size and carry the pricing rule", () => {
  const { tiers, included, billing, auditNote } = platform();
  assert.deepEqual(tiers.map((t) => t.id), ["starter", "growth", "scale"]);
  for (let i = 1; i < tiers.length; i += 1) {
    assert.ok(tiers[i].list > tiers[i - 1].list, "prices must rise");
    assert.ok(tiers[i].people_up_to > tiers[i - 1].people_up_to, "sizes must rise");
  }
  for (const t of tiers) {
    assert.equal(t.type, "product");
    assert.match(t.rule, /minus 15%/, `${t.id} records how its price was set`);
    assert.match(t.monthly, /^\$[\d,]+ a month$/);
    assert.match(t.monthToMonth, /^\$[\d,]+ a month$/);
    assert.ok(Number(t.monthToMonth.replace(/\D/g, "")) > Number(t.monthly.replace(/\D/g, "")), "month to month costs more than the term");
    assert.equal(t.termLabel, "12-month term");
    assert.match(t.peopleLabel, /^Up to \d+ people$/);
    assert.ok(t.frameworkLabels.includes("Cyber insurance questionnaire"), "every tier starts with the insurer questionnaire");
    assert.ok(t.includes.length >= 4);
  }
  assert.equal(tiers[0].integrationsLabel, "1 integration");
  assert.equal(tiers[2].integrationsLabel, "Unlimited integrations");
  assert.ok(included.some((line) => /policy library/i.test(line)), "policies are included at every tier");
  assert.match(billing, /paid monthly/);
  assert.match(billing, /No automatic increase/);
  assert.match(billing, /locked for 24 months/);
  assert.match(billing, /[Ee]xport/);
  assert.match(auditNote, /audit/i);
});

test("services are fixed-fee ranges and free resources cost nothing", () => {
  for (const s of services()) {
    assert.equal(s.type, "service");
    assert.match(s.price, /^\$[\d,]+ to \$[\d,]+$/, `${s.id} needs a quoted range`);
  }
  assert.equal(service("insurance_ready_30").name, "Insurance-ready in 30 days");
  assert.throws(() => service("nope"));
  for (const f of freeResources()) assert.equal(f.price, "Free", `${f.id} must be free`);
  assert.equal(product("free").href, "/resources");
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
  const keys = Object.keys(brand.colors);
  for (const required of ["primary", "primary_on_dark", "secondary", "accent", "background", "background_alt", "background_dark", "surface", "text", "text_muted", "text_inverse", "border", "border_strong", "success", "warning", "danger", "info", "focus_ring", "focus_ring_on_dark"]) {
    assert.ok(keys.includes(required), `brand.yaml is missing colors.${required}`);
  }
  const css = cssVariables(brand);
  assert.match(css, /--color-primary:#9A3B1E/);
  assert.match(css, /--color-background-alt:#/);
  assert.match(css, /--font-body:/);
  assert.ok(!/#[0-9A-Fa-f]{3}\b(?![0-9A-Fa-f])/.test(css.replace(/#[0-9A-Fa-f]{6}/g, "")), "only six-digit hex colors");
});

test("cssVariables rejects anything but six-digit hex", () => {
  assert.throws(() => cssVariables({ ...brand, colors: { ...brand.colors, primary: "red" } }));
  assert.throws(() => cssVariables({ ...brand, colors: { ...brand.colors, primary: "#abc" } }));
});

test("content: insurer questions, check counts, policies, frameworks and controls read from the repo", () => {
  const questions = insurerQuestions();
  assert.ok(questions.length >= 8);
  assert.ok(questions.some((q) => q.automated));
  const counts = checkCounts();
  assert.equal(counts.total, counts.m365 + counts.gws + counts.attestation);
  const list = policies();
  assert.ok(list.length >= 20);
  assert.ok(list.every((p) => /^POL-\d{2}$/.test(p.id) && p.title.length > 5));
  const fws = frameworks();
  assert.deepEqual(fws.map((f) => f.id).sort(), ["hipaa", "insurer", "iso27001", "iso42001", "soc2"]);
  assert.ok(fws.every((f) => f.requirementCount > 10 && f.short.length > 2));
  const controls = controlSummary();
  assert.ok(controls.total >= 30 && controls.automated >= 5 && controls.domains.length >= 5);
});

test("free documents render without their own h1 or any unfilled placeholder", () => {
  assert.equal(fillPlaceholders("{{Company}} and {{Security Lead}} on {{Effective Date}}"), "The Company and the Security Lead on [effective date]");
  const docs = freeDocs();
  assert.equal(docs.length, FREE_DOCS.length);
  for (const d of docs) {
    assert.ok(d.title.length > 5 && d.words > 200, `${d.slug} looks empty`);
    assert.ok(!d.html.includes("<h1"), `${d.slug} keeps its own h1`);
    assert.ok(!d.html.includes("{{"), `${d.slug} has an unfilled placeholder`);
    assert.ok(d.html.includes("<h2"), `${d.slug} has no sections`);
  }
  const policy = docs.find((d) => d.slug === "information-security-policy");
  assert.equal(policy.id, "POL-01");
  assert.match(policy.html, /TEMPLATE\. Adapt before adopting/);
});
