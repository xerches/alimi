#!/usr/bin/env python3
"""Build the policies to DOCX and PDF with pandoc.

    python policies/build/build.py                       # every policy -> policies/build/out/<slug>.docx and .pdf
    python policies/build/build.py --only POL-13         # one policy
    python policies/build/build.py --fill "Acme Inc" --set "Security Lead=Dana Lee" --set "CEO=Sam Ortiz"
    python policies/build/build.py --fill "Acme Inc" --final   # strips the TEMPLATE header; refuses if placeholders or review markers remain
    python policies/build/build.py --pack                # one combined policy-pack.docx and .pdf
    python policies/build/build.py --docx-only            # skip PDF (no WeasyPrint)

PDF goes through pandoc's weasyprint engine (pip install weasyprint), so no LaTeX is needed.
Output is git-ignored. Nothing here changes the Markdown sources.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage import HEADER, load_policies  # noqa: E402

POLICIES_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = POLICIES_DIR / "build" / "out"
CSS = POLICIES_DIR / "build" / "style.css"
PLACEHOLDER = re.compile(r"\{\{([^}]+)\}\}")
REVIEW_MARKER = "[HR or legal review]"
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
HEADER_LINE = re.compile(r"^> \*\*TEMPLATE\. Adapt before adopting\..*\*\*\n\n?", re.MULTILINE)


def fill(text: str, values: dict[str, str]) -> str:
    return PLACEHOLDER.sub(lambda m: values.get(m.group(1).strip(), m.group(0)), text)


def prepare(markdown: str, *, values: dict[str, str], final: bool, name: str) -> str:
    text = FRONT_MATTER.sub("", fill(markdown, values), count=1)  # pandoc would render the front matter as a title block
    if final:
        left = sorted(set(PLACEHOLDER.findall(text)))
        if left:
            raise SystemExit(f"{name}: --final refused, placeholders still unfilled: {', '.join(left)} (use --set 'Name=Value')")
        if REVIEW_MARKER in text:
            raise SystemExit(f"{name}: --final refused, '{REVIEW_MARKER}' markers remain; have a human review those sections and remove the markers")
        text = HEADER_LINE.sub("", text, count=1)
    return text


def pandoc(src: Path, dst: Path, *, pdf: bool, title: str) -> None:
    cmd = ["pandoc", str(src), "-o", str(dst), "--from", "markdown", "--standalone", "--metadata", f"pagetitle={title}"]
    if pdf:
        cmd += ["--pdf-engine=weasyprint", "--css", str(CSS)]
    subprocess.run(cmd, check=True)


def page_break(for_pdf: bool) -> str:
    if for_pdf:
        return '\n\n<div style="page-break-before: always"></div>\n\n'
    return '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", action="append", default=[], help="policy id (POL-01) or slug; repeatable")
    parser.add_argument("--fill", metavar="COMPANY", help="value for {{Company}}")
    parser.add_argument("--set", action="append", default=[], metavar="NAME=VALUE", help="value for another placeholder, e.g. 'Security Lead=Dana Lee'")
    parser.add_argument("--final", action="store_true", help="strip the TEMPLATE header; refuse if any placeholder or review marker remains")
    parser.add_argument("--pack", action="store_true", help="also build one combined policy pack")
    parser.add_argument("--docx-only", action="store_true", help="skip the PDF")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)

    if shutil.which("pandoc") is None:
        print("pandoc is not installed. Get it from https://pandoc.org/installing.html (free).", file=sys.stderr)
        return 2
    values = {"Company": args.fill} if args.fill else {}
    for item in args.set:
        if "=" not in item:
            parser.error(f"--set expects NAME=VALUE, got {item!r}")
        name, value = item.split("=", 1)
        values[name.strip()] = value.strip()
    if args.final and not args.fill:
        parser.error("--final needs --fill COMPANY")

    policies = load_policies()
    if args.only:
        wanted = {w.lower() for w in args.only}
        policies = [p for p in policies if p.id.lower() in wanted or str(p.meta.get("slug", "")).lower() in wanted]
        if not policies:
            parser.error(f"no policy matches {args.only}")

    args.out.mkdir(parents=True, exist_ok=True)
    formats = ["docx"] if args.docx_only else ["docx", "pdf"]
    built: list[Path] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for policy in policies:
            text = prepare(policy.path.read_text(encoding="utf-8"), values=values, final=args.final, name=policy.path.name)
            src = tmp_dir / policy.path.name
            src.write_text(text, encoding="utf-8")
            for fmt in formats:
                dst = args.out / f"{policy.meta.get('slug', policy.path.stem)}.{fmt}"
                pandoc(src, dst, pdf=fmt == "pdf", title=f"{values.get('Company', '')} {policy.title}".strip())
                built.append(dst)
        if args.pack:
            for fmt in formats:
                parts = []
                company = values.get("Company", "{{Company}}")
                parts.append(f"---\ntitle: \"{company} Policy Pack\"\n---\n\n" + ("" if args.final else f"> **{HEADER}**\n\n"))
                parts.append("This pack contains the following policies:\n\n" + "\n".join(f"- {p.id} {p.title}" for p in policies) + "\n")
                for policy in policies:
                    body = prepare(policy.path.read_text(encoding="utf-8"), values=values, final=args.final, name=policy.path.name)
                    parts.append(page_break(for_pdf=fmt == "pdf") + body)
                src = tmp_dir / f"policy-pack.{fmt}.md"
                src.write_text("".join(parts), encoding="utf-8")
                dst = args.out / f"policy-pack.{fmt}"
                pandoc(src, dst, pdf=fmt == "pdf", title=f"{company} Policy Pack")
                built.append(dst)
    for path in built:
        print(_display(path))
    return 0


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(POLICIES_DIR.parent))
    except ValueError:  # --out pointed outside the repo
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
