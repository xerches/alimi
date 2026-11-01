"""Public DNS lookups for SPF, DKIM and DMARC.

These records are public, so no tenant permission is involved. Microsoft 365
signs mail with DKIM through two CNAMEs, selector1._domainkey and
selector2._domainkey, so their presence is the signal that DKIM is set up.
"""

from __future__ import annotations

import dns.exception
import dns.resolver

from ..snapshot import DomainEmailAuth

M365_DKIM_SELECTORS = ("selector1", "selector2")


def _txt(name: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(name, "TXT")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return []
    records = []
    for rdata in answers:
        records.append("".join(part.decode("utf-8", "replace") for part in rdata.strings))
    return records


def spf_record(domain: str) -> str | None:
    for record in _txt(domain):
        if record.lower().startswith("v=spf1"):
            return record
    return None


def dmarc_record(domain: str) -> str | None:
    for record in _txt(f"_dmarc.{domain}"):
        if record.lower().startswith("v=dmarc1"):
            return record
    return None


def dkim_enabled_m365(domain: str) -> bool:
    for selector in M365_DKIM_SELECTORS:
        try:
            dns.resolver.resolve(f"{selector}._domainkey.{domain}", "CNAME")
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            continue
    return False


def lookup_domain(domain: str) -> DomainEmailAuth:
    """Raises dns.exception.DNSException when the resolver itself fails (no network, timeout)."""
    return DomainEmailAuth(
        domain=domain,
        spf=spf_record(domain),
        dkim_enabled=dkim_enabled_m365(domain),
        dmarc=dmarc_record(domain),
    )


DNSError = dns.exception.DNSException
