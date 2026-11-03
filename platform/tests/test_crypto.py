from __future__ import annotations

import logging

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import text

from alimi_platform.crypto import RedactingFilter, Secret, TokenBox, redact
from alimi_platform.db import org_scope


def test_round_trip_and_wrong_key():
    box = TokenBox(Fernet.generate_key().decode())
    ciphertext = box.encrypt("very-secret-value")
    assert b"very-secret-value" not in ciphertext
    assert box.decrypt(ciphertext).reveal() == "very-secret-value"
    with pytest.raises(ValueError):
        TokenBox(Fernet.generate_key().decode()).decrypt(ciphertext)


def test_bad_key_is_rejected_without_echoing_it():
    with pytest.raises(ValueError) as info:
        TokenBox("not-a-key")
    assert "not-a-key" not in str(info.value)


def test_secret_never_prints():
    s = Secret("hunter2-token")
    assert "hunter2" not in repr(s) and "hunter2" not in str(s) and "hunter2" not in f"{s}"


def test_redaction_patterns():
    assert "abc123secretvalue" not in redact("token=abc123secretvalue")
    assert "eyJhbGciOiJIUzI1" not in redact("Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.x.y")
    assert "[redacted]" in redact(TokenBox(Fernet.generate_key().decode()).encrypt("x").decode())


def test_log_filter_scrubs_messages(caplog):
    logger = logging.getLogger("alimi.test")
    logger.addFilter(RedactingFilter())
    with caplog.at_level(logging.INFO, logger="alimi.test"):
        logger.info("connecting with secret=%s", "s3cr3t-value-here")
    assert "s3cr3t-value-here" not in caplog.text
    assert "[redacted]" in caplog.text


def test_tokens_are_stored_encrypted(app_engine, settings, orgs):
    org = orgs["saltmarsh"]
    with org_scope(app_engine, org.id) as conn:
        stored = conn.execute(text("SELECT token_ciphertext FROM integrations")).scalar()
    assert b"mock-token" not in bytes(stored)
    assert TokenBox(settings.token_key).decrypt(stored).reveal() == f"mock-token-for-{org.slug}"
