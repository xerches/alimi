# Alimi scanner

Read-only security checks for Microsoft 365 and Google Workspace. It reads a tenant through Microsoft Graph or the Google Admin SDK, runs the checks listed in `config/checks.yaml`, and writes a findings file that the report generator and, later, the platform consume.

**Mock mode is the default.** Nothing here touches a real tenant unless you pass `--tenant --authorized`, and that flag is your statement that you own the tenant or hold a signed pilot authorization letter.

## Run it

```bash
cd tools/scanner
pip install -e ".[dev]"            # once
alimi-scan m365                     # mock scan of the Microsoft 365 "pass" fixture, table on screen, JSON in ./out/
alimi-scan gws                      # same for Google Workspace
alimi-scan gws --fixture fail       # a tenant that trips every check
alimi-scan checks                   # every check in checks.yaml and whether it is implemented
alimi-scan permissions              # the Graph permissions a real Microsoft 365 scan needs
alimi-scan permissions -p gws       # the OAuth scopes a real Google Workspace scan needs
pytest                              # 98 tests, no network
```

Output goes to `./out/` (or `$ALIMI_OUTPUT_DIR`), which is git-ignored. Each run writes `<platform>-<timestamp>.findings.json`; add `--save-snapshot` to also keep the raw snapshot the checks ran on, which is handy for re-running checks later with `--snapshot <file>`.

## Scan a real Microsoft 365 tenant

Only tenants you own or that are covered by a signed pilot authorization letter from `/templates`.

1. **Create the app registration.** Entra admin center, App registrations, New registration. Name it `Alimi scanner (read-only)`, single tenant, no redirect URI.
2. **Add application permissions** (API permissions, Add a permission, Microsoft Graph, *Application permissions*), then click **Grant admin consent**. All of them are read-only:

| Permission | Used for | Graph calls |
| --- | --- | --- |
| `Organization.Read.All` | tenant name and verified domains | `GET /organization` |
| `User.Read.All` | user list: member or guest, enabled, mailbox present, sign-in activity | `GET /users` |
| `AuditLog.Read.All` | MFA registration report, last sign-in dates, legacy-auth sign-ins, audit log availability | `GET /reports/authenticationMethods/userRegistrationDetails`, `/auditLogs/signIns`, `/auditLogs/directoryAudits` |
| `Policy.Read.All` | Conditional Access policies and the Security Defaults switch | `GET /identity/conditionalAccess/policies`, `/policies/identitySecurityDefaultsEnforcementPolicy` |
| `RoleManagement.Read.Directory` | who holds Global Administrator and other privileged roles | `GET /directoryRoles?$expand=members` |
| `MailboxSettings.Read` | inbox rules that forward or redirect mail | `GET /users/{id}/mailFolders/inbox/messageRules` |
| `SharePointTenantSettings.Read.All` | tenant sharing level (anyone links) | `GET /admin/sharepoint/settings` |
| `SecurityEvents.Read.All` | Microsoft Secure Score | `GET /security/secureScores` |

   `alimi-scan permissions` prints the same table from the code, so the two cannot drift.

3. **Create a client secret** (Certificates and secrets, New client secret, 90 days). Copy it once.
4. **Fill in `.env`** from `.env.example` at the repo root: `M365_TENANT_ID`, `M365_CLIENT_ID`, `M365_CLIENT_SECRET`. `.env` is git-ignored and gitleaks blocks a commit that contains a secret anyway.
5. Run:

```bash
alimi-scan m365 --tenant --authorized
```

A missing permission does not stop the scan. The connector records a note, leaves that part of the snapshot empty, and the affected check reports `error` with the permission to grant. Nothing is guessed.

**Optional licence note.** Sign-in activity and the sign-in log need Entra ID P1, which Microsoft 365 Business Premium includes. Without it the scanner still runs; the legacy-auth check relies on the policy alone and says so, and guest inactivity is measured from account creation.

## Scan a real Google Workspace tenant

Same rule: only tenants you own or that a signed pilot letter covers. Google has no "application permission" concept; instead a **service account** is allowed to act as an admin (and, for Gmail settings, as each user) through **domain-wide delegation**, limited to the scopes below. Every scope is read-only.

1. **Create a Google Cloud project** (any name, for example `alimi-scanner`) at console.cloud.google.com. Billing is not needed; these APIs are free.
2. **Enable four APIs** in APIs & Services, Library: *Admin SDK API*, *Cloud Identity API*, *Gmail API* and (already part of Admin SDK) the Reports API.
3. **Create a service account** (IAM & Admin, Service Accounts, Create). No Cloud IAM roles are needed. Open it, Keys, Add key, JSON. Save the file **outside the repo** (for example `~/.config/alimi/gws-service-account.json`); `.gitignore` also blocks `service-account*.json`. Copy the service account's **Client ID** (a long number) from its details page.
4. **Delegate the scopes** in the Workspace Admin console: Security, Access and data control, API controls, Manage Domain Wide Delegation, Add new. Paste the Client ID and these scopes, comma-separated:

