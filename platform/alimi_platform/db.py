"""Database access: one engine for the app role, and the per-request organization context.

SQLAlchemy Core with plain SQL rather than the ORM. The tables, constraints and row-level
security are defined in SQL migrations, so writing the queries in SQL too keeps one language
for the data layer and makes it obvious that nothing filters by organization in Python:
Postgres does it. SQLAlchemy still earns its place for the connection pool and for safe
parameter binding (:name placeholders, never string formatting).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

from sqlalchemy import Connection, Engine, create_engine, text

MIGRATIONS = Path(__file__).parent / "migrations"


def make_engine(url: str) -> Engine:
    # pool_pre_ping drops connections the database closed while idle.
    return create_engine(url, pool_pre_ping=True, future=True)


@contextmanager
def org_scope(engine: Engine, org_id: UUID | str | None, user_id: UUID | str | None = None) -> Iterator[Connection]:
    """A transaction that acts for one organization.

    set_config(..., true) is the function form of SET LOCAL: the value lasts until this
    transaction commits or rolls back, then the pooled connection is clean again.
    """
    with engine.begin() as conn:
        conn.execute(
            text("SELECT set_config('app.org_id', :org, true), set_config('app.user_id', :user, true)"),
            {"org": str(org_id) if org_id else "", "user": str(user_id) if user_id else ""},
        )
        yield conn


def migrate(owner_engine: Engine) -> list[str]:
    """Apply every migrations/*.sql file not applied yet, in name order. Returns what it applied."""
    applied_now: list[str] = []
    with owner_engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                " name text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
            )
        )
        # One migrator at a time, even if two containers start together.
        conn.execute(text("SELECT pg_advisory_xact_lock(4242)"))
        done = {row[0] for row in conn.execute(text("SELECT name FROM schema_migrations"))}
        for path in sorted(MIGRATIONS.glob("*.sql")):
            if path.name in done:
                continue
            # Straight to the psycopg cursor with no parameters, so the file may hold many
            # statements and format('%I') calls without being read as placeholders.
            with conn.connection.driver_connection.cursor() as cur:
                cur.execute(path.read_text(encoding="utf-8"))
            conn.execute(text("INSERT INTO schema_migrations (name) VALUES (:n)"), {"n": path.name})
            applied_now.append(path.name)
    return applied_now
