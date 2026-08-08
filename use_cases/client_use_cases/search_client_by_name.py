from __future__ import annotations
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
logger= logging.getLogger(__name__)


class SearchClietByName:
    def __init__(self,
        repo: ClientRepository,
        audit: Auditoria,
        profile: Profile
        ):
        self._repo= repo
        self._audit= audit
        self._profile= profile


    def execute(self, name) -> list[dict]:
        clientes= self._repo.search_name(name)
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'search_client_by_name',
                detalhes= f'termo da pesquisa: {name}'
            )
        except Exception:
            logger.warning('falha ao auditar a accao', exc_info= True)
        return clientes