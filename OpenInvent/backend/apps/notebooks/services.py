"""Service: regras de negócio de `notebooks`. Não conhece MongoDB nem HTTP.

Checkout, devolução e histórico (Fase 2) também vivem aqui, coordenando
NotebookRepository + MovementRepository para manter as duas collections
consistentes.
"""
from __future__ import annotations

from apps.core.exceptions import ConflictError, InvalidStateError, NotFoundError
from apps.core.utils import utcnow
from apps.notebooks.constants import STATUS_EM_ESTOQUE, STATUS_EM_USO, STATUSES_ALLOWED_VIA_UPDATE
from apps.notebooks.repositories import NotebookRepository


class NotebookService:
    def __init__(self, repository: NotebookRepository | None = None):
        self.repository = repository or NotebookRepository()

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
