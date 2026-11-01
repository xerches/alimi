# alimi templates

Drafts of the documents alimi needs before its first pilot and its first paid work, written as structure and plain-language clauses for a Massachusetts attorney to turn into agreements. Every file starts with **DRAFT. Not legal advice. Review by a Massachusetts attorney before use.** and marks the clauses that need legal text with `[Attorney review]`. alimi drafts intent; it does not invent legal language.

Prices never appear in the templates as numbers. They are read from `config/pricing.yaml` through `{{pricing.*}}` tokens when a document is rendered, so a proposal cannot contradict the price list. A test fails if a dollar amount is typed into a template.

## What is here

| File | Use it when |
| --- | --- |
| `pilot-authorization-letter.md` | Before any scan of a tenant alimi does not own. One page, no fee, read-only, either side may stop. Required by CLAUDE.md. |
| `master-services-agreement-outline.md` | The first paid engagement. Sets the terms every SOW sits under. |
| `sow-workspace-scan-and-report.md` | Selling the full insurer-ready report. |
| `sow-insurance-ready-in-30-days.md` | Selling the fix-it service with the tabletop and the evidence pack to the broker. |
| `sow-payment-fraud-workshop.md` | Selling the half-day workshop and yearly drill from the payment fraud kit. |
| `sow-policy-adoption-workshop.md` | Selling the policy library with the adoption workshop. |
| `sow-ai-policy-implementation.md` | Selling the AI policy implementation with the optional ISO 42001 gap check. |
| `sow-fractional-security-lead.md` | The monthly retainer. |
| `reseller-agreement-outline.md` | An MSP, IT consultancy or vCISO firm wants to resell. Tiers, white-label terms, billing, client data, channel promise. |
| `referral-agreement-outline.md` | A broker, CPA or attorney will refer but not resell. Fee, and the option to decline it under professional rules. |
| `case-study-template.md` | After a pilot or engagement, with the client's signed permission. Honest-claims rules built in. |
| `referral-partner-one-pager.md` | Handing to a partner in a first conversation. |

## Placeholders

`{{Client}}`, `{{Client Address}}`, `{{Client Contact}}`, `{{Client Signatory}}`, `{{Client Title}}`, `{{alimi Entity}}` (the legal name once the LLC exists; before that, the attorney advises what to write), `{{alimi Signatory}}`, `{{alimi Address}}`, `{{Effective Date}}`, `{{Start Date}}`, `{{End Date}}`, `{{Tenant}}` (Microsoft 365 or Google Workspace), `{{Tenant Domain}}`, `{{Reseller}}`, `{{Partner}}`, `{{Partner Firm}}`, `{{Fee}}` (an hourly rate agreed per client), `{{Quoted Price}}` (the number inside the published range), `{{Contact Email}}`, `{{Contact Phone}}`, `{{Website}}`.

Pricing tokens, resolved from `config/pricing.yaml`: `{{pricing.products.<product>.<tier>.price|name|includes|product_name}}`, `{{pricing.retainers.<retainer>.price|hours|name}}`, `{{pricing.partners.reseller.tiers_table|includes|who|buys_at|billing|review}}`, `{{pricing.partners.reseller.discount.<tier>}}`, `{{pricing.partners.referral.fee|of|paid|who}}`, `{{pricing.partners.principle}}`, `{{pricing.terms.payment|minimum_monthly_retainer}}`; `<product>` is `platform`, `services` or `free`.

## Rendering

```
python templates/build/render.py --check                                   # every pricing token resolves
python templates/build/render.py                                           # all templates with prices filled -> templates/build/out/ (Markdown, plus DOCX if pandoc is installed)
python templates/build/render.py --only sow-workspace-scan-and-report --set "Client=Acme Inc" --set "Tenant=Microsoft 365" --set "Quoted Price=$750"
python templates/build/render.py --pdf                                     # also PDF (pip install weasyprint)
```

Output is git-ignored. The Markdown sources are never changed by the script.

## Tests

```
pip install pyyaml pytest && pytest templates
```

They check that the twelve templates exist, start with the header, use only the placeholders above, resolve every pricing token, type no dollar amounts, carry `[Attorney review]` markers where a lawyer is needed, that the pilot letter fits one page and says read-only, no fee and either side may stop, that each SOW names its price from the price list, that the reseller outline renders the tier table, and that the render script builds a DOCX. `.github/workflows/templates.yml` runs them on changes under `templates/` or to `config/pricing.yaml`.

## Gates these documents respect

- No paid SOW is signed before the LLC exists and professional and cyber liability insurance is in place (MSA section 14). The pilot letter is free and is the only document used before then.
- No tenant is scanned without a signed pilot letter or SOW (CLAUDE.md, "test tenants only").
- A case study is published only with the signed permission on the template, and quotes only that client's measured results.
- The reseller and referral terms are starting points proposed on Nov 1, 2026; confirm them before the first partner conversation and change `config/pricing.yaml`, not the templates.
