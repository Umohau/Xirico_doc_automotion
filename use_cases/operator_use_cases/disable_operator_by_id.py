from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.exc import PermissionDeniedError


if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository, messageBox_repository
    from Projeto_xirico.segurança import Autententicacao,  Auditoria
    from Projeto_xirico.profile import Profile


class DisableOperatorByID:
     def __init__(
        self,
        repo: OperatorRepository,
        message_box: messageBoxRepository,
        profile: Profile,
        audit: Auditoria
        ):
        self._repo= repo
        self._message_box= message_box
        self._profile= profile
        self._audit= audit
        
        
    def execute(self, id: int) -> int:
        if not self._profile.ADM:
            raise PermissionDeniedError("nao ADMs nao podem desativar_operadores")
        
        operador= self._repo.search_id(id)
        #executa e armazena o numero de deletados
        efeito= self._repo.delete(id) 
        #audita a accao
        self._audit(
            operador= self._profile.id,
            operacao= "disable operator",
            detalhes= f'desativou o operador id {id}')
        #adiciona uma mensagem de notificacao na caixa para envio
        self._message_box.add_(
            dados={
                "to": operador.get('email'),
                "type": 'Disable',
                "name": operador.get('nome'),
                "channel": 'email'
               } )
        return efeito