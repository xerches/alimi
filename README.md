# denimi

Security that insurers, customers and auditors accept, for companies too small for a security team.

This repo holds everything denimi builds. Start with `CLAUDE.md` (the project brief Claude Code reads every session) and `PROMPTS.md` (the build prompts, in order).

| Folder | What lives here |
| --- | --- |
| `site/` | Static marketing site. Deploys free to Netlify or Cloudflare Pages. |
| `tools/scanner/` | Read-only Python package and CLI that scores Microsoft 365 and Google Workspace security. `--mock` by default. The platform imports it. |
| `tools/report/` | Turns scanner findings into an insurer-ready HTML/PDF report. |
| `platform/` | Hosted compliance platform (phase 3 and later): FastAPI, HTMX pages, Postgres. Orgs, login, scheduled runs, controls, evidence, policies, people, dashboard. |
| `tools/ai-policy/` | Static web app that generates an AI acceptable use policy, staff guide and tool inventory. |
| `policies/` | Security and company policy library in Markdown, mapped to SOC 2, ISO 27001 and ISO 42001 by criterion ID. Sold as a policy pack, imported by the platform. |
| `kits/payment-fraud/` | Markdown sources for the payment-change and wire verification kit, rendered to PDF. |
| `templates/` | MSA, SOW, pilot authorization letter, case study and partner one-pager. Drafts for attorney review. |
| `docs/` | Research summaries, decisions log, pilot runbook. |
| `config/` | `pricing.yaml`, `brand.yaml`, `checks.yaml`. Single source of truth for prices, brand and scanner checks. |

## Rules in one breath

No real credentials or tenant IDs in git. Mock mode is the default. Tools run only against tenants we own or have written permission for. Legal templates are drafts for a Massachusetts attorney. Claims on the site are attributed honestly.

## Local setup

```bash
pip install pre-commit && pre-commit install   # secret scanning on every commit
cp .env.example .env                           # fill in only for your own test tenants
```
