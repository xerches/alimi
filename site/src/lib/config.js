// Reads config/brand.yaml and config/pricing.yaml at build time. Plain JavaScript so the Node test
// runner can import it without a build step. Nothing here runs in the browser.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { load as parseYaml } from "js-yaml";

// Astro bundles this module into dist/.prerender at build time, so the config folder is found by
// walking up from wherever the module runs until /config/brand.yaml appears.
function findConfigDir(start) {
  let dir = start;
  for (;;) {
    const candidate = path.join(dir, "config", "brand.yaml");
    if (existsSync(candidate)) return path.dirname(candidate);
    const parent = path.dirname(dir);
    if (parent === dir) throw new Error(`config/brand.yaml not found above ${start}`);
    dir = parent;
  }
}

export const CONFIG_DIR = findConfigDir(path.dirname(fileURLToPath(import.meta.url)));

function load(name) {
  return parseYaml(readFileSync(path.join(CONFIG_DIR, name), "utf8"));
}

export const brand = load("brand.yaml");
export const pricing = load("pricing.yaml");

/** TODO in a config value means "not decided yet"; treat it as absent. */
export function decided(value) {
  if (value === null || value === undefined) return null;
  const text = String(value).trim();
  return text === "" || text.toUpperCase() === "TODO" ? null : text;
}

export function money(amount) {
  return "$" + Number(amount).toLocaleString("en-US");
}

/** "Free", "$499" or "$500 to $1,500". `list` wins over `range`, as in templates/build/render.py. */
export function tierPrice(tier) {
  if (typeof tier.list === "number") return tier.list === 0 ? "Free" : money(tier.list);
  if (Array.isArray(tier.range) && tier.range.length === 2) return `${money(tier.range[0])} to ${money(tier.range[1])}`;
  return "Quoted";
}

export function tierNote(tier) {
  if (tier.type === "service") return "Fixed fee, confirmed after a short call";
  if (tier.list === 0) return "No card and no account needed";
  return "Paid monthly";
}

/** The platform's billing terms from pricing.yaml, as one plain-English sentence pair. */
export function billingText(b = pricing.products.platform.billing) {
  return (
    `Every plan is paid monthly: a ${b.term_months}-month term at the list price, or month to month for ${percent(b.monthly_premium)} more. ` +
    `No automatic increase at renewal, and your price is locked for ${b.price_lock_months} months. ${b.exit}`
  );
}

// One product (the platform), the fixed-fee services around it, and the free resources in front of it.
export const PRODUCT_ORDER = ["platform", "services", "free"];

export const PRODUCT_PAGES = {
  platform: "/platform",
  services: "/pricing#services",
  free: "/resources",
};

export const FRAMEWORK_LABELS = {
  insurer: "Cyber insurance questionnaire",
  soc2: "SOC 2",
  iso27001: "ISO 27001",
  hipaa: "HIPAA",
  iso42001: "ISO 42001",
};

function decorate(tier) {
  const out = { ...tier, price: tierPrice(tier), note: tierNote(tier) };
  if (typeof tier.people_up_to === "number") {
    const b = pricing.products.platform.billing;
    out.monthly = `${money(Math.round(tier.list / b.term_months))} a month`;
    out.monthToMonth = `${money(Math.round((tier.list / b.term_months) * (1 + b.monthly_premium)))} a month`;
    out.termLabel = `${b.term_months}-month term`;
    out.yearly = `${money(tier.list)} a year`;
    out.peopleLabel = `Up to ${tier.people_up_to} people`;
    out.frameworkLabels = (tier.frameworks ?? []).map((id) => FRAMEWORK_LABELS[id] ?? id);
    out.integrationsLabel =
      tier.integrations === null || tier.integrations === undefined
        ? "Unlimited integrations"
        : `${tier.integrations} integration${tier.integrations === 1 ? "" : "s"}`;
  }
  return out;
}

export function product(key) {
  const entry = pricing.products[key];
  if (!entry) throw new Error(`pricing.yaml has no product "${key}"`);
  return {
    key,
    name: entry.name,
    tagline: entry.tagline,
    href: PRODUCT_PAGES[key],
    tiers: entry.tiers.map(decorate),
  };
}

export function products(order = PRODUCT_ORDER) {
  return order.map(product);
}

/** The platform: tiers in price order plus what every tier includes. */
export function platform() {
  const entry = pricing.products.platform;
  return {
    ...product("platform"),
    included: entry.included_everywhere,
    billing: billingText(entry.billing),
    billingTerms: entry.billing,
    auditNote: entry.audit_note,
  };
}

export function services() {
  return product("services").tiers;
}

export function freeResources() {
  return product("free").tiers;
}

export function service(id) {
  const found = services().find((tier) => tier.id === id);
  if (!found) throw new Error(`pricing.yaml has no service "${id}"`);
  return found;
}

const TIER_NAMES = { starter: "Starter", growth: "Growth", scale: "Scale" };

function clientsLabel([low, high]) {
  return high === null || high === undefined ? `${low} or more` : `${low} to ${high}`;
}

export function percent(fraction) {
  return `${Math.round(Number(fraction) * 100)}%`;
}

export function resellerTiers() {
  return pricing.partners.reseller.tiers.map((tier) => ({
    id: tier.id,
    name: TIER_NAMES[tier.id] ?? tier.id,
    clients: clientsLabel(tier.active_clients),
    discount: percent(tier.discount),
  }));
}

export function partners() {
  const { reseller, referral, principle } = pricing.partners;
  return {
    principle,
    reseller: { ...reseller, tiers: resellerTiers() },
    referral: { ...referral, feeText: percent(referral.fee) },
  };
}

export function retainer() {
  const r = pricing.retainers.fractional_security_lead;
  return {
    name: r.name,
    price: `${money(r.range_per_month[0])} to ${money(r.range_per_month[1])} a month`,
    hours: `${r.hours_per_month[0]} to ${r.hours_per_month[1]} hours a month`,
  };
}

export const terms = pricing.terms;
