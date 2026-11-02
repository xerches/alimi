---
id: POL-01
slug: information-security-policy
title: Information Security Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: all staff, contractors, systems and data of {{Company}}
requirements:
  soc2: [CC1.1, CC1.2, CC1.3, CC1.5, CC2.1, CC2.2, CC2.3, CC4.1, CC4.2, CC5.1, CC5.2, CC5.3]
  iso27001: ["4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "6.2", "6.3", "7.1", "7.3", "7.4", "7.5.1", "7.5.2", "7.5.3", "8.1", "9.1", "9.2.1", "9.2.2", "9.3", "10.1", "10.2", "A.5.1", "A.5.2", "A.5.4", "A.5.5", "A.5.6", "A.5.31", "A.5.35", "A.5.36", "A.5.37", "A.8.34"]
  iso42001: ["A.2.3"]
  hipaa: ["164.308(a)(1)", "164.308(a)(2)", "164.308(a)(8)", "164.316"]
  insurer: []
related: [POL-02, POL-03, POL-13, POL-15, POL-16]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Information Security Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-01 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual, and after a major change or a serious incident |

## 1. Purpose

This policy states how {{Company}} protects the information it holds for its customers, its staff and itself. It is the top of the policy set: every other security policy in this library sits under it and follows its rules. It exists so that a customer, an insurer or an auditor can see, in one place, who is responsible for security, what we protect, and how we know the protections work.

## 2. Scope

This policy applies to everyone who works for or on behalf of {{Company}}: employees, contractors, temporary staff and interns. It covers all information {{Company}} creates, receives or processes, in any form, and every system that stores or moves that information, whether we run it, rent it as a cloud service or use it on a personal device under the Remote Work and Personal Devices Policy.

The information security management system (ISMS) described here covers {{Company}}'s business operations, its customer-facing services and the Microsoft 365 or Google Workspace tenant, laptops, cloud services and offices that support them. Exclusions, if any, are listed in the risk register and approved by {{CEO}}.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{CEO}} | Owns the security programme. Approves this policy, the risk acceptance criteria and any exception to a policy that carries high risk. Provides the budget and time the programme needs. |
| {{Security Lead}} | Runs the programme day to day: maintains the policies, the risk register and the asset inventory, coordinates incident response, reports to {{CEO}} at least quarterly, and is the named security contact for customers, insurers and authorities. This role may be held by an employee, a managed service provider or a fractional security lead. |
| {{IT Lead}} or managed service provider | Operates the systems to the standards in these policies and keeps the evidence that they do. |
| {{HR Lead}} | Owns the people parts: screening, onboarding, training records, offboarding and the disciplinary process. |
| Managers | Make sure their teams know and follow the policies, approve access requests for their staff, and report concerns. |
| Everyone | Follows the policies, completes training, protects the information they handle and reports security events without delay. |

## 4. Policy statements

### 4.1 Commitment and objectives

1. {{Company}} protects the confidentiality, integrity and availability of its information in proportion to the harm its loss would cause.
2. Leadership sets measurable security objectives each year (for example: multi-factor authentication on 100% of accounts, critical patches within 14 days, a restore test every quarter, an incident tabletop every year) and reviews progress against them at least quarterly.
3. Security requirements come from four sources, all tracked by {{Security Lead}}: the law and regulators, customer contracts, the cyber insurance policy, and our own risk assessment.

### 4.2 The policy set

4. The security policy set consists of this policy and the topic policies listed in section 8. Together they form the documented ISMS.
5. Each policy names an owner, a version, an approver and a review cycle. A policy takes effect when the approver signs it and it is published where staff can find it.
6. Where a policy conflicts with a law or a signed contract, the law or the contract wins and {{Security Lead}} updates the policy.

### 4.3 Risk-based decisions

7. {{Company}} keeps a risk register and runs the risk assessment described in the Risk Management Policy at least once a year and whenever something significant changes: a new system, a new customer type, a new office, an acquisition or a serious incident.
8. Controls are chosen to bring risks within the acceptance criteria approved by {{CEO}}. A risk left above the criteria is accepted in writing by {{CEO}}, with a date to revisit it.

### 4.4 Compliance with the law and with contracts

9. {{Security Lead}} keeps a list of the laws, regulations and contractual security obligations that apply to {{Company}} and the policy or control that meets each one. **[HR or legal review]** The list is confirmed by counsel when a new jurisdiction, customer type or data category is added.
10. Where {{Company}} handles protected health information, personal data of EU or UK residents, payment card data or other specially regulated data, the obligations and the named responsible person are recorded in that list.

### 4.5 Communication and awareness

11. Every new joiner reads this policy and the Acceptable Use Policy and confirms in writing that they will follow them before they get access to systems. Everyone re-confirms once a year.
12. {{Security Lead}} tells staff about relevant changes, new threats and lessons from incidents in plain language, at least quarterly.
13. Customers, vendors and partners are told about the security commitments that concern them, and about incidents that affect them, through the Incident Response Policy and the Vendor and Third-Party Risk Policy.

### 4.6 Documentation and procedures

14. Operating procedures that matter for security (how to onboard a user, how to restore from backup, how to respond to a phishing report) are written down, kept current and available to the people who perform them.
15. Policies, procedures and the records that show controls operate (access reviews, training logs, restore tests, risk reviews) are kept in a controlled location with version history, protected from unauthorised change, and retained for at least six years.

### 4.7 Checking that controls work

16. {{Security Lead}} measures the security objectives and reviews key control evidence at least quarterly, using the workspace security scan and the operational reports listed in the Logging and Monitoring Policy.
17. Once a year someone independent of day-to-day operations (an internal reviewer from another function, the fractional security lead or an outside firm) reviews the programme against this policy set and reports findings to {{CEO}}.
18. {{CEO}} and {{Security Lead}} hold a management review at least once a year covering: results of audits and reviews, incidents and near misses, status of risks and actions, changes in the business or the law, and whether the objectives and resources are still right. Decisions and actions are minuted.
19. Audit and testing activities on live systems are planned with the system owner so they do not disrupt the business.

### 4.8 Improvement

20. Findings from reviews, audits, incidents and near misses are logged as actions with an owner and a date. {{Security Lead}} tracks them to closure and looks for the underlying cause, not only the symptom.

### 4.9 Outside contacts

21. {{Security Lead}} keeps current contact details for the cyber insurer and its breach hotline, legal counsel, law enforcement (the FBI field office or the Internet Crime Complaint Center), relevant regulators, and the managed service provider, so no one has to search for them during an incident.
22. {{Security Lead}} stays in touch with at least one security community or information-sharing source relevant to {{Company}}'s industry to learn about threats early.

### 4.10 Everyone's duty

23. Management requires every person in scope to apply these policies. Following them is a condition of employment or engagement, as described in the Human Resources Security Policy.

## 5. Exceptions

An exception to any security policy is requested in writing to {{Security Lead}}, stating the reason, the risk, the compensating control and an end date. {{Security Lead}} approves low-risk exceptions; {{CEO}} approves the rest. Exceptions are logged in the risk register and reviewed at least every six months. An exception without an end date is not an exception; it is a policy change.

## 6. Enforcement

Breaches of this policy are handled under the disciplinary process in the Human Resources Security Policy. **[HR or legal review]** For contractors and vendors, breaches are handled under the terms of their contract and may end the engagement.

## 7. Review

{{Security Lead}} reviews this policy at least once a year, after a major change to the business or its systems, and after any serious incident. Changes are approved by {{CEO}} and recorded in the revision history.

## 8. Related documents

POL-02 Acceptable Use · POL-03 Access Control · POL-04 Password and Authentication · POL-05 Asset Management · POL-06 Data Classification and Handling · POL-07 Cryptography and Key Management · POL-08 Secure Development and Change Management · POL-09 Vulnerability and Patch Management · POL-10 Logging and Monitoring · POL-11 Backup and Recovery · POL-12 Business Continuity and Disaster Recovery · POL-13 Incident Response · POL-14 Vendor and Third-Party Risk · POL-15 Risk Management · POL-16 Human Resources Security · POL-17 Physical and Environmental Security · POL-18 Remote Work and Personal Devices · POL-19 Network, Endpoint and Email Security · POL-20 Data Retention and Disposal · POL-21 Privacy and Data Protection · POL-22 AI Acceptable Use · POL-23 AI Governance.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{Security Lead}} |
