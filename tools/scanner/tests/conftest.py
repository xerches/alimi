from __future__ import annotations

import pytest

from alimi_scanner.catalog import load_catalog
from alimi_scanner.connectors.mock import load_fixture
from alimi_scanner.schema import Platform, TenantInfo


@pytest.fixture(scope="session")
def catalog():
    return load_catalog()


@pytest.fixture
def pass_snapshot():
    return load_fixture(Platform.m365, "pass")


@pytest.fixture
def fail_snapshot():
    return load_fixture(Platform.m365, "fail")


@pytest.fixture
def gws_pass_snapshot():
    return load_fixture(Platform.gws, "pass")


@pytest.fixture
def gws_fail_snapshot():
    return load_fixture(Platform.gws, "fail")


@pytest.fixture
def tenant():
    return TenantInfo(display_name="Test", primary_domain="example.com", source="test")
