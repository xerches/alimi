"""Public DNS lookups for SPF, DKIM and DMARC.

These records are public, so no tenant permission is involved. DKIM is set up
when the provider's selector record exists: Microsoft 365 uses two CNAMEs,
selector1._domainkey and selector2._domainkey; Google Workspace uses a TXT
record at google._domainkey by default.
"""

from __future__ import annotations

import dns.exception
import dns.resolver

from ..snapshot import DomainEmailAuth

M365_DKIM_SELECTORS = ("selector1", "selector2")
GOOGLE_DKIM_SELECTORS = ("google",)


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


def dkim_enabled(domain: str, selectors: tuple[str, ...] = M365_DKIM_SELECTORS) -> bool:
    for selector in selectors:
        name = f"{selector}._domainkey.{domain}"
        for record_type in ("CNAME", "TXT"):
            try:
                dns.resolver.resolve(name, record_type)
                return True
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                continue
    return False


def dkim_enabled_m365(domain: str) -> bool:
    return dkim_enabled(domain, M365_DKIM_SELECTORS)


def lookup_domain(domain: str, dkim_selectors: tuple[str, ...] = M365_DKIM_SELECTORS) -> DomainEmailAuth:
    """Raises dns.exception.DNSException when the resolver itself fails (no network, timeout)."""
    return DomainEmailAuth(
        domain=domain,
        spf=spf_record(domain),
        dkim_enabled=dkim_enabled(domain, dkim_selectors),
        dmarc=dmarc_record(domain),
    )


DNSError = dns.exception.DNSException
