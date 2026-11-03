"""The audit log: who did what, in which organization, when. Append only for the app role."""

from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import Connection, text

from .crypto import redact


def _scrub(value):
    """Redact anything that looks like a secret, string by string, so the JSON stays valid."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {k: _scrub(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_scrub(v) for v in value]
    return value


def record(
    conn: Connection,
    org_id: UUID | str,
    actor_user_id: UUID | str | None,
    action: str,
    target: str | None = None,
    detail: dict | None = None,
) -> None:
    conn.execute(
        text(
            "INSERT INTO audit_log (organization_id, actor_user_id, action, target, detail) "
            "VALUES (:org, :actor, :action, :target, CAST(:detail AS jsonb))"
        ),
        {
            "org": str(org_id),
            "actor": str(actor_user_id) if actor_user_id else None,
            "action": action,
            "target": target,
            # Belt and braces: nothing that looks like a secret is written, even by mistake.
            "detail": json.dumps(_scrub(detail or {}), default=str),
        },
    )
