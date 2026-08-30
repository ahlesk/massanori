import { api, getToken, clearToken } from "./api.js";
import {
  MOVEMENT_TYPE_LABELS,
  escapeHtml,
  formatDateTime,
  initHeaderSession,
  showToast,
} from "./ui.js";

if (!getToken()) {
  window.location.href = "login.html";
}

const cards = {
  EM_ESTOQUE: document.getElementById("card-em-estoque"),
  EM_USO: document.getElementById("card-em-uso"),
  MANUTENCAO: document.getElementById("card-manutencao"),
  INATIVO: document.getElementById("card-inativo"),
  total: document.getElementById("card-total"),
};

const feedBody = document.querySelector("#movements-feed tbody");
const FEED_LIMIT = 10;

async function loadSummary() {
  try {
    const summary = await api.getSummary();
    Object.entries(cards).forEach(([key, el]) => {
      el.textContent = summary[key] ?? 0;
    });
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadFeed() {
  feedBody.innerHTML = `<tr><td colspan="5">Carregando...</td></tr>`;
  try {
    const movements = await api.listMovements({ limit: FEED_LIMIT });
    if (!movements.length) {
      feedBody.innerHTML = `<tr><td colspan="5">Nenhuma movimentação registrada ainda.</td></tr>`;
      return;
    }
    feedBody.innerHTML = movements.map(feedRowHtml).join("");
  } catch (err) {
    feedBody.innerHTML = `<tr><td colspan="5">Erro ao carregar movimentações.</td></tr>`;
    showToast(err.message, "error");
  }
}

function feedRowHtml(movement) {
  const isCheckout = movement.type === "RETIRADA";
  const employee = isCheckout ? movement.responsible : movement.returned_by;
  const operator = isCheckout ? movement.performed_by : movement.received_by;

  return `
    <tr>
      <td><span class="badge badge-${movement.type.toLowerCase()}">${MOVEMENT_TYPE_LABELS[movement.type] || movement.type}</span></td>
      <td><a href="notebook-detail.html?asset=${encodeURIComponent(movement.asset)}">${escapeHtml(movement.asset)}</a></td>
      <td>${escapeHtml(employee ? employee.name : "—")}</td>
      <td>${escapeHtml(operator ? operator.name : "—")}</td>
      <td>${formatDateTime(movement.date)}</td>
    </tr>
  `;
}

initHeaderSession(api, clearToken);
loadSummary();
loadFeed();
