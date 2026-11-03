// Progressive enhancement for tables: a text filter and chip filters. Every row is visible without
// this script; it only hides rows. Served from the site's own origin, so it fits the CSP.
// Also: a query string such as ?domain=access applies the matching row filter on load (the second
// column links to the controls page that way), and the column link for the current URL is marked.
function rowsOf(selector) {
  const table = document.querySelector(selector);
  return table ? [...table.querySelectorAll("tbody tr")] : [];
}

const state = new Map(); // table selector -> { text, chips: { key: value } }

function apply(selector) {
  const s = state.get(selector) ?? { text: "", chips: {} };
  for (const row of rowsOf(selector)) {
    let show = true;
    if (s.text && !row.textContent.toLowerCase().includes(s.text)) show = false;
    for (const [key, value] of Object.entries(s.chips)) {
      if (value === "all") continue;
      const own = (row.dataset[key] ?? "").split(" ");
      if (!own.includes(value)) show = false;
    }
    row.classList.toggle("hidden-by-filter", !show);
  }
  const count = document.querySelector(`[data-count-for="${selector}"]`);
  if (count) {
    const visible = rowsOf(selector).filter((r) => !r.classList.contains("hidden-by-filter")).length;
    count.textContent = `${visible} shown`;
  }
}

for (const input of document.querySelectorAll("input[data-filter]")) {
  const selector = input.dataset.filter;
  input.addEventListener("input", () => {
    const s = state.get(selector) ?? { text: "", chips: {} };
    s.text = input.value.trim().toLowerCase();
    state.set(selector, s);
    apply(selector);
  });
}

for (const group of document.querySelectorAll("[data-chips]")) {
  const selector = group.dataset.chips;
  const key = group.dataset.key;
  const buttons = [...group.querySelectorAll("button[data-value]")];
  for (const button of buttons) {
    button.addEventListener("click", () => {
      for (const b of buttons) b.setAttribute("aria-pressed", String(b === button));
      const s = state.get(selector) ?? { text: "", chips: {} };
      s.chips[key] = button.dataset.value;
      state.set(selector, s);
      apply(selector);
    });
  }
}

// ?key=value filters the first filterable table whose rows carry data-<key>.
const params = new URLSearchParams(location.search);
for (const [key, value] of params) {
  const table = [...document.querySelectorAll("table[id]")].find((t) => t.querySelector(`tbody tr[data-${key}]`));
  if (!table) continue;
  const selector = `#${table.id}`;
  const s = state.get(selector) ?? { text: "", chips: {} };
  s.chips[key] = value;
  state.set(selector, s);
  apply(selector);
  const chip = document.querySelector(`[data-chips="${selector}"][data-key="${key}"] button[data-value="${value}"]`);
  if (chip) chip.click();
}

// The column link that matches this exact URL (path and query) is the current one.
const here = location.pathname.replace(/\.html$/, "") + location.search;
for (const link of document.querySelectorAll("[data-column-link]")) {
  const target = link.getAttribute("href");
  if (target === here) {
    for (const other of document.querySelectorAll(".column a[aria-current]")) other.removeAttribute("aria-current");
    link.setAttribute("aria-current", "page");
  }
}
