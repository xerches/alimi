"""Runs the registered check functions over a snapshot and builds the ScanResult.

How a check joins in: a function in alimi_scanner.checks decorated with
@check("m365.some.id") that takes (snapshot, definition) and returns a
CheckOutcome. The engine matches it to its entry in checks.yaml, wraps the
outcome in a Finding, and rolls the findings up into insurer answers and a
score. A check that raises becomes an "error" finding, never a crash.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from datetime import datetime, timezone

from . import __version__
from .catalog import Catalog
from .schema import (
    SEVERITY_WEIGHT,
    CheckDefinition,
    CheckKind,
    CheckOutcome,
    Finding,
    InsurerAnswer,
    Platform,
    ScanResult,
    Status,
    Summary,
    TenantInfo,
)
from .snapshot import BaseSnapshot

CheckFunc = Callable[[BaseSnapshot, CheckDefinition], CheckOutcome]

_REGISTRY: dict[str, CheckFunc] = {}


def check(check_id: str) -> Callable[[CheckFunc], CheckFunc]:
    """Register a function as the implementation of one checks.yaml id."""

    def register(func: CheckFunc) -> CheckFunc:
        if check_id in _REGISTRY:
            raise ValueError(f"check {check_id} registered twice")
        _REGISTRY[check_id] = func
        return func

    return register


def registered_ids() -> list[str]:
    _load_check_modules()
    return sorted(_REGISTRY)


def _load_check_modules() -> None:
    # Importing the package runs the decorators. Done lazily so schema-only users pay nothing.
    importlib.import_module("alimi_scanner.checks")


def run_checks(
    snapshot: BaseSnapshot,
    catalog: Catalog,
    platform: Platform,
    tenant: TenantInfo,
) -> ScanResult:
    _load_check_modules()
    findings: list[Finding] = []
    for definition in catalog.for_platform(platform):
        question_text = catalog.insurer_questions[definition.insurer_question]
        if definition.kind == CheckKind.attestation:
            findings.append(_attestation_finding(definition, question_text))
            continue
        func = _REGISTRY.get(definition.id)
        if func is None:
            outcome = CheckOutcome(
                status=Status.error,
                summary="No check function is implemented for this id yet.",
            )
        else:
            try:
                outcome = func(snapshot, definition)
            except Exception as exc:  # noqa: BLE001 - one bad check must not sink the scan
                outcome = CheckOutcome(
                    status=Status.error,
                    summary=f"The check raised an error: {type(exc).__name__}: {exc}",
                )
        findings.append(
            Finding(
                check_id=definition.id,
                platform=definition.platform,
                kind=definition.kind,
                title=definition.title,
                severity=definition.severity,
                status=outcome.status,
                insurer_question=definition.insurer_question,
                insurer_question_text=question_text,
                summary=outcome.summary,
                evidence=outcome.evidence,
                remediation=definition.remediation,
                notes=outcome.notes,
            )
        )
    return ScanResult(
        scanner_version=__version__,
        platform=platform,
        tenant=tenant,
        collected_at=snapshot.collected_at or datetime.now(timezone.utc),
        findings=findings,
        summary=summarize(findings),
        insurer_answers=insurer_answers(findings, catalog),
        notes=list(snapshot.notes),
    )


def _attestation_finding(definition: CheckDefinition, question_text: str) -> Finding:
    return Finding(
        check_id=definition.id,
        platform=definition.platform,
        kind=definition.kind,
        title=definition.title,
        severity=definition.severity,
        status=Status.attestation_needed,
        insurer_question=definition.insurer_question,
        insurer_question_text=question_text,
        summary="This cannot be read from the tenant. The client confirms it and supplies the evidence.",
        remediation=definition.remediation,
        evidence_requested=definition.evidence,
    )


def summarize(findings: list[Finding]) -> Summary:
    counts = {status: 0 for status in Status}
    for finding in findings:
        counts[finding.status] += 1
    evaluable = [f for f in findings if f.kind == CheckKind.automated and f.status in (Status.passed, Status.failed)]
    total_weight = sum(SEVERITY_WEIGHT[f.severity] for f in evaluable)
    passed_weight = sum(SEVERITY_WEIGHT[f.severity] for f in evaluable if f.status == Status.passed)
    score = round(100.0 * passed_weight / total_weight, 1) if total_weight else None
    return Summary(
        total=len(findings),
        passed=counts[Status.passed],
        failed=counts[Status.failed],
        attestation_needed=counts[Status.attestation_needed],
        errors=counts[Status.error],
        not_applicable=counts[Status.not_applicable],
        score_percent=score,
    )


def insurer_answers(findings: list[Finding], catalog: Catalog) -> list[InsurerAnswer]:
    """One line per underwriting question: fail beats unknown beats attestation beats pass."""
    answers: list[InsurerAnswer] = []
    for question_id, question_text in catalog.insurer_questions.items():
        related = [f for f in findings if f.insurer_question == question_id]
        statuses = {f.status for f in related}
        if Status.failed in statuses:
            status = "fail"
        elif Status.error in statuses:
            status = "unknown"
        elif Status.attestation_needed in statuses:
            status = "attestation_needed"
        elif Status.passed in statuses:
            status = "pass"
        else:
            status = "unknown"
        answers.append(
            InsurerAnswer(
                question_id=question_id,
                question_text=question_text,
                status=status,
                check_ids=[f.check_id for f in related],
            )
        )
    return answers
