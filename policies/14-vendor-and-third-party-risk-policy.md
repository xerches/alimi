---
id: POL-14
slug: vendor-and-third-party-risk-policy
title: Vendor and Third-Party Risk Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: every supplier, cloud service, contractor, managed service provider and partner that touches {{Company}}'s data, systems or operations
requirements:
  soc2: [CC2.3, CC9.2]
  iso27001: ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23", "A.8.30"]
  iso42001: ["A.10.2", "A.10.3", "A.10.4"]
  hipaa: ["164.308(b)(1)", "164.314(a)"]
  insurer: [vendor_risk]
related: [POL-03, POL-06, POL-08, POL-12, POL-13, POL-21, POL-23]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Vendor and Third-Party Risk Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-14 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

A company of {{Company}}'s size runs on other people's software and services: email and files in a cloud tenant, payroll, accounting, a customer database, a managed IT provider, a developer on contract. Each of them can lose {{Company}}'s data or stop the business, and when they do, customers and regulators still hold {{Company}} responsible. This policy makes sure that the company knows who its suppliers are, picks them with care in proportion to the risk, writes the right things into the contract, and checks on them afterwards.

## 2. Scope

Every outside party that stores, processes or can reach {{Company}} information, that has access to its systems, offices or accounts, or that a critical business process depends on. This includes free and trial services, browser extensions and AI tools that staff sign up for themselves. It does not cover the purchase of goods with no data or access involved.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns this policy and the vendor register, sets each supplier's tier, runs or reviews the due diligence, reviews suppliers on schedule. |
| Business owner of the supplier (the person who wanted it) | Requests the supplier, provides the business case, is the day-to-day contact, confirms the review each year. |
| {{Finance Lead}} | Does not pay a new supplier that is not in the register; keeps the contract on file. |
| {{Privacy Lead}} | Reviews suppliers that process personal data and the data processing terms. |
| {{AI Lead}} | Reviews suppliers that provide or embed AI systems. |
| {{CEO}} | Approves critical-tier suppliers and accepted risks. |

## 4. Policy statements

### 4.1 The vendor register

1. {{Security Lead}} keeps a register of every supplier in scope with: name, service, business owner, data it holds or can reach (and its classification under the Data Classification and Handling Policy), access it has to systems or offices, tier, contract and renewal date, security evidence on file and its date, last review date, and whether it is critical to a business process in the Business Continuity and Disaster Recovery Policy.
2. Staff do not sign up for, connect or pay for a new service that will hold company data or connect to the company tenant without a request to {{Security Lead}}. Finance pays only suppliers in the register. Self-service sign-ups found through the tenant's app inventory, expense reports or audit logs are added to the register or shut down.

### 4.2 Tiering

3. Each supplier gets a tier that drives the rest of the process:

| Tier | Meaning | Examples |
| --- | --- | --- |
| Critical | Holds confidential or regulated data at scale, has administrative access, or the business stops without it | Email and file tenant, managed IT provider, payroll, customer database, main cloud host |
| High | Holds confidential data or has user-level access to systems | Support desk tool, e-signature, backup service, contract developer |
| Standard | Holds internal data only, no system access | Project tool with no customer data, travel booking |
| Low | Public data or no data | Stationery, utilities |

### 4.3 Due diligence before signing

4. Before a critical or high tier supplier is used, {{Security Lead}} obtains and reviews independent security evidence: a current SOC 2 report or ISO 27001 certificate with its scope checked, or where the supplier is too small for those, a completed security questionnaire and a conversation. The review looks for multi-factor authentication, encryption, access control, logging, incident response, backups, subcontractors, breach notification practice and cyber insurance. Standard tier suppliers get a short questionnaire; low tier suppliers need none.
5. Supplier software and hardware are chosen with their supply chain in mind: components and libraries from maintained sources, updates signed by the vendor, administrative tools from the original publisher, and no equipment or software from sources that cannot be verified.
6. Suppliers that will process personal data are also reviewed by {{Privacy Lead}} for the data processing terms the Privacy and Data Protection Policy requires. Suppliers that provide an AI system, or embed one in their service, are also reviewed by {{AI Lead}} for how the data is used for training, what the model can see, and what the supplier commits to about accuracy, bias and incidents.
7. Findings that are not acceptable are fixed by contract, by compensating controls on {{Company}}'s side, or by choosing another supplier. A risk that remains is recorded in the risk register and accepted by {{CEO}} for critical tier suppliers.

