// The platform's modules, in one place: each entry feeds its card on /platform, its item in the Platform menu
// and its own page under /platform/<id> (Nov 5, 2026, after the Drata and Vanta reviews: a short page per module
// with screens from the demo). The screens are captures of the demo's sample company, Saltmarsh Payroll, which
// is fictional; they live in public/screens at 1280 by 800, and every caption says they are a sample. Texts
// that quote a tier, a count or an allowance read config/pricing.yaml and config/frameworks.yaml through
// config.js, so nothing here can drift. No scalable count is typed here (founder's rule, Nov 2, 2026).
import { brand, decided, platform, choosableFrameworks, alwaysIncludedFrameworks, questionnaireAllowances } from "./config.js";

const plat = platform();
const [silver, gold, platinum] = plat.tiers;
const demo = decided(brand.demo_url);
const posture = alwaysIncludedFrameworks()[0];
const frameworkCount = choosableFrameworks().length;
const allowances = questionnaireAllowances();

/** The sample company the screens come from, and the date of its data, for the captions. */
export const SAMPLE = { company: "Saltmarsh Payroll", asOf: "Nov 1, 2026" };

const screen = (file, title, alt, caption) => ({ src: `/screens/${file}.webp`, width: 1280, height: 800, title, alt, caption });

/** "In every tier" or "From Gold, $25 per user a month". */
export function availability(m) {
  const base = m.from.id === silver.id ? "In every tier" : `From ${m.from.name}, ${m.from.perUser} per user a month`;
  return m.preview ? `${base}, in preview` : base;
}

