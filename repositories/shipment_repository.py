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
        Busca por exportacoes em intervalo de tempo (date) fornecido.
        
        Args:
            data_inicio(date): data apartir da qual começa a busca.
            data_fim(date): data maxima ate onde vai  a busca.
            
        Returns:
            list[dict]: lista de dicionarios como os dados de cada exportacao, organizados por data da mais recente a mais antiga.
            
        Raises:
            EntityNotFoundError: se nao houverem registros para o intervalo fornecido
            
        Note:
            os resultados incluem a data de envio em orders.
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
                logger.warning("falha: nao foram encontrados registros  na epoca %s a %s", data_inicio, data_fim)
                raise EntityNotFoundError("nenhum registro encontrado na epoca definida")
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
        Busca todas as exportacoes feitas a um cliente pelo seu id.
        
        Args:
            cliente_id(int): id do cliente alvo.
           
        Returns:
            list[dict]: lista de dicionarios com os dados de cada exportacao ao cliente ordenados da data mais recente a mais antiga.
            
        Raises:
            EntityNotFoundError: se nao houvem exportacoes que correspondam.
            
        Note:
            Os resultados incluem a data de envio obtida em orders.
        """
        dados=self._buscar_termo("cliente_id", cliente_id)
        if not dados:
                logger.warning("falha: nao ha registros de exportacoes referentes ao cliente id%d", cliente_id)
                raise EntityNotFoundError("nao foram encontradas registros de exportacao para o cliente")
        return dados
        
            
    def get_shipment_oid(self, order_id):
         """
         Busca uma exportacao pelo  id do pedido.
         
         Args:
             order_id(int): id da exportacao alvo da busca.
             
         Returns:
             dict: dicionario comos dados da exportacao.
             
         Raises:
             EntityNotFoundError: se a exportacao nao for emcontrada
         """
         dados= self._buscar_termo("order_id", order_id)
         if not dados:
             logger.warning("falha: nao foi encontrada uma exportacao que corrw")
             raise EntityNotFoundError("nenhuma exportacao com id fornecido")
         return dados[0]
         
  
    def get_shipments_gid(self, operador_id):
        """
        Busca todas as exportacoes gerenciadas pelo operador fornecido em operador_id.
        
        Args:
            operador_id(int): id do operador alvo.
            
        Returns:
            list[dict]: lista de dicionarios com as exportacoes gerenciadas pelo operador, odenadas da mais recente a mais antiga.
            
        Raises:
            EntityNotFoundError: se nenhuma exportacao gerida pelo operador for encontrada.
        """
        
        dados=self._buscar_termo("gestor_id", operador_id)
        
        if not dados:
            logger.warning("nenhuma exportacao gerida pelo operador id%d", operador_id)
            raise EntityNotFoundError("nenhuma exportacao referente ao operador informado")
        return dados

