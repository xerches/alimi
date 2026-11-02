# alimi policy library

Twenty-three security and company policies for a 10 to 200 person company, written in plain English for an owner rather than an auditor, and mapped by criterion ID to SOC 2, ISO 27001:2022, ISO 42001:2023, the HIPAA Security Rule and the cyber insurance questionnaire. The library is sold on its own as a policy pack, included in the services, and read by the platform (prompt 13) and the AI policy kit (prompt 15).

Every file starts with the header **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.** The library maps to requirements by ID only; it never quotes SOC 2 or ISO text, which is copyrighted. `requirements.yaml` holds our own one-line summaries of what each ID asks for.

## What is here

| Path | What it is |
| --- | --- |
| `NN-<slug>.md` | The 23 policies, Markdown with YAML front matter |
| `requirements.yaml` | The requirement catalogue: five frameworks, 275 IDs, each with a one-line summary in our words |
| `coverage.md` | Generated matrix of requirement to policy, with any uncovered IDs flagged; do not edit by hand |
| `build/coverage.py` | Builds `coverage.md` from the front matter; `--check` fails if it is stale or a policy cites an unknown ID |
| `build/build.py` | Builds DOCX and PDF with pandoc, fills placeholders, assembles the combined pack |
| `build/style.css` | Print styles for the PDF |
| `tests/test_policies.py` | Checks every policy's structure, placeholders, length, mappings and the build |

## The policies

The counts are how many requirement IDs in each framework the policy maps to. Several policies can map to the same ID; `coverage.md` has the full matrix.

| ID | Policy | Owner role | Maps to |
| --- | --- | --- | --- |
| POL-01 | Information Security Policy | {{Security Lead}} | soc2 12, iso27001 32, iso42001 1, hipaa 4 |
| POL-02 | Acceptable Use Policy | {{Security Lead}} | soc2 5, iso27001 9, iso42001 1, hipaa 2, insurer 2 |
| POL-03 | Access Control Policy | {{Security Lead}} | soc2 3, iso27001 8, hipaa 3, insurer 1 |
| POL-04 | Password and Authentication Policy | {{Security Lead}} | soc2 2, iso27001 2, hipaa 2, insurer 2 |
| POL-05 | Asset Management Policy | {{IT Lead}} | soc2 3, iso27001 8, iso42001 3, hipaa 1, insurer 1 |
| POL-06 | Data Classification and Handling Policy | {{Security Lead}} | soc2 4, iso27001 5, iso42001 1, hipaa 2, insurer 1 |
| POL-07 | Cryptography and Key Management Policy | {{Security Lead}} | soc2 3, iso27001 1, hipaa 3, insurer 1 |
| POL-08 | Secure Development and Change Management Policy | {{IT Lead}} | soc2 3, iso27001 12, iso42001 3 |
| POL-09 | Vulnerability and Patch Management Policy | {{IT Lead}} | soc2 2, iso27001 3, hipaa 1, insurer 2 |
| POL-10 | Logging and Monitoring Policy | {{Security Lead}} | soc2 4, iso27001 4, iso42001 1, hipaa 2, insurer 1 |
| POL-11 | Backup and Recovery Policy | {{IT Lead}} | soc2 3, iso27001 2, hipaa 2, insurer 1 |
| POL-12 | Business Continuity and Disaster Recovery Policy | {{CEO}} | soc2 5, iso27001 6, hipaa 2, insurer 2 |
| POL-13 | Incident Response Policy | {{Security Lead}} | soc2 5, iso27001 7, iso42001 1, hipaa 1, insurer 1 |
| POL-14 | Vendor and Third-Party Risk Policy | {{Security Lead}} | soc2 2, iso27001 6, iso42001 3, hipaa 2, insurer 1 |
| POL-15 | Risk Management Policy | {{Security Lead}} | soc2 7, iso27001 8, iso42001 5, hipaa 1 |
| POL-16 | Human Resources Security Policy | {{HR Lead}} | soc2 7, iso27001 10, iso42001 3, hipaa 2, insurer 1 |
| POL-17 | Physical and Environmental Security Policy | {{Security Lead}} | soc2 3, iso27001 11, hipaa 2 |
| POL-18 | Remote Work and Personal Devices Policy | {{Security Lead}} | soc2 3, iso27001 4, hipaa 3, insurer 2 |
| POL-19 | Network, Endpoint and Email Security Policy | {{Security Lead}} | soc2 5, iso27001 9, hipaa 2, insurer 3 |
| POL-20 | Data Retention and Disposal Policy | {{Security Lead}} | soc2 4, iso27001 5, hipaa 2 |
| POL-21 | Privacy and Data Protection Policy | {{Privacy Lead}} | soc2 19, iso27001 3, iso42001 1 |
| POL-22 | AI Acceptable Use Policy | {{AI Lead}} | soc2 2, iso27001 3, iso42001 7, insurer 1 |
| POL-23 | AI Governance Policy | {{AI Lead}} | soc2 2, iso27001 1, iso42001 65 |

