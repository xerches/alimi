# alimi

Working name for a security company founded by Alex Dennis (Boston, MA). Renamed from denimi on Nov 1, 2026 because it sounds better and avoids the "denim" search-engine autocorrect. The GitHub repo is `xerches/alimi` (renamed from denimi; the old URL redirects). Pre-LLC: everything here is a prototype until the entity, insurance and first signed SOW exist. This file is the project brief that Claude Code reads at the start of every session. Keep it current; when a decision changes, change it here first.

## What alimi is

One buyer: the owner or operations lead of a 10 to 200 person company that cannot hire security staff. Referral partners: insurance brokers, CPAs, business and real estate attorneys, and MSPs.

Positioning line (draft): **Security that insurers, customers and auditors accept, for companies too small for a security team.**

The long-term product is a compliance automation platform in the style of Vanta and Drata, sized and priced for companies those tools ignore. It is built in stages, and each stage sells on its own. Two kits sit beside it. Full plan (Claude Docs, Nov 1, 2026): https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a

1. **Workspace security scanner, growing into the platform.**
   - *Phases 1 and 2 (the scanner):* read-only CLI for Microsoft 365 (Graph) and Google Workspace (Admin SDK) that runs the checks in `config/checks.yaml` (MFA coverage, legacy auth, admin count, external forwarding, sharing settings, audit logs) and renders an insurer-ready evidence report. Free summary, paid full report. Service: "Insurance-ready in 30 days" (fix findings, run a tabletop, deliver the evidence pack to the broker). Runs from the operator's laptop and stores no customer tokens, so it fits the pre-LLC rules.
   - *Phases 3 and 4 (the platform):* a hosted web app that imports the same scanner package. Organizations and login, connected tenants with scheduled runs, controls proven by automated tests or uploaded evidence, policies from the `/policies` library with staff sign-off, a people list from the identity provider, a readiness dashboard per framework, an export pack for a broker or auditor, and a multi-tenant view for resellers. First framework is the insurer questionnaire, then SOC 2, then ISO 27001.
   - *Later, only when a customer asks:* vendor risk, risk register, questionnaire answer library, trust center, more integrations (AWS, GitHub, Intune, Jamf, HR systems), auditor portal.
2. **Payment fraud protection kit.** Digital kit: payment-change and wire verification procedure, callback scripts, staff poster, 20-minute training video, and a closing-day checklist for home buyers. Service: half-day workshop for finance teams and Massachusetts real estate closing attorneys, plus a yearly drill. Built right after the scanner ships.
3. **AI usage policy and inventory kit.** Web app: ~20 questions produce an AI acceptable use policy, a one-page staff guide and an AI tool inventory. Paid tier adds a read-only scan of Microsoft 365 or Google Workspace audit logs to find AI apps actually in use. Service: fixed-fee implementation (policy adoption, access rules, staff training, ISO 42001 gap check). Later becomes the policy module inside the platform.

Under all three sits the **policy library** in `/policies`: security and company policies (information security, acceptable use, access control, asset management, incident response, vendor risk, AI governance and the rest) written for a 10 to 200 person company and mapped by criterion ID to SOC 2, ISO 27001, ISO 42001, HIPAA where relevant, and the insurer questions. Sold on its own as a policy pack, included in the services, and imported by the platform and the AI policy kit.

Two channels. **Direct:** owners who find the site or get a referral. **Resellers:** MSPs, IT consultancies and vCISO firms buy at wholesale (tiered discount by active client count in `config/pricing.yaml`), set their own client price, and get a white-label option on reports and policy packs, a not-for-resale licence for their own tenant, and the multi-tenant view once the platform exists. Brokers, CPAs and attorneys who refer but do not resell get a referral fee. alimi never sells direct to a reseller's client for less than the reseller pays.

How alimi differs from Vanta and Drata: a published price in the low thousands a year instead of $20K+, insurer-facing outputs before audit-facing ones, plain English for an owner rather than an auditor, and the founder included as a fractional compliance lead who makes the scoping and policy calls those tools leave to the customer.

Suggested starting prices live in `config/pricing.yaml` so the site, proposals and this file never drift.

## Repo layout

