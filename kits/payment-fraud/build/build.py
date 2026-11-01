#!/usr/bin/env python3
"""Build the Payment Fraud Protection Kit to PDF and DOCX with pandoc and WeasyPrint.

    python kits/payment-fraud/build/build.py                        # every document -> kits/payment-fraud/build/out/
    python kits/payment-fraud/build/build.py --only staff-poster    # one document (id or slug), repeatable
    python kits/payment-fraud/build/build.py --fill "Acme Inc" --set "Finance Lead=Dana Lee" --set "Threshold=$10,000"
    python kits/payment-fraud/build/build.py --docx-only            # skip PDF (no WeasyPrint needed)

PDF goes through pandoc's weasyprint engine (pip install weasyprint), so no LaTeX is needed.
The poster uses build/poster.css and is checked to fit one page by the tests. Output is git-ignored.
Nothing here changes the Markdown sources.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

KIT_DIR = Path(__file__).resolve().parents[1]
BUILD_DIR = KIT_DIR / "build"
OUT_DIR = BUILD_DIR / "out"
DOC_CSS = BUILD_DIR / "style.css"
POSTER_CSS = BUILD_DIR / "poster.css"
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
PLACEHOLDER = re.compile(r"\{\{([^}]+)\}\}")
ALLOWED_PLACEHOLDERS = {
    "{{Company}}",
    "{{Finance Lead}}",
    "{{CEO}}",
    "{{Security Lead}}",
    "{{Threshold}}",
    "{{Bank Fraud Line}}",
    "{{Effective Date}}",
    "{{Your Name}}",
    "{{Firm}}",
    "{{Firm Phone}}",
}
DEFAULTS = {"Threshold": "$10,000"}


@dataclass
class Doc:
    path: Path
    meta: dict
    body: str

    @property
    def id(self) -> str:
        return str(self.meta["id"])

    @property
    def slug(self) -> str:
        return str(self.meta["slug"])

    @property
    def title(self) -> str:
        return str(self.meta["title"])

    @property
    def kind(self) -> str:
        return str(self.meta.get("kind", "document"))

    @property
    def css(self) -> Path:
        return POSTER_CSS if self.kind == "poster" else DOC_CSS


def load_docs(folder: Path = KIT_DIR) -> list[Doc]:
    docs = []
    for path in sorted(folder.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        match = FRONT_MATTER.match(text)
        if not match:
            raise SystemExit(f"{path.name}: missing YAML front matter")
        docs.append(Doc(path, yaml.safe_load(match.group(1)) or {}, text[match.end():]))
    return docs


def fill(text: str, values: dict[str, str]) -> str:
    merged = {**DEFAULTS, **values} if values else {}
    if not merged:
        return text
    return PLACEHOLDER.sub(lambda m: merged.get(m.group(1).strip(), m.group(0)), text)


def pandoc(src: Path, dst: Path, *, pdf: bool, css: Path, title: str) -> None:
    cmd = ["pandoc", str(src), "-o", str(dst), "--from", "markdown", "--standalone", "--metadata", f"pagetitle={title}"]
    if pdf:
        cmd += ["--pdf-engine=weasyprint", "--css", str(css)]
    subprocess.run(cmd, check=True)


def to_html(doc: Doc, values: dict[str, str]) -> str:
    """Standalone HTML with the document's CSS inlined, for tests and previews."""
    body = fill(doc.body, values)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / doc.path.name
        src.write_text(body, encoding="utf-8")
        result = subprocess.run(
            ["pandoc", str(src), "--from", "markdown", "--to", "html5", "--standalone", "--metadata", f"pagetitle={doc.title}", "--css", str(doc.css), "--embed-resources"],
            check=True,
            capture_output=True,
            text=True,
        )
    return result.stdout


def parse_values(fill_company: str | None, sets: list[str]) -> dict[str, str]:
    values = {"Company": fill_company} if fill_company else {}
    for item in sets:
        if "=" not in item:
            raise SystemExit(f"--set expects NAME=VALUE, got {item!r}")
        name, value = item.split("=", 1)
        values[name.strip()] = value.strip()
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", action="append", default=[], help="document id (PFK-03) or slug (staff-poster); repeatable")
    parser.add_argument("--fill", metavar="COMPANY", help="value for {{Company}}")
    parser.add_argument("--set", action="append", default=[], metavar="NAME=VALUE", help="value for another placeholder, e.g. 'Finance Lead=Dana Lee'")
    parser.add_argument("--docx-only", action="store_true", help="skip the PDF")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)

    if shutil.which("pandoc") is None:
        print("pandoc is not installed. Get it from https://pandoc.org/installing.html (free).", file=sys.stderr)
        return 2
    values = parse_values(args.fill, args.set)
    docs = load_docs()
    if args.only:
        wanted = {w.lower() for w in args.only}
        docs = [d for d in docs if d.id.lower() in wanted or d.slug.lower() in wanted]
        if not docs:
            parser.error(f"no document matches {args.only}")

    args.out.mkdir(parents=True, exist_ok=True)
    formats = ["docx"] if args.docx_only else ["docx", "pdf"]
    built: list[Path] = []
    with tempfile.TemporaryDirectory() as tmp:
        for doc in docs:
            src = Path(tmp) / doc.path.name
            src.write_text(fill(doc.body, values), encoding="utf-8")
            for fmt in formats:
                dst = args.out / f"{doc.slug}.{fmt}"
                pandoc(src, dst, pdf=fmt == "pdf", css=doc.css, title=f"{values.get('Company', '')} {doc.title}".strip())
                built.append(dst)
    for path in built:
        try:
            print(path.relative_to(KIT_DIR.parents[1]))
        except ValueError:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
