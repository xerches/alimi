"""SPF, DKIM and DMARC evaluation shared by the Microsoft 365 and Google Workspace checks."""

from __future__ import annotations

import re

from ..schema import CheckOutcome, Status
from ..snapshot import DomainEmailAuth

_DMARC_POLICY = re.compile(r"(?:^|;)\s*p\s*=\s*(none|quarantine|reject)", re.IGNORECASE)


def dmarc_policy(record: str | None) -> str | None:
    match = _DMARC_POLICY.search(record or "")
    return match.group(1).lower() if match else None


def evaluate_email_auth(records: list[DomainEmailAuth] | None, *, provider_default: str) -> CheckOutcome:
    if records is None:
        return CheckOutcome(
            status=Status.error,
            summary="DNS lookups for SPF, DKIM and DMARC did not run, so the sending domains could not be checked.",
            notes=["missing data: DNS records for the verified domains"],
        )
    if not records:
        return CheckOutcome(
            status=Status.not_applicable,
            summary=f"The tenant has no custom domain; mail only uses {provider_default}.",
        )
    per_domain = []
    failing = []
    for record in records:
        spf_ok = bool(record.spf and record.spf.lower().startswith("v=spf1"))
        policy = dmarc_policy(record.dmarc)
        dmarc_ok = policy in ("quarantine", "reject")
        dkim_ok = record.dkim_enabled is True
        per_domain.append({"domain": record.domain, "spf": spf_ok, "dkim": record.dkim_enabled, "dmarc_policy": policy})
        gaps = []
        if not spf_ok:
            gaps.append("no SPF")
        if not dkim_ok:
            gaps.append("DKIM not enabled")
        if not dmarc_ok:
            gaps.append(f"DMARC {policy or 'missing'}")
        if gaps:
            failing.append(f"{record.domain} ({', '.join(gaps)})")
    evidence = {"domains": per_domain}
    if failing:
        return CheckOutcome(
            status=Status.failed,
            summary=f"{len(failing)} of {len(records)} sending domains are not fully protected: {'; '.join(failing)}.",
            evidence=evidence,
        )
    return CheckOutcome(
        status=Status.passed,
        summary=f"SPF, DKIM and an enforcing DMARC policy are in place on all {len(records)} sending domains.",
        evidence=evidence,
    )
