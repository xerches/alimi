"""alimi_report: findings JSON from alimi_scanner in, insurer-ready HTML and PDF out.

Library first, CLI second. The platform calls render() or write_report();
the command line is a thin wrapper around the same functions.
"""

__version__ = "0.1.0"

from .brand import Brand, Reseller, load_brand  # noqa: E402,F401
from .render import Report, ReportPaths, render, render_html, write_report  # noqa: E402,F401
