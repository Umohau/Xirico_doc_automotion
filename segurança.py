import bcrypt
import sys
import json
from pathlib import Path
from datetime import datetime


class SegSenha:
    @staticmethod
    def hashear(senha: str) -> bytes:
        """
        Cria um hash e salt da senha fornecoda no argumento senha.
        
        Args:
            senha(str): senha a ser hasheada.
            
        Returns:
            bytes: retorna a senha hasheada e com salt em byte.
        """
        pin= senha.encode("utf-8")
        senha_hasheada= bcrypt.hashpw(pin, bcrypt.gensalt())
        return senha_hasheada
     
           
    @staticmethod
    def verificar(senha: str, senha_armazenada: bytes)-> bool:
        """
        Extrai o salt e compara a senha fornecida no argumento senha com a armazenada (em hash).
        
        Args:
            senha(str): senha a ser verificada.
            
            senha_armazenada(bytes): senha de comparacao(senha armazenada hasheada)
            
        Returns:
            bool: True se as senhas forem compativeis. False se nao compativeis
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
        Obtem a base ou caminho onde o programa esta rodando
        
        Returns:
            Path: o caminho absoluto onde o pregrama esta rodando em objeto Path
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).parent
        
        
    def auditar(self, operador, operacao, detalhes=''):
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
        
                
    def historico_hoje(self, operador_id):
        historico=list()
        with open(self._arquivo, "r", encoding="utf-8") as arquivo:
                for linha in arquivo:
                    if linha.strip():
                        registros=json.loads(linha)
                        if registros["operador_id"]==operador_id:
                            historico.append(registros)
        return historico
        

    def historico_diario(self, operador_id,data:str ) -> list[dict] :
        historico=list()
        ficheiro= self._base/"aud"/f"registro_{data}.jsonl"
        
        with open(ficheiro, "r", encoding="utf-8") as  arquivo:
            for linha in arquivo:
                if linha.strip():
                    registro= json.loads(linha)
                    historico.append(registro)
        return historico


#instancias globais das classes sem dependencia externa para facilitar acesso
segsenha=SegSenha() # da classe SegSenha
auditoria=Auditoria() # da classe Auditoria

class Autenticacao:
    def gerar_token(self, operador_id: int, adm: bool) -> str:
        """
        Gera um token de acesso para o usuario autenticado.
        
        Args:
            operador_id(int): id do operador logado.
            adm(bool): define a categoria do operador.
            
        Returns:
            str: o token gerado
        """
        carga_util={
            "id_operador": operador_id,
            "ADM":adm,
            "iat":IAT,
            "exp":EXP}
        logger.debug("gerando token")
        return jwt.encode(carga_util, CHAVE_SECRETA, algorithm="HS256")


    def descodificar_token(token:str, chave:bytes, ) -> dict:
        """
        Descodifica o token  fornecido.
        
        Args:
            token(str): token a descodificar.
            chave(bytes): chave do token.
            
        Returns:
            dict: dicionario com os dados do token.
            
        Raises:
            InvalidTokenError: se o token for invalido(assinatura invalida, token expirado ou outro que invalide o token)
        """
        try:
            logger.debug("descodificando token")
            return jwt.decode(token, chave, algorithms=["HS256"])
        except InvalidTokenError as e:
            logger.warning("token invalido")
            raise  
            
            
    def guardar_token(nome_usuario:str, token: str ) -> None:
        """
        Armazena o token  de forma segura  no gerenciador de senhas do sistema operacional usando  bibliotec keyring.
        
        Args:
            nome_usuario(str): nome do usuario do token.
            token(str): token a ser armazenado.
            
        Returns:
            None
            
        Raises:
            InitError: se o chaveiro estiver indisponivel.
            PasswordSetError: se nao for possivel armazenar o token no chaveiro.
        """
        try:
            logger.debug("salvando token")
            keyring.set_password("servico_xirico", nome_usuario, token)
            logger.debug("sucesso: token salvo")
            return None
        except keyring.errors.InitError as e:
            logger.warning("erro: falha ao guardar token chaveiro indisponivel-----Erro: %d", e.errno())
            raise
        except keyring.errors.PasswordSetError as e:
            logger.warning("erro: falha ao guardar token-----Erro: %d", e.errno())
            raise
            
            
    def pegar_token(nome_usuario:str) -> str:
        """
        Recupera o token armazenado no gestor de senhas do sistema.
        
        Args:
            nome_usuario(str): nome do usuario do token a ser recuperado.
            
        Returns:
            str:o token recuperado do gestor de senhas.
            
        Raises:
            InitError: se o gestor de senhas estiver indisponivel.
            PasswordGetError: se falhar ao acessar o token.
            
        """
        try:
            logger.debug("caregndo token")
            return keyring.get_password("servico_xirico", nome_usuario)
        except keyring.errors.InitError as e:
            logger.warning("erro: falha ao pegar token. chaveiro indisponivel-----Erro: %d", e.errno())
            raise
        except keyring.errors.PasswordGetError as e:
            logger.warning("erro: falha ao pegar token.falha no acesso-----Erro: %d", e.errno())
            raise