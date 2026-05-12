import logging
from segurança import auditoria
from repositorios import RepositorioClientes, RepositorioAves, RepositorioOperadores
from infra import DuplicateError,PermissionDeniedError, EntityNotFoundError, InfraBanco, Conector

logger= logging.getLogger(__name__)
logging.basicConfig(format= '%(levelname)s: %(message)s  %(asctime)s',
   datefmt= '%H:%M',
   level=logging.DEBUG)
   
class PermissaoMixIn:
    
    def permissao(self,repo_operador:RepositorioOperadores, id_operador: int, operacao:str):
        """
        verifica se o operador existe e se existir verifica se é ADM
        
        Args:
            repo_operador(object): instancia de RepositorioOperadores.
            id_operador: id do operador a ser verificado.
            operacao(str): nome da operacao que o operador pretende realizar.
            
        Returns:
            bool: True se existir e for ADM. False se existir mas nao for ADM
            
        Raises:
            EntityNotFoundError: se o operador nao existir
        """
        
        #verifica se operdor existe
        try:
            operador= repo_operador. buscar_id(id_operador)
        except EntityNotFoundError:
            logger.warning("operador inexistente tentou %s", operacao)
            raise
        
        # verifica se operdor é ADM
        if not operador.get("ADM"):
                logger.warning("PERMISSAO NEGADA: tentativa de %s pelo operador id:%d.", operacao, id_operador)
                return False
        return True
            
            
        
        
        
        
