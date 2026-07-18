import sqlalchemy as sa
from typing import Optional
import logging
from Projeto_xirico.exc import EntityNotFoundError

logger= logging.getLogger(__name__)


class messageBoxRepository:
    def __init__(self, conector):
        self.engine= conector.engine
        self.metadata= conector.metadata
        if 'messageBox' not in self.metadata.tables:
            logger.warning("Table 'messageBox' not found in metadata object")
            raise RuntimeError("""messageBox table not found in metadata.
Ensure that the same Connector object is used in both the InfraData and the messageBoxRepository class.""")
        self.tabela= self.metadata.tables["messageBox"]
       
        
        
    def add_(self, dados:dict) -> int:
        add=self.tabela.insert().values(dados)
        with self.engine.begin() as conexao:
             res=conexao.execute(add)
             return res.inserted_primary_key[0]


    def delete_by_status(self, status:str) -> int:
        delete= sa.delete(self.tabela).where(self.tabela.c.status == status)
        with self.engine.begin() as conexao:
            res=conexao.execute(delete)
            return res.rowcount
            
            
    def update(self, dados:dict, id:int) -> int:
        update= self.tabela.update().values(dados).where(self.tabela.c.message_id== id)
        with self.engine.begin() as conexao:
            res= conexao.execute(update).rowcount
            if not res:
                logger.warning('mensagem com id: %d nao encontrada', id)
                raise EntityNotFoundError("nenhuma mensagem com id {id}  foi encontrada  na caixa de mensagens ") 
            return res
            
            
    def _get(self, coluna: str, filtro: Optional[str]):
        stm= self.tabela.select().where(self.tabela.c[coluna]==filtro)
        with self.engine.begin() as conexao:
            res= conexao.execute(stm).fetchall()
            return [messege._asdict() for  messege in res]
        

    def get_by_status(self, status: str) -> list[dict]:
        return self._get(coluna= 'status', filtro= status)
            
            
    def get_by_id(self, id: int) -> dict:
            message= self._get(coluna= "message_id", filtro=id)
            if len(message)==0:
                raise EntityNotFoundError("nenhuma mensagem com id {id}  foi encontrada  na caixa de mensagens ")
            return message[0]


    def get_by_channel(self, channel: str) -> list[dict]:
            return self._get(coluna= "channel", filtro= channel)
            
            
    def get_by_retrys(self, limite: int):
        get_=self.tabela.select().where(self.tabela.c.retry >= limite)
        with self.engine.begin() as conexao:
            res=conexao.execute(get_)
            
            return [messege._asdict() for  messege in res]
            