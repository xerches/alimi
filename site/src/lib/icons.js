// Menu icons for the header strip: one small line drawing per top-level menu, as inner SVG markup
// for a 20x20 viewBox. Drawn here, not taken from an icon set, so there is nothing to license.
// Stroke and fill come from CSS (currentColor), never from a typed color.
export const ICONS = {
  platform: '<rect x="3" y="3" width="6" height="6" rx="1.5"/><rect x="11" y="3" width="6" height="6" rx="1.5"/><rect x="3" y="11" width="6" height="6" rx="1.5"/><rect x="11" y="11" width="6" height="6" rx="1.5"/>',
  solutions: '<circle cx="10" cy="10" r="7"/><circle cx="10" cy="10" r="2.5"/><path d="M10 3v2M10 15v2M3 10h2M15 10h2"/>',
  frameworks: '<path d="M10 3l7 3.5-7 3.5-7-3.5z"/><path d="M3 10l7 3.5 7-3.5"/><path d="M3 13.5L10 17l7-3.5"/>',
  pricing: '<path d="M3 3h7l7 7-7 7-7-7z"/><circle cx="6.5" cy="6.5" r="1.2"/>',
  compare: '<rect x="3" y="4" width="5.5" height="12" rx="1.5"/><rect x="11.5" y="4" width="5.5" height="12" rx="1.5"/><path d="M4.5 8h2.5M13 8h2.5M4.5 11h2.5M13 11h2.5"/>',
  partners: '<circle cx="7" cy="7" r="2.6"/><circle cx="13.5" cy="8" r="2.1"/><path d="M2.5 16.5c0-2.8 2-4.6 4.5-4.6s4.5 1.8 4.5 4.6"/><path d="M12.5 12.3c2.6 0 4.5 1.6 4.5 4.2"/>',
  resources: '<path d="M4 3.5h5.5a1.5 1.5 0 011.5 1.5v11.5H5.5A1.5 1.5 0 014 15z"/><path d="M11 5a1.5 1.5 0 011.5-1.5H16V15h-5"/><path d="M6.5 7h2.5M6.5 10h2.5"/>',
  contact: '<rect x="2.5" y="4.5" width="15" height="11" rx="2"/><path d="M3 5.5l7 5.5 7-5.5"/>',
};

/** The icon markup for a menu, or an empty string when the menu has none. */
export function icon(key) {
  return ICONS[key] ?? "";
}
