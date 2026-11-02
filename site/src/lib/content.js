// Reads repo data the pages render: insurer questions and check counts from config/checks.yaml,
// policy names from /policies. Build time only, like config.js.
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { load as parseYaml } from "js-yaml";
import { marked } from "marked";
import { CONFIG_DIR } from "./config.js";

export const REPO_DIR = path.resolve(CONFIG_DIR, "..");

const checksFile = parseYaml(readFileSync(path.join(CONFIG_DIR, "checks.yaml"), "utf8"));

/** The underwriting questions the scanner gives evidence for, with whether a tenant read answers them. */
export function insurerQuestions() {
  return Object.entries(checksFile.insurer_questions).map(([id, question]) => ({
    id,
    question,
    automated: checksFile.checks.some((check) => check.insurer_question === id && check.kind === "automated"),
  }));
}

export function checkCounts() {
  const counts = { m365: 0, gws: 0, attestation: 0, total: checksFile.checks.length };
  for (const check of checksFile.checks) {
    if (check.kind === "attestation") counts.attestation += 1;
    else if (check.platform === "m365") counts.m365 += 1;
    else if (check.platform === "gws") counts.gws += 1;
  }
  return counts;
}

export function check(id) {
  const found = checksFile.checks.find((entry) => entry.id === id);
  if (!found) throw new Error(`checks.yaml has no check "${id}"`);
  return found;
}

const FRONT_MATTER = /^---\n([\s\S]*?)\n---/;

/** id and title of every policy in /policies, in file order. */
export function policies() {
  const dir = path.join(REPO_DIR, "policies");
  return readdirSync(dir)
    .filter((file) => /^\d{2}-.*\.md$/.test(file))
    .sort()
    .map((file) => {
      const text = readFileSync(path.join(dir, file), "utf8");
      const match = FRONT_MATTER.exec(text);
      if (!match) throw new Error(`${file} has no front matter`);
      const meta = parseYaml(match[1]);
      return { id: meta.id, title: meta.title };
    });
}

export function formatDate(value) {
  const date = value instanceof Date ? value : new Date(value);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
}


/** Frameworks from policies/requirements.yaml: id, name, short name and requirement count. No framework text is stored. */
export function frameworks() {
  const file = parseYaml(readFileSync(path.join(REPO_DIR, "policies", "requirements.yaml"), "utf8"));
  return Object.entries(file.frameworks).map(([id, fw]) => ({
    id,
    name: fw.name,
    short: fw.short,
    requirementCount: Object.keys(fw.requirements ?? {}).length,
  }));
}

/** The control catalogue in config/controls.yaml: count, domains and how many have an automated test. */
export function controlSummary() {
  const file = parseYaml(readFileSync(path.join(CONFIG_DIR, "controls.yaml"), "utf8"));
  const list = file.controls ?? [];
  const domains = [...new Set(list.map((c) => c.domain))];
  const automated = list.filter((c) => (c.tests ?? []).length > 0).length;
  return { total: list.length, domains, automated };
}

// Documents from the repo rendered as pages: the free policies and the payment fraud procedure.
export const FREE_DOCS = [
  { slug: "information-security-policy", file: "policies/01-information-security-policy.md", group: "Core policies" },
  { slug: "acceptable-use-policy", file: "policies/02-acceptable-use-policy.md", group: "Core policies" },
  { slug: "incident-response-policy", file: "policies/13-incident-response-policy.md", group: "Core policies" },
  { slug: "ai-acceptable-use-policy", file: "policies/22-ai-acceptable-use-policy.md", group: "AI policy" },
  { slug: "payment-verification-procedure", file: "kits/payment-fraud/procedure.md", group: "Payment fraud procedure" },
  { slug: "callback-scripts", file: "kits/payment-fraud/callback-scripts.md", group: "Payment fraud procedure" },
  { slug: "payment-fraud-poster", file: "kits/payment-fraud/poster.md", group: "Payment fraud procedure" },
];

const ROLE_PLACEHOLDERS = ["Security Lead", "IT Lead", "HR Lead", "Finance Lead", "Privacy Lead", "AI Lead", "CEO"];

/** Fill the template placeholders for reading on the site; the downloaded documents keep them. */
export function fillPlaceholders(text) {
  const filled = text.replace(/\{\{\s*([^}]+?)\s*\}\}/g, (_, name) => {
    if (name === "Company") return "the Company";
    if (ROLE_PLACEHOLDERS.includes(name)) return `the ${name}`;
    return `[${name.toLowerCase()}]`;
  });
  // "the Company" at the start of a sentence, list item or table cell reads "The Company".
  return filled.replace(/(^|[.!?:]\s+|\n\s*\n\s*|\n\s*(?:[-*]|\d+\.)\s+(?:\[[ x]\]\s+)?|\|\s*)the (?=[A-Z])/g, (_, pre) => `${pre}The `);
}

/** A repo Markdown document as a page: front matter, HTML body without its own h1, and the word count. */
export function freeDoc(slug) {
  const entry = FREE_DOCS.find((d) => d.slug === slug);
  if (!entry) throw new Error(`no free document "${slug}"`);
  const text = readFileSync(path.join(REPO_DIR, entry.file), "utf8");
  const match = FRONT_MATTER.exec(text);
  if (!match) throw new Error(`${entry.file} has no front matter`);
  const meta = parseYaml(match[1]);
  const body = text.slice(match[0].length);
  const filled = fillPlaceholders(body);
  const html = marked
    .parse(filled, { gfm: true })
    .replace(/<h1>[\s\S]*?<\/h1>\s*/, "")
    // GFM task items render as disabled checkboxes with no label; on a printed checklist a box glyph says the same thing.
    .replace(/<input (checked="" )?disabled="" type="checkbox">\s*/g, (_, checked) => `<span class="box" aria-hidden="true">${checked ? "☑" : "☐"}</span> `);
  return {
    ...entry,
    id: meta.id,
    title: meta.title,
    version: meta.version ?? null,
    requirements: meta.requirements ?? null,
    html,
    words: filled.split(/\s+/).filter(Boolean).length,
  };
}

export function freeDocs() {
  return FREE_DOCS.map((d) => freeDoc(d.slug));
}
