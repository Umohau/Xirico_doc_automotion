import sqlalchemy as sa
import abc
import logging
from infra import Conector, EntityNotFoundError, DuplicateError, EmptyTableError, InfraBanco

logger1= logging.getLogger(__name__)
logging.basicConfig(
   format= '%(levelname)s: %(message)s: %(asctime)s',
   datefmt= '%H:%M',
   level=logging.DEBUG)
   
               
class Operacoes(abc.ABC):
    def __init__(self,conector:Conector):
        self.engine=conector.engine
        self.metadata=conector.metadata
      
        
    @abc.abstractmethod
    def inserir(self, dados:dict):
        """
        Recebe um dicionario de dados e adiciona ao repositorio
        """
        pass
        
                        
    @abc.abstractmethod
    def deletar(self, id):
        """
        elimina um dados do repositorio pelo id
        """
        pass
    
    
     
    @abc.abstractmethod  
    def  actualizar(self, id:int, dados:dict) -> int:
        """
        Actualiza os dados atraves do id 
        """
        pass
    
    @abc.abstractmethod   
    def buscar_id(self, id:int) -> dict:
         """
         busca os dados de um repositorio filtrando pelo id .
         """
         pass
         
    @abc.abstractmethod
    def buscar_tudo(self) -> list[dict]:
        """
        Busca todos os dados do reposirorio e ordena pelo id
        """
        pass
        
          
    @abc.abstractmethod
    def buscar_nome(self, nome:str) -> list[dict]:
        """
        Faz uma busca parcial do texto fornecido retornando tudo que tenha ou paressa com o texto.
        """
        pass
        
    @property   
    @abc.abstractmethod
    def total_registros(self) -> int:
        pass
    
    
