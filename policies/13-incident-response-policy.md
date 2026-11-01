---
id: POL-13
slug: incident-response-policy
title: Incident Response Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: everyone who works for {{Company}}, every system and account it uses, and every supplier that handles its data
requirements:
  soc2: [CC2.2, CC2.3, CC7.3, CC7.4, CC7.5]
  iso27001: ["A.5.5", "A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28", "A.6.8"]
  iso42001: ["A.8.4"]
  hipaa: ["164.308(a)(6)"]
  insurer: [incident_response]
related: [POL-10, POL-11, POL-12, POL-14, POL-21, POL-23]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Incident Response Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-13 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Something will eventually go wrong: a staff member clicks a link, a laptop is left in a taxi, an invoice arrives with new bank details, a supplier is breached. The difference between a bad week and a company-ending event is how fast the problem is noticed, who gets told, and whether the first hour is spent on the right things. This policy sets those rules so that nobody has to invent them under pressure. It is also what the cyber insurer, customers and auditors mean when they ask whether {{Company}} has an incident response plan.

## 2. Scope

Any event that threatens the confidentiality, integrity or availability of {{Company}}'s information or systems, whether it happens on company equipment, a personal device used for work, a cloud service, or at a supplier. Incidents involving personal data also follow the Privacy and Data Protection Policy; incidents involving an AI tool also involve {{AI Lead}} under the AI Governance Policy. Keeping the business running during a long disruption is the Business Continuity and Disaster Recovery Policy.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| Everyone | Reports anything suspicious at once, follows instructions during an incident, does not investigate on their own or talk about it outside the company. |
| {{Security Lead}} | Incident lead: triages reports, runs the response, keeps the incident log, decides when an event is an incident, runs the review afterwards. |
| {{CEO}} | Declares a major incident, approves spending and outside help, decides on notifications with counsel, speaks for the company. |
| {{IT Lead}} or managed service provider | Executes technical containment and recovery, preserves logs and evidence. |
| {{Privacy Lead}} | Decides whether personal data is involved and which notice obligations apply. |
| {{HR Lead}} | Handles incidents that involve staff conduct, and staff communication during a major incident. |
| {{Finance Lead}} | Handles payment fraud with the bank, including recall requests. |

## 4. Policy statements

### 4.1 Reporting

1. Everyone reports a suspected incident immediately, by the channel named in the response plan (a phone number and a dedicated email or chat channel that does not depend on the system that may be compromised). Reporting early and being wrong is welcome; staying quiet is the only mistake. Nobody is disciplined for reporting an incident they caused by honest error.
2. Things that must be reported include: a phishing email that was clicked or answered, a password typed into an unexpected page, a multi-factor prompt that was not requested, a lost or stolen device, an email sent to the wrong recipient, a request to change bank or payment details, a ransom note or files that will not open, an unknown app granted access to an account, a supplier reporting a breach, and any sign that an outsider has read or changed company data.
3. Suppliers that process {{Company}} data must report incidents affecting it within the time their contract sets (24 hours is the target) to the same channel, under the Vendor and Third-Party Risk Policy.

### 4.2 Triage and severity

4. {{Security Lead}} looks at every report within one business hour during the working day and within four hours outside it, decides whether it is an incident, assigns a severity, and opens an entry in the incident log. The log records: date and time reported and detected, reporter, what happened, systems and data involved, severity, actions taken with times, people involved, notifications made, and the closing summary. The log is kept for at least six years.
5. Severity sets the pace:

| Severity | Examples | First response | Who is told |
| --- | --- | --- | --- |
| S1 Critical | Ransomware, confirmed account takeover of an administrator, confirmed theft of customer or personal data, fraudulent payment sent | Immediately, around the clock | {{CEO}} at once, insurer within 24 hours |
| S2 High | Compromised user account with no confirmed data loss, malware on a device, supplier breach involving our data, sensitive email sent outside | Within 2 hours | {{CEO}} the same day |
| S3 Medium | Phishing clicked with no credentials entered, lost encrypted device, policy violation with limited exposure | Within 1 business day | Weekly summary to {{CEO}} |
| S4 Low | Blocked phishing, scanner finding, near miss | Within 5 business days | Monthly metrics |

### 4.3 Containment, evidence and recovery

