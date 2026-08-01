from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class DeleteOperatorById:
    def __init__(
            self,
            repo: ClientRepository,
            profile: Profile,
            audit: Auditoria
        ):
        self._repo= self._repo
        self._profile= profile
        self._audit= audit

    def execute(self, id: int) -> int:
        effect= self._repo.delete(id)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'delete_operator_by_id',
            detalhes= f'deletou o cliente com id {id}'
        )
        return effect