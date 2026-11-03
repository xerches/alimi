"""Test setup: a fresh database built the same way docker compose builds one.

Needs a running Postgres and a superuser URL in ALIMI_TEST_ADMIN_URL (CI provides one through
a service container; locally, point it at any Postgres 14+). The superuser is used only here,
to create the two roles and a throwaway database. Everything after that runs as alimi_owner
(migrations, catalog, seed) and alimi_app (the tests), exactly as in production.
"""

from __future__ import annotations

import os
from dataclasses import replace

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from alimi_platform.catalog import load, sync
from alimi_platform.config import REPO_ROOT, Settings
from alimi_platform.db import make_engine, migrate
from alimi_platform.seed import SAMPLE_ORGS, seed

ADMIN_URL = os.environ.get("ALIMI_TEST_ADMIN_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres")
TEST_DB = "alimi_test"
OWNER_PW = "alimi_owner_local"
APP_PW = "alimi_app_local"


def _url(user: str, password: str) -> str:
    return make_url(ADMIN_URL).set(username=user, password=password, database=TEST_DB).render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def database():
    admin = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)"))
        for role, pw, extra in (("alimi_owner", OWNER_PW, ""), ("alimi_app", APP_PW, " NOCREATEDB")):
            exists = conn.execute(text("SELECT 1 FROM pg_roles WHERE rolname = :r"), {"r": role}).first()
            verb = "ALTER" if exists else "CREATE"
            conn.execute(text(f"{verb} ROLE {role} LOGIN PASSWORD '{pw}' NOSUPERUSER NOCREATEROLE NOBYPASSRLS{extra}"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB} OWNER alimi_owner"))
    test_admin = create_engine(make_url(ADMIN_URL).set(database=TEST_DB), isolation_level="AUTOCOMMIT")
    with test_admin.connect() as conn:
        conn.execute(text("ALTER SCHEMA public OWNER TO alimi_owner"))
        conn.execute(text("REVOKE ALL ON SCHEMA public FROM PUBLIC"))
        conn.execute(text(f"GRANT CONNECT ON DATABASE {TEST_DB} TO alimi_app"))
    test_admin.dispose()

    settings = Settings(
        mode="mock",
        database_url=_url("alimi_app", APP_PW),
        owner_database_url=_url("alimi_owner", OWNER_PW),
        token_key=Fernet.generate_key().decode(),
        session_secret="test-session-secret",
        repo_root=REPO_ROOT,
    )
    owner = make_engine(settings.owner_database_url)
    migrate(owner)
    with owner.begin() as conn:
        sync(conn, load(REPO_ROOT))
    seed(owner, settings)
    yield settings, owner
    owner.dispose()
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)"))
    admin.dispose()


@pytest.fixture(scope="session")
def settings(database):
    return database[0]


@pytest.fixture(scope="session")
def owner_engine(database):
    return database[1]


@pytest.fixture(scope="session")
def app_engine(settings):
    engine = make_engine(settings.database_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def orgs():
    return {o.slug: o for o in SAMPLE_ORGS}


@pytest.fixture
def client(settings, app_engine):
    from fastapi.testclient import TestClient

    from alimi_platform.main import create_app

    with TestClient(create_app(settings, app_engine)) as c:
        yield c


@pytest.fixture
def signed_in(client, orgs):
    def _sign_in(slug: str, user_index: int = 0):
        org = orgs[slug]
        r = client.post(
            "/login",
            data={"org_id": str(org.id), "user_id": str(org.users[user_index].id)},
            follow_redirects=False,
        )
        assert r.status_code == 303, r.text
        return client

    return _sign_in


@pytest.fixture
def mock_settings(settings):
    return lambda **kw: replace(settings, **kw)
