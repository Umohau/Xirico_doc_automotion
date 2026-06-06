from segurança import auditoria
import exc


class ServicoOrders:
    def __init__(self, perfil, repo_orders):
        self._perfil= perfil
        self._repo_orders= repo_orders
        
    def adicionar_pedido(self, dados:dict) -> int:
        """
        Adiciona um novo pedido, qualquer operdor tem acesso a executar esta operacao.
        
        Args:
            dados(dict): dados do novo pedido a adicionar.
            
        Returns:
            int: id do novo pedido adicionado.
            
        Raises:
            IntegrityError: se uma chave estrangeira for invalida.
        """
        id= self._repo_orders.inserir(dados)
        auditoria.auditar(
            operador=self._perfil.id,
            operacao= "adicionar_pedido",
            detalhes=f"adiciou o pedido id:{id}")

        return id
        
        
    def deletar_pedido(self, order_id: int) ->None:
        """
        Exclue o pedido referente ao id informado.
        So é possivel excluir pedidos que ainda nao foram concluidos.
        Qualquer operador tem acesso a este metodo.
        
        Args:
            order_id(int): id do pedido alvo.
            
        Returns:
            None
            
        Raises:
            EntityNotFoundError: se nao encontrar o pedido alvo.
            IntegrityError: se o pedido ja tiver sido concluido
        """
        self._repo_orders.deletar(order_id)
        auditoria.auditar(
            operador=self._perfil.id,
            operacao= "deletar_pedido",
            detalhes=f"deletou o pedido id:{order_id}")
            
            
    def actualizar_pedido(self, order_id:int, dados: dict):
        """Actualiza os dados de um pedido pedente  e regista auditoria.
        Nao permite actualizar os campos: gestor_id, regustado_at, e enviado_at, 
        esses campos sao inalteraveis via este metodo, o metodo ignora esses campos se informados.
        Metodo acessivel para o gestor do pedido e ADM.
        
        Args:
            order_id(int): id do pedido a ser actualizado.
            dados(dict): dicionario com os novos dados com pares coluna-dado.
            
        Returns:
            list: campos actualizados.
            
        Raises:
            EntityNotFoundError: se o pedido alvo nao for encontrado
            EntityProtectedError: se o pedido alvo estiver  concluido.
            PermissionDeniedError: se o operador que chamou nao for ADM ou  gestor do pedido.
        """
        #pega o id do gestor do pedido
        gestor_id=self._repo_orders.buscar_order_oid(order_id)["gestor_id"]
        
        #verifica a permissao do operador
        logger.debug("checando permissao para actualizar")
        if not self._perfil.id==gestor_id and not self._perfil.ADM:
            logger.warning("permissao negada para actualizar")
            raise exc.PermissionDeniedError("permissao megada  para actualizar")
            
        logger.debug("permissao verificada para actualizar")    
        
        #lista de campos restritos
        restritos=["gestor_id", "registado_at", "enviado_at" ]
        dados_limpos=dict()
        
        #filtra e ignora os campos restritos
        for campo, valor  in dados.items():
            if campo not in restritos:
                dados_limpos[campo]= valor
           
        #tenta actualizar o pedido             
        try:      
            self._repo_orders.actualizar(order_id, dados_limpos)
        except IntegrityError:
            raise exc.EntityProtectedError("nao é possivel editar o pedido")
            
        campos= list(dados_limpos.keys())
        auditoria.auditar(
            operador=self._perfil.id,
            operacao= "atualizar_pedido",
            detalhes=f"actualizou os campos:  {campos} do pedido:{order_id}") 
        return campos
        
        
    @property
    def buscar_pedidos(self):
        """
        Busca todos os pedidos incluindo os cocluidos .
        
        Returns:
            list[dict]: lista de dicionarios com os dados de cada pedido.
            
        Raises:
            EmptyTableError: se nao houverem pedidos (tabela vazia)
        """
        logger.debug("buscando todos os pedidos")
        pedidos=self._repo_orders.buscar_pedidos()
        auditoria.auditar(
            operador=self._perfil.id,
            operacao= "buscar_pedidos",
            detalhes=f"buscou todos os pedidos") 
        return pedidos
    

    def buscar_pedido_oid(self, order_id: int) -> dict:
        """
        Busca um pedido pelo seu id .
        
        Args:
            order_id(int): id do pedido alvo.
            
        Returns:
            dict: dicionrio com os dados do pedido.
            
        Raises:
            EntityNotFoundError: se o pedido nao for encontrado.
        """
        logger.debug("buscando pedido %d", order_id)
        pedido=self._repo_orders.buscar_order_oid(order_id)
        auditoria.auditar(
            operador=self._perfil.id,
            operacao= "buscar_order_oid",
            detalhes=f"buscou pelo pedido {order_id}") 
        return pedido


    def buscar_pedido_cid(self, cliente_id:int) -> list[dict]:
        """
        Busca todos os pedidos de um cliente pelo id do cliente.
        
        Args:
            cliente_id(int): id do cliente alvo.
            
        Returns:
            list[dict]: lista de dicionarios com dados de cada pedido.
            
        Raises:
            EntityNotFoundError: se nao encontrar nenhum pedido que corresponda ao cliente informado.
        """                                
        pedidos=self._repo_orders.buscar_orders_cid(cliente_id)
        auditoria.auditar(
            operador=self._perfil.id,
            operacao= "buscar_orders_cid",
            detalhes=f"buscou pelos pedidos  do cliente id:{cliente_id}") 
        return pedidos


    def buscar_pedido_gid(self, gestor_id:int) -> list[dict]:
        """
        Busca todos os pedidos gerenciados por um operador.
        Apenas ADM tem acesso a este metodo.
        
        Args:
            gestor_id(int): id do gestor(operador) alvo.
            
        Returns:
            list[dict]: lista de dicionarios com dados de cada pedido gerencido pelo operador.
            
        Raises:
            PermissionDeniedError: se quem tentar executar nao for ADM.
            EntityNotFoundError: se nao forem encontrados pedidos gerenciados pelo operador infirmado.
        """
        
        #verifica se é ADM         
        if not self._perfil.ADM:
            raise exc.PermissionDeniedError("nao tem permissao para este metodo de busca.")
        pedidos= self._repo_orders.buscar_orders_gid(gestor_id)
        auditoria.auditar(
            operador=self._perfil.id,
            operacao= "buscar_orders_gid",
            detalhes=f"buscou pelos pedidos  gerenciados pelo operador id:{gestor_id}") 
        return pedidos
        