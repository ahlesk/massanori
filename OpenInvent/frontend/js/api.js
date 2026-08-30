/**
 * Único módulo que fala HTTP com o backend. Nenhum outro arquivo JS deve
 * chamar fetch() diretamente — tudo passa por aqui, evitando duplicar
 * montagem de URL, headers e tratamento de erro em cada tela.
 */
const API_BASE_URL = "http://localhost:8000/api";
const TOKEN_STORAGE_KEY = "notebooks_inventory_token";

export function getToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

function toQueryString(params = {}) {
  const entries = Object.entries(params).filter(
    ([, value]) => value !== undefined && value !== null && value !== ""
  );
  if (!entries.length) return "";
  return `?${new URLSearchParams(entries).toString()}`;
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Token ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    // Token expirado/revogado numa chamada autenticada: manda direto pro
    // login em vez de deixar cada tela tratar 401 na mão.
    const onLoginPage = window.location.pathname.endsWith("login.html");
    if (auth && response.status === 401 && !onLoginPage) {
      clearToken();
      window.location.href = "login.html";
    }

    const message = (data && (data.detail || firstFieldError(data))) || `Erro ${response.status}`;
    throw new ApiError(message, response.status, data);
  }

  return data;
}

/** Erros de validação do DRF vêm como {campo: ["mensagem"]}; pega a primeira. */
function firstFieldError(data) {
  if (typeof data !== "object" || data === null) return null;
  const firstKey = Object.keys(data)[0];
  const value = data[firstKey];
  return Array.isArray(value) ? `${firstKey}: ${value[0]}` : null;
}

export const api = {
  login: (email, password) =>
    request("/auth/login/", { method: "POST", body: { email, password }, auth: false }),
  logout: () => request("/auth/logout/", { method: "POST" }),
  me: () => request("/auth/me/"),

  listUsers: (params) => request(`/users/${toQueryString(params)}`),
  createUser: (payload) => request("/users/", { method: "POST", body: payload, auth: false }),

  getSummary: () => request("/notebooks/summary/"),
  listNotebooks: (params) => request(`/notebooks/${toQueryString(params)}`),
  createNotebook: (payload) => request("/notebooks/", { method: "POST", body: payload }),
  getNotebook: (asset) => request(`/notebooks/${encodeURIComponent(asset)}/`),
  updateNotebook: (asset, payload) =>
    request(`/notebooks/${encodeURIComponent(asset)}/`, { method: "PUT", body: payload }),
  deleteNotebook: (asset) =>
    request(`/notebooks/${encodeURIComponent(asset)}/`, { method: "DELETE" }),
  checkoutNotebook: (asset, payload) =>
    request(`/notebooks/${encodeURIComponent(asset)}/checkout/`, { method: "POST", body: payload }),
  returnNotebook: (asset, payload) =>
    request(`/notebooks/${encodeURIComponent(asset)}/return/`, { method: "POST", body: payload }),
  getHistory: (asset) => request(`/notebooks/${encodeURIComponent(asset)}/history/`),

  listMovements: (params) => request(`/movements/${toQueryString(params)}`),
};
