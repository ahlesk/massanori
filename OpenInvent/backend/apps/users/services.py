"""Service: regras de negócio de `users`. Não conhece MongoDB nem HTTP."""
from __future__ import annotations

from apps.core.exceptions import ConflictError, NotFoundError
from apps.core.utils import to_object_id
from apps.users.repositories import UserRepository


class UserService:
    def __init__(self, repository: UserRepository | None = None):
        self.repository = repository or UserRepository()

    def create_user(self, data: dict) -> dict:
        email = data["email"]
        if self.repository.exists_by_email(email):
            raise ConflictError(f"Já existe um usuário com o e-mail '{email}'.")

        doc = {
            "name": data["name"],
            "email": email,
            "department": data["department"],
            "active": data.get("active", True),
        }
        return self.repository.insert(doc)

    def list_users(self, active: bool | None = None) -> list[dict]:
        return self.repository.list(active=active)

    def get_user(self, user_id: str) -> dict:
        """Usado pelo NotebookService para embutir {user_id, name} em
        current_responsible/responsible no momento do checkout."""
        try:
            oid = to_object_id(user_id)
        except ValueError as exc:
            raise NotFoundError(str(exc)) from exc

        user = self.repository.find_by_id(oid)
        if not user:
            raise NotFoundError(f"Usuário '{user_id}' não encontrado.")
        return user
