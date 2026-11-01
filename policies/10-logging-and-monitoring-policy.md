---
id: POL-10
slug: logging-and-monitoring-policy
title: Logging and Monitoring Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: all systems that hold or move {{Company}} data, and the identity, email, endpoint and cloud platforms around them
requirements:
  soc2: [CC4.1, CC7.1, CC7.2, CC7.3]
  iso27001: ["A.6.8", "A.8.15", "A.8.16", "A.8.17"]
  iso42001: ["A.6.2.8"]
  hipaa: ["164.312(b)", "164.308(a)(1)"]
  insurer: [logging]
related: [POL-02, POL-03, POL-13, POL-19]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Logging and Monitoring Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-10 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

When something goes wrong, logs are how {{Company}} finds out what happened, how far it went and what to tell customers and the insurer. This policy says which logs are kept, for how long, how they are protected, and who looks at them. It answers "are audit logs enabled and retained for at least 90 days?" with specifics.

## 2. Scope

The identity provider (Microsoft Entra ID or Google Workspace), email, file storage and collaboration, endpoint detection and response, device management, cloud infrastructure, network equipment, business applications holding Confidential or Restricted data, security tools, and software {{Company}} builds, including AI systems.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns the policy, decides what is logged and alerted, reviews reports, leads investigations. |
| {{IT Lead}} or managed service provider | Turns logging on, forwards and retains logs, keeps clocks synchronised, maintains alerts. |
| System owners | Make sure their systems produce the logs in section 4.1 and keep them for the retention period. |
| Everyone | Reports anything unusual; does not attempt to disable or alter logs. |

## 4. Policy statements

### 4.1 What is logged

1. The following are logged with a timestamp, the account or system involved, the source (device or IP address), the action and the result:
   - sign-ins, including failures, multi-factor outcomes and sign-ins from new locations or devices;
   - administrator actions: changes to users, groups, roles, policies, mail flow, sharing settings, security tools and logging itself;
   - access to and changes in Confidential and Restricted data where the platform can record it (file access, sharing, downloads, exports, mailbox access by others);
   - email events: inbound and outbound mail flow, forwarding and inbox-rule creation, quarantine and phishing reports;
   - endpoint events from the detection and response tool, device enrolment and compliance changes;
   - security tool alerts, backup job results and restore operations;
   - application security events in software {{Company}} builds: authentication, authorisation failures, privileged actions, errors, and the inputs, outputs and decisions of AI systems to the extent the AI Governance Policy requires.
2. The audit log of the Microsoft 365 or Google Workspace tenant is turned on and never turned off. The workspace security scan confirms it quarterly.
3. Logs do not contain passwords, full card numbers, keys or other secrets. Personal data in logs is limited to what the purpose needs.

### 4.2 Retention

4. Security-relevant logs are kept for at least **12 months**, with at least the most recent **90 days** immediately searchable. Where the platform's own retention is shorter, logs are exported to a log store or the retention add-on is bought.
5. Logs needed for an investigation, a legal hold or an insurance claim are kept until {{Security Lead}} and counsel release them. **[HR or legal review]**

### 4.3 Protecting logs

6. Logs are stored where the people and systems being logged cannot change or delete them: a separate log store, an append-only configuration, or the platform's immutable audit service. Access to logs is by role, limited to {{Security Lead}}, {{IT Lead}} and named responders, and is itself logged.
7. Logging services are monitored; a log source that stops sending is alerted within one day.
8. All systems synchronise their clocks to a reliable time source and record timestamps in UTC or with the time zone, so events across systems line up.

### 4.4 Monitoring and alerting

9. Automated alerts are configured for events that need action the same day, at minimum: use of the break-glass account; new administrator or role assignment; changes to Conditional Access, multi-factor settings, mail-flow or forwarding rules; sign-ins from impossible locations or anonymising networks; a high-severity endpoint detection; disabling of a security tool or of logging; a failed backup; mass download or deletion of files; new OAuth application grants with mail or file access.
10. Alerts go to a channel that someone watches during business hours and, for high-severity endpoint and identity alerts, to an on-call person or a managed detection and response provider at all hours. {{Security Lead}} documents who that is.
11. {{Security Lead}} or a delegate reviews the following reports **weekly**: sign-in risk and failed sign-ins, new and changed admin roles, external sharing and new OAuth grants, endpoint detections, and quarantine and phishing reports; and **monthly**: the full audit log for admin actions, backup results and the log-source health check. Reviews are recorded with the date, the reviewer and any follow-up.
12. Anything that looks like a security event is handled under the Incident Response Policy. Reviewing logs and doing nothing with what they show is not monitoring.

### 4.5 Investigations and privacy

13. Logs are used to run the business securely, to investigate incidents and suspected policy breaches, and to meet legal duties. They are not used to monitor individuals' productivity or private life.
14. An investigation focused on a named person's activity needs the approval of {{CEO}} or {{HR Lead}} together with {{Security Lead}}, is limited to what the question needs, and is recorded. **[HR or legal review]** Counsel confirms the notice and approval requirements for each jurisdiction where {{Company}} employs people, and the monitoring notice in the Acceptable Use Policy is kept consistent with this section.

### 4.6 Evidence

15. During an incident, logs and other evidence are preserved under the Incident Response Policy before any clean-up, so that what happened can be established and, if needed, used in a legal or insurance process.

## 5. Exceptions

Follow the Information Security Policy. A system that cannot produce or export the logs in section 4.1 is an exception with a compensating control (restricted access, more frequent manual review) and a replacement date.

## 6. Enforcement

Turning off, altering or deleting logs without authorisation is a serious breach under the Human Resources Security Policy. Vendors who fail to provide contracted logs are handled under the Vendor and Third-Party Risk Policy.

## 7. Review

{{Security Lead}} reviews this policy annually, after every incident where logs were missing or insufficient, and when platforms add new log sources.

## 8. Related documents

POL-02 Acceptable Use · POL-03 Access Control · POL-11 Backup and Recovery · POL-13 Incident Response · POL-19 Network, Endpoint and Email Security · POL-23 AI Governance.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
