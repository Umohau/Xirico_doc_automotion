import logging
from segurança import auditoria,gestor_sessao, PermissaoMixIn, otp
from repositorios import RepositorioOperadores #para testes locais
from infra import DuplicateError,PermissionDeniedError, EntityNotFoundError, InfraBanco, Conector

logger= logging.getLogger(__name__)
logging.basicConfig(
   format= '%(levelname)s: %(message)s: %(asctime)s',
   datefmt= '%H:%M',
   level=logging.DEBUG) 
   
   
class FiltroMixIn:
    def filtrar_dados(self,dados, filtros):
        dados_filtrados=dict()
        logger.debug("filtrando dados")
        for campo, valor in dados.items():
            if campo not in filtros:
                dados_filtrados[campo]= valor
        return dados_filtrados
           
class ServicoOperador(PermissaoMixIn, FiltroMixIn):
    def __init__(self, repo_operador:RepositorioOperadores):
        self._repo_operador=repo_operador
        
        
    @property
    def operador(self):
        return gestor_sessao.operador
        
    def adicionar_operador(self, dados, cod):
            """
            Adiciona um novo operador ao repositorio e registra auditoria.Apenas ADM pode adicionar operdores. 
            
            Args:
                dados(dict): dicionario de dados do novo operador.
                cod(int): codigo otp enviado ao email do novo operador para confirmar identidade.
                
            Returns:
                int: id do operador adicionado
                
            Raises:
                PermissionDeniedError: se operador que chama o metodo nao for ADM
                DuplicateError: se existir operador com os dados fornecidos.
                
                ExpiredOtpError: se o codigo otp tiver expirado.
                
                InvalidOtpError: se o codigo otp estiver errado.
            """
    
            operador_id= self.operador["id_operador"]
    
            # verifica se o operador é ADM
            if self.permissao(self.operador):
                if otp.verificar_otp(cod):
                    #verifica campos unicos
                    for chave, dado in dados.items():
                        valor={chave:dado}
                        self._repo_operador.verificar_unicidade(valor)
        
                    # insere os dados do novo operador no repositorio    
                    novo_id=self._repo_operador.inserir(dados) 
        
                   #registra o log de audiroria
                    auditoria.auditar(
                       operador_id,
                       operacao= "adicionar_operador",
                       detalhes= f"adicionou o operador id: {novo_id}")
        
                    return novo_id 
                    
            raise PermissionDeniedError("somente ADM pode adicionar novos operadores")        
            
    def pesquisar_nome(self, nome):
        """
        Busca operadores que tenham um nome similar ao fornecido.
        Filtra os resultados de duas formas: 
            se quem executa for ADM retorna todos campos exceto : senha.
            se quem executa nao for ADM retorna: email, nome, ativo, ADM.
         Faz o registro de auditoria
        
        
        Args:
            nome(str): nome completo ou parcial do operador.
            
        Returns:
            list[dict]: lista de dicionarios que contem dados dos operadores.
            
        Raises:
            EntityNotFoundError: se nao operdores que corespondam ao nome.
        """
        operador_id=self.operador.get("id_operador")
        filtro=[]
        dados_prontos=[]
        #busca operadores
        logger.debug("buscando operadores com nome similar a %s", nome)  
        dados= self._repo_operador.buscar_nome(nome)
        
        #verifica se é ADM e define filtros
        logger.debug("definindo filtros")
        if self.permissao(self.operador):
            filtro=["senha"]
            logger.debug("definido: filtro ADM")
        else:
            filtro=["identificacao", "senha", "telefone", "endereco"]
            logger.debug("definido: filtro comum ")   
            
       #registra auditoria     
        auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_nome",
                    detalhes=f"pesquisou pelo operador com  nome parecido a :{nome}")
        
        for operador in dados:
            dados_prontos.append(self.filtrar_dados(operador, filtro))
        return dados_prontos
        
        
    def pesquisar_id(self, id:int) -> dict:
        """
        Busca operador do id fornecido.
        Filtra o resultado e omite a senha .
         Faz o registro de auditoria
        
        
        Args:
            id(int): id do operador.
            
        Returns:
            dict:  dicionario com os dados do operador
            
        Raises:
            EntityNotFoundError: se nao encontrar o operdor do id fornecido.
            PermissionDeniedError: se o quem executa nao for ADM
        """
        operador_id=self.operador.get("id_operador") # para registro de log
        filtro=["senha"]
        
        # verifica permissao e busca operador
        if not self.permissao(self.operador):
            raise PermissionDeniedError("operacao restrita. busca exclusiva a ADMs.")
        logger.debug("buscando operador com  id: %d", id)  
        dados= self._repo_operador.buscar_id(id)
        
        #registra auditoria     
        auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_id",
                    detalhes=f"pesquisou pelo operador com id:{id}")
                    
        return self.filtrar_dados(dados, filtro)
        
       
    def pesquisar_operadores(self):
        """
        busca todos os operadores e filtra os dados.
        """
        operador_id= self.operador.get("id_operador")
        filtro=["identificacao", "senha", "telefone", "endereco"]
        dados_prontos=[]
        dados=self._repo_operador.buscar_tudo()
        #registra auditoria     
        auditoria.auditar(
            operador_id,
            operacao="pesquisar_operadores",
            detalhes=f"realizou uma pesquisa global")
        
        for operador in dados:
            dados_prontos.append(self.filtrar_dados(operador, filtro))
        return dados_prontos
        
    def desativar_operador(self, id_alvo: int) -> None:
      """
      Faz um sof delete do operador alvo (desativa).Somente operadores ADM podem eliminar operadores, registra a operacao em logs de auditoria.
      
      Args:
          id_alvo(int): id do operador a ser desativado.
          
      Returns:
          None
          
      Raises:
          EntityNotFoundError: se o operador alvo nao for encontrado.
          PermissionDeniedError: se o operador executor nao for ADM
      """
      
      operador_id= self.operador["id_operador"]
      
      #verifica se o operador é ADM
      if self.permissao(self.operador):
          try:
            # desativa o operador
            self._repo_operador.deletar(id_alvo)
            
            #registra auditoria
            auditoria.auditar(
                operador_id, 
                "desativar_operador",
                f"desativou o operador com id:{id_alvo}")
            return
          except EntityNotFoundError:
             raise
          
      raise PermissionDeniedError("somente ADM pode desativar operadores")       


    def mudar_nome(self, nome:str) -> list:
        """
        Altera o nome do operador para o nome fornecido, um operador so pode actualizar seu proprio nome.Registra auditotia da accao.
        
        Args:
            nome(str): novo nome do operador.
            
        Returns:
            None
        """
        operador_id= self.operador.get("id_operador")
        
        dado={"nome": nome}
        logger.debug("actualizando nome")
        self._repo_operador.actualizar( operador_id, dado)
        auditoria.auditar(
            operador_id,
            operacao="mudar_nome",
            detalhes="editou seu nome")
            
            
    def actualizar_identificacao(self, id_alvo,codigo, ident:str) -> None:
        """
        Actualiza a identifucacao do operador alvo, só pode ser executdo por um adm e concluida apos verificao com otp do operador alvo para confirmar.
        
        Args:
            id_alvo(int): id do operador alvo da actulizacao.
            codigo(int): codigo otp enviado ao operador alvo para confirmacao.
            ident(str): nova identificao do operador.
            
        Returns:
            None
            
        Raises:
            EntityNotFoundError: se o operador alvo nao for encontrado.
            InvalidOtpError: se o codigo otp estiver errado.
            ExpiredOtpError: se o otp tiver expirado.
        """
        operador_id=self.operador.get("id_operador")
        
        #verifica se e ADM
        if not self.permissao(self.operador):
            raise PermissionDeniedError("apenas adm pode executar esta accao")
        if otp.verificar_otp(codigo):
            dado={"identificacao":ident}
            logger.debug("actualizando identificacao")
            self._repo_operador.actualizar(id_alvo, dado)
            auditoria.auditar(
                operador_id,
                operacao="actualizar_identificacao",
                detalhes=f"actualizou a identificacao do operador id: {id_alvo}") 
                        
            
URL_CONEXAO="sqlite:///xirico.db"
CONECTOR= Conector(URL_CONEXAO)
InfraBanco(CONECTOR)
a= RepositorioOperadores(CONECTOR)
ser=ServicoOperador(a)
otp.gerar_otp()
otp.enviar_codigo("muhau")

r= int(input("otp: "))
q=ser.actualizar_identificacao(1, r,  "445678754787332")
print(q)