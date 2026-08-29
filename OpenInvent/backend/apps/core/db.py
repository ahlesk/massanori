"""
Camada de acesso bruto ao MongoDB.

Mantém um único MongoClient por processo (o driver do pymongo já
gerencia um pool de conexões internamente) e expõe helpers para obter
o database e garantir os índices exigidos pelas regras de negócio.
"""
from __future__ import annotations

import threading

from django.conf import settings
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

_client: MongoClient | None = None
_lock = threading.Lock()


def get_client() -> MongoClient:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = MongoClient(settings.MONGO_URI)
    return _client


def get_db() -> Database:
    return get_client()[settings.MONGO_DB_NAME]


def ensure_indexes() -> None:
    """Cria (de forma idempotente) os índices que sustentam as regras de negócio."""
    db = get_db()

    # asset é o identificador de patrimônio e precisa ser estritamente único.
    db.notebooks.create_index([("asset", ASCENDING)], unique=True, name="uniq_asset")
    db.notebooks.create_index([("status", ASCENDING)], name="idx_status")

    db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_email")

    # histórico é consultado por notebook e ordenado por data.
    db.movements.create_index([("notebook_id", ASCENDING)], name="idx_notebook_id")
    db.movements.create_index([("asset", ASCENDING)], name="idx_asset")
    db.movements.create_index([("date", ASCENDING)], name="idx_date")
