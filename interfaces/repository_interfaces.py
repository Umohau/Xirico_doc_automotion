from __future__ import annotations
import abc
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.infra import Conector

class RepositoryInterface(abc.ABC):

    def __init__(self,conector:Conector):
        self._engine=conector.engine
        self._metadata=conector.metadata
      
        
    @abc.abstractmethod
    def insert(self, dados:dict):
        """
        Recebe um dicionario de dados e adiciona ao repositorio.
        
        """
        inserir= self.tabela.insert()
        
        with self.engine.begin() as conexao:
            
                resultado=conexao.execute(inserir, dados)
                id=resultado.inserted_primary_key[0]
                return id
                        
    @abc.abstractmethod
    def delete(self, id):
        """
        elimina um dados do repositorio pelo id
        """
        desativar= self.tabela.update().where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True)).values(ativo=False)
        
        with self.engine.begin() as conexao:
            resultado=conexao.execute(desativar).rowcount
            if resultado:
                return resultado
            logger.warning("falha ao desativar alvo nao encontrado ou já inativo")
            raise EntityNotFoundError('Alvo nao encontrado')
    
    
     
    @abc.abstractmethod  
    def  update(self, dados:dict,  id:int=None, email:str=None) -> int:
        """
        Actualiza os dados atraves do id 
        """
        if not email and not id:
            raise exc.IdentificatorError("nao foi passado nenhum identificador do  alvo (id ou email)")
        actualizar= self.tabela.update()
        if id==None:
            actualizar=actualizar.where(sa.and_(self.tabela.c.email==email, self.tabela.c.ativo==True))
        else:
             actualizar=actualizar.where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True))
        actualizar=actualizar.values(dados)
   
        with self.engine.begin() as conexao:
            res=conexao.execute(actualizar).rowcount
            
            if not res:
                raise exc.EntityNotFoundError(f" alvo nao encontrado")
            return list(dados.keys())
    
    
    @abc.abstractmethod   
    def search_id(self, id:int) -> dict:
         """
         busca os dados de um repositorio filtrando pelo id .
         """
         busca= sa.select(self.tabela).where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True))
        
         with self.engine.begin() as conexao:
            res=conexao.execute(busca).first()
            if not res:
                raise EntityNotFoundError("Alvo nao encontrado para o id fornecido")
            return res._asdict()
         
    @abc.abstractmethod
    def search_all(self) -> list[dict]:
        """
        Busca todos os dados do reposirorio e ordena pelo id
        """
        dados=list()
        busca= sa.select(self.tabela)
        busca=busca.where(self.tabela.c.ativo==True)
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                raise EmptyTableError("sua tabela  esta vazia")
            return dados
                
        
          
    @abc.abstractmethod
    def search_name(self, nome:str) -> list[dict]:
        """
        Faz uma busca parcial do texto fornecido retornando tudo que tenha ou paressa com o texto.
        """
        dados=list()
        busca= sa.select(self.tabela)
        busca=busca.where(sa.and_(
        self.tabela.c.nome.ilike(f'%{nome}%'),
        self.tabela.c.ativo==True))
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                raise EntityNotFoundError(f"nenhuma correspondencia para  '{nome}")
            return dados
        
        
    @property   
    @abc.abstractmethod
    def total_records(self) -> int:
        with self.engine.begin() as conexao:
            pegar_tot=sa.select(sa.func.count(self.tabela.c.id)).where(self.tabela.c.ativo==True)
            total= conexao.execute(pegar_tot.scalar())
            return total