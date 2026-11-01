---
id: POL-18
slug: remote-work-and-personal-devices-policy
title: Remote Work and Personal Devices Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: anyone who works for {{Company}} away from the office or on a device the company does not own
requirements:
  soc2: [CC6.1, CC6.6, CC6.7]
  iso27001: ["A.6.7", "A.7.7", "A.7.9", "A.8.1"]
  iso42001: []
  hipaa: ["164.310(b)", "164.310(c)", "164.312(e)(1)"]
  insurer: [remote_access, mfa]
related: [POL-02, POL-03, POL-04, POL-05, POL-17, POL-19]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Remote Work and Personal Devices Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-18 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Work at {{Company}} happens at kitchen tables, in cafés, on trains and from phones. The office walls, locks and network do not follow people home, so the protection has to be on the device, in the account and in the habits. This policy says what a device needs before it touches company data, what to do in public places, and what the company may and may not do on a personal phone or laptop. It also answers the insurer's questions about remote access and multi-factor authentication.

## 2. Scope

All work done outside {{Company}}'s premises, and all company data accessed from a device the company does not own (bring your own device), including phones used for email and chat. Contractors who use their own equipment are covered through their contract.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns this policy and the device standard, approves personal device enrolment, reviews remote access logs. |
| {{IT Lead}} or managed service provider | Configures devices and the management tooling, supports remote staff, removes company data from devices when needed. |
| Managers | Make sure their people can work securely from home and that sensitive work is done on suitable devices. |
| Everyone working remotely | Keeps their device and workplace to this standard, reports loss or theft immediately. |

## 4. Policy statements

### 4.1 Getting in: accounts and connections

1. Every route into company data from outside (the cloud tenant, remote desktop, a virtual private network, administrative consoles, the code repository) requires multi-factor authentication with a phishing-resistant method where the service offers it, under the Password and Authentication Policy. No account is exempt, including the owner's and the managed service provider's.
2. Access from outside goes to cloud services directly over encrypted connections, or through the company's virtual private network or zero-trust access service for anything hosted on the company's own network. Remote desktop, file shares and administrative ports are never exposed directly to the internet. Legacy sign-in methods that cannot do multi-factor authentication are disabled.
3. Where the identity provider supports it, sign-in rules require a device that is enrolled and compliant for access to confidential data, block sign-ins from countries where the company has no staff, and prompt for re-authentication on risky sign-ins. Remote access logs are reviewed under the Logging and Monitoring Policy.
4. Public Wi-Fi is acceptable only because every connection is encrypted; where a hotspot asks for software to be installed or shows certificate warnings, the device is disconnected and a phone hotspot is used instead. Home routers have their default administrator password changed and their firmware updated.

### 4.2 The device

5. Company-owned laptops and phones meet the device standard before they are issued: full-disk encryption on, automatic updates on, endpoint protection installed and reporting, screen lock after at most ten minutes with a strong passcode or biometric, firewall on, the user without administrator rights for daily work, remote lock and wipe enabled, and enrolment in the device management tooling so that {{IT Lead}} can see the device is compliant.
6. Personal devices may be used for work only if the owner agrees to this policy in writing, the device meets the same standard (encryption, updates, screen lock, supported operating system version, no jailbreak or root), and company data is kept inside the managed apps or work profile that the management tooling provides. Access to confidential or regulated data from personal devices is limited to those managed apps; local copies, personal cloud backups of work files, and forwarding to personal accounts are not allowed.
7. The company's management of a personal device is limited to the work profile or managed apps. **[HR or legal review]** The company can see the device's model, operating system version, compliance status and the data in the work profile; it does not read personal messages, photos, browsing or location, and it says so in the enrolment agreement. On leaving, or when the device is lost, the company removes only the work profile and the data in it.
8. Family members and friends do not use work devices or work accounts. Where a shared home computer is unavoidable, work is done only in a separate, password-protected user account and through the browser with no local downloads, and only for internal data.
9. Devices used for work are not left unattended in cars, cafés or hotel lobbies, are carried as hand luggage, and are locked away or kept in sight in shared accommodation. Screens are angled away from strangers, privacy filters are used on trains and planes, and confidential calls are not taken where they can be overheard. At home, the work area is kept so that household members and visitors do not see confidential material, and paper records are kept to a minimum and locked away or shredded.

### 4.3 Workstations handling regulated data

10. Where a role involves protected health information, payment details or other regulated data, the role description says which tasks may be done remotely and on what kind of device. These tasks are done only on a company-managed device, with the screen not visible to others, and without printing at home unless the manager has approved it and the paper is shredded afterwards.

### 4.4 When things go wrong

11. A lost or stolen device, or a device that may have been accessed by someone else, is reported to {{IT Lead}} and {{Security Lead}} within an hour of noticing, day or night, by the incident channel in the Incident Response Policy. {{IT Lead}} locks and wipes the device remotely and revokes the account's sessions. Reporting a lost device promptly is never a disciplinary matter; the loss of an encrypted, promptly wiped device is usually not a reportable breach.
12. If a personal device used for work is sold, given away, repaired by a third party or replaced, the work profile is removed first and {{IT Lead}} confirms the device is no longer enrolled.

### 4.5 Travel

13. Before international travel staff tell {{Security Lead}}; for some destinations the company issues a clean loan device and limits the data on it, and staff keep devices with them through border checks and report any inspection or seizure. Devices are not plugged into public charging ports or unknown accessories.

### 4.6 Working well remotely

14. Remote staff have what they need to work securely without workarounds: a company device where the role needs one, a password manager, a headset for confidential calls, and access to {{IT Lead}} for help. Managers check in on this at least yearly and when a person's home situation changes.

## 5. Exceptions

Follow the Information Security Policy. A personal device that cannot meet the standard is not granted access; the alternative is a company device. An unmanaged route into the company network is a Critical risk and needs {{CEO}}'s acceptance.

## 6. Enforcement

Devices that fall out of compliance lose access automatically where the tooling allows, and otherwise within one business day of detection, until fixed. Deliberate bypasses (disabling encryption or endpoint protection, moving data to personal accounts) follow the Acceptable Use Policy.

## 7. Review

{{Security Lead}} reviews this policy and the device standard yearly, after any incident involving a remote device, and when the company changes its identity provider or device management tooling.

## 8. Related documents

POL-02 Acceptable Use · POL-03 Access Control · POL-04 Password and Authentication · POL-05 Asset Management · POL-10 Logging and Monitoring · POL-13 Incident Response · POL-17 Physical and Environmental Security · POL-19 Network, Endpoint and Email Security · the device standard · the personal device enrolment agreement.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