### 4.4 Contracts

8. Contracts with critical and high tier suppliers include, in words a lawyer has reviewed: confidentiality; the security measures the supplier maintains; notification of security incidents affecting {{Company}}'s data within 24 hours of discovery, or at most 72; the right to request evidence of controls each year; use of {{Company}}'s data only to provide the service; the names or categories of subcontractors and a duty to flow these terms down to them; return or deletion of data at the end of the service, with confirmation; and the supplier's continuity and support commitments.
9. Where {{Company}} is a HIPAA covered entity or business associate, a supplier that creates, receives, maintains or transmits protected health information signs a business associate agreement containing the required security and breach terms before it receives any such information. Where personal data of EU or UK residents is processed, a data processing agreement is in place.
10. Click-through terms for cloud services are read before acceptance by the business owner, with {{Security Lead}} checking the data use, data location and termination clauses for anything above standard tier.

### 4.5 Managing the relationship

11. The managed IT provider and any other supplier with administrative access follows the Access Control Policy: named accounts, multi-factor authentication, access limited to what the service needs, activity visible in {{Company}}'s own logs, and access removed the day the contract ends.
12. Outsourced software development is supervised: {{Company}} owns the code and the repositories, the supplier follows the Secure Development and Change Management Policy, code is reviewed before it is merged, and secrets are never shared in chat or email.
13. Suppliers are reviewed on a schedule by tier: critical yearly with fresh evidence and a conversation about changes, high yearly with refreshed evidence, standard at renewal. The review also covers service quality, incidents, changes in ownership or subcontractors, and whether the supplier is still needed. Security news about critical suppliers (breaches, major vulnerabilities, acquisitions) is watched and acted on between reviews.
14. Changes a supplier makes to its service, terms, subcontractors or data location are assessed when they are announced, and the tier is updated if the data or access changes.
15. When a supplier reports an incident, the Incident Response Policy applies and the business owner and {{Security Lead}} stay in contact until it is closed. Unauthorised disclosures of personal data by a supplier are recorded under the Privacy and Data Protection Policy.
16. Where {{Company}} provides a service to its own customers, it answers their security and AI questions honestly, tells them which suppliers process their data when asked, and meets the commitments in its own contracts; those commitments are passed to the suppliers who need to meet them.

### 4.6 Ending the relationship

17. When a service ends, the business owner confirms the data has been exported, the supplier has deleted or returned it, its accounts, API keys and integrations are removed, and the register is updated. Critical tier suppliers have an exit plan written before they are adopted: how long leaving would take, and what the alternative is.

## 5. Exceptions

Follow the Information Security Policy. A critical supplier with no independent evidence, or a contract without breach notification terms, is a recorded risk with an expiry date, accepted by {{CEO}}.

## 6. Enforcement

Services adopted outside this process are suspended until reviewed. Repeated bypasses are handled under the Acceptable Use Policy. Suppliers that fail to meet their security commitments are escalated by {{Security Lead}}, with replacement as the last step.

## 7. Review

{{Security Lead}} reviews this policy yearly, after any supplier incident, and when a new law, customer contract or insurance requirement changes what suppliers must commit to.

## 8. Related documents

POL-03 Access Control · POL-06 Data Classification and Handling · POL-08 Secure Development and Change Management · POL-12 Business Continuity and Disaster Recovery · POL-13 Incident Response · POL-21 Privacy and Data Protection · POL-23 AI Governance · the vendor register · the supplier security questionnaire.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{Security Lead}} |
