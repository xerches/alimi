# Alimi

Working name for a security company founded by Alex Dennis (Boston, MA). Renamed from denimi on Nov 1, 2026 because it sounds better and avoids the "denim" search-engine autocorrect. The GitHub repo is `xerches/alimi` (renamed from denimi; the old URL redirects). Pre-LLC: everything here is a prototype until the entity, insurance and first signed SOW exist. This file is the project brief that Claude Code reads at the start of every session. Keep it current; when a decision changes, change it here first.

## What Alimi is

One buyer: the owner or operations lead of a 10 to 200 person company that cannot hire security staff. Referral partners: insurance brokers, CPAs, business and real estate attorneys, and MSPs.

Positioning line (draft): **Security that insurers, customers and auditors accept, for companies too small for a security team.**

**One product: the Alimi platform.** A compliance automation platform of the kind Vanta and Drata sell (continuous control monitoring, evidence collection, policies with sign-off, people, vendors, risks, frameworks, a trust page), sized and priced for the companies those tools quote out of reach. Direction fixed Nov 1, 2026 after the founder's correction: anything a company can do with an AI chat or an IT contractor (a policy pack, a kit) is not a product; the platform is. The phase plan still holds (Claude Docs, Nov 1, 2026: https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a); the packaging below replaces its "three products".

What the platform is made of, and where each piece lives today:

- **Integrations and monitoring.** Read-only connections to Microsoft 365 (Graph) and Google Workspace (Admin SDK). The scanner in `/tools/scanner` is the first integration: the 23 checks in `config/checks.yaml` (12 Microsoft 365, 8 Google Workspace, 3 attestations) run on a schedule, each one a test behind a control. It also runs alone from the operator's laptop, in mock mode or against an owned tenant, which is how the free scan summary and the pilots work before the hosted app exists.
- **Controls and evidence.** `config/controls.yaml`: 40 controls across 10 domains, 13 tested automatically, the rest proven by evidence with an owner and a renewal date. `/tools/report` renders the insurer-ready report (HTML, optional PDF) and grows into the export pack for a broker or auditor.
- **Policies.** The 23-policy library in `/policies`, mapped by criterion ID to SOC 2, ISO 27001, ISO 42001, HIPAA and the insurer questions. The platform tracks versions, approvals and staff acknowledgement. Three core policies, the AI acceptable use policy and the payment fraud procedure are published free on the site as the same documents.
- **People and training**, from the identity provider: policies accepted, training current, MFA, device compliance, onboarding and offboarding checklists.
- **Frameworks.** The cyber insurance questionnaire first, because every company faces it, then SOC 2, ISO 27001, HIPAA and ISO 42001. Requirement IDs and our own one-line summaries only; readiness per framework is computed from the same controls.
- **Vendors and risks, AI governance, trust page and questionnaires, the assistant.** Built in the demo (`/demo`, a sample company on real scanner and policy data) and specified for the platform; they ship in the hosted app in the order customers ask.

**The former kits are modules or free content, not products.** The payment fraud kit (`/kits/payment-fraud`) is free content on the site and the procedure inside the policy module; the AI policy kit (prompts 15 and 16) becomes the AI governance module (policy generator plus the AI app inventory scan). The policy library is not sold on its own. **Services** (`products.services` in `config/pricing.yaml`) are fixed-fee work delivered by the founder that lands the customer in the platform: security assessment and insurer report, insurance-ready in 30 days, policy adoption workshop, payment fraud workshop and yearly drill, AI policy implementation, plus the fractional security lead retainer.

**Published prices**, by the founder's rule (average of comparable vendors minus 5 to 15%, applied at 15%; comparables and arithmetic in `docs/research/platform-pricing.md`): Starter $3,900 a year (up to 25 people, insurer framework, one integration), Growth $7,900 (up to 100 people, adds SOC 2 and ISO 27001, vendors, risks, questionnaires, three integrations), Scale $15,700 (up to 200 people, adds HIPAA and ISO 42001, auditor access, API, unlimited integrations, the multi-tenant view). Paid monthly (Nov 2, 2026): a 12-month term at the list price, or month to month at 15% more; no automatic increase at renewal, price locked for 24 months, and a customer can export every policy, test result and piece of evidence at any time. The CPA audit fee is separate, as everywhere. The policy library, read-only integrations, an owner and tasks per control and a named compliance lead are in every tier.

Two channels. **Direct:** owners who find the site or get a referral. **Resellers:** MSPs, IT consultancies and vCISO firms buy at wholesale (10% off at 1 to 50 active clients, 15% at 51 to 150, 20% at 151 or more, in `config/pricing.yaml`), set their own client price, and get a white-label option on reports, policy packs and the trust page, a not-for-resale licence for their own tenant, and the multi-tenant view. Brokers, CPAs and attorneys who refer but do not resell get a 10% referral fee. Alimi never sells direct to a reseller's client for less than the reseller pays.

