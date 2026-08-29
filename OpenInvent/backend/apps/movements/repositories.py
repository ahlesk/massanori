"""Repository: única camada que fala diretamente com a collection `movements`.

Histórico imutável: propositalmente não há update/delete aqui, apenas
insert e leitura. Registros de movimentação nunca são alterados nem removidos.
"""
from __future__ import annotations

from apps.core.db import get_db


class MovementRepository:
    def __init__(self, db=None):
        self._db = db or get_db()

    @property
    def collection(self):
        return self._db.movements

    def insert(self, doc: dict) -> dict:
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    def list(self, asset: str | None = None, notebook_id=None) -> list[dict]:
        query: dict = {}
        if asset:
            query["asset"] = asset
        if notebook_id:
            query["notebook_id"] = notebook_id
        return list(self.collection.find(query).sort("date", -1))
