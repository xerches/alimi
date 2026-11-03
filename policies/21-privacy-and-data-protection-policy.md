---
id: POL-21
slug: privacy-and-data-protection-policy
title: Privacy and Data Protection Policy
version: "1.0"
status: template
owner_role: "{{Privacy Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: personal information about customers, prospects, staff, candidates, suppliers and anyone else that {{Company}} collects or handles
requirements:
  soc2: [C1.1, P1.1, P2.1, P3.1, P3.2, P4.1, P4.2, P4.3, P5.1, P5.2, P6.1, P6.2, P6.3, P6.4, P6.5, P6.6, P6.7, P7.1, P8.1]
  iso27001: ["A.5.31", "A.5.34", "A.8.11"]
  iso42001: ["A.5.4"]
  hipaa: []
  insurer: []
related: [POL-06, POL-13, POL-14, POL-20, POL-22, POL-23]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Privacy and Data Protection Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-21 |
| Version | 1.0 |
| Owner | {{Privacy Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

{{Company}} holds information about people: customers and their staff, prospects, its own employees and candidates, suppliers' contacts. Those people have expectations and, increasingly, legal rights about what the company does with it. This policy sets how the company collects, uses, shares, keeps and protects personal information, and how it answers the people it concerns, so that the promises in the privacy notice are the way the company actually works.

## 2. Scope

Any information that identifies or could identify a living person, in any form and in any system, that {{Company}} collects or processes for itself or on behalf of a customer. Protected health information under HIPAA, payment card data and children's data carry extra rules that are referenced where they apply. The security measures that protect the data are in the other policies; this policy is about what the company may do with it.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Privacy Lead}} | Owns this policy, the data map and the privacy notice, handles requests and complaints, advises on new uses of personal data, decides with counsel whether a breach must be notified. |
| {{CEO}} | Approves the privacy notice, high-risk processing and breach notifications. |
| {{Security Lead}} | Protects the data under the security policies and runs the response to a breach. |
| {{HR Lead}} | Applies this policy to staff and candidate data. |
| Process owners | Collect and use personal data only as the data map says, and route requests to the Privacy Lead. |
| Everyone | Handles personal information with care and reports mistakes at once. |

## 4. Policy statements

### 4.1 Knowing what the company holds

1. {{Privacy Lead}} keeps a data map: each category of personal information, whose it is, where it came from, why the company has it, the legal basis where the law requires one, which systems and suppliers hold it, who can see it, how long it is kept under the Data Retention and Disposal Policy, and whether it leaves the country. The map is reviewed yearly and whenever a system, supplier or use changes.
2. **[HR or legal review]** {{Privacy Lead}} maintains a short register of the privacy laws that apply to the company and its customers (for example, the Massachusetts data security regulations, state consumer privacy laws where the company meets their thresholds, HIPAA where health information is involved, the GDPR and UK rules where European residents' data is handled, and the laws on marketing email and text messages) and what each requires, confirmed by counsel.

### 4.2 Telling people and collecting fairly

3. The company publishes a privacy notice in plain language, approved by {{CEO}}, that says what personal information it collects, why, on what basis, who it is shared with, how long it is kept, whether it is transferred abroad, what rights people have and how to exercise them, and how to complain. Staff and candidates get an equivalent notice. Notices are updated before any new use starts and dated so that people can see what changed.
4. Personal information is collected only for the purposes in the notice, only as much as those purposes need, and by fair means: no hidden collection, no buying lists without checking their origin, no scraping. Where the notice or the law promises a choice (for example, marketing email, cookies that are not strictly needed, or sharing with partners), the choice is offered before the data is used that way, is as easy to withdraw as to give, and is recorded.
5. **[HR or legal review]** Explicit consent is obtained and recorded before collecting sensitive categories of information (health, biometrics, precise location, information about children, financial account details beyond what a transaction needs) unless counsel confirms another legal basis, and such collection is approved by {{CEO}} in advance.

### 4.3 Using personal information

6. Personal information is used only for the purposes it was collected for or purposes a reasonable person would expect from the notice. A new use (a new analytics tool, a new marketing program, training or prompting an AI system with customer data) is reviewed by {{Privacy Lead}} before it starts; where it could significantly affect people, a documented privacy impact assessment is done and {{CEO}} approves. AI systems that process personal data are also assessed under the AI Governance Policy for their effect on the individuals and groups concerned.
7. Personal information is kept accurate and complete for the purpose: it is collected from the person where practical, corrected promptly when the company learns it is wrong, and systems that make decisions about people use current data.
8. Personal information is protected under the Data Classification and Handling Policy (it is at least Confidential), with access limited to the roles that need it under the Access Control Policy, encryption under the Cryptography and Key Management Policy, and test and development systems using masked or synthetic data under the Secure Development and Change Management Policy. Personal information used in test environments is anonymised or pseudonymised so that it cannot be tied back to a person.
9. Personal information is kept only as long as the Data Retention and Disposal Policy allows and is then deleted or anonymised so that it cannot be recovered.

### 4.4 Sharing personal information

10. Personal information is disclosed to outside parties only as the notice says, with the person's consent where the notice or the law requires it, or where the law compels it. Each category of recipient is in the data map, and each supplier that processes personal information on the company's behalf is bound by a written agreement under the Vendor and Third-Party Risk Policy that limits its use of the data to the company's instructions, requires security measures, requires it to report unauthorised disclosure without undue delay (24 to 72 hours), passes the same terms to its subcontractors, and requires return or deletion at the end.
11. Disclosures outside the ordinary flows in the data map (a one-off transfer to a new partner, a response to a legal request, a disclosure in an incident) are recorded with the date, the recipient, the data and the reason, so that the company can account to the person for where their information went.
12. **[HR or legal review]** Requests from police, regulators or courts for personal information are passed to {{Privacy Lead}} and {{CEO}}, who respond with counsel, disclose only what the request lawfully requires, and record the disclosure. Transfers of personal information to another country are made only with the safeguards the applicable law requires.

### 4.5 People's rights and complaints

13. Anyone can ask what personal information the company holds about them, ask for it to be corrected or deleted, withdraw consent, object to marketing, ask for a copy, or ask who it was shared with. Requests reach {{Privacy Lead}} through the contact in the notice, are logged, the requester's identity is verified in proportion to the sensitivity of the data, and the company responds within the time the applicable law sets (30 days is the default target) in plain language. Refusals explain the legal reason. Staff who receive a request anywhere pass it to {{Privacy Lead}} the same day.
14. Privacy questions and complaints are received through the same contact, acknowledged within five business days, investigated by {{Privacy Lead}}, answered with what the company found and did, and reviewed quarterly for patterns. People are told how to escalate to the relevant regulator if they are not satisfied.

### 4.6 When something goes wrong

15. Any unauthorised access to, disclosure, loss or alteration of personal information, including a misdirected email or a supplier's incident, is reported under the Incident Response Policy and recorded in the privacy incident log whether or not it must be notified. {{Privacy Lead}} assesses the risk to the people affected.
16. **[HR or legal review]** Where the law, a contract or the risk to people requires it, {{CEO}} notifies the affected people, the regulators and the customers whose data was involved within the deadlines that apply, with the content the law requires, in words the people can understand, and the notifications are recorded. Where the company processes data on a customer's behalf, it tells the customer without undue delay and supports the customer's own notifications.

### 4.7 Building it in

17. Privacy is considered at the start of every new product, process, system or supplier that touches personal information, through the review in statement 6, and the default settings of the company's products and systems are the most privacy-protective ones that still work. Staff who handle personal information are trained on this policy under the Human Resources Security Policy.

## 5. Exceptions

Using personal information in a way the notice does not cover is not an exception, it is a change that requires the notice to be updated first. Other deviations need {{Privacy Lead}}'s written agreement, recorded with a review date.

## 6. Enforcement

Misuse of personal information, including looking up people without a business reason or sharing it outside the data map, is a serious breach handled under the Acceptable Use Policy. Process owners who do not route requests promptly are escalated to {{CEO}}.

## 7. Review

{{Privacy Lead}} reviews this policy, the notice and the data map yearly, after any privacy incident or complaint that reveals a gap, and when a law, a product or a customer contract changes what the company must do.

## 8. Related documents

POL-03 Access Control · POL-06 Data Classification and Handling · POL-07 Cryptography and Key Management · POL-13 Incident Response · POL-14 Vendor and Third-Party Risk · POL-20 Data Retention and Disposal · POL-22 AI Acceptable Use · POL-23 AI Governance · the privacy notice · the data map · the request and complaint log.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{Privacy Lead}} |
