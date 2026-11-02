---
id: POL-22
slug: ai-acceptable-use-policy
title: AI Acceptable Use Policy
version: "1.0"
status: template
owner_role: "{{AI Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: everyone who works for {{Company}} and any AI tool or feature they use for work, approved or not
requirements:
  soc2: [C1.1, CC6.7]
  iso27001: ["A.5.10", "A.5.12", "A.5.14"]
  iso42001: ["A.2.2", "A.2.3", "A.3.3", "A.8.2", "A.9.2", "A.9.3", "A.9.4"]
  hipaa: []
  insurer: [data_sharing]
related: [POL-02, POL-06, POL-14, POL-21, POL-23]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} AI Acceptable Use Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-22 |
| Version | 1.0 |
| Owner | {{AI Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Staff at {{Company}} already use AI assistants to draft emails, summarise documents, write code and answer questions, and many of the company's existing tools have added AI features. Used well, these save hours. Used carelessly, they send confidential data to a third party, produce confident errors that reach a customer, or break a contract or a law without anyone noticing. This policy says which tools may be used, what may be put into them, how to treat what comes out, and how to raise a concern. The company's own governance of AI systems, including those it builds, is in the AI Governance Policy.

## 2. Scope

Any use of an AI tool or feature for {{Company}} work by anyone who works for the company: general-purpose assistants, AI features inside email, office, meeting, design, development and customer tools, browser extensions, AI agents that act on the user's behalf, and tools used on personal devices for work. It applies whether the company pays for the tool or not.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{AI Lead}} | Owns this policy and the approved tool list, reviews requests for new tools, keeps the AI tool inventory, answers questions. |
| {{Security Lead}} | Reviews tools for security and data handling, watches the tenant for unapproved AI apps. |
| {{Privacy Lead}} | Reviews tools and uses that involve personal information. |
| Managers | Make sure their teams know the rules and that AI use in their area is appropriate to the work. |
| Everyone | Uses only approved tools, protects data, checks outputs, reports problems. |

## 4. Policy statements

### 4.1 Which tools

1. {{AI Lead}} publishes and keeps current a list of approved AI tools and features, with the data classification each may receive and any conditions (for example, business account only, training on company data turned off, a specific feature disabled). A tool gets on the list after review by {{AI Lead}}, {{Security Lead}} and, where personal information is involved, {{Privacy Lead}}, under the Vendor and Third-Party Risk Policy. The review checks who can see the data, whether it is used to train models, where it is stored, how long it is kept, and what the tool's terms say about ownership of outputs.
2. Tools not on the list may be used only with public information, on a business account where one exists, until they are reviewed; anyone who wants a tool reviewed asks {{AI Lead}}, and the answer comes within ten business days. Personal accounts on consumer AI tools are not used for company work that involves anything above public data.
3. The company's own AI tools are used through the company's accounts and single sign-on so that use is covered by the company's terms with the supplier and visible in the audit logs, not through personal sign-ups. {{Security Lead}} reviews the tenant's application and sign-in logs for AI tools in use that are not on the list and asks {{AI Lead}} to review or block them.

### 4.2 What goes in

4. The Data Classification and Handling Policy decides what may be entered into a tool. Unless the approved list says otherwise for a specific tool: public and internal information may be used; confidential information (customer data, contracts, financials, source code, unreleased plans) may be used only in tools approved for that classification; restricted and regulated information (health, payment card, personal information of customers' end users, credentials, encryption keys) is never entered into a general-purpose AI tool.
5. Before pasting or uploading, the user removes or replaces names, account numbers and other identifying details that the task does not need. Documents from customers, partners or suppliers are not uploaded to an AI tool unless the contract with them allows it or they have agreed.
6. AI tools that can act (send email, change files, run code, make purchases, browse on the user's behalf) are given only the access the task needs, operate under the user's own account, never under a shared or administrative account, and their actions are reviewed before anything leaves the company. Credentials and multi-factor codes are never given to an AI tool.
7. Meeting recording and transcription features are used only when every participant has been told and, where the law or the customer requires, has agreed; recordings and transcripts are stored under the Data Retention and Disposal Policy and not kept by default.

### 4.3 What comes out

8. The person using the tool is responsible for the output as if they had written it. Anything that goes to a customer, into a contract, into production code, into a financial record or into a public statement is checked by a person who understands the subject: facts, figures, quotes, citations, legal and medical claims, and code behaviour are verified, because AI tools produce plausible errors. The company does not use "the AI said so" as an explanation to a customer.
9. AI output is not presented as a person's own original work where that matters (academic, journalistic or contractual contexts), and where a customer or partner asks whether AI was used, the company answers honestly. Where a regulation or a contract requires disclosure that AI was used, or requires a human decision, the company complies; decisions with legal or similarly significant effects on a person (hiring, firing, credit, pricing for an individual, medical or legal advice) are made by a person, with AI used only to inform.
10. Outputs are checked for material the company may not use: copyrighted text or images reproduced at length, personal information about someone that the user did not supply, and content that is defamatory, discriminatory or otherwise harmful. Generated images, voices and video are not used to imitate real people without their written consent and are labelled where the audience could be misled.
11. Code generated with AI follows the Secure Development and Change Management Policy: reviewed before merging, scanned for vulnerabilities and licence conflicts, and never containing secrets copied from prompts.

### 4.4 Concerns and incidents

12. Anyone who sees an AI tool produce harmful, biased or clearly wrong output in a way that matters, suspects confidential data went into the wrong tool, or is unsure whether a use is allowed, tells {{AI Lead}} or {{Security Lead}}; data exposure is an incident under the Incident Response Policy and is reported straight away. Raising a concern in good faith is never penalised. Customers and the public can raise concerns about the company's use of AI through the contact in the privacy notice.
13. {{AI Lead}} keeps an inventory of the AI tools in use, who uses them, for what, and with what data, and reviews it quarterly with {{Security Lead}}; the inventory feeds the AI Governance Policy's risk assessment.

### 4.5 Making it work

14. The company's position is that AI is encouraged where it helps and the rules above are met; it sets the goal of using AI to do better work faster, without putting customers, staff or the company at risk, and {{AI Lead}} shares good practice and example prompts for common tasks. Staff receive short training on this policy at induction and yearly under the Human Resources Security Policy, and the approved list is linked from the places people work.
15. This policy is consistent with the Acceptable Use Policy, the Data Classification and Handling Policy and the Privacy and Data Protection Policy; where they appear to conflict, the stricter rule applies and {{AI Lead}} resolves the wording at the next review.

## 5. Exceptions

A one-off use of a confidential data set in an unapproved tool is not granted. Exceptions for a specific tool and data type are approved in writing by {{AI Lead}} and {{Security Lead}} with an expiry date and recorded in the inventory.

## 6. Enforcement

Use of an unapproved tool with confidential data, or of restricted data in any general-purpose AI tool, is handled under the Acceptable Use Policy and, where data was exposed, as an incident. The first response to an honest mistake is training and a fix, not discipline.

## 7. Review

{{AI Lead}} reviews this policy and the approved list yearly, and sooner when a tool changes its terms, a new category of tool appears, a law on AI use takes effect, or an incident shows a gap.

## 8. Related documents

POL-02 Acceptable Use · POL-06 Data Classification and Handling · POL-08 Secure Development and Change Management · POL-13 Incident Response · POL-14 Vendor and Third-Party Risk · POL-16 Human Resources Security · POL-20 Data Retention and Disposal · POL-21 Privacy and Data Protection · POL-23 AI Governance · the approved AI tool list · the AI tool inventory · the one-page staff guide to AI.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{AI Lead}} |
