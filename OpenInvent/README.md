# OpenInvent — Inventário e Rastreabilidade de Notebooks Corporativos

Sistema de auditoria/rastreabilidade de notebooks: quem está com qual
máquina, histórico imutável de retiradas e devoluções.

## Status

- **Fase 1 (concluída):** estrutura Django + DRF, conexão MongoDB via
  pymongo, arquitetura em camadas (View → Serializer → Service →
  Repository → MongoDB), CRUD básico de `notebooks` e `users` (soft
  delete incluso).
- **Fase 2 (a seguir):** checkout, devolução, histórico e testes.
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

### Endpoints (Fase 1)

- `GET/POST /api/users/`
- `GET /api/notebooks/?status=&asset=` (busca por status e por trecho do asset)
- `POST /api/notebooks/`
- `GET/PUT/DELETE /api/notebooks/{asset}/` (DELETE é soft delete → `INATIVO`)
- `GET /api/movements/?asset=`

`checkout`, `return` e `history` chegam na Fase 2.
