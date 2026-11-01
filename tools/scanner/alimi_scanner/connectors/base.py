"""What every connector looks like, so the engine and the CLI can treat mock and real tenants alike."""

from __future__ import annotations

from typing import Protocol

from ..schema import Platform
from ..snapshot import M365Snapshot


class Connector(Protocol):
    platform: Platform
    source: str  # "mock:pass", "graph", ... goes into TenantInfo.source

    def fetch(self) -> M365Snapshot:
        """Read everything the checks need, once, and return it. Read-only by construction."""
        ...