## Policy format

Front matter keys: `id`, `slug`, `title`, `version`, `status` (always `template` here), `owner_role`, `approver_role`, `review_cycle`, `applies_to`, `requirements` (one list per framework key in `requirements.yaml`: `soc2`, `iso27001`, `iso42001`, `hipaa`, `insurer`) and `related` (other policy IDs).

Body: the header line, then `# {{Company}} <Title>`, a metadata table, and nine sections in this order: Purpose, Scope, Roles and responsibilities, Policy statements (numbered, grouped under 4.x headings), Exceptions, Enforcement, Review, Related documents, Revision history. Each policy is two to four pages when built.

Placeholders, filled by the build script or by hand: `{{Company}}`, `{{CEO}}`, `{{Security Lead}}`, `{{IT Lead}}`, `{{HR Lead}}`, `{{Privacy Lead}}`, `{{Finance Lead}}`, `{{AI Lead}}`, `{{Effective Date}}`. In a small company several of these are the same person; fill them with the same name.

`[HR or legal review]` marks a statement that touches employment law, contracts, notification duties or the law of a specific place (background checks, monitoring of personal devices, breach notification, retention periods, legal holds). A human reviews and edits those statements before adoption. The `--final` build refuses to run while any marker or placeholder remains.

The insurer IDs (`mfa`, `admin_access`, `email_security`, `data_sharing`, `logging`, `edr`, `backups`, `incident_response`) are the same IDs the scanner uses in `config/checks.yaml`, so a scan finding and the policy that answers the question line up. The catalogue adds five questionnaire items the scanner cannot check (`training`, `patching`, `encryption`, `vendor_risk`, `remote_access`); the policies answer those on paper.

## Adopting the library at a company

1. Decide which policies apply. All 23 for SOC 2 or ISO 27001; the 21 without the two AI policies if the company neither uses nor builds AI systems (rare now); the `insurer` column of `coverage.md` shows the smallest set that answers the insurance questionnaire.
2. Build a filled draft: `python policies/build/build.py --fill "Acme Inc" --set "CEO=Sam Ortiz" --set "Security Lead=Dana Lee" --set "Effective Date=2027-01-15"`.
3. Read each policy with the owner. Change what does not fit (the company may not have an office, may not build software, may use a managed service provider for everything). Have HR or counsel review the marked statements and remove the markers.
4. Approve and sign (the metadata table has the approver), publish where staff can find them, train staff under POL-16, and collect acknowledgements under POL-02.
5. Build the final copies: add `--final` to strip the TEMPLATE header. Keep the Markdown sources under version control so the revision history is real.

The build never changes the Markdown sources. Output goes to `policies/build/out/` (git-ignored) unless `--out` says otherwise.

## Building

Needs [pandoc](https://pandoc.org/installing.html) (free). PDF also needs WeasyPrint (`pip install weasyprint`); there is no LaTeX dependency.

```
python policies/build/build.py                         # every policy to DOCX and PDF
python policies/build/build.py --only POL-13           # one policy (id or slug), repeatable
python policies/build/build.py --fill "Acme Inc" --set "Security Lead=Dana Lee"
python policies/build/build.py --fill "Acme Inc" --final    # strips the header; refuses if placeholders or review markers remain
python policies/build/build.py --pack                  # also one combined policy-pack.docx and .pdf
python policies/build/build.py --docx-only             # skip PDF
```

## Coverage and tests

```
python policies/build/coverage.py          # rewrite coverage.md
python policies/build/coverage.py --check  # CI: stale matrix or unknown ID fails
pip install pyyaml pytest && pytest policies
```

The tests assert that there are 23 policies, that each has the header, the sections in order, only known placeholders, 700 to 2200 words and at least ten numbered statements, that every cited ID exists, that every ID in all five frameworks is covered, that `coverage.md` is current, that the HR and legal markers are present where expected, and (when pandoc is installed) that the build and the `--final` gate work. `.github/workflows/policies.yml` runs them on every change under `policies/`.

A mapping means the policy contains statements that address the requirement, not that an auditor has agreed. Add a requirement by adding its ID and a one-line summary in our own words to `requirements.yaml`, then mapping at least one policy to it; the coverage check will tell you if you forgot.

## How the rest of alimi uses this folder

- The scanner's insurer-ready report names the policy that answers each failed insurer question.
- The platform's policy module (prompt 13) reads the front matter for its policy list, versions, owners, review dates and the control mapping; staff sign-off is tracked against the `id` and `version`.
- The platform's AI governance module (prompt 15) generates a company-specific POL-22 and POL-23 from this source.
- The reseller white-label option replaces the alimi name in the revision history and the pack cover; the policy text itself does not mention alimi.
