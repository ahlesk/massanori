"""Repository: única camada que fala diretamente com a collection `users`."""
from __future__ import annotations

from bson import ObjectId

from apps.core.db import get_db


class UserRepository:
    def __init__(self, db=None):
        self._db = db or get_db()

    @property
    def collection(self):
        return self._db.users

    def insert(self, doc: dict) -> dict:
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    def find_by_id(self, user_id: ObjectId) -> dict | None:
        return self.collection.find_one({"_id": user_id})

    def exists_by_email(self, email: str) -> bool:
        return self.collection.count_documents({"email": email}, limit=1) > 0

    def list(self, active: bool | None = None) -> list[dict]:
        query: dict = {}
        if active is not None:
            query["active"] = active
        return list(self.collection.find(query).sort("name", 1))
