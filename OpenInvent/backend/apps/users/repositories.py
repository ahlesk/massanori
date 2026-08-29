"""Repository: única camada que fala diretamente com a collection `users`."""
from __future__ import annotations

from bson import ObjectId

from apps.core.db import get_db


class UserRepository:
    def __init__(self, db=None):
        # get_db() só é chamado dentro de `collection`, na hora do acesso —
        # nunca aqui. Views guardam o service/repository como atributo de
        # classe (singleton criado na importação do módulo); se resolvêssemos
        # o db já no __init__, essa instância ficaria presa ao banco vigente
        # naquele instante, ignorando qualquer troca posterior de
        # settings.MONGO_DB_NAME (é exatamente o que os testes fazem via
        # override_settings em apps.core.testing.MongoAPITestCase).
        self._db = db

    @property
    def collection(self):
        return (self._db or get_db()).users

    def insert(self, doc: dict) -> dict:
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    def find_by_id(self, user_id: ObjectId) -> dict | None:
        return self.collection.find_one({"_id": user_id})

    def find_by_email(self, email: str) -> dict | None:
        return self.collection.find_one({"email": email})

    def find_by_token(self, token: str) -> dict | None:
        return self.collection.find_one({"auth_token": token})

    def exists_by_email(self, email: str) -> bool:
        return self.collection.count_documents({"email": email}, limit=1) > 0

    def list(self, active: bool | None = None) -> list[dict]:
        query: dict = {}
        if active is not None:
            query["active"] = active
        return list(self.collection.find(query).sort("name", 1))

    def set_token(self, user_id: ObjectId, token: str) -> None:
        self.collection.update_one({"_id": user_id}, {"$set": {"auth_token": token}})

    def clear_token(self, user_id: ObjectId) -> None:
        self.collection.update_one({"_id": user_id}, {"$unset": {"auth_token": ""}})
