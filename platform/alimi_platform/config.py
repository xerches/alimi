"""Settings, read once from the environment.

Plain environment variables rather than a settings library: there are only a handful, and
reading os.environ in one place keeps every knob visible on one screen.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    mode: str                  # "mock" until the customer-data gate in CLAUDE.md is met
    database_url: str          # the app role: cannot bypass row-level security
    owner_database_url: str    # the table owner: migrations and the sample seed only
    token_key: str             # Fernet key for integration tokens; never stored in the database
    session_secret: str        # signs the session cookie
    repo_root: Path

    @property
    def is_mock(self) -> bool:
        return self.mode == "mock"


def _secret(env: dict, name: str) -> str:
    """A secret from NAME, or from the file NAME_FILE points at (how docker compose passes them)."""
    value = env.get(name, "")
    path = env.get(f"{name}_FILE")
    if not value and path and Path(path).is_file():
        value = Path(path).read_text(encoding="utf-8").strip()
    return value


def load_settings() -> Settings:
    env = os.environ
    mode = env.get("ALIMI_MODE", "mock")
    settings = Settings(
        mode=mode,
        database_url=env.get(
            "ALIMI_DATABASE_URL", "postgresql+psycopg://alimi_app:alimi_app_local@localhost:5432/alimi"
        ),
        owner_database_url=env.get(
            "ALIMI_OWNER_DATABASE_URL", "postgresql+psycopg://alimi_owner:alimi_owner_local@localhost:5432/alimi"
        ),
        token_key=_secret(env, "ALIMI_TOKEN_KEY"),
        session_secret=_secret(env, "ALIMI_SESSION_SECRET"),
        repo_root=Path(env.get("ALIMI_REPO_ROOT", REPO_ROOT)),
    )
    if mode != "mock":
        # Live mode needs real login (12b) and the customer-data gate. Until then it does not start.
        raise ConfigError(
            "ALIMI_MODE must be 'mock'. Live mode waits for real login (prompt 12b) and the "
            "customer-data gate in CLAUDE.md (LLC, insurance, signed pilot letter, outside review)."
        )
    if not settings.token_key:
        raise ConfigError("ALIMI_TOKEN_KEY is not set. Generate one with: python -m alimi_platform.crypto")
    if not settings.session_secret:
        raise ConfigError("ALIMI_SESSION_SECRET is not set. Any long random string works in mock mode.")
    return settings
