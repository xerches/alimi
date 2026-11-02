---
slug: pilot-authorization-letter
kind: compact
title: Pilot Authorization Letter
---
> **DRAFT. Not legal advice. Review by a Massachusetts attorney before use.**

# Pilot authorization letter

*On {{Client}} letterhead. One page. Signed before any access is created.*

{{Effective Date}}. From {{Client}}, {{Client Address}}, to {{Alimi Entity}} ("Alimi"), {{Alimi Address}}.

**1. Authorization.** {{Client}} authorizes Alimi to run a **read-only** security assessment of our {{Tenant}} environment for the domain **{{Tenant Domain}}**, as a free pilot, between {{Start Date}} and {{End Date}}.

**2. Scope.** The assessment runs the checks in the attached appendix (Alimi's published check list for {{Tenant}}: multi-factor authentication, administrator accounts, legacy sign-in, external forwarding, sharing, audit logging, email authentication and related settings). It reads configuration and audit data only, never the content of email, files or chats, and changes nothing. Anything else needs a new signed letter.

**3. Access.** Our administrator creates the access (an app registration or service account) with exactly the read-only permissions in the appendix, and removes it by {{End Date}} or within one business day of either side stopping. Alimi receives no administrator account and no password. **[Attorney review]** Confirm this gives Alimi the authorization that computer-access laws require.

**4. Data.** Alimi runs the scan from an encrypted computer it controls and keeps the results (findings and a configuration snapshot with no email or file content) only there. It stores no credentials or tokens. The report goes to {{Client Contact}}; Alimi deletes its copies 30 days after delivery unless we ask in writing to keep them, keeps the results confidential, and uses nothing publicly without a separate signed permission.

**5. Terms.** **No fee**, and no obligation on either side to buy or sell anything afterwards. **Either side may stop** the pilot at any time by email to the contacts below. The report describes what the scanner found on the day it ran: information to act on, not a guarantee of security, insurability or compliance, and Alimi is not responsible for decisions we make on it. **[Attorney review]** Disclaimer wording. {{Client}} confirms it owns or controls {{Tenant Domain}} and may grant this access.

**6. Contacts.** {{Client}}: {{Client Contact}}. Alimi: {{Alimi Signatory}}, {{Contact Email}}, {{Contact Phone}}.

Signed for {{Client}}: ______________________ {{Client Signatory}}, {{Client Title}} Date: ____________

Acknowledged for Alimi: ______________________ {{Alimi Signatory}} Date: ____________

*Appendix: the check list and read-only permissions for {{Tenant}}, printed from `alimi-scan checks` and `alimi-scan permissions` on the day of signing.*