How Alimi differs from Vanta and Drata: a published price in the low thousands a year where those platforms quote $12,000 to $25,000 by sales call, insurer-facing outputs before audit-facing ones, plain English for an owner rather than an auditor, and the founder included as a compliance lead who makes the scoping and policy calls those tools leave to the customer.

Prices live in `config/pricing.yaml`; the site, the templates and this file read or quote that file so they never drift.

## Repo layout

```
/site                 static marketing site (Astro) for the one platform offer: Home, Platform, Pricing, Free resources (policies and the fraud procedure rendered from /policies and /kits), For partners, About, Contact; Netlify Forms; deploys free to Netlify
/tools/scanner        Python package alimi_scanner + thin typer CLI: findings schema, checks engine, m365 and gws connectors, mock connector. The platform imports it.
/tools/report         findings JSON -> insurer-ready HTML/PDF report, also importable by the platform
/demo                 platform demo: Astro, sample company "Saltmarsh Payroll", every module, built from the real scanner run and policy library; unlisted, noindex
/platform             hosted web app (phase 3+): FastAPI, HTMX pages, Postgres; orgs, login, scheduled runs, controls, evidence, policies, people, dashboard
/tools/ai-policy      AI governance module (prompts 15-16, not started): policy generator + AI app inventory; a static generator may ship as free content first
/policies             policy library (the platform's policy module): Markdown + YAML front matter mapped to SOC 2, ISO 27001, ISO 42001, HIPAA and insurer IDs; coverage matrix; build to DOCX/PDF
/kits/payment-fraud   payment fraud procedure, scripts, poster, checklist, training script; free content on the site and a policy-module document; build script to PDF
/templates            MSA, SOW, pilot authorization letter, case-study template ({{placeholders}}, attorney-review header)
/docs                 research summaries, decisions log, pilot runbook
/config               pricing.yaml (tiers, services, free, partners), checks.yaml (scanner checks + severity + insurer mapping), controls.yaml (40 controls), brand.yaml
```

## Rules (non-negotiable)

- **Never commit credentials, tokens or tenant IDs.** `.env.example` only. Pre-commit secret scanning stays on.
- **Mock mode is the default.** Every tool and the platform run with `--mock` sample data unless the operator explicitly points them at a tenant.
- **Test tenants only.** Tools run only against tenants Alex owns, or a tenant covered by a signed pilot authorization letter from `/templates`. No exceptions for friends.
- **The hosted platform holds no customer data until the LLC, insurance and a signed pilot letter exist**, and it has had an outside security review. Until then it runs on mock data and Alex's own tenants.
- **Read-only permissions.** Graph and Admin SDK scopes are read-only. Document the exact scopes in each tool's README.
- **Customer tokens are encrypted at rest** with a key kept outside the database (environment or secret manager), and they are never written to logs or error reports.
- **Every platform query is scoped to one organization.** Postgres row-level security on every table that holds customer data, so an app bug cannot leak one company's data to another.
- **Framework text is never copied in.** SOC 2 criteria (AICPA) and ISO 27001 are copyrighted. Store criterion IDs and our own plain-English summaries only.
- **No client data in the repo.** Pilot outputs go to a local, git-ignored `out/` folder.
- **Legal templates carry a header:** "DRAFT. Not legal advice. Review by a Massachusetts attorney before use." Claude drafts structure and plain-language clauses; it does not invent legal text where a lawyer is required.
- **Policies carry a header:** "TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer." A policy maps to requirements by criterion ID only.
- **Honest claims.** Resume metrics ($1M revenue unblocked, premiums cut 15-30%, phishing down 85%) are from employment, not Alimi clients, and the founder dropped them from the site on Nov 1, 2026; do not put them back. Site copy names past employers only ("as Information Security Manager at..."), leaves the current employer unnamed until the outside-work clause is checked, and never implies consulting clients until there are case studies.
- **Free to run.** Site and AI policy app must work on free static hosting with no server. Forms use Netlify Forms or Formspree free tier. The platform needs a server; keep it on free tiers until paying customers cover the bill.
- **Accessible and fast.** Mobile-first, Lighthouse 95+ on every page.

## Build order and status

Order changed Nov 1, 2026: scanner first, then the documents and kits, and from here the hosted platform around the scanner. Later the same day the founder made the platform the only product: the kits became modules and free content, and the site was rebuilt around one offer. On Nov 2, 2026 prompt 12 was split in three (12a, 12b, 12c) and the insurer dashboard and export pack moved ahead of prompt 13, so the first framework is sellable end to end before policies and people arrive; the plan is https://claude.ai/artifact/VjN79aEaY6paZNPDxAwdoS. Dates are targets for evenings and weekends; the CISSP exam on Nov 30 slows November.

