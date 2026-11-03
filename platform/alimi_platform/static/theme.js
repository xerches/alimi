// Theme choice (Nov 3, 2026), the same script the marketing site runs: light by default, dark when the
// device asks for it, and a toggle in the top bar for the person who wants the other one. base.html
// loads this file in <head> without defer, so it runs before the page paints and a saved choice never
// flashes the other theme. The choice is kept in this browser's localStorage under "alimi-theme" only
// when it differs from the device setting; nothing else is stored, nothing is sent to the server.
(function () {
  var KEY = "alimi-theme";
  var root = document.documentElement;
  var media = window.matchMedia("(prefers-color-scheme: dark)");

  function stored() {
    try {
      var v = localStorage.getItem(KEY);
      return v === "dark" || v === "light" ? v : null;
    } catch (e) {
      return null;
    }
  }
  function device() {
    return media.matches ? "dark" : "light";
  }
  function effective() {
    return stored() || device();
  }
  function apply() {
    var choice = stored();
    if (choice) root.setAttribute("data-theme", choice);
    else root.removeAttribute("data-theme");
    root.setAttribute("data-theme-active", effective());
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) buttons[i].setAttribute("aria-pressed", effective() === "dark" ? "true" : "false");
  }
  function choose(next) {
    try {
      if (next === device()) localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, next);
    } catch (e) {
      /* private mode or storage off: the choice lasts for this page only */
      root.setAttribute("data-theme", next);
    }
    apply();
    if (!stored() && next !== device()) root.setAttribute("data-theme", next);
  }

  apply();
  document.addEventListener("DOMContentLoaded", function () {
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function () {
        choose(effective() === "dark" ? "light" : "dark");
      });
    }
    apply();
  });
  if (media.addEventListener) media.addEventListener("change", apply);
})();