```
/site                 static marketing site (Astro or plain HTML/CSS), deploys free to Netlify or Cloudflare Pages
/tools/scanner        Python package alimi_scanner + thin typer CLI: findings schema, checks engine, m365 and gws connectors, mock connector. The platform imports it.
/tools/report         findings JSON -> insurer-ready HTML/PDF report, also importable by the platform
/platform             hosted web app (phase 3+): FastAPI, HTMX pages, Postgres; orgs, login, scheduled runs, controls, evidence, policies, people, dashboard
/tools/ai-policy      static web app, generates policy + one-pager + inventory client-side (no backend)
/policies             policy library: Markdown + YAML front matter mapped to SOC 2, ISO 27001, ISO 42001 criterion IDs; coverage matrix; build to DOCX/PDF
/kits/payment-fraud   Markdown sources for the procedure, scripts, poster, checklist; build script to PDF
/templates            MSA, SOW, pilot authorization letter, case-study template ({{placeholders}}, attorney-review header)
/docs                 research summaries, decisions log, pilot runbook
/config               pricing.yaml, checks.yaml (scanner checks + severity + insurer mapping), brand.yaml
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
- **Honest claims.** Resume metrics ($1M revenue unblocked, premiums cut 15-30%, phishing down 85%) are from employment, not alimi clients. Site copy says "as Information Security Manager at..." and never implies consulting clients until there are case studies.
- **Free to run.** Site and AI policy app must work on free static hosting with no server. Forms use Netlify Forms or Formspree free tier. The platform needs a server; keep it on free tiers until paying customers cover the bill.
- **Accessible and fast.** Mobile-first, Lighthouse 95+ on every page.

## Build order and status

Order changed Nov 1, 2026: scanner first, then the fraud kit, then the platform around the scanner. Dates are targets for evenings and weekends; the CISSP exam on Nov 30 slows November.

| # | Deliverable | Target | Status |
| --- | --- | --- | --- |
| 1 | Repo foundation, config files, CLAUDE.md | Nov 14, 2026 | done Oct 31, 2026 (prompts 1-2) |
| 2 | Scanner core and Microsoft 365 checks (prompt 3) | Dec 5, 2026 | not started |
| 3 | Google Workspace checks and insurer-ready report (prompts 4-5) | Jan 9, 2027 | not started |
| 4 | Payment fraud kit: docs, poster, checklist, video script (prompt 6) | Jan 30, 2027 | not started |
| 5 | Policy library mapped to SOC 2, ISO 27001, ISO 42001 (prompt 7); documents only, can run in parallel with code | Feb 2027 | not started |
| 6 | Templates (incl. reseller and referral agreements) and pilot runbook (prompts 8-9), needed before the first pilot | Feb 2027 | not started |
| 7 | Marketing site and copy, with the For Partners page (prompts 10-11) | Mar 2027 | not started |
| 8 | Platform web app: orgs, login, scheduled runs, controls, evidence, reseller view (prompt 12) | Mar 2027 | not started |
| 9 | Platform: policies, people, dashboard, SOC 2 and ISO 27001 frameworks (prompts 13-14) | Apr 2027 | not started |
| 10 | AI policy generator and AI app inventory (prompts 15-16) | May 2027 | not started |
| 11 | Technical SEO and analytics (prompt 17) | when the site has copy | not started |
| 12 | 15 partner conversations (incl. 5 MSPs on the reseller terms), 3 free pilots, 3 case studies | from Jan 2027, alongside the build | not started |

Gate after #3: the scanner sells on its own (free summary, paid report) before any platform code starts.

Gate to form the LLC: one partner has agreed to refer, one pilot wants the paid service, and the name has passed the Massachusetts entity search, USPTO search and domain check.

Gate for the hosted platform to hold customer data: LLC formed, insurance in place, signed pilot letter, outside security review done.

## Tone and brand

Plain English a business owner understands. No fear-mongering, no hooded-hacker imagery, no "cyber" clichés. Explain the term the first time it appears (MFA, EDR, BEC). Brand tokens live in `config/brand.yaml`; until then, neutral dark-teal and off-white from the earlier Caprius site are fine.

## Background

Research behind these choices (Claude Docs, Oct 31, 2026):
- Which path: https://claude.ai/artifact/W82aBf1gnAxyVXQuXXFhZX
- Top 10 market needs and niche gaps: https://claude.ai/artifact/QhBz47ZMzQ54KDHdyQPr8A
- Three areas to build first and 90-day plan: https://claude.ai/artifact/5Xsmabw1PnuLHPtfSamXFE
- Platform plan, scope, stack, phases and risks (Nov 1, 2026): https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a

Founder background: Senior Cybersecurity Specialist at Rhythm Pharmaceuticals; prior Information Security Manager at Exclaimer (SaaS) and Boston IT Services (MSP); SOC 2, ISO 27001/27018, HIPAA, GDPR, ISO 42001; Security+, CySA+; CISSP exam Nov 30, 2026; French, Russian, English.

## Working with Claude Code in this repo

- Ask for a plan before anything larger than a small fix.
- Write tests for the scanner checks; each check has a mock fixture that triggers it and one that passes.
- Scanner and report code is a library first and a CLI second, so the platform can import it without the command line.
- Explain anything the founder asks about; keeping his Python and API skills sharp is part of the point.
- When a prompt in `PROMPTS.md` is done, update the status table above in the same commit.
