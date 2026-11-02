---
id: POL-06
slug: data-classification-and-handling-policy
title: Data Classification and Handling Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: all information {{Company}} creates, receives, stores or transmits, in any form
requirements:
  soc2: [C1.1, C1.2, CC6.1, CC6.7]
  iso27001: ["A.5.12", "A.5.13", "A.5.14", "A.8.11", "A.8.12"]
  iso42001: ["A.7.3"]
  hipaa: ["164.312(c)(1)", "164.312(e)(1)"]
  insurer: [data_sharing]
related: [POL-02, POL-07, POL-20, POL-21, POL-22]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Data Classification and Handling Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-06 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Not all information needs the same protection. This policy sorts {{Company}}'s information into four levels and says, for each level, how it may be stored, shared, sent and destroyed. It is what makes "is external file sharing controlled?" answerable with a yes.

## 2. Scope

All information that {{Company}} creates, receives, stores or transmits, in any form: documents, email, chat, databases, backups, printouts, recordings and what is typed into an AI tool. It applies to everyone in scope of the Acceptable Use Policy.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| Information owners | Classify the information their function produces and decide who may access it. |
| {{Security Lead}} | Owns the scheme, configures sharing and data loss prevention settings with IT, and audits sharing quarterly. |
| {{IT Lead}} or managed service provider | Implements the technical handling rules (sharing limits, encryption, labels, retention). |
| Everyone | Labels, handles and shares information according to its level, and asks when unsure. |

## 4. Policy statements

### 4.1 The four levels

| Level | What it is | Examples | If it leaked |
| --- | --- | --- | --- |
| **Public** | Approved for anyone to see | Website copy, published prices, marketing material | No harm |
| **Internal** | Everyday business information for staff | Internal procedures, meeting notes, org charts, most email | Embarrassment, minor cost |
| **Confidential** | Would harm {{Company}}, a customer or a person if disclosed | Customer data and contracts, financials, employee records, source code, security findings, personal data | Loss of customers, legal exposure, fines |
| **Restricted** | Would cause serious harm; the smallest set | Protected health information, payment card data, credentials and keys, M&A plans, personal data of a sensitive kind | Regulatory action, large liability, serious harm to people |

1. Information is **Internal by default**. The owner raises it to Confidential or Restricted when it fits those rows, and lowers it to Public only through an approved publication.
2. A set of information takes the highest level of anything in it. A spreadsheet with one column of card numbers is Restricted.
3. Classification does not expire on its own; owners review it when the information is reused or at the retention review.

### 4.2 Labelling

4. Confidential and Restricted documents and emails carry the label, using the platform's sensitivity labels where available or the word in the header or subject line otherwise. Labels drive the technical handling rules in the next sections.
5. Information received from customers and partners is handled at the level their contract or label says, and at Confidential at minimum.

### 4.3 Handling rules

| Rule | Public | Internal | Confidential | Restricted |
| --- | --- | --- | --- | --- |
| Where it lives | Anywhere approved | Company cloud storage and systems | Company systems only, access by role | Named systems approved by {{Security Lead}}, access by named person |
| Sharing with staff | Open | Open | Need to know | Named individuals, logged |
| Sharing outside | Free | With a business reason | Named recipients, link expiry, no "anyone" links, NDA or contract in place | Only under contract, encrypted, approved by the owner, logged |
| Email | Yes | Yes | Yes to named recipients; encrypt attachments or use a secure link | Not by email unless encrypted end to end and approved |
| Encryption | Not required | At rest by platform default | At rest and in transit, always | At rest, in transit and, where possible, in use; keys per the Cryptography Policy |
| Personal devices | Yes | Managed apps only | Managed apps only, no local copies | Not permitted |
| Printing | Yes | Yes | Avoid; collect immediately, store locked, shred | Not permitted without {{Security Lead}} approval |
| AI tools | Yes | Approved tools | Approved enterprise tools with no-training terms only | Not permitted unless the tool is approved for Restricted data |
| Disposal | Delete | Delete | Secure deletion per the Retention and Disposal Policy | Secure deletion with record |

### 4.4 Sharing outside the company

6. External sharing from company cloud storage is limited by tenant setting to named people or allowlisted partner domains. Links to "anyone" are disabled, or, where a business need is approved, expire within 30 days and are reviewed monthly.
7. Automatic forwarding of company email to outside addresses is blocked at the tenant.
8. Before sending Confidential information to a new outside party, the sender checks that a contract or NDA covers it, under the Vendor and Third-Party Risk Policy.
9. Transfers of Restricted data use an encrypted channel agreed in writing with the recipient (secure file transfer, customer portal, or end-to-end encrypted mail), never consumer file-sharing services.
10. {{Security Lead}} reviews the external sharing report and the "shared with anyone" report from the workspace security scan at least quarterly and removes shares that no longer have a reason.

### 4.5 Data loss prevention and masking

11. Where the platform supports it, data loss prevention rules warn or block when card numbers, health identifiers, government IDs or credentials are shared outside the company or posted in chat.
12. Production Confidential and Restricted data is not copied into test, demo or training environments. Where realistic data is needed, it is masked or synthetic, as the Secure Development and Change Management Policy requires.
13. Data used to build or tune AI systems is acquired and recorded under the AI Governance Policy and handled at its classification.

### 4.6 Integrity

14. Confidential and Restricted records that must stay accurate (financial records, health information, contracts) are stored in systems with version history and access logging, so that unauthorised changes can be detected and reversed.

### 4.7 Special categories

15. Protected health information, payment card data and personal data covered by privacy law are Restricted or Confidential as the table says, and carry the additional obligations tracked under the Privacy and Data Protection Policy. **[HR or legal review]** Counsel confirms which categories apply to {{Company}}.

## 5. Exceptions

Follow the Information Security Policy. An exception that allows "anyone with the link" sharing or Restricted data outside approved systems needs {{Security Lead}} approval, an end date and a review.

## 6. Enforcement

Shares and copies that breach this policy are removed when found. Breaches follow the Human Resources Security Policy and, for contractors and vendors, their contracts.

## 7. Review

{{Security Lead}} reviews this policy annually and whenever a new data category, customer requirement or platform feature changes how information should be handled.

## 8. Related documents

POL-02 Acceptable Use · POL-07 Cryptography and Key Management · POL-08 Secure Development and Change Management · POL-14 Vendor and Third-Party Risk · POL-20 Data Retention and Disposal · POL-21 Privacy and Data Protection · POL-22 AI Acceptable Use · POL-23 AI Governance.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{Security Lead}} |
