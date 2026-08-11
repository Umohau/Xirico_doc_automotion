from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.shipment_repository import ShipmentRepository

class SearchShipmentByOrderId:
    def __init__(self, repo:ShipmentRepository):
        self._repo= repo


    def execute(self, order_id: str) -> dict:
        return self._repo.get_shipment_oid(order_id)


class SearchShipmentsByEpoc:
    def __init__(self, repo:ShipmentRepository):
        self._repo= repo
    
    
    def execute(self, data_inicio, data_limite) -> list[dict]:
        return self._repo.search_epoc(data_inicio= data_inicio, data_fim= data_limite)
