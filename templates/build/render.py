#!/usr/bin/env python3
"""Render the templates: fill prices from config/pricing.yaml, optionally fill the other placeholders, and build DOCX/PDF with pandoc.

    python templates/build/render.py --check                     # every {{pricing.*}} token resolves; exit 1 otherwise
    python templates/build/render.py                             # Markdown with prices filled -> templates/build/out/*.md (+ .docx if pandoc is installed)
    python templates/build/render.py --only pilot-authorization-letter --set "Client=Acme Inc" --set "Tenant=Microsoft 365"
    python templates/build/render.py --pdf                       # also PDF through pandoc's weasyprint engine

Tokens that read pricing.yaml (so proposals never drift from the price list):
    {{pricing.products.<product>.<tier>.price}}   "$500 to $1,500", "$99" or "free"
    {{pricing.products.<product>.<tier>.name}}
    {{pricing.products.<product>.<tier>.includes}}  bullet list
    {{pricing.products.<product>.product_name}} / .tagline
    {{pricing.retainers.<retainer>.price}}        "$3,000 to $6,000 a month"
    {{pricing.retainers.<retainer>.hours}}        "10 to 20 hours a month"
    {{pricing.partners.reseller.tiers_table}}     Markdown table of the wholesale tiers
    {{pricing.partners.reseller.includes}}        bullet list
    {{pricing.partners.referral.fee}}             "10%"
    {{pricing.partners.referral.of}} / .paid / .who
    {{pricing.partners.principle}}
    {{pricing.terms.payment}} / .minimum_monthly_retainer / .discount_multi_product

Every other {{Placeholder}} is left for the person preparing the document unless passed with --set.
Nothing here changes the Markdown sources. Output is git-ignored.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

TEMPLATES_DIR = Path(__file__).resolve().parents[1]
REPO = TEMPLATES_DIR.parent
PRICING_FILE = REPO / "config" / "pricing.yaml"
OUT_DIR = TEMPLATES_DIR / "build" / "out"
CSS = TEMPLATES_DIR / "build" / "style.css"
COMPACT_CSS = TEMPLATES_DIR / "build" / "compact.css"
HEADER = "DRAFT. Not legal advice. Review by a Massachusetts attorney before use."
ATTORNEY_MARKER = "[Attorney review]"
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TOKEN = re.compile(r"\{\{\s*pricing\.([A-Za-z0-9_.]+)\s*\}\}")
PLACEHOLDER = re.compile(r"\{\{([^}]+)\}\}")
ALLOWED_PLACEHOLDERS = {
    "{{Client}}",
    "{{Client Address}}",
    "{{Client Contact}}",
    "{{Client Signatory}}",
    "{{Client Title}}",
    "{{alimi Entity}}",
    "{{alimi Signatory}}",
    "{{alimi Address}}",
    "{{Effective Date}}",
    "{{Start Date}}",
    "{{End Date}}",
    "{{Tenant}}",
    "{{Tenant Domain}}",
    "{{Reseller}}",
    "{{Partner}}",
    "{{Partner Firm}}",
    "{{Fee}}",
    "{{Quoted Price}}",
    "{{Contact Email}}",
    "{{Contact Phone}}",
    "{{Website}}",
}


@dataclass
class Template:
    path: Path
    meta: dict
    body: str

    @property
    def slug(self) -> str:
        return str(self.meta.get("slug", self.path.stem))

    @property
    def title(self) -> str:
        return str(self.meta.get("title", self.path.stem))

    @property
    def css(self) -> Path:
        return COMPACT_CSS if self.meta.get("kind") == "compact" else CSS


def load_pricing(path: Path = PRICING_FILE) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_templates(folder: Path = TEMPLATES_DIR) -> list[Template]:
    out = []
    for path in sorted(folder.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        match = FRONT_MATTER.match(text)
        if not match:
            raise SystemExit(f"{path.name}: missing YAML front matter")
        out.append(Template(path, yaml.safe_load(match.group(1)) or {}, text[match.end():]))
    return out


def money(value: float | int) -> str:
    return f"${value:,.0f}"


def money_range(pair: list) -> str:
    low, high = pair
    if high is None:
        return f"{money(low)} and up"
    return f"{money(low)} to {money(high)}"


def tier_price(tier: dict) -> str:
    """The list price when the price list publishes one (0 means free), otherwise the quoted range."""
    if "list" in tier:
        return "free" if tier["list"] == 0 else money(tier["list"])
    if "range" in tier:
        return money_range(tier["range"])
    raise KeyError("tier has neither range nor list")


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def percent(value: float) -> str:
    return f"{round(value * 100)}%"


def reseller_tiers_table(reseller: dict) -> str:
    rows = ["| Tier | Active client companies | Discount off list |", "| --- | --- | --- |"]
    for tier in reseller["tiers"]:
        low, high = tier["active_clients"]
        clients = f"{low} to {high}" if high is not None else f"{low} or more"
        rows.append(f"| {tier['id'].title()} | {clients} | {percent(tier['discount'])} |")
    return "\n".join(rows)


def resolve(path: str, pricing: dict) -> str:
    parts = path.split(".")
    try:
        if parts[0] == "products" and len(parts) == 3:
            _, product, field = parts
            product_data = pricing["products"][product]
            if field == "product_name":
                return str(product_data["name"])
            if field == "tagline":
                return str(product_data["tagline"])
        if parts[0] == "products":
            _, product, tier_id, field = parts
            product_data = pricing["products"][product]
            tier = next(t for t in product_data["tiers"] if t["id"] == tier_id)
            if field == "price":
                return tier_price(tier)
            if field == "name":
                return str(tier["name"])
            if field == "includes":
                return bullets(tier["includes"])
            if field == "product_name":
                return str(product_data["name"])
        if parts[0] == "retainers":
            _, retainer, field = parts
            data = pricing["retainers"][retainer]
            if field == "price":
                return money_range(data["range_per_month"]) + " a month"
            if field == "hours":
                low, high = data["hours_per_month"]
                return f"{low} to {high} hours a month"
            if field == "name":
                return str(data["name"])
        if parts[0] == "partners":
            if parts[1] == "principle" and len(parts) == 2:
                return str(pricing["partners"]["principle"])
            if parts[1] == "reseller":
                reseller = pricing["partners"]["reseller"]
                field = parts[2]
                if field == "tiers_table":
                    return reseller_tiers_table(reseller)
                if field == "includes":
                    return bullets(reseller["includes"])
                if field in ("who", "buys_at", "billing", "review"):
                    return str(reseller[field])
                if field == "discount" and len(parts) == 4:
                    tier = next(t for t in reseller["tiers"] if t["id"] == parts[3])
                    return percent(tier["discount"])
            if parts[1] == "referral":
                referral = pricing["partners"]["referral"]
                field = parts[2]
                if field == "fee":
                    return percent(referral["fee"])
                if field in ("who", "of", "paid"):
                    return str(referral[field])
        if parts[0] == "terms":
            value = pricing["terms"][parts[1]]
            if parts[1] == "minimum_monthly_retainer":
                return money(value) + " a month"
            if parts[1] == "discount_multi_product":
                return percent(value)
            return str(value)
    except (KeyError, StopIteration, ValueError):
        pass
    raise KeyError(path)


def fill_pricing(text: str, pricing: dict) -> tuple[str, list[str]]:
    missing: list[str] = []

    def sub(match: re.Match) -> str:
        try:
            return resolve(match.group(1), pricing)
        except KeyError:
            missing.append(match.group(1))
            return match.group(0)

    return TOKEN.sub(sub, text), missing


def fill_placeholders(text: str, values: dict[str, str]) -> str:
    if not values:
        return text
    return PLACEHOLDER.sub(lambda m: values.get(m.group(1).strip(), m.group(0)), text)


def render(template: Template, pricing: dict, values: dict[str, str] | None = None) -> str:
    text, missing = fill_pricing(template.body, pricing)
    if missing:
        raise SystemExit(f"{template.path.name}: unknown pricing tokens: {', '.join(missing)}")
    return fill_placeholders(text, values or {})


def to_html(template: Template, pricing: dict, values: dict[str, str] | None = None) -> str:
    """Standalone HTML with the print CSS, for tests and previews (needs pandoc)."""
    import tempfile

    text = render(template, pricing, values)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / template.path.name
        src.write_text(text, encoding="utf-8")
        result = subprocess.run(
            ["pandoc", str(src), "--from", "markdown", "--to", "html5", "--standalone", "--metadata", f"pagetitle={template.title}", "--css", str(template.css), "--embed-resources"],
            check=True,
            capture_output=True,
            text=True,
        )
    return result.stdout


def pandoc(src: Path, dst: Path, *, pdf: bool, title: str, css: Path = CSS) -> None:
    cmd = ["pandoc", str(src), "-o", str(dst), "--from", "markdown", "--standalone", "--metadata", f"pagetitle={title}"]
    if pdf:
        cmd += ["--pdf-engine=weasyprint", "--css", str(css)]
    subprocess.run(cmd, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="only verify that every pricing token resolves")
    parser.add_argument("--only", action="append", default=[], help="template slug; repeatable")
    parser.add_argument("--set", action="append", default=[], metavar="NAME=VALUE", help="fill another placeholder, e.g. 'Client=Acme Inc'")
    parser.add_argument("--pdf", action="store_true", help="also build PDF (needs weasyprint)")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)

    pricing = load_pricing()
    templates = load_templates()
    if args.only:
        wanted = {w.lower() for w in args.only}
        templates = [t for t in templates if t.slug.lower() in wanted]
        if not templates:
            parser.error(f"no template matches {args.only}")

    if args.check:
        bad = 0
        for template in templates:
            _, missing = fill_pricing(template.body, pricing)
            if missing:
                bad += 1
                print(f"{template.path.name}: unknown pricing tokens: {', '.join(missing)}", file=sys.stderr)
        print(f"{len(templates)} templates checked, {bad} with unresolved pricing tokens")
        return 1 if bad else 0

    values: dict[str, str] = {}
    for item in args.set:
        if "=" not in item:
            parser.error(f"--set expects NAME=VALUE, got {item!r}")
        name, value = item.split("=", 1)
        values[name.strip()] = value.strip()

    args.out.mkdir(parents=True, exist_ok=True)
    have_pandoc = shutil.which("pandoc") is not None
    for template in templates:
        text = render(template, pricing, values)
        md = args.out / f"{template.slug}.md"
        md.write_text(text, encoding="utf-8")
        print(md)
        if have_pandoc:
            docx = args.out / f"{template.slug}.docx"
            pandoc(md, docx, pdf=False, title=template.title)
            print(docx)
            if args.pdf:
                pdf = args.out / f"{template.slug}.pdf"
                pandoc(md, pdf, pdf=True, title=template.title, css=template.css)
                print(pdf)
    if not have_pandoc:
        print("pandoc not installed; wrote Markdown only (https://pandoc.org/installing.html)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