| # | Deliverable | Target | Status |
| --- | --- | --- | --- |
| 1 | Repo foundation, config files, CLAUDE.md | Nov 14, 2026 | done Oct 31, 2026 (prompts 1-2) |
| 2 | Scanner core and Microsoft 365 checks (prompt 3) | Dec 5, 2026 | done Nov 1, 2026, PR #2 |
| 3 | Google Workspace checks and insurer-ready report (prompts 4-5) | Jan 9, 2027 | done Nov 1, 2026: prompt 4 PR #3, prompt 5 PR #4 |
| 4 | Payment fraud procedure, scripts, poster, checklist, training script (prompt 6); now free content and a policy-module document | Jan 30, 2027 | done Nov 1, 2026, PR #6 |
| 5 | Policy library mapped to SOC 2, ISO 27001, ISO 42001 (prompt 7); the platform's policy module | Feb 2027 | done Nov 1, 2026, PR #5 |
| 6 | Templates (incl. reseller and referral agreements) and pilot runbook (prompts 8-9), needed before the first pilot | Feb 2027 | done Nov 1, 2026: prompt 8 PR #7, prompt 9 PR #8 |
| 7 | Marketing site (prompt 10), then the one-platform rework with final copy, published tiers and free resources (prompt 11) | Mar 2027 | done Nov 1, 2026, PR #9 (both prompts), merged Nov 2 |
| 7a | Platform demo for prospects (`/demo`): sample company, every module, from the real scanner and policy data | | done Nov 1, 2026, PR #10, merged Nov 2 |
| 8 | Platform foundation (prompt 12a): models, row-level security, mock scans with evidence on every test; the demo is the spec | Mar 2027 | next |
| 8a | Platform: login, nightly worker, reseller view, evidence with renewal dates, recurring tasks, false-positive notes (prompt 12b) | Mar 2027 | not started |
| 8b | Platform: insurer readiness dashboard with two scores, in-app report, export pack, data-quality page (prompt 12c, pulled forward from prompt 14) | Apr 2027 | not started |
| 9 | Platform: policies, people, then SOC 2 and ISO 27001 frameworks (prompts 13-14) | Apr 2027 | not started |
| 10 | AI governance module: AI policy generator and AI app inventory (prompts 15-16), inside the platform | May 2027 | not started |
| 11 | Technical SEO and analytics (prompt 17) | when the site has copy | not started |
| 12 | 15 partner conversations (incl. 5 MSPs on the reseller terms), 3 free pilots, 3 case studies | from Jan 2027, alongside the build | not started |

Gate after #3 (met Nov 1, 2026, in mock mode): the scanner runs end to end before platform code starts. Validation against a real tenant waits for a tenant Alex owns.

Gate to form the LLC: one partner has agreed to refer, one pilot wants the paid service, and the name has passed the Massachusetts entity search, USPTO search and domain check.

Gate for the hosted platform to hold customer data: LLC formed, insurance in place, signed pilot letter, outside security review done.

## Tone and brand

The name is written **Alimi**, with a capital A, in every sentence, title and brand field (decided Nov 2, 2026). Code identifiers, package names, commands, paths and URLs stay lowercase because Python and npm conventions expect it: `alimi_scanner`, `alimi_report`, `alimi-scan`, `alimi-report`, `xerches/alimi`.

Plain English a business owner understands. No fear-mongering, no hooded-hacker imagery, no "cyber" clichés. Explain the term the first time it appears (MFA, EDR, BEC). Brand tokens live in `config/brand.yaml` (palette revised Nov 1, 2026 to "brick and slate": brick primary, blue-gray slate for dark bands, white and cool gray backgrounds, amber accent on dark surfaces only; the founder rejected the earlier beige and teal-green); the site generates its CSS variables from that file and the report reads the same keys, so no component types a color.

## Background

Research behind these choices (Claude Docs, Oct 31, 2026):
- Which path: https://claude.ai/artifact/W82aBf1gnAxyVXQuXXFhZX
- Top 10 market needs and niche gaps: https://claude.ai/artifact/QhBz47ZMzQ54KDHdyQPr8A
- Three areas to build first and 90-day plan: https://claude.ai/artifact/5Xsmabw1PnuLHPtfSamXFE
- Platform plan, scope, stack, phases and risks (Nov 1, 2026): https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a

Founder background: Senior Cybersecurity Specialist at Rhythm Pharmaceuticals; prior Information Security Manager at Exclaimer (SaaS) and Boston IT Services (MSP); SOC 2, ISO 27001/27018, HIPAA, GDPR, ISO 42001; Security+, CySA+; CISSP exam Nov 30, 2026; French, Russian, English.

## Working with Claude Code in this repo

- Ask for a plan before anything larger than a small fix.
- Write tests for the scanner checks; each check has a mock fixture that triggers it and one that passes. Run `pytest tools/scanner` before every commit that touches the scanner.
- Scanner and report code is a library first and a CLI second, so the platform can import it without the command line.
- Explain anything the founder asks about; keeping his Python and API skills sharp is part of the point.
- When a prompt in `PROMPTS.md` is done, update the status table above in the same commit.
