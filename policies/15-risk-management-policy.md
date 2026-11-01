---
id: POL-15
slug: risk-management-policy
title: Risk Management Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: security, privacy, AI and operational risks to {{Company}}'s information, systems, people and obligations
requirements:
  soc2: [CC3.1, CC3.2, CC3.3, CC3.4, CC4.1, CC4.2, CC9.1]
  iso27001: ["6.1.1", "6.1.2", "6.1.3", "8.1", "8.2", "8.3", "9.1", "A.5.7"]
  iso42001: ["6.1.1", "6.1.2", "6.1.3", "8.2", "8.3"]
  hipaa: ["164.308(a)(1)"]
  insurer: []
related: [POL-01, POL-12, POL-13, POL-14, POL-23]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Risk Management Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-15 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

{{Company}} cannot protect against everything, and a company of its size should not try. This policy sets a simple, repeatable way to decide what could hurt the business, how badly, how likely it is, and what to do about it, so that time and money go to the risks that matter and the choice to live with a risk is made on purpose by the right person. It is the engine behind the other policies: each of them exists because a risk in the register needed a control.

## 2. Scope

Risks to the confidentiality, integrity and availability of {{Company}}'s information and systems; risks to the privacy of the people whose data it holds; risks from the AI systems it uses or builds; risks of fraud; risks of failing a legal, contractual or insurance obligation; and risks to the business processes that depend on all of the above. Financial and market risks are managed by {{CEO}} outside this policy.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{CEO}} | Sets the risk appetite, accepts risks above the Security Lead's authority, reviews the register at least twice a year. |
| {{Security Lead}} | Owns this policy, runs the assessment, keeps the risk register, tracks treatment actions, reports to the CEO. |
| Risk owners (department heads, system owners) | Know the risks in their area, own the treatment actions assigned to them, report changes. |
| {{Privacy Lead}} and {{AI Lead}} | Bring privacy and AI risks into the same register and process. |
| Everyone | Raises a risk they notice to their manager or {{Security Lead}}. |

## 4. Policy statements

### 4.1 Objectives and appetite

1. The assessment starts from what the company is trying to achieve: the objectives in the Information Security Policy (and the AI objectives in the AI Governance Policy), the obligations to customers, regulators and the insurer, and the business processes identified in the Business Continuity and Disaster Recovery Policy. A risk is anything that could stop those objectives being met.
2. {{CEO}} sets the risk appetite in one page: what the company will not accept at any price (for example, loss of customer data through a known, unpatched flaw; a payment made without verification), what it will accept with controls, and the financial size below which a department head may accept a risk alone.

### 4.2 Identifying risks

3. {{Security Lead}} runs a full risk assessment at least once a year and a focused one whenever something significant changes: a new product or service, a new critical supplier or system, a new type of data (especially health, financial or children's data), a new office, a new law or contract, a merger, a serious incident, or a new AI use case. Changes that could affect the controls themselves (a migration, a reorganisation, the departure of the only administrator) are treated as triggers too.
4. Risks are found from several directions so that the obvious ones do not crowd out the rest: the asset inventory and data map, threat scenarios relevant to small companies (business email compromise, ransomware, account takeover, insider error, supplier failure, lost devices), the results of the security scanning tooling and vulnerability scans, incidents and near misses, audit and customer findings, supplier reviews, and interviews with each department head.
5. Fraud is considered explicitly: how someone inside or outside could divert payments, misuse access, falsify records or abuse an AI system, and which controls (payment verification, separation of duties, logging) address it.

### 4.3 Analysing and evaluating

6. Each risk is written as a sentence anyone can understand (what could happen, to what, because of what, with what consequence), given a risk owner, and scored on a five-point scale for likelihood and for impact. Impact considers money, legal and contractual penalties, harm to customers and individuals, reputation and operational disruption. The two scores multiply into a rating of Low (1 to 5), Medium (6 to 11), High (12 to 19) or Critical (20 to 25).
7. The scoring guide, with examples for each point on each scale, is kept with the register so that two people would score the same risk the same way. Existing controls are listed against each risk, and the score reflects the risk with those controls in place.
8. The rating sets what happens next: Critical and High risks need a treatment plan within 30 days and are reported to {{CEO}}; Medium risks need an owner and a decision within 90 days; Low risks are accepted and reviewed yearly.

### 4.4 Treating risks

9. For each risk above appetite the owner chooses to reduce it with a control, avoid it by stopping the activity, share it through insurance or a contract, or accept it. The choice, the controls selected, the person responsible, the date and the expected residual rating are recorded as the risk treatment plan. Controls come first from the company's own policies and the control catalogue; a control that is not applicable is marked as such with the reason, so the list of applicable controls can be shown to an auditor or customer as the Statement of Applicability.
10. Accepting a risk is a signature, not a silence. Risks rated High or Critical are accepted only by {{CEO}}, in writing, with an expiry date of at most twelve months. Medium risks may be accepted by {{Security Lead}}. Risk acceptances are listed separately in the register and reviewed at every management review.
11. Treatment actions are tracked like any other project, with progress reviewed monthly by {{Security Lead}} and overdue actions reported to {{CEO}}.

### 4.5 Watching the risks

12. {{Security Lead}} defines a short set of measures that show whether the controls work (for example: percentage of accounts with multi-factor authentication, patching within target, backup restore test results, phishing simulation click rate, overdue treatment actions, open supplier findings) and reports them to {{CEO}} quarterly. Where the security tooling can measure a control automatically, that measurement is used instead of a self-assessment.
13. Controls are checked independently of the people who run them: internal audits under the Information Security Policy, the annual penetration test, supplier evidence reviews, and customer or auditor findings. Gaps found are logged as nonconformities with a cause analysis and a corrective action, and tracked to closure.
14. Threat information from sources relevant to small companies (government advisories, the insurer, industry groups, the managed service provider, vendor security bulletins) is reviewed at least monthly by {{Security Lead}} and turned into risk register entries or immediate actions where it applies.

### 4.6 Records

15. The risk register, the scoring guide, the risk appetite statement, the treatment plans, the risk acceptances and the assessment reports are kept as controlled documents for at least six years, access-limited to management, and provided to auditors, insurers and customers on request as the evidence that risk is managed.

## 5. Exceptions

Skipping the annual assessment or the review of a trigger event needs {{CEO}}'s written agreement and is itself recorded as a risk.

## 6. Enforcement

Risk owners who do not complete treatment actions or who hide known risks are escalated to {{CEO}}. Knowingly concealing a Critical risk is misconduct under the Acceptable Use Policy.

## 7. Review

{{Security Lead}} reviews this policy, the appetite statement and the scoring guide yearly and after any incident whose cause was a risk that had been underestimated or missed.

## 8. Related documents

POL-01 Information Security · POL-12 Business Continuity and Disaster Recovery · POL-13 Incident Response · POL-14 Vendor and Third-Party Risk · POL-23 AI Governance · the risk register and scoring guide · the risk appetite statement · the Statement of Applicability.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
