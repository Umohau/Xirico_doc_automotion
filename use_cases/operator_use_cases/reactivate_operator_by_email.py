from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.exc import PermissionDeniedError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
    from Projeto_xirico.segurança import Auditoria
    from Projeto_xirico.profile import Profile

class ReactivateOperatorByEmail:
    def __init__(
        self, 
        message_box: messageBoxRepository,
        repo: OperatorRepository,
        profile: Profile,
        audit: Auditoria,
        auth: Autenticacao
        ) :
        self._message_box= message_box
        self._repo= repo
        self._profile= profile
        self._audit= audit
        self._auth = auth
        
        
    def execute(self, email: str, otp: str) -> int:
        if not self._profile.ADM:
            raise PermissionDeniedError("nao ADMs nao podem reactivar operadores")
            
        self._auth.verificar_codigo(otp)
        effect= self._repo.reactivate(email)
        nome= self._repo.search_email(email).get("nome")
        self._audit.auditar(
             operador= self._profile.id,
             operacao="reactivate operator",
             detalhes= f"reactivou o operador de email {email}")
        self._message_box.add_(
           dados={
               "to": email,
               "name":nome,
               "type": 'reactivate',
               "channel": 'email'
               }
          )  
        return effect
        