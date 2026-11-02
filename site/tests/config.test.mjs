import test from "node:test";
import assert from "node:assert/strict";
import {
  brand,
  pricing,
  money,
  tierPrice,
  tierNote,
  product,
  products,
  platform,
  services,
  service,
  resellerTiers,
  partners,
  retainer,
  decided,
  frameworkCatalog,
  choosableFrameworks,
  alwaysIncludedFrameworks,
  framework,
  frameworkPricing,
  frameworkDiscount,
  quote,
  EXAMPLE_SIZES,
  PRODUCT_PAGES,
  PRODUCT_ORDER,
} from "../src/lib/config.js";
import { cssVariables } from "../src/lib/tokens.js";
import { insurerQuestions, checkCounts, policies, mappedFrameworks, controlSummary } from "../src/lib/content.js";

test("money prints whole dollars, and cents only when there are some", () => {
  assert.equal(money(13), "$13");
  assert.equal(money(1560), "$1,560");
  assert.equal(money(16.8), "$16.80");
  assert.equal(money(14.95), "$14.95");
});

test("tierPrice renders per-user, list, range and quoted prices", () => {
  assert.equal(tierPrice({ per_user_month: 13 }), "$13 per user a month");
  assert.equal(tierPrice({ list: 3900 }), "$3,900");
  assert.equal(tierPrice({ range: [500, 1500] }), "$500 to $1,500");
  assert.equal(tierPrice({}), "Quoted");
});

test("tierNote tells the platform and the services apart", () => {
  assert.match(tierNote({ type: "service" }), /Fixed fee/);
  assert.match(tierNote({ type: "product", per_user_month: 13 }), /monthly/);
});

test("one product, the platform, then services, each with a page; no free product", () => {
  assert.deepEqual(PRODUCT_ORDER, ["platform", "services"]);
  assert.deepEqual(Object.keys(pricing.products).sort(), [...PRODUCT_ORDER].sort());
  for (const p of products()) {
    assert.ok(PRODUCT_PAGES[p.key], `${p.key} has no page`);
    assert.ok(p.tiers.length >= 4, `${p.key} has too few tiers`);
  }
});

test("platform tiers are Silver, Gold, Platinum, Diamond, per user, rising, each with its pricing rule", () => {
  const { tiers, included, billing, auditNote, minimumUsers, frameworks } = platform();
  assert.deepEqual(tiers.map((t) => t.id), ["silver", "gold", "platinum", "diamond"]);
  assert.deepEqual(tiers.map((t) => t.name), ["Silver", "Gold", "Platinum", "Diamond"]);
  for (let i = 1; i < tiers.length; i += 1) {
    assert.ok(tiers[i].per_user_month > tiers[i - 1].per_user_month, "prices must rise");
  }
  for (const t of tiers) {
    assert.equal(t.type, "product");
    assert.match(t.rule, /minus 15%/, `${t.id} records how its price was set`);
    assert.match(t.price, /^\$\d+ per user a month$/);
    assert.match(t.perUser, /^\$\d+$/);
    assert.ok(Number(t.perUserMonthToMonth.replace(/\D/g, "")) > Number(t.perUser.replace(/\D/g, "")), "month to month costs more than the term");
    assert.equal(t.termLabel, "12-month term");
    assert.equal(t.minimumUsers, minimumUsers);
    assert.ok(t.summary.length > 20, `${t.id} has a one-line summary`);
    assert.ok(t.includes.length >= 4);
    assert.equal(t.examples.length, EXAMPLE_SIZES.length);
  }
  assert.equal(tiers[0].integrationsLabel, "1 integration");
  assert.equal(tiers[2].integrationsLabel, "Unlimited integrations");
  assert.equal(minimumUsers, 10);
  assert.equal(frameworks.included, 1);
  assert.ok(included.some((line) => /policy library/i.test(line)), "policies are included at every tier");
  assert.ok(included.some((line) => /lessons|training/i.test(line)), "training is included at every tier");
  assert.match(billing, /paid monthly/);
  assert.match(billing, /No automatic increase/);
  assert.match(billing, /locked for 24 months/);
  assert.doesNotMatch(billing, /[Ee]xport/, "the exit promise left the billing text on Nov 2, 2026");
  assert.match(auditNote, /audit/i);
});

test("the framework catalog carries IDs, our own summaries and the posture score, never framework text", () => {
  const catalog = frameworkCatalog();
  assert.ok(catalog.length >= 20);
  const ids = catalog.map((f) => f.id);
  for (const required of ["alimi_posture", "insurer", "soc2", "iso27001", "hipaa", "pci_dss", "gdpr", "iso42001", "nist_csf", "ma_201_cmr_17"]) {
    assert.ok(ids.includes(required), `frameworks.yaml is missing ${required}`);
  }
  for (const f of catalog) {
    assert.ok(f.name.length > 2 && f.short.length > 2 && f.summary.length > 30 && f.audience.length > 10, `${f.id} is incomplete`);
    assert.ok(f.summary.split(/\s+/).length <= 40, `${f.id} summary is not one line`);
    assert.equal(typeof f.mapped, "boolean");
  }
  const posture = alwaysIncludedFrameworks();
  assert.equal(posture.length, 1);
  assert.equal(posture[0].id, "alimi_posture");
  assert.ok(!choosableFrameworks().some((f) => f.always_included));
  assert.equal(choosableFrameworks().length, catalog.length - 1);
  // The mapped ones are exactly those the policy library carries requirement IDs for.
  const mapped = catalog.filter((f) => f.mapped && !f.always_included).map((f) => f.id).sort();
  assert.deepEqual(mapped, mappedFrameworks().map((f) => f.id).sort());
  assert.equal(framework("soc2").short, "SOC 2");
  assert.throws(() => framework("nope"));
});

