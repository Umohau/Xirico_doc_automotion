from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class RegistNEwClient:
    def __init__(self,
        repo: ClientRepository,
        audit: Auditoria,
        profile: Profile
        ):
        self._repo= repo
        self._audit= audit
        self._profile= profile


    def execute(self, dados: dict) -> int:
        self._repo.check_unique(dados)
        id_gerado= self._repo.insert(dados)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'regist_new_client',
            detalhes= f"registou o cliente com id {id_gerado}"
        )
        return id_gerado