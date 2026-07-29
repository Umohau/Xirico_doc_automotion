from __future__ import TYPECHECKING
from typing import annotation
from Projeto_xirico.exc import PermissionDeniedError
if TYPECHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


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
        self._audit.auditar(
            operador= self._prorile.id,
            operacao= "search_by_id",
            detalhes= f"pesquisou pelo operador com id {id}"
        )
        return operator