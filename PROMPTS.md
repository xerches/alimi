# alimi build prompts for Claude Code

Run one prompt per session, in order. Review what it builds, commit, then move on. For anything bigger than a small change, the prompt already asks for a plan first; read the plan before saying go.

Order changed Nov 1, 2026: the workspace scanner and insurer-ready report come first, the payment fraud kit second, and the hosted platform grows around the scanner from prompt 12. The reasoning and the phase plan are in https://claude.ai/artifact/VDceUWrZQPkL2Gorc7798a. Prompts that are documents only (6, 7, 8, 9) can run in parallel with code prompts in a separate session.

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
with name "alimi", a placeholder tagline, and color tokens (dark teal, off-white, one accent).
Create /config/checks.yaml listing the scanner checks for Microsoft 365 and Google Workspace
with an id, title, severity, plain-English explanation, remediation, and which cyber insurance
question it maps to (MFA, EDR, backups, email security, admin access). Leave EDR and backups as
"attestation" checks since they can't be read from the tenant.
```

## Phase 2: Workspace scanner and insurer-ready report (weeks 3-10)

**3. Scanner core and Microsoft 365 connector** (done Nov 1, 2026)
```
Read CLAUDE.md and /config/checks.yaml. In /tools/scanner, build an installable Python package
`alimi_scanner` with a thin typer CLI on top. The package has: a shared findings schema (check
id, status, severity, evidence, remediation, insurer mapping) as dataclasses or pydantic models;
a checks engine that loads /config/checks.yaml and runs one check function per id; a connector
interface; a mock connector that is the default; and a Microsoft 365 connector using Microsoft
Graph with a read-only app registration. The m365 checks: MFA registration coverage, Conditional
Access policies, legacy authentication, Security Defaults, global admin count and role
assignments, external mailbox forwarding and inbox rules, anonymous sharing links, guest users,
audit log status, and Secure Score. Mock fixtures: one that triggers each check and one that
passes. Output findings JSON to the git-ignored out/ folder. Write pytest tests. Document the
exact Graph permissions and the app registration steps in a README. The package must be usable
without the CLI, because the platform web app imports it in prompt 12. Show me the plan first.
```

**4. Google Workspace connector** (done Nov 1, 2026)
```
Extend alimi_scanner with a Google Workspace connector using the Admin SDK with a read-only
service account and domain-wide delegation. Check: 2-Step Verification enforcement, super
admin count, external forwarding, third-party OAuth apps and their scopes, external Drive
sharing settings, less-secure app access, and audit log availability. Same findings schema,
same mock pattern, tests, README with exact scopes and the service account setup steps.
```

**5. Insurer-ready report** (done Nov 1, 2026)
```
Read /config/checks.yaml. In /tools/report, build a package `alimi_report` that takes findings
JSON from the scanner and renders an HTML and PDF report: a one-page summary with an overall
score, a "what your insurer will ask" table mapping each underwriting question (MFA, EDR,
backups, email security, admin access, incident response) to pass/fail/attestation-needed,
top 5 fixes in plain English, a detailed findings appendix, and an evidence pack section
listing screenshots or exports the client should attach. Brand from /config/brand.yaml. Add a
--free flag that renders only the one-page summary, and a --reseller option that puts a
partner's name and logo on the cover with a "powered by alimi" line. Expose a render()
function the platform can call, plus a CLI. Tests on the mock findings.
```

Gate: the scanner and report sell on their own before any platform code starts.

## Phase 3: Payment fraud kit (weeks 11-13)

**6. Payment fraud kit, documents** (done Nov 1, 2026)
```
Read CLAUDE.md. In /kits/payment-fraud, write Markdown sources for: (a) a payment-change and
wire verification procedure for a company of 10-200 people, with a verified-callback rule using
a phone number on file, a two-person rule above a threshold, and a 24-hour hold on new or changed
bank details; (b) callback scripts for finance staff; (c) a one-page staff poster; (d) a
closing-day checklist for home buyers and sellers in a Massachusetts attorney-led closing;
(e) a 20-minute training video script with slide notes. Use {{Company}} placeholders. Add a
build script that renders each to PDF with pandoc or weasyprint. Plain English, no jargon
without a definition. Show me the plan first.
```

## Phase 4: Policy library, templates and pilot runbook (weeks 13-16, before the first pilot)

**7. Policy library** (done Nov 1, 2026)
```
Read CLAUDE.md. In /policies, write a library of security and company policies sized for a
10-200 person company, in Markdown with YAML front matter: id, title, version, owner role,
review cycle, and the requirements each policy satisfies by criterion ID only (SOC 2 trust
services criteria such as CC6.1, ISO 27001:2022 clauses and Annex A controls such as A.5.15,
ISO 42001:2023 clauses and Annex A controls, HIPAA Security Rule sections where relevant, and
the cyber insurance question). Write as many as the frameworks call for; start with:
information security policy, acceptable use, access control, asset management, data
classification and handling, cryptography and key management, secure development and change
management, vulnerability and patch management, logging and monitoring, backup and recovery,
business continuity and disaster recovery, incident response, vendor and third-party risk,
risk management, human resources security (screening, onboarding, offboarding, training),
physical and environmental security, remote work and personal devices, password and
authentication, network and endpoint security, data retention and disposal, privacy, AI
acceptable use, and AI governance (AI policy, roles, impact assessment, AI system lifecycle,
for ISO 42001). Each policy: purpose, scope, roles, numbered policy statements, exceptions,
enforcement, review, revision history; 2-4 pages; plain English; {{Company}} placeholders.
Header on every file: "TEMPLATE. Adapt before adopting. Sections marked [HR or legal review]
need a human reviewer." Generate /policies/coverage.md, a matrix of requirement -> policy,
from the front matter with a script, and flag requirements no policy covers. Add a build
script to DOCX and PDF with pandoc, with a --fill option for the company name. Never copy
framework text; cite IDs only. The platform (prompt 13) and the AI policy kit (prompt 15)
import this folder. Show me the plan first.
```

**8. Templates** (done Nov 1, 2026)
```
In /templates, create Markdown templates with the attorney-review header from CLAUDE.md for:
a pilot authorization letter (one page: scope, read-only access, data handling, no fee, either
side may stop), a Master Services Agreement outline, a Statement of Work for each of the
services, a reseller agreement outline (wholesale tiers from /config/pricing.yaml, white-label
terms, who invoices whom, data handling for the reseller's clients), a referral agreement
outline, a one-page case-study template (problem, what we did, result, with permission line),
and a referral partner one-pager. Use {{placeholders}}. Draft structure and plain-language
clauses only; mark anything that needs a lawyer.
```

**9. Pilot runbook** (done Nov 1, 2026)
```
In /docs, write a pilot runbook: how to onboard a free pilot in one hour (authorization letter,
app registration or service account setup with read-only scopes, run the scanner, render the
report, debrief call script, case-study ask). Include a checklist for cleaning up access after
the pilot. Extend the decisions log with a section where I record what partners and pilots said.
```

## Phase 5: Marketing site (weeks 17-19)

**10. Marketing site** (done Nov 1, 2026)
```
Read CLAUDE.md and /config. In /site, build a fast static site with Astro. Pages: Home, the
product pages (Workspace Security Scan, Policy Pack, Payment Fraud Kit, AI Policy Kit), For
Partners (resellers: MSPs and IT consultancies; referrers: brokers, CPAs, attorneys), About,
Contact. Each product page has a waitlist form using Netlify Forms, a "how it works" section,
and a pricing block read from /config/pricing.yaml at build time. The For Partners page shows
the reseller tiers and the referral fee from pricing.yaml and has its own sign-up form. The
scanner page has a short "what comes next" block about the hosted platform. Pull brand tokens
from /config/brand.yaml. Mobile-first, accessible, Lighthouse 95+. Placeholder copy marked
TODO. Add a netlify.toml so it deploys with no settings. Show me the plan first.
```

**11. Site copy**
```
Read CLAUDE.md, /docs/research (I'll paste the three research summaries there first), and the
site. Replace every TODO with final copy. Homepage headline leads with the outcome for a
business owner, not the technology. Each product page states the complaint, what they get,
what it costs, and what happens next. The For Partners page states the margin a reseller
keeps in one sentence. Resume metrics are attributed to employment per the Rules in
CLAUDE.md. Write the About page in first person, 150 words.
```

## Phase 6: Platform web app (weeks 20-29)

**12. Platform foundation**
```
Read CLAUDE.md and the platform plan it links. In /platform, build a FastAPI app with HTMX
server-rendered pages and Postgres. Models: Organization, User, Integration (a connected tenant
with read-only scopes, an encrypted token, last sync), Framework, Requirement, Control, Test,
Evidence (file or attestation with an expiry date), AuditLog. A reseller is an Organization
with child organizations and a multi-tenant view. Login through a hosted auth provider with a
free tier; recommend one and explain the choice. Row-level security on every table that holds
customer data, keyed by organization. Tokens encrypted with a key from the environment, never
logged. Import alimi_scanner: connect a tenant (mock by default), run the checks on demand and
nightly from a worker, store each result as a Test against its Control. First framework: the
insurer questionnaire, built from the insurer mapping in /config/checks.yaml, with criterion
IDs and our own plain-English summaries only. One `docker compose up` runs app, database and
worker on mock data; CI runs the tests on every PR. Show me the plan first.
```

**13. Policies and people**
```
Extend /platform. Policies: import the /policies library (front matter becomes the framework
mapping), versions, an approver, and staff acceptance tracking with reminders. People: pull
the staff list from the connected Microsoft 365 or Google Workspace tenant, an onboarding and
offboarding checklist per person, and training completion. Link policies and people to
controls so the dashboard can score them. Mock data, tests, plain-English page copy.
```

**14. Dashboard, reports and SOC 2**
```
Extend /platform. A readiness dashboard per framework: overall score, each requirement with its
controls and whether they pass, fail or need attestation, top fixes. Render the insurer-ready
report by calling alimi_report inside the app, with the reseller's branding when the
organization belongs to one, and build an export pack (zip of the report plus evidence files
and adopted policies) for a broker or auditor. Add SOC 2 as the second framework and ISO 27001
as the third: criterion IDs and our own summaries only, mapped onto the existing controls and
policies. Tests on mock data.
```

## Phase 7: AI policy kit (weeks 30-32)

**15. AI policy generator**
```
Read CLAUDE.md. In /tools/ai-policy, build a static web app (no backend; plain HTML/JS or
Astro island) with a ~20-question form: company size, industry, regulated data types, which AI
tools are approved, whether customer data may be entered, review and logging expectations,
and who owns AI decisions. From the answers generate (a) an AI acceptable use policy,
(b) a one-page staff guide, (c) an AI tool inventory template, all downloadable as Markdown and
DOCX. Questions and clause text live in a YAML file so I can edit them without touching code;
the clauses start from the AI policies in /policies. Free tier generates everything; add a
clearly marked "paid: find the AI apps your staff actually use" call to action that links to
the scanner.
```

**16. AI app inventory from audit logs**
```
Extend alimi_scanner with an `ai-inventory` command that reads sign-in and OAuth consent logs
(Microsoft Graph) and token/OAuth audit events (Google Admin SDK) to list AI services in use
(ChatGPT, Claude, Gemini, Copilot, Notion AI, Otter, Fireflies, etc. from a maintained
/config/ai-apps.yaml), with user counts and whether access was via a personal or corporate
account where that can be inferred. Output a findings file the AI policy kit and the platform
can import. --mock mode and tests.
```

## Phase 8: Growth basics (when the site has copy)

**17. Technical SEO and analytics**
```
Add per-page meta titles and descriptions, Open Graph tags, ProfessionalService schema,
sitemap.xml, robots.txt, canonical URLs, and privacy-respecting analytics (Plausible or
Umami free tier, or none). Add a blog collection with two starter posts I'll paste in:
"Cyber insurance renewal checklist for Massachusetts small businesses" and "Do you need an
AI policy? A 10-minute answer." Run Lighthouse and fix anything under 95.
```

## Later, only when a customer asks (no prompts yet)

Vendor risk list with review dates, risk register, customer questionnaire answer library, public trust center, more integrations (AWS, GitHub, Intune, Jamf, HR systems), auditor portal, reseller billing and usage reports. Write the prompt when the first customer or reseller asks for the module.

## Habits

- Before building: "show me the plan first" on anything larger than a small fix.
- While building: ask for tests, and ask Claude to explain what you don't understand.
- Testing for real: only tenants you own or that are covered by a signed pilot authorization letter.
- After each prompt: update the status table in CLAUDE.md in the same commit.
