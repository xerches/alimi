# Sample data

Everything in this folder describes **Saltmarsh Payroll, Inc.**, a fictional company. People, vendors named as fictional, dates, scores and numbers are invented by `../scripts/make_sample_data.py`. No file here was read from a real tenant, and none may ever be: the demo is static and the rule in `CLAUDE.md` (test tenants only, no client data in the repo) applies.

| File | What it holds |
| --- | --- |
| `company.json` | Name, size, sector, the renewal dates, the frameworks in scope, the remediation plan for the failing tests, the `as_of` date |
| `snapshot.json` | A fictional Microsoft 365 tenant in the scanner's snapshot format: 61 accounts, four Conditional Access policies, inbox rules, sharing settings, audit retention, secure score. Input to the scanner, never output from one |
| `scan.json` | The scanner's real output on that snapshot: 12 checks, 9 pass, 3 fail, 3 attestation items, insurer answers |
| `monitoring-history.json` | Five weekly runs of the same checks, Oct 2 to Oct 30, 2026 |
| `people.json` | 52 staff and 4 external accounts (IT provider, Alimi, an admin-only account, the broker's guest) with department, manager, start date, groups, MFA, device, training and acknowledgement state |
| `assignments.json` | Which role owns what: owner roles map to people here and nowhere else |
| `policies.json` | Adoption data per policy: version, status, owner, approver, dates, who has acknowledged |
| `evidence.json` | 42 evidence items with type, owner, created and renewal dates, and the controls or attestations they support |
| `vendors.json` | 21 vendors with discovery source, data shared, the four rubric scores, review state, evidence, findings and the breach alert |
| `ai-tools.json` | 11 AI tools in use with model, risk level, status and access, plus the vendor AI change feed |
| `risks.json` | 13 risks scored likelihood x impact on a 4-point scale, with treatment, owner and linked controls |
| `questionnaires.json` | The insurer questionnaire answers and the bank's 30-question review |
| `assets.json` | 55 devices and the data-store inventory |
| `training.json` | Three courses with completion and due dates |
| `integrations.json` | What is connected (Microsoft 365, read-only, the seven permissions), what can connect next |

## Regenerating

```bash
npm run data                       # rewrites every file except scan.json; deterministic
pip install -e ../tools/scanner    # once
npm run scan                       # runs alimi-scan on snapshot.json and writes scan.json
```

Commit the result. CI runs both and fails on a diff, so the committed files always match the generator and the scanner that produced them.

## Conventions

- Real products a 52-person company would use (Microsoft 365, Dropbox, Zapier, Slack and so on) appear under their own names as *things the sample company uses*. Vendors that are invented carry `"fictional": true` and are labelled as fictional on their page.
- Dates are measured from `as_of` (2026-11-01), not from today, so the walkthrough numbers stay stable.
- Owner roles (Security Lead, IT Lead, HR Lead, Finance Lead, Privacy Lead, AI Lead) resolve to people through `assignments.json`; two controls deliberately have no owner to show the state.
- Three tests fail and three need an attestation on purpose; `company.json` carries the fix plan the pages show.
