"""Base de testes de API que usam o MongoDB de domínio.

Usa um banco Mongo dedicado (MONGO_DB_NAME de teste) e limpa as
collections antes de cada teste: o TestCase do Django só dá rollback
automático no banco relacional (sqlite), nunca no Mongo.
"""
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.core.db import ensure_indexes, get_db

TEST_MONGO_DB_NAME = "notebooks_inventory_test"


@override_settings(MONGO_DB_NAME=TEST_MONGO_DB_NAME)
class MongoAPITestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ensure_indexes()

    def setUp(self):
        super().setUp()
        db = get_db()
        db.users.delete_many({})
        db.notebooks.delete_many({})
        db.movements.delete_many({})

    def register_and_login(
        self,
        email: str = "operador@example.com",
        password: str = "senha123456",
        name: str = "Operador Teste",
        department: str = "TI",
    ) -> tuple[dict, str]:
        """Cadastra um usuário e já loga com ele, deixando self.client
        autenticado. Reflete o requisito de que um usuário recém-criado já
        consegue logar e usar a aplicação, sem passo de ativação."""
        create_resp = self.client.post(
            "/api/users/",
            {"name": name, "email": email, "department": department, "password": password},
            format="json",
        )
        assert create_resp.status_code == 201, create_resp.data

        login_resp = self.client.post(
            "/api/auth/login/", {"email": email, "password": password}, format="json"
        )
        assert login_resp.status_code == 200, login_resp.data

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login_resp.data['token']}")
        return login_resp.data["user"], login_resp.data["token"]
