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
