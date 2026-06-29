import logging
from Projeto_xirico.interfaces.repository_interfaces import RepositoryInterface

logger=logging.getLogger(__name__)


class ClientsRepoitory(RepositoryInterface):
    def __init__(self, conector):
        super().__init__(conector)
        if 'clients' not in self.metadata.tables:
            logger.warning("Table 'clients' not found in metadata object")
            raise RuntimeError("""Clients table not found in metadata.
Ensure that the same Connector object is used in both the InfraData and the ClientsRepository class.""")
        self.tabela= self.metadata.tables["clients"]
        
        
    def insert(dados: dict)->int:
        '''
        Insert data into the clients table.

        Args:
            dados (dict): Data to be inserted into the table.
        
        Returns:
            int: ID of the newly inserted record.
        
        Raises:
            DuplicteError: If the client already exists.
        '''
        try:
            return super().insert(dados)
      
        except DuplicateError:
                logger.warning('Attempt to insert an already existing client.')
                raise DuplicateError('Client already exists with the provided data')


    def delete(id:int)-> int:
        '''
        Delete a client from the clients table.

        Performs a soft delete by setting the `ativo` field from `True` to `False`.
        
        Args:
            id (int): ID of the client to be deleted.
        
        Returns:
            int: Number of clients deleted.
        
        Raises:
            EntityNotFoundError: If the client ID is not found.
        '''
        try:
            return super().delete(id)
        except EntityNotFoundError:
            logger.warning("Failed to delete client with id %d - not found", id)
            raise EntityNotFoundError('Could not delete client with id %d - not found')

    def reactivate (self , email:str) -> int:
        """
        Reactivate an inactive client by changing its active state from `False` to `True`.

        Args:
            email (str): Email of the target client.
        
        Returns:
            int: Number of clients reactivated.
        
        Raises:
            EntityNotFoundError: If the inactive client is not found.
        """
        activar= self.tabela.update().values(ativo=True).where(sa.and_(self.tabela.c.email== email, self.tabela.c.ativo==False))
        
        with self.engine.begin() as conexao:
            res=conexao.execute(activar).rowcount
            if not  res:
                logger1.warning("Failed to reactivate client - not found")
                raise EntityNotFoundError("No client found for email: {email}")
            
    def update(self, dados:dict,  id:int=None, email:str=None) -> list:
        """
        Update data for a client specified by either ID or email, using fields provided in the `dados` argument.

        Args:
            id (int): ID of the target client.
            email (str): Email of the target client.
            dados (dict): New data for the client.
        
        Returns:
            list: List of updated fields.
        
        Raises:
            EntityNotFoundError: If no client is found with the provided ID or email.
            
        """
        try:
            return super.update(dados, id, email)
        except EntityNotFoundError:
            logger.warning("Failed to update data for client - not found", id)
            raise EntityNotFoundError(f"'No client found")
            
            
    def search_id(self, id:int) -> dict:
         try:
             return super().search_id(id)
         except EntityNotFoundError:
              logger.warning("No client found with id:%d", id)
              raise EntityNotFoundError("'Client not found for the provided ID.'")   
         
         
    def search_all(self) -> list[dict]:
        """
        Fetch all active clients from the clients table.

        Returns:
            list[dict]: A list of dictionaries containing the query result data.
        
        Raises:
            EmptyTableError: If the table is empty.
        """
        try:
            return super().search_all()
        except EmptyTableError:
             logger.warning('Failed to fetch data from clients table: table is empty.')
             raise EmptyTableError("'Cannot fetch data from empty clients table.'")


    def search_name(self, nome:str) -> list[dict]:
        """
        Search for clients with a name similar to the one provided in the `nome` argument.

        Args:
            nome (str): Target name for the search (can be a partial match).
        
        Returns:
            list[dict]: A list of dictionaries containing the query result data.
        
        Raises:
            EntityNotFoundError: If no record matches the provided name.
          
        """
        try:
            return super().search_name(nome)
        except EntityNotFoundError:
             logger.warning(" Search by name did not find any client with a name similar to '%s' ", nome)
             raise EntityNotFoundError(f"'No client matches the name {nome}'")
             
    @property        
    def total_records(self) -> int:
        return super().total_records             