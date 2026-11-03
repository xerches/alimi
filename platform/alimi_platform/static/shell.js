// The account menu in the top bar is a <details> element, so it opens and closes without this file.
// This adds the two things a menu is expected to do that HTML alone does not: close when the person
// clicks elsewhere, and close on Escape with focus back on the button.
(function () {
  function closeAll(except) {
    var open = document.querySelectorAll("details.menu[open]");
    for (var i = 0; i < open.length; i++) if (open[i] !== except) open[i].removeAttribute("open");
  }
  document.addEventListener("click", function (event) {
    var inside = event.target.closest ? event.target.closest("details.menu") : null;
    closeAll(inside);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    var open = document.querySelector("details.menu[open]");
    if (!open) return;
    open.removeAttribute("open");
    var summary = open.querySelector("summary");
    if (summary) summary.focus();
  });
})();
