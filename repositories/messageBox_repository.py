import sqlalchemy as sa
from typing import optional


class messageBoxRepository:
    def __init__(self, conector):
        self.engine= conector.engine
        self.metadata= conector.metadata
        if 'operators' not in self.metadata.tables:
            logger.warning("Table 'messageBox' not found in metadata object")
            raise RuntimeError("""messageBox table not found in metadata.
Ensure that the same Connector object is used in both the InfraData and the OperatorsRepository class.""")
        self.tabela= self.metadata.tables["messageBox"]
       
        
        
    def add_(dados:dict) -> int:
        add=self.tabela.insert(dados)
        with self.engine.begin() as conexao:
             res=conexao.execute(add)
             return res.inserted_primary_key[0]


    def delete_by_status(status:str) -> int:
        delete= sa.delete().where(self.tabela.c.status == status)
        with self.engine.begin() as conexao:
            res=conexao.execute(delete)
            return re.rowcount
            
            
    def update(dados:dict, id:int) -> int:
        update= sa.update().values(dados).where(self.tabela.id== id)
        with self.engine.begin() as conexao:
            res= conexao.execute(update)

    def _get(coluna: str, filtro: optional[str]):
        stm= self.tabela.select().where(self.tabela.c[coluna]==filtro)
        with self.engine.begin() as conexao:
            res= conexao.execute(stm).fetchall()
            return [dict(messege) for  messege in res]
        

    def get_by_status(status: str) -> list[dict]:
        return self._get(coluna= 'status', filtro= status)
            
            
    def get_by_id(id: int) -> dict:
            return self._get(coluna= "id", filtro=id)[0]


    def get_by_channel(channel: str) -> list[dict]:
            return self._get(coluna= "channel", filtro= channel)