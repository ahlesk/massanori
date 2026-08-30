# OpenInvent — Inventário e Rastreabilidade de Notebooks Corporativos

Sistema de auditoria/rastreabilidade de notebooks: quem está com qual
máquina, histórico imutável de retiradas e devoluções.

## Status

- **Fase 1 (concluída):** estrutura Django + DRF, conexão MongoDB via
  pymongo, arquitetura em camadas (View → Serializer → Service →
  Repository → MongoDB), CRUD básico de `notebooks` e `users` (soft
  delete incluso).
- **Autenticação (adiantada da Fase 4):** todo usuário criado via
  `POST /api/users/` já nasce com senha e consegue logar imediatamente
  em `POST /api/auth/login/` — sem passo de ativação. Login por token
  opaco (`Authorization: Token <valor>`), validado direto contra a
  collection `users` (ver `apps/core/authentication.py`). Todos os
  endpoints exigem esse token por padrão; só o cadastro e o login ficam
  abertos. Não há papéis/permissões diferenciadas ainda — qualquer
  usuário autenticado tem acesso completo (cadastrar notebook, estoque,
  checkout/devolução).
- **Fase 2 (concluída):** checkout, devolução, histórico e testes
  automatizados (26 testes, `manage.py test`, contra o MongoDB real).
- **Fase 3 (concluída):** front-end vanilla JS (HTML/CSS modular + ES
  modules) — login, listagem com filtros, criação de notebook,
  retirada/devolução por modal. Validado ponta a ponta em Chromium real
  via Playwright (login → criar → retirar → ver → devolver → filtrar →
  logout).
- **Fase 4 (concluída):** dashboard com métricas (`GET
  /api/notebooks/summary/`) e feed das últimas movimentações (`GET
  /api/movements/?limit=`), tela de detalhes do notebook com ficha
  técnica + histórico completo, e um refinamento de autenticação
  (qualquer 401 numa chamada autenticada já redireciona pro login,
  em vez de cada tela tratar isso na mão). Validado ponta a ponta em
  Chromium via Playwright. Papéis/permissões continuam no modelo
  flat decidido na Fase 2 (qualquer usuário autenticado tem acesso
  completo) — RBAC de verdade (admin vs operador comum) ficou de fora
  por decisão explícita, não por esquecimento.

## Arquitetura do back-end

```
backend/
  config/            settings, urls, wsgi/asgi
  apps/
    core/            db.py (conexão pymongo + índices), exceptions.py,
                      api.py (exception handler do DRF), utils.py
    users/           repositories.py, services.py, serializers.py, views.py, urls.py
    notebooks/       idem
    movements/       idem (histórico imutável: só insert + leitura)
```

Django/DRF atua só como camada web (roteamento, parsing, serialização).
Todo o domínio (`users`, `notebooks`, `movements`) é persistido no
MongoDB via pymongo, isolado atrás da camada Repository — nenhuma
service ou view fala com o driver Mongo diretamente. O sqlite do Django
é usado apenas pelos apps internos (`admin`/`auth`/`sessions`).

## Como rodar localmente

```bash
# 1. subir o MongoDB
docker compose up -d

# 2. configurar e rodar o backend
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
./venv/bin/python manage.py migrate   # apenas tabelas internas do Django
./venv/bin/python manage.py runserver
```

API disponível em `http://localhost:8000/api/`.

### Endpoints (Fase 1 + autenticação)

Autenticação (abertos, sem token):
- `POST /api/users/` — cadastro (name, email, department, password, active?)
- `POST /api/auth/login/` — body `{email, password}` → `{token, user}`

Autenticados (`Authorization: Token <valor>`):
- `GET /api/users/`
- `POST /api/auth/logout/` — invalida o token atual
- `GET /api/auth/me/` — usuário do token atual
- `GET /api/notebooks/?status=&asset=` (busca por status e por trecho do asset)
- `POST /api/notebooks/`
- `GET/PUT/DELETE /api/notebooks/{asset}/` (DELETE é soft delete → `INATIVO`)
- `POST /api/notebooks/{asset}/checkout/` — body `{user_id, observation?}`
- `POST /api/notebooks/{asset}/return/` — body `{condition?, observation?}` (`condition="AVARIA"` → `MANUTENCAO`; qualquer outro valor/ausente → `EM_ESTOQUE`)
- `GET /api/notebooks/{asset}/history/` — timeline completa (mais recente primeiro)
- `GET /api/notebooks/summary/` — contagem por status (cards do dashboard)
- `GET /api/movements/?asset=&limit=` — `limit` corta o resultado (usado no feed do dashboard)

### Rodando os testes

```bash
cd backend
docker compose -f ../docker-compose.yml up -d   # Mongo precisa estar de pé
./venv/bin/python manage.py test apps
```

Os testes usam um banco Mongo separado (`notebooks_inventory_test`,
configurado em `apps/core/testing.py` via `override_settings`) e limpam
as collections a cada teste — não tocam nos dados de desenvolvimento.

## Front-end (Fases 3 e 4)

```
frontend/
  index.html            redireciona para dashboard.html (logado) ou login.html
  login.html            tela de login
  dashboard.html        métricas por status + feed das últimas movimentações
  notebooks.html        listagem + modais (novo/retirar/devolver) + soft delete
  notebook-detail.html  ficha técnica + histórico imutável completo de um notebook
  css/                  reset.css, layout.css, components.css
  js/
    api.js              único módulo que fala HTTP com o backend (fetch + token)
    ui.js               helpers compartilhados: modal, toast, cabeçalho/sessão,
                         labels de status/tipo de movimento, escape de HTML
    login.js             lógica da tela de login
    dashboard.js          lógica do dashboard
    notebooks.js          lógica da listagem
    notebook-detail.js    lógica da tela de detalhes
```

`js/api.js` é o único arquivo que chama `fetch()` — todas as outras
telas passam por ele, incluindo a injeção do header
`Authorization: Token <valor>` (guardado em `localStorage`) e o
redirecionamento automático para `login.html` caso o token seja
rejeitado (401) em qualquer chamada autenticada. Não há build step:
são módulos ES nativos (`<script type="module">`), por isso o front
precisa ser servido por HTTP (não aberto como `file://`).

Rodando localmente (com o backend já de pé em `:8000`):

```bash
cd frontend
python3 -m http.server 5500
# abrir http://localhost:5500/
```
