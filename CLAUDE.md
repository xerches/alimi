# Alimi

Working name for a security company founded by Alex Dennis (Boston, MA). Renamed from denimi on Nov 1, 2026 because it sounds better and avoids the "denim" search-engine autocorrect. The GitHub repo is `xerches/alimi` (renamed from denimi; the old URL redirects). Pre-LLC: everything here is a prototype until the entity, insurance and first signed SOW exist. This file is the project brief that Claude Code reads at the start of every session. Keep it current; when a decision changes, change it here first.

## What Alimi is

One buyer: the owner or operations lead of a company of 10 people and up that cannot hire security staff. There is no upper limit on company size (founder, Nov 3, 2026): the minimum is 10 employees and the highest tier is offered to companies of 500 and more. Referral partners: insurance brokers, CPAs, business and real estate attorneys, and MSPs.

Positioning line (draft): **Security that insurers, customers and auditors accept, for companies too small for a security team.**

**One product: the Alimi platform.** A compliance automation platform of the kind Vanta and Drata sell (continuous control monitoring, evidence collection, policies with sign-off, people, vendors, risks, frameworks, a trust page), sized and priced for the companies those tools quote out of reach. Direction fixed Nov 1, 2026 after the founder's correction: anything a company can do with an AI chat or an IT contractor (a policy pack, a kit) is not a product; the platform is. The phase plan still holds (Claude Docs, Nov 1, 2026: https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a); the packaging below replaces its "three products".

What the platform is made of, and where each piece lives today:

- **Integrations and monitoring.** Read-only connections to Microsoft 365 (Graph) and Google Workspace (Admin SDK). The scanner in `/tools/scanner` is the first integration: the 23 checks in `config/checks.yaml` (12 Microsoft 365, 8 Google Workspace, 3 attestations) run on a schedule, each one a test behind a control. It also runs alone from the operator's laptop, in mock mode or against an owned tenant, which is how the security assessment and the pilots work before the hosted app exists.
- **Controls and evidence.** `config/controls.yaml`: 40 controls across 10 domains, 13 tested automatically, the rest proven by evidence with an owner and a renewal date. `/tools/report` renders the insurer-ready report (HTML, optional PDF) and grows into the export pack for a broker or auditor.
- **Policies.** The 23-policy library in `/policies`, mapped by criterion ID to SOC 2, ISO 27001, ISO 42001, HIPAA and the insurer questions. The platform tracks versions, approvals and staff acknowledgement. No policy text is published anywhere (decided Nov 2, 2026): the site shows titles and counts, the demo shows an outline and an opening paragraph, and the documents themselves sit behind the subscription.
- **People and training**, from the identity provider: policies accepted, training current, MFA, device compliance, onboarding and offboarding checklists. The security awareness training module (prompt 18, lesson plan in `docs/training-modules.md`): eight short lessons with a quiz each, completion dates per person and a yearly cycle, in every tier; scripts, slides and quizzes are written here, recordings are made later from them.
- **Frameworks.** The catalog in `config/frameworks.yaml` (Nov 2, 2026): 23 entries. First the **Alimi Recommended Security Posture Score** (name fixed by the founder Nov 2, 2026), our own and not accredited, in every plan and outside the framework count: the controls security teams recommend beyond what any compliance framework asks, scored the way Microsoft Secure Score scores a tenant, because compliance is not security. Then 22 frameworks: the cyber insurance questionnaire first, because every company faces it, SOC 2, ISO 27001, HIPAA and ISO 42001 (mapped to the policy library today), and PCI DSS, GDPR, CCPA, NIST CSF, NIST 800-53 and 800-171, CMMC, CIS Controls, Cyber Essentials, NIS2, the FTC Safeguards Rule, 201 CMR 17.00, NYDFS 500, SOX ITGC, the EU AI Act and the NIST AI RMF (mapped before launch, in the order customers ask). Requirement IDs and our own one-line summaries only; readiness per framework is computed from the same controls.
- **Vendors and risks, AI governance, trust page and questionnaires, the assistant.** Built in the demo (`/demo`, a sample company on real scanner and policy data) and specified for the platform; they ship in the hosted app in the order customers ask.

