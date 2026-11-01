---
id: POL-11
slug: backup-and-recovery-policy
title: Backup and Recovery Policy
version: "1.0"
status: template
owner_role: "{{IT Lead}}"
approver_role: "{{Security Lead}}"
review_cycle: annual
applies_to: all data and systems {{Company}} would need to continue operating or meet its obligations
requirements:
  soc2: [A1.2, A1.3, CC7.5]
  iso27001: ["A.8.13", "A.8.14"]
  iso42001: []
  hipaa: ["164.308(a)(7)", "164.310(d)(1)"]
  insurer: [backups]
related: [POL-07, POL-12, POL-13, POL-20]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Backup and Recovery Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-11 |
| Version | 1.0 |
| Owner | {{IT Lead}} |
| Approved by | {{Security Lead}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Ransomware, a deleted mailbox, a failed migration or a vendor outage are survivable if there is a copy of the data that the attacker could not reach and that someone has actually restored before. This policy sets what is backed up, how often, where, how the copies are protected and how restores are tested. It gives the insurer the answer to "are backups immutable or offline and restore-tested quarterly?"

## 2. Scope

Data in the Microsoft 365 or Google Workspace tenant (mail, files, chat, sites); line-of-business applications and databases; servers and cloud infrastructure; configuration of identity, security tools and network devices; source code; and keys and secrets. Laptops are not a primary data store: work files live in company cloud storage, which is backed up.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{IT Lead}} or managed service provider | Runs the backups, monitors them daily, performs and records restore tests. |
| {{Security Lead}} | Approves the policy and the recovery objectives, reviews test records quarterly, confirms separation of backup access. |
| System and data owners | State what must be kept and for how long, and take part in restore tests of their systems. |

## 4. Policy statements

### 4.1 What is backed up and the recovery objectives

1. Every system in scope has a documented recovery point objective (RPO: how much data can be lost, measured in time) and recovery time objective (RTO: how long it may be unavailable), set by the owner and approved by {{Security Lead}} as part of the Business Continuity and Disaster Recovery Policy. Defaults where the owner has not set stricter ones:

| System | RPO | RTO | Backup frequency |
| --- | --- | --- | --- |
| Email, files, chat (workspace tenant) | 24 hours | 1 business day | Daily, by a third-party backup service independent of the tenant |
| Core business applications and databases | 24 hours (4 hours for transactional systems) | 1 business day | Daily, plus transaction logs where applicable |
| Identity and security tool configuration | 7 days | 1 business day | Weekly export, and after every significant change |
| Source code | 24 hours | 4 hours | Mirrored to a second location daily |
| Servers and infrastructure | 24 hours | 2 business days | Daily image or snapshot, infrastructure defined as code where possible |

2. The vendor's own resilience is not a backup. Platform retention features (recycle bins, version history, litigation hold) help with small mistakes but do not protect against account takeover, malicious deletion by an administrator or the vendor's own failure; a separate backup copy does.

### 4.2 The 3-2-1 rule and immutability

3. At least **three copies** of important data exist (the live data and two backups), on **two different types of storage or services**, with **one copy offline or immutable**: it cannot be changed or deleted by anyone, including an administrator whose account has been taken over, until its retention period ends.
4. Backup copies are stored in a different account, tenant or provider from the systems they protect, with their own credentials, so that an attacker inside the production environment cannot reach them.
5. Backups are encrypted at rest and in transit under the Cryptography and Key Management Policy, and the keys to read them are held separately from the backups and the production environment.

### 4.3 Retention

6. Daily backups are kept for at least 30 days, weekly for at least 90 days and monthly for at least 12 months, unless the Data Retention and Disposal Policy or a contract requires longer. Backups of data that must be deleted under a retention rule or a privacy request are allowed to age out on this schedule and are not restored except under legal hold. **[HR or legal review]**

### 4.4 Access to backups

7. Access to the backup platform is limited to {{IT Lead}}, a named deputy and the break-glass account, uses phishing-resistant multi-factor authentication, and is logged. Deleting backups or shortening retention requires two people or a time-delayed deletion feature.

### 4.5 Monitoring

8. Backup jobs are monitored every business day. A failed or missed job is investigated the same day and fixed before the next cycle; two consecutive failures of the same job are reported to {{Security Lead}}.
9. Backup coverage is reconciled against the asset inventory quarterly so that new systems are not left out.

### 4.6 Restore testing

10. A restore test is performed and recorded at least **quarterly**, rotating through the systems in scope so that every system is restored at least once a year. Tests include at least: a mailbox and a set of files from the workspace backup; a database or application restore to a test location; a configuration restore; and, once a year, a full recovery exercise of a critical system to measure the real RTO.
11. Each test records the date, the system, the backup used, the steps, the time taken, whether the data was complete and correct, and problems found. Problems become actions with owners and dates.
12. Restore procedures are written down in enough detail that a competent person who did not set the system up could follow them, and are stored where they are available even if the main systems are down.

### 4.7 Recovery in an incident

13. During a ransomware or destructive incident, restores are performed only after the Incident Response Policy's containment steps, onto clean systems, from a backup taken before the compromise, and the restored data is checked for malware before use.

## 5. Exceptions

Follow the Information Security Policy. A system with no backup or no immutable copy is an exception with a dated plan to fix it.

## 6. Enforcement

Backup failures that are not investigated and test schedules that are missed are reported to {{Security Lead}} and {{CEO}} and tracked as findings.

## 7. Review

{{IT Lead}} reviews this policy annually, after every restore test that found a problem, and when systems are added or retired.

## 8. Related documents

POL-05 Asset Management · POL-07 Cryptography and Key Management · POL-12 Business Continuity and Disaster Recovery · POL-13 Incident Response · POL-20 Data Retention and Disposal.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{IT Lead}} |
