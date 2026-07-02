import sqlalchemy as sa
import logging
from Projeto_xirico.exc import DuplicateError, EntityNotFoundError, IdentificatorError, EmptyTableError
from Projeto_xirico.interfaces.repository_interfaces import BaseRepository

logger=logging.getLogger(__name__)


class OperatorRepository(BaseRepository):
    def __init__(self, conector):
        super().__init__(conector)
        if 'operators' not in self.metadata.tables:
            logger.warning("Table 'operators' not found in metadata object")
            raise RuntimeError("""Operators table not found in metadata.
Ensure that the same Connector object is used in both the InfraData and the OperatorsRepository class.""")
        self.tabela= self.metadata.tables["operators"]
    
    
    def insert(self, dados:dict) ->int:
        '''
        Insert data into the operators table.

        Args:
            data (dict): Data to be inserted into the table.
        
        Returns:
            int: ID of the newly inserted record.
        
        Raises:
            DuplicateError: If the operator already exists.
        '''
        try:
            return super().insert(dados)
            
        except sa.exc.IntegrityError as e:
                logger.error('Attempt to insert an operator that already exists.')
                raise DuplicateError('An operator already exists with the given data.') from e
                
        
    def delete(self, id:int) -> int:
        '''
        Perform a soft delete by setting the `activo` column to `False`.

        Args:
            id (int): ID of the operator to be deleted.
        
        Returns:
            int: Number of operators deleted.
        
        Raises:
            EntityNotFoundError: If the operator is not found.
        '''
        try:
                return super().delete(id)
        except EntityNotFoundError:
            logger.warning('Could not deactivate operator ID %d - not found or already inactive.', id)
            raise EntityNotFoundError('Operator does not exist or is already inactive.')
        
        
    def update(self,dados_:dict, id:int=None, email:str=None) ->list:
        """
        Update data for an active operator specified by either id or email, using fields provided in the data argument.

        Args:
            id (int): ID of the operator to be updated.
            email (str): Email of the operator to be updated.
            dados (dict): New data for the operator.
        
        Returns:
            list: List of updated fields.
        
        Raises:
            EntityNotFoundError: If no operator is found with the provided id or email.
            IdentificatorError: If neither email nor id is provided for the target.
        
        Note:
            If both email and id are provided simultaneously, id takes precedence.
        """
        if not email and not id:
            raise IdentificatorError("No target operator identifier provided (id or email).")
        actualizar= self.tabela.update()
        if id is None:
            actualizar=actualizar.where(sa.and_(self.tabela.c.email==email, self.tabela.c.ativo==True))
        else:
             actualizar=actualizar.where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True))
        actualizar=actualizar.values(dados_)
    
        
        with self.engine.begin() as conexao:
            res=conexao.execute(actualizar).rowcount
            
            if not res:
                logger.warning('Could not update operator: not found.')
                raise EntityNotFoundError('Could not update operator: not found.')
          
            
            return list(dados_.keys())

        
    def reactivate(self,  id:int) ->bool:
        """
       Reactivate the operator by setting the `active` field to `True`.

Args:
    id (int): ID of the operator to reactivate.

Returns:
    bool: True if reactivated.
        """   
        reactivar= self.tabela.update().values(ativo=True).where(self.tabela.c.id==id)
        
        with self.engine.begin() as conexao:
            res=conexao.execute(reactivar)
            if res.rowcount:
                return True
                                                       
                                                        
        
    def search_id(self, id:int) -> dict:
        """
        Retrieve an operator by ID.

        Args:
            id (int): ID of the operator to retrieve.
        
        Returns:
            dict: Dictionary containing the operator data.
        
        Raises:
            EntityNotFound: If no operator is found with the provided ID.
        """
        
        try:
             return super().search_id(id)
        except EntityNotFoundError:
                logger.warning("Search for operator ID %d returned no results", id)
                raise EntityNotFoundError('No operator exists with the specified ID.')
            
        
        
    def search_all(self) -> list[dict]:
        """
           Fetch all operators from the operators table.
            
            Returns:
                list[dict]: A list of dictionaries containing the query result data.
            
            Raises:
                EmptyTableError: If the table is empty.
        """
        try:
                return super().search_all()
        except EmptyTableError:
                logger.warning("tentativa de buscar dados na tabela operadores vazia")
                raise EmptyTableError("sua tabela operadores esta vazia")
        
        
    def search_name(self, nome:str) ->list[dict]:
        """
        Search for operators with a name similar to the one provided in the `nome` argument.

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
             logger.warning("Name search returned no operator similar to '%s' ", nome)
             raise EntityNotFoundError(f"No operator matches the name '{nome}' ")
            
        

    def search_email(self, email:str) -> dict:
        """
        Retrieve an operator by email.

        Args:
            email (str): Target email for the search.
        
        Returns:
            dict: Operator data resulting from the search.
        
        Raises:
            EntityNotFoundError: If the operator is not found.
            
        """
        busca= sa.select(self.tabela).where(sa.and_(
        self.tabela.c.email==email,
        self.tabela.c.ativo==True)) 
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            resultado=res.first()
            if not resultado:
                logger.warning("No operator with the provided email.")
                raise EntityNotFoundError("Operator with the provided email not found.")
            return resultado._asdict()


    def found_inactive(self, email):
            """
            Retrieve an inactive operator from the database by email.
        
            Args:
                email (str): Email of the inactive operator.
            
            Returns:
                dict: Dictionary containing the operator data.
            
            Raises:
                EntityNotFoundError: If the operator is not found.
            """
            
            busca= sa.select(self.tabela).where(sa.and_(self.tabela.c.ativo==False, self.tabela.c.email== email))      
            
            with self.engine.begin() as conexao:
                res=conexao.execute(busca)
                operador= res.first()
                if not operador:
                    raise EntityNotFoundError("'Inactive operator not found.'")    
                return operador._asdict()

                                
    def get_password(self, email:str)->bytes:
        """
       Retrieve the operator's password by the provided email.

        Args:
            email (str): Email of the target operator.
        
        Returns:
            bytes: Password hash with salt.
            
            
        Note:
            returns None if not found de operator password
        """
        pegar_senha=sa.select(self.tabela.c.senha).where(sa.and_(self.tabela.c.email==email, self.tabela.c.ativo==True))
        
        with self.engine.begin() as conexao:
            res=conexao.execute(pegar_senha)
            senha= res.first()
            return senha[0]
        
                
    def check_unique(self, dados:dict) -> bool:
        """
        Check if the value from the key-value pair in the `dados` argument exists in the operators table.

        Args:
            dados (dict): A single key-value pair. This is the data to be checked.
        
        Returns:
            bool: True if the data is unique (does not yet exist in the operators table).
        
        Raises:
            DuplicateError: If the data already exists.
        """
        ignorados=["nome", "senha", "endereco", "ativo", "ADM"] #campos nao sujeitos a verificacao de unicidadde
        
        for key, valor in dados.items():
            coluna=getattr(self.tabela.c, key )
            if key not in ignorados:
                busca= sa.select(self.tabela).where(coluna== valor)
                #realiza a busca no banco
                logger.debug("Checking uniqueness of %s", key)
                with self.engine.begin() as conexao:
                    res=conexao.execute(busca).first()
                    
                    if res:
                        logger.debug("Failure: %s is not unique", key)
                        raise DuplicateError(f"Operator with provided {key} already exists'")
                    logger.debug("Success: %s is unique", key)
                    
        return True                
            
            
    @property
    def total_records(self):
        """
        Count the total number of operators in the database (operators table).

        Returns:
            int: Total number of operators in the database.
        """
        return super().total_records