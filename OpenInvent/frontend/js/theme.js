/*
 * Tema claro/escuro. Script clássico (não módulo) carregado no <head> de
 * todas as páginas: aplica o tema antes da primeira pintura, evitando o
 * "piscar" do tema errado, e depois insere o botão de alternância.
 *
 * Ordem de escolha: tema salvo pelo usuário > preferência do sistema > escuro.
 */
(function () {
  var STORAGE_KEY = "openinvent-theme";
  var root = document.documentElement;

  function readStored() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function store(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      // modo privado/armazenamento bloqueado: tema vale só para esta página.
    }
  }

  function systemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches
      ? "light"
      : "dark";
  }

  function current() {
    return root.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  var stored = readStored();
  root.setAttribute("data-theme", stored === "light" || stored === "dark" ? stored : systemTheme());

  var ICON_SUN =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var ICON_MOON =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

  function updateButton(button) {
    var isDark = current() === "dark";
    // Mostra o ícone do tema para o qual o clique vai mudar.
    button.innerHTML = isDark ? ICON_SUN : ICON_MOON;
    var label = isDark ? "Mudar para tema claro" : "Mudar para tema escuro";
    button.setAttribute("aria-label", label);
    button.title = label;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "theme-toggle";
    updateButton(button);

    button.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      store(next);
      updateButton(button);
    });

    // No cabeçalho, antes do nome do usuário; sem cabeçalho (login), no canto.
    var userInfo = document.querySelector(".app-header .user-info");
    if (userInfo) {
      userInfo.insertBefore(button, userInfo.firstChild);
    } else if (document.body.classList.contains("login-page")) {
      button.classList.add("theme-toggle-floating");
      document.body.appendChild(button);
    }
  });
})();
