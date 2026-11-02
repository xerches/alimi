-- Alimi platform foundation (prompt 12a).
--
-- Two kinds of table live here:
--
--   Reference tables (frameworks, requirements, controls, tests and the links between them)
--   are Alimi's own catalog, loaded from /config and /policies. They hold no customer data,
--   every organization reads the same rows, and the app role can only SELECT them.
--
--   Customer tables carry organization_id and row-level security (RLS). The policies compare
--   that column with app_org(), the organization the current transaction says it acts for.
--   FORCE ROW LEVEL SECURITY makes the rules apply to the table owner as well, so the only
--   way around them is a superuser or a BYPASSRLS role, and the app is neither.
--
-- The app sets the organization once per request with
--   SELECT set_config('app.org_id', '<uuid>', true)
-- The "true" makes it local to the transaction: when the transaction ends the setting is gone,
-- so a pooled connection never carries one company's context into the next request.
-- No setting means app_org() is NULL, NULL never equals anything, and every query returns
-- nothing. Forgetting the context fails closed.


CREATE FUNCTION app_org() RETURNS uuid
LANGUAGE sql STABLE AS $$
    SELECT nullif(current_setting('app.org_id', true), '')::uuid
$$;

CREATE FUNCTION app_user() RETURNS uuid
LANGUAGE sql STABLE AS $$
    SELECT nullif(current_setting('app.user_id', true), '')::uuid
$$;

-- ---------------------------------------------------------------- reference catalog

CREATE TABLE frameworks (
    id              text PRIMARY KEY,           -- config/frameworks.yaml id, e.g. insurer, soc2
    name            text NOT NULL,
    short_name      text NOT NULL,
    summary         text NOT NULL,              -- our own words
    mapped          boolean NOT NULL DEFAULT false,
    always_included boolean NOT NULL DEFAULT false,
    position        integer NOT NULL
);

CREATE TABLE requirements (
    id           text PRIMARY KEY,              -- "<framework>:<criterion id>", e.g. insurer:mfa, soc2:CC6.1
    framework_id text NOT NULL REFERENCES frameworks (id),
    code         text NOT NULL,                 -- the criterion ID only; never the framework's text
    summary      text,                          -- our own plain-English summary, when we have written one
    position     integer NOT NULL DEFAULT 0,
    UNIQUE (framework_id, code)
);

CREATE TABLE controls (
    id             text PRIMARY KEY,            -- CTL-01 ...
    name           text NOT NULL,
    domain         text NOT NULL,
    description    text NOT NULL,
    implementation text,
    owner_role     text,
    frequency      text NOT NULL,
    evidence_types text[] NOT NULL DEFAULT '{}'
);

CREATE TABLE control_requirements (
    control_id     text NOT NULL REFERENCES controls (id),
    requirement_id text NOT NULL REFERENCES requirements (id),
    PRIMARY KEY (control_id, requirement_id)
);

CREATE TABLE tests (
    id               text PRIMARY KEY,          -- config/checks.yaml id, e.g. m365.mfa.coverage
    platform         text NOT NULL,             -- m365 | gws | any
    kind             text NOT NULL,             -- automated | attestation
    title            text NOT NULL,
    severity         text NOT NULL,
    insurer_question text NOT NULL,
    rule             text NOT NULL,             -- pass_when in plain English
    explain          text NOT NULL,
    remediation      text NOT NULL,
    version          text NOT NULL              -- digest of the definition; changes when the check changes
);

CREATE TABLE control_tests (
    control_id text NOT NULL REFERENCES controls (id),
    test_id    text NOT NULL REFERENCES tests (id),
    PRIMARY KEY (control_id, test_id)
);

-- ---------------------------------------------------------------- customer tables

CREATE TABLE organizations (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name       text NOT NULL,
    slug       text NOT NULL UNIQUE,
    parent_id  uuid REFERENCES organizations (id),  -- a reseller's client points at the reseller (12b)
    is_sample  boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);
-- organizations is keyed by its own id rather than organization_id; the policy below says so.

