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
            
            
        
        
        
        
class ServicoCliente(PermissaoMixIn):
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
            EntityNotFoundError: se o operador que chamou o metodo nao existir.
        """
        
        if self.permissao(self._repo_operador, operador_id, "adicionar_cliente"):
            try:
               novo_id=self._repo_cliente.inserir(dados)
               auditoria.auditar(operador_id,"adiconar_cliente", f" adicionou um novo cliente com id:{novo_id}")
               return novo_id
            except DuplicateError as e:
                raise DuplicateError("ja existe um cliente com email, telefone ou dominio fornecudos" )
        raise PermissionDeniedError("Apenas ADM pode adicionar novos clientes")
        
        
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
      
      if self.permissao(self._repo_operador, operador_id, "eliminar_cliente"):
          try:
            # elimina o cliente
            self._repo_cliente.deletar(cliente_id)
            
            #registra auditoria
            auditoria.auditar(
                operador_id, 
                "eliminar_cliente",
                f"eliminou o cliente com id:{cliente_id}")
            return
          except EntityNotFoundError:
             raise
          
      raise PermissionDeniedError("somente ADM pode eliminar clientes")
          
      
      
         
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
        

class ServicoOperador(PermissaoMixIn):
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
            PermissionDeniedError: se operador que chama o metodo nao for ADM
            DuplicateError: se existir operador com os dados fornecidos.
        """
        
       
      
        # verifica se o operador é ADM
        if self.permissao(self._repo_operador, operador_id, "adicionar_operdor"):
            # insere os dados do novo operador no repositorio
            novo_id=self._repo_operador.inserir(dados) 
            
           #registra o log de audiroria
            auditoria.auditar(
               operador_id,
               operacao= "adicionar_operador",
               detalhes= f"adicionou o operador id: {novo_id}")
            
            return novo_id
        raise PermissionDeniedError("somente ADM pode adicionar novos operadores")
            
        
    def pesquisar_operadores(self,operador_id: int, termo: int|str=None) -> dict|list[dict]:
        """
        pesquisa por operadores no repositorio operadores e registra logs de auditoria.
        
        Args:
            operador_id(int): id do operador.
            termo(int| str| None): termo a ser pesquisado pode ser um id ou nome parcial:
                -se for "int" a pesquisa busca por id.
                -se for "str" a pesquisa busca por nome (parcial).
                -se for "None" a pesquisa busca todos os clientes.

        Returns:
            dict: se a busca for por id -retorna dicionario com os dados do operador.
            list[dict]: se a pesquisa buscar tudo,ou nome parcial - lista de dicionarios com os dados do operador.
        
        Raises:
            EntityNotFoundError: se a busca por nome ou id nao nao encontrar operadores que correspondam.
            EmptyTableError: se a busca por todos nao encontrar operadores.
            TypeError: se o tipo do termo nao for str, int ou None.
        """
        if self.permissao(self._repo_operador, operador_id, "pesquisar operadores"):
            if isinstance(termo, int):
                auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_operadores",
                    detalhes=f"pesquisou por :{termo}, em operadores.")
                logger.debug("buscando por id")     
                return self._repo.operador_.buscar_id(termo)
            
            elif isinstance(termo, str):
                auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_clientes",
                    detalhes=f"pesquisou pelo cliente com  nome parecido a :{termo}")
                logger.debug("buscando operadores por nome similar")    
                return self._repo_operador.buscar_nome(termo)
            elif not termo:
                auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_operadores",
                    detalhes=f"pesquisou por todos os operadores")
                logger.debug("buscando todos operadoreas")
                return self._repo_operador.buscar_tudo()
                
            else:
                raise TypeError("valor do argumento 'termo' invalido")
        raise PermissionDeniedError("apenas ADM pode pesquisar operadores")
        
        
    def eliminar_operador(self, operador_id:int, id_alvo: int) -> None:
      """
      Faz um sof delete, com a restricao de que so operadores ADM podem eliminar operadores, e registra a operacao em logs de auditoria.
      
      Args:
          operador_id(int): id do operador que executa a accao.
          id_alvo(int): id do operador a ser eliminado.
          
      Returns:
          None
          
      Raises:
          EntityNotFoundError: se o operador alvo nao for encontrado.
          PermissionDeniedError: se o operador executor nao for ADM
      """
      
      #verifica se o operador existe e se e ADM
      
      if self.permissao(self._repo_operador, operador_id, "eliminar_operador"):
          try:
            # elimina o operador
            logger.debug(f"eliminando operador id {id_alvo}")
            self._repo_operador.deletar(id_alvo)
            
            #registra auditoria
            auditoria.auditar(
                operador_id, 
                "eliminar_operador",
                f"eliminou o operador com id:{id_alvo}")
            return
          except EntityNotFoundError:
             raise
          
      raise PermissionDeniedError("somente ADM pode eliminar operadores")       


    def actualizar_operador(self, operador_id:int, id_alvo:int,  dados: dict) -> list:
        """
        Actualisa os dados de um operador e regstra um log de auditoria.
        Impede a actulizacao dos campos (ADM, id, Identificacao), os novos dados nao podem ser iguais aos antigos.
        
        Args:
            operador_id(int): id do operador executor.
            id_alvo(int): id do operador a  receber actualizacao.
            dados(dict): dicionario com campos a serem actualizados e novos dados.
        
        Returns:
            list: lista com os campos actualizados.
            
        Raises:
            KeyError: se dados incluir campos como(identificacao, id)
            PermissionDeniedError: se dados incluir o campo ADM
            EntityNotFoundError: se o operador  alvo nao for encontrado.
            
        """
        
        if not self.permissao(self._repo_operador, operador_id, "actualizar_operador"):
            if "ADM" in dados.keys():
                raise PermissionDeniedError("so ADM pode promover operadore.")
                
        if "identificacao" in dados.keys() or "id" in dados.keys() :
            raise KeyError("campo nao sujeito a alteracao.")
         
         #Verifica se os dados de actualizacao sao  novos.
        logger.debug("verificando  campos %s" , dados.keys())
        dados_antigos= self._repo_operador.buscar_id(id_alvo)
        for campo, valor in dados.items():
                   if (campo, valor) in dados_antigos.items():
                       raise ValueError(f"{campo} nao deve ser igual ao antigo") 
                       
        #actualiza os dados 
        logger.debug("atualizando dados do operador %d", id_alvo)              
        campos=self._repo_operador.actualizar(id_alvo, dados)
        auditoria.auditar(
            operador_id,
            operacao= "actualizar_operador",
            detalhes=f"actualizou os dados do operador id:{id_alvo}. nos campos: {campos}"
        )
        return campos


    def promover_operador(self, operador_id, id_alvo):
        """
        Promove um operador para ADM, alterdo o  valor do campo ADM pata True.
        
        Args:
            operador_id(int): id do operdor que executa a promocao.
            id_alvo(int): id do operador a ser provido.
            
            
        Return:
            bool: True se sucesso.
            
        
        Raises:
            EntityNotFoundError: se o operador alvo nao for encontrado.
        """
        dados={"ADM": True}
        
        #verifica se é ADM
        if not self.permissao(self._repo_operador, operador_id, "promover_operador"):
            raise PermissionDeniedError("somente ADM pode promover operadores")
        
        logger.debug("promovendo operador id %d a ADM", id_alvo)
        self._repo_operador.actualizar(id_alvo, dados)
        auditoria.auditar(
            operador_id,
            operacao= "promover_operador",
            detalhes=f"promoveu o operador id:{id_alvo}."
        )
        logger.info("sucesso: operador id %d promovido", id_alvo)
        

    def rebaixar_operador(self, operador_id, id_alvo):
        dados={"ADM": False}
        
        #verifica se é ADM
        if not self.permissao(self._repo_operador, operador_id, "rebaixar_operador"):
            raise PermissionDeniedError("somente ADM pode rebaixar operadores")
        
        logger.debug("rebaixando operador id %d a ADM", id_alvo)
        self._repo_operador.actualizar(id_alvo, dados)
        auditoria.auditar(
            operador_id,
            operacao= "rebaixar_operador",
            detalhes=f"rebaixu o operador id:{id_alvo}."
        )
        logger.info("sucesso: operador id %d rebaixado", id_alvo)
        
                