6. Containment comes before full understanding when harm is ongoing. Standard first moves are: disable the account and revoke all its sessions and tokens, reset the password and re-register multi-factor authentication, isolate the device from the network (do not switch it off), block the sender or domain, remove the malicious mailbox rule or app consent, and for payment fraud call the bank immediately to recall the transfer. {{IT Lead}} may take these steps without waiting for approval and reports them to {{Security Lead}}.
7. Evidence is preserved before anything is wiped or rebuilt: export the relevant sign-in, audit and mail logs; screenshot the suspicious message, rule or consent; note who handled what and when; keep the original device image where the incident may lead to a claim, a dispute or a prosecution. Evidence is stored in a restricted folder and handled by as few people as possible.
8. Eradication removes the cause (the malware, the backdoor rule, the stale credential, the unpatched flaw), and recovery restores systems and data under the Backup and Recovery Policy. Every credential the attacker could have seen is changed, including service accounts, API keys and shared passwords, before the system is declared clean.
9. Payment fraud and business email compromise follow the payment verification procedure: the bank's fraud line is called within hours because recall windows are short, the counterparty is called on a known number, and the fraud is reported to law enforcement (in the United States, the FBI's Internet Crime Complaint Center) and to the insurer.

### 4.4 Communication and notification

10. During an incident {{Security Lead}} gives short, factual updates to {{CEO}} and the people who need to act. Staff are told what to do, not the full story, until the review is done. Nobody discusses an incident on social media, with the press, or with customers unless {{CEO}} has asked them to.
11. **[HR or legal review]** Outside notifications are decided by {{CEO}} with legal counsel and {{Privacy Lead}}, and recorded in the log with date, recipient and content. The list of possible duties includes: the cyber insurer (within the deadline in the policy, and before engaging outside forensics or lawyers, because the insurer usually requires its own panel); customers and partners under contract; individuals and regulators under breach notification laws, including the Massachusetts data security regulations (201 CMR 17.00 and chapter 93H), the HIPAA Breach Notification Rule when protected health information is involved, and the GDPR's 72-hour rule when EU residents' data is involved; and law enforcement. Notifications are honest, timely and do not speculate about cause.
12. {{Security Lead}} keeps a contact list of authorities and helpers, checked every six months: the insurer's incident hotline and claim number, legal counsel, a forensics firm acceptable to the insurer, the bank's fraud line, local police and the FBI field office, the state Attorney General's breach notification contact, the relevant data protection authority if EU data is held, and the account managers at critical cloud providers.
13. When an incident involves an AI system (for example, a tool that exposed data or produced harmful output that reached a customer), {{AI Lead}} joins the response, and people affected by the AI system's behaviour are informed in the same way as for any other incident.

### 4.5 Learning from incidents

14. Every S1 and S2 incident, and any S3 incident {{Security Lead}} chooses, gets a written review within ten business days of closing: timeline, root cause, what detection and response did well, what did not, and actions with owners and dates. Actions are tracked to completion and reported to {{CEO}}. Patterns across S3 and S4 events are reviewed quarterly.
15. Lessons feed back into the other policies, the checks run by the security tooling, the training programme and the risk register. Incident metrics (count by severity, time to detect, time to contain, overdue actions) go to {{CEO}} quarterly.
16. The response plan is exercised at least once a year with a tabletop scenario (ransomware, account takeover and payment fraud rotate), and whenever the plan or the team changes significantly. New staff are told how to report an incident during their first week.

## 5. Exceptions

There are no exceptions to the duty to report. Deviations from the response steps during a live incident are decided by {{Security Lead}} or {{CEO}} and written in the log with the reason.

## 6. Enforcement

Hiding an incident, destroying evidence, or talking about an incident outside the company without permission is a serious breach of this policy, handled by {{HR Lead}} under the Acceptable Use Policy. Honest mistakes that are reported promptly are treated as training needs, not misconduct.

## 7. Review

{{Security Lead}} reviews this policy and the response plan every year, after every S1 or S2 incident, after every exercise, and when the insurer, a customer contract or the law changes the notification duties.

## 8. Related documents

POL-10 Logging and Monitoring · POL-11 Backup and Recovery · POL-12 Business Continuity and Disaster Recovery · POL-14 Vendor and Third-Party Risk · POL-21 Privacy and Data Protection · POL-23 AI Governance · the incident response plan and contact list · the payment verification procedure.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
