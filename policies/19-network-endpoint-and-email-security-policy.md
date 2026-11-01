---
id: POL-19
slug: network-endpoint-and-email-security-policy
title: Network, Endpoint and Email Security Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: every computer, phone, server, network and email account that {{Company}} owns or manages
requirements:
  soc2: [CC6.1, CC6.6, CC6.7, CC6.8, CC7.1]
  iso27001: ["A.8.1", "A.8.7", "A.8.9", "A.8.18", "A.8.19", "A.8.20", "A.8.21", "A.8.22", "A.8.23"]
  iso42001: []
  hipaa: ["164.308(a)(5)", "164.312(e)(1)"]
  insurer: [edr, email_security, remote_access]
related: [POL-03, POL-04, POL-05, POL-09, POL-10, POL-18]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Network, Endpoint and Email Security Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-19 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Almost every attack on a company of {{Company}}'s size arrives through email or lands on a laptop. This policy sets the technical baseline for the three places where that can be stopped: the devices people use (endpoints), the networks they connect through, and the email system. It is written to be checkable: most of these statements can be verified by the company's security scanning tooling or a screenshot, which is what the insurer, a customer or an auditor will ask for.

## 2. Scope

Laptops, desktops, phones, tablets and any servers {{Company}} owns or manages; the office network and Wi-Fi; the email and collaboration tenant and its domains; and the security tools that protect them. Personal devices are covered by the Remote Work and Personal Devices Policy, cloud infrastructure that the company builds on by the Secure Development and Change Management Policy.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns this policy and the configuration baselines, reviews the tooling's findings, approves exceptions. |
| {{IT Lead}} or managed service provider | Implements and maintains the baselines, the endpoint protection, the network equipment and the email security settings; responds to alerts. |
| Everyone | Does not disable or work around the protections, reports suspicious email and odd device behaviour. |

## 4. Policy statements

### 4.1 Endpoints

1. Every company device is built from a documented, hardened baseline before use: supported operating system, full-disk encryption, automatic updates, host firewall on, unnecessary services and software removed, screen lock, and no standing administrator rights for the user. Baselines follow a recognised benchmark adapted to the company's needs and are reviewed yearly. Devices are enrolled in management tooling that reports whether they still match the baseline.
2. Every laptop, desktop and server runs endpoint detection and response (EDR) software, a protection tool that watches for malicious behaviour as well as known malware, blocks it, and lets {{IT Lead}} investigate and isolate the device. It is centrally managed, always on, tamper-protected so that users cannot stop it, and its alerts are reviewed under the Logging and Monitoring Policy. Plain antivirus alone does not meet this statement.
3. Only software from the approved list, from the official app store or installed by {{IT Lead}} runs on company devices. Application control blocks unknown executables and scripts where the device supports it. Browser extensions are limited to an approved list. Staff do not install remote access tools, personal file-sync clients, pirated software or tools that disable protections.
4. Removable media (USB drives, memory cards) are blocked or read-only on company devices unless {{Security Lead}} approves a specific need, in which case the media is company-issued and encrypted under the Data Classification and Handling Policy.
5. Devices are patched under the Vulnerability and Patch Management Policy and protected by the Password and Authentication Policy. Devices that fall out of compliance are blocked from company data until fixed, under the Access Control Policy.

### 4.2 Networks

