"""HTML to PDF. WeasyPrint when installed (pip install 'alimi-report[pdf]'); otherwise a clear message."""

from __future__ import annotations

from pathlib import Path


class PdfUnavailable(RuntimeError):
    pass


def pdf_backend() -> str | None:
    try:
        import weasyprint  # noqa: F401
    except Exception:  # noqa: BLE001 - missing module or missing system libraries both mean "no backend"
        return None
    return "weasyprint"


def html_to_pdf(html: str, path: Path) -> Path:
    backend = pdf_backend()
    if backend != "weasyprint":
        raise PdfUnavailable(
            "No PDF backend is installed. Run: pip install 'alimi-report[pdf]' (WeasyPrint), "
            "or open the HTML file in a browser and print to PDF."
        )
    from weasyprint import HTML

    path = Path(path)
    HTML(string=html).write_pdf(str(path))
    return path
