# Alimi

Security that insurers, customers and auditors accept, for companies too small for a security team.

This repo holds everything Alimi builds. Start with `CLAUDE.md` (the project brief Claude Code reads every session) and `PROMPTS.md` (the build prompts, in order).

| Folder | What lives here |
| --- | --- |
| `site/` | Static marketing site for the one offer, the Alimi platform: published tiers, services, free resources, partner terms. Deploys free to Netlify. |
| `tools/scanner/` | Read-only Python package and CLI that scores Microsoft 365 and Google Workspace security. `--mock` by default. The platform imports it. |
| `tools/report/` | Turns scanner findings into an insurer-ready HTML/PDF report. |
| `platform/` | Hosted compliance platform (phase 3 and later): FastAPI, HTMX pages, Postgres. Orgs, login, scheduled runs, controls, evidence, policies, people, dashboard. |
| `demo/` | Platform demo for prospects: a sample company, every module, built from the real scanner run and policy library. Unlisted. |
| `tools/ai-policy/` | AI governance module (not started): AI policy generator and AI app inventory, inside the platform. |
| `policies/` | Security and company policy library in Markdown, mapped to SOC 2, ISO 27001, ISO 42001, HIPAA and the insurer questions by criterion ID. The platform's policy module; three core policies are published free on the site. |
| `kits/payment-fraud/` | Payment-change and wire verification procedure, scripts, poster and checklist. Free on the site; the workshop is a service. |
| `templates/` | MSA, SOW, pilot authorization letter, case study and partner one-pager. Drafts for attorney review. |
| `docs/` | Research summaries, decisions log, pilot runbook. |
| `config/` | `pricing.yaml`, `brand.yaml`, `checks.yaml`, `controls.yaml`. Single source of truth for prices, brand, scanner checks and controls. |

## Rules in one breath

No real credentials or tenant IDs in git. Mock mode is the default. Tools run only against tenants we own or have written permission for. Legal templates are drafts for a Massachusetts attorney. Claims on the site are attributed honestly.

## Local setup

```bash
pip install pre-commit && pre-commit install   # secret scanning on every commit
cp .env.example .env                           # fill in only for your own test tenants
```
