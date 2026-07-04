import sqlalchemy as sa
import logging
from Projeto_xirico.exc import EntityNotFoundError

logger=logging.getLogger(__name__)

class ShipmentRepository:
    def __init__(self, conector):
        self.engine=conector.engine
        self.metadata=conector.metadata
        if 'shipments' not in self.metadata.tables:
            logger.warning('shipments table not found in metadata object')
            raise RuntimeError("""shipments table not found in metadata.
Make sure to use the
 SAME Connector object in both the InfraBanco and the RepositorioOrders class.""")
        self.tabela= self.metadata.tables["shipments"]
        self.orders= self.metadata.tables["orders"]
        
      
    def insert(self, dados:dict) -> int:
        """
        Insert data for a new completed export.

    Args:
        dados (dict): Data for the new export.
    
    Returns:
        int: ID of the newly completed export.
    
    Raises:
        IntegrityError: If any foreign key is invalid.
        
        """
        inserir= self.tabela.insert()
        
        with self.engine.begin() as conexao:
            try:
                res= conexao.execute(inserir, dados)
                return res.inserted_primary_key[0]
            except sa.exc.IntegrityError as e:
                logger.warning('Failed to insert export: ParmError - %s', e.params)
                raise


    def update(self, dados:dict, expo_id) -> list:
        actualizar=self.tabela.update().where(self.tabela.c.exportacao_id== expo_id)
        actualizar=actualizar.values(dados)
        
        with self.engine.begin() as conexao:
            res= conexao.execute(actualizar)
            if not res:
                logger.warning("falha: nao foi possivel actualizar exportacao %d. nao encontrada")
                raise EntityNotFoundError("exportacao nao encontrada")
            return res.rowcount
            

    def search_epoc(self, data_inicio, data_fim) -> list[dict]:
        """
       Search for exports within the provided time interval (date).

        Args:
            data_inicio (date): Start date from which the search begins.
            data_fim (date): End date up to which the search goes.
        
        Returns:
            list[dict]: A list of dictionaries containing the data for each export, ordered by date from newest to oldest.
        
        Raises:
            EntityNotFoundError: If no records are found for the provided interval.
        
        Note:
            The results include the dispatch date in orders.
        """
        dados= list() 
        busca= sa.select(self.tabela, self.orders.c.enviado_at)
        
        # cria um join entre as tabelas
        #orders e exportacoes
        busca=busca.select_from(self.tabela.join(self.orders, self.tabela.c.order_id== self.orders.c.order_id))      
        #filtra os dados pelo intervalo 
        #de datas
        busca=busca.where(self.orders.c.registado_at.between(data_inicio, data_fim))
        
        #organiza de forma decrescente
        busca=busca.order_by(self.orders.c.registado_at.desc())             
        
        with self.engine.begin() as conexao:
            res= conexao.execute(busca).fetchall()
            if not res:
                logger.warning("Failed to find records for period %s to %s", data_inicio, data_fim)
                raise EntityNotFoundError("No records found for defined period.")
            for resultado in res:
                dados.append(resultado._asdict())
            return dados
        

    def _buscar_termo(self, coluna_o, termo_o):
        """
        Busca exportacoes usando uma coluna fornecida e o termo da busca.
        Args:
            coluna_o(str): nome da coluna , sera usado para filtrar os resultados.
            termo_o( str| int): termo de comparacao com o valor da coluna para o filtro where.
            
        Returns:
            list[dict]: lista de dicionarios com os dados das exportacoes ordenados da mais recente a mais antiga.
        """
        dados=list() #para acumular os dicionarios
        #define a coluna para filtro
        coluna= self.orders.c[coluna_o]
        
        busca= sa.select(self.tabela, self.orders.c.enviado_at)
        
        #cria um join entre as tabelas orders e exportacoes
        busca= busca.select_from(self.tabela.join(self.orders, self.tabela.c.order_id == self.orders.c.order_id))
        
        #filtra pela coluna e termo informados
        busca= busca.where(coluna==termo_o)
        
        #ordena por data mais recente
        busca=busca.order_by(self.orders.c.enviado_at.desc())
        
        #realiza a busca 
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            
            for resultado in res.mappings():
                dados.append(dict(resultado))
            return dados
            
        
    def get_shipments_cl(self, cliente_id: int) -> list[dict]:
        """
        Fetch all exports made to a client by client ID.

        Args:
            cliente_id (int): ID of the target client.
        
        Returns:
            list[dict]: A list of dictionaries containing the data for each export to the client, ordered from newest to oldest by date.
        
        Raises:
            EntityNotFoundError: If no matching exports are found.
        
        Note:
            The results include the dispatch date obtained from orders.
        """
        dados=self._buscar_termo("cliente_id", cliente_id)
        if not dados:
                logger.warning("Failed: no export records found for client id%d", cliente_id)
                raise EntityNotFoundError('No export records found for the client.')
        return dados
        
            
    def get_shipment_oid(self, order_id):
         """
        Retrieve an export by order ID.
        
        Args:
            order_id (int): ID of the target order for the search.
        
        Returns:
            dict: Dictionary containing the export data.
        
        Raises:
            EntityNotFoundError: If the export is not found.
         """
         dados= self._buscar_termo("order_id", order_id)
         if not dados:
             logger.warning("Failed to find a matching export for oid:%s", order_id)
             raise EntityNotFoundError('No export found for the provided ID.')
         return dados[0]
         
  
    def get_shipments_gid(self, operador_id):
        """
       Fetch all exports managed by the operator provided in `operador_id`.

        Args:
            operador_id (int): ID of the target operator.
        
        Returns:
            list[dict]: A list of dictionaries containing the exports managed by the operator, ordered from newest to oldest.
        
        Raises:
            EntityNotFoundError: If no exports managed by the operator are found.
        """
        
        dados=self._buscar_termo("gestor_id", operador_id)
        
        if not dados:
            logger.warning("No exports managed by operator id%d", operador_id)
            raise EntityNotFoundError('No exports found for the provided operator')
        return dados

