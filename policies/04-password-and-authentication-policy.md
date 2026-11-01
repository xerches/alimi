---
id: POL-04
slug: password-and-authentication-policy
title: Password and Authentication Policy
version: "1.0"
status: template
owner_role: "{{Security Lead}}"
approver_role: "{{CEO}}"
review_cycle: annual
applies_to: every account and credential used to reach {{Company}} systems or data
requirements:
  soc2: [CC6.1, CC6.6]
  iso27001: ["A.5.17", "A.8.5"]
  iso42001: []
  hipaa: ["164.312(d)", "164.308(a)(5)"]
  insurer: [mfa, remote_access]
related: [POL-03, POL-07, POL-18, POL-19]
---
> **TEMPLATE. Adapt before adopting. Sections marked [HR or legal review] need a human reviewer.**

# {{Company}} Password and Authentication Policy

| Field | Value |
| --- | --- |
| Policy ID | POL-04 |
| Version | 1.0 |
| Owner | {{Security Lead}} |
| Approved by | {{CEO}} |
| Effective date | {{Effective Date}} |
| Review cycle | Annual |

## 1. Purpose

Stolen or guessed passwords are the way into most companies. This policy makes a password alone insufficient to reach anything that matters, and makes the passwords themselves hard to steal or guess. It answers the insurer's first question: is multi-factor authentication enforced for everyone, including email, remote access and administrators?

## 2. Scope

All accounts used to reach {{Company}} systems or data: staff, contractor, administrator, service, vendor and shared accounts; the identity provider, email, cloud services, VPN or zero-trust access, network equipment, applications and devices. It also covers API keys, tokens and other secrets used by software.

## 3. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| {{Security Lead}} | Owns the policy, sets the technical standards and checks enforcement with the workspace security scan. |
| {{IT Lead}} or managed service provider | Configures the identity provider and systems to enforce these rules by default, and runs the password manager. |
| Everyone | Uses the password manager, keeps credentials secret and reports anything unusual. |

## 4. Policy statements

### 4.1 Multi-factor authentication (MFA)

1. MFA (a second proof of identity beyond the password, such as an authenticator app prompt, a security key or a passkey) is **enforced** for every account that can sign in: all users, all administrators, all contractors and all vendor accounts. "Available" or "encouraged" is not enforced; the identity provider policy requires it and the scan proves it.
2. MFA covers every entry point: email and the workspace suite, remote access, cloud consoles, source code, finance and HR systems, the password manager itself and any application reached with single sign-on.
3. Administrators and finance staff use **phishing-resistant** MFA: a FIDO2 security key or a passkey. SMS and voice codes are not permitted for these roles and are a last resort for anyone else.
4. Number matching or equivalent is turned on for push notifications so that an attacker cannot get in by sending prompts until someone taps approve. Staff deny unexpected prompts and report them.
5. Legacy sign-in protocols that cannot do MFA (POP, IMAP, SMTP AUTH, basic authentication) are blocked at the tenant. Exceptions for a scanner or a printer are approved by {{Security Lead}}, limited to one account and reviewed quarterly.
6. MFA registration happens on the first day, before any other access. Re-registration after a lost device requires identity verification by IT using a method that an attacker on email cannot pass (video call, in person, or a code sent to a manager).

### 4.2 Single sign-on and the password manager

7. Applications are connected to the identity provider for single sign-on (SSO) wherever they support it, so that one well-protected identity replaces many passwords and offboarding removes everything at once.
8. Where SSO is not possible, credentials are generated and stored in the company password manager, shared through the manager's vaults rather than by email or chat, and never stored in browsers' built-in managers on unmanaged devices, in spreadsheets or in notes.

### 4.3 Password standards

9. Passwords are at least **14 characters** for people and at least 32 random characters for service accounts and shared credentials. Length matters more than symbols; passphrases are encouraged.
10. Passwords are unique: never reused across systems, and never the same as a personal password.
11. Commonly used and breached passwords are blocked by the identity provider's banned-password feature; a password that appears in a known breach is changed immediately.
12. There is **no scheduled password rotation** for people. Passwords are changed when there is reason to believe they are compromised, when someone who knew a shared credential leaves, and after an incident. Service account and shared credentials are rotated at least yearly.
13. Initial and reset passwords are temporary, delivered by a channel other than the account's own email, and must be changed at first use.
14. Password hints, security questions and knowledge-based answers are not used as authentication.

### 4.4 Sessions and lockout

15. Accounts lock or throttle after 10 failed attempts and unlock after a delay or by IT, so guessing is slow and visible.
16. Devices lock after 10 minutes of inactivity and require re-authentication. Administrative sessions time out after at most 8 hours, and sensitive applications after a period set by the system owner.
17. Sign-in is allowed only from managed or compliant devices for Confidential and Restricted systems where the identity provider supports device conditions; sign-ins from unexpected countries or impossible travel are blocked or challenged.

### 4.5 Secrets used by software

18. API keys, tokens, certificates and service passwords are stored in a secret manager or the password manager, never in source code, configuration files in repositories, chat messages or tickets. Secret scanning runs on repositories under the Secure Development and Change Management Policy.
19. Each secret has an owner, a purpose and a rotation date. Secrets are rotated when a person with access leaves and at least yearly.

### 4.6 Vendors and remote access

20. Remote access to any {{Company}} system (VPN, zero-trust access, remote desktop, management consoles) requires MFA and a company-managed or compliant device as described in the Network, Endpoint and Email Security Policy.
21. Vendor and managed service provider accounts meet every rule in this policy, including phishing-resistant MFA for any privileged access.

### 4.7 Recovery and help

22. Account recovery methods (backup codes, recovery email, recovery phone) are set up at onboarding, kept current, and cannot point at a personal address for administrator accounts.
23. The helpdesk verifies identity before any password reset or MFA change, using a method documented in the operating procedure, and records the request. Resets requested by email alone are refused.

## 5. Exceptions

Follow the Information Security Policy. An exception to MFA is granted only for a non-interactive service account or a device that cannot support it, with a compensating control (IP restriction, limited permissions, extra logging), approval by {{Security Lead}} and quarterly review. No exceptions are granted for people.

## 6. Enforcement

Accounts that fall outside these standards are brought into line or disabled. Sharing credentials or disabling MFA is a serious breach under the Human Resources Security Policy. **[HR or legal review]**

## 7. Review

{{Security Lead}} reviews this policy annually and when the identity provider adds stronger options (for example when passkeys become available for all users).

## 8. Related documents

POL-02 Acceptable Use · POL-03 Access Control · POL-07 Cryptography and Key Management · POL-08 Secure Development and Change Management · POL-18 Remote Work and Personal Devices · POL-19 Network, Endpoint and Email Security.

## 9. Revision history

| Version | Date | Change | Author |
| --- | --- | --- | --- |
| 1.0 | {{Effective Date}} | First version from the alimi policy library template | {{Security Lead}} |
