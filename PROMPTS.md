# denimi build prompts for Claude Code

Run one prompt per session, in order. Review what it builds, commit, then move on. For anything bigger than a small change, the prompt already asks for a plan first; read the plan before saying go.

## Phase 1: Foundation (weeks 1-2)

**1. Repo foundation** (done Oct 31, 2026)
```
Read CLAUDE.md. Create the repo layout it describes: /site, /tools/scanner, /tools/report,
/tools/ai-policy, /kits/payment-fraud, /templates, /docs, /config. Set up git, a .gitignore
that excludes .env, out/ and any *.json under out/, a .env.example, and pre-commit hooks with
gitleaks for secret scanning. Add a root README that explains each folder in two lines.
Do not write product code yet. Show me the plan first.
```

**2. Config files** (done Oct 31, 2026)
```
Read CLAUDE.md. Create /config/pricing.yaml with the three products, each with product tiers
(free, paid) and service tiers, using these starting prices: AI policy kit free to $99,
implementation $2,500-$5,000; scanner summary free, full report $500-$1,500, 30-day service
$4,000-$8,000; payment fraud kit $149-$299, workshop $1,500-$3,000. Create /config/brand.yaml
with name "denimi", a placeholder tagline, and color tokens (dark teal, off-white, one accent).
Create /config/checks.yaml listing the scanner checks for Microsoft 365 and Google Workspace
with an id, title, severity, plain-English explanation, remediation, and which cyber insurance
question it maps to (MFA, EDR, backups, email security, admin access). Leave EDR and backups as
"attestation" checks since they can't be read from the tenant.
```

## Phase 2: Payment fraud kit and site (weeks 3-4)

**3. Payment fraud kit, documents**
```
Read CLAUDE.md. In /kits/payment-fraud, write Markdown sources for: (a) a payment-change and
wire verification procedure for a company of 10-200 people, with a verified-callback rule using
a phone number on file, a two-person rule above a threshold, and a 24-hour hold on new or changed
bank details; (b) callback scripts for finance staff; (c) a one-page staff poster; (d) a
closing-day checklist for home buyers and sellers in a Massachusetts attorney-led closing;
(e) a 20-minute training video script with slide notes. Use {{Company}} placeholders. Add a
build script that renders each to PDF with pandoc or weasyprint. Plain English, no jargon
without a definition.
```

**4. Marketing site**
```
Read CLAUDE.md and /config. In /site, build a fast static site with Astro. Pages: Home, the
three product pages (AI Policy Kit, Workspace Security Scan, Payment Fraud Kit), For Partners
(brokers, CPAs, attorneys, MSPs), About, Contact. Each product page has a waitlist form using
Netlify Forms, a "how it works" section, and a pricing block read from /config/pricing.yaml at
build time. Pull brand tokens from /config/brand.yaml. Mobile-first, accessible, Lighthouse 95+.
Placeholder copy marked TODO. Add a netlify.toml so it deploys with no settings. Show me the
plan first.
```

**5. Site copy**
```
Read CLAUDE.md, /docs/research (I'll paste the three research summaries there first), and the
site. Replace every TODO with final copy. Homepage headline leads with the outcome for a
business owner, not the technology. Each product page states the complaint, what they get,
what it costs, and what happens next. Resume metrics are attributed to employment per the
Rules in CLAUDE.md. Write the About page in first person, 150 words.
```

## Phase 3: Workspace security scanner (weeks 5-8)

**6. Scanner core and Microsoft 365 module**
```
Read CLAUDE.md and /config/checks.yaml. In /tools/scanner, build a Python CLI (typer) with a
shared findings schema (check id, status, severity, evidence, remediation, insurer mapping).
Implement the Microsoft 365 module with Microsoft Graph, read-only app registration, checking:
MFA registration coverage, Conditional Access policies, legacy authentication, Security
Defaults, global admin count and role assignments, external mailbox forwarding and inbox rules,
anonymous sharing links, guest users, audit log status, and Secure Score. Include --mock mode
with fixtures that trigger each check and fixtures that pass. Write tests. Document the exact
Graph permissions in a README. Show me the plan first.
```

