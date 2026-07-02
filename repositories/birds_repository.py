import sqlalchemy as sa
import logging
from Projeto_xirico.interfaces.repository_interfaces import BaseRepository
from Projeto_xirico.exc import EntityNotFoundError, DuplicateError, EmptyTableError, IdentificatorError

logger=logging.getLogger(__name__)


class BirdsRepository(BaseRepository):
    def __init__(self, conector):
        super().__init__(conector)
        if 'birds' not in self.metadata.tables:
            logger.warning("Table 'birds' not found in metadata object")
            raise RuntimeError("""Birds table not found in metadata.
Ensure that the same Connector object is used in both the InfraData and the BirdsRepository class.""")
        self.tabela= self.metadata.tables["birds"]
        
        
    def insert(self, dados:dict) -> int:
        """
          Insert data into the birds table.
    
        Args:
            dados (dict): Data to be inserted into the table.
        
        Returns:
            int: ID of the newly inserted record.
        
        Raises:
            DuplicteError: If the bird already exists.
        """
        try:
            return super().insert(dados)
        except DuplicateError as e:
            logger.warning('Attempt to insert an already existing bird.')
            raise DuplicateError('Bird with provided data already exists') from e


    def delete(self, id:int) -> int:
        '''
        Delete a bird from the birds table.

        Performs a soft delete by setting the `ativo` field from `True` to `False`.
        
        Args:
            id (int): ID of the bird to be deleted.
        
        Returns:
            int: Number of birds deleted.
        
        Raises:
            EntityNotFoundError: If the bird ID is not found.
        '''
        try:
            return super().delete(id)
        except EntityNotFoundError:
            logger.warning("Failed to delete bird ID %d: not found", id)
            raise EntityNotFoundError('Bird with the provided ID not found.')
            
            
    def recover(self, nome_cientifico)->bool:
        """
        Restore a previously inserted and deleted bird to available status for operations.
        
        Args:
            ave_id (int): ID of the target bird.
        
        Returns:
            None
        
        Raises:
            EntityNotFoundError: If the target bird does not exist or is already available.
        """
        dispo= self.tabela.update().values(ativo=True)
        dispo=dispo.where(sa.and_(
            self.tabela.c.nome_cientifico==nome_cientifico,
            self.tabela.c.ativo==False
            ))
            
        with self.engine.begin() as conexao:
            res=conexao.execute(dispo).rowcount
            if not res:
                logger.warning('Bird  not found')
                raise EntityNotFoundError(f'Bird  not found or already available')
            return True
            
            
    def update(self, dados_:dict, id:int=None, nome_cientifico=None):
        """
        Update data for a bird specified by either ID or scientific name, using fields provided in the `dados` argument.

        Args:
            id (int): ID of the bird to be updated.
            nome_cientifico (str): Scientific name of the target bird.
            dados_ (dict): New data for the bird.
        
        Returns:
            list: List of updated fields.
        
        Raises:
            EntityNotFoundError: If no bird is found with the provided ID or scientific name.
        
        Note:
            If both `id` and `nome_cientifico` are provided simultaneously, `id` takes precedence.
        """
        if not id and not nome_cientifico:
            logger.warning("sem identificadores, id ou nome_cientifico")
            raise IdentificatorError("nenhum identificador da ave foi fornecido (id ou email")
        actualizar= self.tabela.update()
        if not id:
            actualizar=actualizar.where(sa.and_(self.tabela.c.nome_cientifico==nome_cientifico, self.tabela.c.ativo==True))
        else:
             actualizar=actualizar.where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True))
        actualizar=actualizar.values(dados_)
    
        with self.engine.begin() as conexao:
            res=conexao.execute(actualizar).rowcount
            
            if not res:
                logger.warning('Failed to update data for bird: not found.' )
                raise EntityNotFoundError('Bird not found for update.')
            return list(dados_.keys())
            
            
    def search_name(self, nome:str)-> list[dict]:
        dados=list()
        busca= sa.select(self.tabela)
        busca=busca.where(sa.or_(
            sa.and_(
                self.tabela.c.nome_comum.ilike(f'%{nome}%'),
                self.tabela.c.ativo==True
                ),
            
            sa.and_(
                self.tabela.c.nome_cientifico.ilike(f'%{nome}%'),
                self.tabela.c.ativo==True
                )
            ))
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                logger.warning("No bird similar to '%s' found", nome)
                raise EntityNotFoundError(f"No bird matches the name {nome}")
            return dados


    def search_id(self, id:int)-> dict:
        try:
            return super().search_id(id)
        except EntityNotFoundError:
            logger.warning('No bird found with id:%d', id)
            raise


    def serch_all() -> list[dict]:
        try:
            return super.search_all()
        except EmptyTableError:
            logger1.warning("Cannot fetch data from empty birds table.")
            raise EmptyTableError('Cannot fetch data from empty birds table.')
            
            
   