# Alimi demo

An unlisted, clickable demo of the Alimi platform, the compliance automation platform described on the marketing site. It is what the founder shows a prospect or a partner; it is never linked from the marketing site.

The sample company is **Saltmarsh Payroll, Inc.**, a fictional 52-person payroll bureau in Quincy, Massachusetts, 75 days from its cyber insurance renewal. Every person, vendor, date and number is invented. What is real: the 23 policies in `/policies`, the 40 controls in `/config/controls.yaml`, the requirement IDs in `/policies/requirements.yaml`, and the 12 Microsoft 365 checks from `/tools/scanner`, which were run for real on a fictional tenant snapshot (`data/snapshot.json`) to produce `data/scan.json`.

Nothing is saved. Forms have no action, buttons that would write are labelled "Demo: does nothing", and every page carries a banner saying the company is fictional.

## Running it

```bash
cd demo
npm install
npm run dev          # http://localhost:4321
npm run build        # astro build + scripts/check-dist.mjs
npm test             # data invariants, contrast, shared-lib equality
CHROME_PATH=/opt/pw-browsers/chromium npm run lighthouse   # or just npm run lighthouse where Chrome is on PATH
```

Node 22 or newer. The build reads `config/brand.yaml`, `config/controls.yaml`, `config/checks.yaml`, `policies/requirements.yaml` and `policies/*.md` from the repo, so run it from a full checkout.

## The twenty screens

| Group | Screen | What it shows |
| --- | --- | --- |
| Home | `/` | Readiness tiles, compliance progress per framework, what needs attention, tasks due, last scan |
| Compliance | `/frameworks`, `/frameworks/:id` | Insurer questionnaire, SOC 2, ISO 27001, HIPAA, ISO 42001: percent ready, one row per requirement ID with the controls and policies that satisfy it |
| Compliance | `/controls`, `/controls/:id` | 40 controls with owner, status, frameworks, evidence and tests; a control page with tests and their history, evidence with renewal dates, the add-evidence form, policies, risks, requirements and activity |
| Compliance | `/policies`, `/policies/:id` | The policy library: status, owner, version, acknowledgements; the policy's outline and opening paragraph (the text itself is never published) with its requirement mapping and the controls it sets rules for |
| Compliance | `/evidence` | The evidence library with status (ready, upcoming renewal, needs renewal, needs artifact), owner and renewal filters |
| Compliance | `/monitoring` | The 12 automated tests from the scanner, five weeks of history, the three attestation items, failing tests with the fix plan |
| Risk | `/risks` | Risk register scored on a 4x4 scale with treatment, owner, review date and linked controls |
| Risk | `/vendors`, `/vendors/:id` | Vendor inventory found through sign-in logs, app consent and accounts payable; inherent-risk rubric (data types, business criticality, integration access, communication scope); review tabs Evidence, Findings, Activity; a breach alert flagged as a finding |
| Risk | `/ai` | AI tool inventory (model, risk level, status, who has access), vendor AI changes feed, the AI policy acknowledgement count |
| People | `/people`, `/people/:id` | One row per person, one column per check (policies, training, MFA, device, background check); a person's page with their own tasks, including a new hire's onboarding checklist |
| People | `/training` | Three courses with completion, overdue learners and the yearly cycle |
| People | `/owners` | Tasks grouped by owner, with overdue counts and the reminder schedule |
| Assets | `/assets` | Devices from the tenant (EDR, disk encryption, compliance) and the data-store inventory with classification |
| Trust | `/trust` | The public trust page a prospect or bank would see: frameworks, published controls, request-access form |
| Trust | `/questionnaires` | The insurer questionnaire answered from the scan and a bank's 30-question review half drafted |
| Assistant | `/assistant` | Placeholder for the assistant: five prepared answers from the same data, each with its sources |
| Setup | `/integrations`, `/settings` | Microsoft 365 connected read-only with the exact permissions listed; what connects next; company settings |

## How statuses are computed

Nothing on these pages is typed as a status. `src/lib/data.js` derives everything from the data files, which is also the logic the platform (prompt 12) will reuse:

- **Evidence** is `ready` when it has an artifact and a renewal date more than 30 days out, `upcoming` within 30 days, `needs_renewal` past it, and `needs_artifact` when the item exists but nothing was attached.
- **Control** is `needs_owner` without an owner, `needs_attention` when a linked test fails, `needs_evidence` when an attestation test has no ready evidence or any evidence is missing or expired, otherwise `ok`.
- **Framework readiness** is the share of mapped controls that are `ok`, counted over controls, not requirement IDs.
- **People** are compliant when every check is a yes; tasks and overdue counts come from the same rows.
- Dates are measured from `AS_OF` (Nov 1, 2026) in `scripts/make_sample_data.py`, so the story (75 days to renewal, 44 days to the broker's deadline) does not drift as real time passes.

## Data

`data/*.json` is generated by `npm run data` (deterministic; two runs give identical files) and `data/scan.json` by `npm run scan`, which runs the real scanner on `data/snapshot.json` (`pip install -e ../tools/scanner` first). CI regenerates both and fails if the committed files differ. Details in [`data/README.md`](data/README.md).

## Brand and shared code

Colors and fonts come from `config/brand.yaml` through `src/lib/tokens.js`; a component never types a color, and `scripts/check-dist.mjs` fails the build on any hex, rgb or hsl value outside the inlined token block. `src/lib/config.js`, `tokens.js` and `contrast.js` are byte-for-byte copies of the marketing site's (`tests/shared-lib.test.mjs` fails if they diverge), because the two Netlify sites install their own dependencies and cannot import across folders. A palette change is one edit in `config/brand.yaml`; the contrast test and both builds prove it.

## Hosting

The demo is its own Netlify site with the base directory set to `demo` (so `demo/netlify.toml` applies: publish `dist`, Node 22, `X-Robots-Tag: noindex, nofollow, noarchive`, a strict Content-Security-Policy, no forms). `public/robots.txt` disallows everything and every page has `<meta name="robots" content="noindex, nofollow">`. Set `DEMO_SITE_URL` in the site's environment if the final URL is not `https://alimi-demo.netlify.app`.

The demo must stay free to run: static files only, no server, no analytics.

## Showing it (a 15-minute path)

1. **Home.** "Renewal in 75 days, broker wants the pack in 44. Here is where we stand: 31 of 40 controls fine, three failing tests, 33 of 52 people compliant."
2. **Monitoring.** The scanner's 12 checks on the tenant, read-only. Open the failing external-forwarding test: what it found, the plan, the owner, the due date.
3. **Controls → CTL-09 (MFA).** One owner, one status. Tests set it where a tenant read can; evidence with a renewal date covers the rest. Show the add-evidence form.
4. **Policies → Password and Authentication Policy.** The policy library in place: owner, version, who has acknowledged, and the requirement IDs it answers.
5. **Frameworks → Insurer.** The 13 questions the broker will ask, each answered by a control and a policy. Then SOC 2 at 77% to show the same work counts twice.
6. **People → Yara Castillo.** What a new hire sees on day one: policies to accept, training, MFA, device.
7. **Vendors → Brightfile.** The breach alert, flagged as a finding, with the review that follows.
8. **AI governance.** Which AI tools are in use, who has access, and what changed at a vendor this month.
9. **Questionnaires and Trust page.** The bank's review half drafted from existing answers; the page a prospect would see.
10. **Assistant.** Where it is going: answers from the program's own data with sources on every line.

The founder (as Security Lead) and the IT provider appear as two of the owners, which is how the service is sold: the platform plus a fractional compliance lead.
