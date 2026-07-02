import sqlalchemy as sa
from Projeto_xirico.interfaces.repository_interface import BaseRepository
from Projeto_xiric.exc import EntityNotFoundError, DuplicateError, EmptyTableError


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
        except DuplicateError:
            logger.warning('Attempt to insert an already existing bird.')
            raise DuplicateError('Bird with provided data already exists')


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
        dispo= self.tabela.update().values(disponivel=True)
        dispo=dispo.where(sa.and_(
            self.tabela.c.id==ave_id,
            self.tabela.c.disponivel==False
            ))
            
        with self.engine.begin() as conexao:
            res=conexao.execute(dispo).rowcount
            if not res:
                logger.warning('Bird with id %d not found', ave_id)
                raise EntityNotFoundError(f'Bird {ave_id} not found or already available')
            return True
            
            
    def update(self, dados:dict, id:int=None, nome_cientifico=None):
        """
        Update data for a bird specified by either ID or scientific name, using fields provided in the `dados` argument.

        Args:
            id (int): ID of the bird to be updated.
            nome_cientifico (str): Scientific name of the target bird.
            dados (dict): New data for the bird.
        
        Returns:
            list: List of updated fields.
        
        Raises:
            EntityNotFoundError: If no bird is found with the provided ID or scientific name.
        
        Note:
            If both `id` and `nome_cientifico` are provided simultaneously, `id` takes precedence.
        """
        actualizar= self.tabela.update()
        if not id:
            where(sa.and_(self.tabela.c.nome_cientifico==nome_cientifico, self.tabela.c.ativo==True))
        else:
             actualizar=actualizar.where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True))
        actualizar=actualizar.values(dados)
    
        with self.engine.begin() as conexao:
            res=conexao.execute(actualizar).rowcount
            
            if not res:
                logger1.warning('Failed to update data for bird: not found.' )
                raise EntityNotFoundError('Bird not found for update.')
            return list(dados.keys())
            
            
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
                logger1.warning("No bird similar to '%s' found", nome)
                raise EntityNotFoundError(f"No bird matches the name {nome}")
            return dados


    def search_id(self, id:int)-> dict:
        try:
            return super().search_id(id)
        except EntityNotFoundError:
            logger1.warning('No bird found with id:%d', id)
            raise


    def serch_all() -> list[dict]:
        try:
            return super.search_all()
        except EmptyTableError:
            logger1.warning("Cannot fetch data from empty birds table.")
            raise EmptyTableError('Cannot fetch data from empty birds table.')