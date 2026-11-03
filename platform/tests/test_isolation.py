"""The point of 12a: the database itself keeps one company's data away from another's.

Every test here talks to Postgres as alimi_app, the role the web app uses, with no Python
filtering in between. If one of these fails, an app bug could leak data across customers.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, ProgrammingError

from alimi_platform.db import org_scope

CUSTOMER_TABLES = ["memberships", "integrations", "scan_runs", "test_results", "evidence", "audit_log", "projects", "tasks", "task_comments", "policies", "policy_versions", "policy_acknowledgements",
                   "trust_pages", "trust_folders", "trust_documents", "trust_questions", "trust_subprocessors", "trust_updates", "trust_subscribers", "trust_access_requests", "trust_views"]


def test_app_role_cannot_bypass_row_level_security(app_engine):
    with app_engine.connect() as conn:
        row = conn.execute(
            text("SELECT rolsuper, rolbypassrls, rolcreaterole FROM pg_roles WHERE rolname = current_user")
        ).one()
    assert tuple(row) == (False, False, False)


def test_app_role_owns_no_tables(app_engine):
    with app_engine.connect() as conn:
        owned = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tableowner = current_user")
        ).all()
    assert owned == []


def test_every_table_with_organization_data_has_forced_rls(owner_engine):
    """Guards future migrations: a new customer table without RLS fails here."""
    with owner_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity, "
                "  EXISTS (SELECT 1 FROM pg_policy p WHERE p.polrelid = c.oid) AS has_policy "
                "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public' AND c.relkind = 'r' AND ("
                "  EXISTS (SELECT 1 FROM information_schema.columns col "
                "          WHERE col.table_schema = 'public' AND col.table_name = c.relname AND col.column_name = 'organization_id')"
                "  OR c.relname IN ('organizations', 'users'))"
            )
        ).all()
    names = {r.relname for r in rows}
    assert set(CUSTOMER_TABLES) | {"organizations", "users"} <= names
    for r in rows:
        assert r.relrowsecurity and r.relforcerowsecurity and r.has_policy, f"{r.relname} is missing row-level security"


@pytest.mark.parametrize("table", CUSTOMER_TABLES + ["organizations"])
def test_each_org_sees_only_its_own_rows(app_engine, orgs, table):
    column = "id" if table == "organizations" else "organization_id"
    seen = {}
    for slug, org in orgs.items():
        with org_scope(app_engine, org.id) as conn:
            ids = {r[0] for r in conn.execute(text(f"SELECT DISTINCT {column} FROM {table}"))}
        assert ids == {org.id}, f"{slug} saw {ids} in {table}"
        seen[slug] = ids
    assert len(seen) == 3


@pytest.mark.parametrize("table", CUSTOMER_TABLES + ["organizations", "users", "user_settings"])
def test_no_context_means_no_rows(app_engine, table):
    with app_engine.begin() as conn:
        assert conn.execute(text(f"SELECT count(*) FROM {table}")).scalar() == 0


def test_lookup_by_id_of_another_orgs_row_finds_nothing(app_engine, orgs):
    saltmarsh, harbor = orgs["saltmarsh"], orgs["harbor-dental"]
    with org_scope(app_engine, saltmarsh.id) as conn:
        assert conn.execute(text("SELECT * FROM integrations WHERE id = :id"), {"id": harbor.integration_id}).first() is None
        assert conn.execute(text("SELECT * FROM organizations WHERE id = :id"), {"id": harbor.id}).first() is None
        # An app bug that forgets the WHERE clause still gets only Saltmarsh's results.
        orgs_in_results = {r[0] for r in conn.execute(text("SELECT organization_id FROM test_results"))}
        assert orgs_in_results == {saltmarsh.id}


def test_users_of_other_orgs_are_invisible(app_engine, orgs):
    saltmarsh, harbor = orgs["saltmarsh"], orgs["harbor-dental"]
    with org_scope(app_engine, saltmarsh.id) as conn:
        emails = {r[0] for r in conn.execute(text("SELECT email FROM users"))}
    assert emails == {u.email for u in saltmarsh.users}
    assert not emails & {u.email for u in harbor.users}


def test_cannot_write_rows_into_another_org(app_engine, orgs):
    saltmarsh, harbor = orgs["saltmarsh"], orgs["harbor-dental"]
    with pytest.raises(DBAPIError, match="row-level security"):
        with org_scope(app_engine, saltmarsh.id) as conn:
            conn.execute(
                text("INSERT INTO audit_log (organization_id, action) VALUES (:org, 'planted')"),
                {"org": harbor.id},
            )


def test_cannot_move_a_row_to_another_org(app_engine, orgs):
    saltmarsh, harbor = orgs["saltmarsh"], orgs["harbor-dental"]
    with pytest.raises(DBAPIError, match="row-level security"):
        with org_scope(app_engine, saltmarsh.id) as conn:
            conn.execute(
                text("UPDATE integrations SET organization_id = :other WHERE id = :id"),
                {"other": harbor.id, "id": saltmarsh.integration_id},
            )


def test_update_aimed_at_another_org_changes_nothing(app_engine, orgs):
    saltmarsh, harbor = orgs["saltmarsh"], orgs["harbor-dental"]
    with org_scope(app_engine, saltmarsh.id) as conn:
        result = conn.execute(
            text("UPDATE integrations SET display_name = 'hijacked' WHERE id = :id"), {"id": harbor.integration_id}
        )
        assert result.rowcount == 0


def test_audit_log_is_append_only_for_the_app(app_engine, orgs):
    org = orgs["saltmarsh"]
    for statement in ("UPDATE audit_log SET action = 'edited'", "DELETE FROM audit_log"):
        with pytest.raises(ProgrammingError, match="permission denied"):
            with org_scope(app_engine, org.id) as conn:
                conn.execute(text(statement))


def test_app_cannot_change_the_catalog(app_engine, orgs):
    with pytest.raises(ProgrammingError, match="permission denied"):
        with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
            conn.execute(text("UPDATE controls SET name = 'x'"))


def test_context_does_not_leak_between_transactions_on_a_pooled_connection(app_engine, orgs):
    with org_scope(app_engine, orgs["saltmarsh"].id) as conn:
        assert conn.execute(text("SELECT count(*) FROM integrations")).scalar() == 1
    # Same pool, likely the same connection: the setting must be gone.
    with app_engine.begin() as conn:
        assert conn.execute(text("SELECT app_org()")).scalar() is None
        assert conn.execute(text("SELECT count(*) FROM integrations")).scalar() == 0


def test_a_made_up_org_id_sees_nothing(app_engine):
    with org_scope(app_engine, uuid.uuid4()) as conn:
        for table in CUSTOMER_TABLES:
            assert conn.execute(text(f"SELECT count(*) FROM {table}")).scalar() == 0


def test_catalog_is_shared_reference_data(app_engine, orgs):
    counts = set()
    for org in orgs.values():
        with org_scope(app_engine, org.id) as conn:
            counts.add(conn.execute(text("SELECT count(*) FROM controls")).scalar())
    assert counts == {40}
