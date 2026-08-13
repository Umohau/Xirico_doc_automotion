from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from Projeto_xirico.DTOs.operator_DTOs import OperatorGetByAdmResponse, OperatorGetResponse
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
        operators=self._repo.search_all()
        operator_dto= list()
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= "list_active_operators",
            )
        except Exception:
            logger.warning("falha no registro de auditoria", exc_info= True)

        for operator in operators:
            if operator.get('ADM') == True:
                roll= 'ADM'
            else:
                roll= 'operator'
            if self._profile.ADM:
                operator_dto.append(
                    OperatorGetByAdmResponse(
                    id= operator['id'],
                    name= operator['nome'],
                    roll= roll,
                    email= operator['email'],
                    telephone= operator['telefone'],
                    adress= operator['endereco'],
                    BI= operator['identificacao']
                    )
                )
            else:
                operator_dto.append(
                    OperatorGetResponse(
                    id= operator['id'],
                    name= operator['nome'],
                    roll= roll
                    )
                )


        return operator_dto