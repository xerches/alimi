"""Loads config/checks.yaml, the single list of checks shared by the scanner, the report and the site."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .schema import CheckDefinition, Platform

ENV_VAR = "ALIMI_CHECKS"


class Catalog(BaseModel):
    insurer_questions: dict[str, str]
    checks: list[CheckDefinition]
    source: Path | None = Field(default=None, exclude=True)

    def by_id(self, check_id: str) -> CheckDefinition:
        for check in self.checks:
            if check.id == check_id:
                return check
        raise KeyError(check_id)

    def for_platform(self, platform: Platform) -> list[CheckDefinition]:
        """Checks that apply to one platform, plus the attestations that apply to all."""
        return [c for c in self.checks if c.platform in (platform, Platform.any)]


def find_checks_file(explicit: Path | str | None = None) -> Path:
    """Locate checks.yaml: an explicit path, then $ALIMI_CHECKS, then config/checks.yaml up the tree.

    The walk starts from the working directory and from this package's folder,
    so the CLI works from anywhere inside the repo and the tests work from CI.
    """
    if explicit:
        path = Path(explicit)
        if path.is_file():
            return path
        raise FileNotFoundError(f"checks file not found: {path}")
    env = os.environ.get(ENV_VAR)
    if env:
        path = Path(env)
        if path.is_file():
            return path
        raise FileNotFoundError(f"{ENV_VAR} points at a missing file: {path}")
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for folder in (start, *start.parents):
            candidate = folder / "config" / "checks.yaml"
            if candidate.is_file():
                return candidate
    raise FileNotFoundError(
        "Could not find config/checks.yaml. Run from inside the repo, or set ALIMI_CHECKS to its path."
    )


def load_catalog(path: Path | str | None = None) -> Catalog:
    checks_file = find_checks_file(path)
    with checks_file.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    catalog = Catalog(
        insurer_questions=raw["insurer_questions"],
        checks=[CheckDefinition.model_validate(entry) for entry in raw["checks"]],
        source=checks_file,
    )
    unknown = [c.id for c in catalog.checks if c.insurer_question not in catalog.insurer_questions]
    if unknown:
        raise ValueError(f"checks map to an insurer question that is not defined: {unknown}")
    return catalog
