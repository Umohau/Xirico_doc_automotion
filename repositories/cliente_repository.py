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
        Insere dados na tabela clientes.
        
        Args:
            dados(dict): dados inseridos na tabela
        Returns:
            int: id da nova insersao
        
        Raises:
            DuplicteError: se o cliente ja existir
        '''
        try:
            return super().insert(dados)
      
        except DuplicateError:
                logger.warning('tentativa de inserir cliente ja existente')
                raise DuplicateError('já existe um cliente com os dados fornrcidos') from e


    def delete(id:int)-> int:
        '''
        Deleta um cliente da tabela clientes
        (faz um soft delete alterando o estado ativo de true para false)
        
        Args:
            id(int): id do cliente deletado
            
        Retunrs:
           int: numero de clientes deletados
        
        Raises:
            EntityNotFoundError: se o id do cliente nao for encontrado
        '''
        try:
            return super().delete(id)
        except EntityNotFoundError:
            logger.warning("falha ao deletar cliente de id  %d -nao encontrado", id)
            raise EntityNotFoundError('cliente nao encontrado ')

    def reactivate (self , email:str) -> int:
        """
        Reativa um cliente inativo, alterando seu estado ativo de False para True.
        
        Args:
            email(int): email do cliente alvo da operacao.
            
        Returns:
            int: clientes reactivados
            
        Raises:
            EntityNotFoundError: se o cliente inativo nao for encontrado.
        """
        activar= self.tabela.update().values(ativo=True).where(sa.and_(self.tabela.c.email== email, self.tabela.c.ativo==False))
        
        with self.engine.begin() as conexao:
            res=conexao.execute(activar).rowcount
            if not  res:
                logger1.warning("falha ao  reativar cliente. Nao encontrado")
                raise EntityNotFoundError("cliente email: {email}  nao encontrado")
            
    def update(self, dados:dict,  id:int=None, email:str=None) -> list:
        """
        Actualida dados de um cliente especificado pelo id, em campos fornecidos no argumento dados.
        
        Args:
            id(int): id do cliente a receber actualizacao
            dados(dict): novos dados do cliente
       
       Returns:
            list:lista dos campos actualizdos
        
        Raises:
            EntityNotFoundError: se nenhum clinte for encontrado com o id fornecido
            
        """
        try:
            return super.update(dados, id, email)
        except EntityNotFoundError:
            logger.warning("falha ao tentar  actulizar dados para cliente id: %d-nao encontrado", id)
            raise EntityNotFoundError(f"cliente com id {id} nao encontrado")
            
            
    def search_id(self, id:int) -> dict:
         try:
             return super().search_id(id)
         except EntityNotFoundError:
              logger.warning("a busca por id nao encontrou um cliente com id:%d", id)
              raise EntityNotFoundError("nenhum cliente com o id fornecido")   
         
         
    def search_all(self) -> list[dict]:
        """
        busca clientes activos na tabela clientes, retorna todos os registros da tabela
        
        Returns:
            list[dict]: uma lista com dicionarios contendo dados resultados da busca
          
        Raises:
            EmptyTableError: se a tabela estiver vazia
        """
        try:
            return super().search_all()
        except EmptyTableError:
             logger.warning("tentativa de buscar dados numa tabela (clientes) vazia")
             raise EmptyTableError("sua tabela clientes esta vazia")


    def search_name(self, nome:str) -> list[dict]:
        """
        busca um cliente com o nome similar ao nome fornecido no argumento nome.
     
       Args:
          nome(str): nome alvo da busca (pode ser parte do nome)
       
       Returns:
          list[dict]: lista de dicionarios com dados resultados da busca
          
        Raises:
          EntityNotFoundError: se  nenhum nome nos registros corresponder ao nome fornecido.
          
        """
        try:
            return super().search_name(nome)
        except EntityNotFoundError:
             logger.warning("a busca por nome nao encontrou nenhum cliente com nome parecido a '%s' ", nome)
             raise EntityNotFoundError(f"nenhum cliente corrsponde ao nome '{nome}")
             
    @property        
    def total_records(self) -> int:
        return super().total_records             