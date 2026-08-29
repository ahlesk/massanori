from rest_framework.test import APIClient

from apps.core.testing import MongoAPITestCase


class UserRegistrationAndAuthTests(MongoAPITestCase):
    def _register(self, email="user@example.com", password="senha123456", **extra):
        payload = {
            "name": extra.pop("name", "Usuario Teste"),
            "email": email,
            "department": extra.pop("department", "TI"),
            "password": password,
            **extra,
        }
        return self.client.post("/api/users/", payload, format="json")

    def test_register_does_not_leak_password(self):
        resp = self._register()
        self.assertEqual(resp.status_code, 201)
        self.assertNotIn("password", resp.data)
        self.assertNotIn("password_hash", resp.data)

    def test_register_duplicate_email_conflict(self):
        self._register(email="dup@example.com")
        resp = self._register(email="dup@example.com")
        self.assertEqual(resp.status_code, 409)

    def test_login_wrong_password(self):
        self._register(email="user2@example.com", password="senhacerta1")
        resp = self.client.post(
            "/api/auth/login/", {"email": "user2@example.com", "password": "errada"}, format="json"
        )
        self.assertEqual(resp.status_code, 401)

    def test_user_can_login_immediately_after_creation(self):
        self._register(email="imediato@example.com", password="minhasenha1")
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "imediato@example.com", "password": "minhasenha1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("token", resp.data)

    def test_list_users_requires_authentication(self):
        anon = APIClient()
        resp = anon.get("/api/users/")
        self.assertEqual(resp.status_code, 401)

    def test_logout_invalidates_token(self):
        self._register(email="logout@example.com", password="minhasenha1")
        login_resp = self.client.post(
            "/api/auth/login/",
            {"email": "logout@example.com", "password": "minhasenha1"},
            format="json",
        )
        token = login_resp.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        logout_resp = self.client.post("/api/auth/logout/")
        self.assertEqual(logout_resp.status_code, 204)

        me_resp = self.client.get("/api/auth/me/")
        self.assertEqual(me_resp.status_code, 401)