test("framework add-ons: $4 per user, 5% off from five frameworks, 10% off from ten, capped at ten", () => {
  const fp = frameworkPricing();
  assert.equal(fp.addon, 4);
  assert.equal(fp.max, 10);
  assert.deepEqual(fp.discounts.map((d) => [d.fromTotal, d.off]), [[5, 0.05], [10, 0.1]]);
  assert.equal(frameworkDiscount(1), 0);
  assert.equal(frameworkDiscount(4), 0);
  assert.equal(frameworkDiscount(5), 0.05);
  assert.equal(frameworkDiscount(9), 0.05);
  assert.equal(frameworkDiscount(10), 0.1);
  assert.match(fp.text, /One framework of your choice is included/);
  assert.match(fp.text, /Posture Score/);
  assert.match(fp.rule, /minus 15%/);
});

test("quote: per-user arithmetic, the minimum, the discounts and the month-to-month premium", () => {
  const silver25 = quote({ tierId: "silver", users: 25 });
  assert.equal(silver25.perUser, 13);
  assert.equal(silver25.monthly, 325);
  assert.equal(silver25.yearly, 3900);
  assert.equal(silver25.yearlyText, "$3,900 a year");
  const tiny = quote({ tierId: "silver", users: 4 });
  assert.equal(tiny.seats, 10, "below the minimum, the plan bills ten users");
  assert.equal(tiny.monthly, 130);
  const gold2 = quote({ tierId: "gold", users: 50, frameworks: 2 });
  assert.equal(gold2.addons, 1);
  assert.equal(gold2.perUser, 29);
  assert.equal(gold2.yearly, 29 * 50 * 12);
  const five = quote({ tierId: "silver", users: 10, frameworks: 5 });
  assert.equal(five.discount, 0.05);
  assert.equal(five.perUser, 13 + 4 * 4 * 0.95);
  const ten = quote({ tierId: "silver", users: 10, frameworks: 10 });
  assert.equal(ten.discount, 0.1);
  assert.equal(ten.perUser, 13 + 9 * 4 * 0.9);
  const capped = quote({ tierId: "silver", users: 10, frameworks: 14 });
  assert.equal(capped.frameworks, 10, "the account holds at most ten frameworks");
  const m2m = quote({ tierId: "silver", users: 25, monthToMonth: true });
  assert.equal(m2m.perUser, 14.95);
  assert.equal(m2m.perUserText, "$14.95 per user a month");
  assert.throws(() => quote({ tierId: "starter", users: 25 }));
});

test("services are fixed-fee ranges", () => {
  for (const s of services()) {
    assert.equal(s.type, "service");
    assert.match(s.price, /^\$[\d,]+ to \$[\d,]+$/, `${s.id} needs a quoted range`);
  }
  assert.equal(service("insurance_ready_30").name, "Insurance-ready in 30 days");
  assert.throws(() => service("nope"));
  assert.throws(() => product("free"), "the free resources product is gone");
});

test("reseller tiers, incentives and the referral fee come from pricing.yaml", () => {
  const tiers = resellerTiers();
  assert.deepEqual(tiers.map((t) => t.name), ["Partner", "Preferred", "Premier"]);
  assert.deepEqual(tiers.map((t) => t.discount), ["10%", "15%", "20%"]);
  assert.deepEqual(tiers.map((t) => t.discountFraction), [0.1, 0.15, 0.2]);
  assert.equal(tiers[2].clients, "151 or more");
  const { reseller, referral } = partners();
  assert.ok(reseller.incentives.length >= 3, "the reseller programme publishes incentives");
  for (const i of reseller.incentives) assert.ok(i.id && i.name && i.text.length > 20);
  assert.equal(referral.feeText, "10%");
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
  assert.match(css, /--color-primary:#4338CA/, "the indigo primary of Nov 2, 2026");
  assert.match(css, /--color-background-alt:#/);
  assert.match(css, /--font-body:/);
  assert.ok(!/#[0-9A-Fa-f]{3}\b(?![0-9A-Fa-f])/.test(css.replace(/#[0-9A-Fa-f]{6}/g, "")), "only six-digit hex colors");
});

test("cssVariables rejects anything but six-digit hex", () => {
  assert.throws(() => cssVariables({ ...brand, colors: { ...brand.colors, primary: "red" } }));
  assert.throws(() => cssVariables({ ...brand, colors: { ...brand.colors, primary: "#abc" } }));
});

test("content: insurer questions, check counts, policy titles, mapped frameworks and controls read from the repo", () => {
  const questions = insurerQuestions();
  assert.ok(questions.length >= 8);
  assert.ok(questions.some((q) => q.automated));
  const counts = checkCounts();
  assert.equal(counts.total, counts.m365 + counts.gws + counts.attestation);
  const list = policies();
  assert.ok(list.length >= 20);
  assert.ok(list.every((p) => /^POL-\d{2}$/.test(p.id) && p.title.length > 5));
  assert.ok(list.every((p) => Object.keys(p).sort().join() === "id,title"), "policy bodies are never read for the site");
  const fws = mappedFrameworks();
  assert.deepEqual(fws.map((f) => f.id).sort(), ["hipaa", "insurer", "iso27001", "iso42001", "soc2"]);
  assert.ok(fws.every((f) => f.requirementCount > 10 && f.short.length > 2));
  const controls = controlSummary();
  assert.ok(controls.total >= 30 && controls.automated >= 5 && controls.domains.length >= 5);
});