6. The office network sits behind a business-grade firewall that blocks all inbound connections by default and permits outbound traffic by policy; its firmware is kept current, its administrator account has multi-factor authentication and is not reachable from the internet, and its configuration is backed up and documented. Default passwords on every network device are changed before installation.
7. The network is divided so that a compromise in one part does not reach the rest: staff devices, guest and visitor Wi-Fi, printers and smart devices (cameras, screens, thermostats) and any servers are on separate networks or virtual networks, with only the connections between them that the business needs. Guest Wi-Fi reaches only the internet.
8. Wi-Fi uses current encryption (WPA3, or WPA2-Enterprise where WPA3 is unavailable) with per-user authentication for the staff network; shared Wi-Fi passwords are used only for the guest network and changed at least quarterly and when staff leave. Networks the company does not control are treated as hostile under the Remote Work and Personal Devices Policy.
9. Anything the company hosts itself and must reach from the internet (a website, an application) sits behind a reverse proxy or web application firewall with current certificates; administrative interfaces are reachable only through the virtual private network or zero-trust access service. Domain name records are protected by multi-factor authentication at the registrar and reviewed yearly for stale entries that an attacker could take over.
10. Network and security devices log to the central store, their time is synchronised, and the diagrams and inventory of the network are kept current in the asset register.

### 4.3 Email and collaboration

11. Every domain the company owns, including those used only for marketing or redirects, publishes the three email authentication records: SPF listing only the services allowed to send, DKIM signing for every sending service, and a DMARC policy at "quarantine" or "reject" with reports sent to a mailbox {{IT Lead}} reviews. Domains that never send email publish a reject-everything policy. These settings are checked by the security scanning tooling.
12. The email tenant's anti-phishing, anti-malware and safe-attachment features are on at the recommended or strict level: links are rewritten and checked at click time, attachments are detonated before delivery, impersonation protection covers the executives and the finance team, and external emails carry a visible banner. Automatic forwarding to outside addresses is blocked at the tenant level, and mailbox rules that forward or delete are alerted on.
13. Legacy sign-in protocols that bypass multi-factor authentication (basic authentication for IMAP, POP, SMTP and older clients) are disabled. Third-party applications may connect to the tenant only with administrator consent after review under the Vendor and Third-Party Risk Policy; user consent to new apps is turned off.
14. Confidential information sent by email to outside parties is protected under the Data Classification and Handling Policy: encrypted message or a link to a protected file, never an unprotected attachment. Transmissions of regulated data use the tenant's encryption or the recipient's secure portal.
15. Staff report suspicious messages with the report button or to the incident channel rather than deleting them, so that {{IT Lead}} can remove copies from other mailboxes and block the sender. Requests to change bank details, to buy gift cards, or to act urgently on behalf of an executive are treated as fraud until verified by a call to a known number, under the payment verification procedure. Training on these scams is part of the Human Resources Security Policy.
16. Web browsing from company devices goes through DNS or web filtering that blocks known malicious sites and newly registered domains, and warns on categories the company has chosen to block. The filter's logs are kept under the Logging and Monitoring Policy and used for investigation, not for monitoring individuals' browsing without cause.

### 4.4 Checking that it holds

17. {{Security Lead}} runs the security scanning tooling against the tenant at least monthly and reviews the configuration baselines, EDR coverage, firewall rules and email authentication records at least quarterly. Any device without EDR, any domain without DMARC, and any account with legacy authentication is treated as a finding with a seven-day fix target.

## 5. Exceptions

Follow the Information Security Policy. A device that cannot run EDR (an embedded system, an old machine that runs one piece of equipment) is isolated on its own network segment, has no email or internet access, and is recorded as a risk with a replacement date.

## 6. Enforcement

Protections turned off without approval are turned back on and the matter raised with the person's manager. Devices and accounts that cannot be brought into compliance are removed from service. Deliberate circumvention follows the Acceptable Use Policy.

## 7. Review

{{Security Lead}} reviews this policy and the baselines yearly, after any malware or email-based incident, and when the company changes its email tenant, endpoint tooling or network equipment.

## 8. Related documents

POL-03 Access Control · POL-04 Password and Authentication · POL-05 Asset Management · POL-06 Data Classification and Handling · POL-09 Vulnerability and Patch Management · POL-10 Logging and Monitoring · POL-14 Vendor and Third-Party Risk · POL-18 Remote Work and Personal Devices · the device and network baselines · the approved software list.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
