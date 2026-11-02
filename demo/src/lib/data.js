// The demo's data layer. Reads the sample company from demo/data/*.json and the product content from
// the repo (config/controls.yaml, config/checks.yaml, policies/requirements.yaml, policies/*.md), then
// computes every status the screens show: control status, evidence status, framework readiness,
// policy acknowledgements, people compliance, tasks and the owner view. Build time only; nothing
// here runs in the browser. The platform (prompt 12) replaces the JSON reads with database queries
// and keeps the rules.
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { load as parseYaml } from "js-yaml";
import { marked } from "marked";
import { CONFIG_DIR } from "./config.js";

export const REPO_DIR = path.resolve(CONFIG_DIR, "..");
const DATA_DIR = path.join(REPO_DIR, "demo", "data");
const json = (name) => JSON.parse(readFileSync(path.join(DATA_DIR, name), "utf8"));
const yaml = (file) => parseYaml(readFileSync(file, "utf8"));

// ------------------------------------------------------------------ raw inputs

export const company = json("company.json");
export const AS_OF = new Date(`${company.as_of}T00:00:00Z`);
const peopleFile = json("people.json");
const assignments = json("assignments.json");
const policyMeta = json("policies.json").policies;
const evidenceFile = json("evidence.json").evidence;
const vendorsFile = json("vendors.json");
const aiFile = json("ai-tools.json");
const risksFile = json("risks.json");
const questionnairesFile = json("questionnaires.json");
const assetsFile = json("assets.json");
const trainingFile = json("training.json");
export const integrations = json("integrations.json");
export const scan = json("scan.json");
const monitoringFile = json("monitoring-history.json");

const controlsFile = yaml(path.join(CONFIG_DIR, "controls.yaml"));
const checksFile = yaml(path.join(CONFIG_DIR, "checks.yaml"));
const requirementsFile = yaml(path.join(REPO_DIR, "policies", "requirements.yaml"));

// ------------------------------------------------------------------ helpers

const DAY = 86_400_000;
export function daysUntil(value) {
  if (!value) return null;
  return Math.round((new Date(`${value}T00:00:00Z`) - AS_OF) / DAY);
}
export function formatDate(value) {
  if (!value) return "";
  const date = value instanceof Date ? value : new Date(value.length === 10 ? `${value}T00:00:00Z` : value);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
}
export function formatDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  return `${formatDate(date)}, ${date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", timeZone: "America/New_York" })} ET`;
}
export function pct(part, whole) {
  return whole ? Math.round((100 * part) / whole) : 0;
}
export function plural(n, word, pluralWord) {
  return `${n} ${n === 1 ? word : (pluralWord ?? `${word}s`)}`;
}
export const href = {
  control: (id) => `/controls/${id}`,
  policy: (id) => `/policies/${id}`,
  framework: (id) => `/frameworks/${id}`,
  person: (id) => `/people/${id}`,
  vendor: (id) => `/vendors/${id}`,
  evidence: (id) => `/evidence#${id}`,
  risk: (id) => `/risks#${id}`,
  test: (id) => `/monitoring#${id.replaceAll(".", "-")}`,
  ai: (id) => `/ai#${id}`,
};

// Status vocabulary: few words, the same everywhere. tone picks the colour token.
export const STATUS = {
  ok: { label: "Ok", tone: "success" },
  needs_attention: { label: "Needs attention", tone: "danger" },
  needs_evidence: { label: "Needs evidence", tone: "warning" },
  needs_owner: { label: "Needs owner", tone: "warning" },
  ready: { label: "Ready", tone: "success" },
  upcoming: { label: "Upcoming renewal", tone: "info" },
  needs_renewal: { label: "Needs renewal", tone: "warning" },
  needs_artifact: { label: "Needs artifact", tone: "danger" },
  pass: { label: "Pass", tone: "success" },
  fail: { label: "Fail", tone: "danger" },
  attestation_needed: { label: "Attestation", tone: "info" },
  error: { label: "Error", tone: "warning" },
  not_run: { label: "Not run", tone: "neutral" },
  published: { label: "Published", tone: "success" },
  renews_soon: { label: "Renews soon", tone: "info" },
  past_due: { label: "Past due", tone: "danger" },
  needs_approval: { label: "Needs approval", tone: "warning" },
  draft: { label: "Draft", tone: "neutral" },
  compliant: { label: "Compliant", tone: "success" },
  not_compliant: { label: "Not compliant", tone: "warning" },
  completed: { label: "Completed", tone: "success" },
  due: { label: "Due", tone: "warning" },
  overdue: { label: "Overdue", tone: "danger" },
};
export function status(key) {
  return STATUS[key] ?? { label: key, tone: "neutral" };
}
export const TONE_FOR = {
  // vendor review and AI statuses, risk ratings and tiers
  Reviewed: "success", Due: "danger", "In progress": "warning", "Under review": "warning", Blocked: "danger", "Not required": "neutral",
  Approved: "success", Critical: "danger", High: "warning", Medium: "info", Low: "neutral", Open: "warning", Treating: "info", Accepted: "neutral", Closed: "success",
  Yes: "success", Partial: "warning", No: "danger", Connected: "success", Available: "neutral",
};
export function tone(value) {
  return TONE_FOR[value] ?? "neutral";
}