**7. Google Workspace module**
```
Extend /tools/scanner with a Google Workspace module using the Admin SDK with a read-only
service account and domain-wide delegation. Check: 2-Step Verification enforcement, super
admin count, external forwarding, third-party OAuth apps and their scopes, external Drive
sharing settings, less-secure app access, and audit log availability. Same findings schema,
--mock mode, tests, README with exact scopes.
```

**8. Insurer-ready report**
```
Read /config/checks.yaml. In /tools/report, build a generator that takes findings JSON from the
scanner and renders an HTML and PDF report: a one-page summary with an overall score, a
"what your insurer will ask" table mapping each underwriting question (MFA, EDR, backups, email
security, admin access, incident response) to pass/fail/attestation-needed, top 5 fixes in
plain English, a detailed findings appendix, and an evidence pack section listing screenshots
or exports the client should attach. Brand from /config/brand.yaml. Add a --free flag that
renders only the one-page summary.
```

## Phase 4: AI policy kit (weeks 9-10)

**9. AI policy generator**
```
Read CLAUDE.md. In /tools/ai-policy, build a static web app (no backend; plain HTML/JS or
Astro island) with a ~20-question form: company size, industry, regulated data types, which AI
tools are approved, whether customer data may be entered, review and logging expectations,
and who owns AI decisions. From the answers generate (a) an AI acceptable use policy,
(b) a one-page staff guide, (c) an AI tool inventory template, all downloadable as Markdown and
DOCX. Questions and clause text live in a YAML file so I can edit them without touching code.
Free tier generates everything; add a clearly marked "paid: find the AI apps your staff actually
use" call to action that links to the scanner.
```

**10. AI app inventory from audit logs**
```
Extend /tools/scanner with an `ai-inventory` command that reads sign-in and OAuth consent logs
(Microsoft Graph) and token/OAuth audit events (Google Admin SDK) to list AI services in use
(ChatGPT, Claude, Gemini, Copilot, Notion AI, Otter, Fireflies, etc. from a maintained
/config/ai-apps.yaml), with user counts and whether access was via a personal or corporate
account where that can be inferred. Output a findings file the AI policy kit can import.
--mock mode and tests.
```

## Phase 5: Templates and pilots (weeks 9-13)

**11. Templates**
```
In /templates, create Markdown templates with the attorney-review header from CLAUDE.md for:
a pilot authorization letter (one page: scope, read-only access, data handling, no fee, either
side may stop), a Master Services Agreement outline, a Statement of Work for each of the three
services, a one-page case-study template (problem, what we did, result, with permission line),
and a referral partner one-pager. Use {{placeholders}}. Draft structure and plain-language
clauses only; mark anything that needs a lawyer.
```

**12. Pilot runbook**
```
In /docs, write a pilot runbook: how to onboard a free pilot in one hour (authorization letter,
app registration or service account setup with read-only scopes, run the scanner, render the
report, debrief call script, case-study ask). Include a checklist for cleaning up access after
the pilot. Add a decisions log file where I record what partners and pilots said.
```

## Phase 6: Growth basics (when the site has copy)

**13. Technical SEO and analytics**
```
Add per-page meta titles and descriptions, Open Graph tags, ProfessionalService schema,
sitemap.xml, robots.txt, canonical URLs, and privacy-respecting analytics (Plausible or
Umami free tier, or none). Add a blog collection with two starter posts I'll paste in:
"Cyber insurance renewal checklist for Massachusetts small businesses" and "Do you need an
AI policy? A 10-minute answer." Run Lighthouse and fix anything under 95.
```

## Habits

- Before building: "show me the plan first" on anything larger than a small fix.
- While building: ask for tests, and ask Claude to explain what you don't understand.
- Testing for real: only tenants you own or that are covered by a signed pilot authorization letter.
- After each prompt: update the status table in CLAUDE.md in the same commit.
