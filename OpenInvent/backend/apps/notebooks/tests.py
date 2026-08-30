from rest_framework.test import APIClient

from apps.core.testing import MongoAPITestCase


class NotebookCRUDTests(MongoAPITestCase):
    def setUp(self):
        super().setUp()
        self.operator, self.token = self.register_and_login()

    def _create_notebook(self, asset="NOTE0001", **overrides):
        payload = {
            "asset": asset,
            "brand": "Dell",
            "model": "Latitude 5420",
            "serial_number": "SN123",
            **overrides,
        }
        return self.client.post("/api/notebooks/", payload, format="json")

    def test_create_notebook(self):
        resp = self._create_notebook()
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["status"], "EM_ESTOQUE")
        self.assertIsNone(resp.data["current_responsible"])

    def test_duplicate_asset_conflict(self):
        self._create_notebook()
        resp = self._create_notebook()
        self.assertEqual(resp.status_code, 409)

    def test_list_requires_authentication(self):
        anon = APIClient()
        resp = anon.get("/api/notebooks/")
        self.assertEqual(resp.status_code, 401)

    def test_update_brand(self):
        self._create_notebook()
        resp = self.client.put("/api/notebooks/NOTE0001/", {"brand": "Dell Inc"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["brand"], "Dell Inc")

    def test_cannot_set_em_uso_via_put(self):
        self._create_notebook()
        resp = self.client.put("/api/notebooks/NOTE0001/", {"status": "EM_USO"}, format="json")
        self.assertEqual(resp.status_code, 422)

    def test_get_unknown_asset_404(self):
        resp = self.client.get("/api/notebooks/NOPE9999/")
        self.assertEqual(resp.status_code, 404)

    def test_soft_delete_sets_inativo(self):
        self._create_notebook()
        resp = self.client.delete("/api/notebooks/NOTE0001/")
        self.assertEqual(resp.status_code, 204)

        get_resp = self.client.get("/api/notebooks/NOTE0001/")
        self.assertEqual(get_resp.data["status"], "INATIVO")


class NotebookSummaryTests(MongoAPITestCase):
    def setUp(self):
        super().setUp()
        self.operator, self.token = self.register_and_login()

    def _create_notebook(self, asset, **overrides):
        payload = {
            "asset": asset,
            "brand": "Dell",
            "model": "Latitude 5420",
            "serial_number": f"SN-{asset}",
            **overrides,
        }
        return self.client.post("/api/notebooks/", payload, format="json")

    def test_summary_counts_by_status(self):
        self._create_notebook("NOTE0001")
        self._create_notebook("NOTE0002")
        self._create_notebook("NOTE0003")
        self.client.put("/api/notebooks/NOTE0003/", {"status": "MANUTENCAO"}, format="json")

        resp = self.client.get("/api/notebooks/summary/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["EM_ESTOQUE"], 2)
        self.assertEqual(resp.data["MANUTENCAO"], 1)
        self.assertEqual(resp.data["EM_USO"], 0)
        self.assertEqual(resp.data["INATIVO"], 0)
        self.assertEqual(resp.data["total"], 3)

    def test_summary_requires_authentication(self):
        anon = APIClient()
        resp = anon.get("/api/notebooks/summary/")
        self.assertEqual(resp.status_code, 401)

    def test_summary_asset_named_summary_does_not_collide(self):
        """Garante que a rota fixa /summary/ tem prioridade sobre
        /<asset>/ mesmo se alguém cadastrar um notebook chamado 'summary'."""
        create_resp = self._create_notebook("summary")
        self.assertEqual(create_resp.status_code, 201)

        resp = self.client.get("/api/notebooks/summary/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("total", resp.data)


class CheckoutReturnHistoryTests(MongoAPITestCase):
    def setUp(self):
        super().setUp()
        self.operator, self.operator_token = self.register_and_login(
            email="operador@example.com", name="Operador"
        )

        employee_resp = self.client.post(
            "/api/users/",
            {
                "name": "Funcionario Teste",
                "email": "funcionario@example.com",
                "department": "Vendas",
                "password": "senha123456",
            },
            format="json",
        )
        self.employee = employee_resp.data

        self.client.post(
            "/api/notebooks/",
            {
                "asset": "NOTE0001",
                "brand": "Dell",
                "model": "Latitude 5420",
                "serial_number": "SN123",
            },
            format="json",
        )

    def _checkout(self, **overrides):
        payload = {"user_id": self.employee["id"], **overrides}
        return self.client.post("/api/notebooks/NOTE0001/checkout/", payload, format="json")

    def _return(self, **payload):
        return self.client.post("/api/notebooks/NOTE0001/return/", payload, format="json")

    def test_checkout_success_sets_em_uso_and_responsible(self):
        resp = self._checkout(observation="uso remoto")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "EM_USO")
        self.assertEqual(resp.data["current_responsible"]["user_id"], self.employee["id"])

    def test_checkout_creates_retirada_movement_with_dual_traceability(self):
        self._checkout()
        history = self.client.get("/api/notebooks/NOTE0001/history/")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.data), 1)

        movement = history.data[0]
        self.assertEqual(movement["type"], "RETIRADA")
        self.assertEqual(movement["responsible"]["user_id"], self.employee["id"])
        self.assertEqual(movement["performed_by"]["user_id"], self.operator["id"])

    def test_checkout_twice_fails(self):
        self._checkout()
        resp = self._checkout()
        self.assertEqual(resp.status_code, 422)

    def test_checkout_unknown_user_404(self):
        resp = self._checkout(user_id="000000000000000000000000")
        self.assertEqual(resp.status_code, 404)

    def test_checkout_inactive_user_fails(self):
        inactive = self.client.post(
            "/api/users/",
            {
                "name": "Inativo",
                "email": "inativo@example.com",
                "department": "TI",
                "password": "senha123456",
                "active": False,
            },
            format="json",
        )
        resp = self._checkout(user_id=inactive.data["id"])
        self.assertEqual(resp.status_code, 422)

    def test_return_bom_sets_em_estoque_and_clears_responsible(self):
        self._checkout()
        resp = self._return(condition="BOM", observation="tudo certo")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "EM_ESTOQUE")
        self.assertIsNone(resp.data["current_responsible"])

    def test_return_creates_devolucao_movement_with_dual_traceability(self):
        self._checkout()
        self._return(condition="BOM")

        history = self.client.get("/api/notebooks/NOTE0001/history/")
        self.assertEqual(len(history.data), 2)

        devolucao = history.data[0]  # mais recente primeiro
        self.assertEqual(devolucao["type"], "DEVOLUCAO")
        self.assertEqual(devolucao["returned_by"]["user_id"], self.employee["id"])
        self.assertEqual(devolucao["received_by"]["user_id"], self.operator["id"])

    def test_return_avaria_sets_manutencao(self):
        self._checkout()
        resp = self._return(condition="AVARIA")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "MANUTENCAO")

    def test_return_without_checkout_fails(self):
        resp = self._return()
        self.assertEqual(resp.status_code, 422)

    def test_history_not_found_for_unknown_asset(self):
        resp = self.client.get("/api/notebooks/NOPE9999/history/")
        self.assertEqual(resp.status_code, 404)

    def test_history_requires_authentication(self):
        anon = APIClient()
        resp = anon.get("/api/notebooks/NOTE0001/history/")
        self.assertEqual(resp.status_code, 401)
