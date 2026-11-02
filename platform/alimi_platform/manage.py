"""Command line for setup: `python -m alimi_platform.manage init` migrates, loads the catalog
and seeds the sample organizations. docker compose runs it before starting the web server.

It connects as the table owner (ALIMI_OWNER_DATABASE_URL); the web server never does.
"""

from __future__ import annotations

import argparse
import os
import secrets
import sys
from pathlib import Path

from cryptography.fernet import Fernet

from .catalog import load, sync
from .config import load_settings
from .db import make_engine, migrate
from .seed import seed


def init(seed_samples: bool = True) -> None:
    settings = load_settings()
    owner = make_engine(settings.owner_database_url)
    try:
        applied = migrate(owner)
        print(f"migrations applied: {', '.join(applied) or 'none (up to date)'}")
        with owner.begin() as conn:
            sync(conn, load(settings.repo_root))
        print("catalog loaded from config/ and policies/requirements.yaml")
        if seed_samples:
            seed(owner, settings)
            print("sample organizations ready (mock data only)")
    finally:
        owner.dispose()


def ensure_keys(folder: Path) -> None:
    """Mock mode only: create a token key and a session secret in `folder` if they are missing.

    docker compose keeps that folder on its own volume, outside the database, so the key
    survives restarts and a copy of the database alone cannot decrypt a token. Anything that
    ever holds real data gets its key from a secret manager instead.
    """
    if os.environ.get("ALIMI_MODE", "mock") != "mock":
        raise SystemExit("ensure-keys only runs in mock mode")
    folder.mkdir(parents=True, exist_ok=True)
    for name, make in (("token.key", lambda: Fernet.generate_key().decode()), ("session.secret", lambda: secrets.token_urlsafe(48))):
        path = folder / name
        if not path.exists():
            path.write_text(make(), encoding="utf-8")
            path.chmod(0o600)
            print(f"created {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="alimi-platform")
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init", help="migrate, load the catalog and seed sample data")
    p_init.add_argument("--no-seed", action="store_true", help="skip the sample organizations")
    p_keys = sub.add_parser("ensure-keys", help="mock mode: create the token key and session secret files")
    p_keys.add_argument("--dir", default="/var/lib/alimi", type=Path)
    args = parser.parse_args(argv)
    if args.command == "init":
        init(seed_samples=not args.no_seed)
    elif args.command == "ensure-keys":
        ensure_keys(args.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
