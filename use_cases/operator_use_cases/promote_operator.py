from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.exc import PermissionDeniedError


if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
    from Projeto_xirico.segurança import Auditoria
    from Projeto_xirico.profile import Profile
    
class PromoteOperator:
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
            
            
    def execute(self, id: int) -> int:
        #verifica se o operdor em sessao é ADM
        if not self._profile.ADM:
            raise PermissionDeniedError('nao ADMs nao podem promover operadores')
        operador= self._repo.search_id(id)# revupera os dados do operador a promover
        effect= self._repo.update(
            id,
            dados={"ADM": True}
            
         )# executa a promocao
        #audita a accao
        self._audit.auditar(
            operador= id,
            operacao= "Promote_operator",
            detalhes= f"promoveu a ADM o operador de id: {id}")
        #adiciona uma mensagem a caixa de mensagens para envio
        self._message_box.add_(
            dados={
                "to":operador.get("email"),
                "type":'promote',
                "name": operador.get("nome"),
                "channel": 'email'
               } )
        return effect