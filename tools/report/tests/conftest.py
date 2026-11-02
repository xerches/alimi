from __future__ import annotations

import pytest
from alimi_scanner.catalog import load_catalog
from alimi_scanner.connectors.mock import MockConnector
from alimi_scanner.engine import run_checks
from alimi_scanner.schema import Platform, ScanResult, TenantInfo

from alimi_report.brand import Brand, Offer


def scan(platform: str, fixture: str) -> ScanResult:
    plat = Platform(platform)
    connector = MockConnector(plat, fixture=fixture)
    snapshot = connector.fetch()
    tenant = TenantInfo(display_name=snapshot.tenant_display_name, primary_domain=snapshot.primary_domain(), source=connector.source)
    return run_checks(snapshot, load_catalog(), plat, tenant)


@pytest.fixture(scope="session")
def m365_fail() -> ScanResult:
    return scan("m365", "fail")


@pytest.fixture(scope="session")
def m365_pass() -> ScanResult:
    return scan("m365", "pass")


@pytest.fixture(scope="session")
def gws_fail() -> ScanResult:
    return scan("gws", "fail")


@pytest.fixture(scope="session")
def gws_pass() -> ScanResult:
    return scan("gws", "pass")


@pytest.fixture
def brand() -> Brand:
    return Brand(display_name="Alimi", tagline="Security that insurers accept.", contact_email="hello@example.com", location="Boston, MA")


@pytest.fixture
def offer() -> Offer:
    return Offer(report_from=500, service_from=4000, report_includes=["Every finding", "Evidence pack checklist"])
