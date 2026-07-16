from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.exc import PermissionDeniedError, CredentialsError
import logging


if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.segurança import Autententicacao,  Auditoria
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.notifications import     NotificatorEmail
    from Projeto_xirico.schemes.operator_scheme import dados:OperatorRegist
    
    

logger=logging.getLogger(__name__)

        
class RegistNewOperator:
    def __init__(
        self,
        repo: OperatorRepository,
        auth:Autententicacao,
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
        """
        Registra um novo operador no sitema.
        Args:
            dados: dados do novo operador a registrar
            otp: codigo de 8 digitos enviado ao novo operador por email para confirmar identidade.
        Returns:
            id do operador recem registrado
            
        Raises:
            PermissionDeniedError: se operador nao for ADM
            DuplicateError: se o os dados do novo operador, ja estiverem cadastrados
            InvalidOtpError:se o otp estiver errado.
            ExpiredOtpError: se o otp estiver expirado
            AttemptsExcededError: se exceder 3 tentativas(passar o otp errado 3 vezes)
            
        Note: A maioria das excecoes sao levantadas pelos proprios metodos de verificacao.
        """
        dados_=dados.model_dump()
        if not self._profile.ADM:
            raise PermissionDeniedError("nao operadores nao podem registrar novos operadores")
        self._repo.check_unique(dados_) #verifica a unicidade dos dados
        self._auth.verificar_otp(otp) #verifica o codigo otp
        id_gerado= self._repo.insert(dados_) #persiste os dados no repositorio
        self._audit.auditar(
            operador= self._profile.id,
            operacao= "regist new operator",
            detalhes= f"registou  um operador com o id {id_gerado}")
        try:
        self._notificator.notify_operator(
            destino= dados.email,
            titulo= "Bem vindo(a)",
            msg= "seu registro como operador na xirico foi efectuado com sucesso.\nAcesse a sua conta e comece a operar")
        except CredentialsError:
            pass
        except Exception as e:
            logger.warning("falha no envio de email", exc_info=True)
        return id_gerado
        