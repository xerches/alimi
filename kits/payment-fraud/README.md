# Payment Fraud Protection Kit

Five documents that stop the most expensive crime a company of 10 people and up faces: a payment sent to a criminal because an email said so. Since Nov 1, 2026 the kit is not a product of its own, and since Nov 2, 2026 it is not public either: the procedure, scripts and poster live in the platform's policy module, the training script is the finance lesson of the training module (`docs/training-modules.md`), and the half-day workshop and yearly drill are a service (`products.services.fraud_workshop` in `config/pricing.yaml`). It is written in plain English for finance staff, office managers and the owner, with every term defined where it first appears.

| ID | File | What it is | For whom |
| --- | --- | --- | --- |
| PFK-01 | `procedure.md` | Payment Verification Procedure: the verified callback to a number already on file, the two-person rule above `{{Threshold}}`, the 24-hour hold on new or changed bank details, payroll and customer-side rules, the first hour after a loss | Anyone who can create a vendor, change bank details, approve a payment or change payroll |
| PFK-02 | `callback-scripts.md` | Word-for-word scripts for six situations, what never to say, red flags to listen for | Finance and payroll staff |
| PFK-03 | `poster.md` | One-page poster: the three rules, the red flags, the boss rule, the first hour | Every desk |
| PFK-05 | `training-video-script.md` | 20-minute training: twelve slides with timings, speaker script, slide notes, a red-flag exercise and a quiz | The person recording or presenting the training |

## Placeholders

`{{Company}}`, `{{Finance Lead}}`, `{{CEO}}`, `{{Security Lead}}`, `{{Threshold}}` (default `$10,000` when built), `{{Bank Fraud Line}}`, `{{Effective Date}}`, `{{Your Name}}` (left for the caller in the scripts), and in the closing checklist `{{Firm}}` and `{{Firm Phone}}` for the law office or brokerage handing it out.

## Building

Needs [pandoc](https://pandoc.org/installing.html) (free). PDF also needs WeasyPrint (`pip install weasyprint`); there is no LaTeX dependency. Output goes to `kits/payment-fraud/build/out/` (git-ignored).

```
python kits/payment-fraud/build/build.py                                  # all five, DOCX and PDF
python kits/payment-fraud/build/build.py --only staff-poster              # one document (id or slug)
python kits/payment-fraud/build/build.py --fill "Acme Inc" --set "Finance Lead=Dana Lee" --set "Bank Fraud Line=555-0100"
python kits/payment-fraud/build/build.py --docx-only                      # skip PDF
```

The poster uses `build/poster.css` and must fit one Letter page; the tests check that. The other documents use `build/style.css`.

## Tests

```
pip install pyyaml pytest weasyprint && pytest kits/payment-fraud
```

The tests check the four documents exist with front matter, use only the placeholders above, define BEC and ACH before using the acronym, stay within their word ranges, state the three rules, name the source and year of every statistic, carry the kit note, and build to DOCX; with WeasyPrint installed they also render the poster and assert it is one page. `.github/workflows/kits.yml` runs them on changes under `kits/`.

## Sources and honest claims

- Loss figures are from the FBI Internet Crime Complaint Center's annual Internet Crime Report. The kit cites the 2025 report (published April 2026): 24,768 business email compromise complaints and $3.04 billion in reported losses. Update the figures and the year each April from ic3.gov.
- The FBI's Financial Fraud Kill Chain is referenced for international wires of $50,000 or more reported within 72 hours; confirm the current criteria with the bank or the FBI when adapting the procedure.
- The scenario in the training script is a composite built from the FBI's public descriptions, labelled as such. No client stories: Alimi has none yet, and the rules in `CLAUDE.md` forbid implying otherwise.

## What is not here

The video itself. PFK-05 is the script and slide notes; record it with a screen recorder and the brand colours from `config/brand.yaml`. The procedure refers to the Incident Response Policy (POL-13) in `/policies`; a company adopting both gets a consistent first-hour plan.
