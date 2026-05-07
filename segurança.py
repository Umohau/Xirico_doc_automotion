import bcrypt

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
