-- Trust center (Nov 3, 2026): a public page per company that answers the first round of a
-- customer's, a bank's or a broker's questions, and the admin side that decides what is public,
-- what is on request behind an NDA and an approval, and what stays private.
--
-- Everything here is customer data behind forced row-level security, with one deliberate
-- exception: trust_directory, the slug that names a company's public page. A visitor has no
-- organization, so the lookup from slug to organization must work with no context; the table
-- holds nothing but that slug and whether the page is on, and its policies let a company insert
-- and update only its own row. The public route then opens the organization's own context and
-- reads only what is marked public (or on request, with a valid access key).

CREATE TABLE trust_directory (
    slug            text PRIMARY KEY,
    organization_id uuid NOT NULL UNIQUE REFERENCES organizations (id),
    enabled         boolean NOT NULL DEFAULT false
);
ALTER TABLE trust_directory ENABLE ROW LEVEL SECURITY;
ALTER TABLE trust_directory FORCE ROW LEVEL SECURITY;
CREATE POLICY public_lookup ON trust_directory FOR SELECT USING (true);
CREATE POLICY own_row_insert ON trust_directory FOR INSERT WITH CHECK (organization_id = app_org());
CREATE POLICY own_row_update ON trust_directory FOR UPDATE USING (organization_id = app_org()) WITH CHECK (organization_id = app_org());
GRANT SELECT, INSERT, UPDATE ON trust_directory TO alimi_app;

CREATE TABLE trust_pages (
    organization_id      uuid PRIMARY KEY REFERENCES organizations (id),
    headline             text,
    statement            text,                              -- Markdown, rendered with raw HTML off
    contact_name         text,
    contact_email        text,
    show_controls        boolean NOT NULL DEFAULT true,     -- "N controls monitored, last check <date>" on the page
    nda_text             text,                              -- Markdown; blank means no click-through before a request
    access_days          integer NOT NULL DEFAULT 365,      -- how long an approved access key works
    auto_approve_domains text[] NOT NULL DEFAULT '{}',      -- a request from these email domains is approved at once
    blocked_domains      text[] NOT NULL DEFAULT '{}',      -- a request from these is refused
    updated_at           timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE trust_folders (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    name            text NOT NULL,
    position        integer NOT NULL DEFAULT 0,
    UNIQUE (organization_id, id)
);

CREATE TABLE trust_documents (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    folder_id       uuid,
    title           text NOT NULL,
    description     text,
    visibility      text NOT NULL DEFAULT 'private' CHECK (visibility IN ('public', 'on_request', 'private')),
    kind            text NOT NULL DEFAULT 'link' CHECK (kind IN ('link', 'policy')),
    url             text,                                   -- kind link: where the file lives (uploads arrive with evidence, 12b)
    policy_id       uuid,                                   -- kind policy: one of the company's approved policies
    position        integer NOT NULL DEFAULT 0,
    updated_at      timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (organization_id, folder_id) REFERENCES trust_folders (organization_id, id),
    FOREIGN KEY (organization_id, policy_id) REFERENCES policies (organization_id, id),
    -- Policy text is never public (founder, Nov 2, 2026): at most on request, behind the NDA and an approval.
    CHECK (kind <> 'policy' OR visibility <> 'public')
);

CREATE TABLE trust_questions (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    category        text,
    question        text NOT NULL,
    answer          text NOT NULL,                          -- Markdown
    published       boolean NOT NULL DEFAULT true,
    position        integer NOT NULL DEFAULT 0,
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE trust_subprocessors (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    name            text NOT NULL,
    purpose         text NOT NULL,
    location        text,
    url             text,
    position        integer NOT NULL DEFAULT 0,
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE trust_updates (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    title           text NOT NULL,
    body            text,                                   -- Markdown
    published_on    date NOT NULL DEFAULT current_date,
    created_by      uuid REFERENCES users (id),
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE trust_subscribers (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    email           text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, email)
);

CREATE TABLE trust_access_requests (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    name            text NOT NULL,
    email           text NOT NULL,
    company         text,
    reason          text,
    nda_accepted    boolean NOT NULL DEFAULT false,
    status          text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'denied')),
    token_hash      text,                                   -- sha256 of the access key; the key is shown once and never stored
    expires_on      date,
    decided_by      uuid REFERENCES users (id),
    decided_at      timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX trust_access_requests_by_token ON trust_access_requests (organization_id, token_hash);

CREATE TABLE trust_views (
    organization_id uuid NOT NULL REFERENCES organizations (id),
    day             date NOT NULL,
    views           integer NOT NULL DEFAULT 0,
    PRIMARY KEY (organization_id, day)
);

DO $$
DECLARE
    t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['trust_pages', 'trust_folders', 'trust_documents', 'trust_questions', 'trust_subprocessors',
                             'trust_updates', 'trust_subscribers', 'trust_access_requests', 'trust_views']
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

-- No DELETE for the app role, as everywhere: a document is made private, a question unpublished,
-- a request denied. Updates, subscribers and requests are records that stay.
GRANT SELECT, INSERT, UPDATE ON trust_pages, trust_folders, trust_documents, trust_questions, trust_subprocessors, trust_access_requests, trust_views TO alimi_app;
GRANT SELECT, INSERT ON trust_updates, trust_subscribers TO alimi_app;
