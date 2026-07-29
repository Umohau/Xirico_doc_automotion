from __future__ import TYPECHECKING
from typing import annotation
if TYPECHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class SearchByName:
    def __init__(
            self,
            profile: Profile,
            repo: OperatorRepository,
            audit: Auditoria
        ):
        self._profile= profile
        self._repo= repo
        self.audit= audit


    def execute(self, name: str) -> list[dict]:
        operators= self._repo.search_name(name)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= "search by name",
            detalhes= f"pesquisou por um nome similar a {name}"
        )
        return operators