| Scope (under `https://www.googleapis.com/auth/`) | Used for | Calls |
| --- | --- | --- |
| `admin.directory.customer.readonly` | organization name and primary domain | Directory API `customers.get` |
| `admin.directory.domain.readonly` | verified domains, for the SPF, DKIM and DMARC lookups | Directory API `domains.list` |
| `admin.directory.user.readonly` | user list: suspended, super admin, 2-Step Verification enrolled and enforced, org unit, last login | Directory API `users.list` |
| `admin.reports.audit.readonly` | third-party OAuth grants (token events) and login and admin audit log availability | Reports API `activities.list` for `token`, `login`, `admin` |
| `cloud-identity.policies.readonly` | 2-Step Verification enforcement, less secure apps, Gmail auto-forwarding, Drive external sharing, Marketplace access | Cloud Identity Policy API `policies.list` |
| `gmail.readonly` | each user's automatic forwarding address and filters that forward mail | Gmail API `users.settings.getAutoForwarding`, `users.settings.filters.list` (as each user) |

   `alimi-scan permissions -p gws` prints the same table from the code.

5. **Fill in `.env`**: `GWS_SERVICE_ACCOUNT_FILE` (path to the JSON key), `GWS_DELEGATED_ADMIN` (a super admin's address; the service account acts as this admin for the directory, reports and policy calls), `GWS_CUSTOMER_ID` (leave `my_customer`), and optionally `GWS_APPROVED_CLIENT_IDS`, a comma-separated list of OAuth client ids the company has knowingly approved, so they do not count against the third-party app check. The same list can be given per run with `--approved-app <client id>`.
6. Run:

```bash
alimi-scan gws --tenant --authorized
```

As with Microsoft 365, a scope that was not delegated does not stop the scan: the connector records a note, the field stays empty, and the affected check reports `error` naming the scope. Gmail settings are read by impersonating each active user; a user without a Gmail licence (a Cloud Identity account) is skipped with a note, and the per-run cap is 500 mailboxes.

**Licence note.** Cloud Identity Free (no Gmail or Drive) is enough for the user, policy and audit checks; the forwarding check needs Gmail licences, and the Drive sharing policy only exists on a Workspace edition.

## What the checks read

### Microsoft 365

| Check | Reads | Passes when |
| --- | --- | --- |
| `m365.mfa.coverage` | userRegistrationDetails for enabled members | every enabled member is MFA-registered |
| `m365.conditional_access.present` | Conditional Access policies | an enabled policy requires MFA (or an authentication strength) for all users and all apps |
| `m365.legacy_auth.blocked` | Conditional Access, Security Defaults, successful sign-ins by legacy clients in 30 days | something blocks legacy auth and no legacy sign-in succeeded |
| `m365.security_defaults` | Security Defaults switch, Conditional Access | Security Defaults on, or CA covers MFA for all and blocks legacy auth |
| `m365.admins.global_count` | Global Administrator members, whether each has a mailbox | 2 to 4 admins, none with a mailbox |
| `m365.admins.mfa` | members of 15 privileged roles, their registration | every privileged account is MFA-registered |
| `m365.forwarding.external` | inbox rules of every mailbox, outbound forwarding policy | no rule forwards outside the verified domains and the tenant blocks auto-forwarding (the tenant setting needs a screenshot, see gaps) |
| `m365.email_auth.dmarc` | public DNS: SPF TXT, `selector1/2._domainkey` CNAMEs, `_dmarc` TXT | SPF present, DKIM CNAMEs present, DMARC `p=quarantine` or `reject` on every custom domain |
| `m365.sharing.anonymous_links` | SharePoint `sharingCapability` | anyone links off, or expiring within 30 days |
| `m365.guests.review` | guests, last sign-in or creation date | no guest inactive for 90 days |
| `m365.audit.enabled` | directory audit availability, unified audit log state | unified audit log on with 90 days retention (state needs a Purview screenshot, see gaps) |
| `m365.secure_score` | latest Secure Score | above 60% of maximum |

### Google Workspace

| Check | Reads | Passes when |
| --- | --- | --- |
| `gws.2sv.enforced` | each active user's `isEnrolledIn2Sv` and `isEnforcedIn2Sv`, the 2-Step Verification enforcement policy per org unit | every active user is enrolled and under enforcement, and no org unit is left unenforced |
| `gws.admins.super_count` | active users with `isAdmin` | 2 to 4 super admins, every one enrolled in 2-Step Verification |
| `gws.forwarding.external` | each user's automatic forwarding address and filters with a forward action, the tenant auto-forwarding policy | nothing forwards outside the verified domains and the policy disables automatic forwarding (an unreadable policy asks for a screenshot) |
| `gws.email_auth.dmarc` | public DNS: SPF TXT, `google._domainkey` TXT, `_dmarc` TXT | SPF present, DKIM record present, DMARC `p=quarantine` or `reject` on every custom domain |
| `gws.oauth.third_party` | `token` `authorize` events from the last 180 days, grouped by client id with their scopes and user count, plus your approved list | no unapproved app holds a mail, Drive, calendar, contacts or directory scope, and unconfigured third-party apps are restricted (that setting needs a screenshot, see gaps) |
| `gws.drive.external_sharing` | the Drive external sharing policy, taking the loosest org unit | files cannot be published to anyone on the web, and external sharing is allowlisted, disallowed, or at least warned |
| `gws.lsa.disabled` | the less secure apps policy | no org unit allows less secure apps (Google removed the setting in 2025, so an empty policy passes with a note) |
| `gws.audit.available` | one `login` and one `admin` activity query over 90 days | both logs answer through the Reports API |

The three `att.*` attestation checks (EDR, backups, incident response plan) are included in every result for both platforms as `attestation_needed` with the evidence the client should attach.

## Honest gaps

Some settings insurers care about are not exposed by the APIs at all. The scanner says so instead of guessing.

**Microsoft 365** (Exchange Online PowerShell, SharePoint PowerShell or the Purview portal only):

- **Tenant-wide automatic external forwarding** (anti-spam outbound policy). The scanner reads every inbox rule, and if none forwards externally it returns `attestation_needed` asking for a screenshot of the outbound policy. Fixtures set `outbound_forwarding_blocked` directly so the pass and fail paths are tested.
- **Unified audit log state and retention.** The scanner confirms Entra audit logs are reachable and returns `attestation_needed` asking for a Purview screenshot. Anyone-link expiry (`RequireAnonymousLinksExpireInDays`) has the same limit, so a tenant that allows anyone links fails unless expiry is known.

**Google Workspace:**

- **"Unconfigured third-party apps" restriction** (Admin console, Security, API controls). No API returns it. The scanner lists every app granted sensitive scopes in the last 180 days and, when none is unapproved, returns `attestation_needed` asking for a screenshot of the API controls page. Fixtures set `third_party_access_restricted` directly.
- **Apps authorized more than 180 days ago.** The Reports API keeps six months of events, so an older grant that is still active does not appear. The finding says so in a note.
- **Org unit names in policies.** The Policy API names org units by id; the scanner names unenforced org units from the users' own `isEnforcedIn2Sv` flag and org unit path instead of asking for another scope.

A later prompt can add an optional Exchange Online PowerShell step for operators who have it; the snapshot already has the fields.

## How it is put together

```
alimi_scanner/
  schema.py         Finding, ScanResult, Status, Severity: the contract every other tool reads
  snapshot.py       BaseSnapshot plus M365Snapshot and GWSSnapshot: the normalized tenant data checks run against
  catalog.py        loads config/checks.yaml (explicit path, $ALIMI_CHECKS, or walk up to the repo root)
  engine.py         @check registry, run_checks(), score and insurer-question rollup
  checks/m365.py    one function per m365.* id; reads the snapshot, returns a CheckOutcome
  checks/gws.py     one function per gws.* id
  checks/_email_auth.py   the SPF, DKIM and DMARC evaluation both platforms share
  connectors/
    mock.py         default; loads fixtures/<platform>/<name>.json
    m365.py         GraphConnector: msal client-credentials token, httpx GETs, pagination, 429 retry
    gws.py          GoogleWorkspaceConnector over a small GoogleApi protocol; DiscoveryGoogleApi wraps google-api-python-client
    dns_lookup.py   public SPF, DKIM, DMARC lookups with dnspython (Microsoft and Google DKIM selectors)
  cli.py            typer commands: m365, gws, checks, fixtures, permissions, version
fixtures/m365/      pass.json (everything passes), fail.json (everything fails)
fixtures/gws/       same pair for Google Workspace
tests/              98 tests: catalog, every check both ways and in isolation, engine, CLI, both connectors against fakes
```

The design choice that matters: **checks never call an API.** A connector fetches everything once into a snapshot, then checks read the snapshot. That is why every check is testable from JSON, why a run can be replayed with `--snapshot`, and why the platform (prompt 12) can store snapshots and run the same checks on a schedule without the CLI.

Snapshots and findings never contain the tenant ID, the Google customer ID, the client secret or the service account key. They do contain user addresses, because the report needs to say which accounts to fix. Keep `out/` local; it is git-ignored.

## Adding a check

1. Add the entry to `config/checks.yaml` (id, severity, insurer question, plain-English explain and remediation).
2. If the connector does not already read what you need, add a field to `snapshot.py` and fill it in `connectors/m365.py` or `connectors/gws.py`.
3. Write the function in `checks/m365.py` or `checks/gws.py` with `@check("<platform>.your.id")`. Return `error` with the permission or scope name when the field is `None`.
4. Update the platform's `fixtures/<platform>/pass.json` and `fail.json`, add a `break_*` case in the matching `tests/test_checks_*.py`, run `pytest`.
