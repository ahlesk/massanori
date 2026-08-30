import { api, getToken, clearToken } from "./api.js";
import { openModal, closeModal, initModals, showToast } from "./ui.js";

if (!getToken()) {
  window.location.href = "login.html";
}

const STATUS_LABELS = {
  EM_ESTOQUE: "Em estoque",
  EM_USO: "Em uso",
  MANUTENCAO: "Manutenção",
  INATIVO: "Inativo",
};

const state = { status: "", search: "" };

const tbody = document.querySelector("#notebooks-table tbody");
const statusFilter = document.getElementById("filter-status");
const searchInput = document.getElementById("filter-search");
const btnNewNotebook = document.getElementById("btn-new-notebook");
const btnLogout = document.getElementById("btn-logout");
const currentUserLabel = document.getElementById("current-user");

function formError(form, message) {
  const box = form.querySelector("[data-form-error]");
  if (box) box.textContent = message || "";
}

async function loadCurrentUser() {
  try {
    const me = await api.me();
    currentUserLabel.textContent = `${me.name} (${me.department})`;
  } catch (err) {
    clearToken();
    window.location.href = "login.html";
  }
}

async function loadNotebooks() {
  tbody.innerHTML = `<tr><td colspan="6">Carregando...</td></tr>`;
  try {
    const notebooks = await api.listNotebooks({ status: state.status, asset: state.search });
    renderNotebooks(notebooks);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6">Erro ao carregar notebooks.</td></tr>`;
    showToast(err.message, "error");
  }
}

function renderNotebooks(notebooks) {
  if (!notebooks.length) {
    tbody.innerHTML = `<tr><td colspan="6">Nenhum notebook encontrado.</td></tr>`;
    return;
  }

  tbody.innerHTML = notebooks.map(rowHtml).join("");
}

function rowHtml(nb) {
  const responsible = nb.current_responsible ? nb.current_responsible.name : "—";
  const canCheckout = nb.status === "EM_ESTOQUE";
  const canReturn = nb.status === "EM_USO";
  const canDelete = nb.status !== "EM_USO" && nb.status !== "INATIVO";
  const statusLabel = STATUS_LABELS[nb.status] || nb.status;

  return `
    <tr>
      <td>${escapeHtml(nb.asset)}</td>
      <td>${escapeHtml(nb.brand)} / ${escapeHtml(nb.model)}</td>
      <td>${escapeHtml(nb.serial_number)}</td>
      <td><span class="badge badge-${nb.status.toLowerCase()}">${statusLabel}</span></td>
      <td>${escapeHtml(responsible)}</td>
      <td class="actions">
        <button class="btn btn-sm" data-action="view" data-asset="${escapeHtml(nb.asset)}">Ver</button>
        <button class="btn btn-sm btn-primary" data-action="checkout" data-asset="${escapeHtml(nb.asset)}" ${canCheckout ? "" : "disabled"}>Retirar</button>
        <button class="btn btn-sm btn-secondary" data-action="return" data-asset="${escapeHtml(nb.asset)}" ${canReturn ? "" : "disabled"}>Devolver</button>
        <button class="btn btn-sm btn-danger" data-action="delete" data-asset="${escapeHtml(nb.asset)}" ${canDelete ? "" : "disabled"}>Excluir</button>
      </td>
    </tr>
  `;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]
  ));
}

tbody.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || button.disabled) return;

  const { action, asset } = button.dataset;
  if (action === "view") openViewModal(asset);
  if (action === "checkout") openCheckoutModal(asset);
  if (action === "return") openReturnModal(asset);
  if (action === "delete") handleDelete(asset);
});

async function handleDelete(asset) {
  if (!confirm(`Descontinuar o notebook ${asset}? Ele passará para o status INATIVO.`)) return;
  try {
    await api.deleteNotebook(asset);
    showToast(`Notebook ${asset} descontinuado.`, "success");
    loadNotebooks();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ---- modal: ver notebook ----

const viewModal = document.getElementById("modal-view");

async function openViewModal(asset) {
  try {
    const nb = await api.getNotebook(asset);
    viewModal.querySelector("[data-field=asset]").textContent = nb.asset;
    viewModal.querySelector("[data-field=brand]").textContent = nb.brand;
    viewModal.querySelector("[data-field=model]").textContent = nb.model;
    viewModal.querySelector("[data-field=serial_number]").textContent = nb.serial_number;
    viewModal.querySelector("[data-field=status]").textContent = STATUS_LABELS[nb.status] || nb.status;
    viewModal.querySelector("[data-field=responsible]").textContent = nb.current_responsible
      ? nb.current_responsible.name
      : "—";
    openModal(viewModal);
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ---- modal: novo notebook ----

const createModal = document.getElementById("modal-create-notebook");
const createForm = document.getElementById("form-create-notebook");

btnNewNotebook.addEventListener("click", () => {
  createForm.reset();
  formError(createForm, "");
  openModal(createModal);
});

createForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError(createForm, "");

  const payload = {
    asset: document.getElementById("create-asset").value.trim(),
    brand: document.getElementById("create-brand").value.trim(),
    model: document.getElementById("create-model").value.trim(),
    serial_number: document.getElementById("create-serial").value.trim(),
  };

  try {
    await api.createNotebook(payload);
    closeModal(createModal);
    showToast(`Notebook ${payload.asset} cadastrado.`, "success");
    loadNotebooks();
  } catch (err) {
    formError(createForm, err.message);
  }
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
    if (!users.length) {
      checkoutUserSelect.innerHTML = `<option value="">Nenhum usuário ativo cadastrado</option>`;
    } else {
      checkoutUserSelect.innerHTML = users
        .map((u) => `<option value="${u.id}">${escapeHtml(u.name)} — ${escapeHtml(u.department)}</option>`)
        .join("");
    }
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
    loadNotebooks();
  } catch (err) {
    formError(checkoutForm, err.message);
  }
});

// ---- modal: devolução (return) ----

const returnModal = document.getElementById("modal-return");
const returnForm = document.getElementById("form-return");
let returnAsset = null;

function openReturnModal(asset) {
  returnAsset = asset;
  returnForm.reset();
  formError(returnForm, "");
  openModal(returnModal);
}

returnForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError(returnForm, "");

  const payload = {
    condition: document.getElementById("return-condition").value,
    observation: document.getElementById("return-observation").value.trim(),
  };

  try {
    await api.returnNotebook(returnAsset, payload);
    closeModal(returnModal);
    showToast(`Notebook ${returnAsset} devolvido com sucesso.`, "success");
    loadNotebooks();
  } catch (err) {
    formError(returnForm, err.message);
  }
});

// ---- filtros ----

statusFilter.addEventListener("change", () => {
  state.status = statusFilter.value;
  loadNotebooks();
});

let searchDebounce;
searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    state.search = searchInput.value.trim();
    loadNotebooks();
  }, 300);
});

// ---- logout ----

btnLogout.addEventListener("click", async () => {
  try {
    await api.logout();
  } catch {
    // token já pode estar inválido; segue para o login de qualquer forma.
  }
  clearToken();
  window.location.href = "login.html";
});

initModals();
loadCurrentUser();
loadNotebooks();
