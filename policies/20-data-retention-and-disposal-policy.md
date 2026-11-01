---
id: POL-20
slug: data-retention-and-disposal-policy
title: Data Retention and Disposal Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: all records and data {{Company}} holds, in any format, on any medium, including copies held by suppliers
requirements:
  soc2: [C1.2, CC6.5, P4.2, P4.3]
  iso27001: ["A.5.31", "A.5.33", "A.7.10", "A.7.14", "A.8.10"]
  iso42001: []
  hipaa: ["164.310(d)(1)", "164.316"]
  insurer: []
related: [POL-05, POL-06, POL-11, POL-17, POL-21]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Data Retention and Disposal Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-20 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Data that no longer serves a purpose is pure risk: it can still be stolen, still be demanded in a lawsuit, still be subject to a privacy complaint, and still cost money to store and protect. Data that is deleted too early can breach a law, a contract or the company's own needs. This policy sets how long {{Company}} keeps each kind of record, how it decides, and how data and the equipment that held it are destroyed so that they cannot be recovered.

## 2. Scope

Every record and data set {{Company}} creates or receives, in every format (documents, email, chat, databases, backups, logs, paper, recordings) and on every medium (cloud services, laptops, phones, servers, removable media, paper), including copies held by suppliers on the company's behalf.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns this policy and the retention schedule, oversees disposal, keeps the disposal records. |
| {{Privacy Lead}} | Sets the retention periods for personal data and handles deletion requests. |
| {{Finance Lead}} | Sets the retention periods for financial, tax and contract records. |
| {{HR Lead}} | Sets the retention periods for employment records. |
| Record owners (department heads, system owners) | Apply the schedule in their systems and review what they hold yearly. |
| {{IT Lead}} or managed service provider | Configures retention in the systems, performs wiping and destruction, keeps the certificates. |
| {{CEO}} | Approves the schedule and any legal hold with counsel. |

## 4. Policy statements

### 4.1 The retention schedule

1. {{Security Lead}} keeps a retention schedule listing each category of record, the system or place it lives, the owner, how long it is kept and from what event (end of contract, end of tax year, departure of the employee), the reason (law, contract, business need), and how it is disposed of at the end. The schedule is approved by {{CEO}} and reviewed yearly.
2. **[HR or legal review]** Periods are set by the longest applicable rule. Typical starting points for a US company, to be confirmed by counsel and the company's accountant: tax and accounting records seven years; contracts and the correspondence that interprets them seven years after they end; employment records seven years after departure, with payroll and benefits records longer where the law requires; security policies, risk assessments, incident records, access reviews and training records six years (the HIPAA minimum, which also suits SOC 2 and ISO 27001 audits); security logs at least one year under the Logging and Monitoring Policy; customer data for the length of the contract plus the period the contract specifies, then deleted or returned; marketing and prospect data while there is a relationship and for no more than two years of inactivity; recruitment records for unsuccessful candidates one year.
3. Personal data is kept no longer than the purpose it was collected for requires, under the Privacy and Data Protection Policy, and the schedule says when each category is deleted or anonymised. Where the law gives individuals the right to deletion, requests are handled under that policy and override the schedule unless a legal reason to keep the data applies.
4. Records are kept in the system of record named in the schedule, not in personal drives, email attachments or chat. Where retention can be automated (mailbox retention policies, document library rules, database jobs, log store lifecycle rules), it is, and {{IT Lead}} documents the settings. Backups under the Backup and Recovery Policy follow their own cycle and are not used as an archive; data deleted from a system disappears from backups when the backup cycle expires.
5. Each record owner reviews what their systems hold once a year, deletes what is past its period, and confirms the review to {{Security Lead}}. Systems and suppliers are told which categories they hold so that they can apply the periods.

### 4.2 Legal holds

6. **[HR or legal review]** When litigation, an investigation, an audit or a regulator's request is reasonably expected, {{CEO}} with counsel issues a legal hold naming the records, the people and the systems involved. Deletion of those records stops immediately, including automated deletion; the people involved are told in writing what to preserve; and the hold is lifted in writing when it ends. Legal holds are logged with their dates.

### 4.3 Disposal of data

7. When a record reaches the end of its period and is not under hold, it is disposed of in the way its classification under the Data Classification and Handling Policy requires: confidential and regulated data is deleted so that it cannot be recovered by ordinary means (emptied from recycle bins and second-stage recycle bins, purged from retention holds, removed from search indexes), and the supplier is instructed to delete copies and confirm. Internal data is deleted normally. Public data needs no special care.
8. Paper records containing confidential or personal data are shredded with a cross-cut shredder or placed in locked shred bins emptied by a disposal supplier that provides a certificate of destruction. They are never put in ordinary waste or recycling.
9. When a supplier relationship ends, the data it held is returned or deleted under the Vendor and Third-Party Risk Policy and the confirmation is kept in the disposal record.

### 4.4 Disposal of equipment and media

10. Laptops, desktops, servers, phones, removable media and any device with storage (printers and copiers included) are wiped before they are reused, returned to a lessor, sold, donated or recycled. Encrypted devices are wiped by destroying the encryption key and resetting; unencrypted storage is overwritten with a recognised method or physically destroyed. Media that cannot be wiped reliably (failed drives, old optical media) is physically destroyed.
11. Disposal of equipment is recorded in the asset register under the Asset Management Policy with the date, the method, the person who did it and, where a disposal supplier is used, the certificate of destruction. Equipment leaving the premises for repair follows the Physical and Environmental Security Policy.
12. Removable media is tracked while in use under the Asset Management Policy, stored locked away, carried in hand luggage, and destroyed when no longer needed or when the data on it is past its period.
13. Where protected health information is involved, the movement of hardware and media into, out of and within the company is logged, and the records of disposal and media reuse are kept for six years.

### 4.5 Records of this policy

14. The disposal log (what was destroyed, when, how, by whom, with any certificate) and the retention schedule are kept for at least six years and are available to auditors, insurers and customers as evidence that data does not linger.
15. The policies, procedures and records that document {{Company}}'s security and privacy programme are themselves retained for at least six years from their creation or last effective date, in the controlled document store under the Information Security Policy.

## 5. Exceptions

Follow the Information Security Policy. Keeping a category beyond its period for a business reason needs the record owner's written justification and {{Privacy Lead}}'s agreement where personal data is involved; it is recorded in the schedule with a review date.

## 6. Enforcement

Record owners who do not complete the yearly review, or who keep data outside the system of record, are escalated to {{CEO}}. Destroying records under a legal hold, or disposing of equipment without wiping it, is a serious breach handled under the Acceptable Use Policy and reported as an incident.

## 7. Review

{{Security Lead}} reviews this policy and the schedule yearly with {{Privacy Lead}}, {{Finance Lead}} and {{HR Lead}}, and whenever a law, a contract or a new category of data changes the periods.

## 8. Related documents

POL-05 Asset Management · POL-06 Data Classification and Handling · POL-10 Logging and Monitoring · POL-11 Backup and Recovery · POL-14 Vendor and Third-Party Risk · POL-17 Physical and Environmental Security · POL-21 Privacy and Data Protection · the retention schedule · the disposal log.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
