from __future__ import annotations
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from Projeto_xirico.repositories.cliente_repository import ClientRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
logger= logging.getLogger(__name__)


class ListClients:
    def __init__(
        self,
        repo: ClientRepository,
        profile: Profile,
        audit: Auditoria
    ):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self):
        clients= self._repo.search_all()
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= 'list_clients'
            )
        except Exception:
            logger.warning('falha ao auditar accao', exc_info= True)
        return clients