import { api, getToken, setToken } from "./api.js?v=2";

if (getToken()) {
  window.location.href = "dashboard.html";
}

const form = document.getElementById("login-form");
const errorBox = document.getElementById("login-error");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.textContent = "";

  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  const submitButton = form.querySelector("button[type=submit]");
  submitButton.disabled = true;

  try {
    const { token } = await api.login(email, password);
    setToken(token);
    window.location.href = "dashboard.html";
  } catch (err) {
    errorBox.textContent = err.message || "Não foi possível entrar.";
  } finally {
    submitButton.disabled = false;
  }
});
