from rest_framework.test import APIClient

from apps.core.testing import MongoAPITestCase


class MovementListTests(MongoAPITestCase):
    def setUp(self):
        super().setUp()
        self.operator, self.token = self.register_and_login()

    def test_requires_authentication(self):
        anon = APIClient()
        resp = anon.get("/api/movements/")
        self.assertEqual(resp.status_code, 401)

    def test_empty_list_when_no_movements(self):
        resp = self.client.get("/api/movements/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, [])

    def test_limit_caps_number_of_results(self):
        employee_resp = self.client.post(
            "/api/users/",
            {
                "name": "Funcionario",
                "email": "func_limit@example.com",
                "department": "Vendas",
                "password": "senha123456",
            },
            format="json",
        )
        employee_id = employee_resp.data["id"]

        for i in range(3):
            asset = f"NOTE-LIMIT-{i}"
            self.client.post(
                "/api/notebooks/",
                {
                    "asset": asset,
                    "brand": "Dell",
                    "model": "Latitude",
                    "serial_number": f"SN-{i}",
                },
                format="json",
            )
            self.client.post(
                f"/api/notebooks/{asset}/checkout/", {"user_id": employee_id}, format="json"
            )

        resp = self.client.get("/api/movements/?limit=2")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)
