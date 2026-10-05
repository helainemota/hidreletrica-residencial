(() => {
  document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("page-ready");

    // Efeito de toque/ripple para cards, links e botões.
    document.querySelectorAll(".metric-card, .quick-card, .panel, .status-card, button, nav a").forEach((el) => {
      el.classList.add("touch-target");
      el.addEventListener("pointerdown", (event) => {
        el.classList.add("is-pressed");
        const rect = el.getBoundingClientRect();
        const ripple = document.createElement("span");
        ripple.className = "touch-ripple";
        ripple.style.left = `${event.clientX - rect.left}px`;
        ripple.style.top = `${event.clientY - rect.top}px`;
        el.appendChild(ripple);
        setTimeout(() => ripple.remove(), 650);
      });
      ["pointerup", "pointercancel", "pointerleave"].forEach((type) => {
        el.addEventListener(type, () => el.classList.remove("is-pressed"));
      });
    });

    // Navegação com feedback imediato ao toque.
    document.querySelectorAll("nav a, .quick-card").forEach((link) => {
      link.addEventListener("click", () => {
        document.body.classList.add("page-leaving");
      });
    });

    // Atualização opcional: qualquer elemento com data-refresh atualiza os dados.
    document.querySelectorAll("[data-refresh]").forEach((button) => {
      button.addEventListener("click", async () => {
        button.classList.add("is-loading");
        const original = button.innerHTML;
        button.innerHTML = "Atualizando…";
        try {
          await fetch("/atualizar", { cache: "no-store" });
          window.location.reload();
        } catch (error) {
          button.innerHTML = original;
          button.classList.remove("is-loading");
        }
      });
    });

    // Pequena animação nos números principais.
    document.querySelectorAll(".metric-card strong, .history-summary strong").forEach((el) => {
      el.classList.add("number-pop");
    });
  });
})();
