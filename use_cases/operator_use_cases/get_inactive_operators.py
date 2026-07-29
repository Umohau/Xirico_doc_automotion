from __future__ import TYPECHECKING
from typing import annotation
if TYPECHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


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
        inactives= self._repo.search_inactive
        self._audit.auditar(
            operador= self._profile.id,
            operacao= "get_inactive_operators",
            detalhes= "pesquisou por todos operadores inactivos"
        )
        return inactives
    