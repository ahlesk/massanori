import { api, getToken, clearToken } from "./api.js?v=2";
import {
  MOVEMENT_TYPE_LABELS,
  STATUS_LABELS,
  escapeHtml,
  formatDateTime,
  initHeaderSession,
  showToast,
} from "./ui.js?v=2";

if (!getToken()) {
  window.location.href = "login.html";
}

const asset = new URLSearchParams(window.location.search).get("asset");
const historyBody = document.querySelector("#history-table tbody");

async function loadNotebook() {
  if (!asset) {
    document.getElementById("detail-asset").textContent = "Asset não informado";
    return;
  }

  try {
    const nb = await api.getNotebook(asset);
    document.title = `${nb.asset} — Inventário de Notebooks`;
    document.getElementById("detail-asset").textContent = nb.asset;
    document.getElementById("detail-brand").textContent = nb.brand;
    document.getElementById("detail-model").textContent = nb.model;
    document.getElementById("detail-serial").textContent = nb.serial_number;
    document.getElementById("detail-responsible").textContent = nb.current_responsible
      ? nb.current_responsible.name
      : "—";

    const statusBadge = document.getElementById("detail-status");
    statusBadge.textContent = STATUS_LABELS[nb.status] || nb.status;
    statusBadge.className = `badge badge-${nb.status.toLowerCase()}`;
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadHistory() {
  if (!asset) {
    historyBody.innerHTML = `<tr><td colspan="6">Informe um asset na URL (?asset=...).</td></tr>`;
    return;
  }

  historyBody.innerHTML = `<tr><td colspan="6">Carregando...</td></tr>`;
  try {
    const movements = await api.getHistory(asset);
    if (!movements.length) {
      historyBody.innerHTML = `<tr><td colspan="6">Nenhuma movimentação registrada para este notebook.</td></tr>`;
      return;
    }
    historyBody.innerHTML = movements.map(historyRowHtml).join("");
  } catch (err) {
    historyBody.innerHTML = `<tr><td colspan="6">Erro ao carregar histórico.</td></tr>`;
    showToast(err.message, "error");
  }
}

function historyRowHtml(movement) {
  const isCheckout = movement.type === "RETIRADA";
  const employee = isCheckout ? movement.responsible : movement.returned_by;
  const operator = isCheckout ? movement.performed_by : movement.received_by;

  return `
    <tr>
      <td><span class="badge badge-${movement.type.toLowerCase()}">${MOVEMENT_TYPE_LABELS[movement.type] || movement.type}</span></td>
      <td>${escapeHtml(employee ? employee.name : "—")}</td>
      <td>${escapeHtml(operator ? operator.name : "—")}</td>
      <td>${formatDateTime(movement.date)}</td>
      <td>${escapeHtml(movement.condition || "—")}</td>
      <td>${escapeHtml(movement.observation || "—")}</td>
    </tr>
  `;
}

initHeaderSession(api, clearToken);
loadNotebook();
loadHistory();
