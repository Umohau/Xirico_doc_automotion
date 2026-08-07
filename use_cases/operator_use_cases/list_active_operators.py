from __future__ import annotations
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.profile import Profile
    from Pojeto_xirico.repositories.operator_repository import OperatorRepository
logger= logging.getLogger(__name__)

class ListActiveOperators:
    def __init__(self, repo: OperatorRepository, profile: Profile, audit: Auditoria):   
        self._repo= repo
        self._profile= profile
        self._audit= audit
    

    def execute(self):
        all_=self._repo.search_all()
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= "list_active_operators",
            )
        except Exception:
            logger.warning("falha no registro de auditoria", exc_info= True)
        return all_