from __future__ import annotations

import pytest

from alimi_platform.config import ConfigError, load_settings


def test_refuses_to_start_outside_mock_mode(monkeypatch):
    monkeypatch.setenv("ALIMI_MODE", "live")
    monkeypatch.setenv("ALIMI_TOKEN_KEY", "x")
    monkeypatch.setenv("ALIMI_SESSION_SECRET", "x")
    with pytest.raises(ConfigError, match="mock"):
        load_settings()


def test_needs_a_token_key(monkeypatch):
    monkeypatch.setenv("ALIMI_MODE", "mock")
    monkeypatch.delenv("ALIMI_TOKEN_KEY", raising=False)
    monkeypatch.setenv("ALIMI_SESSION_SECRET", "x")
    with pytest.raises(ConfigError, match="ALIMI_TOKEN_KEY"):
        load_settings()


def test_app_factory_refuses_a_live_settings_object(mock_settings):
    from alimi_platform.main import create_app

    with pytest.raises(ConfigError):
        create_app(mock_settings(mode="live"))
