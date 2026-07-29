from __future__ import TYPECHECKING
from typing import anotation
if TYPECHECKING:
    from Projeto_xirico.seguranca import Auditoria
    from Projeto_xirico.profile import Profile
    from Pojeto_xirico.repositories.operator_repository import OperatorRepository

class ListActiveOperators:
    def __init__(self, repo: OperatorRepository, profile: Profile, audit: Auditoria):   
        self._repo= self._repo
        self._profile= self._profile
        self._audit= audit
    

    def execute(self):
        all_=self._repo.search_all()
        self._audit.auditar(
            operador= self._profile.id,
            operacao= "list_active_operators",
        )
        return all_