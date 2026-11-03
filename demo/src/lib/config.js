// Reads config/brand.yaml, config/pricing.yaml and config/frameworks.yaml at build time. Plain
// JavaScript so the Node test runner can import it without a build step. Nothing here runs in the
// browser except the small pricing calculator, which receives the numbers it needs as data attributes.
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
const catalog = load("frameworks.yaml").frameworks;

/** TODO in a config value means "not decided yet"; treat it as absent. */
export function decided(value) {
  if (value === null || value === undefined) return null;
  const text = String(value).trim();
  return text === "" || text.toUpperCase() === "TODO" ? null : text;
}

/** "$13", "$1,560" or "$16.80": whole dollars unless the amount has cents. */
export function money(amount) {
  const n = Math.round(Number(amount) * 100) / 100;
  return "$" + n.toLocaleString("en-US", Number.isInteger(n) ? { maximumFractionDigits: 0 } : { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function percent(fraction) {
  return `${Math.round(Number(fraction) * 100)}%`;
}

/** "$13 per user a month", "$500 to $1,500" or "Quoted". Mirrors templates/build/render.py. */
export function tierPrice(tier) {
  if (typeof tier.per_user_month === "number") return `${money(tier.per_user_month)} per user a month`;
  if (typeof tier.list === "number") return tier.list === 0 ? "Free" : money(tier.list);
  if (Array.isArray(tier.range) && tier.range.length === 2) return `${money(tier.range[0])} to ${money(tier.range[1])}`;
  return "Quoted";
}

export function tierNote(tier) {
  if (tier.type === "service") return "Fixed fee, confirmed after a short call";
  return "Paid monthly";
}

/** The platform's billing terms from pricing.yaml, as plain English. */
export function billingText(b = pricing.products.platform.billing) {
  return (
    `Every plan is paid monthly: a ${b.term_months}-month term at the list price, or month to month for ${percent(b.monthly_premium)} more. ` +
    `No automatic increase at renewal, and your price is locked for ${b.price_lock_months} months.`
  );
}

// One product (the platform) and the fixed-fee services around it.
export const PRODUCT_ORDER = ["platform", "services"];

export const PRODUCT_PAGES = {
  platform: "/platform",
  services: "/pricing#services",
};

// ----- frameworks: the catalog in config/frameworks.yaml and how they are priced -----

/** The catalog's categories in display order, our own grouping in the buyer's words (Nov 2, 2026). */
export const FRAMEWORK_CATEGORIES = [
  { id: "security", name: "Security", text: "The standards a customer, an insurer or a buyer's security team asks for." },
  { id: "privacy", name: "Privacy", text: "Laws and standards about personal data, by country, state and industry." },
  { id: "ai", name: "AI", text: "How a company governs the AI it builds or uses." },
  { id: "government", name: "Government and defence", text: "What federal, state and defence customers require of their suppliers." },
  { id: "financial", name: "Financial services", text: "Rules for banks, insurers, lenders, fintechs and the companies that serve them." },
  { id: "industry", name: "Industry and operations", text: "Continuity, quality and sector standards that arrive with a particular customer." },
];

const CATEGORY_IDS = new Set(FRAMEWORK_CATEGORIES.map((c) => c.id));
for (const f of catalog) {
  if (!CATEGORY_IDS.has(f.category)) throw new Error(`frameworks.yaml: "${f.id}" has an unknown category "${f.category}"`);
}

/** The page for one framework: /frameworks/<id with hyphens>. */
export function frameworkHref(id) {
  return `/frameworks/${String(id).replace(/_/g, "-")}`;
}

/** Every framework in the catalog, in order. IDs, names and our own summaries only. */
export function frameworkCatalog() {
  return catalog.map((f) => ({ ...f, always_included: Boolean(f.always_included), slug: String(f.id).replace(/_/g, "-"), href: frameworkHref(f.id) }));
}

/** The framework whose page is /frameworks/<slug>, or null. */
export function frameworkBySlug(slug) {
  return frameworkCatalog().find((f) => f.slug === slug) ?? null;
}

/** The choosable frameworks grouped by category, in category order; categories with no entry are left out. */
export function frameworksByCategory() {
  const choosable = choosableFrameworks();
  return FRAMEWORK_CATEGORIES.map((c) => ({ ...c, frameworks: choosable.filter((f) => f.category === c.id) })).filter((c) => c.frameworks.length > 0);
}

/** The frameworks a customer picks from: the catalog without the Alimi Recommended Security Posture Score, which every plan carries. */
export function choosableFrameworks() {
  return frameworkCatalog().filter((f) => !f.always_included);
}

/** The frameworks in every plan regardless of tier (the Alimi Recommended Security Posture Score). */
export function alwaysIncludedFrameworks() {
  return frameworkCatalog().filter((f) => f.always_included);
}

export function framework(id) {
  const found = catalog.find((f) => f.id === id);
  if (!found) throw new Error(`frameworks.yaml has no framework "${id}"`);
  return { ...found };
}

/** id -> name, for pages that print a framework by its ID. */
export const FRAMEWORK_LABELS = Object.fromEntries(catalog.map((f) => [f.id, f.name]));

/** "A", "A and B", "A, B and C": names in a sentence. */
export function listNames(names) {
  if (names.length <= 1) return names.join("");
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
}

/** The add-on price, the included count, the volume discounts and the cap, with text for the page. The included
 *  framework is chosen from the frameworks that are mapped today (finding 2 of the Nov 2, 2026 site scan). */
export function frameworkPricing() {
  const f = pricing.products.platform.frameworks;
  const discounts = [...f.discounts].sort((a, b) => a.from_total - b.from_total);
  return {
    included: f.included,
    addon: f.addon_per_user_month,
    addonText: `${money(f.addon_per_user_month)} per user a month`,
    discounts: discounts.map((d) => ({ fromTotal: d.from_total, off: d.discount, offText: percent(d.discount) })),
    max: f.max,
    rule: f.rule,
    includedChoices: choosableFrameworks().filter((c) => c.mapped).map((c) => c.name),
    pendingCount: choosableFrameworks().filter((c) => !c.mapped).length,
    // Two sentences, trimmed at the founder's request on Nov 2, 2026; the mapped-today list is a pricing FAQ.
    text:
      `${f.included === 1 ? "One framework of your choice is" : `${f.included} frameworks of your choice are`} included in every plan, and the ${alwaysIncludedFrameworks()[0].name} comes with all of them. ` +
      `Each further framework is ${money(f.addon_per_user_month)} per user a month, ${discounts.map((d) => `${percent(d.discount)} off from the ${ordinal(d.from_total)}`).join(" and ")}, up to ${f.max} on one account.`,
  };
}

function ordinal(n) {
  const words = { 1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth" };
  return words[n] ?? `${n}th`;
}

/** The discount on add-on frameworks for an account holding `total` frameworks (the included one counts). */
export function frameworkDiscount(total) {
  const f = pricing.products.platform.frameworks;
  let off = 0;
  for (const d of f.discounts) if (total >= d.from_total && d.discount > off) off = d.discount;
  return off;
}

/**
 * A quote for one tier: `users` people, `frameworks` frameworks on the account (1 to max), on the
 * 12-month term or month to month. Seats never drop below the plan minimum. The same arithmetic runs
 * in the browser calculator on the pricing page; keep the two in step (tests compare fixed cases).
 */
export function quote({ tierId, users, frameworks: total = 1, monthToMonth = false }) {
  const plat = pricing.products.platform;
  const tier = plat.tiers.find((t) => t.id === tierId);
  if (!tier) throw new Error(`pricing.yaml has no platform tier "${tierId}"`);
  const f = plat.frameworks;
  const held = Math.min(Math.max(1, Math.round(Number(total) || 1)), f.max);
  const seats = Math.max(Math.round(Number(users) || 0), plat.minimum_users);
  const addons = Math.max(0, held - f.included);
  const discount = frameworkDiscount(held);
  const addonRate = f.addon_per_user_month * (1 - discount);
  let perUser = tier.per_user_month + addons * addonRate;
  if (monthToMonth) perUser *= 1 + plat.billing.monthly_premium;
  perUser = Math.round(perUser * 100) / 100;
  const monthly = Math.round(perUser * seats);
  return {
    tier: tier.name,
    seats,
    frameworks: held,
    addons,
    discount,
    perUser,
    monthly,
    yearly: monthly * 12,
    perUserText: `${money(perUser)} per user a month`,
    monthlyText: `${money(monthly)} a month`,
    yearlyText: `${money(monthly * 12)} a year`,
  };
}

/** Company sizes the pricing page shows worked examples for. */
export const EXAMPLE_SIZES = [10, 25, 50, 100, 200];

function decorate(tier) {
  const out = { ...tier, price: tierPrice(tier), note: tierNote(tier) };
  if (typeof tier.per_user_month === "number") {
    const plat = pricing.products.platform;
    const b = plat.billing;
    out.perUser = money(tier.per_user_month);
    out.perUserMonthToMonth = money(Math.round(tier.per_user_month * (1 + b.monthly_premium)));
    out.termLabel = `${b.term_months}-month term`;
    out.minimumUsers = plat.minimum_users;
    out.integrationsLabel =
      tier.integrations === null || tier.integrations === undefined
        ? "Unlimited integrations"
        : `${tier.integrations} integration${tier.integrations === 1 ? "" : "s"}`;
    out.examples = EXAMPLE_SIZES.map((users) => ({ users, ...quote({ tierId: tier.id, users }) }));
    // Questionnaire allowance (Nov 2, 2026): 0 = not in the tier, a number = per year, "unlimited" = no cap.
    const q = tier.questionnaires_per_year;
    if (q === "unlimited") {
      out.questionnairesShort = "unlimited";
      out.questionnairesLabel = "Unlimited questionnaires";
    } else if (typeof q === "number" && q > 0) {
      out.questionnairesShort = `${q} a year`;
      out.questionnairesLabel = `${q} questionnaires a year`;
    } else {
      out.questionnairesShort = null;
      out.questionnairesLabel = null;
    }
  }
  return out;
}

/** "24 a year on Gold, 100 a year on Platinum, unlimited on Diamond": the questionnaire allowances in one phrase. */
export function questionnaireAllowances() {
  return platform()
    .tiers.filter((t) => t.questionnairesShort)
    .map((t) => `${t.questionnairesShort} on ${t.name}`)
    .join(", ");
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

/** The platform: tiers in price order, what every tier includes, how frameworks are priced, the billing terms. */
export function platform() {
  const entry = pricing.products.platform;
  return {
    ...product("platform"),
    included: entry.included_everywhere,
    minimumUsers: entry.minimum_users,
    frameworks: frameworkPricing(),
    billing: billingText(entry.billing),
    billingTerms: entry.billing,
    auditNote: entry.audit_note,
  };
}

export function services() {
  return product("services").tiers;
}

export function service(id) {
  const found = services().find((tier) => tier.id === id);
  if (!found) throw new Error(`pricing.yaml has no service "${id}"`);
  return found;
}

const RESELLER_TIER_NAMES = { partner: "Partner", preferred: "Preferred", premier: "Premier" };

function clientsLabel([low, high]) {
  return high === null || high === undefined ? `${low} or more` : `${low} to ${high}`;
}

export function resellerTiers() {
  return pricing.partners.reseller.tiers.map((tier) => ({
    id: tier.id,
    name: RESELLER_TIER_NAMES[tier.id] ?? tier.id,
    clients: clientsLabel(tier.active_clients),
    discount: percent(tier.discount),
    discountFraction: tier.discount,
  }));
}

export function partners() {
  const { reseller, referral, principle } = pricing.partners;
  return {
    principle,
    reseller: { ...reseller, tiers: resellerTiers(), incentives: reseller.incentives ?? [] },
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
