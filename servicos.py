import logging
from repositorios import RepositorioClientes, RepositorioAves, RepositorioOperadores
from infra import DuplicateError,PermissionDeniedError, EntityNotFoundError, InfraBanco, Conector

logger= logging.getLogger(__name__)
logging.basicConfig(format= '%(levelname)s: %(message)s  %(asctime)s',
   datefmt= '%H:%M',
   level=logging.DEBUG)

class ServicoCliente:
    def __init__(self, repo_cliente:RepositorioClientes, repo_operador:RepositorioOperadores):
        self._repo_cliente=repo_cliente
        self._repo_operador=repo_operador
        
    
    def adicionar_cliente(self, dados:dict, operador_id:int) -> int:
        """
        Adiciona um novo cliente, com restricao a restricao so operadores ADM podem adicionar novos clientes
        
        Args:
            dados(dict): dicionario com os dados do cliente.
            operador_id(int): id do operador logado.
        
        Returns:
            int: id do novo cliente adicionado
            
        Raises:
            PermissionDeniedError: se o operador nao for ADM
            DuplicateError: se ja existir um cliente com os dados fornecidos(email, telefone, dominio)
        """
        try:
            operador= self._repo_operador. buscar_id(operador_id)
        except EntityNotFoundError:
            logger.warning("PERMISSAO NEGADA: tentativa de adicionar cliente pelo operador id:%d-Nao encontrado.", operador_id)
            raise PermissionDeniedError("nao tem permissao para efectuar esta accao")
            
        if not operador["ADM"]:
                logger.warning("PERMISSAO NEGADA: tentativa de adicionar cliente pelo operador id:%d.", operador_id)
                raise PermissionDeniedError("nao tem permissao para efectuar esta accao")
      
        try:
           return self._repo_cliente.inserir(dados)
        except DuplicateError as e:
            raise DuplicateError("ja existe um cliente com email, telefone ou dominio fornecudos" )
            

 
      