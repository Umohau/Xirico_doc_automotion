import logging
import os
from dotenv import load_dotenv

#pega o nivel do logging
load_dotenv("config.env")
log_level_str= os.getenv("LOG_LEVEL", "DEBUG")
log_level= getattr(logging, log_level_str)

#configura o logging
logger= logging.getLogger(__name__)
logging.basicConfig(
    format= "%(levelname)s: %(name)s: %(message)s: %(asctime)s",
    datefmt="%H:%M",
    level= log_level
)


class Perfil:
    def __init__(self, sessao, repo_operador, autenticador, auditoria):
        self._id=sessao.id
        self._repo_operador=repo_operador
        self._autenticador= autenticador
        self._auditoria= auditoria
        self._dados_cache=None
        self._operador=self._obter_dados()
    @property
    def nome(self) ->str:
        return self._operador.get("nome")


    @property
    def id(self) -> int:
        """
        Obtem o id do operador logado.
        """
        return self._id
            
    @property
    def ADM(self) -> bool:
        return self._operador.get("ADM")
        

    @property
    def email(self) -> str:
        return self._operador.get("email")
        
        
    @property
    def telefone(self) -> str:
        return self._operador.get("telefone")


    @property
    def estado(self) -> bool:
        return self._operador.get("ativo")
        


    def _obter_dados(self):
        if  self._dados_cache is None:
            self._dados_cache= self._repo_operador.buscar_id(self.id)
        return self._dados_cache
        
        
    def editar_nome(self, nome:str)->None:
        """
        Edita o nome do operador, um operador so pode editar seu proprio nome.
        
        Args:
            nome(str): nome editado (ou novo nome).
            
        Returns:
            None
        """
        dado={"nome": nome}
        logger.debug("editando nome")
        self._repo_operador.actualizar(self.id, dado)
        self._dados_cache=None
        self._auditoria.auditar(
            self.id,
            "editar nome",
            "editou seu nome de perfil")
        logger.info("sucesso: nome editado")
        
        
    def mudar_email(self, email:str, codigo:str)->None:
        """
        Altera o endereço de email do operador
         exige vericacao do actual e do novo email por otp.
         
         Args:
             email(str): novo endereco de email
             codigo(str): codigo otp enviado  ao email actual.
            
        Retunrs:
            None
            
        Raises:
            InvalidOtpError:
                Se o codigo fornecido estiver errado.
        """
        dado={"email":email}
        logger.debug("alterando email")
        if self._autenticador.verificar_otp(codigo):
            self._repo_operador.actualizar(self.id, dado)
            self._dados_cache=None
            self._auditoria.auditar(
                self.id,
                "mudar_email",
                "alterou o seu email")
            logger.debug("sucesso: email alterado")
        
        
        
    def trocar_telefone(self, telefone:str, codigo:str) ->None:
        """
        Troca o numero telefonico do operador.
        Exige verificacao de identidade por otp.
        
        Ags:
            telefone(str): novo numero telefonico.
            codigo(str): codigo otp enviado ao telefone actual.
            
        Returns:
            None
            
        Raises:
            InvalidOtpError: se o codigo otp estiver errado.
        """
        dado={"telefone": telefone}
        logger.debug("actualizando numero telefonico")
        if self._autenticador.verificar_otp(codigo):
            self._repo_operador.actualizar(self.id, dado)
            self._dados_cache=None
            self._auditoria.auditar(
                self.id,
                "trocar_telefone",
                "alterou seu telefone")
            