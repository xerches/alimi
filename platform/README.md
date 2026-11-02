# platform

The Alimi compliance platform web app. This is the prompt 12a foundation: the data model, the
tenant isolation, and mock scans with evidence on every test. **Mock mode only**: sample
companies on the scanner's sample tenants. It refuses to start with `ALIMI_MODE` set to anything
but `mock`, and it holds no customer data until the gate in `../CLAUDE.md` is met.

## Run it

```
cd platform
docker compose up
```

Open http://localhost:8000, pick a sample user, and press **Run checks now**. Three organizations
are seeded: Saltmarsh Payroll (Microsoft 365, the scanner's failing sample tenant), Harbor Dental
(Google Workspace, failing) and Alimi (our own organization for dogfooding, Microsoft 365,
passing). `docker compose down -v` wipes the database and the generated keys.

## What is in it

| Piece | Where | Notes |
| --- | --- | --- |
| Tables and row-level security | `alimi_platform/migrations/0001_foundation.sql` | Organization, User, Membership, Integration, ScanRun, TestResult, Evidence, AuditLog are customer tables; Framework, Requirement, Control, Test and the links are Alimi's own catalog |
| App role permissions | `alimi_platform/migrations/0002_app_role_grants.sql` | the app can read the catalog, cannot delete anything, and can only append to the audit log |
| Database roles | `db/init-roles.sql` | `alimi_owner` owns the tables and runs migrations; `alimi_app` is what the web server uses |
| Catalog load | `alimi_platform/catalog.py` | reads `config/frameworks.yaml`, `policies/requirements.yaml`, `config/controls.yaml`, `config/checks.yaml` |
| Scans | `alimi_platform/scans.py` | imports `alimi_scanner`, stores each finding as a TestResult |
| Status rules | `alimi_platform/status.py` | control and requirement status are computed, never typed in |
| Token encryption | `alimi_platform/crypto.py` | Fernet with a key from the environment; a log filter redacts anything token-shaped |
| Pages | `alimi_platform/main.py`, `templates/` | FastAPI, Jinja templates, HTMX (vendored, `static/htmx.min.js`, 2.0.4, BSD Zero Clause licence) |
| Sample data | `alimi_platform/seed.py` | fixed IDs, so the mock picker can list users without the database |

## How the isolation works

Every customer table has an `organization_id` column, row-level security switched on and
**forced**, and one policy: a row is visible, and can be written, only when its
`organization_id` equals `app_org()`, the organization the current transaction acts for. The
app sets that once per request with `set_config('app.org_id', ..., true)`; the `true` scopes it
to the transaction, so a pooled connection never carries one company into the next request. With
no setting, every query returns nothing.

The app logs in as `alimi_app`, which owns no tables, is not a superuser and has no `BYPASSRLS`,
so it cannot switch the rules off. Forcing RLS means even `alimi_owner` goes through the policies;
the seed writes each sample company inside that company's context, the same way the app does.

`tests/test_isolation.py` proves it against a real Postgres: each company sees only its own rows
in every table, a lookup by another company's ID finds nothing, writes into or moves rows to
another company are refused by the database, the audit log cannot be edited, and a test fails if
a future migration adds a table with `organization_id` but no forced policy.

## Tokens

Integration tokens are stored encrypted (`token_ciphertext`) with Fernet, authenticated
encryption from the `cryptography` package, and the key comes from `ALIMI_TOKEN_KEY` (or the file
`ALIMI_TOKEN_KEY_FILE` names). docker compose generates the key on first start into its own
volume, outside the database. Mock integrations store an encrypted placeholder so the same
decrypt step runs on every scan. A decrypted token is wrapped in `Secret`, which prints as
`********`, and a logging filter redacts anything shaped like a token.

## Login

`/login` is a picker of the sample users in `seed.py`, and it only exists in mock mode. The
session cookie is signed and `SameSite=Lax`; every request re-checks the membership in the
database, so a forged or stale cookie lands back on the picker. Real login over OIDC is 12b.

## Tests

The tests need a Postgres 14 or newer and a superuser URL, which they use only to create the two
roles and a throwaway `alimi_test` database:

```
pip install -e ../tools/scanner -e ".[dev]"
ALIMI_TEST_ADMIN_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres pytest
```

CI runs the same against a Postgres service container (`.github/workflows/tests.yml`, job `platform`).

## Not in 12a

Real login, the nightly worker, the reseller view and its policy, evidence uploads, recurring
tasks and false-positive notes are prompt 12b. Readiness scores, the Alimi Security Posture Score,
the in-app report, the export pack and the data-quality page are 12c. Policies and people are 13.
Control owners are not modelled yet, so no control shows "Needs owner".
