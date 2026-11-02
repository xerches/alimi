-- What the web app's database role may do. The role (alimi_app) is created outside the
-- migrations, by db/init-roles.sql, because creating roles needs more power than the
-- migration owner has. It owns nothing, is not a superuser and does not have BYPASSRLS,
-- so every row it touches goes through the policies in 0001.

GRANT USAGE ON SCHEMA public TO alimi_app;
GRANT EXECUTE ON FUNCTION app_org(), app_user() TO alimi_app;

-- Reference catalog: read only.
GRANT SELECT ON frameworks, requirements, controls, control_requirements, tests, control_tests TO alimi_app;

-- Customer tables: no DELETE anywhere yet. Removing data is a deliberate act that 12b will
-- add with its own audit entry.
GRANT SELECT ON organizations TO alimi_app;
GRANT SELECT, INSERT, UPDATE ON users, memberships, integrations, scan_runs, evidence TO alimi_app;
GRANT SELECT, INSERT ON test_results TO alimi_app;

-- The audit log is append only for the app: it can add entries and read them, never edit them.
GRANT SELECT, INSERT ON audit_log TO alimi_app;
GRANT USAGE ON SEQUENCE audit_log_id_seq TO alimi_app;
