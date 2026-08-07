from __future__ import annotations
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
from Projeto_xirico.exc import PermissionDeniedError
logger= logging.getLogger(__name__)


class SearchByID:
    def __init__(
        self,
        profile: Profile,
        repo: OperatorRepository,
        audit: Auditoria 
    ):
        self._profile= profile
        self._repo= repo
        self._audit= audit
    

    def execute(self, id: int) -> dict:
        if not self._profile.ADM:
            raise PermissionDeniedError("metodo de pesquisa exclusivo a ADMs")
        operator= self._repo.search_id(id)
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= "search_by_id",
                detalhes= f"pesquisou pelo operador com id {id}"
            )
        except Exception:
            logger.warning('falha no registro de auditoria', exc_info= True)
        return operator