**The former kits are modules, not products, and nothing is given away** (Nov 2, 2026: the founder ended free resources). The payment fraud kit (`/kits/payment-fraud`) is the payment verification procedure inside the policy module and the finance lesson in the training module; the AI policy kit (prompts 15 and 16) becomes the AI governance module (policy generator plus the AI app inventory scan), behind sign-in. The policy library is not sold on its own and is not published. **Services** (`products.services` in `config/pricing.yaml`) are fixed-fee work delivered by the founder that lands the customer in the platform: security assessment and insurer report, insurance-ready in 30 days, policy adoption workshop, payment fraud workshop and yearly drill, AI policy implementation, plus the fractional security lead retainer.

**Published prices**, per user a month since Nov 2, 2026, by the founder's rule (average of comparable vendors minus 5 to 15%, applied at 15%; comparables and arithmetic in `docs/research/platform-pricing.md`), minimum 10 users: Silver $13 (one framework, one integration, controls with tests, evidence, policies, training, people, quarterly call), Gold $25 (adds the public trust page, vendors, risk register, 24 questionnaires a year, auditor and broker access with the export pack, three integrations, monthly call), Platinum $38 (adds unlimited integrations and API, access reviews, AI governance, custom controls and frameworks, SSO, priority support, 100 questionnaires a year), Diamond $50 (adds the audit run by Alimi, a dedicated compliance lead, a quarterly board report, multi-entity, unlimited questionnaires). The trust page moved from Silver to Gold and the questionnaire allowances were published on Nov 2, 2026 after the vanta.com and drata.com scan (`docs/research/vanta-drata-site-scan.md`). One framework of the customer's choice is included in every tier, chosen today from the five that are mapped (the pricing page names them and marks the rest "before launch"); each further framework is $4 per user a month, 5% off every add-on with five or more frameworks on the account, 10% off with ten or more, and ten is the cap for now; the Posture Score is in every plan and never counted. Paid monthly: a 12-month term at the list price, or month to month at 15% more; no automatic increase at renewal, price locked for 24 months. The CPA audit fee is separate, as everywhere. The policy library, the training lessons, read-only integrations, an owner and tasks per control and a named compliance lead are in every tier. The exit promise ("export everything at any time") was removed from every page on Nov 2, 2026 at the founder's request; return of the client's data at termination is an attorney-review item in the MSA outline, not a marketing line.

Two channels. **Direct:** owners who find the site or get a referral. **Resellers:** MSPs, IT consultancies and vCISO firms buy at wholesale (Partner tier, 10% off at 1 to 50 active clients; Preferred, 15% at 51 to 150; Premier, 20% at 151 or more, in `config/pricing.yaml`), set their own client price, and get a white-label option on reports, policy packs and the trust page, a not-for-resale licence and a demo tenant, the multi-tenant view, partner training, and four incentives (a launch tier at the Preferred discount for six months, deal registration with 90-day protection and 5 extra points on the first year, the tier discount on add-on frameworks, and service fees kept by a reseller that delivers them) that stay proposals until the first partner conversation. The short version is on For partners, the full one on For resellers. Brokers, CPAs and attorneys who refer but do not resell get a 10% referral fee. Alimi never sells direct to a reseller's client for less than the reseller pays.

How Alimi differs from Vanta and Drata: a published per-user price (a 25-person company pays $3,900 a year on Silver) where those platforms quote $12,000 to $25,000 by sales call, insurer-facing outputs before audit-facing ones, plain English for an owner rather than an auditor, the founder included as a compliance lead who makes the scoping and policy calls those tools leave to the customer, and a Compare page that takes what their own customers complain about in sub-four-star reviews (renewal jumps, add-on fees, noisy tests, the agent, support after the sale) and says what Alimi does about each, every statement sourced (`docs/research/vanta-drata-complaints.md`, `docs/research/vanta-drata-site-scan.md`).

