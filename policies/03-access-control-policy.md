---
id: POL-03
slug: access-control-policy
title: Access Control Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: all accounts and access rights on {{Company}} systems, including vendor and service accounts
requirements:
  soc2: [CC6.1, CC6.2, CC6.3]
  iso27001: ["A.5.3", "A.5.15", "A.5.16", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.18"]
  iso42001: []
  hipaa: ["164.308(a)(3)", "164.308(a)(4)", "164.312(a)(1)"]
  insurer: [admin_access]
related: [POL-04, POL-10, POL-14, POL-16]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Access Control Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-03 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Most breaches use a valid account. This policy limits who can get into {{Company}}'s systems and data, how much they can do once in, and how quickly access is removed when it is no longer needed. It gives an insurer or a customer a direct answer to "who are your administrators and how do you control them".

## 2. Scope

Every account on every {{Company}} system: staff and contractor accounts, administrator accounts, shared mailboxes, service accounts used by software, vendor accounts, and guest accounts given to outside people. It covers the identity provider (Microsoft Entra ID or Google Workspace), cloud services, line-of-business applications, network devices, source code repositories and any system holding {{Company}} data.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns this policy, defines the access model, runs the access reviews and approves privileged access. |
| {{IT Lead}} or managed service provider | Creates, changes and removes access on request, keeps the identity provider as the single source of identity and keeps the records. |
| Managers | Request access for their staff by role, approve what their team members need and confirm it at review time. |
| System owners | Decide who may access the system they own and at what level. |
| {{HR Lead}} | Tells IT about joiners, movers and leavers in time for access to be set up or removed on the right day. |

## 4. Policy statements

### 4.1 Principles

1. **Least privilege.** People and systems get the minimum access needed for their role, for the time they need it.
2. **Need to know.** Access to Confidential and Restricted information is granted to named roles, not to everyone by default.
3. **Individual accountability.** Every person has their own account. Shared accounts are prohibited except where a system cannot support individual accounts; those are approved by {{Security Lead}}, kept in the password manager with access logged, and reviewed quarterly.
4. **Separation of duties.** Where practical, the person who requests access does not approve it, the person who makes a payment does not also approve it, and developers do not deploy their own untested changes to production. Where the team is too small to separate duties, the activity is logged and reviewed by someone else.
5. **Default deny.** New systems start with no access and access is added by role.

### 4.2 Identity lifecycle

6. Access is based on roles. {{Security Lead}} keeps a role-to-access matrix (role, systems, level) that managers choose from when requesting access.
7. **Joiners.** Access is requested by the manager, approved by the system owner where needed, and created by IT no earlier than the start date. The account is in the identity provider; local accounts in individual applications are avoided and single sign-on is used wherever the application supports it.
8. **Movers.** When someone changes role, their manager reviews their access within 5 business days; rights that do not fit the new role are removed, not accumulated.
9. **Leavers.** HR tells IT the departure date in advance. On the last working day, or immediately for involuntary departures, all access is disabled: identity provider account, multi-factor devices, VPN, application accounts, shared-mailbox rights, API keys and physical access. Mail and files are handed to the manager under the Data Retention and Disposal Policy. The account is deleted after the retention period.
10. Guest accounts for outside collaborators expire after 90 days by default, are sponsored by a named employee and are removed when the work ends.

### 4.3 Privileged access

11. Administrative rights are held in **separate admin accounts** that are not used for email or web browsing. Day-to-day work is done from a standard account.
12. The number of accounts with the highest privilege (Global Administrator, Super Admin, root, domain admin) is kept between two and four. One of them is a **break-glass** account: strong credentials stored sealed in the password manager or a safe, excluded from Conditional Access lockouts, with every use alerted and reviewed.
13. All privileged accounts use phishing-resistant multi-factor authentication (security key or passkey) as described in the Password and Authentication Policy.
14. Lower-privilege roles (Exchange admin, Helpdesk admin, Billing admin) are used instead of the highest role wherever the task allows. Where the platform offers time-limited or just-in-time elevation, it is used.
15. Privileged actions are logged and the log is reviewed as described in the Logging and Monitoring Policy.
16. Privileged utilities and tools that can bypass controls (remote management tools, scripting consoles with admin tokens, database admin clients) are installed only on admin workstations or privileged access devices and are not available to standard users.
17. Local administrator rights on laptops are removed from users. Where a role genuinely needs them, the exception is approved by {{Security Lead}} and reviewed quarterly.

### 4.4 Service, vendor and emergency access

18. Service accounts (used by software, not people) have one named human owner, a documented purpose, the minimum permissions, no interactive sign-in where the platform allows it, and credentials stored in a secret manager and rotated at least yearly or when a person who knew them leaves.
19. Vendor and managed service provider staff get individual named accounts, with multi-factor authentication, limited to the systems in their contract, enabled only for the engagement and reviewed quarterly. Standing vendor access is listed in the vendor register.
20. Emergency access to systems or data outside the normal process (for example to a departed employee's mailbox or during an outage) is approved by {{Security Lead}} or {{CEO}}, time-limited, logged and reviewed afterwards. **[HR or legal review]** Access to an individual's mailbox or files follows the monitoring notice in the Acceptable Use Policy and applicable employment law.

### 4.5 Access to source code and production

21. Access to source code repositories, build systems and production environments is granted by role, uses single sign-on with multi-factor authentication, and is reviewed quarterly. Production access is logged. See the Secure Development and Change Management Policy.

### 4.6 Access reviews

22. {{Security Lead}} runs an access review **quarterly** for privileged accounts, service accounts, vendor accounts and guest accounts, and **at least every six months** for all other accounts. Managers and system owners confirm each right is still needed; anything not confirmed within 10 business days is removed.
23. Reviews are recorded (who reviewed, what was removed, when) and kept as evidence for six years.
24. Accounts with no sign-in for 60 days are disabled and investigated; accounts of people who have left are deleted after the retention period.

### 4.7 Authentication and sessions

25. Authentication standards (multi-factor authentication, password strength, legacy protocol blocking, session timeouts) are set in the Password and Authentication Policy and apply to every account in scope here.

## 5. Exceptions

Exceptions follow the Information Security Policy. An exception that grants standing privileged access or shared credentials needs {{CEO}} approval and a compensating control such as extra logging and a shorter review cycle.

## 6. Enforcement

Access granted outside this policy is removed when found. Breaches by staff are handled under the Human Resources Security Policy; breaches by vendors under their contract. **[HR or legal review]**

## 7. Review

Annual review by {{Security Lead}}, and after any incident involving misuse of an account.

## 8. Related documents

POL-01 Information Security · POL-04 Password and Authentication · POL-08 Secure Development and Change Management · POL-10 Logging and Monitoring · POL-14 Vendor and Third-Party Risk · POL-16 Human Resources Security.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{Security Lead}} |
