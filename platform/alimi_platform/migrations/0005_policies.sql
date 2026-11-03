-- Policies (Nov 3, 2026): the policy module. Alimi's library, the 23 Markdown policies in
-- /policies, is catalog, loaded by catalog.py the way the controls are. What a company adopts is
-- customer data: its own copy of each policy with the placeholders filled, every version of the
-- text, who approved which version and who acknowledged it. The text is read only by signed-in
-- members (the founder's rule of Nov 2, 2026: no policy text in public).

CREATE TABLE policy_templates (
    id            text PRIMARY KEY,         -- POL-01 ...
    slug          text NOT NULL UNIQUE,
    title         text NOT NULL,
    version       text NOT NULL,            -- the library's own version of the template, e.g. 1.0
    owner_role    text,                     -- the placeholder as written, e.g. {{Security Lead}}
    approver_role text,
    review_cycle  text NOT NULL DEFAULT 'annual',
    applies_to    text,
    related       text[] NOT NULL DEFAULT '{}',
    position      integer NOT NULL,
    body          text NOT NULL             -- Markdown with the placeholders; front matter and the TEMPLATE header removed
);

CREATE TABLE policy_requirements (
    policy_id      text NOT NULL REFERENCES policy_templates (id),
    requirement_id text NOT NULL REFERENCES requirements (id),
    PRIMARY KEY (policy_id, requirement_id)
);

CREATE TABLE control_policies (
    control_id text NOT NULL REFERENCES controls (id),
    policy_id  text NOT NULL REFERENCES policy_templates (id),
    PRIMARY KEY (control_id, policy_id)
);

GRANT SELECT ON policy_templates, policy_requirements, control_policies TO alimi_app;

-- The company's copy. One row per adopted policy; the text lives in policy_versions, and
-- current_version says which one is in force (or being drafted).
CREATE TABLE policies (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id  uuid NOT NULL REFERENCES organizations (id),
    template_id      text REFERENCES policy_templates (id),  -- NULL for a policy the company writes itself (later)
    slug             text NOT NULL,
    title            text NOT NULL,
    status           text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'in_review', 'approved', 'retired')),
    owner_user_id    uuid REFERENCES users (id),
    approver_user_id uuid REFERENCES users (id),
    review_cycle     text NOT NULL DEFAULT 'annual',
    applies_to       text,
    current_version  integer NOT NULL DEFAULT 1,
    approved_at      timestamptz,            -- of the current version; NULL while it is a draft
    next_review_on   date,
    created_at       timestamptz NOT NULL DEFAULT now(),
    updated_at       timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, slug),
    UNIQUE (organization_id, id)
);

CREATE TABLE policy_versions (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    policy_id       uuid NOT NULL,
    number          integer NOT NULL,         -- 1, 2, 3: the company's own count, not the library's
    body            text NOT NULL,            -- the Markdown as adopted, placeholders filled; never edited, only superseded
    change_note     text,
    author_user_id  uuid REFERENCES users (id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    approved_by     uuid REFERENCES users (id),
    approved_at     timestamptz,
    FOREIGN KEY (organization_id, policy_id) REFERENCES policies (organization_id, id),
    UNIQUE (organization_id, policy_id, number)
);

-- An acknowledgement is of one version: a new approved version asks everyone again.
CREATE TABLE policy_acknowledgements (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    policy_id       uuid NOT NULL,
    version_number  integer NOT NULL,
    user_id         uuid NOT NULL REFERENCES users (id),
    acknowledged_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (organization_id, policy_id) REFERENCES policies (organization_id, id),
    UNIQUE (organization_id, policy_id, version_number, user_id)
);

DO $$
DECLARE
    t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['policies', 'policy_versions', 'policy_acknowledgements']
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

-- A version's text and an acknowledgement are written once and kept: that is the audit trail an
-- auditor or an insurer asks for. The app may stamp the approval on a version (two columns) but
-- never change its body. The policy row itself changes status and version.
GRANT SELECT, INSERT, UPDATE ON policies TO alimi_app;
GRANT SELECT, INSERT ON policy_versions, policy_acknowledgements TO alimi_app;
GRANT UPDATE (approved_by, approved_at) ON policy_versions TO alimi_app;