Prices live in `config/pricing.yaml` and the framework catalog in `config/frameworks.yaml`; the site, the demo, the templates and this file read or quote those files so they never drift.

## Repo layout

```
/site                 static marketing site (Astro) for the one platform offer: Home, Platform, Integrations, Frameworks (+ a page per framework), Security, Solutions, Pricing (per-user calculator), Compare (Vanta and Drata, sourced), For partners, For resellers, Resources (library, glossary, help, academy, community, customer stories), About, Press, Careers, Trust, Status, Legal, Privacy, Contact; menus from site/src/lib/nav.js; no policy text, no free downloads, no scalable counts on any page (the framework count is the one number allowed); Netlify Forms; deploys free to Netlify
/tools/scanner        Python package alimi_scanner + thin typer CLI: findings schema, checks engine, m365 and gws connectors, mock connector. The platform imports it.
/tools/report         findings JSON -> insurer-ready HTML/PDF report, also importable by the platform
/demo                 platform demo: Astro, sample company "Saltmarsh Payroll", every module, built from the real scanner run and policy library; noindex, linked from the site as "See the product" since Nov 2, 2026
/platform             hosted web app: FastAPI, HTMX pages, Postgres with row-level security, mock mode (`docker compose up`); built: the 12a foundation, the demo's app shell, account pages and the dark theme, tasks and projects, the policy module, the trust center (in review Nov 3, 2026); real login, the worker, people and the dashboards follow in 12b-14
/tools/ai-policy      AI governance module (prompts 15-16, not started): policy generator + AI app inventory, inside the platform behind sign-in; nothing ships free
/policies             policy library (the platform's policy module): Markdown + YAML front matter mapped to SOC 2, ISO 27001, ISO 42001, HIPAA and insurer IDs; coverage matrix; build to DOCX/PDF
/kits/payment-fraud   payment fraud procedure, scripts, poster, training script; a policy-module document and the finance lesson of the training module, not public; build script to PDF
/templates            MSA, SOW, pilot authorization letter, case-study template ({{placeholders}}, attorney-review header)
/docs                 research summaries, decisions log, pilot runbook
/config               pricing.yaml (per-user tiers, framework add-on, services, partners), frameworks.yaml (49-entry catalog in six categories, led by the Posture Score; every framework Vanta and Drata list), checks.yaml (scanner checks + severity + insurer mapping), controls.yaml (40 controls), brand.yaml
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
- **No policy or lesson text in public.** The site shows policy titles and counts only, the demo shows an outline and an opening paragraph, the training lessons sit behind sign-in, and no page offers a free download (founder, Nov 2, 2026: a reader could otherwise copy the library and skip the product). The repository is private (founder's decision, Nov 2, 2026; the switch is in GitHub settings and only the founder can flip it), so `/policies` is not readable without access, and the site no longer links to GitHub.
- **Honest claims.** Resume metrics ($1M revenue unblocked, premiums cut 15-30%, phishing down 85%) are from employment, not Alimi clients, and the founder dropped them from the site on Nov 1, 2026; do not put them back. Site copy names past employers only ("as Information Security Manager at..."), leaves the current employer unnamed until the outside-work clause is checked, and never implies consulting clients until there are case studies.
- **Free to run.** Site and AI policy app must work on free static hosting with no server. Forms use Netlify Forms or Formspree free tier. The platform needs a server; keep it on free tiers until paying customers cover the bill.
- **Accessible and fast.** Mobile-first, Lighthouse 95+ on every page.

## Build order and status

Order changed Nov 1, 2026: scanner first, then the documents and kits, and from here the hosted platform around the scanner. Later the same day the founder made the platform the only product: the kits became modules and free content, and the site was rebuilt around one offer. On Nov 2, 2026 prompt 12 was split in three (12a, 12b, 12c) and the insurer dashboard and export pack moved ahead of prompt 13, so the first framework is sellable end to end before policies and people arrive; the plan is https://claude.ai/artifact/VjN79aEaY6paZNPDxAwdoS. The same evening a review round changed the packaging without changing the order: per-user tiers (Silver, Gold, Platinum, Diamond), the framework catalog with the Alimi Security Posture Score, no free resources and no public policy text, the Compare and For resellers pages, the indigo palette, and the training module as prompt 18 after prompt 13. On Nov 3, 2026 the founder chose to build the product out completely before coming back to the demo, with sign-in as the only way in; the demo in `/demo` is frozen as the spec, its shell carried into the platform, and what the demo becomes is decided when the product is done. Dates are targets for evenings and weekends; the CISSP exam on Nov 30 slows November.

| # | Deliverable | Target | Status |
| --- | --- | --- | --- |
| 1 | Repo foundation, config files, CLAUDE.md | Nov 14, 2026 | done Oct 31, 2026 (prompts 1-2) |
| 2 | Scanner core and Microsoft 365 checks (prompt 3) | Dec 5, 2026 | done Nov 1, 2026, PR #2 |
| 3 | Google Workspace checks and insurer-ready report (prompts 4-5) | Jan 9, 2027 | done Nov 1, 2026: prompt 4 PR #3, prompt 5 PR #4 |
| 4 | Payment fraud procedure, scripts, poster, training script (prompt 6); now free content and a policy-module document; the home-buyer closing checklist was removed Nov 2, 2026 | Jan 30, 2027 | done Nov 1, 2026, PR #6 |
| 5 | Policy library mapped to SOC 2, ISO 27001, ISO 42001 (prompt 7); the platform's policy module | Feb 2027 | done Nov 1, 2026, PR #5 |
| 6 | Templates (incl. reseller and referral agreements) and pilot runbook (prompts 8-9), needed before the first pilot | Feb 2027 | done Nov 1, 2026: prompt 8 PR #7, prompt 9 PR #8 |
| 7 | Marketing site (prompt 10), then the one-platform rework with final copy and published tiers (prompt 11); its free resources were removed Nov 2, 2026 | Mar 2027 | done Nov 1, 2026, PR #9 (both prompts), merged Nov 2 |
| 7a | Platform demo for prospects (`/demo`): sample company, every module, from the real scanner and policy data | | done Nov 1, 2026, PR #10, merged Nov 2 |
| 7b | Review round: per-user tiers, framework catalog and Posture Score, indigo palette, Compare and For resellers pages, no free resources or policy text, reseller incentives, training lesson plan | | done Nov 2, 2026, PR #14 |
| 7c | Site-scan actions: score renamed to the Alimi Recommended Security Posture Score, trust page to Gold, questionnaire allowances, included frameworks named, demo linked, Compare widened to 11 complaints, Who it is for, agenda file, dogfooding plan | | done Nov 2, 2026, PR #15 |
| 8 | Platform foundation (prompt 12a): models, row-level security, mock scans with evidence on every test; the demo is the spec | Mar 2027 | done Nov 2, 2026 in mock mode (`docker compose up` in `/platform`), PR #16 |
| 8a | Platform: login, nightly worker, reseller view, evidence with renewal dates, recurring tasks, false-positive notes (prompt 12b) | Mar 2027 | tasks and projects delivered in the Nov 3 round (8c); the rest next |
| 8b | Platform: insurer readiness dashboard with two scores (audit readiness and the Alimi Recommended Security Posture Score), in-app report, export pack, data-quality page (prompt 12c, pulled forward from prompt 14) | Apr 2027 | not started |
| 8c | Platform, Nov 3 round: the demo's app shell (PR #20), account menu, profile pages and the light/dark theme (#22), tasks and projects with a Jira or Monday.com reference (#23), the policy module with the full text behind sign-in (#25), the trust center with its public page and admin side (#26) | | in review Nov 3, 2026, stacked on #16 (merged) |
| 9 | Platform: policies and people (prompt 13), then the framework catalog: SOC 2 and ISO 27001 first, the rest of `config/frameworks.yaml` as customers ask (prompt 14) | Apr 2027 | policy module in review Nov 3, 2026, PR #25; people and the framework catalog not started |
| 9a | Security awareness training module: eight lessons with quizzes and completion tracking (prompt 18; plan in `docs/training-modules.md`) | May 2027 | not started |
| 10 | AI governance module: AI policy generator and AI app inventory (prompts 15-16), inside the platform | May 2027 | not started |
| 11 | Technical SEO and analytics (prompt 17) | when the site has copy | not started |
| 12 | 15 partner conversations (incl. 5 MSPs on the reseller terms), 3 free pilots, 3 case studies | from Jan 2027, alongside the build | not started |

Gate after #3 (met Nov 1, 2026, in mock mode): the scanner runs end to end before platform code starts. Validation against a real tenant waits for a tenant Alex owns.

Gate to form the LLC: one partner has agreed to refer, one pilot wants the paid service, and the name has passed the Massachusetts entity search, USPTO search and domain check.

Gate for the hosted platform to hold customer data: LLC formed, insurance in place, signed pilot letter, outside security review done.

After the LLC (decided Nov 2, 2026 from the site scan): Alimi runs its own security programme in its own platform on the founder's tenant, publishes its own trust page, and pursues a SOC 2 Type I report when revenue covers the audit fee. Open items with dates, including the Nov 17, 2026 Vanta Trusted Network webinar and the training-module review, live in `docs/agenda.md`.

## Tone and brand

The name is written **Alimi**, with a capital A, in every sentence, title and brand field (decided Nov 2, 2026). Code identifiers, package names, commands, paths and URLs stay lowercase because Python and npm conventions expect it: `alimi_scanner`, `alimi_report`, `alimi-scan`, `alimi-report`, `xerches/alimi`.

Plain English a business owner understands. No fear-mongering, no hooded-hacker imagery, no "cyber" clichés. Explain the term the first time it appears (MFA, EDR, BEC). Brand tokens live in `config/brand.yaml` (palette revised Nov 2, 2026 to "indigo and ink": deep indigo primary, indigo-ink header, footer and dark bands, white and faintly lavender gray backgrounds, periwinkle links on dark surfaces, amber accent on dark surfaces only; the founder asked for blue or purple that stands out lightly, after rejecting beige and teal-green on Oct 31 and settling for brick on Nov 1); the site generates its CSS variables from that file and the report reads the same keys, so no component types a color.

## Background

Research behind these choices (Claude Docs, Oct 31, 2026):
- Which path: https://claude.ai/artifact/W82aBf1gnAxyVXQuXXFhZX
- Top 10 market needs and niche gaps: https://claude.ai/artifact/QhBz47ZMzQ54KDHdyQPr8A
- Three areas to build first and 90-day plan: https://claude.ai/artifact/5Xsmabw1PnuLHPtfSamXFE
- Platform plan, scope, stack, phases and risks (Nov 1, 2026): https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a
- Next three build steps, with the Nov 2, 2026 findings from vanta.com and drata.com: https://claude.ai/artifact/VjN79aEaY6paZNPDxAwdoS
- In the repo (Nov 2, 2026): `docs/research/platform-pricing.md` (per-user arithmetic), `docs/research/vanta-drata-complaints.md` (sub-four-star reviews), `docs/research/vanta-drata-site-scan.md` (how they sell), `docs/training-modules.md` (lesson plan)

Founder background: Senior Cybersecurity Specialist at Rhythm Pharmaceuticals; prior Information Security Manager at Exclaimer (SaaS) and Boston IT Services (MSP); SOC 2, ISO 27001/27018, HIPAA, GDPR, ISO 42001; Security+, CySA+; CISSP exam Nov 30, 2026; French, Russian, English.

## Working with Claude Code in this repo

- Ask for a plan before anything larger than a small fix.
- Write tests for the scanner checks; each check has a mock fixture that triggers it and one that passes. Run `pytest tools/scanner` before every commit that touches the scanner.
- Scanner and report code is a library first and a CLI second, so the platform can import it without the command line.
- Explain anything the founder asks about; keeping his Python and API skills sharp is part of the point.
- When a prompt in `PROMPTS.md` is done, update the status table above in the same commit.
- Open items for the founder, with dates, go in `docs/agenda.md`; decisions taken go in `docs/decisions.md`.
