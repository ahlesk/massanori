"""Service: leitura do histórico de `movements`.

A criação de registros (RETIRADA/DEVOLUCAO) é feita pelo NotebookService no
momento do checkout/return (Fase 2), garantindo que notebook e movimento
sejam sempre escritos de forma consistente.
"""
from __future__ import annotations

from apps.movements.repositories import MovementRepository


class MovementService:
    def __init__(self, repository: MovementRepository | None = None):
        self.repository = repository or MovementRepository()

    def list_movements(self, asset: str | None = None) -> list[dict]:
        return self.repository.list(asset=asset)
