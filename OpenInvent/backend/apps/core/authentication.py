"""Autenticação por token opaco contra a collection `users` do MongoDB.

Não usamos rest_framework.authtoken porque ele amarra o Token ao model
django.contrib.auth.User (ORM/sqlite) — nosso usuário de domínio vive
inteiramente no Mongo, então o token é gerado e validado ali mesmo
(ver UserService.login / get_user_by_token).
"""
from __future__ import annotations

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from apps.core.exceptions import NotFoundError


class MongoUser:
    """Wrapper leve em torno do documento de `users`, para servir de request.user."""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, doc: dict):
        self.id = str(doc["_id"])
        self.name = doc.get("name")
        self.email = doc.get("email")
        self.department = doc.get("department")
        self.active = doc.get("active", True)

    def __str__(self):
        return self.email or self.id


class MongoTokenAuthentication(BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Token de autenticação não informado.")
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed("Cabeçalho de autenticação inválido.")

        token = auth[1].decode()
        return self._authenticate_token(token)

    def _authenticate_token(self, token: str):
        # Import local para evitar import circular (services -> ... -> apps carregados).
        from apps.users.services import UserService

        try:
            user_doc = UserService().get_user_by_token(token)
        except NotFoundError as exc:
            raise exceptions.AuthenticationFailed(str(exc)) from exc

        return (MongoUser(user_doc), token)

    def authenticate_header(self, request):
        return self.keyword
