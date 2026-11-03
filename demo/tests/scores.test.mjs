// The Alimi Recommended Security Posture Score against a hand calculation, so a change to
// config/scoring.yaml or to the scan fixture shows up here before it shows up on a customer's Home.
import { test } from "node:test";
import assert from "node:assert/strict";
import { postureScore, posture, postureHistory, resultsAt, scoring, auditReadiness } from "../src/lib/scores.js";
import { monitoring, attestations } from "../src/lib/data.js";

const rules = { severity_points: { critical: 4, high: 3, medium: 2, low: 1 }, insurer_multiplier: 1.5, attestations_count: true, exclude_statuses: ["error", "not_applicable", "not_run"] };

test("postureScore follows the rule in config/scoring.yaml on a hand-built set", () => {
  const results = [
    { severity: "critical", kind: "automated", status: "pass", insurer_question: "mfa" }, // 6 of 6
    { severity: "high", kind: "automated", status: "fail", insurer_question: "email_security" }, // 0 of 4.5
    { severity: "low", kind: "automated", status: "pass", insurer_question: null }, // 1 of 1
    { severity: "critical", kind: "attestation", status: "attestation_needed", insurer_question: null, attested: true }, // 4 of 4
    { severity: "high", kind: "attestation", status: "attestation_needed", insurer_question: null, attested: false }, // 0 of 3
    { severity: "medium", kind: "automated", status: "error", insurer_question: "logging" }, // left out
  ];
  const r = postureScore(results, rules);
  assert.equal(r.possible, 18.5);
  assert.equal(r.earned, 11);
  assert.equal(r.score, 59); // 11 / 18.5 = 0.5946
  assert.equal(r.counted, 5);
  assert.equal(r.excluded, 1);
});

test("attestations can be switched off, and an empty set has no score", () => {
  const results = [{ severity: "critical", kind: "attestation", status: "attestation_needed", attested: true }];
  assert.equal(postureScore(results, { ...rules, attestations_count: false }).score, null);
  assert.equal(postureScore([], rules).score, null);
});

test("the sample company's score matches the arithmetic on its scan", () => {
  // Every check in config/checks.yaml answers an insurer question, so the 1.5 multiplier applies to all
  // of them and cancels out of the ratio. Automated checks on Oct 30, 2026: 12, worth 33 points by
  // severity (critical 4 x 3, high 3 x 5, medium 2 x 2, low 1 x 2); three fail (MFA coverage, critical 4;
  // external forwarding, high 3; anonymous links, medium 2) = 9 points lost. Attestations: EDR (critical 4),
  // backups (critical 4), incident drill (high 3) = 11 points; the ones with current evidence count.
  const attested = monitoring.tests.filter((t) => t.kind === "attestation").map((t) => ({ t, ok: attestations(t.check_id).some((e) => e.status === "ready" || e.status === "upcoming") }));
  const attestedPoints = attested.filter((a) => a.ok).reduce((n, a) => n + rules.severity_points[a.t.severity], 0);
  const expectedPossible = (33 + 11) * 1.5;
  const expectedEarned = (33 - 9 + attestedPoints) * 1.5;
  assert.equal(scoring.posture_score.insurer_multiplier, 1.5);
  assert.equal(posture.possible, expectedPossible);
  assert.equal(posture.earned, expectedEarned);
  assert.equal(posture.score, Math.round((100 * expectedEarned) / expectedPossible));
  assert.ok(posture.score >= 0 && posture.score <= 100);
});

test("the trend has one score per weekly scan and the first scan was worse than today", () => {
  assert.equal(postureHistory.length, monitoring.runs.length);
  for (const h of postureHistory) assert.ok(h.score >= 0 && h.score <= 100, `${h.date}: ${h.score}`);
  assert.ok(postureHistory[0].score < posture.score, "eight checks failed on the first scan");
  assert.equal(postureHistory.at(-1).score, posture.score);
  assert.equal(resultsAt(monitoring.runs[0].date).filter((r) => r.status === "fail").length, 8);
});

test("audit readiness is the insurer framework's readiness", () => {
  assert.equal(auditReadiness.id, "insurer");
  assert.ok(auditReadiness.percent >= 0 && auditReadiness.percent <= 100);
  assert.equal(auditReadiness.ok + auditReadiness.remaining, auditReadiness.total);
});
