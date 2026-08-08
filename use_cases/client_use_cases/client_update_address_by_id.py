from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class ClientUpdateAdressById:
    def __init__(
            self,
            repo: ClientRepository,
            profile: Profile,
            audit: Auditoria
        ):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, client_id:int, adress: dict) -> int:
        effect= self._repo.update(dados= adress, id= client_id)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'client_update_adress_by_id',
            detalhes= f'actualizou o endereço do cliente com id {client_id}'
        )
        return effect