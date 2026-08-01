from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class RecoveryClient:
    def __init__(
            self,
            repo: ClientRepository,
            profile: Profile,
            audit: Auditoria
        ):
        self._repo= self._repo
        self._profile= profile
        self._audit= audit


    def execute(self, email: str) -> int:
        effect= self._repo.reactivate(email)
        id= self._repo.search_email(email).get('id')
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'recovery_client',
            detalhes= 'recuperou o cliente com id {id}'
        )
        return id