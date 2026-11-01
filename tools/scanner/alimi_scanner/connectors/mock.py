"""The default connector: loads a JSON fixture instead of calling an API.

Fixtures live in tools/scanner/fixtures/<platform>/<name>.json and are plain
M365Snapshot documents. "pass" is a tenant that passes every check, "fail" is
one that trips every check. The platform picks the snapshot model. Tests mutate "pass" one field at a time to prove
each check fires on its own.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..schema import Platform
from ..snapshot import BaseSnapshot, GWSSnapshot, M365Snapshot

MODELS: dict[Platform, type[BaseSnapshot]] = {Platform.m365: M365Snapshot, Platform.gws: GWSSnapshot}

FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "fixtures"


def fixture_dir(platform: Platform | str) -> Path:
    return FIXTURE_ROOT / Platform(platform).value


def list_fixtures(platform: Platform | str = Platform.m365) -> list[str]:
    folder = fixture_dir(platform)
    if not folder.is_dir():
        return []
    return sorted(p.stem for p in folder.glob("*.json"))


def load_fixture(platform: Platform | str, name: str) -> BaseSnapshot:
    path = fixture_dir(platform) / f"{name}.json"
    if not path.is_file():
        available = ", ".join(list_fixtures(platform)) or "none"
        raise FileNotFoundError(f"no fixture '{name}' for {Platform(platform).value}; available: {available}")
    return load_snapshot_file(platform, path)


def load_snapshot_file(platform: Platform | str, path: Path) -> BaseSnapshot:
    model = MODELS[Platform(platform)]
    return model.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


class MockConnector:
    def __init__(self, platform: Platform | str = Platform.m365, fixture: str = "pass", path: Path | None = None):
        self.platform = Platform(platform)
        self.fixture = fixture
        self.path = path
        self.source = f"mock:{path.name if path else fixture}"

    def fetch(self) -> BaseSnapshot:
        if self.path:
            return load_snapshot_file(self.platform, self.path)
        return load_fixture(self.platform, self.fixture)
