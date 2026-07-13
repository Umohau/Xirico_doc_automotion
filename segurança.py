import bcrypt
import sys
import os
import json
import jwt
import logging
import secrets
import keyring
import time
from dotenv import load_dotenv
from pathlib import Path
from keyrings.alt.file import PlaintextKeyring #para testes em desenvolvimento
from datetime import datetime, timezone, timedelta
from Projeto_xirico.exc import AttemptsExcedError, InvalidOtpError, ExpiredOtpError, CredentialsError, EntityNotFoundError

BASE= os.path.dirname(__file__)
load_dotenv(BASE/Path("config.env")) #carrega o env com as definicoes


logger= logging.getLogger(__name__)

if os.getenv("ENV") == "devolopment":
    keyring.set_keyring(PlaintextKeyring()) # para testes durante desenvolvimento



class SenhaMixIn:
    @staticmethod
    def hashear(senha: str) -> bytes:
        """
        Create a salted hash of the password provided in the `senha` argument.

        Args:
            senha (str): Password to be hashed.
        
        Returns:
            bytes: The password hash with salt, as bytes.
        """
        pin= senha.encode("utf-8")
        senha_hasheada= bcrypt.hashpw(pin, bcrypt.gensalt())
        return senha_hasheada
     
           
    @staticmethod
    def verificar_senha(senha: str, senha_armazenada: bytes)-> bool:
        """
        Extract the salt and compare the provided password in the `senha` argument with the stored hash.

        Args:
            senha (str): Password to be verified.
            senha_armazenada (bytes): Comparison password (stored hashed password).
        
        Returns:
            bool: True if the passwords match. False otherwise.
        """
        pin= senha.encode("utf-8")
        return bcrypt.checkpw(pin, senha_armazenada)


