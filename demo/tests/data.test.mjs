// Invariants of the sample company and the computed statuses. If the generator or the repo content
// drifts (a control test that no longer exists, an owner who is not a person), this fails first.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { load as parseYaml } from "js-yaml";
import * as d from "../src/lib/data.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const checks = parseYaml(readFileSync(path.join(here, "../../config/checks.yaml"), "utf8"));
const checkIds = new Set(checks.checks.map((c) => c.id));
const controlIds = new Set(d.controls.map((c) => c.id));
const personIds = new Set(d.people.map((p) => p.id));
const policyIds = new Set(d.policies.map((p) => p.id));
const statusKeys = new Set(Object.keys(d.STATUS));

test("the company is marked as a sample and frozen on one day", () => {
  assert.equal(d.company.sample, true);
  assert.match(d.company.as_of, /^\d{4}-\d{2}-\d{2}$/);
  assert.equal(d.staff.length, d.company.headcount);
});

test("every control test names a real check and every control has a status from the vocabulary", () => {
  for (const c of d.controls) {
    for (const id of c.tests) assert.ok(checkIds.has(id), `${c.id} tests unknown check ${id}`);
    assert.ok(statusKeys.has(c.status), `${c.id} has status ${c.status}`);
    for (const p of c.policies) assert.ok(policyIds.has(p), `${c.id} maps to unknown policy ${p}`);
  }
  assert.equal(d.controls.length, 40);
});

test("the insurer framework is fully mapped and readiness is a percentage", () => {
  const insurer = d.readinessFor("insurer");
  assert.equal(insurer.mappedRequirements, insurer.total);
  for (const r of d.readiness) assert.ok(r.percent >= 0 && r.percent <= 100, `${r.id} readiness ${r.percent}`);
});

test("evidence points at real controls and owners, and every status is in the vocabulary", () => {
  for (const e of d.evidence) {
    assert.ok(e.controls.length > 0, `${e.id} has no control`);
    for (const id of e.controls) assert.ok(controlIds.has(id), `${e.id} points at unknown control ${id}`);
    if (e.owner) assert.ok(personIds.has(e.owner), `${e.id} owner ${e.owner} is not a person`);
    assert.ok(statusKeys.has(e.status), `${e.id} status ${e.status}`);
    for (const t of e.attests ?? []) assert.ok(checkIds.has(t), `${e.id} attests unknown check ${t}`);
  }
});

test("vendors, risks, AI tools and tasks have real owners or none", () => {
  for (const v of d.vendors) if (v.owner) assert.ok(personIds.has(v.owner), `${v.id} owner`);
  for (const r of d.risks) {
    if (r.owner) assert.ok(personIds.has(r.owner), `${r.id} owner`);
    for (const id of r.controls) assert.ok(controlIds.has(id), `${r.id} control ${id}`);
  }
  for (const t of d.aiTools) if (t.owner) assert.ok(personIds.has(t.owner), `${t.id} owner`);
  for (const t of d.tasks) if (t.owner) assert.ok(personIds.has(t.owner), `task "${t.title}" owner ${t.owner}`);
});

test("every policy in the repo has adoption data and an acknowledgement count that fits its audience", () => {
  assert.equal(d.policies.length, 23);
  for (const p of d.policies) {
    assert.ok(p.version && p.status_label, `${p.id} lacks adoption data`);
    assert.ok(p.acknowledged >= 0 && p.acknowledged <= p.audience, `${p.id} acknowledged ${p.acknowledged} of ${p.audience}`);
    assert.ok(p.outline.length >= 3, `${p.id} has no section outline`);
    assert.ok(p.words > 200 && p.summary.length > 20, `${p.id} did not render`);
    assert.ok(!p.summary.includes("{{") && !p.outline.join().includes("{{"), `${p.id} has an unfilled placeholder`);
    assert.equal(p.html, undefined, `${p.id} carries policy text; the demo publishes none`);
  }
});

test("the questionnaires answer every insurer question and the bank's open items are counted", () => {
  const ids = new Set(d.questionnaires.insurer.answers.map((a) => a.question_id));
  for (const id of Object.keys(d.insurerQuestions)) assert.ok(ids.has(id), `insurer question ${id} unanswered`);
  assert.equal(d.questionnaires.bank.drafted + d.questionnaires.bank.open, d.questionnaires.bank.questions.length);
});

test("the scan file matches the snapshot's tenant and every finding is a known check", () => {
  assert.equal(d.scan.tenant.display_name, "Saltmarsh Payroll");
  assert.equal(d.scan.tenant.source.startsWith("mock"), true);
  for (const f of d.scan.findings) assert.ok(checkIds.has(f.check_id), `finding ${f.check_id}`);
});

test("the assistant preview has an answer with items for every prepared question", () => {
  for (const a of d.assistantAnswers) assert.ok(a.items.length > 0, `${a.id} has no items`);
});
