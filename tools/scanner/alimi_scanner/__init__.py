"""alimi_scanner: read-only security checks for Microsoft 365 and Google Workspace.

Library first, CLI second. The platform web app imports run_checks, the
connectors and the schema without ever touching the command line.
"""

__version__ = "0.1.0"

from .schema import Finding, Platform, ScanResult, Severity, Status  # noqa: E402,F401
