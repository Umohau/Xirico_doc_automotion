from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from ...DTOs.operator_DTOs import OperatorGetResponse, OperatorGetByAdmResponse
if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria
logger= logging.getLogger(__name__)


class SearchByName:
    def __init__(
            self,
            profile: Profile,
            repo: OperatorRepository,
            audit: Auditoria
        ):
        self._profile= profile
        self._repo= repo
        self._audit= audit


    def execute(self, name: str) -> list[dict]:
        operators= self._repo.search_name(name)
        operator_dto= list()
        try:
            self._audit.auditar(
                operador= self._profile.id,
                operacao= "search by name",
                detalhes= f"pesquisou por um nome similar a {name}"
            )
        except Exception:
            logger.warning("falha no registo  de auditoria", exc_info= True)
        logger.debug('convertendo resultados para DTOS')
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
    