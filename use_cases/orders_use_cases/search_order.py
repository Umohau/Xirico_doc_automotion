from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository

class SearcbOrdersByOrderId:
    def __init__(self, repo: OrdersRepository):
        self._repo= repo


    def execute(self, order_id: str) -> list[dict]:
        return self._repo.search_oid(order_id)