class RepositorioClientes(Operacoes):
    def __init__(self, conector):
        super().__init__(conector)
        if 'clientes' not in self.metadata.tables:
            logger1.warning("Tabela clientes nao encontrada no objeto metadata")
            raise RuntimeError("""tabela clientes nao encontrado metadata\n Certifique-se de:\n
            1. Executar o Inicializador antes de criar objetos RepositorioClientes.\n
            2. Usar o MESMO objeto Conector tanto no Inicializador quanto na classe RepositorioClientes.""")
        self.tabela= self.metadata.tables["clientes"]
    
    
    def inserir(self, dados:dict) -> int:
        '''
        Insere dados na tabela clientes.
        
        Args:
            dados(dict): dados inseridos na tabela
        Returns:
            int: id da nova insersao
        
        Raises:
            DuplicteError: se o cliente ja existir
        '''
      
        inserir= self.tabela.insert()
        
        with self.engine.begin() as conexao:
            try:
                resultado=conexao.execute(inserir, dados)
                id=resultado.inserted_primary_key[0]
                logger1.info('Cliente %s inserido com id %d', dados.get('nome'),id)
                return id
            except sa.exc.IntegrityError as e:
                logger1.warning('tentativa de inserir cliente ja existente')
                raise DuplicateError('já existe um cliente com os dados fornrcidos') from e
                
                
    def deletar(self, id:int) -> int:
        '''
        Deleta um cliente da tabela clientes
        
        Args:
            id(int): id do cliente deletado
            
        Retunrs:
           int: numero de clientes deletados
        
        Raises:
            EntityNotFoundError: se o id do cliente nao for encontrado
        '''
        deletar= self.tabela.delete().where(self.tabela.c.id==id)
        
        with self.engine.begin() as conexao:
            resultado=conexao.execute(deletar).rowcount
            
            if resultado:
                logger1.info('cliente com id %d deletado com sucesso', id)
                return resultado
            logger1.warning("falha ao deletar cliente de id  %d -nao encontrado", id)
            raise EntityNotFoundError('cliente nao encontrado ')
            
        
    def actualizar(self, id:int, dados:dict) ->list:
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
        actualizar= self.tabela.update().where(self.tabela.c.id==id)
        actualizar=actualizar.values(dados)
    
        with self.engine.begin() as conexao:
            res=conexao.execute(actualizar).rowcount
            
            if not res:
                logger1.warning("falha ao tentar  actulizar dados para cliente id: %d-nao encontrado", id)
                raise EntityNotFoundError(f"cliente com id {id} nao encontrado")
            
            logger1.info("cliente id: %d actualizado com sucesso- campos: %s", id , list(dados.keys()))
            return list(dados.keys())
       
       
    def buscar_id(self, id:int) -> dict:
        busca= sa.select(self.tabela).where(self.tabela.c.id==id)
    
        with self.engine.begin() as conexao:
            res=conexao.execute(busca).first()
            if not res:
                logger1.warning("a busca por id nao encontrou um cliente com id:%d", id)
                raise EntityNotFoundError("nenhum cliente com o id fornecido")
            logger1.info("busca do cliente id:%d realizada com exito", id)
            return res._asdict()
            
        
    def buscar_tudo(self) -> list[dict]:
        """
        busca clientes na tabela clientes, retorna todos os registros da tabela
        
        Returns:
            list[dict]: uma lista com dicionarios contendo dados resultados da busca
          
        Raises:
            EmptyTableError: se a tabela estiver vazia
        """
        dados=list()
        busca= sa.select(self.tabela) 
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                logger1.warning("tentativa de buscar dados numa tabela (clientes) vazia")
                raise EmptyTableError("sua tabela clientes esta vazia")
            logger1.info("Abusca por clientes retornou %d resultados", len(dados))     
            return dados
        
        
    def buscar_nome(self, nome:str) ->list[dict]:
        """
        busca um cliente com o nome similar ao nome fornecido no argumento nome.
     
       Args:
          nome(str): nome alvo da busca (pode ser parte do nome)
       
       Returns:
          list[dict]: lista de dicionarios com dados resultados da busca
          
        Raises:
          EntityNotFoundError: se  nenhum nome nos registros corresponder ao nome fornecido.
          
        """
        dados=list()
        busca= sa.select(self.tabela)
        busca=busca.where(
        self.tabela.c.nome.ilike(f'%{nome}%'))    
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                logger1.warning("a busca por nome nao encontrou nenhum cliente com nome parecido a '%s' ", nome)
                raise EntityNotFoundError(f"nenhum cliente corrsponde ao nome '{nome}")
            logger1.info("A busca por nome retornou %d resultado de clientes para '%s'", len(dados), nome)
            return dados
        
        
    @property
    def total_registros(self):
        """
        Consulta quantos clientes tem no banco(na tabela clientes)
        
        Returns:
            int: A quntidade total de clientes no banco
        """
        with self.engine.begin() as conexao:
            total= conexao.execute(sa.func.count(self.tabela.c.id)).scalar()
            return total
        

    
