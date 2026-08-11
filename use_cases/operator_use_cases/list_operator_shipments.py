from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.shipment_repository import ShipmentRepository

class ListOperatorShipments:
    def __init__(self, repo:ShipmentRepository):
        self._repo= repo


    def execute(self, operator_id: str) -> list[dict]:
        return self._repo.get_shipment_gid(operator_id)