"""Shared findings schema.

Every connector produces a snapshot, every check turns part of that snapshot
into a Finding, and a scan run bundles the findings into a ScanResult. The
report generator and, later, the platform read ScanResult JSON and nothing
else, so this file is the contract between the pieces.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = "1"


class Platform(str, Enum):
    m365 = "m365"
    gws = "gws"
    any = "any"  # attestation checks apply to every platform


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


# Weight used for the overall score. A failed critical check costs four times a failed low one.
SEVERITY_WEIGHT: dict[Severity, int] = {
    Severity.critical: 4,
    Severity.high: 3,
    Severity.medium: 2,
    Severity.low: 1,
}


class Status(str, Enum):
    passed = "pass"
    failed = "fail"
    attestation_needed = "attestation_needed"  # cannot be read from the tenant; client supplies evidence
    error = "error"  # the check could not run, usually a missing permission
    not_applicable = "not_applicable"


class CheckKind(str, Enum):
    automated = "automated"
    attestation = "attestation"


class CheckDefinition(BaseModel):
    """One entry from config/checks.yaml."""

    id: str
    platform: Platform
    kind: CheckKind
    title: str
    severity: Severity
    insurer_question: str
    explain: str
    remediation: str
    pass_when: str | None = None
    evidence: str | None = None


class CheckOutcome(BaseModel):
    """What a check function returns. The engine adds the catalog fields around it."""

    status: Status
    summary: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    check_id: str
    platform: Platform
    kind: CheckKind
    title: str
    severity: Severity
    status: Status
    insurer_question: str
    insurer_question_text: str
    summary: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    remediation: str
    evidence_requested: str | None = None
    notes: list[str] = Field(default_factory=list)


class TenantInfo(BaseModel):
    """Enough to label a report. Never the tenant ID: that stays out of every output file."""

    display_name: str | None = None
    primary_domain: str | None = None
    source: str = "mock"


class Summary(BaseModel):
    total: int
    passed: int
    failed: int
    attestation_needed: int
    errors: int
    not_applicable: int
    score_percent: float | None = Field(
        default=None,
        description="Severity-weighted share of automated checks that passed, out of those that could be evaluated.",
    )


class InsurerAnswer(BaseModel):
    question_id: str
    question_text: str
    status: str  # pass | fail | attestation_needed | unknown
    check_ids: list[str] = Field(default_factory=list)


class ScanResult(BaseModel):
    schema_version: str = SCHEMA_VERSION
    scanner_version: str
    platform: Platform
    tenant: TenantInfo
    collected_at: datetime
    findings: list[Finding]
    summary: Summary
    insurer_answers: list[InsurerAnswer]
    notes: list[str] = Field(default_factory=list)
