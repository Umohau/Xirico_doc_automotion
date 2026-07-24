from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.exc import PermissionDeniedError


if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
    from Projeto_xirico.segurança import Auditoria
    from Projeto_xirico.profile import Profile

class DemoteOperator:
    def __init__(
        self, 
        message_box: messageBoxRepository,
        repo: OperatorRepository,
        profile: Profile,
        audit: Auditoria
        ) :
        self._message_box= message_box
        self._repo= repo
        self._profile= profile
        self._audit= audit
        
        
    def execute(self, id):
        if not self._profile.ADM:
            raise PermissionDeniedError("nao ADMs nao podem rebaixar operadores")
        operador= self._repo.search_id(id)
        effect= self._repo.update(
            dados={"ADM":False},
            id)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= "demote operator",
            detalhes= f"rebaixou o operador id: {id}")
        self._message_box.add_(
            dados={
                "to": operador.get("email"),
                "name": operador.get("nome"),
                "type": "demote",
                "channel": "email"
            }
                )
        return effect
