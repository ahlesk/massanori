/** Helpers de UI compartilhados entre telas: modal, toast, cabeçalho e formatação. */

export const STATUS_LABELS = {
  EM_ESTOQUE: "Em estoque",
  EM_USO: "Em uso",
  MANUTENCAO: "Manutenção",
  INATIVO: "Inativo",
};

export const MOVEMENT_TYPE_LABELS = {
  RETIRADA: "Retirada",
  DEVOLUCAO: "Devolução",
};

export function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]
  ));
}

export function formatDateTime(isoString) {
  return new Date(isoString).toLocaleString("pt-BR");
}

/**
 * Toda tela autenticada repete o mesmo cabeçalho (nome do usuário logado +
 * botão de sair). Centralizado aqui para não duplicar essa lógica em
 * dashboard.js, notebooks.js e notebook-detail.js.
 */
export async function initHeaderSession(api, clearToken) {
  const currentUserLabel = document.getElementById("current-user");
  if (currentUserLabel) {
    try {
      const me = await api.me();
      currentUserLabel.textContent = `${me.name} (${me.department})`;
    } catch {
      clearToken();
      window.location.href = "login.html";
    }
  }

  const btnLogout = document.getElementById("btn-logout");
  if (btnLogout) {
    btnLogout.addEventListener("click", async () => {
      try {
        await api.logout();
      } catch {
        // token já pode estar inválido; segue para o login de qualquer forma.
      }
      clearToken();
      window.location.href = "login.html";
    });
  }
}

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
