"""Encryption for integration tokens, and a guard that keeps them out of logs.

Fernet (from the `cryptography` package) is authenticated symmetric encryption: AES-128-CBC
plus an HMAC, with the timestamp and IV packed in. It is a good fit because it is hard to
misuse: one key, encrypt() and decrypt(), and tampering raises instead of returning garbage.
The key comes from ALIMI_TOKEN_KEY, so a copy of the database alone cannot read a token.

Run `python -m alimi_platform.crypto` to print a fresh key.
"""

from __future__ import annotations

import logging
import re

from cryptography.fernet import Fernet, InvalidToken


class Secret:
    """Wraps a decrypted token so printing, logging or an error page shows a placeholder.

    Call .reveal() at the one place the value is handed to a connector.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str):
        self._value = value

    def reveal(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "Secret('********')"

    __str__ = __repr__


class TokenBox:
    def __init__(self, key: str):
        try:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except (ValueError, TypeError):
            raise ValueError("ALIMI_TOKEN_KEY is not a valid Fernet key") from None

    def encrypt(self, token: str) -> bytes:
        return self._fernet.encrypt(token.encode("utf-8"))

    def decrypt(self, ciphertext: bytes) -> Secret:
        try:
            return Secret(self._fernet.decrypt(bytes(ciphertext)).decode("utf-8"))
        except InvalidToken:
            # Never echo the ciphertext or the key in the message.
            raise ValueError("stored token could not be decrypted with the current key") from None


# Fernet tokens start with gAAAAA; bearer tokens and client secrets have recognisable shapes too.
_SECRET_PATTERNS = [
    re.compile(r"gAAAAA[A-Za-z0-9_\-=]{20,}"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{12,}"),
    re.compile(r"(?i)((?:token|secret|password|key)\s*[=:]\s*)\S{6,}"),
]


def redact(text: str) -> str:
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(lambda m: (m.group(1) if m.groups() else "") + "[redacted]", text)
    return text


class RedactingFilter(logging.Filter):
    """Attach to the root logger so a token pasted into a message never reaches a log file."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = ()
        return True


def install_log_redaction() -> None:
    root = logging.getLogger()
    if not any(isinstance(f, RedactingFilter) for f in root.filters):
        root.addFilter(RedactingFilter())
    for handler in root.handlers:
        if not any(isinstance(f, RedactingFilter) for f in handler.filters):
            handler.addFilter(RedactingFilter())


if __name__ == "__main__":
    print(Fernet.generate_key().decode())
