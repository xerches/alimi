"""The app shell's navigation model, chosen Nov 3, 2026 after the layout review.

A captioned icon strip on the left, a second column only where a section has children, breadcrumbs
and the company switcher in the top bar, and on a phone a bottom bar with the four most used
sections plus a menu. This file mirrors demo/src/lib/nav.js so the demo and the platform never
drift; the strip lists only the sections the platform has built so far, in the demo's order, and
the rest (policies, evidence, people, risk, assets, trust, the assistant) join it with their prompts.

Everything a badge or a column shows is computed from this organization's rows inside org_scope;
nothing is typed in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, text

from .catalog import domain_labels
from .status import ControlStatus, control_statuses, latest_results

# The same paths as demo/src/lib/nav.js ICONS, so the two products look alike.
ICONS: dict[str, str] = {
    "home": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M3 9.5L10 3l7 6.5V17H12v-5H8v5H3z"/></svg>',
    "frameworks": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M10 3l7 3.5-7 3.5-7-3.5z"/><path d="M3 10l7 3.5 7-3.5"/><path d="M3 13.5L10 17l7-3.5"/></svg>',
    "controls": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="14" height="14" rx="2"/><path d="M6.5 10l2.5 2.5 4.5-5"/></svg>',
    "monitoring": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 10h3l2-5 3 10 2-5h5"/></svg>',
    "settings": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><circle cx="10" cy="10" r="2.5"/><path d="M10 2.5v2M10 15.5v2M2.5 10h2M15.5 10h2M4.7 4.7l1.4 1.4M13.9 13.9l1.4 1.4M4.7 15.3l1.4-1.4M13.9 6.1l1.4-1.4"/></svg>',
    "menu": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14"/></svg>',
}


@dataclass(frozen=True)
class Section:
    key: str
    label: str
    href: str
    icon: str
    column: bool = False  # the section has children, so the second column shows


# The strip, top to bottom, in the demo's order.
SECTIONS: tuple[Section, ...] = (
    Section("home", "Home", "/dashboard", "home"),
    Section("frameworks", "Frameworks", "/frameworks", "frameworks", column=True),
    Section("controls", "Controls", "/controls", "controls", column=True),
    Section("monitoring", "Monitoring", "/monitoring", "monitoring"),
    Section("settings", "Settings", "/settings", "settings", column=True),
)

# The four sections a phone shows in the bottom bar; the fifth slot opens the full menu.
BOTTOM_BAR: tuple[str, ...] = ("home", "frameworks", "controls", "monitoring")

# Page key -> (strip section, column item). A page in the controls section passes the domain as its
# item; the frameworks column items are framework ids.
PAGE_SECTIONS: dict[str, tuple[str, str | None]] = {
    "dashboard": ("home", None),
    "frameworks": ("frameworks", None),
    "insurer": ("frameworks", "insurer"),
    "controls": ("controls", None),
    "control": ("controls", None),
    "monitoring": ("monitoring", None),
    "scan": ("monitoring", None),
    "settings": ("settings", "settings"),
    "audit": ("settings", "audit"),
}

STATIC_COLUMNS: dict[str, dict[str, Any]] = {
    "settings": {
        "title": "Settings",
        "groups": [
            {
                "label": None,
                "items": [
                    {"key": "settings", "label": "Company", "href": "/settings", "sub": "Your company, your role, what is connected"},
                    {"key": "audit", "label": "Audit log", "href": "/audit", "sub": "Who changed what, when"},
                ],
            }
        ],
        "add": None,
    },
}


def framework_readiness(conn: Connection, controls: list[ControlStatus]) -> dict[str, dict[str, Any]]:
    """Per framework, the controls linked through its requirements and how many are Ok.

    The same rule as the demo: readiness is the share of mapped controls that are Ok, counted over
    controls, not requirement IDs.
    """
    by_id = {c.id: c for c in controls}
    linked: dict[str, set[str]] = {}
    for framework_id, control_id in conn.execute(
        text("SELECT r.framework_id, cr.control_id FROM control_requirements cr JOIN requirements r ON r.id = cr.requirement_id")
    ):
        linked.setdefault(framework_id, set()).add(control_id)
    out: dict[str, dict[str, Any]] = {}
    for framework_id, ids in linked.items():
        total = len(ids)
        ok = sum(1 for i in ids if i in by_id and by_id[i].status == "ok")
        out[framework_id] = {"ok": ok, "total": total, "percent": round(100 * ok / total) if total else None}
    return out


def readiness_tone(percent: int) -> str:
    return "success" if percent >= 90 else "warning" if percent >= 70 else "danger"


def _frameworks_column(conn: Connection, controls: list[ControlStatus]) -> dict[str, Any]:
    frameworks = conn.execute(text("SELECT id, short_name, mapped, always_included FROM frameworks ORDER BY position")).mappings().all()
    ready = framework_readiness(conn, controls)
    posture = [{"key": "posture", "label": "Posture score", "href": "/frameworks#alimi_posture", "sub": "Alimi's recommendations; scored in a later build step"}]
    on_account: list[dict[str, Any]] = []
    mapped_later: list[dict[str, Any]] = []
    rest = 0
    for f in frameworks:
        if f["always_included"]:
            continue
        r = ready.get(f["id"])
        if f["id"] == "insurer":
            item: dict[str, Any] = {"key": "insurer", "label": f["short_name"], "href": "/frameworks/insurer"}
            if r and r["percent"] is not None:
                item.update(percent=r["percent"], tone=readiness_tone(r["percent"]), sub=f"{r['ok']} of {r['total']} controls Ok")
            else:
                item["sub"] = "No controls mapped yet"
            on_account.append(item)
        elif f["mapped"]:
            mapped_later.append(
                {
                    "key": f["id"],
                    "label": f["short_name"],
                    "href": f"/frameworks#{f['id']}",
                    "sub": f"{r['total']} controls mapped, scored in a later step" if r else "Requirement IDs loaded",
                }
            )
        else:
            rest += 1
    groups: list[dict[str, Any]] = [{"label": None, "items": posture}, {"label": "On this account", "items": on_account}]
    if mapped_later:
        groups.append({"label": "Mapped, scored later", "items": mapped_later})
    return {"title": "Frameworks", "groups": groups, "add": {"label": "+ Add a framework", "href": "/frameworks", "sub": f"{rest} more"}}


def _controls_column(controls: list[ControlStatus], labels: dict[str, str]) -> dict[str, Any]:
    ok = sum(1 for c in controls if c.status == "ok")
    not_ok = len(controls) - ok
    everything = {"key": "all", "label": "All controls", "href": "/controls", "count": len(controls), "sub": f"{ok} Ok, {not_ok} need something"}
    areas: list[dict[str, Any]] = []
    for domain, label in labels.items():
        own = [c for c in controls if c.domain == domain]
        if not own:
            continue
        needs = sum(1 for c in own if c.status != "ok")
        areas.append(
            {
                "key": domain,
                "label": label,
                "href": f"/controls?domain={domain}",
                "count": len(own),
                "sub": f"{needs} need{'s' if needs == 1 else ''} something" if needs else "All Ok",
            }
        )
    return {"title": "Controls", "groups": [{"label": None, "items": [everything]}, {"label": "By area", "items": areas}], "add": None}


def shell(conn: Connection, settings, page: str, item: str | None = None, controls: list[ControlStatus] | None = None) -> dict[str, Any]:
    """Everything base.html needs for one page: the strip with its badges, the column, the current item."""
    section_key, default_item = PAGE_SECTIONS[page]
    item = item or default_item
    controls = control_statuses(conn) if controls is None else controls
    not_ok = sum(1 for c in controls if c.status != "ok")
    failing = sum(1 for r in latest_results(conn).values() if r["status"] == "fail")
    badges = {
        "controls": {"n": not_ok, "tone": "neutral", "what": "controls that need something"},
        "monitoring": {"n": failing, "tone": "danger", "what": "failing tests"},
    }
    sections = [
        {
            "key": s.key,
            "label": s.label,
            "href": s.href,
            "icon": ICONS[s.icon],
            "current": s.key == section_key,
            "badge": badges[s.key] if s.key in badges and badges[s.key]["n"] else None,
        }
        for s in SECTIONS
    ]
    column = None
    if section_key == "frameworks":
        column = _frameworks_column(conn, controls)
    elif section_key == "controls":
        column = _controls_column(controls, domain_labels(settings.repo_root))
        item = item or "all"
    elif section_key == "settings":
        column = STATIC_COLUMNS["settings"]
    return {
        "section": section_key,
        "item": item,
        "sections": sections,
        "bottom": [s for s in sections if s["key"] in BOTTOM_BAR],
        "in_bottom": section_key in BOTTOM_BAR,
        "menu_icon": ICONS["menu"],
        "column": column,
    }
