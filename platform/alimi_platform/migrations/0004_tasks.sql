-- Tasks and projects (Nov 3, 2026): the ticketing system the founder asked for, so a company
-- tracks what it has to do in Alimi itself, or mirrors it to the tool it already runs (Jira,
-- Monday.com) through the external ticket fields until a live sync exists.
--
-- A task can point at the thing it is about (a control, a test, evidence, a policy, a trust
-- center access request) through source_kind + source_id, which is how the month's list on Home
-- is built from the same rows. Customer tables, so organization_id and forced RLS as everywhere.

CREATE TABLE projects (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    name            text NOT NULL,
    description     text,
    status          text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'done', 'archived')),
    owner_user_id   uuid REFERENCES users (id),
    due_on          date,
    external_system text CHECK (external_system IN ('jira', 'monday')),  -- the board or project this one mirrors
    external_key    text,                                                -- e.g. SEC-12, or the Monday board id
    external_url    text,
    created_by      uuid REFERENCES users (id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, id)
);

CREATE TABLE tasks (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id  uuid NOT NULL REFERENCES organizations (id),
    number           integer NOT NULL,                      -- T-12 on screen; counted per company
    project_id       uuid,
    title            text NOT NULL,
    detail           text,
    kind             text NOT NULL DEFAULT 'custom' CHECK (kind IN ('fix', 'renew', 'decide', 'custom')),
    source_kind      text CHECK (source_kind IN ('control', 'test', 'evidence', 'policy', 'trust_request')),
    source_id        text,
    status           text NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'blocked', 'done')),
    priority         text NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    assignee_user_id uuid REFERENCES users (id),
    due_on           date,
    external_system  text CHECK (external_system IN ('jira', 'monday')),
    external_key     text,
    external_url     text,
    created_by       uuid REFERENCES users (id),
    created_at       timestamptz NOT NULL DEFAULT now(),
    updated_at       timestamptz NOT NULL DEFAULT now(),
    done_at          timestamptz,
    FOREIGN KEY (organization_id, project_id) REFERENCES projects (organization_id, id),
    UNIQUE (organization_id, number),
    UNIQUE (organization_id, id)
);
CREATE INDEX tasks_by_status ON tasks (organization_id, status, due_on);

CREATE TABLE task_comments (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations (id),
    task_id         uuid NOT NULL,
    author_user_id  uuid REFERENCES users (id),
    body            text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (organization_id, task_id) REFERENCES tasks (organization_id, id)
);

DO $$
DECLARE
    t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['projects', 'tasks', 'task_comments']
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

-- No DELETE for the app role, as everywhere: a task is closed, never erased. Comments are append only.
GRANT SELECT, INSERT, UPDATE ON projects, tasks TO alimi_app;
GRANT SELECT, INSERT ON task_comments TO alimi_app;
