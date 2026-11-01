# Payment Fraud Protection Kit

Five documents that stop the most expensive crime a 10 to 200 person company faces: a payment sent to a criminal because an email said so. The kit is sold as a digital product (`payment_fraud_kit.kit` in `config/pricing.yaml`) and used in the half-day workshop and yearly drill (`payment_fraud_kit.workshop`). It is written in plain English for finance staff, office managers and the owner, with every term defined where it first appears.

| ID | File | What it is | For whom |
| --- | --- | --- | --- |
| PFK-01 | `procedure.md` | Payment Verification Procedure: the verified callback to a number already on file, the two-person rule above `{{Threshold}}`, the 24-hour hold on new or changed bank details, payroll and customer-side rules, the first hour after a loss | Anyone who can create a vendor, change bank details, approve a payment or change payroll |
| PFK-02 | `callback-scripts.md` | Word-for-word scripts for six situations, what never to say, red flags to listen for | Finance and payroll staff |
| PFK-03 | `poster.md` | One-page poster: the three rules, the red flags, the boss rule, the first hour | Every desk |
| PFK-04 | `closing-day-checklist.md` | Checklist for buyers and sellers in a Massachusetts attorney-led closing, with a page for the closing office | Real estate attorneys, agents, their clients |
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

The tests check the five documents exist with front matter, use only the placeholders above, define BEC, ACH and IOLTA before using the acronym, stay within their word ranges, state the three rules, name the source and year of every statistic, carry the kit note, and build to DOCX; with WeasyPrint installed they also render the poster and assert it is one page. `.github/workflows/kits.yml` runs them on changes under `kits/`.

## Sources and honest claims

- Loss figures are from the FBI Internet Crime Complaint Center's annual Internet Crime Report. The kit cites the 2025 report (published April 2026): 24,768 business email compromise complaints and $3.04 billion in reported losses; 12,368 real estate fraud complaints and $275.1 million. Update the figures and the year each April from ic3.gov.
- The Massachusetts closing checklist draws on the Massachusetts Association of Realtors' wire fraud advisory (Form #519) and the Good Funds statute, M.G.L. c. 183 §63B, which requires the closing attorney to hold cleared funds (certified, treasurer's or cashier's check, or wire) before recording. It is general guidance, not legal advice, and says so; a Massachusetts real estate attorney should review it before a firm hands it to clients.
- The FBI's Financial Fraud Kill Chain is referenced for international wires of $50,000 or more reported within 72 hours; confirm the current criteria with the bank or the FBI when adapting the procedure.
- The scenario in the training script is a composite built from the FBI's public descriptions, labelled as such. No client stories: alimi has none yet, and the rules in `CLAUDE.md` forbid implying otherwise.

## What is not here

The video itself. PFK-05 is the script and slide notes; record it with a screen recorder and the brand colours from `config/brand.yaml`. The procedure refers to the Incident Response Policy (POL-13) in `/policies`; a company adopting both gets a consistent first-hour plan.
