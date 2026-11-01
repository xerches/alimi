---
id: POL-02
slug: acceptable-use-policy
title: Acceptable Use Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: everyone who uses {{Company}} accounts, devices, networks or data
requirements:
  soc2: [CC1.1, CC1.4, CC2.2, CC6.7, CC6.8]
  iso27001: ["A.5.10", "A.5.32", "A.6.4", "A.6.8", "A.7.7", "A.8.1", "A.8.7", "A.8.19", "A.8.23"]
  iso42001: ["A.9.4"]
  hipaa: ["164.310(b)", "164.308(a)(5)"]
  insurer: [data_sharing, training]
related: [POL-01, POL-06, POL-18, POL-19, POL-22]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Acceptable Use Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-02 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

This policy sets the rules for using {{Company}}'s accounts, devices, networks, cloud services and information. It is written for everyone, not for IT. Most security incidents at companies our size start with an everyday action: a reused password, a file shared with "anyone with the link", a free app connected to the company mailbox. These rules prevent those.

## 2. Scope

Everyone who has a {{Company}} account or uses a {{Company}} device, including employees, contractors and interns, and anyone using a personal device for {{Company}} work under the Remote Work and Personal Devices Policy. It covers company systems wherever they are used: the office, home, travel or a customer site.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| Everyone | Reads and follows this policy, asks before doing something it does not cover, and reports mistakes quickly. |
| Managers | Make sure new team members have read this policy, and set the example. |
| {{Security Lead}} | Keeps the policy current, answers questions, keeps the list of approved apps and handles reports. |
| {{IT Lead}} or managed service provider | Configures systems so the safe path is the default (approved apps, sharing limits, device protection). |

## 4. Policy statements

### 4.1 Your account is yours alone

1. Use your own account for all work. Never share your password, your multi-factor authentication codes or your signed-in session with anyone, including IT. IT will never ask for your password.
2. Approve a multi-factor authentication prompt only when you are signing in yourself at that moment. An unexpected prompt means someone has your password: deny it and report it the same day.
3. Lock your screen when you step away. Devices lock automatically after 10 minutes at most.
4. Passwords follow the Password and Authentication Policy: long, unique, kept in the company password manager.

### 4.2 Company devices

5. Do work on company-managed devices, or on a personal device that meets the Remote Work and Personal Devices Policy. Do not do {{Company}} work on a family computer or a borrowed device.
6. Do not turn off, remove or work around security software (endpoint protection, disk encryption, updates, device management). If it gets in the way, tell IT.
7. Install only software that IT has approved or that comes from the company app catalogue. Browser extensions count as software.
8. Keep devices with you or locked away. A lost or stolen device is reported within one hour, day or night, so it can be wiped.

### 4.3 Information and sharing

9. Handle information according to its classification in the Data Classification and Handling Policy. When in doubt, treat it as Confidential.
10. Share files from the company's cloud storage with named people, not with "anyone with the link", unless the information is Public. Set an expiry on external shares.
11. Do not send company information to a personal email address, personal cloud storage or a personal messaging app, and do not set up automatic forwarding of company email to any outside address.
12. Do not take Confidential or Restricted information with you when you leave a project or the company, and return or delete it when asked.
13. Printing Confidential information is a last resort; collect it immediately and shred it when done. Keep desks clear of Confidential papers when you leave.

### 4.4 Email, messaging and the web

14. Treat unexpected requests to pay, change bank details, buy gift cards or share credentials as suspicious even when they appear to come from a colleague or executive. Verify by a second channel you already trust (a known phone number, not a number in the message) before acting. This is the single most common fraud against companies our size.
15. Report suspicious messages with the report button or to {{Security Lead}}. Reporting a message that turns out to be fine is always welcome.
16. Do not open attachments or follow links you were not expecting until you have checked the sender.
17. Company email and chat are for business. Limited personal use is fine as long as it does not interfere with work, break the law or breach this policy.
18. Web use must be lawful and professional. {{Company}} filters known malicious and inappropriate sites; attempts to bypass the filter are a breach.

### 4.5 Cloud apps and integrations

19. Connect a third-party app, add-in or integration to your {{Company}} account (for example "Sign in with Google" or an Outlook add-in that reads your mailbox) only if it is on the approved list or {{Security Lead}} has approved it. Such apps can read mail and files silently.
20. Do not sign up for new business tools with your company email without telling {{Security Lead}}; a tool that holds company data has to be on the vendor list.
21. AI tools follow the AI Acceptable Use Policy: no Confidential or Restricted information in tools that are not approved for it.

### 4.6 Legal and ethical use

22. Respect copyright and licence terms: no pirated software, no copying of licensed material beyond the licence, no use of customer or third-party material outside the contract.
23. Do not access, copy or share information you do not need for your job, even if you technically can. Access is not permission.
24. Do not use {{Company}} systems to harass, discriminate, defame or break the law, or to attempt to break into any system, including our own, without written authorisation from {{Security Lead}}.
25. When you speak about {{Company}} on social media, make clear the views are your own and do not share Confidential information.

### 4.7 Monitoring and privacy

26. {{Company}} systems are company property. {{Company}} logs system activity (sign-ins, admin actions, email flow, file sharing, device health) to protect the business, investigate incidents and meet legal obligations. Logs are reviewed as described in the Logging and Monitoring Policy, not to watch individuals without cause. **[HR or legal review]** Confirm the monitoring notice meets the privacy and employment law of every place {{Company}} employs people, and add any consent language required.
27. Personal content on a personal device is not accessed by {{Company}}; only the company data and apps are managed, as described in the Remote Work and Personal Devices Policy.

### 4.8 Reporting

28. Report security events, mistakes and near misses to {{Security Lead}} as soon as you notice them, even if you caused them. Fast reporting turns an incident into a non-event; the response is never worse for the person who reported promptly and honestly.

## 5. Exceptions

Ask {{Security Lead}} before you need the exception, not after. Exceptions are granted in writing for a defined period under the Information Security Policy.

## 6. Enforcement

Breaches are handled under the disciplinary process in the Human Resources Security Policy, up to and including dismissal and, where the law was broken, referral to the authorities. **[HR or legal review]** Contractors are subject to the terms of their agreement.

## 7. Review

{{Security Lead}} reviews this policy annually and after incidents that show a rule is missing or unclear. Everyone re-acknowledges the policy annually.

## 8. Related documents

POL-01 Information Security · POL-04 Password and Authentication · POL-06 Data Classification and Handling · POL-16 Human Resources Security · POL-18 Remote Work and Personal Devices · POL-19 Network, Endpoint and Email Security · POL-22 AI Acceptable Use.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
