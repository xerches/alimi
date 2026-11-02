---
slug: sow-workspace-scan-and-report
title: Statement of Work, Workspace Security Scan and Insurer-Ready Report
---
> **DRAFT. Not legal advice. Review by a Massachusetts attorney before use.**

# Statement of Work: {{pricing.products.services.assessment.name}}

*Under the Master Services Agreement between {{Alimi Entity}} ("Alimi") and {{Client}} dated {{Effective Date}}. SOW number: ______. Prices are read from Alimi's price list at signing.*

## 1. Objective

Give {{Client}} a clear, evidence-backed picture of the security settings in its {{Tenant}} environment, written so that an owner can act on it and a cyber insurer, broker or customer will accept it.

## 2. Scope

**In scope:** one {{Tenant}} tenant, domain {{Tenant Domain}}, up to 200 user accounts. The scan runs Alimi's published checks for {{Tenant}}: multi-factor authentication coverage, administrator accounts and their protection, legacy sign-in methods, external email forwarding and mailbox rules, sharing settings, audit log retention, email authentication records (SPF, DKIM, DMARC), third-party application access, and the settings that need a screenshot because no interface exposes them. Each check is mapped to the question an insurer asks.

**Out of scope:** fixing anything (see the Insurance-ready in 30 days SOW), other tenants or domains, endpoints, cloud infrastructure, penetration testing, and policies.

## 3. Deliverables

{{pricing.products.services.assessment.includes}}

The report is delivered as PDF and HTML and contains, for every check: pass, fail or "you confirm", the evidence collected, the severity, and the plain-English fix. The evidence pack checklist tells the Client what to send the broker and in what form.

## 4. Approach and timeline

| Day | Step |
| --- | --- |
| 1 | Kick-off call (30 minutes). Client's administrator creates the read-only access using Alimi's written instructions. |
| 2 to 3 | Alimi runs the scan from its own encrypted computer and reviews the results by hand. |
| By day 7 | Report delivered to {{Client Contact}}. |
| By day 12 | 30-minute debrief call. Access removed by the Client's administrator; Alimi confirms deletion of scan data within 30 days. |

## 5. Client responsibilities

Name a contact with authority; have an administrator available for about one hour to create and later remove the access; provide screenshots for the three or four settings the scanner cannot read, using Alimi's checklist; confirm it owns or controls {{Tenant Domain}}.

## 6. Access and data

Read-only permissions only, listed in the appendix and created by the Client's administrator; Alimi never holds an administrator account or password and stores no tokens. Scan results contain configuration and audit metadata, not the content of email or files. Data handling follows section 5 of the Master Services Agreement.

## 7. Assumptions

One tenant, up to 200 accounts; a single scan run (a rescan after fixes is available as a change order); the Client's environment is a standard {{Tenant}} tenant without custom federation that blocks read access. Results describe the configuration on the day of the scan.

## 8. Fee and payment

Fixed fee within Alimi's published range of **{{pricing.products.services.assessment.price}}**, quoted for this engagement at **{{Quoted Price}}** based on account count and the number of domains. Payment: {{pricing.terms.payment}}; this SOW is invoiced on signing. No expenses.

## 9. Acceptance

The Client accepts a deliverable by email, or by not objecting within five business days of delivery. Objections name the clause of this SOW the deliverable fails to meet; Alimi re-performs at no charge.

## 10. Changes

Scope, timeline or fee change only by a signed change order under section 11 of the Master Services Agreement.

## Signatures

| | Alimi | {{Client}} |
| --- | --- | --- |
| Name | {{Alimi Signatory}} | {{Client Signatory}} |
| Title | | {{Client Title}} |
| Date | | |
