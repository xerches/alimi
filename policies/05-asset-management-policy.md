---
id: POL-05
slug: asset-management-policy
title: Asset Management Policy
version: "1.0"
status: template
owner_role: "{{IT Lead}}"
approver_role: "{{Security Lead}}"
review_cycle: annual
applies_to: all hardware, software, cloud services and information assets owned or used by {{Company}}
requirements:
  soc2: [CC6.1, CC6.5, CC6.7]
  iso27001: ["A.5.9", "A.5.11", "A.7.9", "A.7.10", "A.7.13", "A.7.14", "A.8.1", "A.8.9"]
  iso42001: ["A.4.2", "A.4.4", "A.4.5"]
  hipaa: ["164.310(d)(1)"]
  insurer: [edr]
related: [POL-06, POL-17, POL-19, POL-20]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Asset Management Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-05 |
| Version | 1.0 |
| Owner | {{IT Lead}} |
| Approved by | {{Security Lead}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

You cannot protect what you do not know you have. This policy keeps an accurate list of {{Company}}'s devices, software, cloud services and information, names an owner for each, and sets the rules for an asset's life from purchase to disposal. The inventory is also what proves to an insurer that endpoint protection really covers every device.

## 2. Scope

Laptops, desktops, phones and tablets used for work (company-owned, and personal devices enrolled under the Remote Work and Personal Devices Policy); servers and network equipment; removable media; software licences and SaaS subscriptions; cloud accounts and tenants; and the information assets (databases, file shares, key documents) that live on them. AI systems and the data, tools and compute they use are inventoried here too, with detail in the AI Governance Policy.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{IT Lead}} or managed service provider | Keeps the inventory, enrols devices, tracks licences, handles repairs and disposal. |
| {{Security Lead}} | Approves the policy, checks the inventory against the endpoint protection and device management consoles quarterly, and approves exceptions. |
| Asset owners | Each system or information asset has a named owner who decides its classification, who may use it and when it is retired. |
| {{Finance Lead}} | Records purchases and disposals and reconciles with the inventory annually. |
| Everyone | Uses assets as issued, keeps them safe, reports loss or damage within one hour, and returns them when asked. |

## 4. Policy statements

### 4.1 The inventory

1. {{IT Lead}} keeps a single inventory of hardware, software, cloud services and information assets. For each asset it records: what it is, a unique identifier (serial number, tag or tenant ID), the owner, the user or custodian, the location or hosting provider, the classification of the data it holds, the date acquired, the support or end-of-life date, and its status.
2. Device records come from the device management tool automatically wherever possible; manual entries are the exception and are reviewed quarterly.
3. The inventory is reconciled quarterly against the device management console, the endpoint protection console and the identity provider's device list. A device in one list and not the others is investigated the same week.
4. The SaaS and cloud inventory is reconciled quarterly against sign-in logs and the OAuth app report from the workspace security scan, so that tools adopted without IT's knowledge are found and either approved or removed.

### 4.2 Ownership and classification

5. Every asset has one named owner. Ownership moves with the role, and {{IT Lead}} updates the record when people join, move or leave.
6. Owners classify the information their assets hold under the Data Classification and Handling Policy; the device or service is protected to the level of the most sensitive data on it.

### 4.3 Company devices

7. Work is done on company-managed devices enrolled in device management, with the baseline in the Network, Endpoint and Email Security Policy applied before the device is issued: disk encryption, endpoint detection and response, automatic updates, screen lock, and no local administrator rights.
8. Devices are issued against a signed receipt that states the return obligation. Users may not lend company devices to anyone, including family.
9. Devices used outside the office follow the Remote Work and Personal Devices Policy: kept in sight or locked away, never left in a vehicle, and reported within one hour if lost or stolen so they can be remotely wiped.
10. Repairs and maintenance use vendors approved by {{IT Lead}}. A device leaving {{Company}}'s control for repair has its data encrypted and, where the fault allows, wiped first.

### 4.4 Software and licences

11. Software is installed from the company app catalogue or by IT. Installed software is inventoried by the device management tool and compared with licence entitlements at least yearly.
12. Unsupported or end-of-life software and operating systems are not used on company devices. {{IT Lead}} tracks end-of-support dates and plans replacements at least six months ahead.
13. Open-source and free software follows the same approval as paid software: known source, current version, licence compatible with its use.

### 4.5 Removable media

14. USB drives and other removable media are not used for Confidential or Restricted information unless encrypted and approved by {{Security Lead}}. Company cloud storage is the default way to move files.
15. Media found or received from outside is not plugged into company devices until IT has checked it.

### 4.6 Configuration baselines

16. Each type of asset (laptop, server, network device, SaaS tenant) has a documented secure configuration baseline, applied by device management or infrastructure-as-code where possible. Drift from the baseline is detected and corrected; the workspace security scan is the baseline check for the Microsoft 365 or Google Workspace tenant.

### 4.7 Return, reuse and disposal

17. When a person leaves or changes role, {{HR Lead}} and the manager make sure all assets (devices, tokens, keys, badges, media, documents) are returned on or before the last day, and {{IT Lead}} records the return.
18. Before a device or drive is reused, it is wiped with a method that prevents recovery: cryptographic erase of an encrypted drive, or a full overwrite following a recognised standard such as NIST SP 800-88, with the result recorded.
19. Devices and media that cannot be wiped are physically destroyed by an approved vendor who provides a certificate of destruction. Disposal records are kept for six years.
20. Cloud services and SaaS subscriptions are offboarded under the Vendor and Third-Party Risk Policy: data exported or deleted, accounts removed, the entry in the inventory closed.

## 5. Exceptions

Follow the Information Security Policy. Unmanaged devices and unencrypted media are exceptions that need {{Security Lead}} approval, a compensating control and a quarterly review.

## 6. Enforcement

Assets missing from the inventory, unenrolled devices and unapproved software are brought into line or removed from the network. Repeated or deliberate breaches follow the Human Resources Security Policy.

## 7. Review

{{IT Lead}} reviews this policy annually; {{Security Lead}} reviews the inventory reconciliation evidence quarterly.

## 8. Related documents

POL-06 Data Classification and Handling · POL-14 Vendor and Third-Party Risk · POL-16 Human Resources Security · POL-17 Physical and Environmental Security · POL-18 Remote Work and Personal Devices · POL-19 Network, Endpoint and Email Security · POL-20 Data Retention and Disposal · POL-23 AI Governance.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the Alimi policy library template | {{IT Lead}} |
