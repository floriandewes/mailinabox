(() => {
  const toggle = document.querySelector("[data-nav-toggle]");
  const menu = document.getElementById("nav-menu");

  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      menu.classList.toggle("is-open", !open);
    });

    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        toggle.setAttribute("aria-expanded", "false");
        menu.classList.remove("is-open");
      });
    });
  }

  const root = document.querySelector("[data-install-switch]");
  if (!root) return;

  const tabs = [...root.querySelectorAll('[role="tab"]')];
  const panels = [...root.querySelectorAll('[role="tabpanel"]')];

  function activate(name) {
    tabs.forEach((tab) => {
      const selected = tab.dataset.tab === name;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    panels.forEach((panel) => {
      const show = panel.dataset.panel === name;
      panel.hidden = !show;
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => activate(tab.dataset.tab));
    tab.addEventListener("keydown", (event) => {
      const index = tabs.indexOf(tab);
      if (event.key === "ArrowRight") {
        event.preventDefault();
        const next = tabs[(index + 1) % tabs.length];
        next.focus();
        activate(next.dataset.tab);
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        const prev = tabs[(index - 1 + tabs.length) % tabs.length];
        prev.focus();
        activate(prev.dataset.tab);
      }
    });
  });
})();
