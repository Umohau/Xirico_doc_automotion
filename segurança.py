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

#instancia global da classe Segsenha
segsenha=SegSenha()


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
