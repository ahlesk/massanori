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
- **Fase 3:** front-end vanilla JS.
- **Fase 4:** dashboard, tela de detalhes, autenticação/permissões.

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
- `GET /api/movements/?asset=`

### Rodando os testes

```bash
cd backend
docker compose -f ../docker-compose.yml up -d   # Mongo precisa estar de pé
./venv/bin/python manage.py test apps
```

Os testes usam um banco Mongo separado (`notebooks_inventory_test`,
configurado em `apps/core/testing.py` via `override_settings`) e limpam
as collections a cada teste — não tocam nos dados de desenvolvimento.