class Auditoria:
    def __init__(self):
        self._nome=f"registro_{datetime.now().strftime('%d_%m_%Y')}.jsonl"
        self._base= self.localizar_app()
        self._arquivo=self._base/"aud"/self._nome
        
    def localizar_app(self):
        """
       Get the base directory or path where the program is running.

        Returns:
        Path: The absolute path where the program is running, as a Path object.
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).parent
        
        
    def auditar(self, operador:int, operacao:str, detalhes='') -> None:
        """
        Log the operation with the operator ID, executed action, operation details, and timestamp in a JSON Lines file.

        Args:
            operador (int): ID of the operator performing the logged operation.
            operacao (str): Name of the executed operation.
            detalhes (str): Details of the executed operation.
        
        Returns:
            None
        """
        dados= {
            "operador_id":operador,
            "operacao": operacao,
            "detalhes_operacao": detalhes,
            "timestamp": datetime.now().strftime("%d_%m_%YT%H:%M:%S")
        }
        
        try:
            with open(self._arquivo, "x", encoding="utf-8") as registro:
                json.dump(dados , registro)
                registro.write("\n")
        except FileExistsError:
            with open(self._arquivo, "a", encoding= "utf-8") as registro:
                json.dump(dados, registro)
                registro.write("\n")
        
                
    def historico_hoje(self, operador_id)->list[dict]:
        """
        Fetch today's operation history for a specified operator by ID.

        Args:
            operador_id (int): ID of the target operator.
        
        Returns:
            list[dict]: A list of dictionaries containing the data for each operation.
        """
        historico=list()
        with open(self._arquivo, "r", encoding="utf-8") as arquivo:
                for linha in arquivo:
                    if linha.strip():
                        registros=json.loads(linha)
                        if registros["operador_id"]==operador_id:
                            historico.append(registros)
        return historico
        

    def historico_diario(self, operador_id,data:str ) -> list[dict] :
        """
        Retrieve the history of an operator for a provided date.
        
        Args:
            operador_id (int): ID of the target operator.
            data (str): Date for which the history is requested.
        
        Returns:
            list[dict]: A list of dictionaries containing the operation data for the operator on the specified date.
            Returns an empty list if the operator has no operations.
        
        Raises:
            FileNotFoundError: If no log file exists for the provided date.
            EntityNotFoundError: If no operation records are found for the provided operator on the given date.
        """
        historico=list()
        ficheiro= self._base/"aud"/f"registro_{data}.jsonl"
        
        with open(ficheiro, "r", encoding="utf-8") as  arquivo:
            for linha in arquivo:
                if linha.strip():
                    registro= json.loads(linha)
                    if registro.get("operador_id")==operador_id:
                        historico.append(registro)
        if len(historico)==0:
            logger.info("sem registros do operador id:%d para a data %s", operador_id, data)
            raise EntityNotFoundError(f"registros nao encontrados para id {operador_id}")
        return historico


class OtpMixIn:
    def __init__(self):
        self._otp= None
        self.__tentativas=0
             
    def gerar_otp(self):
        """
        Generate an 8-digit OTP valid for 5 minutes, and store the code hash in the instance.

        Returns:
            str: The generated 8-digit code.
        """
        logger.debug("gerando otp")
        self.__tentativas=0
        codigo= "".join(secrets.choice("1234567890") for _ in range(8))
        otp=bcrypt.hashpw(codigo.encode("utf-8"), bcrypt.gensalt())
        exp=time.time() +300
        self._otp={"otp":otp, "exp":exp}
        logger.debug('sucesso: otp gerado')
        return codigo
        
        
    @property
    def status_(self):
        if self._otp != None:
            if time.time() > self._otp.get("exp"):
                return "expired"
            
            elif time.time() < self._otp.get("exp"):
                return "pending"
        return "No OTP"
        

    def verificar_otp(self, codigo: str) -> bool:
        """
        Verify whether the OTP provided by the user is valid.

        Args:
            codigo (str): OTP provided by the user.
        
        Returns:
            bool: True if the OTP is valid (matches correctly).
        
        Raises:
            ExpiredOtpError: If the OTP has expired (5-minute validity period).
            AttemptExcedError: If the attempt limit has been exceeded (3 attempts).
            InvalidOtpError: If the OTP is incorrect.
            AttributeError: If no OTP has been generated beforehand.
        """
        logger.debug("cheking otp")
        if self.status_ == "expired":
             logger.debug("invalid otp")
             raise ExpiredOtpError('Validation code expired.')
             
        compativel= bcrypt.checkpw(codigo.encode("utf-8"), self._otp.get("otp"))
        if compativel:
             self.__tentativas=0
             self._otp=None
             logger.debug("otp valido")
             return compativel
        else:
            logger.debug('Incorrect OTP code.')
            self.__tentativas+=1
            if self.__tentativas >=3:
                self._otp=None
                raise AttemptsExcedError('Attempt limit exceeded.')
            raise InvalidOtpError('Invalid OTP. Please check it.')
            
            
    
class Autenticacao(SenhaMixIn, OtpMixIn):
    def __init__(self):
        # chave de 32 bytes usada para assinar e descodificar o token.
        self._chave_jwt=self._pegar_chave_jwt().encode("utf-8")
    
    def _pegar_chave_jwt(self):
        """
        Retrieve the token key from the system keychain if it already exists. If it does not exist, generate a new one and save it.

        Returns:
            bytes: 32-byte key.
        
        Raises:
            CredentialsError: If the service and key credentials are incomplete.
        """ 
        servico= os.getenv("SERVICO")
        key=os.getenv("KEY_JWT")
        if not servico or not key:
            logger.critical('Failed to retrieve or create JWT key: incomplete credentials.')
            raise CredentialsError('Token signing key credentials incomplete.')
        logger.debug('Fetching JWT key.')
        chave= keyring.get_password(servico, key)
        if not chave:
            logger.debug('Key not found.')
            logger.debug('Generating new unique key.')
            chave= secrets.token_urlsafe(32)
            keyring.set_password(servico, key, chave)
            logger.debug('Success: key generated and stored.')
        return chave
        
    def gerar_token(self, carga:dict) -> str:
        """
        Generate an access token for the authenticated user.

        Args:
            carga (dict): Dictionary containing the data to be loaded into the token:
                operator ID, ADM status, operator name, email, phone, and status.
        
        Returns:
            str: The generated token.
        """
        #define a emissao e o prazo para o token
        IAT=int(time.time())
        EXP=int(IAT+ 30)
        carga["iat"]=IAT
        carga["exp"]=EXP
        
        logger.debug('Generating token.')
        token_gerado= jwt.encode(carga, self._chave_jwt, algorithm="HS256")
        logger.debug('Success: token generated.')
        return token_gerado


    def descodificar_token(self,token:str) -> dict:
        """
        Decode the provided token.

        Args:
            token (str): Token to be decoded.
        
        Returns:
            dict: Dictionary containing the token data.
        
        Raises:
            InvalidSignatureError: If the token signature (JWT key) is invalid.
            ExpiredSignatureError: If the token has expired.
        """
        try:
            logger.debug('Decoding token.')
            return jwt.decode(token, self._chave_jwt, algorithms=["HS256"])
        except jwt.exceptions.InvalidTokenError as e:
            logger.warning('Invalid token, E: %s',str(e))
            raise  
            
            
    def guardar_token(self, nome_usuario:str, token: str ) -> None:
        """
        Securely store the token in the operating system's password manager using the keyring library.

        Args:
            nome_usuario (str): Username for the token (it is recommended to use the email address to ensure uniqueness).
            token (str): Token to be stored.
        
        Returns:
            None
        
        Raises:
            InitError: If the keyring is unavailable.
            PasswordSetError: If the token cannot be stored in the keyring.
            CredentialsError: If the SERVICO environment variable is not set or is None.
        """
        servico=os.getenv("SERVICO")
        if not servico:
            logger.critical('Failed to retrieve credential <service>')
            raise CredentialsError('Failed to retrieve credential <service>')
        try:
            logger.debug('Saving token.')
            keyring.set_password(servico, nome_usuario, token)
            logger.debug('Success: token saved.')
            return None
        except keyring.errors.InitError as e:
            logger.error('Error: failed to save token - keyring unavailable. Error: %s', str(e))
            raise
        except keyring.errors.PasswordSetError as e:
            logger.error('Error: failed to save token - keyring unavailable. Error: %s', str(e))
            raise
            
            
    def pegar_token(self, nome_usuario:str) -> str:
        """
        Retrieve the token stored in the system's password manager.

        Args:
            nome_usuario (str): Username of the token to be retrieved.
        
        Returns:
            str: The token retrieved from the password manager.
        
        Raises:
            InitError: If the password manager is unavailable.
            PasswordGetError: If access to the token fails.
            
        """
        servico=os.getenv("SERVICO")
        try:
            logger.debug('Loading token.')
            return keyring.get_password(servico, nome_usuario)
        except keyring.errors.InitError as e:
            logger.error('Error: failed to get token - keyring unavailable. Error: %s', str(e))
            raise
        except keyring.errors.PasswordGetError as e:
            logger.error('Error: failed to get token - access failed. Error: %s', str(e))
            raise

    

class GestorDeSessao:
    def __init__(self, autenticador:Autenticacao):
        self.auth= autenticador
        self._token=None
        self._id=None
        
        
    def iniciar_sessao(self, token:str) -> None:
        self._token=token
        self._id=self.auth.descodificar_token(token).get("id")
        
    @property
    def token(self):
        return self._token
        
              
    @property
    def id(self):
        return self._id
        
    def terminar_sessao(self):
        self._token=None
        self._id=None
 