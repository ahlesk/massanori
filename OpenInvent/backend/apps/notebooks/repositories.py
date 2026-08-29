"""Repository: única camada que fala diretamente com a collection `notebooks`."""
from __future__ import annotations

from apps.core.db import get_db


class NotebookRepository:
    def __init__(self, db=None):
        self._db = db or get_db()

    @property
    def collection(self):
        return self._db.notebooks

    def insert(self, doc: dict) -> dict:
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    def find_by_asset(self, asset: str) -> dict | None:
        return self.collection.find_one({"asset": asset})

    def exists_by_asset(self, asset: str) -> bool:
        return self.collection.count_documents({"asset": asset}, limit=1) > 0

    def list(self, status: str | None = None, search: str | None = None) -> list[dict]:
        query: dict = {}
        if status:
            query["status"] = status
        if search:
            query["asset"] = {"$regex": search, "$options": "i"}
        return list(self.collection.find(query).sort("created_at", -1))

    def update_by_asset(self, asset: str, updates: dict) -> dict | None:
        self.collection.update_one({"asset": asset}, {"$set": updates})
        return self.find_by_asset(asset)