export const MODULES = [
  {
    id: "controls",
    title: "Controls and monitoring",
    from: silver,
    lede: "Every control has one owner, one status and one source of truth, and the status is computed from your tenant and your evidence, never typed in.",
    text: "A control catalog that covers governance, access, email, devices, payments, vendors, resilience and AI. Each control has one owner, one status and one source of truth: tested automatically on every scan of your tenant where an API exposes the setting, proven by evidence with a renewal date where none does. A failing test becomes a task with a plain-English fix and a due date. Nothing is typed as a status; it is computed.",
    points: [
      { title: "Tested on every scan", text: "Where an API exposes the setting, a check runs weekly against your Microsoft 365 or Google Workspace and the control's status follows the result: MFA coverage, legacy sign-in, admin accounts, mail forwarding, sharing links, audit logs." },
      { title: "Proven by evidence where no API can", text: "A control no API can read, such as the yearly policy review or the incident drill, asks for a dated artifact with an owner and a renewal date, and says so on its page." },
      { title: "A failing test becomes a task", text: "The raw evidence, the rule it broke, the plain-English fix and a due date, assigned to the owner, with a reminder on Monday and three days before it is due. A fixed check can be re-run on the spot." },
      { title: "One control, every framework", text: "Each control carries the requirement IDs it answers, so a fix counts for the insurer, the auditor and the customer at the same time." },
    ],
    screens: [
      screen("controls", "The control list", `The Controls screen of the sample company ${SAMPLE.company}: control areas in a column on the left, status tiles and the filtered list on the right, each control with its owner, status, frameworks, evidence and tests`, "The control list, grouped by area, with what needs attention, evidence or an owner."),
      screen("controls-failing", "A control with a failing test", "A control page in the sample company, External automatic forwarding blocked and inbox rules reviewed, with its implementation details, readiness and the test that failed", "A control whose test failed on the last scan: what the scan found, the plain-English fix, and the task it became."),
      screen("monitoring", "Every test, every run", "The Monitoring screen of the sample company: the last run, passing and failing tests, and a table of every automated check with its severity, the insurer question it answers and its history", "Monitoring: every automated check, the insurer question it answers, what the scan found and its history."),
    ],
    demo: "/controls",
    related: ["evidence", "policies"],
  },
  {
    id: "evidence",
    title: "Evidence",
    from: silver,
    lede: "Screenshots, exports and reports, each filed against the control it proves, with an owner, a creation date and a renewal date, so staying compliant looks like a calendar rather than a project.",
    text: "A library of screenshots, exports and reports, each filed against the control it proves, with an owner, a creation date and a renewal date. Four states, computed: ready, upcoming renewal, needs renewal, needs artifact. The export pack for a broker or an auditor is a filter, not a project.",
    points: [
      { title: "Filed against the control", text: "A piece of evidence can prove several controls, and a control can need several artifacts; the link is explicit, so an auditor's question has one answer." },
      { title: "Four states, computed", text: "Ready, upcoming renewal, needs renewal, needs artifact. Scanner reports renew themselves on every run; everything else carries a renewal date and a reminder." },
      { title: "The export pack is a filter", text: "The broker's pack or the auditor's pack is the evidence for one framework, current on the day, in one download, with the control and the requirement ID on every item." },
    ],
    screens: [
      screen("evidence", "The evidence library", `The Evidence screen of the sample company ${SAMPLE.company}: four state tiles, filters by state and type, and a table of evidence with type, status, owner, the controls it proves and its renewal date`, "The evidence library: what is ready, what renews soon, what is past its date and what has been requested but not attached yet."),
    ],
    demo: "/evidence",
    related: ["controls", "trust"],
  },
  {
    id: "policies",
    title: "Policies",
    from: silver,
    lede: "A policy library written for a company without a security team, with a version, an owner, an approver and a record of who has signed, mapped to the frameworks by criterion ID.",
    text: "A policy library written for a company without a security team, from information security and acceptable use to incident response, vendor risk and AI governance. Each policy is mapped by criterion ID to the frameworks, carries a version, an owner and an approver, and tracks who has acknowledged it. Staff sign in the platform; the yearly review is a task like any other.",
    points: [
      { title: "Written for your size", text: "From information security and acceptable use to incident response, vendor risk and AI governance, in plain English, tailored with you in a workshop rather than generated and forgotten." },
      { title: "Versions, approvals and sign-off", text: "Each policy has an owner, an approver, a published version and a review date. Staff read and accept it in the platform; the acknowledgement count is on the page, and a new version asks again." },
      { title: "Mapped by criterion ID", text: "Every policy lists the requirements it answers, by ID, for each framework on the account, so the auditor's policy question is a filter rather than a search." },
    ],
    screens: [
      screen("policies", "The policy library", `The Policies screen of the sample company ${SAMPLE.company}: tiles for published, renewing, past due and awaiting approval, filters by framework, and the library with version, status, owner, acknowledgements and next review`, "The library: every policy with its version, owner, acknowledgements and next review, filtered by framework."),
      screen("policy", "One policy", "A policy page in the sample company, the Information Security Policy, with its details, the acknowledgement bar, the people who have not yet accepted it and the document outline", "One policy: owner, approver, review cycle, who has not yet accepted it, and the document outline. The full text lives behind sign-in."),
    ],
    demo: "/policies",
    related: ["people", "controls"],
  },
  {
    id: "people",
    title: "People and training",
    from: silver,
    lede: "Everyone from your identity provider, one row each, with the checks the insurer asks about, and the security awareness training module behind the training column.",
    text: "Everyone from your identity provider, one row each: policies accepted, training current, MFA registered, device compliant, background check done. Onboarding is a checklist with due dates; offboarding is a check that access actually ended. The security awareness training module, in every tier, gives every user short lessons, each under ten minutes with a quiz: phishing and payment fraud, passwords and MFA, handling customer data, working safely from anywhere, using AI tools at work, and what to do when something looks wrong. Completion is tracked per person on a yearly cycle, so the insurer's training question is answered with dates rather than a promise.",
    points: [
      { title: "One row per person", text: "Policies accepted, training current, MFA registered, device compliant, background check done. A person is compliant when every column is a yes; MFA comes from the tenant scan, not from a form." },
      { title: "Onboarding and offboarding as checklists", text: "A new hire gets tasks with due dates inside the first month; a departure is a check that access actually ended, with the date." },
      { title: "The security awareness training module", text: "Short lessons with a quiz, written for an office rather than an IT team: one for everyone, one for the people who move money, one for AI use. Completion is tracked per person and exported as evidence once a year." },
    ],
    screens: [
      screen("people", "The directory", `The People screen of the sample company ${SAMPLE.company}: tiles for compliant people, MFA registered, onboarding and guests, filters by department, and a table with a column per check`, "The directory: one row per person, one column per check, and the tiles that say who is compliant and who is new."),
      screen("training", "Training, per person", "The Training screen of the sample company: a card per course with its completion bar, who it is assigned to, how often it repeats and who has not completed it yet", "Training: each course with its completion, its cycle and the people still due, exported as evidence once a year."),
    ],
    demo: "/people",
    related: ["policies", "controls"],
  },
  {
    id: "vendors",
    title: "Vendors and risks",
    from: gold,
    lede: "Vendors found from sign-in logs, app consents and accounts payable rather than from memory, scored and reviewed on a schedule, and a risk register in plain sentences linked to the controls that treat each risk.",
    text: "Vendors found from sign-in logs, app consents and accounts payable, not from memory. Each gets an inherent-risk score on four factors (data types, business criticality, integration access, communication scope), a review on a schedule that matches the score, and a place for the contract, the SOC 2 report and the findings. A vendor breach notice becomes a finding with a review behind it. Risks live in a register written in plain sentences, scored, owned and linked to the controls that treat them.",
    points: [
      { title: "Vendors are found, not typed", text: "The tenant's app consents and sign-in logs plus the accounts-payable list, so the vendor that holds your data is on the list before anyone remembers it." },
      { title: "A review that matches the risk", text: "Four factors set the tier, the tier sets how deep and how often the review goes, and the contract, the SOC 2 report and the findings sit on the vendor's page. A breach notice becomes a finding." },
      { title: "A register in plain sentences", text: "Risks come from the yearly workshop, the scanner, vendor reviews and the AI inventory. Each has an owner, a treatment and the controls that treat it, so the register and the control list never disagree." },
    ],
    screens: [
      screen("vendors", "The vendor list", `The Vendors screen of the sample company ${SAMPLE.company}: tiles for vendors, critical and high tiers, reviews to do and alerts, a vendor incident notice, and the vendor table with tier, data shared, owner and next review`, "Vendors: tiers, reviews due, an alert from a vendor's incident notice, and the table with what each one holds."),
      screen("risks", "The risk register", "The Risks screen of the sample company: tiles by rating, filters, and the register with each risk's source, likelihood, impact, rating and treatment", "The risk register: each risk with its source, its rating, its treatment and the controls that treat it."),
    ],
    demo: "/vendors",
    related: ["ai", "controls"],
  },
  {
    id: "ai",
    title: "AI governance",
    from: platinum,
    lede: "An inventory of the AI tools in use, found from sign-in logs and app consents, each with a rule from the AI acceptable use policy, a feed of what changed at each vendor, and the ISO 42001 mapping for companies that need it.",
    text: "An inventory of the AI tools in use, with the model, the risk level, who has access and whether the vendor trains on your data; a feed of what changed at each vendor; the AI acceptable use policy with acknowledgements; and the ISO 42001 mapping for companies that need it.",
    points: [
      { title: "An inventory from the logs", text: "The AI tools people actually use, with the vendor and model, who has access, what data is allowed and whether the vendor trains on it; an agent that acts on its own is marked as one." },
      { title: "A rule per tool", text: "Approved, under review or blocked at sign-in, from the AI acceptable use policy your staff have acknowledged. A decision has an owner and a due date." },
      { title: "Vendor changes before the contract", text: "When a vendor changes its model, its terms or its data use, it lands in the feed with the tools it affects, before it lands in a renewal." },
    ],
    screens: [
      screen("ai", "The AI inventory", `The AI governance screen of the sample company ${SAMPLE.company}: tiles for tools and agents, approved, under review and blocked, people using AI and the ISO 42001 readiness, with the inventory table`, "AI governance: the tools and agents in use, their status, who uses them, and the ISO 42001 readiness beside them."),
    ],
    demo: "/ai",
    related: ["vendors", "policies"],
  },
  {
    id: "trust",
    title: "Trust page and questionnaires",
    from: gold,
    lede: "A public page a prospect, a bank or a broker can read without an account, and security questionnaires drafted from the evidence you already have, every answer pointing at its source.",
    text: `A public page that shows a prospect or a bank which frameworks you follow and which controls are in place, with a request form for the full pack, from the ${gold.name} tier. Security questionnaires are answered from the evidence you already have, with the draft marked for review and every answer pointing at its source: ${allowances}. A questionnaire is one customer's or insurer's form, however long.`,
    points: [
      { title: "What a visitor sees", text: "The frameworks you follow, the controls in place and when they were last checked, in plain English, under your name. Documents marked on request need the visitor's details and your approval; nothing confidential is public." },
      { title: "Answers drafted from evidence", text: "A questionnaire from an insurer, a bank or a customer is drafted from the controls and evidence, with the confidence and the source shown on every line, and a person signs off before anything leaves." },
      { title: "A published allowance", text: `${allowances.charAt(0).toUpperCase()}${allowances.slice(1)}; a questionnaire is one form, however long. The evidence pack for the broker or the auditor is one click behind a request.` },
    ],
    screens: [
      screen("trust", "The public page", `The Trust screen of the sample company ${SAMPLE.company}: the trust page as a visitor sees it, with the company's security statement and the evidence pack and questionnaires buttons`, "The trust page as a visitor sees it, under the company's own name, with the evidence pack one request away."),
      screen("questionnaires", "Questionnaires", "The Questionnaires screen of the sample company: the insurer's questionnaire with its due date, answered and partial counts, and a table of questions with the drafted answer, its confidence and its sources", "Questionnaires: the insurer's form first, each answer with its confidence and the controls and evidence it rests on."),
    ],
    demo: "/trust",
    related: ["evidence", "controls"],
  },
  {
    id: "assistant",
    title: "The assistant",
    from: silver,
    preview: true,
    lede: "Ask in plain words and get the answer from your own program's data, with the source on every line. It suggests; a person accepts.",
    text: "Ask in plain words: which policies answer the insurer's MFA question, what evidence is due before the renewal, who still owes a sign-off. It reads the same tables you see, nothing else, and shows its sources on every line. It suggests; a person accepts. When it finds nothing it says so, and says what it searched. It never changes a record on its own, and your data never leaves the platform to train a model. In preview; the prepared answers are already in the demo.",
    points: [
      { title: "Your tables, nothing else", text: "It reads the controls, evidence, policies, people, vendors and AI tools you see on the other screens, and shows its sources on every line." },
      { title: "A person decides", text: "It drafts and suggests; it never changes a record on its own. When it finds nothing it says so, and says what it searched." },
      { title: "Your data trains nothing", text: "Customer data never leaves the platform to train a model. The assistant is in preview; the prepared answers in the sample company are what it will say." },
    ],
    screens: [
      screen("assistant", "A question and its answer", `The Assistant screen of the sample company ${SAMPLE.company}, marked preview: a question about which policies answer the insurer's MFA question, and the answer listing two policies with their sources`, "A question in plain words, and the answer from the company's own policies and controls, with its sources."),
    ],
    demo: "/assistant",
    related: ["policies", "evidence"],
  },
].map((m) => ({
  ...m,
  href: `/platform/${m.id}`,
  demoHref: demo ? `${demo}${m.demo}` : null,
}));

/** The frameworks section of the platform page: a card like the modules', but its page is the catalog. */
export const FRAMEWORKS_SECTION = {
  id: "frameworks",
  title: "Frameworks",
  href: "/frameworks",
  text: `${frameworkCount} frameworks in the catalog, one included in every plan and the rest as add-ons, all answered by one set of controls. The cyber insurance questionnaire comes first because it is the one every company faces this year; SOC 2, ISO 27001, HIPAA, PCI DSS, GDPR and the others are answered by the same controls and policies when a customer or a regulator asks. Readiness is the share of mapped controls in order, per framework. Alongside them, in every plan, the ${posture.name} scores the controls security teams recommend beyond what any standard asks, because compliance is not security.`,
  link: { href: "/frameworks", label: "The catalog, by who asks for each" },
};

/** The platform page's sections, in reading order: the modules with the frameworks between people and vendors. */
export const PLATFORM_SECTIONS = [...MODULES.slice(0, 4), FRAMEWORKS_SECTION, ...MODULES.slice(4)];

export function module(id) {
  const found = MODULES.find((m) => m.id === id);
  if (!found) throw new Error(`modules.js has no module "${id}"`);
  return found;
}