class RepositorioOperadores(Operacoes):
    def __init__(self, conector):
        super().__init__(conector)
        if 'operadores' not in self.metadata.tables:
            logger1.warning("Tabela operadores nao encontrada no objeto metadata")
            raise RuntimeError("""tabela operadores nao encontrado metadata\n Certifique-se de:\n
            1. Executar o Inicializador antes de criar objetos RepositorioOperadores.\n
            2. Usar o MESMO objeto Conector tanto no Inicializador quanto na classe RepositorioOperadores.""")
        self.tabela= self.metadata.tables["operadores"]
    
    
    def inserir(self, dados:dict) -> int:
        '''
        Insere dados na tabela operadores
        
        Args:
            dados(dict): dados inseridos na tabela
        Returns:
            int: id da nova insersao
        
        Raises:
            DuplicteError: se o operador já existir
        '''
        inserir= self.tabela.insert()
        
        with self.engine.begin() as conexao:
            try:
                resultado=conexao.execute(inserir, dados)
                id=resultado.inserted_primary_key[0]
                logger1.info('Operador %s inserido com id %d', dados.get('nome'),id)
                return id
            except sa.exc.IntegrityError as e:
                logger1.warning('tentativa de inserir Operador ja existente')
                raise DuplicateError('já existe um operador com os dados fornrcidos') from e
                
        
    def deletar(self, id:int) -> int:
        '''
        Faz um sof delete. Alterando a coluna activo para False
        
        Args:
            id(int): id do operador deletado
            
        Retunrs:
            int: numero de operadores deletados
        
        Raises:
            EntityNotFoundError: se o operador nao for encontrado.
        '''
        deletar= self.tabela.update().where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True)).values(ativo=False)
        
        with self.engine.begin() as conexao:
            resultado=conexao.execute(deletar).rowcount
            if resultado:
                logger1.info('operador com id %d desativado com sucesso', id)
                return resultado
            logger1.warning("falha ao desativar operador de id  %d -nao encontrado ou já inativo", id)
            raise EntityNotFoundError('operador nao encontrado ')
        
        
    def actualizar(self, id:int, dados:dict) ->list:
        """
        Actualida dados de um operador especificado pelo id, em campos fornecidos no argumento dados.
        
        Args:
            id(int): id do operador a receber actualizacao
            dados(dict): novos dados do operador
       
       Returns:
            list:lista dos campos actualizdos
        
        Raises:
            EntityNotFoundError: se nenhum operador for encontrado com o id fornecido
            
        """
        actualizar= self.tabela.update().where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True)) 
        actualizar=actualizar.values(dados)
    
        with self.engine.begin() as conexao:
            res=conexao.execute(actualizar).rowcount
            
            if not res:
                logger1.warning("falha ao tentar  actulizar dados para operado id: %d-nao encontrado", id)
                raise EntityNotFoundError(f"operador com id {id} nao encontrado")
            
            logger1.info("operador id: %d actualizado com sucesso- campos: %s", id , list(dados.keys()))
            return list(dados.keys())
        
        
    def buscar_id(self, id:int) -> dict:
        """
        Busca um operdor pelo id
        
        Args:
            id(int): id do operador a buscar
            
        Returns:
            dict: dicionario com os dados do operador
        
        Raises:
            EntityNotFound: se nenhum operador for encontrado com o id fornecido
        """
        
        busca= sa.select(self.tabela).where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True))
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca).first()
            if not res:
                logger1.warning("a busca por id nao encontrou nenhum operador com id:%d", id)
                raise EntityNotFoundError("nenhum operador com o id fornecido")
            logger1.info("busca do operador id:%d realizada com exito", id)
            return res._asdict()
        
        
    def buscar_tudo(self) -> list[dict]:
        """
        busca operadores na tabela operdores, retorna todos os registros da tabela
        
        Returns:
            list[dict]: uma lista com dicionarios contendo dados resultados da busca
          
        Raises:
            EmptyTableError: se a tabela estiver vazia
        """
        dados=list()
        busca= sa.select(self.tabela)
        busca=busca.where(self.tabela.c.ativo==True)
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                logger1.warning("tentativa de buscar dados numa tabela (operadores) vazia")
                raise EmptyTableError("sua tabela operadores esta vazia")
            logger1.info("A busca por operdores retornou %d resultados", len(dados))     
            return dados
                
        
        
    def buscar_nome(self, nome:str) ->list[dict]:
        """
        busca um operdor com o nome similar ao nome fornecido no argumento nome.
     
       Args:
          nome(str): nome alvo da busca(pode ser parte do nome).
       
       Returns:
          list[dict]: lista de dicionarios com dados resultados da busca
          
        Raises:
          EntityNotFoundError: se  nenhum nome nos registros corresponder ao nome fornecido.
          
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
                logger1.warnig("a busca por nome nao encontrou nenhum operdor com nome parecido a '%s' ", nome)
                raise EntityNotFoundError(f"nenhum operador corrsponde ao nome '{nome}")
            logger1.info("A busca por nome retornou %d resultado de operadores para '%s'", len(dados), nome)
            return dados
        

    def busca_email(self, email:str) -> dict:
        """
        Busca um operador pelo email
        
        Args:
            email(str): email alvo da busca.
            
       Returns:
            dict: dados do eperador resultados da busca.
            
        Raises:
            EntityNotFoundError: se o operador nao for encontrado
            
        """
        busca= sa.select(self.tabela).where(sa.and_(
        self.tabela.c.email==email,
        self.tabela.c.ativo==True)) 
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            resultado=res.first()
            if not resultado:
                logger1.warning("operador com email fornecido nao encontrado")
                raise EntityNotFoundError("operador com o email fornrcido nao encontrado")
            logger1.info("operador localizado pelo email fornecido")    
            return resultado._asdict()

    def buscar_inativo(self, email):
            """
            Busca um operador desativado no banco usando seu email.
            
            Args:
                email(str): email do operador inativo.
                
             Returns:
                 bool:True se a buscar encontrar operador.
            
            Raises:
                EntityNotFoundError: se a buscs nao encontra o operador.   
            """
            
            busca= sa.select(self.tabela).where(sa.and_(self.tabela.c.ativo==False, self.tabela.c.email== email))      
            
            with self.engine.begin() as conexao:
                logger1.debug("buscando operador inativo ")
                res=conexao.execute(busca)
                operador= res.first()
                if not operador:
                    raise EntityNotFoundError("operador inativo nao encontrado")
                logger1.info("sucesso: busca de operador inativo concluida.")     
                return operador
                
    def pegar_senha(self, email):
        """
        Busca a senha do operador do email fornecido.
        
        Args:
            email(str): email do operador da senha alvo.
            
        Returns:
            bytes: hash com salt da senha.
        """
        pegar_senha=sa.select(self.tabela.c.senha).where(sa.and_(self.tabela.c.email==email, self.tabela.c.ativo==True))
        
        with self.engine.begin() as conexao:
            logger1.debug("Buscando senha do operador.")
            res=conexao.execute(pegar_senha)
            senha= res.first()
            logger1.info("sucesso: busca da senha finalizada")
            return senha
            
                                    
    @property
    def total_registros(self):
        """
        Consulta quantos operadores tem no banco(na tabela operadores)
        
        Returns:
            int: A quntidade total de operadores no banco
        """
        with self.engine.begin() as conexao:
            pegar_tot=sa.select(sa.func.count(self.tabela.c.id)).where(self.tabela.c.ativo==True)
            total= conexao.execute(pegar_tot.scalar())
            return total
        
        
    
class RepositorioAves(Operacoes):
    def __init__(self, conector):
        super().__init__(conector)
        if 'aves' not in self.metadata.tables:
            logger1.warning("Tabela aves nao encontrada no objeto metadata")
            raise RuntimeError("""tabela aves nao encontrado no metadata\n Certifique-se de:\n
            1. Executar o Inicializador antes de criar objetos RepositorioAves.\n
            2. Usar o MESMO objeto Conector tanto no Inicializador quanto na classe RepositorioAves.""")
        self.tabela= self.metadata.tables["aves"]
  
      
    def inserir(self, dados:dict) -> int:
        '''
        Insere dados na tabela aves.
        
        Args:
            dados(dict): dados inseridos na tabela
        Returns:
            int: id da nova insersao
        
        Raises:
            DuplicteError: se a ave já existir
        '''
        inserir= self.tabela.insert()
        
        with self.engine.begin() as conexao:
            try:
                resultado=conexao.execute(inserir, dados)
                id=resultado.inserted_primary_key[0]
                logger1.info('Ave %s inserida com id %d', dados.get('nome_comum'),id)
                return id
            except sa.exc.IntegrityError as e:
                logger1.warning('tentativa de inserir Ave  ja existente')
                raise DuplicateError('já existe uma Ave com os dados fornrcidos') from e
                
        
    def deletar(self, id:int) -> int:
        '''
        Deleta uma ave da tabela aves
        
        Args:
            id(int): id da ave deletada
            
        Retunrs:
           int: numero de aves deletadas
        
        Raises:
            EntityNotFoundError: se o id da ave nao for encontrado
        '''
        deletar= self.tabela.delete().where(self.tabela.c.id==id)
        
        with self.engine.begin() as conexao:
            resultado=conexao.execute(deletar).rowcount
            
            if resultado:
                logger1.info('Ave com id %d deletado com sucesso', id)
                return resultado
            logger1.warning("falha ao deletar Ave de id  %d -nao encontrado", id)
            raise EntityNotFoundError('ave  nao encontrada')
        
        
    def actualizar(self, id:int, dados:dict) ->list:
        """
        Actualida dados de uma ave especificada pelo id, em campos fornecidos no argumento dados.
        
        Args:
            id(int): id da ave a receber actualizacao
            dados(dict): novos dados da ave
       
       Returns:
            list:lista dos campos actualizdos
        
        Raises:
            EntityNotFoundError: se nenhuma ave for encontrada com o id fornecido
            
        """
        actualizar= self.tabela.update().where(self.tabela.c.id==id)
        actualizar=actualizar.values(dados)
    
        with self.engine.begin() as conexao:
            res=conexao.execute(actualizar).rowcount
            
            
            if not res:
                logger1.warning("falha ao tentar  actulizar dados para ave id: %d-nao encontrado", id)
                raise EntityNotFoundError(f"ave com id {id} nao encontrada")
            
            logger1.info("ave id: %d actualizada com sucesso- campos: %s", id , list(dados.keys()))
            return list(dados.keys())
       
       
    def buscar_id(self, id:int) -> dict:
        """
        Busca uma ave pelo id
        
        Args:
            id(int): id da ave a buscar
            
        Returns:
            dict: dicionario com os dados da ave
        
        Raises:
            EntityNotFound: se nenhuma ave for encontrada com o id fornecido
        """
        busca= sa.select(self.tabela).where(self.tabela.c.id==id)
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca).first()
            if not res:
                logger1.warning("a busca por id nao encontrou nenhuma ave com id:%d", id)
                raise EntityNotFound("nenhuma ave com o id fornecido")
            logger1.info("busca da ave id:%d realizada com exito", id)
            return res._asdict()
        
    def buscar_tudo(self) -> list[dict]:
        """
        busca aves na tabela aves, retorna todos os registros da tabela
        
        Returns:
            list[dict]: uma lista com dicionarios contendo dados resultados da busca
          
        Raises:
            EmptyTableError: se a tabela estiver vazia
        """
        dados=list()
        busca= sa.select(self.tabela) 
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                logger1.warning("tentativa de buscar dados numa tabela (aves) vazia")
                raise EmptyTableError("sua tabela aves esta vazia")
            logger1.info("Abusca por aves retornou %d resultados", len(dados))     
            return dados
                
        
        
    def buscar_nome(self, nome:str) ->list[dict]:
        """
        busca uma ave com o nome similar ao nome fornecido no argumento nome.
     
       Args:
          nome(str): nome alvo da busca, (pode ser parte do  nome).
       
       Returns:
          list[dict]: lista de dicionarios com dados resultados da busca
          
        Raises:
          EntityNotFoundError: se  nenhum nome nos registros corresponder ao nome fornecido.
          
        """
        dados=list()
        busca= sa.select(self.tabela)
        busca=busca.where(sa.or_(
        self.tabela.c.nome_comum.ilike(f"%{nome}%"),
        self.tabela.c.nome_cientifico.ilike(f"%{nome}%"))
        )
        
        with self.engine.begin() as conexao:
            res=conexao.execute(busca)
            for resultado in res.fetchall():
                dados.append(resultado._asdict())
            if not dados:
                logger1.warnig("a busca por nome nao encontrou nenhuma ave com nome parecido a '%s' ", nome)
                raise EntityNotFoundError(f"nenhuma ave corrsponde ao nome '{nome}")
            logger1.info("A busca por nome retornou %d resultado de aves para '%s'", len(dados), nome)
            return dados

            
    @property
    def total_registros(self):
            """
            Consulta quantas aves tem no banco(na tabela aves)
            
            Returns:
                int: A quntidade total de aves no banco
            """
            with self.engine.begin() as conexao:
                total= conexao.execute(sa.func.count(self.tabela.c.id)).scalar()
                return total



  
dados2={'nome': 'umohau', 'identificacao': '8368925', 'telefone': '8509082', 'email': 'muhauhara8374@gmail.com', 'endereco': 'moamba, matadouro',
'senha':'muhau333',
'ADM':True, 'ativo':True}      


