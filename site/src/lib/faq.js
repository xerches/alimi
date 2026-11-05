// The owner's questions on each mapped framework's page (Nov 5, 2026). The questions and answers live in
// src/data/framework-faq.yaml; the tokens in double braces are filled here from config/pricing.yaml and
// config/brand.yaml, so no price is typed in the YAML and a price change on the pricing page changes the
// answers too. An unknown token fails the build rather than printing braces.
import { readFileSync } from "node:fs";
import path from "node:path";
import { load as parseYaml } from "js-yaml";
import { CONFIG_DIR, brand, platform, quote, money, frameworkPricing } from "./config.js";

// Found from the repo root (CONFIG_DIR is <repo>/config), as content.js does, because Astro bundles this
// module into dist/.prerender at build time and a path relative to the module would point nowhere.
const file = parseYaml(readFileSync(path.join(CONFIG_DIR, "..", "site", "src", "data", "framework-faq.yaml"), "utf8"));

/** The values a question or an answer may quote. */
export function faqTokens() {
  const plat = platform();
  const [silver, gold, platinum, diamond] = plat.tiers;
  const fw = frameworkPricing();
  return {
    brand: brand.display_name,
    silverName: silver.name,
    goldName: gold.name,
    platinumName: platinum.name,
    diamondName: diamond.name,
    silverPrice: silver.perUser,
    goldPrice: gold.perUser,
    platinumPrice: platinum.perUser,
    diamondPrice: diamond.perUser,
    silver25: quote({ tierId: "silver", users: 25 }).yearlyText,
    gold25two: money(quote({ tierId: "gold", users: 25, frameworks: 2 }).yearly),
    addon: money(fw.addon),
    minimum: String(plat.minimumUsers),
  };
}

const TOKEN = /\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g;

export function fill(text, tokens = faqTokens()) {
  return String(text).replace(TOKEN, (_, key) => {
    if (!(key in tokens)) throw new Error(`framework-faq.yaml: unknown token {{${key}}}`);
    return tokens[key];
  });
}

/** The framework ids that have questions. */
export function faqFrameworkIds() {
  return Object.keys(file.frameworks ?? {});
}

/** The questions for one framework, filled in, or an empty list. */
export function frameworkFaq(id) {
  const entries = file.frameworks?.[id] ?? [];
  const tokens = faqTokens();
  return entries.map((entry) => ({ q: fill(entry.q, tokens), a: fill(entry.a, tokens) }));
}
