from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.repositories.orders_repository import OrdersRepository
from Projeto_xirico.profile import Profile
from Projeto_xirico.seguranca import Auditoria

class DeleteOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(order_id: str) -> 
        