// ------------------------------------------------------------------ people

export const people = peopleFile.people;
const personById = new Map(people.map((p) => [p.id, p]));
export function person(id) {
  return id ? personById.get(id) ?? null : null;
}
export function personName(id, fallback = "Unassigned") {
  return person(id)?.name ?? fallback;
}
export function roleOwner(roleKey) {
  return person(company.roles[roleKey]);
}
export const groups = company.groups;
for (const p of people) {
  p.groups = Object.entries(groups).filter(([, ids]) => ids.includes(p.id)).map(([name]) => name);
  p.managerName = personName(p.manager, "");
  p.deviceRecord = assetsFile.devices.find((d) => d.id === p.device) ?? null;
}

// ------------------------------------------------------------------ frameworks and requirements

export const frameworkCatalog = yaml(path.join(REPO_DIR, "config", "frameworks.yaml")).frameworks;
const FRAMEWORK_ORDER = company.frameworks;
export const frameworks = FRAMEWORK_ORDER.map((id) => {
  const fw = requirementsFile.frameworks[id];
  return {
    id,
    name: fw.name,
    short: fw.short,
    requirements: fw.requirements,
    total: Object.keys(fw.requirements).length,
    target: company.framework_targets[id] ?? null,
  };
});
const frameworkById = new Map(frameworks.map((f) => [f.id, f]));
export function framework(id) {
  return frameworkById.get(id);
}
export function requirementSummary(fwId, reqId) {
  return frameworkById.get(fwId)?.requirements?.[reqId] ?? "";
}

// ------------------------------------------------------------------ checks, findings, monitoring

const checkById = new Map(checksFile.checks.map((c) => [c.id, c]));
export const insurerQuestions = checksFile.insurer_questions;
const findingById = new Map(scan.findings.map((f) => [f.check_id, f]));
const remediationByTest = new Map((company.remediation_plan ?? []).map((r) => [r.test, r]));

export const monitoring = {
  runs: monitoringFile.runs,
  collectedAt: scan.collected_at,
  summary: scan.summary,
  tests: scan.findings.map((f) => ({
    ...f,
    definition: checkById.get(f.check_id) ?? null,
    history: monitoringFile.history[f.check_id] ?? [],
    remediation_plan: remediationByTest.get(f.check_id) ?? null,
    anchor: f.check_id.replaceAll(".", "-"),
    controls: [],
  })),
};
const testById = new Map(monitoring.tests.map((t) => [t.check_id, t]));
export function testResult(id) {
  return testById.get(id) ?? null;
}
export const insurerAnswers = scan.insurer_answers;

// ------------------------------------------------------------------ evidence

function evidenceStatus(e) {
  if (!e.artifact) return "needs_artifact";
  if (!e.renewal) return "ready";
  const days = daysUntil(e.renewal);
  if (days < 0) return "needs_renewal";
  if (days <= 30) return "upcoming";
  return "ready";
}
export const evidence = evidenceFile.map((e) => ({
  ...e,
  status: evidenceStatus(e),
  ownerName: personName(e.owner),
  daysToRenewal: daysUntil(e.renewal),
}));
const evidenceById = new Map(evidence.map((e) => [e.id, e]));
export function evidenceItem(id) {
  return evidenceById.get(id) ?? null;
}
const evidenceByControl = new Map();
for (const e of evidence) {
  for (const cid of e.controls) {
    if (!evidenceByControl.has(cid)) evidenceByControl.set(cid, []);
    evidenceByControl.get(cid).push(e);
  }
}
const attestedBy = new Map(); // test id -> evidence items that attest it
for (const e of evidence) {
  for (const t of e.attests ?? []) {
    if (!attestedBy.has(t)) attestedBy.set(t, []);
    attestedBy.get(t).push(e);
  }
}
export function attestations(testId) {
  return attestedBy.get(testId) ?? [];
}

