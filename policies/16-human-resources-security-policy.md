---
id: POL-16
slug: human-resources-security-policy
title: Human Resources Security Policy
version: "1.0"
status: template
owner_role: "{{HR Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: employees, contractors, interns and temporary staff of {{Company}}, from the job offer to after they leave
requirements:
  soc2: [CC1.1, CC1.3, CC1.4, CC1.5, CC2.2, CC6.2, CC6.3]
  iso27001: ["7.2", "7.3", "A.5.11", "A.5.18", "A.6.1", "A.6.2", "A.6.3", "A.6.4", "A.6.5", "A.6.6"]
  iso42001: ["7.2", "7.3", "A.4.6"]
  hipaa: ["164.308(a)(3)", "164.308(a)(5)"]
  insurer: [training]
related: [POL-02, POL-03, POL-05, POL-13, POL-18]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Human Resources Security Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-16 |
| Version | 1.0 |
| Owner | {{HR Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Most security incidents at small companies begin with a person: someone was never told the rules, someone kept access after changing jobs, someone left and took the customer list, someone was fooled because no one had shown them what a scam looks like. This policy covers the people side of security from the first conversation with a candidate to the months after someone leaves, so that staff know what is expected, have the skills to meet it, and lose their access on the day they should.

## 2. Scope

Everyone who works for {{Company}} in any capacity: employees, contractors, interns, temporary staff and staff of suppliers who get company accounts. Where a managed service provider or agency supplies people, these rules apply to those people through the contract under the Vendor and Third-Party Risk Policy.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{HR Lead}} | Owns this policy, the hiring and leaving checklists, the training records and the disciplinary process. |
| Managers | Request and approve access for their people, confirm it at reviews, tell HR and IT the day someone's role changes or ends, and set the example. |
| {{Security Lead}} | Designs the training and awareness program, reviews joiner and leaver records, runs phishing simulations. |
| {{IT Lead}} or managed service provider | Creates and removes accounts and devices on the dates HR gives. |
| {{CEO}} | Demonstrates that security and honesty are part of how the company works, and acts on breaches at any level. |
| Everyone | Completes training, follows the policies, reports concerns. |

## 4. Policy statements

### 4.1 Before someone starts

1. Each role has a short written description of what it does and what information it needs, so that access can be set to the role rather than to the person. Roles that administer systems, handle money, or see regulated data are marked as sensitive.
2. **[HR or legal review]** Candidates for any role are checked before the offer is final: identity, right to work, the employment history and qualifications on the CV, and references. Candidates for sensitive roles get the additional checks the law allows and the role justifies (such as a criminal background check through a compliant provider, with the candidate's consent). Checks are proportionate, consistent between candidates, and the results are kept confidential and only as long as needed.
3. **[HR or legal review]** Every employment contract and contractor agreement includes confidentiality and intellectual property terms, a requirement to follow the company's security policies, the right to monitor company systems within the law, and the duties that continue after leaving. Confidentiality agreements are signed before access to confidential information is given.

### 4.2 Starting

4. New starters receive the Information Security Policy, the Acceptable Use Policy and the policies for their role on their first day and acknowledge them in writing (or electronically, with a record) before receiving credentials. The acknowledgement is repeated yearly and whenever a policy changes materially.
5. Access is requested by the manager and set up under the Access Control Policy to the role's needs, with multi-factor authentication registered before the first login. Devices are issued under the Asset Management Policy and recorded against the person.
6. Security induction in the first week covers how to spot and report phishing and payment fraud, how to report an incident, how to handle company data and devices, password manager setup, and who to ask. Nobody handles regulated data or sensitive systems until they have done it.

### 4.3 During employment

7. Everyone completes security awareness training within 30 days of starting and at least yearly after that, with short refreshers during the year on the current scams. Training covers phishing and business email compromise, malware and ransomware, passwords and multi-factor authentication, safe use of email and sharing, working remotely, physical security, recognising and reporting incidents, and the basics of privacy. Completion is recorded by {{HR Lead}} and reported to {{CEO}} quarterly; the insurer and customers may ask for the completion rate.
8. Staff in sensitive roles receive training specific to the role: administrators on secure configuration and logging, finance staff on payment verification, developers on secure coding, anyone handling health data on the privacy rules, anyone using or building AI systems on the AI policies. Where a role needs a skill the company does not have, {{HR Lead}} and the manager arrange training, mentoring or a hire, and the decision is recorded.
9. Phishing simulations run at least quarterly. Results guide training; individuals who are caught get a short lesson, not a punishment, and are never named to colleagues. Repeated failures lead to coaching with the manager.
10. Managers review their people's access at least every six months and whenever a role changes. A change of role is treated as a leaver from the old role and a joiner to the new one: old access is removed, not added to.
11. **[HR or legal review]** Breaches of security policies are handled through the company's disciplinary process, which is written down, applied consistently regardless of seniority, proportionate to intent and harm, and documented. Outcomes range from a conversation and retraining to dismissal and referral to the authorities for deliberate or criminal acts. The process is explained to staff before it is ever needed.
12. The company expects honesty and ethical conduct and says so, in the Acceptable Use Policy, at induction and in performance reviews. Security responsibilities are part of job descriptions and reviews so that people are accountable for them. Staff can raise concerns about security, privacy or the use of AI systems to {{Security Lead}}, {{HR Lead}} or {{CEO}} without fear of retaliation, and anonymously where the company provides a channel.
13. The company keeps a record of who is competent for which sensitive task, including the people who design, operate or oversee AI systems, so that gaps are visible when someone leaves or a system is introduced.

### 4.4 Remote work and working hours

14. Staff working outside the office follow the Remote Work and Personal Devices Policy. Managers consider the extra risks of isolation, home environments and personal devices when assigning sensitive work.

### 4.5 Leaving or changing role

15. {{HR Lead}} tells {{IT Lead}} and {{Security Lead}} of every departure as soon as it is known and no later than the last working day, including the exact time access should end. For an involuntary departure, access ends at the moment the person is told, and the manager and HR plan the conversation with IT in advance.
16. The leaver checklist is completed within one business day of departure: all accounts disabled and later deleted under the Access Control Policy; multi-factor devices and sessions revoked; shared passwords the person knew changed; mailbox and files transferred to the manager; devices, keys, badges and cards returned and checked under the Asset Management Policy; access by the person to any supplier systems removed; and the person reminded in writing of their continuing confidentiality duties. {{HR Lead}} signs off the checklist and keeps it.
17. {{Security Lead}} compares the HR leaver list with active accounts every month; any account that outlived its owner is treated as an incident and investigated.

## 5. Exceptions

Follow the Information Security Policy. Deferring training for someone in a sensitive role, or giving access before the acknowledgement is signed, needs {{HR Lead}}'s written agreement with a date to resolve.

## 6. Enforcement

Managers who do not report leavers or role changes, or whose teams do not complete training, are accountable to {{CEO}}. Breaches by staff follow statement 11.

## 7. Review

{{HR Lead}} and {{Security Lead}} review this policy yearly, after any incident involving a person's access or conduct, and when employment law or the company's structure changes.

## 8. Related documents

POL-02 Acceptable Use · POL-03 Access Control · POL-05 Asset Management · POL-13 Incident Response · POL-18 Remote Work and Personal Devices · POL-22 AI Acceptable Use · the joiner and leaver checklists · the training plan and records · the disciplinary process.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{HR Lead}} |
