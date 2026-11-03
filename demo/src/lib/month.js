// Home is a month, not a dashboard (the founder's choice, Nov 3, 2026): what the company does this
// month, picked by one visible rule. The rule: items that move the nearest deadline (the insurer's
// evidence pack) come first, then whatever is overdue, then by due date. Everything is derived from
// the same tasks the Owners page shows; nothing is typed in.
import { AS_OF, company, tasks, control, policy, readinessFor, testResult, daysUntil, formatDate, plural } from "./data.js";

const iso = (d) => d.toISOString().slice(0, 10);
const year = AS_OF.getUTCFullYear();
const monthIndex = AS_OF.getUTCMonth();
const start = new Date(Date.UTC(year, monthIndex, 1));
const end = new Date(Date.UTC(year, monthIndex + 1, 0));

export const month = {
  label: AS_OF.toLocaleDateString("en-US", { month: "long", year: "numeric", timeZone: "UTC" }),
  short: AS_OF.toLocaleDateString("en-US", { month: "short", timeZone: "UTC" }),
  start: iso(start),
  end: iso(end),
  daysLeft: daysUntil(iso(end)),
};

// The nearest deadline that matters: the broker's evidence pack, then the renewal itself.
export const deadline = {
  label: "insurer evidence pack",
  date: company.insurance.questionnaire_due,
  days: daysUntil(company.insurance.questionnaire_due),
  renewalDays: daysUntil(company.insurance.renewal),
};

const insurerControls = new Set(readinessFor("insurer").controls.map((c) => c.id));
const GROUP = { test: "fix", evidence: "renew", control: "decide", policy: "decide", vendor: "decide", ai: "decide", risk: "decide" };
export const GROUP_LABEL = { fix: "Fix", renew: "Renew", decide: "Decide" };

function forInsurer(task) {
  if (insurerControls.has(task.source)) return true;
  const p = policy(task.source);
  return p ? (p.requirements?.insurer ?? []).length > 0 : false;
}

function why(task) {
  const c = control(task.source);
  switch (task.kind) {
    case "test": {
      const t = testResult(task.source ? control(task.source)?.tests.find((id) => testResult(id)?.status === "fail") : null);
      return t?.remediation_plan?.action ?? t?.definition?.explain ?? "A failing test keeps its control red until the next scan passes.";
    }
    case "evidence":
      return c ? `Proves ${c.name.charAt(0).toLowerCase()}${c.name.slice(1)}.` : "Evidence past its renewal date does not count.";
    case "control":
      return "Nothing moves on a control nobody owns; the owner gets the tasks and the reminders.";
    case "policy":
      return task.title.startsWith("Approve") ? "Staff cannot be asked to accept a policy nobody has approved." : "A policy past its yearly review stops counting as current.";
    case "vendor":
      return "A vendor that holds client data needs a current review before the next questionnaire asks.";
    case "ai":
      return "An AI tool under review is neither allowed nor blocked, so staff keep using it.";
    case "risk":
      return "An open risk needs a treatment decision or it stays on the register unowned.";
    default:
      return "";
  }
}

const candidates = tasks
  .filter((t) => t.kind !== "person" && (t.overdue || (t.due && t.due <= month.end)))
  .map((t) => ({ ...t, group: GROUP[t.kind] ?? "decide", insurer: forInsurer(t), why: why(t) }));

candidates.sort((a, b) => Number(b.insurer) - Number(a.insurer) || Number(b.overdue) - Number(a.overdue) || (a.due ?? "9999").localeCompare(b.due ?? "9999"));

export const SHOWN = 8;
export const monthItems = candidates.slice(0, SHOWN);
export const monthCounts = {
  total: candidates.length,
  more: Math.max(0, candidates.length - SHOWN),
  insurer: candidates.filter((t) => t.insurer).length,
  overdue: candidates.filter((t) => t.overdue).length,
  byGroup: Object.fromEntries(["fix", "renew", "decide"].map((g) => [g, candidates.filter((t) => t.group === g).length])),
};

export const monthLead = `${plural(monthCounts.total, "thing")} to do in ${month.label.split(" ")[0]}, ${monthCounts.insurer} of them for the ${deadline.label} due ${formatDate(deadline.date)}. Done by ${formatDate(month.end)}, the pack is ready with ${deadline.days - month.daysLeft} days to spare.`;
