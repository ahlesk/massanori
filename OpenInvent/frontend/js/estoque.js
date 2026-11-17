import { api, getToken, clearToken } from "./api.js";
import {
  STATUS_LABELS,
  closeModal,
  escapeHtml,
  initHeaderSession,
  initModals,
  openModal,
  showToast,
} from "./ui.js";

if (!getToken()) {
  window.location.href = "login.html";
}

// Esta tela lista apenas notebooks disponíveis (status EM_ESTOQUE).
const STOCK_STATUS = "EM_ESTOQUE";

const state = { search: "" };

const tbody = document.querySelector("#stock-table tbody");
const searchInput = document.getElementById("filter-search");
const stockCount = document.getElementById("stock-count");

function formError(form, message) {
  const box = form.querySelector("[data-form-error]");
  if (box) box.textContent = message || "";
}

async function loadStock() {
  tbody.innerHTML = `<tr><td colspan="5">Carregando...</td></tr>`;
  try {
    const notebooks = await api.listNotebooks({ status: STOCK_STATUS, asset: state.search });
    stockCount.textContent = `(${notebooks.length})`;
    if (!notebooks.length) {
      tbody.innerHTML = `<tr><td colspan="5">Nenhum notebook em estoque.</td></tr>`;
      return;
    }
    tbody.innerHTML = notebooks.map(rowHtml).join("");
  } catch (err) {
    stockCount.textContent = "";
    tbody.innerHTML = `<tr><td colspan="5">Erro ao carregar o estoque.</td></tr>`;
    showToast(err.message, "error");
  }
}

function rowHtml(nb) {
  const detailHref = `notebook-detail.html?asset=${encodeURIComponent(nb.asset)}`;

  return `
    <tr>
      <td>${escapeHtml(nb.asset)}</td>
      <td>${escapeHtml(nb.brand)} / ${escapeHtml(nb.model)}</td>
      <td>${escapeHtml(nb.serial_number)}</td>
      <td><span class="badge badge-${nb.status.toLowerCase()}">${STATUS_LABELS[nb.status] || nb.status}</span></td>
      <td class="actions">
        <a class="btn btn-sm" href="${detailHref}">Ver</a>
        <button class="btn btn-sm btn-primary" data-action="checkout" data-asset="${escapeHtml(nb.asset)}">Retirar</button>
      </td>
    </tr>
  `;
}

tbody.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action='checkout']");
  if (button) openCheckoutModal(button.dataset.asset);
});

// ---- modal: retirada (checkout) ----

const checkoutModal = document.getElementById("modal-checkout");
const checkoutForm = document.getElementById("form-checkout");
const checkoutUserSelect = document.getElementById("checkout-user");
let checkoutAsset = null;

async function openCheckoutModal(asset) {
  checkoutAsset = asset;
  checkoutForm.reset();
  formError(checkoutForm, "");

  try {
    const users = await api.listUsers({ active: true });
    checkoutUserSelect.innerHTML = users.length
      ? users
          .map((u) => `<option value="${u.id}">${escapeHtml(u.name)} — ${escapeHtml(u.department)}</option>`)
          .join("")
      : `<option value="">Nenhum usuário ativo cadastrado</option>`;
    openModal(checkoutModal);
  } catch (err) {
    showToast(err.message, "error");
  }
}

checkoutForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError(checkoutForm, "");

  const payload = {
    user_id: checkoutUserSelect.value,
    observation: document.getElementById("checkout-observation").value.trim(),
  };

  try {
    await api.checkoutNotebook(checkoutAsset, payload);
    closeModal(checkoutModal);
    showToast(`Notebook ${checkoutAsset} retirado com sucesso.`, "success");
    loadStock();
  } catch (err) {
    formError(checkoutForm, err.message);
  }
});

// ---- busca ----

let searchDebounce;
searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    state.search = searchInput.value.trim();
    loadStock();
  }, 300);
});

initModals();
initHeaderSession(api, clearToken);
loadStock();
