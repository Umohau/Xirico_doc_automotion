from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrderRepository

class ListClientOrders:
    def __init__(self, repo: OrderRepository):
        self._repo= repo


    def execute(self, client_id: str) -> list[dict]:
        return self._repo.get_order_cid(client_id)