CREATE TABLE users (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email        text NOT NULL UNIQUE,
    display_name text NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE memberships (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    user_id         uuid NOT NULL REFERENCES users (id),
    role            text NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'auditor')),
    created_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, user_id)
);

CREATE TABLE integrations (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   uuid NOT NULL REFERENCES organizations (id),
    platform          text NOT NULL CHECK (platform IN ('m365', 'gws')),
    display_name      text NOT NULL,
    mode              text NOT NULL DEFAULT 'mock' CHECK (mode IN ('mock', 'live')),
    fixture           text,                      -- mock mode: which scanner fixture stands in for the tenant
    scopes            text[] NOT NULL DEFAULT '{}',  -- read-only scopes granted, for the record
    token_ciphertext  bytea,                     -- Fernet-encrypted; the key lives outside the database
    last_sync_at      timestamptz,
    last_sync_status  text,
    created_at        timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, id)
);

CREATE TABLE scan_runs (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    integration_id  uuid NOT NULL,
    started_by      uuid REFERENCES users (id),
    started_at      timestamptz NOT NULL DEFAULT now(),
    finished_at     timestamptz,
    scanner_version text NOT NULL,
    source          text NOT NULL,               -- mock:fail, graph, ...
    score_percent   numeric(5, 1),
    -- the integration must belong to the same organization as the run
    FOREIGN KEY (organization_id, integration_id) REFERENCES integrations (organization_id, id),
    UNIQUE (organization_id, id)
);

CREATE TABLE test_results (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    scan_run_id     uuid NOT NULL,
    test_id         text NOT NULL REFERENCES tests (id),
    control_ids     text[] NOT NULL DEFAULT '{}',
    status          text NOT NULL CHECK (status IN ('pass', 'fail', 'attestation_needed', 'error', 'not_applicable')),
    summary         text NOT NULL,
    raw_evidence    jsonb NOT NULL DEFAULT '{}',  -- exactly what the check read
    rule            text NOT NULL,                -- the rule in plain English, as it stood at scan time
    criterion_ids   text[] NOT NULL DEFAULT '{}', -- requirement ids this result gives evidence for
    check_version   text NOT NULL,                -- scanner version + definition digest
    collected_at    timestamptz NOT NULL,
    FOREIGN KEY (organization_id, scan_run_id) REFERENCES scan_runs (organization_id, id)
);
CREATE INDEX test_results_latest ON test_results (organization_id, test_id, collected_at DESC);

CREATE TABLE evidence (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    control_id      text NOT NULL REFERENCES controls (id),
    kind            text NOT NULL CHECK (kind IN ('file', 'attestation')),
    evidence_type   text NOT NULL,                -- policy | report | export | record | register | contract
    title           text NOT NULL,
    note            text,
    file_name       text,                          -- uploads arrive in 12b
    attested_by     uuid REFERENCES users (id),
    collected_on    date NOT NULL,
    renews_on       date,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
    id              bigserial PRIMARY KEY,
    organization_id uuid NOT NULL REFERENCES organizations (id),
    actor_user_id   uuid REFERENCES users (id),
    action          text NOT NULL,
    target          text,
    detail          jsonb NOT NULL DEFAULT '{}',
    at              timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------- row-level security

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations FORCE ROW LEVEL SECURITY;
CREATE POLICY org_isolation ON organizations
    USING (id = app_org()) WITH CHECK (id = app_org());

-- A user row is visible when it is the signed-in user or a member of the current organization.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;
CREATE POLICY user_visibility ON users
    USING (
        id = app_user()
        OR EXISTS (SELECT 1 FROM memberships m WHERE m.user_id = users.id AND m.organization_id = app_org())
    )
    WITH CHECK (id = app_user() OR app_org() IS NOT NULL);

DO $$
DECLARE
    t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['memberships', 'integrations', 'scan_runs', 'test_results', 'evidence', 'audit_log']
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
        EXECUTE format(
            'CREATE POLICY org_isolation ON %I USING (organization_id = app_org()) WITH CHECK (organization_id = app_org())',
            t
        );
    END LOOP;
END
$$;
