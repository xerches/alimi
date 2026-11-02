-- Run once by a superuser when the database is created (docker compose mounts this into
-- /docker-entrypoint-initdb.d). Creates the two roles the platform uses:
--
--   alimi_owner  owns the tables and runs migrations and the sample-data seed. Not a superuser
--                and no BYPASSRLS, so FORCE ROW LEVEL SECURITY applies to it too.
--   alimi_app    what the web app logs in as. Owns nothing and cannot bypass row-level security.
--
-- The passwords here are for the local mock-mode database only. Anything that ever holds real
-- data sets its own through the environment.

CREATE ROLE alimi_owner LOGIN PASSWORD 'alimi_owner_local' NOSUPERUSER NOCREATEROLE NOBYPASSRLS;
CREATE ROLE alimi_app   LOGIN PASSWORD 'alimi_app_local'   NOSUPERUSER NOCREATEROLE NOCREATEDB NOBYPASSRLS;

CREATE DATABASE alimi OWNER alimi_owner;
\connect alimi
ALTER SCHEMA public OWNER TO alimi_owner;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT CONNECT ON DATABASE alimi TO alimi_app;
