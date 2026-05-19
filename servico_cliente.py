import logging
from segurança import auditoria,gestor_sessao
from repositorios import RepositorioClientes
from infra import DuplicateError,PermissionDeniedError, EntityNotFoundError, InfraBanco, Conector

logger= logging.getLogger(__name__)
logging.basicConfig(format= '%(levelname)s: %(message)s  %(asctime)s',
   datefmt= '%H:%M',
   level=logging.DEBUG)
   
class PermissaoMixIn:
    @staticmethod 
    def permissao(operador):
        """
        Verifica se o operdor logado é Administrador ou nao.
        Params:
            operador: operador a ser verificado 
            
        Returns:
            True: se o operador for ADM
            False: se nao for ADM
        
        Raises:
            InvalidTokenError: se o token for invalido 
        """
        return operador.get("ADM", False)
        


class ServicoCliente(PermissaoMixIn):
    def __init__(self, repo_cliente:RepositorioClientes, gestor_sessao):
        self._repo_cliente=repo_cliente
        self._gestor_sessao=gestor_sessao
        
        
    @property
    def operador(self):
        return self._gestor_sessao.operador
        
        
    def adicionar_cliente(self, dados:dict,) -> int:
        """
        Adiciona um novo cliente. Registra a operacao em logs de auditoria.
        
        Args:
            dados(dict): dicionario com os dados do cliente.
        
        Returns:
            int: id do novo cliente adicionado
            
        Raises:
            DuplicateError: se ja existir um cliente com os dados fornecidos(email, telefone, dominio)
            EntityNotFoundError: se o operador que chamou o metodo nao existir.
        """
        operador_id= self.operador["id_operador"]
        if not operador_id:
            raise RunTimeError("sem sessao iniciada")
            
        try:     
            novo_id=self._repo_cliente.inserir(dados)
            auditoria.auditar(operador_id,"adiconar_cliente", f" adicionou um novo cliente com id:{novo_id}")
            return novo_id
        except DuplicateError as e:
                raise DuplicateError("ja existe um cliente com email, telefone ou dominio fornecudos" )
        
        
    def eliminar_cliente(self, cliente_id: int) -> None:
      """
      Elimina um cliente , com a restricao de que so operadores ADM podem eliminar clientes, e registra a operacao em logs de auditoria.
      
      Args:
          cliente_id(int): id do cliente a ser eliminado.
          
      Returns:
          None
          
      Raises:
          PermissionDeniedError: se o operador nao for ADM
      """
      
      #verifica se o operador e ADM
      logger.debug("verificando permissao")
      if self.permissao(self.operador):
          logger.debug("sucesso:permissao Válida")
          operador_id= self.operador["id_operador"]
          try:
            logger.debug("eliminando cliente")
            # elimina o cliente
            self._repo_cliente.deletar(cliente_id)
            logger.debug("sucesso: cliente eliminado")
            
            #registra auditoria
            auditoria.auditar(
                operador_id, 
                "eliminar_cliente",
                f"eliminou o cliente com id:{cliente_id}")
            return
          
          except EntityNotFoundError:
             logger.debug("erro: cliente nao encontrado")
             raise
      logger.debug("permissao negada")    
      raise PermissionDeniedError("somente ADM pode eliminar clientes")
          
      
      
         
    def pesquisar_clientes(self, termo: int|str=None) -> dict | list[dict]:
        """
        pesquisa por clientes no repositorio clientes e registra logs de auditoria.
        
        Args:
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
        operador_id=self.operador["id_operador"]
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
            

    def actualizar_cliente(self, cliente_id:int,  dados: dict) -> list:
        """
        Actualisa os dados de um cliente e regstra um log de auditoria.
        
        Args:
            cliente_id(int): id do cliente alvo.
            dados(dict): dicionario com campos a serem actualizados e novos dados.
        
        Returns:
            list: lista com os campos actualizados.
            
        Raises:
            EntityNotFoundError: se o cliente alvo nao for encontrado.
            
        """
        operador_id= self.operador["id_operador"]
        logger.debug("actualizando dados do cliente %d", cliente_id)
        campos=self._repo_cliente.actualizar(cliente_id, dados)
        auditoria.auditar(
            operador_id,
            operacao= "actualizar_cliente",
            detalhes=f"actualizou os dados do cliente id:{cliente_id}. nos campos: {campos}"
        )
        return campos
        


        
