"""Service: regras de negócio de `users`. Não conhece MongoDB nem HTTP."""
from __future__ import annotations

import secrets

from django.contrib.auth.hashers import check_password, make_password

from apps.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from apps.core.utils import to_object_id
from apps.users.repositories import UserRepository


class UserService:
    def __init__(self, repository: UserRepository | None = None):
        self.repository = repository or UserRepository()

    def create_user(self, data: dict) -> dict:
        """Com e-mail + senha, o usuário pode logar imediatamente via
        POST /api/auth/login/, sem passo de ativação. Sem eles, é um
        responsável: só nome e departamento, sem login, usado apenas para
        retirar/devolver notebooks."""
        doc = {
            "name": data["name"],
            "department": data["department"],
            "active": data.get("active", True),
        }

        email = data.get("email")
        if email:
            if self.repository.exists_by_email(email):
                raise ConflictError(f"Já existe um usuário com o e-mail '{email}'.")
            doc["email"] = email
            doc["password_hash"] = make_password(data["password"])

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

    def authenticate(self, email: str, password: str) -> dict:
        user = self.repository.find_by_email(email)
        # Mensagem genérica de propósito: não revela se o e-mail existe ou não.
        if not user or not user.get("active", True) or not check_password(
            password, user.get("password_hash", "")
        ):
            raise AuthenticationError()
        return user

    def login(self, email: str, password: str) -> tuple[dict, str]:
        user = self.authenticate(email, password)
        token = secrets.token_hex(32)
        self.repository.set_token(user["_id"], token)
        return user, token

    def logout(self, user_id: str) -> None:
        self.repository.clear_token(to_object_id(user_id))

    def get_user_by_token(self, token: str) -> dict:
        user = self.repository.find_by_token(token)
        if not user or not user.get("active", True):
            raise NotFoundError("Token inválido ou expirado.")
        return user
