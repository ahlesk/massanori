/** Helpers de UI compartilhados entre telas: modal e toast de feedback. */

export function openModal(modalEl) {
  modalEl.classList.remove("hidden");
}

export function closeModal(modalEl) {
  modalEl.classList.add("hidden");
}

/** Fecha ao clicar no backdrop, em qualquer [data-close-modal] ou apertar Esc. */
export function initModals() {
  document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (event) => {
      if (event.target === backdrop) closeModal(backdrop);
    });
  });

  document.querySelectorAll("[data-close-modal]").forEach((el) => {
    el.addEventListener("click", () => {
      const modal = el.closest(".modal-backdrop");
      if (modal) closeModal(modal);
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    document.querySelectorAll(".modal-backdrop:not(.hidden)").forEach(closeModal);
  });
}

let toastTimeout;

export function showToast(message, type = "info") {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.className = `toast-${type} show`;

  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.remove("show"), 3500);
}
