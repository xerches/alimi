// Theme choice (Nov 3, 2026): light by default, dark when the device asks for it, and a toggle in the
// top bar for the visitor who wants the other one. The layout inlines this file in <head>, so it runs
// before the page paints (a saved choice never flashes the other theme) and costs no request; the
// Content Security Policy in netlify.toml allows it by the hash of this exact text, which
// scripts/check-dist.mjs and tests/theme.test.mjs recompute, so a change here means a new hash there.
// The choice is kept in this browser's localStorage under "alimi-theme" only when it differs from the
// device setting; nothing else is stored, nothing is sent. When storage is unavailable (private mode,
// a policy) the choice lasts for the page. The theme-color metas follow the active theme, so the
// browser's own bar matches the page.
(function () {
  var KEY = "alimi-theme";
  var root = document.documentElement;
  var media = window.matchMedia("(prefers-color-scheme: dark)");
  var memory = null;
  var metas = document.querySelectorAll('meta[name="theme-color"][data-theme]');
  var bar = {};
  for (var m = 0; m < metas.length; m++) bar[metas[m].getAttribute("data-theme")] = metas[m].getAttribute("content");

  function valid(v) {
    return v === "dark" || v === "light" ? v : null;
  }
  function stored() {
    try {
      return valid(localStorage.getItem(KEY)) || memory;
    } catch (e) {
      return memory;
    }
  }
  function device() {
    return media.matches ? "dark" : "light";
  }
  function apply() {
    var choice = stored();
    var active = choice || device();
    if (choice) root.setAttribute("data-theme", choice);
    else root.removeAttribute("data-theme");
    root.setAttribute("data-theme-active", active);
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) buttons[i].setAttribute("aria-pressed", active === "dark" ? "true" : "false");
    if (bar[active]) for (var j = 0; j < metas.length; j++) metas[j].setAttribute("content", bar[active]);
  }
  function choose(next) {
    memory = next === device() ? null : next;
    try {
      if (next === device()) localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, next);
    } catch (e) {
      /* private mode or storage off: memory carries the choice for this page */
    }
    apply();
  }

  apply();
  document.addEventListener("DOMContentLoaded", function () {
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function () {
        choose(root.getAttribute("data-theme-active") === "dark" ? "light" : "dark");
      });
    }
    apply();
  });
  if (media.addEventListener) media.addEventListener("change", apply);
})();
