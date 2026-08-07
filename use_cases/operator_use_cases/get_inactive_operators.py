from __future__ import annotations
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
logger= logging.getLogger(__name__)
 
class GetInactiveOperators:
    def __init__(
        self,
        repo: OperatorRepository,
        profile: Profile,
        audit: Auditoria,
        ):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self):
        inactives= self._repo.search_inactive()
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= "get_inactive_operators",
                detalhes= "pesquisou por todos operadores inactivos"
            )
        except Exception:
            logger.warning("falha no registro de auditoria", exc_info= True)
        return inactives
    