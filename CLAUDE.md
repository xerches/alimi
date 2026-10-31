# denimi

Working name for a security company founded by Alex Dennis (Boston, MA). Pre-LLC: everything here is a prototype until the entity, insurance and first signed SOW exist. This file is the project brief that Claude Code reads at the start of every session. Keep it current; when a decision changes, change it here first.

## What denimi is

One buyer: the owner or operations lead of a 10 to 200 person company that cannot hire security staff. Referral partners: insurance brokers, CPAs, business and real estate attorneys, and MSPs.

Positioning line (draft): **Security that insurers, customers and auditors accept, for companies too small for a security team.**

Three products, each with a free or cheap product tier that generates leads and a paid service tier that generates income:

1. **AI usage policy and inventory kit.** Web app: ~20 questions produce an AI acceptable use policy, a one-page staff guide and an AI tool inventory. Paid tier adds a read-only scan of Microsoft 365 or Google Workspace audit logs to find AI apps actually in use. Service: fixed-fee implementation (policy adoption, access rules, staff training, ISO 42001 gap check).
2. **Workspace security scanner.** Read-only CLI for Microsoft 365 (Graph) and Google Workspace (Admin SDK) that scores MFA coverage, legacy auth, admin count, external forwarding, sharing settings and backups, then renders an insurer-ready evidence report. Free summary, paid full report. Service: "Insurance-ready in 30 days" (fix findings, run a tabletop, deliver the evidence pack to the broker).
3. **Payment fraud protection kit.** Digital kit: payment-change and wire verification procedure, callback scripts, staff poster, 20-minute training video, and a closing-day checklist for home buyers. Service: half-day workshop for finance teams and Massachusetts real estate closing attorneys, plus a yearly drill.

Suggested starting prices live in `config/pricing.yaml` so the site, proposals and this file never drift.

## Repo layout

```
/site                 static marketing site (Astro or plain HTML/CSS), deploys free to Netlify or Cloudflare Pages
/tools/scanner        Python CLI: m365 and gws modules, shared findings schema, --mock mode
/tools/report         findings JSON -> insurer-ready HTML/PDF report
/tools/ai-policy      static web app, generates policy + one-pager + inventory client-side (no backend)
/kits/payment-fraud   Markdown sources for the procedure, scripts, poster, checklist; build script to PDF
/templates            MSA, SOW, pilot authorization letter, case-study template ({{placeholders}}, attorney-review header)
/docs                 research summaries, decisions log, pilot runbook
/config               pricing.yaml, checks.yaml (scanner checks + severity + insurer mapping), brand.yaml
```

## Rules (non-negotiable)

- **Never commit credentials, tokens or tenant IDs.** `.env.example` only. Pre-commit secret scanning stays on.
- **Mock mode is the default.** Every tool runs with `--mock` sample data unless the operator explicitly points it at a tenant.
- **Test tenants only.** Tools run only against tenants Alex owns, or a tenant covered by a signed pilot authorization letter from `/templates`. No exceptions for friends.
- **Read-only permissions.** Graph and Admin SDK scopes are read-only. Document the exact scopes in each tool's README.
- **No client data in the repo.** Pilot outputs go to a local, git-ignored `out/` folder.
- **Legal templates carry a header:** "DRAFT. Not legal advice. Review by a Massachusetts attorney before use." Claude drafts structure and plain-language clauses; it does not invent legal text where a lawyer is required.
- **Honest claims.** Resume metrics ($1M revenue unblocked, premiums cut 15-30%, phishing down 85%) are from employment, not denimi clients. Site copy says "as Information Security Manager at..." and never implies consulting clients until there are case studies.
- **Free to run.** Site and AI policy app must work on free static hosting with no server. Forms use Netlify Forms or Formspree free tier.
- **Accessible and fast.** Mobile-first, Lighthouse 95+ on every page.

## Build order and status

| # | Deliverable | Target | Status |
| --- | --- | --- | --- |
| 1 | Repo foundation, config files, CLAUDE.md | Nov 14, 2026 | done Oct 31, 2026 (prompts 1-2) |
| 2 | Payment fraud kit (docs, poster, checklist, video script) + landing page | Nov 28, 2026 | not started |
| 3 | Scanner: M365 module, then Google, then report | Dec 2026 | not started |
| 4 | AI policy generator + AI app inventory | early Jan 2027 | not started |
| 5 | Templates: MSA, SOW, pilot authorization, case study | Jan 2027 | not started |
| 6 | 15 partner conversations, 3 free pilots, 3 case studies | late Jan 2027 | not started |

Gate to form the LLC: one partner has agreed to refer, one pilot wants the paid service, and the name has passed the Massachusetts entity search, USPTO search and domain check.

## Tone and brand

Plain English a business owner understands. No fear-mongering, no hooded-hacker imagery, no "cyber" clichés. Explain the term the first time it appears (MFA, EDR, BEC). Brand tokens live in `config/brand.yaml`; until then, neutral dark-teal and off-white from the earlier Caprius site are fine.

## Background

Research behind these choices (Claude Docs, Oct 31, 2026):
- Which path: https://claude.ai/artifact/W82aBf1gnAxyVXQuXXFhZX
- Top 10 market needs and niche gaps: https://claude.ai/artifact/QhBz47ZMzQ54KDHdyQPr8A
- Three areas to build first and 90-day plan: https://claude.ai/artifact/5Xsmabw1PnuLHPtfSamXFE

Founder background: Senior Cybersecurity Specialist at Rhythm Pharmaceuticals; prior Information Security Manager at Exclaimer (SaaS) and Boston IT Services (MSP); SOC 2, ISO 27001/27018, HIPAA, GDPR, ISO 42001; Security+, CySA+; CISSP exam Nov 30, 2026; French, Russian, English.

## Working with Claude Code in this repo

- Ask for a plan before anything larger than a small fix.
- Write tests for the scanner checks; each check has a mock fixture that triggers it and one that passes.
- Explain anything the founder asks about; keeping his Python and API skills sharp is part of the point.
- When a prompt in `PROMPTS.md` is done, update the status table above in the same commit.