class ServicoCliente(PermissoMixIn):
    def __init__(self, repo_cliente:RepositorioClientes, repo_operador:RepositorioOperadores):
        self._repo_cliente=repo_cliente
        self._repo_operador=repo_operador
        
    
    def adicionar_cliente(self, dados:dict, operador_id:int) -> int:
        """
        Adiciona um novo cliente, com restricao a restricao so operadores ADM podem adicionar novos clientes, e registra a operacao em logs de auditoria.
        
        Args:
            dados(dict): dicionario com os dados do cliente.
            operador_id(int): id do operador logado.
        
        Returns:
            int: id do novo cliente adicionado
            
        Raises:
            PermissionDeniedError: se o operador nao for ADM
            DuplicateError: se ja existir um cliente com os dados fornecidos(email, telefone, dominio)
        """
        if 
            raise 
            
        if permissao==False:
                raise PermissionDeniedError("nao tem permissao para efectuar esta accao")
      
        try:
           novo_id=self._repo_cliente.inserir(dados)
           auditoria.auditar(operador_id,"adiconar_cliente", f" adicionou um novo cliente com id:{novo_id}")
           return novo_id
        except DuplicateError as e:
            raise DuplicateError("ja existe um cliente com email, telefone ou dominio fornecudos" )
            

    def eliminar_cliente(self, operador_id:int, cliente_id: int) -> None:
      """
      Elimina um cliente , com a restricao de que so operadores ADM podem eliminar clientes, e registra a operacao em logs de auditoria.
      
      Args:
          operador_id(int): id do operador que executa a accao.
          cliente_id(int): id do cliente a ser eliminado.
          
      Returns:
          None
          
      Raises:
          EntityNotFoundError: se o cliente nao for encontrado.
          PermissionDeniedError: se o operador nao for ADM
      """
      
      #verifica se o operador existe e se e ADM
      try:
          operador= self._repo_operador.buscar_id(operador_id)
      except EntityNotFoundError:
          logger.critical("falha critica na seguranca um operador inexistente tentou eliminar um cliente")
          raise
      if not operador["ADM"]:
          logger.info("PERMICAO NEGADA: o operaor id: %d tentou eliminar o cliente id:%d", operador_id, cliente_id)
          raise PermissionDeniedError("somente ADM pode eliminar clientes")
          
      # elimina o cliente
      try:
        self._repo_cliente.deletar(cliente_id)
        auditoria.auditar(operador_id, "eliminar_cliente", f"eliminou o cliente com id:{cliente_id}")
      except EntityNotFoundError:
         raise
         
    def pesquisar_clientes(self,operador_id: int, termo: int|str=None) -> dict|list[dict]:
        """
        pesquisa por clientes no repositorio clientes e registra logs de auditoria.
        
        Args:
            operador_id(int): id do operador.
            termo(int| str| None): termo a ser pesquisado:
                -se for "int" a pesquisa busca por id.
                -se for "str" a pesquisa busca por nome (parcial).
                -se for "None" a pesquisa busca todos os clientes.

        Returns:
            dict: se a busca for por id -retorna dicionario com os dados do cliente.
            list[dict]: se a pesquisa buscar tudo,ou nome parcial - lista de dicionarios com os dados do cliente.
        
        Raises:
            EntityNotFoundError: se a busca por nome ou id nao nao encontrar clientes que correspondam.
            EmptyTableError: se a busca por todos nao encontrar clientes.
            TypeError: se o tipo do termo nao for str, int ou None.
        """
        if isinstance(termo, int):
            auditoria.auditar(
                operador_id,
                operacao="pesquisar_clientes",
                detalhes=f"pesquisou pelo cliente id:{termo}")
            return self._repo_cliente.buscar_id(termo)
        
        elif isinstance(termo, str):
            auditoria.auditar(
                operador_id,
                operacao="pesquisar_clientes",
                detalhes=f"pesquisou pelo cliente com  nome parecido a :{termo}")
            return self._repo_cliente.buscar_nome(termo)
        elif not termo:
            auditoria.auditar(
                operador_id,
                operacao="pesquisar_clientes",
                detalhes=f"pesquisou por todos os clientes")
            return self._repo_cliente.buscar_tudo()
        else:
            raise TypeError("valor do argumento 'termo' invalido")
            

    def actualizar_cliente(self, operador_id:int, cliente_id:int,  dados: dict) -> list:
        """
        Actualisa os dados de um cliente e regstra um log de auditoria.
        
        Args:
            operador_id(int): id do operador.
            cliente_id(int): id do cliente alvo.
            dados(dict): dicionario com campos a serem actualizados e novos dados.
        
        Returns:
            list: lista com os campos actualizados.
            
        Raises:
            EntityNotFoundError: se o cliente alvo nao for encontrado.
            
        """
        campos=self._repo_cliente.actualizar(cliente_id, dados)
        auditoria.auditar(
            operador_id,
            operacao= "actualizar_cliente",
            detalhes=f"actualizou os dados do cliente id:{cliente_id}. nos campos: {campos}"
        )
        return campos
        

class ServicoOperador:
    def __init__(self, repo_operador:RepositorioOperadores):
        self._repo_operador=repo_operador
        
    def adicionar_operador(self, operador_id, dados):
        """
        Adiciona um novo operador ao repositorio e registra auditoria.
        
        Args:
            operador_id(int): id do operador que executa a adicao.
            dados(dict): dicionario de dados do novo operador.
            
        Returns:
            int: id do operador adicionado
            
        Raises:
            DuplicateError: se existir operador com os dados fornecidos.
        """
        
        # verifica se operador que esta chamando o metodo existe
        try:
            operador=self._repo_operador.buscar_id(operador_id)
        except EntityNotFoundError:
            logger.critical("falha critica na seguranca um operador inexistente tentou adicionar um novo cliente.")
            raise
        
        # verifica se o operador é ADM
        if not operador["ADM"] :
            logger.warning("PERMISSAO NEGADA: o perador id:%d tentou inserir um novo operador", operador_id)
            raise PermissionDeniedError("somente ADM pode adicionar novos operadores")
            
        # insere os dados do novo operador no repositorio
        novo_id=self._repo_operador.inserir(dados) 
        
        #registra o log de audiroria
        auditoria.auditar(
           operador_id,
           operacao= "adicionar_operador",
           detalhes= f"adicionou o operador id: {novo_id}")
        return novo_id
        

   