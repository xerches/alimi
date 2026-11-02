---
id: POL-23
slug: ai-governance-policy
title: AI Governance Policy
version: "1.0"
status: template
owner_role: "{{AI Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: every AI system {{Company}} develops, buys, embeds in its products or relies on in its operations, and the people who design, run, oversee and use them
requirements:
  soc2: [CC3.4, CC8.1]
  iso27001: ["A.5.8"]
  iso42001: ["4.1", "4.2", "4.3", "4.4", "5.1", "5.2", "5.3", "6.1.1", "6.1.2", "6.1.3", "6.1.4", "6.2", "6.3", "7.1", "7.2", "7.3", "7.4", "7.5", "8.1", "8.2", "8.3", "8.4", "9.1", "9.2", "9.3", "10.1", "10.2", "A.2.2", "A.2.3", "A.2.4", "A.3.2", "A.3.3", "A.4.2", "A.4.3", "A.4.4", "A.4.5", "A.4.6", "A.5.2", "A.5.3", "A.5.4", "A.5.5", "A.6.1.2", "A.6.1.3", "A.6.2.2", "A.6.2.3", "A.6.2.4", "A.6.2.5", "A.6.2.6", "A.6.2.7", "A.6.2.8", "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6", "A.8.2", "A.8.3", "A.8.4", "A.8.5", "A.9.2", "A.9.3", "A.9.4", "A.10.2", "A.10.3", "A.10.4"]
  hipaa: []
  insurer: []
