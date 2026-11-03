// The two numbers on Home. Audit readiness comes from data.js (share of a framework's controls that are
// Ok). The Alimi Recommended Security Posture Score is computed here from the scan results and the
// weights in config/scoring.yaml, so the platform (prompt 12c) can read the same file and the same
// rule. postureScore() is pure: give it results and rules, get a score; the tests check it against a
// hand calculation.
import { readFileSync } from "node:fs";
import path from "node:path";
import { load as parseYaml } from "js-yaml";
import { CONFIG_DIR } from "./config.js";
import { monitoring, attestations, readinessFor, frameworkCatalog } from "./data.js";

export const scoring = parseYaml(readFileSync(path.join(CONFIG_DIR, "scoring.yaml"), "utf8"));
export const postureDefinition = frameworkCatalog.find((f) => f.always_included);

/**
 * Compute the posture score.
 * @param {Array<{severity: string, kind: string, status: string, insurer_question?: string|null, attested?: boolean}>} results
 * @param {object} rules the posture_score block of config/scoring.yaml
 * @returns {{score: number|null, earned: number, possible: number, counted: number, excluded: number}}
 */
export function postureScore(results, rules = scoring.posture_score) {
  const excluded = new Set(rules.exclude_statuses ?? []);
  let earned = 0;
  let possible = 0;
  let counted = 0;
  let left = 0;
  for (const r of results) {
    if (excluded.has(r.status)) {
      left += 1;
      continue;
    }
    if (r.kind === "attestation" && !rules.attestations_count) {
      left += 1;
      continue;
    }
    const points = (rules.severity_points[r.severity] ?? 0) * (r.insurer_question ? rules.insurer_multiplier : 1);
    possible += points;
    counted += 1;
    const inPlace = r.kind === "attestation" ? Boolean(r.attested) : r.status === "pass";
    if (inPlace) earned += points;
  }
  return { score: possible ? Math.round((100 * earned) / possible) : null, earned, possible, counted, excluded: left };
}

function attested(testId) {
  return attestations(testId).some((e) => e.status === "ready" || e.status === "upcoming");
}

/** The scan results in the shape postureScore() reads, with the status of one run when a date is given. */
export function resultsAt(date) {
  return monitoring.tests.map((t) => ({
    severity: t.severity,
    kind: t.kind,
    insurer_question: t.insurer_question,
    status: date ? (t.history.find((h) => h.date === date)?.status ?? t.status) : t.status,
    attested: t.kind === "attestation" ? attested(t.check_id) : undefined,
  }));
}

export const posture = { ...postureScore(resultsAt()), version: scoring.version, asOf: monitoring.collectedAt };

/** One score per weekly scan, for the trend line. Attestations are taken as they stand today. */
export const postureHistory = monitoring.runs.map((run) => ({ date: run.date, note: run.note, score: postureScore(resultsAt(run.date)).score }));

export const auditReadiness = (() => {
  const insurer = readinessFor("insurer");
  return { id: insurer.id, short: insurer.short, percent: insurer.percent, ok: insurer.ok, total: insurer.controls.length, remaining: insurer.remaining, target: insurer.target };
})();

export const scoreDefinitions = {
  readiness: "Share of the framework's controls that are Ok: tests passing, evidence current, an owner named.",
  posture: "Check results weighted by severity and by whether an insurer asks about them. Alimi's own recommendations beyond compliance, not a certification.",
};
