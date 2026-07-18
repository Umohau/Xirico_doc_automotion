from Projeto_xirico.interfaces.repository_interfaces import BaseRepository

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
             