"""Service: regras de negócio de `notebooks`. Não conhece MongoDB nem HTTP.

Checkout, devolução e histórico coordenam NotebookRepository +
MovementRepository (+ UserService, para resolver o funcionário no
checkout) para manter as duas collections sempre consistentes.
"""
from __future__ import annotations

from apps.core.exceptions import ConflictError, InvalidStateError, NotFoundError
from apps.core.utils import utcnow
from apps.movements.repositories import MovementRepository
from apps.notebooks.constants import (
    CONDITION_AVARIA,
    STATUS_CHOICES,
    STATUS_EM_ESTOQUE,
    STATUS_EM_USO,
    STATUS_MANUTENCAO,
    STATUSES_ALLOWED_VIA_UPDATE,
    TYPE_DEVOLUCAO,
    TYPE_RETIRADA,
)
from apps.notebooks.repositories import NotebookRepository
from apps.users.services import UserService


class NotebookService:
    def __init__(
        self,
        repository: NotebookRepository | None = None,
        movement_repository: MovementRepository | None = None,
        user_service: UserService | None = None,
    ):
        self.repository = repository or NotebookRepository()
        self.movement_repository = movement_repository or MovementRepository()
        self.user_service = user_service or UserService()

    def create_notebook(self, data: dict) -> dict:
        asset = data["asset"]
        if self.repository.exists_by_asset(asset):
            raise ConflictError(f"Já existe um notebook com o asset '{asset}'.")

        now = utcnow()
        doc = {
            "asset": asset,
            "brand": data["brand"],
            "model": data["model"],
            "serial_number": data["serial_number"],
            "status": data.get("status") or STATUS_EM_ESTOQUE,
            "current_responsible": None,
            "created_at": now,
            "updated_at": now,
        }
        return self.repository.insert(doc)

    def list_notebooks(self, status: str | None = None, search: str | None = None) -> list[dict]:
        return self.repository.list(status=status, search=search)

    def get_notebook(self, asset: str) -> dict:
        notebook = self.repository.find_by_asset(asset)
        if not notebook:
            raise NotFoundError(f"Notebook '{asset}' não encontrado.")
        return notebook

    def update_notebook(self, asset: str, data: dict) -> dict:
        notebook = self.get_notebook(asset)

        updates = {}
        for field in ("brand", "model", "serial_number"):
            if field in data:
                updates[field] = data[field]

        if "status" in data:
            new_status = data["status"]
            if new_status not in STATUSES_ALLOWED_VIA_UPDATE:
                raise InvalidStateError(
                    "O status EM_USO só pode ser definido através do endpoint de checkout."
                )
            if notebook["status"] == STATUS_EM_USO:
                raise InvalidStateError(
                    "Não é possível alterar o status de um notebook em uso; registre a devolução primeiro."
                )
            updates["status"] = new_status

        if not updates:
            return notebook

        updates["updated_at"] = utcnow()
        return self.repository.update_by_asset(asset, updates)

    def soft_delete_notebook(self, asset: str) -> dict:
        """DELETE nunca remove o documento: apenas move o notebook para INATIVO."""
        notebook = self.get_notebook(asset)
        if notebook["status"] == STATUS_EM_USO:
            raise InvalidStateError(
                "Não é possível descontinuar um notebook em uso; registre a devolução primeiro."
            )
        return self.repository.update_by_asset(
            asset, {"status": "INATIVO", "updated_at": utcnow()}
        )

    def checkout(self, asset: str, user_id: str, performed_by: dict, observation: str = "") -> dict:
        """Retirada: só permitida a partir de EM_ESTOQUE. Define
        current_responsible, muda o status para EM_USO e grava um
        movimento RETIRADA com responsible (funcionário) + performed_by
        (operador logado que registrou)."""
        notebook = self.get_notebook(asset)
        if notebook["status"] != STATUS_EM_ESTOQUE:
            raise InvalidStateError(
                f"Notebook '{asset}' não está em estoque (status atual: {notebook['status']})."
            )

        user = self.user_service.get_user(user_id)
        if not user.get("active", True):
            raise InvalidStateError(
                f"Usuário '{user_id}' está inativo e não pode retirar equipamentos."
            )

        responsible = {"user_id": str(user["_id"]), "name": user["name"]}
        now = utcnow()

        updated = self.repository.update_by_asset(
            asset,
            {
                "status": STATUS_EM_USO,
                "current_responsible": responsible,
                "updated_at": now,
            },
        )

        self.movement_repository.insert(
            {
                "notebook_id": str(notebook["_id"]),
                "asset": asset,
                "type": TYPE_RETIRADA,
                "responsible": responsible,
                "returned_by": None,
                "performed_by": performed_by,
                "received_by": None,
                "date": now,
                "observation": observation or "",
                "condition": None,
            }
        )
        return updated

    def return_notebook(
        self, asset: str, received_by: dict, condition: str | None = None, observation: str = ""
    ) -> dict:
        """Devolução: só permitida a partir de EM_USO. Limpa
        current_responsible, muda o status para EM_ESTOQUE (ou MANUTENCAO,
        se condition=AVARIA) e grava um movimento DEVOLUCAO com returned_by
        (o funcionário que estava com o equipamento) + received_by (operador
        logado que registrou)."""
        notebook = self.get_notebook(asset)
        if notebook["status"] != STATUS_EM_USO:
            raise InvalidStateError(
                f"Notebook '{asset}' não está em uso (status atual: {notebook['status']})."
            )

        returned_by = notebook.get("current_responsible")
        new_status = STATUS_MANUTENCAO if condition == CONDITION_AVARIA else STATUS_EM_ESTOQUE
        now = utcnow()

        updated = self.repository.update_by_asset(
            asset,
            {
                "status": new_status,
                "current_responsible": None,
                "updated_at": now,
            },
        )

        self.movement_repository.insert(
            {
                "notebook_id": str(notebook["_id"]),
                "asset": asset,
                "type": TYPE_DEVOLUCAO,
                "responsible": None,
                "returned_by": returned_by,
                "performed_by": None,
                "received_by": received_by,
                "date": now,
                "observation": observation or "",
                "condition": condition,
            }
        )
        return updated

    def get_history(self, asset: str) -> list[dict]:
        self.get_notebook(asset)  # garante 404 se o asset não existir
        return self.movement_repository.list(asset=asset)

    def get_status_summary(self) -> dict[str, int]:
        """Contagem por status para os cards do dashboard. Sempre traz as
        quatro chaves (0 quando não há nenhum notebook naquele status)."""
        counts = self.repository.count_by_status()
        summary = {status: counts.get(status, 0) for status in STATUS_CHOICES}
        summary["total"] = sum(summary.values())
        return summary
