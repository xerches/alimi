---
id: POL-08
slug: secure-development-and-change-management-policy
title: Secure Development and Change Management Policy
version: "1.0"
status: template
owner_role: "{{IT Lead}}"
approver_role: "{{Security Lead}}"
review_cycle: annual
applies_to: software {{Company}} builds or customises, and changes to production systems and tenant configuration
requirements:
  soc2: [CC8.1, CC6.8, CC3.4]
  iso27001: ["6.3", "A.5.8", "A.8.4", "A.8.25", "A.8.26", "A.8.27", "A.8.28", "A.8.29", "A.8.30", "A.8.31", "A.8.32", "A.8.33"]
  iso42001: ["A.6.1.3", "A.6.2.4", "A.6.2.5"]
  hipaa: []
  insurer: []
related: [POL-03, POL-07, POL-09, POL-14]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Secure Development and Change Management Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-08 |
| Version | 1.0 |
| Owner | {{IT Lead}} |
| Approved by | {{Security Lead}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Changes cause outages and open holes. This policy makes sure that software {{Company}} writes is built with security in mind from the start, and that changes to production systems, including the settings of the Microsoft 365 or Google Workspace tenant, are requested, approved, tested and recorded, so that a bad change can be found and reversed.

## 2. Scope

Part A (secure development) applies when {{Company}} builds, customises or commissions software, including websites, integrations, scripts and AI systems. Part B (change management) applies to everyone who changes a production system: servers, cloud infrastructure, network devices, SaaS tenant settings, identity provider policies and security tools. If {{Company}} writes no software, Part A is marked not applicable in the risk register and Part B still applies.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{IT Lead}} | Owns the change process, approves standard and normal changes, keeps the change record. |
| {{Security Lead}} | Approves this policy, reviews security-significant changes, sets the security requirements for software. |
| Developers (staff or contracted) | Follow the secure development practices, review each other's code, keep secrets out of code. |
| System owners | Approve changes to their systems and confirm the result. |

## 4. Policy statements

### Part A: Secure development

#### 4.1 Security in the lifecycle

1. Security is considered at the start of every project or significant feature: the owner records the data it handles and its classification, the users, the threats that matter and the security requirements, before building starts.
2. Security requirements for applications include at minimum: authentication through the company identity provider, authorisation by role, input validation, encryption as in the Cryptography Policy, logging of security events, and protection against the common web weaknesses described in the current OWASP Top 10.
3. Architecture decisions that affect security (where data lives, what is exposed to the internet, which third-party services are used) are written down and reviewed by {{Security Lead}}.

#### 4.2 Writing and reviewing code

4. Developers follow secure coding practices for their language and framework, use the framework's built-in protections rather than custom ones, and keep dependencies current.
5. Every change to code is reviewed by someone other than the author before it is merged. The review covers function and security. Where the team is one person, the review is done by a contracted reviewer or by {{Security Lead}} for security-significant changes, and automated checks carry more of the weight.
6. Source code lives in a company-controlled repository with access by role, multi-factor authentication, protected main branches and a history that cannot be rewritten without approval.
7. Secrets are never committed. Secret scanning runs on every push and blocks a commit containing a credential; a leaked secret is rotated under the Cryptography Policy.
8. Third-party and open-source components are recorded (a software bill of materials where practical), checked for known vulnerabilities automatically, kept to supported versions, and used under licences compatible with {{Company}}'s use.

#### 4.3 Testing

9. Automated tests run on every change: unit tests, dependency vulnerability checks, static analysis and secret scanning. A failing security check blocks the merge until fixed or accepted by {{Security Lead}}.
10. Security testing proportional to the risk happens before a release that changes authentication, authorisation, payment, data export or anything internet-facing: at minimum a review against the security requirements, and for customer-facing systems an external penetration test at least yearly and after major changes.
11. Development, test and production environments are separate. Developers do not have standing write access to production data; deployments go through the pipeline.
12. Test data does not contain production Confidential or Restricted data. Masked or synthetic data is used, as the Data Classification and Handling Policy requires.

#### 4.4 Outsourced development

13. Contracted developers and agencies follow this policy; the contract says so, assigns intellectual property to {{Company}}, requires secure handling of code and data, and gives {{Company}} the right to review the code and the security testing results. See the Vendor and Third-Party Risk Policy.

#### 4.5 AI systems

14. Software that includes an AI model or calls an AI service follows this policy and, in addition, the verification, validation and deployment steps in the AI Governance Policy.

### Part B: Change management

#### 4.6 Change types

15. **Standard changes** are routine, low-risk and pre-approved (for example applying a vendor patch, adding a user to an approved group, renewing a certificate). They are recorded but need no individual approval.
16. **Normal changes** are everything else planned: infrastructure changes, new integrations, tenant policy changes, firewall rules, software releases. They follow the steps in 4.7.
17. **Emergency changes** fix an outage or an active security problem. They may be made first and documented within one business day; {{IT Lead}} or {{Security Lead}} approves them verbally at the time and in writing afterwards.

#### 4.7 The change steps

18. **Request**: what will change, why, which systems and users are affected, the risk, the test plan and the rollback plan, recorded in the change log (a ticket system, a repository pull request or a shared log).
19. **Approve**: the system owner approves; {{Security Lead}} also approves changes to identity, access, security tools, logging, backups, network exposure or encryption.
20. **Test**: the change is tested in a non-production environment or, where none exists (most SaaS settings), on a pilot group first.
21. **Schedule and communicate**: changes with user impact are made outside core hours where possible and announced beforehand.
22. **Implement and verify**: the person making the change confirms the expected result and checks for side effects, including that monitoring, backups and security settings still work. The workspace security scan is re-run after tenant changes.
23. **Record**: the log shows who requested, approved, made and verified the change, and when. Records are kept for at least six years.
24. **Roll back**: if the change fails or causes harm, the rollback plan is executed and the failure is reviewed.

#### 4.8 Changes to the management system

25. Planned changes to the security programme itself (new policies, new scope, new tools) go through the same request-and-approve steps with {{Security Lead}}, so the ISMS changes deliberately rather than by drift.

## 5. Exceptions

Follow the Information Security Policy. Skipping code review or testing is not an exception; it is an emergency change and is documented as one.

## 6. Enforcement

Unauthorised changes are reversed when found and reviewed as an incident if they affected security. Breaches follow the Human Resources Security Policy or the contractor's agreement.

## 7. Review

{{IT Lead}} reviews this policy annually and after any outage or incident caused by a change.

## 8. Related documents

POL-03 Access Control · POL-07 Cryptography and Key Management · POL-09 Vulnerability and Patch Management · POL-10 Logging and Monitoring · POL-14 Vendor and Third-Party Risk · POL-23 AI Governance.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{IT Lead}} |