related: [POL-01, POL-08, POL-13, POL-14, POL-15, POL-21, POL-22]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} AI Governance Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-23 |
| Version | 1.0 |
| Owner | {{AI Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

{{Company}} uses AI systems in its work and may build or embed them in what it sells. Customers, regulators and insurers increasingly ask how the company decides which AI systems to use, how it knows they work, who is accountable when they do not, and what happens to the people affected. This policy is the company's AI management system in miniature: it says how AI systems are chosen, assessed, built or bought, run, watched and retired, in a way that fits a company without an AI department. It is structured so that an ISO 42001 gap check can map to it directly. Day-to-day rules for staff using AI tools are in the AI Acceptable Use Policy.

## 2. Scope

Every AI system the company develops, buys, embeds in a product, or depends on for an operational or customer-facing process, across its life from the idea to retirement. "AI system" means software that produces outputs such as predictions, content, recommendations or decisions from the data it is given using machine learning or similar techniques, including large language models accessed through a supplier. The scope statement for the management system, listing the systems, products, sites and roles covered, is kept with the AI inventory and approved by {{CEO}}.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{CEO}} | Accountable for responsible AI at the company; approves this policy, the AI objectives and the risk acceptances; provides the budget and people; chairs the management review. |
| {{AI Lead}} | Owns this policy and the AI management system: inventory, risk and impact assessments, lifecycle controls, metrics, internal audit coordination, improvement. |
| System owners | Each AI system has a named owner responsible for its purpose, its assessment, its operation and its documentation. |
| {{Security Lead}} and {{Privacy Lead}} | Bring security and privacy requirements into every assessment and review. |
| Developers and operators | Follow the lifecycle controls and keep the records they produce. |
| Everyone | Uses AI systems as intended and reports concerns. |

## 4. Policy statements

### 4.1 Context, scope and leadership

1. {{AI Lead}} keeps a one-page context statement, reviewed yearly: the company's role for each AI system (user, developer, provider, or a mix), the internal and external issues that affect its use of AI (the business model, the data it holds, the skills it has, the sector's rules), the laws and contracts that apply, and the interested parties (customers, their end users, staff, regulators, suppliers, the insurer) with what each expects from the company's AI. The scope in section 2 is derived from this statement.
2. {{CEO}} approves this policy, publishes it to staff and makes it available to customers and partners on request, and shows leadership by setting the AI objectives, funding the work, taking part in the management review and acting on its findings. The policy is consistent with the Information Security, Privacy and Data Protection and AI Acceptable Use Policies and is reviewed with them.
3. Responsibilities and authorities for AI are written down: this table, the system owner for each system in the inventory, and who may approve a system going live, a change to it, or a risk acceptance. Where the company lacks a competence (for example, evaluating a model's bias), it names the outside help it uses.
4. Anyone inside the company can raise a concern about an AI system to {{AI Lead}}, {{Security Lead}} or {{CEO}}, anonymously if they choose, without fear of retaliation; the concern is logged and answered. People outside the company can report an adverse effect of a company AI system through the contact in the privacy notice and on the product; reports are logged, acknowledged and investigated like complaints.

### 4.2 Objectives, planning and resources

5. {{CEO}} sets measurable AI objectives each year (for example: every AI system in production has a current impact assessment; no high-risk use without human review; customer-facing AI accuracy above an agreed threshold; all staff trained on the AI policy), with an owner, a measure, a target date and the resources needed. Progress is reported quarterly.
6. The AI management system has the resources it needs: {{AI Lead}}'s time, budget for tools and outside expertise, and the people named as system owners. Changes to the management system itself (a new owner, a new standard, a reorganisation) are planned with their effect on the objectives and the controls considered before they happen.
7. For each AI system the inventory records its resources: the data it uses (sources, categories, personal data, licences), the tooling and models (including the supplier, the model version and its terms), the computing and hosting it runs on, and the people who design, operate and oversee it with the competence each needs. People in those roles are competent through training, experience or supervision, and the record of who is competent for what is kept under the Human Resources Security Policy. All staff receive awareness of this policy and their part in it.
8. This policy, the inventory, the assessments, the objectives, the procedures and the records they produce are controlled documents under the Information Security Policy: versioned, approved, available to those who need them and retained. {{AI Lead}} plans what is communicated about AI, to whom, when and how: staff, customers, partners and regulators each have a channel.

### 4.3 Risk and impact

9. AI risks and opportunities are managed through the Risk Management Policy with the same register, scoring and acceptance rules. The AI risk assessment is repeatable: it uses defined criteria for likelihood and impact that include harm to individuals, groups and society as well as to the company, it runs before a system goes live, at least yearly, and whenever the system, its data, its supplier or its use changes materially, and its results are kept.
10. For each risk above appetite a treatment is chosen and recorded; the controls applicable to the company's AI systems, and those judged not applicable with the reason, are listed in a Statement of Applicability kept with the risk register. Treatment plans are implemented and tracked like any other action.
11. Before an AI system is adopted, built or changed significantly, and at least yearly while it is in use, the system owner completes an AI system impact assessment, using the company's template, that identifies who could be affected (users, the people the outputs are about, groups that could be treated unfairly, society more broadly where the scale or the domain warrants), how (accuracy, fairness, privacy, safety, transparency, autonomy, economic or environmental effects), how likely and how serious the impact is, what reduces it, and whether the use should go ahead. {{AI Lead}} reviews each assessment, {{CEO}} approves those with significant impacts, and the assessments are retained as records.

### 4.4 Developing and buying AI systems

12. The company states its objectives for responsible development and use (for example: accuracy fit for the purpose, fairness across the groups the system affects, transparency to users, privacy by design, security, human oversight, and accountability) and designs each system against them. Development follows a defined process layered on the Secure Development and Change Management Policy: documented requirements and specifications including the intended use and the uses that are out of scope; design decisions, model choices and their rationale recorded; verification and validation against the requirements with test data that reflects real use, including tests for bias and failure modes; a deployment plan with a rollback path; and technical documentation adequate for the people who operate, audit or integrate it.
13. Data used to develop, tune or evaluate an AI system is managed deliberately: its acquisition is approved and its licence and consent checked; its provenance (where it came from, when, under what terms) is recorded; its quality (completeness, representativeness, accuracy, currency) is defined and checked for the purpose; and the steps used to prepare it (cleaning, labelling, splitting, anonymising) are documented so that the result can be reproduced. Personal data in training or evaluation sets follows the Privacy and Data Protection Policy.
14. AI systems bought or accessed from suppliers, including models used through an interface, are reviewed under the Vendor and Third-Party Risk Policy with the added questions of what the supplier does with the company's inputs and outputs, what the supplier commits to about accuracy, safety, bias and incidents, which responsibilities sit with the supplier and which with the company, and how the company would leave. The split of responsibilities is written in the contract or the inventory entry. Where the company supplies AI to customers, it understands and meets their expectations and obligations, tells them what they need to know, and passes the relevant requirements to its own suppliers.

### 4.5 Operating AI systems

15. Each AI system in production is operated and monitored by its owner: performance, drift, error rates, complaints and incidents are measured against the thresholds set at deployment; the system logs the events needed to trace what it did and when, under the Logging and Monitoring Policy; and the owner reviews the measurements at least monthly and reports exceptions to {{AI Lead}}.
16. Users of a company AI system, inside or outside, are told that they are interacting with AI, what it is for and not for, its known limitations, how to get a human, and how to report a problem; the information is in the product, the documentation or the privacy notice as fits the audience. Interested parties who need more (customers under contract, auditors, regulators) receive the documentation and the assessments relevant to them.
17. AI systems are used only for their intended purpose and within the conditions the impact assessment set; the processes for responsible use, the objectives for use, and the staff rules in the AI Acceptable Use Policy are followed. A new use of an existing system is a change that triggers statements 9 and 11.
18. Incidents involving an AI system (harmful or discriminatory output that reached a person, data exposure, misuse, a supplier failure, a significant accuracy failure) are handled under the Incident Response Policy with {{AI Lead}} on the response team, and the people affected are told what happened and what the company is doing about it.

### 4.6 Checking and improving

19. {{AI Lead}} monitors and measures the AI management system itself: the objectives in statement 5, the currency of assessments, training completion, concerns raised and resolved, and audit findings, and reports to {{CEO}} quarterly. The management system is audited internally at least yearly, by someone independent of the systems being audited (another manager, a consultant, or a peer company on exchange), against this policy and the standard the company has chosen; findings are recorded with owners and dates.
20. {{CEO}} chairs a management review of AI at least yearly, with {{AI Lead}}, {{Security Lead}} and {{Privacy Lead}}, covering changes in context, objectives and their measures, risk and impact assessment results, incidents and concerns, audit findings, supplier performance, resource needs and opportunities to improve; decisions and actions are minuted.
21. Nonconformities (a control not followed, an assessment missed, an objective not met) are recorded, corrected, their cause analysed and addressed so that they do not recur, and the effectiveness of the fix checked; the management system is improved continually from these, from the reviews and from what the company learns.

## 5. Exceptions

An AI system may run without a current impact assessment only during a documented pilot with no external users and no personal data, for at most 90 days, approved by {{AI Lead}}. Other deviations follow the Information Security Policy and are recorded as risks.

## 6. Enforcement

An AI system found in production without an owner, an assessment or the required documentation is paused until these exist, by {{AI Lead}}'s decision with {{CEO}} informed. Breaches of the staff rules follow the AI Acceptable Use Policy.

## 7. Review

{{AI Lead}} reviews this policy yearly at the management review, after any AI incident, and when a law on AI, a customer contract or the company's role (for example, moving from user to provider) changes.

## 8. Related documents

POL-01 Information Security · POL-08 Secure Development and Change Management · POL-10 Logging and Monitoring · POL-13 Incident Response · POL-14 Vendor and Third-Party Risk · POL-15 Risk Management · POL-16 Human Resources Security · POL-21 Privacy and Data Protection · POL-22 AI Acceptable Use · the AI inventory and context statement · the AI impact assessment template · the Statement of Applicability.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{AI Lead}} |