// ------------------------------------------------------------------ policies

const FRONT_MATTER = /^---\n([\s\S]*?)\n---\n?/;
const policyDir = path.join(REPO_DIR, "policies");
const ROLE_LABELS = Object.keys(company.roles);

function fillPlaceholders(text, meta) {
  return text
    .replaceAll("{{Company}}", company.name)
    .replaceAll("{{Effective Date}}", meta.approved ? formatDate(meta.approved) : "Pending approval")
    .replace(/\{\{([^}]+)\}\}/g, (_, name) => (ROLE_LABELS.includes(name) ? name : name));
}

export const policies = readdirSync(policyDir)
  .filter((file) => /^\d{2}-.*\.md$/.test(file))
  .sort()
  .map((file) => {
    const text = readFileSync(path.join(policyDir, file), "utf8");
    const match = FRONT_MATTER.exec(text);
    if (!match) throw new Error(`${file} has no front matter`);
    const front = parseYaml(match[1]);
    const meta = policyMeta.find((m) => m.id === front.id);
    if (!meta) throw new Error(`demo/data/policies.json has no entry for ${front.id}`);
    let body = text.slice(match[0].length);
    // The repo file carries the template banner; the sample company has adopted the policy, so the
    // banner is replaced by an adoption note on the page.
    body = body.replace(/^>\s*\*\*TEMPLATE\.[^\n]*\n+/, "");
    body = fillPlaceholders(body, meta);
    // Policy text is never published (founder's rule, Nov 2, 2026): the page shows the outline, the
    // opening paragraph and the word count, and the full document stays inside the platform.
    const outline = [...body.matchAll(/^##\s+(.+)$/gm)].map((m) => m[1].trim());
    const opening = body
      .split(/\n\s*\n/)
      .map((s) => s.trim())
      .find((s) => s && !/^(#|>|\||[-*]\s|\d+\.\s)/.test(s));
    const summary = marked.parseInline(opening ?? "", { gfm: true });
    const words = body.split(/\s+/).filter(Boolean).length;
    const groupName = meta.applies_to === "all" ? "All staff" : meta.applies_to;
    const audience = groups[groupName] ?? [];
    const pending = audience.filter((pid) => {
      const p = person(pid);
      return p && (p.policies_pending === "all" || p.policies_pending.includes(front.id));
    });
    return {
      ...front,
      file,
      ...meta,
      ownerName: personName(meta.owner),
      approverName: personName(meta.approver),
      audienceName: groupName,
      audience: audience.length,
      acknowledged: audience.length - pending.length,
      pendingPeople: pending,
      requirementCount: Object.values(front.requirements ?? {}).reduce((n, ids) => n + (ids?.length ?? 0), 0),
      outline,
      summary,
      words,
      controls: [],
    };
  });
const policyById = new Map(policies.map((p) => [p.id, p]));
export function policy(id) {
  return policyById.get(id) ?? null;
}

// ------------------------------------------------------------------ controls

const ROLE_FROM_PLACEHOLDER = /^\{\{(.+)\}\}$/;
function resolveOwner(control) {
  const assignment = assignments[control.id] ?? {};
  if (assignment.unassigned) return { owner: null, approver: person(assignment.approver), note: assignment.note };
  if (assignment.owner) return { owner: person(assignment.owner), approver: person(assignment.approver), note: assignment.note };
  const role = ROLE_FROM_PLACEHOLDER.exec(control.owner_role)?.[1];
  return { owner: roleOwner(role), approver: person(assignment.approver ?? company.roles.CEO), note: assignment.note, role };
}

function controlStatus(control, tests, items) {
  if (!control.owner) return "needs_owner";
  if (tests.some((t) => t.status === "fail" || t.status === "error")) return "needs_attention";
  const unattested = tests.filter((t) => t.status === "attestation_needed" && !attestations(t.check_id).some((e) => e.status === "ready" || e.status === "upcoming"));
  if (unattested.length) return "needs_evidence";
  if (items.length === 0) return "needs_evidence";
  if (items.some((e) => e.status === "needs_artifact" || e.status === "needs_renewal")) return "needs_evidence";
  return "ok";
}

export const controls = controlsFile.controls.map((c) => {
  const { owner, approver, note, role } = resolveOwner(c);
  const tests = c.tests.map((id) => testResult(id)).filter(Boolean);
  const items = evidenceByControl.get(c.id) ?? [];
  const control = {
    ...c,
    owner,
    ownerName: owner?.name ?? "Unassigned",
    ownerRole: role ?? ROLE_FROM_PLACEHOLDER.exec(c.owner_role)?.[1] ?? c.owner_role,
    approver,
    assignmentNote: note ?? null,
    testResults: tests,
    testsNotRun: c.tests.filter((id) => !testResult(id)),
    evidenceItems: items,
    frameworks: FRAMEWORK_ORDER.filter((fw) => (c.requirements?.[fw] ?? []).length > 0),
    policyRecords: c.policies.map((id) => policy(id)).filter(Boolean),
    domainLabel: controlsFile.domains[c.domain],
    frequencyLabel: controlsFile.frequencies[c.frequency],
    lastChecked: tests.length ? scan.collected_at : items.map((e) => e.created).filter(Boolean).sort().at(-1) ?? null,
  };
  control.status = controlStatus(control, tests, items);
  return control;
});
const controlById = new Map(controls.map((c) => [c.id, c]));
export function control(id) {
  return controlById.get(id) ?? null;
}
for (const c of controls) {
  for (const t of c.testResults) t.controls.push(c);
  for (const p of c.policyRecords) p.controls.push(c);
}
export const controlDomains = Object.entries(controlsFile.domains).map(([id, label]) => ({ id, label, controls: controls.filter((c) => c.domain === id) }));
export const evidenceTypes = controlsFile.evidence_types;

export function controlCounts(list = controls) {
  const counts = { ok: 0, needs_attention: 0, needs_evidence: 0, needs_owner: 0 };
  for (const c of list) counts[c.status] += 1;
  return counts;
}

// ------------------------------------------------------------------ framework readiness

export const readiness = frameworks.map((fw) => {
  const inScope = controls.filter((c) => c.frameworks.includes(fw.id));
  const ok = inScope.filter((c) => c.status === "ok").length;
  const mapped = new Set();
  for (const c of inScope) for (const id of c.requirements[fw.id] ?? []) mapped.add(id);
  return {
    ...fw,
    controls: inScope,
    ok,
    remaining: inScope.length - ok,
    percent: pct(ok, inScope.length),
    mappedRequirements: mapped.size,
    daysToTarget: daysUntil(fw.target?.date),
  };
});
export function readinessFor(id) {
  return readiness.find((r) => r.id === id);
}
/** Requirements of one framework with the controls that satisfy each. */
export function requirementRows(fwId) {
  const fw = framework(fwId);
  return Object.entries(fw.requirements).map(([id, summary]) => {
    const mapped = controls.filter((c) => (c.requirements[fwId] ?? []).includes(id));
    const policiesMapped = policies.filter((p) => (p.requirements?.[fwId] ?? []).includes(id));
    const stateKey = mapped.length === 0 ? "needs_evidence" : mapped.every((c) => c.status === "ok") ? "ok" : mapped.some((c) => c.status === "needs_attention") ? "needs_attention" : "needs_evidence";
    return { id, summary, controls: mapped, policies: policiesMapped, status: mapped.length === 0 ? "unmapped" : stateKey };
  });
}

// ------------------------------------------------------------------ vendors, AI, risks

export const vendorRubric = vendorsFile.rubric;
export const vendors = vendorsFile.vendors.map((v) => ({
  ...v,
  ownerName: personName(v.owner),
  rubricTotal: Object.values(v.rubric).reduce((a, b) => a + b, 0),
  daysToReview: daysUntil(v.next_review),
  aiTools: aiFile.tools.filter((t) => t.vendor_id === v.id),
  risks: risksFile.risks.filter((r) => (v.findings ?? []).some((f) => f.risk === r.id)),
}));
const vendorById = new Map(vendors.map((v) => [v.id, v]));
export function vendor(id) {
  return vendorById.get(id) ?? null;
}
export const vendorCounts = {
  total: vendors.length,
  byTier: Object.fromEntries(["Critical", "High", "Medium", "Low"].map((t) => [t, vendors.filter((v) => v.inherent_risk === t).length])),
  alerts: vendors.filter((v) => v.alerts.length).length,
  needingAction: vendors.filter((v) => ["Due", "In progress", "Under review"].includes(v.review_status)).length,
  needsOwner: vendors.filter((v) => !v.owner && v.review_status !== "Not required").length,
  subprocessors: vendors.filter((v) => v.subprocessor),
};

export const aiTools = aiFile.tools.map((t) => ({ ...t, ownerName: personName(t.owner), vendorRecord: vendor(t.vendor_id) }));
export const aiVendorChanges = aiFile.vendor_changes.map((c) => ({ ...c, tools: c.affects.map((id) => aiTools.find((t) => t.id === id)).filter(Boolean) }));
export const aiCounts = {
  total: aiTools.length,
  byStatus: Object.fromEntries(["Approved", "Under review", "Blocked"].map((s) => [s, aiTools.filter((t) => t.status === s).length])),
  users: aiTools.filter((t) => t.status !== "Blocked").reduce((n, t) => n + t.users, 0),
  agents: aiTools.filter((t) => t.kind === "agent").length,
};
export const aiPolicy = policy(aiFile.policy);
export const aiGovernancePolicy = policy(aiFile.governance_policy);

export const riskScale = risksFile.scale;
export const risks = risksFile.risks.map((r) => ({ ...r, ownerName: personName(r.owner), controlRecords: r.controls.map((id) => control(id)).filter(Boolean) }));
export const riskCounts = {
  total: risks.length,
  byRating: Object.fromEntries(["Critical", "High", "Medium", "Low"].map((t) => [t, risks.filter((r) => r.rating === t).length])),
  open: risks.filter((r) => r.status === "Open").length,
  needsOwner: risks.filter((r) => !r.owner).length,
};

// ------------------------------------------------------------------ questionnaires

export const questionnaires = {
  insurer: {
    ...questionnairesFile.insurer,
    answers: questionnairesFile.insurer.answers.map((a) => ({
      ...a,
      question: insurerQuestions[a.question_id],
      summary: requirementSummary("insurer", a.question_id),
      controlRecords: a.controls.map((id) => control(id)).filter(Boolean),
      testRecords: a.tests.map((id) => testResult(id)).filter(Boolean),
      evidenceRecords: a.evidence.map((id) => evidenceItem(id)).filter(Boolean),
    })),
  },
  bank: {
    ...questionnairesFile.bank,
    questions: questionnairesFile.bank.questions.map((q) => ({
      ...q,
      controlRecords: q.controls.map((id) => control(id)).filter(Boolean),
      evidenceRecords: q.evidence.map((id) => evidenceItem(id)).filter(Boolean),
    })),
  },
};
questionnaires.insurer.counts = Object.fromEntries(["Yes", "Partial", "No"].map((s) => [s, questionnaires.insurer.answers.filter((a) => a.answer === s).length]));
questionnaires.bank.drafted = questionnaires.bank.questions.filter((q) => q.answer).length;
questionnaires.bank.open = questionnaires.bank.questions.filter((q) => !q.answer).length;

// ------------------------------------------------------------------ assets and training

export const assets = {
  ...assetsFile,
  devices: assetsFile.devices.map((d) => ({ ...d, assignedName: d.assigned_to ? personName(d.assigned_to) : d.shared_use })),
  apps: vendors.filter((v) => v.discovered_via !== "Manual"),
};
export const deviceCounts = {
  total: assets.devices.length,
  compliant: assets.devices.filter((d) => d.compliant).length,
  encrypted: assets.devices.filter((d) => d.encrypted).length,
  edr: assets.devices.filter((d) => d.edr_active).length,
  macs: assets.devices.filter((d) => d.os.startsWith("macOS")).length,
};

export const courses = trainingFile.courses.map((c) => {
  const assigned = (groups[c.assigned_to] ?? []).map((id) => person(id)).filter(Boolean);
  const rows = assigned.map((p) => ({ person: p, record: p.training[c.id] ?? { status: "due", completed: null, due: null } }));
  const count = (s) => rows.filter((r) => r.record.status === s).length;
  return { ...c, assigned: rows, counts: { assigned: rows.length, completed: count("completed"), due: count("due"), overdue: count("overdue") }, percent: pct(count("completed"), rows.length) };
});

// ------------------------------------------------------------------ people compliance

export const staff = people.filter((p) => p.counted);
export const externals = people.filter((p) => !p.counted);
for (const p of people) {
  const trainingRecords = Object.entries(p.training).map(([courseId, rec]) => ({ course: courses.find((c) => c.id === courseId), ...rec }));
  const pendingPolicies = p.policies_pending === "all" ? policies.filter((pol) => groups[pol.audienceName]?.includes(p.id)) : p.policies_pending.map((id) => policy(id)).filter(Boolean);
  p.checks = [
    { key: "policies", label: "Policies accepted", ok: pendingPolicies.length === 0, detail: pendingPolicies.length ? `${pendingPolicies.length} pending` : "All accepted" },
    { key: "training", label: "Training", ok: trainingRecords.every((t) => t.status === "completed"), detail: trainingRecords.filter((t) => t.status !== "completed").map((t) => `${t.course?.name}: ${t.status}`).join("; ") || "Current" },
    { key: "mfa", label: "MFA", ok: p.mfa_registered, detail: p.mfa_registered ? "Registered" : "Not registered" },
    { key: "device", label: "Device", ok: p.deviceRecord ? p.deviceRecord.compliant : p.external, detail: p.deviceRecord ? (p.deviceRecord.compliant ? `${p.deviceRecord.name} compliant` : p.deviceRecord.issue) : p.external ? "Provider-managed" : "No device" },
    { key: "background", label: "Background check", ok: p.background_check.status !== "pending", detail: p.background_check.status === "completed" ? `Completed ${formatDate(p.background_check.date)}` : p.background_check.status === "pending" ? "Pending" : "Not required" },
  ];
  p.compliant = p.checks.every((c) => c.ok);
  p.pendingPolicies = pendingPolicies;
  p.trainingRecords = trainingRecords;
}
export const peopleCounts = { total: staff.length, compliant: staff.filter((p) => p.compliant).length, onboarding: staff.filter((p) => p.status === "onboarding").length };

// ------------------------------------------------------------------ tasks

function task(kind, title, owner, due, link, source) {
  const days = daysUntil(due);
  return { kind, title, owner, ownerName: personName(owner), due, days, overdue: days !== null && days < 0, href: link, source };
}
export const tasks = [];
for (const e of evidence) {
  if (e.status === "needs_artifact") tasks.push(task("evidence", `Attach evidence: ${e.name}`, e.owner ?? control(e.controls[0])?.owner?.id ?? null, e.due ?? null, href.evidence(e.id), e.controls[0]));
  else if (e.status === "needs_renewal") tasks.push(task("evidence", `Renew evidence: ${e.name}`, e.owner, e.renewal, href.evidence(e.id), e.controls[0]));
  else if (e.status === "upcoming") tasks.push(task("evidence", `Renewal coming up: ${e.name}`, e.owner, e.renewal, href.evidence(e.id), e.controls[0]));
}
for (const t of monitoring.tests) {
  if (t.status === "fail") {
    const plan = t.remediation_plan;
    tasks.push(task("test", `Fix failing test: ${t.title}`, plan?.owner ?? t.controls[0]?.owner?.id ?? null, plan?.due ?? null, href.test(t.check_id), t.controls[0]?.id));
  }
}
for (const p of policies) {
  if (p.status === "renews_soon" || p.status === "past_due") tasks.push(task("policy", `Yearly review: ${p.title}`, p.owner, p.next_review, href.policy(p.id), p.id));
  if (p.status === "needs_approval") tasks.push(task("policy", `Approve ${p.title} v${p.version}`, p.approver, "2026-11-05", href.policy(p.id), p.id));
  if (p.status === "draft") tasks.push(task("policy", `Finish the draft: ${p.title} v${p.version}`, p.owner, "2026-11-30", href.policy(p.id), p.id));
}
for (const v of vendors) {
  if (v.review_status === "Due") tasks.push(task("vendor", `Vendor review overdue: ${v.name}`, v.owner, v.next_review, href.vendor(v.id), v.id));
  if (v.review_status === "In progress") tasks.push(task("vendor", `Finish the review: ${v.name}`, v.owner, v.findings[0]?.date ? "2026-11-15" : null, href.vendor(v.id), v.id));
  if (v.review_status === "Under review") tasks.push(task("vendor", v.owner ? `Decide on ${v.name}` : `Assign an owner and decide on ${v.name}`, v.owner ?? company.roles.AI_Lead ?? company.roles["AI Lead"], "2026-11-14", href.vendor(v.id), v.id));
}
for (const t of aiTools) {
  if (t.status === "Under review") tasks.push(task("ai", `AI review: ${t.name}`, t.owner, "2026-11-14", href.ai(t.id), t.id));
}
for (const r of risks) {
  if (r.status === "Open") tasks.push(task("risk", r.owner ? `Decide the treatment: ${r.title}` : `Assign an owner: ${r.title}`, r.owner, r.next_review, href.risk(r.id), r.id));
}
for (const c of controls) {
  if (c.status === "needs_owner") tasks.push(task("control", `Assign an owner: ${c.name}`, company.roles.CEO, "2026-11-14", href.control(c.id), c.id));
}
for (const p of staff) {
  if (p.pendingPolicies.length) tasks.push(task("person", `Accept ${plural(p.pendingPolicies.length, "policy", "policies")}`, p.id, p.status === "onboarding" ? addDays(p.start_date, 30) : "2026-11-10", href.person(p.id), p.id));
  for (const t of p.trainingRecords) {
    if (t.status !== "completed") tasks.push(task("person", `${t.status === "overdue" ? "Overdue training" : "Training due"}: ${t.course?.name}`, p.id, t.due, href.person(p.id), p.id));
  }
  if (!p.mfa_registered) tasks.push(task("person", "Register for MFA", p.id, addDays(p.start_date, 7), href.person(p.id), p.id));
}
function addDays(dateString, n) {
  return new Date(new Date(`${dateString}T00:00:00Z`).getTime() + n * DAY).toISOString().slice(0, 10);
}
tasks.sort((a, b) => (a.due ?? "9999").localeCompare(b.due ?? "9999"));
export const taskCounts = {
  total: tasks.length,
  overdue: tasks.filter((t) => t.overdue).length,
  next30: tasks.filter((t) => t.days !== null && t.days >= 0 && t.days <= 30).length,
  team: tasks.filter((t) => t.kind !== "person").length,
};
export function tasksFor(personId) {
  return tasks.filter((t) => t.owner === personId);
}

// ------------------------------------------------------------------ owners view

export const owners = (() => {
  const map = new Map();
  const bucket = (id) => {
    if (!map.has(id)) map.set(id, { person: person(id), id, controls: [], policies: [], evidence: [], vendors: [], risks: [], aiTools: [], tasks: [] });
    return map.get(id);
  };
  for (const c of controls) bucket(c.owner?.id ?? null).controls.push(c);
  for (const p of policies) bucket(p.owner).policies.push(p);
  for (const e of evidence) bucket(e.owner).evidence.push(e);
  for (const v of vendors) if (v.review_status !== "Not required" || v.owner) bucket(v.owner).vendors.push(v);
  for (const r of risks) bucket(r.owner).risks.push(r);
  for (const t of aiTools) bucket(t.owner).aiTools.push(t);
  for (const t of tasks) if (t.kind !== "person") bucket(t.owner).tasks.push(t);
  const list = [...map.values()].map((o) => ({ ...o, name: o.person?.name ?? "Unassigned", role: o.person ? Object.entries(company.roles).find(([, pid]) => pid === o.id)?.[0] ?? null : null,
    total: o.controls.length + o.policies.length + o.evidence.length + o.vendors.length + o.risks.length + o.aiTools.length,
    overdue: o.tasks.filter((t) => t.overdue).length }));
  return list.sort((a, b) => (a.person ? 0 : 1) - (b.person ? 0 : 1) || b.total - a.total);
})();

// ------------------------------------------------------------------ home and trust page summaries

export const policyCounts = Object.fromEntries(["published", "renews_soon", "past_due", "needs_approval", "draft"].map((s) => [s, policies.filter((p) => p.status === s).length]));
export const testCounts = (() => {
  const latest = monitoring.tests.filter((t) => t.status === "fail").length;
  const runs = monitoring.runs.map((r) => r.date);
  const failingAt = (date) => monitoring.tests.filter((t) => t.history.find((h) => h.date === date)?.status === "fail").length;
  return { failing: latest, previous: failingAt(runs.at(-2)), first: failingAt(runs[0]), automated: monitoring.tests.filter((t) => t.kind === "automated").length, attestations: monitoring.tests.filter((t) => t.status === "attestation_needed").length };
})();
export const evidenceCounts = Object.fromEntries(["ready", "upcoming", "needs_renewal", "needs_artifact"].map((s) => [s, evidence.filter((e) => e.status === s).length]));

export const trust = {
  frameworks: readiness,
  publishedPolicies: policies.filter((p) => ["published", "renews_soon"].includes(p.status)),
  subprocessors: vendorCounts.subprocessors,
  pack: evidence.filter((e) => ["report", "policy", "record"].includes(e.type) && e.status !== "needs_artifact" && e.controls.some((cid) => control(cid)?.frameworks.includes("insurer"))),
  contact: roleOwner("Security Lead"),
  lastScan: scan.collected_at,
};

// ------------------------------------------------------------------ assistant (preview): answers written from the same data, no model call

export const assistantAnswers = [
  {
    id: "mfa-policies",
    question: "Which policies answer the insurer's MFA question?",
    items: policies.filter((p) => (p.requirements?.insurer ?? []).includes("mfa")).map((p) => ({ text: `${p.title} (v${p.version}, ${status(p.status).label})`, href: href.policy(p.id) })),
    after: `The control behind the question is ${control("CTL-09").name}; its tests ran on ${formatDate(scan.collected_at)}.`,
    sources: ["policies front matter", "config/controls.yaml", "the Oct 30 scan"],
  },
  {
    id: "renewal-evidence",
    question: "What evidence is due before the insurance renewal?",
    items: evidence.filter((e) => e.renewal && daysUntil(e.renewal) <= daysUntil(company.insurance.renewal) || e.status === "needs_artifact").sort((a, b) => (a.renewal ?? "0").localeCompare(b.renewal ?? "0")).map((e) => ({ text: `${e.name}: ${e.renewal ? `renew by ${formatDate(e.renewal)}` : "needs an artifact"} (${e.ownerName})`, href: href.evidence(e.id) })),
    after: `Renewal is ${formatDate(company.insurance.renewal)}; the broker wants the pack by ${formatDate(company.insurance.questionnaire_due)}.`,
    sources: ["demo/data/evidence.json", "company renewal date"],
  },
  {
    id: "ai-policy",
    question: "Who has not accepted the AI Acceptable Use Policy?",
    items: (aiPolicy?.pendingPeople ?? []).map((id) => ({ text: `${personName(id)}, ${person(id)?.title}${person(id)?.status === "onboarding" ? " (started this month)" : ""}`, href: href.person(id) })),
    after: `${aiPolicy?.acknowledged} of ${aiPolicy?.audience} have accepted since it was published on ${formatDate(aiPolicy?.approved)}. A reminder goes out every Monday until they do.`,
    sources: ["demo/data/people.json", "policies.json"],
  },
  {
    id: "ssn-vendors",
    question: "Which vendors hold Social Security numbers, and when were they last reviewed?",
    items: vendors.filter((v) => v.data_shared.some((d) => /Social Security/.test(d))).map((v) => ({ text: `${v.name}: ${v.inherent_risk} tier, ${v.review_status.toLowerCase()}${v.last_review ? `, last review ${formatDate(v.last_review)}` : ""}`, href: href.vendor(v.id) })),
    after: "Every vendor in this list needs a current SOC 2 report or a completed questionnaire and a signed data processing agreement.",
    sources: ["demo/data/vendors.json", "POL-14"],
  },
  {
    id: "change-summary",
    question: "Draft the change summary for the Access Control Policy v2.0",
    items: [
      { text: "Quarterly access reviews now include guest accounts and shared mailboxes, with the COO signing off." },
      { text: "Administrator roles move to dedicated accounts without mailboxes; daily accounts lose standing admin rights." },
      { text: "Access is removed within one business day of a leaver's last day, with the ticket as the record." },
      { text: "Vendor and service accounts get a named owner and a yearly review." },
    ],
    after: "Written from the differences between v1.0 and v2.0. In the platform this is a suggestion you edit and approve, never a silent change.",
    sources: ["policies/03-access-control-policy.md, versions 1.0 and 2.0"],
  },
];
