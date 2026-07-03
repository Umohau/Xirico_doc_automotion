from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.infra import Conector
import sqlalchemy as sa
from Projeto_xirico.exc import EntityNotFoundError, DuplicateError, EmptyTableError, ProtectedEntityError
import logging
logger=logging.getLogger(__name__)

class OrdersRepository:
    def __init__(self, conector:Conetor):
        self.engine=conector.engine
        self.metadata=conector.metadata
        if 'orders' not in self.metadata.tables:
            logger.warning('Orders table not found in metadata object')
            raise RuntimeError("""Orders table not found in metadata.
Make sure to use the SAME Connector 
object in both the InfraData and the OrdersRepository class.""")
        self.tabela= self.metadata.tables["orders"]
        
    
    def insert(self, order_dados:dict) -> str:
        """
       Add a new order to the orders table.

        Args:
            order_dados (dict): Dictionary containing the new order data.
        
        Returns:
            str: ID of the newly created order.
        
        Raises:
            IntegrityError: If a foreign key is invalid.
        """
        inserir= self.tabela.insert()    
        with self.engine.begin() as conexao:
            try:
                res=conexao.execute(inserir, order_dados)    
                id= res.inserted_primary_key[0]
                return id
            except sa.exc.IntegrityError as e:
                logger.warning('Failed to insert new order\n Param: %s', e.params)
                raise
                

    def delete(self, order_id: int) -> int:
        """
        Delete a non-completed order from the orders table.

        Args:
            order_id (int): ID of the order to be deleted.
        
        Returns:
            int: Number of affected rows.
        
        Raises:
            EntityNotFoundError: If the order is not found.
        """
        deletar= self.tabela.delete().where(self.tabela.c.order_id== order_id)
        try:
            with self.engine.begin() as conexao:
                res=conexao.execute(deletar).rowcount
                if not res:
                    logger.warning('Failed to delete order id:%s - not found', order_id)
                    raise EntityNotFoundError(f'Order with id {order_id} not found')
                return res
        except sa.exc.IntegrityError as e:
            raise ProtectedEntityError("Cannot delete completed order.") from e
            
            
    def update(self,order_id: int, novos_dados: dict) -> int:
        """
       Update order data by replacing the fields with the new data provided in the `novos_dados` argument.

        Args:
            order_id (int): ID of the target order.
            novos_dados (dict): Dictionary containing the new data.
        
        Returns:
            int: Number of orders updated.
        
        Raises:
            EntityNotFoundError: If the target order is not found.
            IntegrityError: If the new data contains an invalid foreign key.
        """
        actual=self.tabela.update().where(self.tabela.c.order_id==order_id)
        actual=actual.values(novos_dados)
        
        with self.engine.begin() as conexao:
            res=conexao.execute(actual).rowcount
            if not res:
                logger.warning("Failed to update %s order %s- not found.", list(novos_dados.keys()), order_id)
                raise EntityNotFoundError(f"Order with id {order_id} not found")
            return res
            
            
    def search_orders(self) -> list[dict]:
        """
        Fetch all orders from the orders table.
        
        Returns:
            list[dict]: A list of dictionaries containing the data for each order.
        
        Raises:
            EmptyTableError: If the orders table is empty.
        """
        dados=list()
        busca= sa.select(self.tabela)
        
        with self.engine.begin() as conexao:
            res= conexao.execute(busca).fetchall()
            
            # converte cada tupla do 
            #objeto row em um dicionario
            # e adiciona  na lista dados
            for resultado in res:
                dados.append(resultado._asdict())
                
            # verifica se ha resultados
            if not res:
                logger.warning("Failed: orders table is empty.")
                raise EmptyTableError("Cannot fetch data from empty orders table.")
            return dados
            
            
    def get_order_oid(self, order_id: str) -> dict:
        """
        Retrieve an order by ID from the orders table.

        Args:
            order_id (str): ID of the target order for the search.
        
        Returns:
            dict: Dictionary containing the order data.
        
        Raises:
            EntityNotFoundError: If the order is not found.
        """
        busca= sa.select(self.tabela).where(self.tabela.c.order_id== order_id)
        
        with self.engine.begin() as conexao:
            res= conexao.execute(busca).first()
            
            if not res:
                logger.warning('Order with id %s not found', order_id)
                raise EntityNotFoundError("'Order with provided ID not found.'")
            return res._asdict()
            

    def get_orders_cid(self, cliente_id: int) -> list[dict]:
        """
       Fetch all orders for a client by client ID.

        Args:
            cliente_id (int): ID of the target client.
        
        Returns:
            list[dict]: A list of dictionaries containing the orders data for the client, ordered by registration date from newest to oldest.
        
        Raises:
            EntityNotFoundError: If the client has no orders at the time of method execution.
        """
        dados=list() 
        busca= sa.select(self.tabela).order_by(sa.desc(self.tabela.c.registado_at))
        busca=busca.where(self.tabela.c.cliente_id== cliente_id)
        
        with self.engine.begin() as conexao:
            res= conexao.execute(busca).fetchall()
            if not res:
                logger.warning("Client %d has no orders.", cliente_id)
                raise EntityNotFoundError("No orders found for this client.")
            for resultado in res:
                dados.append(resultado._asdict())
            return dados
            

    def get_orders_gid(self, operador_id: int) -> list[dict]:
        """
        Fetch all orders managed by a specific operator by their ID.

        Args:
            operador_id (int): ID of the target operator.
        
        Returns:
            list[dict]: A list of dictionaries containing the data for each order managed by the operator, ordered by registration date from newest to oldest.
        
        Raises:
            EntityNotFoundError: If the operator has not managed any orders at the time of method execution.
        """
        dados=list() 
        busca= sa.select(self.tabela).order_by(sa.desc(self.tabela.c.registado_at))
        busca=busca.where(self.tabela.c.gestor_id== operador_id)
        
        with self.engine.begin() as conexao:
            res= conexao.execute(busca).fetchall()
            if not res:
                logger.warning('Operator %d has not managed any orders.', operador_id)
                raise EntityNotFoundError("No managed orders found for this operator.")
            for resultado in res:
                dados.append(resultado._asdict())
            return dados
            

    def total_records(self):
        with self.engine.begin() as conexao:
            pegar_tot=sa.select(sa.func.count(self.tabela.c.order_id))
            total= conexao.execute(pegar_tot).scalar()
            return total