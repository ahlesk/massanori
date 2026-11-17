import { api, getToken, clearToken } from "./api.js";
import {
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

const tbody = document.querySelector("#responsibles-table tbody");
const searchInput = document.getElementById("filter-search");
const countLabel = document.getElementById("responsible-count");

// A lista é pequena: carrega uma vez e filtra no próprio navegador.
let allPeople = [];

function formError(form, message) {
  const box = form.querySelector("[data-form-error]");
  if (box) box.textContent = message || "";
}

async function loadPeople() {
  tbody.innerHTML = `<tr><td colspan="4">Carregando...</td></tr>`;
  try {
    allPeople = await api.listUsers();
    render();
  } catch (err) {
    countLabel.textContent = "";
    tbody.innerHTML = `<tr><td colspan="4">Erro ao carregar responsáveis.</td></tr>`;
    showToast(err.message, "error");
  }
}

function render() {
  const term = searchInput.value.trim().toLowerCase();
  const people = term
    ? allPeople.filter((p) =>
        `${p.name} ${p.department}`.toLowerCase().includes(term))
    : allPeople;

  countLabel.textContent = `(${people.length})`;
  if (!people.length) {
    tbody.innerHTML = `<tr><td colspan="4">${
      term ? "Nenhum responsável encontrado." : "Nenhum responsável cadastrado ainda."
    }</td></tr>`;
    return;
  }
  tbody.innerHTML = people.map(rowHtml).join("");
}

function rowHtml(person) {
  // Quem tem e-mail é usuário do sistema (faz login); sem e-mail é só responsável.
  const type = person.email ? "Usuário do sistema" : "Responsável";
  const status = person.active
    ? `<span class="badge badge-em_estoque">Ativo</span>`
    : `<span class="badge badge-inativo">Inativo</span>`;

  return `
    <tr>
      <td>${escapeHtml(person.name)}</td>
      <td>${escapeHtml(person.department)}</td>
      <td>${type}</td>
      <td>${status}</td>
    </tr>
  `;
}

let searchDebounce;
searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(render, 150);
});

// ---- modal: novo responsável ----

const createModal = document.getElementById("modal-create-responsible");
const createForm = document.getElementById("form-create-responsible");
const nameInput = document.getElementById("create-name");
const departmentInput = document.getElementById("create-department");

document.getElementById("btn-new-responsible").addEventListener("click", () => {
  createForm.reset();
  formError(createForm, "");
  openModal(createModal);
  nameInput.focus();
});

createForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError(createForm, "");

  const payload = {
    name: nameInput.value.trim(),
    department: departmentInput.value.trim(),
  };
  if (!payload.name || !payload.department) {
    formError(createForm, "Preencha o nome e o departamento.");
    return;
  }

  try {
    await api.createResponsible(payload);
    closeModal(createModal);
    showToast(`Responsável ${payload.name} cadastrado.`, "success");
    loadPeople();
  } catch (err) {
    formError(createForm, err.message);
  }
});

initModals();
initHeaderSession(api, clearToken);
loadPeople();
