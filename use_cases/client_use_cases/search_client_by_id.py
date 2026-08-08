from __future__ import annotations
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
logger= logging.getLogger(__name__)

class SearchClientById:
    def __init__(self,
        repo: ClientRepository,
        audit: Auditoria,
        profile: Profile
        ):
        self._repo= repo
        self._audit= audit
        self._profile= profile


    def execute(self, client_id: int) -> dict:
        cliente= self._repo.search_by_id(client_id)
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'search_client_by_id',
                detalhes= f'pesquisou pelo id {id}'
            )
        except Exception :
            logger.warning('falha ao auditar uma accao ')
        return cliente