"""One Markdown renderer for everything a company types: policy text, the trust page statement,
answers, update notes. Raw HTML is off, so nothing typed can put script on a page; links are not
auto-detected, so an address is a link only when written as one."""

from __future__ import annotations

from markdown_it import MarkdownIt

MD = MarkdownIt("js-default", {"html": False, "linkify": False})


def to_html(text_: str | None) -> str:
    return MD.render(text_ or "")
