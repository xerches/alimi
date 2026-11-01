// Reads repo data the pages render: insurer questions and check counts from config/checks.yaml,
// policy names from /policies. Build time only, like config.js.
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { load as parseYaml } from "js-yaml";
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
