from __future__ import annotations
from typing import TYPE_CHECKING
from Projeto_xirico.exc import PermissionDeniedError, CredentialsError
import logging


if TYPE_CHECKING:
    from Projeto_xirico.repositories.operator_repository import OperatorRepository
    from Projeto_xirico.segurança import Autententicacao,  Auditoria
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.notifications import     NotificatorEmail
    from Projeto_xirico.schemes.operator_scheme import OperatorRegist
    
    

logger=logging.getLogger(__name__)

        
class RegistNewOperator:
    def __init__(
        self,
        repo: OperatorRepository,
        auth:Autententicacao,
        notificator: NotificatorEmail,
        profile: Profile,
        audit: Auditoria
        ):
        self._repo= repo
        self._auth= auth
        self._notificator= notificator
        self._profile= profile
        self._audit= audit
        
        
    def execute(dados:OperatorRegist, otp: str):
        """
           
        Registers a new operator in the system.
    
        This method performs the complete registration workflow:
        1. Verifies that the current operator has ADMIN privileges.
        2. Ensures that the provided operator data (email, username, etc.) are unique.
        3. Validates the one‑time password (OTP) sent to the new operator's email.
        4. Persists the new operator record in the repository.
        5. Logs the operation in the audit trail.
        6. Sends a welcome email to the new operator (non‑critical; failures are logged).
    
        Args:
            dados (OperatorRegist): Pydantic model containing the new operator's data
                (e.g., name, email, username, role, etc.).
            otp (str): 8‑digit code previously emailed to the new operator for identity
                verification.
    
        Returns:
            int: The unique identifier (ID) assigned to the newly registered operator.
    
        Raises:
            PermissionDeniedError: If the current operator is not an ADMIN.
            DuplicateError: If any of the provided data (email/username) already exists.
            InvalidOtpError: If the OTP does not match the expected value.
            ExpiredOtpError: If the OTP has expired (time window exceeded).
            AttemptsExcededError: If the OTP has been entered incorrectly more than
                the allowed number of times.
    
        Notes:
            - The OTP verification and uniqueness checks are delegated to the `auth`
              and `repo` dependencies, which raise the appropriate exceptions.
            - Email notification failures are caught and logged as warnings; they do
              not block the registration process.
            - All operations are audited for traceability.
    
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
        