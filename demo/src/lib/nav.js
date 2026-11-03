// The demo's navigation model, chosen Nov 3, 2026 after the layout review: a captioned icon strip on
// the left, a second column only where a section has children, breadcrumbs and the company switcher
// in the top bar. The platform's templates mirror this file so the two never drift. A page passes the
// layout a `section` key (and, in a section with a column, the `item` that is active there); this
// file resolves it to a strip section and a column item.

export const ICONS = {
  home: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M3 9.5L10 3l7 6.5V17H12v-5H8v5H3z"/></svg>',
  frameworks: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M10 3l7 3.5-7 3.5-7-3.5z"/><path d="M3 10l7 3.5 7-3.5"/><path d="M3 13.5L10 17l7-3.5"/></svg>',
  controls: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="14" height="14" rx="2"/><path d="M6.5 10l2.5 2.5 4.5-5"/></svg>',
  policies: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M5 2.5h7l3 3V17.5H5z"/><path d="M12 2.5v3h3"/><path d="M7.5 9h5M7.5 12h5"/></svg>',
  evidence: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 9.5l-5.3 5.3a3 3 0 01-4.2-4.2l6-6a2 2 0 012.8 2.8l-6 6a1 1 0 01-1.4-1.4L11 7"/></svg>',
  monitoring: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 10h3l2-5 3 10 2-5h5"/></svg>',
  people: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="8" cy="7" r="3"/><path d="M2.5 17c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><circle cx="14.5" cy="8" r="2"/><path d="M15 12.5c1.8.4 3 1.8 3 4"/></svg>',
  risk: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 3l7.5 13h-15z"/><path d="M10 8v4M10 14h.01"/></svg>',
  assets: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="14" height="9" rx="1.5"/><path d="M1.5 16h17"/></svg>',
  trust: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M10 2.5l6.5 2.5v5c0 3.5-2.8 6-6.5 7.5C6.3 16 3.5 13.5 3.5 10V5z"/><path d="M7.3 10l1.9 1.9 3.6-3.8"/></svg>',
  assistant: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M9 3l1.5 4 4 1.5-4 1.5L9 14l-1.5-4-4-1.5 4-1.5z"/><path d="M15.5 13l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/></svg>',
  settings: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><circle cx="10" cy="10" r="2.5"/><path d="M10 2.5v2M10 15.5v2M2.5 10h2M15.5 10h2M4.7 4.7l1.4 1.4M13.9 13.9l1.4 1.4M4.7 15.3l1.4-1.4M13.9 6.1l1.4-1.4"/></svg>',
  menu: '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14"/></svg>',
};

// The strip, top to bottom. `column: true` means the section has children and shows the second column.
export const SECTIONS = [
  { key: "home", label: "Home", href: "/", icon: "home" },
  { key: "frameworks", label: "Frameworks", href: "/frameworks", icon: "frameworks", column: true },
  { key: "controls", label: "Controls", href: "/controls", icon: "controls", column: true },
  { key: "policies", label: "Policies", href: "/policies", icon: "policies" },
  { key: "evidence", label: "Evidence", href: "/evidence", icon: "evidence" },
  { key: "monitoring", label: "Monitoring", href: "/monitoring", icon: "monitoring" },
  { key: "people", label: "People", href: "/people", icon: "people", column: true },
  { key: "risk", label: "Risk", href: "/risks", icon: "risk", column: true },
  { key: "assets", label: "Assets", href: "/assets", icon: "assets" },
  { key: "trust", label: "Trust", href: "/trust", icon: "trust", column: true },
  { key: "assistant", label: "Assistant", href: "/assistant", icon: "assistant", preview: true },
  { key: "settings", label: "Settings", href: "/settings", icon: "settings", column: true },
];

// The four sections a phone shows in the bottom bar; the fifth slot opens the full menu.
export const BOTTOM_BAR = ["home", "frameworks", "controls", "people"];

// Page section key -> [strip section, column item]. The frameworks and controls columns are built from
// data (one item per framework on the account, one per control domain); the rest are listed here.
export const PAGE_SECTIONS = {
  home: ["home"],
  overview: ["home"],
  frameworks: ["frameworks"],
  controls: ["controls"],
  policies: ["policies"],
  evidence: ["evidence"],
  monitoring: ["monitoring"],
  people: ["people", "people"],
  training: ["people", "training"],
  owners: ["people", "owners"],
  risks: ["risk", "risks"],
  vendors: ["risk", "vendors"],
  ai: ["risk", "ai"],
  assets: ["assets"],
  trust: ["trust", "trust"],
  questionnaires: ["trust", "questionnaires"],
  assistant: ["assistant"],
  settings: ["settings", "settings"],
  integrations: ["settings", "integrations"],
  audit: ["settings", "audit"],
};

export const STATIC_COLUMNS = {
  people: {
    title: "People",
    items: [
      { key: "people", label: "Directory", href: "/people" },
      { key: "training", label: "Training", href: "/training" },
      { key: "owners", label: "Owners", href: "/owners" },
    ],
  },
  risk: {
    title: "Risk",
    items: [
      { key: "risks", label: "Risk register", href: "/risks" },
      { key: "vendors", label: "Vendors", href: "/vendors" },
      { key: "ai", label: "AI governance", href: "/ai" },
    ],
  },
  trust: {
    title: "Trust",
    items: [
      { key: "trust", label: "Trust page", href: "/trust" },
      { key: "questionnaires", label: "Questionnaires", href: "/questionnaires" },
    ],
  },
  settings: {
    title: "Settings",
    items: [
      { key: "settings", label: "Company", href: "/settings" },
      { key: "integrations", label: "Integrations", href: "/integrations" },
      { key: "audit", label: "Audit log", href: "/audit" },
    ],
  },
};

export function resolveSection(pageSection, item) {
  const [sectionKey, defaultItem = null] = PAGE_SECTIONS[pageSection] ?? ["home"];
  const section = SECTIONS.find((s) => s.key === sectionKey);
  return { section, item: item ?? defaultItem };
}
