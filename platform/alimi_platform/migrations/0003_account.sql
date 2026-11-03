-- The person's own settings (Nov 3, 2026): a job title on the user row, and a per-user settings
-- row for the time zone, the language and which notifications they want.
--
-- user_settings is keyed by the user, not the organization: a person's preferences follow them.
-- Its policy is therefore "your own row only" (app_user()), the same way the users table lets a
-- person see themselves. No context, no rows, as everywhere else.

ALTER TABLE users ADD COLUMN job_title text;

CREATE TABLE user_settings (
    user_id                        uuid PRIMARY KEY REFERENCES users (id),
    time_zone                      text NOT NULL DEFAULT 'America/New_York',
    locale                         text NOT NULL DEFAULT 'en-US',
    notify_failed_tests            boolean NOT NULL DEFAULT true,   -- a check that passed starts failing
    notify_renewals                boolean NOT NULL DEFAULT true,   -- evidence or a policy review is due in 30 days
    notify_policy_acknowledgements boolean NOT NULL DEFAULT true,   -- a policy waits for your acknowledgement
    notify_access_requests         boolean NOT NULL DEFAULT true,   -- someone asks for access to the trust center
    notify_weekly_digest           boolean NOT NULL DEFAULT true,   -- Monday summary of the company's position
    updated_at                     timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings FORCE ROW LEVEL SECURITY;
CREATE POLICY own_settings ON user_settings
    USING (user_id = app_user()) WITH CHECK (user_id = app_user());

GRANT SELECT, INSERT, UPDATE ON user_settings TO alimi_app;
