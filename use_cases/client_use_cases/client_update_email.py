from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class ClientUpdateEmail:
    def __init__(
            self,
            repo: ClientRepository,
            profile: Profile,
            audit: Auditoria
        ):
        self._repo= repo
        self._profile= profile
        self.audit= audit


    def execute(self, client_id: int, email: dict) -> int:
        effect= self._repo.update(dados= email, id= client_id)
        self.audit.auditar(
            operador= self._profile.id,
            operacao= 'client_update_email',
            detalhes= f'actualizou o email do cliente com id {client_id}'
        )
        return effect