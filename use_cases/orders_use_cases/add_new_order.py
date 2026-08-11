from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class AddNewOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= Profile
        self._audit= audit


    def execute(self, dados: dict) -> str:
        id= self._repo.insert(dados)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'add_new_order',
            detalhes= f'adicionou o pedido id: {id}'
        )
        return id
    