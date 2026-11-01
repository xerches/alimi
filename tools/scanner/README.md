# alimi scanner

Read-only security checks for Microsoft 365 (Google Workspace comes in prompt 4). It reads a tenant through Microsoft Graph, runs the checks listed in `config/checks.yaml`, and writes a findings file that the report generator and, later, the platform consume.

**Mock mode is the default.** Nothing here touches a real tenant unless you pass `--tenant --authorized`, and that flag is your statement that you own the tenant or hold a signed pilot authorization letter.

## Run it

```bash
cd tools/scanner
pip install -e ".[dev]"         # once
alimi-scan m365                  # mock scan of the "pass" fixture, table on screen, JSON in ./out/
alimi-scan m365 --fixture fail   # a tenant that trips every check
alimi-scan checks                # every check in checks.yaml and whether it is implemented
alimi-scan permissions           # the Graph permissions a real scan needs
pytest                           # 45 tests, no network
```

Output goes to `./out/` (or `$ALIMI_OUTPUT_DIR`), which is git-ignored. Each run writes `m365-<timestamp>.findings.json`; add `--save-snapshot` to also keep the raw snapshot the checks ran on, which is handy for re-running checks later with `--snapshot <file>`.

## Scan a real tenant

Only tenants you own or that are covered by a signed pilot authorization letter from `/templates`.

1. **Create the app registration.** Entra admin center, App registrations, New registration. Name it `alimi scanner (read-only)`, single tenant, no redirect URI.
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

## What the checks read

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

The three `att.*` attestation checks (EDR, backups, incident response plan) are included in every result as `attestation_needed` with the evidence the client should attach.

## Honest gaps

Two settings insurers care about are not exposed by Microsoft Graph at all, only by Exchange Online PowerShell, SharePoint PowerShell or the Purview portal:

- **Tenant-wide automatic external forwarding** (anti-spam outbound policy). The scanner reads every inbox rule, and if none forwards externally it returns `attestation_needed` asking for a screenshot of the outbound policy. Fixtures set `outbound_forwarding_blocked` directly so the pass and fail paths are tested.
- **Unified audit log state and retention.** The scanner confirms Entra audit logs are reachable and returns `attestation_needed` asking for a Purview screenshot. Anyone-link expiry (`RequireAnonymousLinksExpireInDays`) has the same limit, so a tenant that allows anyone links fails unless expiry is known.

A later prompt can add an optional Exchange Online PowerShell step for operators who have it; the snapshot already has the fields.

## How it is put together

```
alimi_scanner/
  schema.py        Finding, ScanResult, Status, Severity: the contract every other tool reads
  snapshot.py      M365Snapshot: the normalized tenant data checks run against
  catalog.py       loads config/checks.yaml (explicit path, $ALIMI_CHECKS, or walk up to the repo root)
  engine.py        @check registry, run_checks(), score and insurer-question rollup
  checks/m365.py   one function per m365.* id; reads the snapshot, returns a CheckOutcome
  connectors/
    mock.py        default; loads fixtures/m365/<name>.json
    m365.py        GraphConnector: msal client-credentials token, httpx GETs, pagination, 429 retry
    dns_lookup.py  public SPF, DKIM, DMARC lookups with dnspython
  cli.py           typer commands: m365, checks, fixtures, permissions, version
fixtures/m365/     pass.json (everything passes), fail.json (everything fails)
tests/             45 tests: catalog, every check both ways and in isolation, engine, CLI, Graph connector against a fake Graph
```

The design choice that matters: **checks never call an API.** A connector fetches everything once into a snapshot, then checks read the snapshot. That is why every check is testable from JSON, why a run can be replayed with `--snapshot`, and why the platform (prompt 12) can store snapshots and run the same checks on a schedule without the CLI.

Snapshots and findings never contain the tenant ID or the client secret. They do contain user principal names, because the report needs to say which accounts to fix. Keep `out/` local; it is git-ignored.

## Adding a check

1. Add the entry to `config/checks.yaml` (id, severity, insurer question, plain-English explain and remediation).
2. If the connector does not already read what you need, add a field to `snapshot.py` and fill it in `connectors/m365.py`.
3. Write the function in `checks/m365.py` with `@check("m365.your.id")`. Return `error` with the permission name when the field is `None`.
4. Update `fixtures/m365/pass.json` and `fail.json`, add a `break_*` case in `tests/test_checks_m365.py`, run `pytest`.
