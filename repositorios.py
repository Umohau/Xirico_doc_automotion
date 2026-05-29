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
        desativar= self.tabela.update().where(sa.and_(self.tabela.c.id==id, self.tabela.c.ativo==True)).values(ativo=False)
        
        with self.engine.begin() as conexao:
            logger1.debug("desativando operador")
            resultado=conexao.execute(desativar).rowcount
            if resultado:
                logger1.info('operador com id %d desativado com sucesso', id)
                return resultado
            logger1.warning("falha ao desativar operador de id  %d -nao encontrado ou já inativo", id)
            raise EntityNotFoundError('operador nao encontrado ')
        
        
    def actualizar(self, id:int, dados:dict) ->list:
        """
        Actualida dados de um operador activo especificado pelo id, em campos fornecidos no argumento dados.
        
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

        
    def reactivar(self,  id:int) ->bool:
        """
        Alter o status do operador no campo ativo para True.
        
        Args:
            id(int): id do operador a reactivar
            
        Returns:
            bool: True se reactivado.
            
       
        """   
        reactivar= self.tabela.update().values(ativo=True).where(self.tabela.c.id==id)
        
        with self.engine.begin() as conexao:
            res=conexao.execute(reactivar)
            if res.rowcount:
                return True
                                                       
                                                        
        
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
                 dict: dicionario com os dados do operador.
            
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
                return operador._asdict()
                
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
            
    def verificar_unicidade(self, dados:dict) -> bool:
        """
        Verifica se o valor da chave do par/chave do argumento dados existe na tabela de operadores.
        
        Args:
            dados(dict): um unico par chave/valor.É o dado que se pretende verificar.
        
        Returns:
            True: se o dado for unico(ainda nao existe na tabela operadores).
            
        Raises:
            DuplicateError: se o dado existir
        """
        ignorados=["nome", "senha", "endereco", "ativo", "ADM"] #campos nao sujeitos a verificacao de unicidadde
        campo= next(iter(dados))
        coluna=getattr(self.tabela.c, campo )
        valor= next(iter(dados.values()))
        if campo not in ignorados:
            busca= sa.select(self.tabela).where(coluna== valor)
            #realiza a busca no banco
            logger1.debug("verificando unicidade de %s", campo)
            with self.engine.begin() as conexao:
                res=conexao.execute(busca).first()
                if not res:
                    logger1.debug("sucesso: %s unico", campo)
                    return True
                logger1.debug("concluida: %s nao é unico", campo)
                raise DuplicateError(f"ja existe o um operador com o {campo} fornecido")
            
            
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


class RepositorioOrders:
    def __init__(self, conector):
        self.engine=conector.engine
        self.metadata=conector.metadata
        if 'orders' not in self.metadata.tables:
            logger1.warning("Tabela orders nao encontrada no objeto metadata")
            raise RuntimeError("""tabela orders nao encontrada no metadata\n Certifique-se de:\n
            1. Usar o MESMO objeto Conector tanto no InfraBanco quanto na classe RepositorioOrders.""")
        self.tabela= self.metadata.tables["orders"]
        
    
    def adicionar(self, order_dados:dict) -> int:
        """
        Adiciona um novo pedido em orders.
        
        Args:
            order_dados(dict): dicionario com os dados do novo pedido.
            
        Returns:
            inr: id do novo pedido
            
        Raises:
            IntegrityError: se uma chave estrangeira foi inválida.
        """
        inserir= self.tabela.insert()    
        with self.engine.begin() as conexao:
            try:
                logger1.debug("process: adicionando um novo pedido")
                res=conexao.execute(inserir, order_dados)    
                id= res.inserted_primary_key[0]
                logger1.info("sucesso: novo pedido adicionado com id:%d", id)
            except sa.exc.IntegrityError as e:
                logger1.warning("falha: ao inserir novo  pedido em orders\n Param: %s", e.params)
                raise
                

    def deletar(self, order_id: int) -> int:
        """
        Deleta um pedido em orders.
        
        Args:
            order_id(int): id do pedido a ser eliminado.
            
        Returns:
           int: o numero das  linhas afetadas.
           
        Raises:
            EntityNotFoundError: se o podido nao for encontrado.
        """
        deletar= self.tabela.delete().where(self.tabela.c.order_id== order_id)
        
        with self.engine.begin() as conexao:
            logger1.debug("process: eliminando pedido %d ", order_id)
            res=conexao.execute(deletar).rowcount
            if not res:
                logger1.info("falha: nao foi possivel eliminar o pedido. nao encontrado")
                raise EntityNotFoundError(f"pedido com id {order_id} nao encontrado")
            logger1.info("sucesso: pedido %d eliminado", order_id)
            return res
            
            
    def actualizar(self,order_id: int, novos_dados: dict) -> int:
        """
        Actualiza os dados do pedido substituindo os campos pelos novos dados do argumento dados.
        
        Args:
            order_id(int): id do pedido alvo.
            novos_dados(dict): dicionario com os novos dados.
            
        Return:
            int: numero de pedidos actualizados.
             
        Raises:
            EntityNotFoundError: se  nao encontrar o pedido alvo.
            IntegrityError: se os novos dados tiverem um ForeignKeys invalido
        """
        actual=self.tabela.update().where(self.tabela.c.order_id==order_id)
        actual=actual.values(novos_dados)
        
        with self.engine.begin() as conexao:
            logger1.debug("process: actualizando dados do pedido %d", order_id)
            res=conexao.execute(actual).rowcount
            if not res:
                logger1.info("falha: falha oa actualizar %s pedido %d nao encontrado.", list(novos_dados.keys()), order_id)
                raise EntityNotFoundError(f"pedido {order_id} nao encontrado")
            logger1.info("sucesso: pedido %d actualizado. Campos: %s" , order_id, list(novos_dados.keys()))
            return res
            
            
    def buscar_pedidos(self) -> list[dict]:
        """
        Busca todos os pedidos na tabela orders .
        
        Returns:
            list[dict]: uma lista de dicionarios que contem os dados de cada pedido.
            
        Raises:
            EmptyTableError: se a tabela orders estiver vazia.
        """
        dados=list()
        busca= sa.select(self.tabela)
        
        with self.engine.begin() as conexao:
            res= conexao.execute(busca).fetchall()
            
            # converte cada tupla do 
            #objeto row em um dicionario
            # e adiciona  na lista dados
            for resultado in res:
                dados.append(resultado._asdict())
                
            # verifica se ha resultados
            if not res:
                logger1.warning("falha: tabela orders vazia")
                raise EmptyTableError("sua tabela orders esta vazia")
            logger1.info("sucesso: a busca  retornou %d resultdos", len(dados))   
            return dados
            
            
    def buscar_order_oid(self, order_id: int) -> dict:
        """
        Busca um pedido pelo id do pedido na tabela orders.
        
        Args:
            order_id(int): id do pedido alvo da busca.
            
        Return:
            dict: dicionario com os dados do pedido.
            
        Raises:
            EntityNotFoundError: se o pedido nao for encontrado.
        """
        busca= sa.select(self.tabela).where(self.tabela.c.order_id== order_id)
        
        with self.engine.begin() as conexao:
            logger1.debug("process: buscando pedido %d", order_id)
            res= conexao.execute(busca).first()
            
            if not res:
                logger1.warning("falha: pedido %d nao encontrado", order_id)
                raise EntityNotFoundError("pedido nao encontrado")
                
            logger1.info("sucesso: busca do pedido %d concluida", order_id)
            return res._asdict()
            

    def buscar_orders_cid(self, cliente_id: int) -> list[dict]:
        """
        Busca todos pedidos de um cliente pelo id do cliente.
        
        Args:
            cliente_id(int): id do cliete alvo
            
        Returns:
            list[dict]: lista de dicionarios com os dados dos pedidos do cliete ordenados pela data de registo do mais recente ao mais antigo.
            
        Raises:
            EntityNotFoundError: se o cliente nao possue nenhum pedido ate o momento de execucao do metodo
        """
        dados=list() 
        busca= sa.select(self.tabela).order_by(sa.desc(self.tabela.c.registado_at))
        busca=busca.where(self.tabela.c.cliente_id== cliente_id)
        
        with self.engine.begin() as conexao:
            logger1.debug("precess: buscando pedidos do cliente id: %d", cliente_id)
            res= conexao.execute(busca).fetchall()
            if not res:
                logger1.warning("falha: o cliente id: %d nao possue pedidos", cliente_id)
                raise EntityNotFoundError("o cliente nao possue pedidos")
            for resultado in res:
                dados.append(resultado._asdict())
            logger1.info("secesso: a busca retornou %d pedidos do cliente id: %d", len(dados), cliente_id)
            return dados
            

    def buscar_order_gid(self, operador_id: int) -> list[dict]:
        """
        Busca os pedidos gerenciados por um operador especifico.
        
        Args:
            operador_id(int): id do operadir alvo.
            
        Returns:
            list[dict]: lista de dicionarios com os dados de cada pedido gerenciado pelo operador, ordenados por data de registro do mais recente ao mais antigo.
            
        Raises:
            EntityNotFoundError: se o operador nao gerenciou nenhum pedido ate o momento de execucao do metodo
        """
        dados=list() 
        busca= sa.select(self.tabela).order_by(sa.desc(self.tabela.c.registado_at))
        busca=busca.where(self.tabela.c.gestor_id== operador_id)
        
        with self.engine.begin() as conexao:
            logger1.debug("precess: buscando pedidos do gestor id: %d", operador_id)
            res= conexao.execute(busca).fetchall()
            if not res:
                logger1.warning("falha: o operador id: %d ainda nao gerenciou  pedidos ", operador_id)
                raise EntityNotFoundError("o operadot nao possue pedidos por si gerenciados")
            for resultado in res:
                dados.append(resultado._asdict())
            logger1.info("secesso: a busca retornou %d pedidos gerenciados pelo operador id: %d", len(dados), operador_id)
            return dados
            
            
class RepositorioExportacoes:
    def __init__(self, conector):
        self.engine=conector.engine
        self.metadata=conector.metadata
        if 'exportacoes' not in self.metadata.tables:
            logger1.warning("Tabela exportacoes nao encontrada no objeto metadata")
            raise RuntimeError("""tabela exportacoes nao encontrada no metadata\n Certifique-se de:\n
            1. Usar o MESMO objeto Conector tanto no InfraBanco quanto na classe RepositorioOrders.""")
        self.tabela= self.metadata.tables["exportacoes"]
        
      
