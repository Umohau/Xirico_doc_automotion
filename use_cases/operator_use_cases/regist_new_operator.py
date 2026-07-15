from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.exc import PermissionDeniedError

if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.segurança import Autententicacao,  Auditoria
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.notifications import     NotificatorEmail
    
class RegistNewOperator:
    def __init__(
        self,
        repo: OperatorRepository,
        auth= Autententicacao,
        notificator: NotificatorEmail,
        profile: Profile,
        audit: Auditoria
        )
        self._repo= repo
        self._auth= auth
        self._notificator= notificator
        self._profile= profile
        self._audit= audit
        
        
    def execute(dados:OperatorRegist, otp: str):
        dados_=dados.model_dump()
        if not self._profile.ADM:
            raise PermissionDeniedError("nao operadores nao podem registrar novos operadores")
        self._repo.check_unique(dados_) #verifica a unicidade dos dados
        self.auth.verificar_otp(otp) #verifica o codigo otp
        id_gerado= self._repo.insert(dados_) #persiste os dados no repositorio
        self._audit.auditar(
            operador= self._profilel.id,
            operacao= "regist new operator",
            detalhes= f"registou  um operador com o id {id_gerado}")
        self._notificator.notify_operator(
            destino= dados.email,
            titulo= "Bem vindo(a)",
            msg= "seu registro como operador na xirico foi efectuado com sucesso.\nAcesse a sua conta e comece a operar")
        
        