---
id: POL-12
slug: business-continuity-and-disaster-recovery-policy
title: Business Continuity and Disaster Recovery Policy
version: "1.0"
status: template
owner_role: "{{CEO}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: the processes, people, systems and suppliers {{Company}} needs to keep operating
requirements:
  soc2: [A1.1, A1.2, A1.3, CC7.5, CC9.1]
  iso27001: ["A.5.29", "A.5.30", "A.7.5", "A.7.11", "A.8.6", "A.8.14"]
  iso42001: []
  hipaa: ["164.308(a)(7)", "164.310(a)(1)"]
  insurer: [backups, incident_response]
related: [POL-11, POL-13, POL-14, POL-15]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Business Continuity and Disaster Recovery Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-12 |
| Version | 1.0 |
| Owner | {{CEO}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

A company of {{Company}}'s size does not survive a long outage on momentum. This policy decides in advance what must keep running, how long each thing can be down, and what happens when the office, the email system, a key supplier or a key person is suddenly unavailable. Security is kept during the disruption, not suspended until it ends.

## 2. Scope

{{Company}}'s critical business processes, the people and skills behind them, the systems and data they use (including cloud services), the office and remote workplaces, and the suppliers they depend on. The Backup and Recovery Policy covers the data copies; the Incident Response Policy covers the security investigation; this policy covers keeping the business going.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{CEO}} | Owns the plan, declares a disruption, makes the calls on priorities and spending, speaks for the company. |
| {{Security Lead}} | Maintains this policy and the plan, runs the annual exercise, keeps security working during disruption. |
| {{IT Lead}} or managed service provider | Owns the technical recovery steps and the systems' redundancy. |
| Process owners | Know how to run their process in degraded mode and keep their part of the plan current. |
| {{HR Lead}} | Owns staff communication and welfare during a disruption. |

## 4. Policy statements

### 4.1 Knowing what matters

1. {{Security Lead}} keeps a business impact analysis, reviewed yearly, listing each critical process (for example: serving customers, taking payments, paying staff, communicating), the systems, people, data and suppliers it needs, the maximum time it can be down before serious harm (the recovery time objective), the data it can afford to lose (the recovery point objective) and the manual workaround if any.
2. Recovery objectives in the Backup and Recovery Policy are derived from this analysis; the two documents are kept consistent.

### 4.2 Scenarios planned for

3. The continuity plan has a short, tested playbook for at least these situations: loss of the email and collaboration tenant or identity provider (including account takeover); ransomware across devices; loss of the office or of power and internet there; loss of a critical supplier or cloud service; unavailability of a key person (illness, departure, travel); and a regional event that affects staff at home.

### 4.3 Reducing the chance and the impact

4. Critical systems have the redundancy their recovery objectives need: cloud services with a published availability commitment, no single server or device that holds the only copy of anything, and at least two people able to administer each critical system.
5. Capacity of critical systems (storage, licences, bandwidth, people) is reviewed quarterly against growth so that running out does not become the disruption.
6. The office has protection proportional to what is in it: uninterruptible power for network equipment, surge protection, smoke detection, no servers in flood-prone or unsecured spaces, and spare internet connectivity (a second line or mobile hotspots) if the office matters to operations. Physical measures are detailed in the Physical and Environmental Security Policy.
7. Suppliers that a critical process depends on are identified in the vendor register with their continuity commitments and an alternative where one exists, under the Vendor and Third-Party Risk Policy.

### 4.4 When disruption happens

8. {{CEO}} (or the deputy named in the plan) declares a disruption and activates the plan. The first hour is about safety of people, then communication, then recovery in the order of the business impact analysis.
9. The plan lists the crisis team, with deputies, and the out-of-band ways to reach them (personal phone numbers, a messaging app that does not depend on the company tenant), stored where everyone on the team can reach it offline.
10. Staff are told what to do and what not to do within two hours, through the channel the plan names. Customers, suppliers, the insurer and regulators are informed by the people the plan names, with messages that are accurate and do not speculate. **[HR or legal review]** Legal notice obligations follow the Incident Response Policy.
11. Security controls stay in force during disruption. Temporary workarounds (a personal email account, a shared password, disabling multi-factor authentication) are not allowed unless {{CEO}} and {{Security Lead}} approve a specific, time-limited exception, which is logged and reversed when the disruption ends. Attackers watch for exactly this moment.
12. Alternate work arrangements (working from home, a temporary office, a coworking space) follow the Remote Work and Personal Devices Policy.

### 4.5 Recovery and return

13. Systems are recovered in the order the business impact analysis sets, from the backups and procedures in the Backup and Recovery Policy, and verified with the process owner before being declared back.
14. The crisis team keeps a timeline of decisions and actions. After return to normal, {{Security Lead}} runs a review within two weeks: what happened, what worked, what did not, and actions with owners and dates.

### 4.6 Exercising the plan

15. At least once a year the crisis team runs a tabletop exercise against one of the scenarios in 4.2, and {{IT Lead}} runs a technical recovery exercise of a critical system. The scenario rotates. Results and improvements are recorded and reported to {{CEO}}; insurers and customers may ask to see the date and the summary.
16. Contact lists, deputies and procedures are checked quarterly and after staff changes.

## 5. Exceptions

Follow the Information Security Policy. A critical process without a workaround or a critical system without redundancy is a recorded risk with a plan and a date, accepted by {{CEO}}.

## 6. Enforcement

Process owners who do not keep their part of the plan current, or skip the exercise, are escalated to {{CEO}}. Security exceptions taken during disruption without approval are treated as incidents.

## 7. Review

{{Security Lead}} reviews this policy and the plan annually, after every exercise and every real disruption, and when the business changes (new office, new critical supplier, new product).

## 8. Related documents

POL-11 Backup and Recovery · POL-13 Incident Response · POL-14 Vendor and Third-Party Risk · POL-15 Risk Management · POL-17 Physical and Environmental Security · POL-18 Remote Work and Personal Devices.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{Security Lead}} |
