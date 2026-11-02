# Alimi report

Turns a findings file from the scanner into the report a client hands to their insurance broker, a customer or an auditor: an HTML page that prints cleanly, and a PDF when WeasyPrint is installed.

Library first: the platform calls `render()` or `write_report()`. The `alimi-report` command wraps the same functions.

## Run it

```bash
cd tools/scanner && pip install -e ".[dev]"          # the report imports the scanner's schema and catalog
cd ../report  && pip install -e ".[dev,pdf]"         # drop ,pdf to skip WeasyPrint; HTML still renders

alimi-report demo                                    # full report from the scanner's m365 "fail" fixture -> ./out/
alimi-report demo -p gws -f pass --free              # free one-page summary, Google Workspace, clean tenant
alimi-report demo --reseller-name "Northside IT" --reseller-logo logo.png --reseller-contact help@northside.example
alimi-report render out/m365-20261101T010654Z.findings.json          # a real findings file
alimi-report render out/m365-...findings.json --free --no-pdf --name acme-summary
alimi-report backends                                # which PDF backend is installed
pytest                                               # 32 tests on the mock findings; the PDF test skips without WeasyPrint
```

Output goes to `./out/` (or `$ALIMI_OUTPUT_DIR`), git-ignored, named `<tenant>-<platform>-<report|summary>-<date>.html` and `.pdf`.

## What the report contains

**Page one (the free tier and the top of the paid report)**

- Cover: brand or reseller, tenant name, platform, the date the settings were read, and "read-only scan, no settings were changed".
- Score out of 100 with a one-word grade (Strong 90+, Good 75+, Needs work 50+, At risk below) and a sentence a business owner can repeat. The score is the scanner's severity-weighted share of automated checks that passed; items the client confirms with evidence do not move it.
- Four tiles: in place, need fixing, you confirm with evidence, could not be checked.
- **What your insurer will ask**: the eight underwriting questions from `config/checks.yaml` with a plain answer (Yes, No, You confirm, Not checked) and the checks behind each.
- **Top 5 fixes, in order**: failed checks ranked by severity, each with what we found, why it matters (from the catalog's `explain`) and what to do (the catalog's `remediation`).
- `--free` stops here and adds a call to action with the paid report and the service, priced from `config/pricing.yaml`.

**The paid report continues with**

- **Every finding**, grouped by what to do next (fix, confirm with evidence, could not be checked, already in place, not applicable), with the check id, the evidence the scanner saw, and notes.
- **Evidence pack**: a checklist of what to attach: the attestation items (EDR coverage export, backup and restore test record, incident response plan and tabletop notes) plus the screenshots the scanner asked for where an API could not read a setting, and anything a missing permission left unchecked.
- Notes from the scan, a glossary of only the terms that appear, and "How to read this report" (scope, date, what is not covered, when to re-run).
- A footer stating the report describes settings as read on that date and is not a guarantee of security, insurance acceptance or audit results.

## Reseller (white-label) mode

`--reseller-name`, `--reseller-logo` and `--reseller-contact` put the partner on the cover ("Prepared for Acme by Northside IT"), embed the logo in the HTML as a data URI so the file stays self-contained, and keep a "powered by Alimi" line under it, as the partner terms in `config/pricing.yaml` describe. `Reseller(powered_by=False)` exists in the library for a future tier; the CLI always shows the line.

## Library use

```python
from alimi_report import render, write_report, Reseller

report = render("out/m365-...findings.json")                # Report(html=..., model=...)
report = render(scan_result, free=True)                       # a ScanResult object works too, as does a dict or JSON string
paths = write_report(scan_result, "out/", pdf=True, reseller=Reseller(name="Northside IT", logo="logo.png"))
```

`render()` reads `config/brand.yaml` (colours, name, tagline, contact) and `config/pricing.yaml` (the free-tier call to action) by walking up from the working directory, or from `--brand` / `ALIMI_BRAND` and `ALIMI_PRICING`. `TODO` values in brand.yaml are treated as not decided and left out.

## PDF

WeasyPrint renders the same HTML with print CSS (Letter, page numbers, no page breaks inside a finding). It needs Pango and friends, which Linux and macOS package managers provide and which GitHub's Ubuntu runners already have. Without it, `write_report(pdf=True)` raises `PdfUnavailable` with the install line, and the CLI falls back to HTML with a note; the HTML prints to PDF from any browser.

## How it is put together

```
alimi_report/
  brand.py       Brand and Reseller models; loads config/brand.yaml and the offer from config/pricing.yaml
  model.py       ReportModel: grade, insurer answers in plain words, fix ranking, sections, evidence pack, glossary
  render.py      render(), render_html(), write_report(); Jinja2 with autoescape
  pdf.py         WeasyPrint backend behind one function, with a clear error when it is missing
  cli.py         typer commands: render, demo, backends, version
  templates/report.html.j2   one self-contained page: inline CSS, print rules, mobile layout
tests/           model decisions without HTML, rendering and flags, CLI, PDF (skipped without WeasyPrint)
```

The report never prints the tenant ID, the Google customer ID or any credential, because the findings file never contains them. It does print user addresses where a finding names accounts to fix; keep `out/` local.
