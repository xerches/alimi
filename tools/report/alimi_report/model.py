"""Turns a ScanResult into the view model the template renders.

Everything the report says is decided here, in plain Python, so it can be
tested without rendering HTML: the grade, the insurer answers, the ranking
of fixes, the evidence pack and the glossary.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from alimi_scanner.catalog import Catalog
from alimi_scanner.schema import SEVERITY_WEIGHT, CheckKind, Finding, Platform, ScanResult, Severity, Status
from pydantic import BaseModel, Field

from .brand import Brand, Offer, Reseller

PLATFORM_LABEL = {Platform.m365: "Microsoft 365", Platform.gws: "Google Workspace", Platform.any: "Workspace"}

# Score bands in words a business owner can repeat to a broker.
GRADES: list[tuple[float, str, str]] = [
    (90, "Strong", "The essentials insurers ask about are in place. Keep the evidence current and fix the few items below."),
    (75, "Good", "Most protections are in place. A short list of fixes would make the answers to an insurer clean."),
    (50, "Needs work", "Several protections insurers expect are missing or unproven. The fixes below are the priority."),
    (0, "At risk", "Core protections are missing. Start with the critical fixes below before the next renewal or customer questionnaire."),
]

ANSWER_LABEL = {
    "pass": "Yes",
    "fail": "No",
    "attestation_needed": "You confirm",
    "unknown": "Not checked",
}
ANSWER_HELP = {
    "pass": "The tenant settings support a yes.",
    "fail": "At least one check behind this question failed. See the fixes.",
    "attestation_needed": "Not readable from the tenant. Attach the evidence listed in the evidence pack.",
    "unknown": "A check could not run, usually a missing permission. Re-run after granting it.",
}

STATUS_LABEL = {
    Status.failed: "Fix",
    Status.attestation_needed: "You confirm",
    Status.error: "Could not check",
    Status.passed: "In place",
    Status.not_applicable: "Not applicable",
}

SECTION_ORDER = [
    (Status.failed, "What needs fixing"),
    (Status.attestation_needed, "What you confirm with evidence"),
    (Status.error, "What could not be checked"),
    (Status.passed, "What is already in place"),
    (Status.not_applicable, "Not applicable to this tenant"),
]

GLOSSARY = [
    ("MFA", "Multi-factor authentication: a second proof of identity at sign-in, such as an app prompt, on top of the password."),
    ("2-Step Verification", "Google's name for multi-factor authentication."),
    ("Conditional Access", "Microsoft 365 rules that decide when a sign-in is allowed and whether it must use MFA."),
    ("Security Defaults", "Microsoft's basic protection switch for tenants without Conditional Access: MFA for everyone, legacy sign-ins blocked."),
    ("legacy authentication", "Old sign-in protocols (POP, IMAP, SMTP AUTH) that cannot ask for a second factor."),
    ("SPF", "A DNS record naming the servers allowed to send mail for your domain."),
    ("DKIM", "A signature on outgoing mail that proves it came from your domain unchanged."),
    ("DMARC", "A DNS policy telling other mail systems what to do with mail that fails SPF and DKIM: none, quarantine or reject."),
    ("EDR", "Endpoint detection and response: software on laptops and servers that spots and stops attacks, beyond antivirus."),
    ("OAuth app", "A third-party app a user has granted access to company mail, files or calendar with a click."),
    ("Secure Score", "Microsoft's own 0 to 100 rating of a tenant's security settings."),
    ("break-glass account", "A spare admin account kept for emergencies, excluded from day-to-day use."),
    ("tabletop", "A one-hour walk-through of a pretend incident to test the response plan."),
]


class FixCard(BaseModel):
    rank: int
    check_id: str
    title: str
    severity: Severity
    found: str
    why: str
    what_to_do: str


class QuestionRow(BaseModel):
    question_id: str
    question_text: str
    status: str
    label: str
    help: str
    checks: list[str] = Field(default_factory=list)


class FindingCard(BaseModel):
    check_id: str
    title: str
    severity: Severity
    status: Status
    status_label: str
    kind: CheckKind
    found: str
    why: str | None = None
    what_to_do: str
    evidence_requested: str | None = None
    notes: list[str] = Field(default_factory=list)
    evidence: list[tuple[str, str]] = Field(default_factory=list)


class Section(BaseModel):
    status: Status
    title: str
    findings: list[FindingCard]


class EvidenceItem(BaseModel):
    check_id: str
    title: str
    attach: str
    answers: str  # the insurer question it supports


class Counts(BaseModel):
    passed: int
    failed: int
    attestation_needed: int
    errors: int
    not_applicable: int
    automated_total: int


class ReportModel(BaseModel):
    brand: Brand
    reseller: Reseller | None = None
    reseller_logo: str | None = None
    offer: Offer
    free: bool
    title: str
    tenant_name: str
    platform_label: str
    source: str
    collected_at: datetime
    generated_at: datetime
    scanner_version: str
    score: float | None
    grade: str
    grade_sentence: str
    counts: Counts
    questions: list[QuestionRow]
    top_fixes: list[FixCard]
    sections: list[Section]
    evidence_pack: list[EvidenceItem]
    notes: list[str]
    glossary: list[tuple[str, str]]


def grade_for(score: float | None) -> tuple[str, str]:
    if score is None:
        return "Not scored", "No automated check could be evaluated, so there is no score. Grant the listed permissions and run again."
    for threshold, name, sentence in GRADES:
        if score >= threshold:
            return name, sentence
    return GRADES[-1][1], GRADES[-1][2]


def rank_fixes(findings: list[Finding], explain: dict[str, str], limit: int = 5) -> list[FixCard]:
    failed = [f for f in findings if f.status == Status.failed]
    failed.sort(key=lambda f: (-SEVERITY_WEIGHT[f.severity], f.check_id))
    return [
        FixCard(
            rank=i + 1,
            check_id=f.check_id,
            title=f.title,
            severity=f.severity,
            found=f.summary,
            why=explain.get(f.check_id, ""),
            what_to_do=f.remediation,
        )
        for i, f in enumerate(failed[:limit])
    ]


def evidence_pack(findings: list[Finding]) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for f in findings:
        if f.kind == CheckKind.attestation and f.evidence_requested:
            items.append(EvidenceItem(check_id=f.check_id, title=f.title, attach=f.evidence_requested, answers=f.insurer_question_text))
        elif f.status == Status.attestation_needed:
            items.append(EvidenceItem(check_id=f.check_id, title=f.title, attach=f.summary, answers=f.insurer_question_text))
        elif f.status == Status.error:
            items.append(
                EvidenceItem(
                    check_id=f.check_id,
                    title=f.title,
                    attach="Nothing to attach yet: " + f.summary,
                    answers=f.insurer_question_text,
                )
            )
    return items


def _evidence_rows(evidence: dict[str, Any], max_items: int = 8) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for key, value in evidence.items():
        label = key.replace("_", " ")
        if isinstance(value, list):
            if not value:
                continue
            shown = [_short(v) for v in value[:max_items]]
            more = f" and {len(value) - max_items} more" if len(value) > max_items else ""
            rows.append((label, ", ".join(shown) + more))
        elif isinstance(value, dict):
            rows.append((label, ", ".join(f"{k}: {_short(v)}" for k, v in list(value.items())[:max_items])))
        elif value is None:
            rows.append((label, "unknown"))
        else:
            rows.append((label, _short(value)))
    return rows


def _short(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, dict):
        return "; ".join(f"{k}: {_short(v)}" for k, v in value.items())
    if isinstance(value, list):
        return ", ".join(_short(v) for v in value)
    text = str(value)
    return text if len(text) <= 80 else text[:77] + "..."


def glossary_for(texts: list[str]) -> list[tuple[str, str]]:
    blob = " ".join(texts).lower()
    picked = []
    for term, meaning in GLOSSARY:
        if term.lower() in blob:
            picked.append((term, meaning))
    return picked


def build_model(
    result: ScanResult,
    *,
    brand: Brand,
    offer: Offer,
    catalog: Catalog | None = None,
    reseller: Reseller | None = None,
    free: bool = False,
    now: datetime | None = None,
) -> ReportModel:
    explain = {c.id: c.explain for c in catalog.checks} if catalog else {}
    findings = result.findings
    score = result.summary.score_percent
    grade, sentence = grade_for(score)

    questions = [
        QuestionRow(
            question_id=a.question_id,
            question_text=a.question_text,
            status=a.status,
            label=ANSWER_LABEL.get(a.status, "Not checked"),
            help=ANSWER_HELP.get(a.status, ANSWER_HELP["unknown"]),
            checks=[f.title for f in findings if f.check_id in a.check_ids],
        )
        for a in result.insurer_answers
    ]

    sections = []
    for status, title in SECTION_ORDER:
        cards = [
            FindingCard(
                check_id=f.check_id,
                title=f.title,
                severity=f.severity,
                status=f.status,
                status_label=STATUS_LABEL[f.status],
                kind=f.kind,
                found=f.summary,
                why=explain.get(f.check_id),
                what_to_do=f.remediation,
                evidence_requested=f.evidence_requested,
                notes=list(f.notes),
                evidence=_evidence_rows(f.evidence),
            )
            for f in sorted((x for x in findings if x.status == status), key=lambda x: (-SEVERITY_WEIGHT[x.severity], x.check_id))
        ]
        if cards:
            sections.append(Section(status=status, title=title, findings=cards))

    automated = [f for f in findings if f.kind == CheckKind.automated]
    counts = Counts(
        passed=result.summary.passed,
        failed=result.summary.failed,
        attestation_needed=result.summary.attestation_needed,
        errors=result.summary.errors,
        not_applicable=result.summary.not_applicable,
        automated_total=len(automated),
    )
    texts = [f.title + " " + f.summary + " " + f.remediation for f in findings] + [explain.get(f.check_id, "") for f in findings]
    tenant_name = result.tenant.display_name or result.tenant.primary_domain or "your tenant"
    return ReportModel(
        brand=brand,
        reseller=reseller,
        reseller_logo=reseller.logo_data_uri() if reseller else None,
        offer=offer,
        free=free,
        title=f"{PLATFORM_LABEL[result.platform]} security report",
        tenant_name=tenant_name,
        platform_label=PLATFORM_LABEL[result.platform],
        source=result.tenant.source,
        collected_at=result.collected_at,
        generated_at=now or datetime.now(timezone.utc),
        scanner_version=result.scanner_version,
        score=score,
        grade=grade,
        grade_sentence=sentence,
        counts=counts,
        questions=questions,
        top_fixes=rank_fixes(findings, explain),
        sections=sections,
        evidence_pack=evidence_pack(findings),
        notes=list(result.notes),
        glossary=glossary_for(texts),
    )
