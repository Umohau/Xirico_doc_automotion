import exc
import os
import logging
from dotenv import load_dotenv


#pega o nivel do logging
load_dotenv("config.env")
log_level_str= os.getenv("LOG_LEVEL", "DEBUG")
log_level= getattr(logging, log_level_str)


#configura o logging
logger= logging.getLogger(__name__)
logging.basicConfig(
    format= "%(levelname)s: %(name)s: %(message)s: %(asctime)s",
    datefmt="%H:%M",
    level= log_level
)


class FiltroMixIn:
    def filtrar_dados(self,dados, filtros):
        dados_filtrados=dict()
        logger.debug("filtrando dados")
        for campo, valor in dados.items():
            if campo not in filtros:
                dados_filtrados[campo]= valor
        return dados_filtrados
        
class Operador(FiltroMixIn):
    def __init__(self, repo_operador, autenticador, auditoria, perfil):
        self._repo_operador= repo_operador
        self._autenticador= autenticador
        self._auditoria= auditoria
        self._perfil= perfil
        
        
    def adicionar_operador(self, dados:dict, cod:str) -> int:
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
                
            Note: As excecoes de otp sao lancadas pelo autenticador.
            """
    
            # verifica se o operador é ADM
            if self._perfil.ADM:
                if self._autenticador.verificar_otp(cod):
                    #verifica campos unicos
                    for chave, dado in dados.items():
                        valor={chave:dado}
                        self._repo_operador.verificar_unicidade(valor)
        
                    # insere os dados do novo operador no repositorio    
                    novo_id=self._repo_operador.inserir(dados) 
        
                   #registra o log de audiroria
                    self._auditoria.auditar(
                       self._perfil.id,
                       operacao= "adicionar_operador",
                       detalhes= f"adicionou o operador id: {novo_id}")
        
                    return novo_id 
                    
            raise exc.PermissionDeniedError("somente ADM pode adicionar novos operadores") 
            
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
        operador_id=self._perfil.id
        
          #verifica se e ADM
        if not self._perfil.ADM:
            raise exc.PermissionDeniedError("apenas adm pode executar esta accao")
        if self._autenticador.verificar_otp(codigo):
            dado={"identificacao":ident}
            logger.debug("actualizando identificacao")
            self._repo_operador.actualizar(id_alvo, dado)
            self._auditoria.auditar(
                operador_id,
                operacao="actualizar_identificacao",
                detalhes=f"actualizou a identificacao do operador id: {id_alvo}")
                
                
    def actualizar_endereco(self, id_alvo, endereco, codigo):
        operador_id=self._perfil.id
        
        #verifica se e ADM
        if not self._perfil.ADM:
            raise exc.PermissionDeniedError("apenas adm pode executar esta accao")
        if self._autenticador.verificar_otp(codigo):
            dado={"endereco":endereco}
            logger.debug("actualizando endereco")
            self._repo_operador.actualizar(id_alvo, dado)
            self._auditoria.auditar(
                operador_id,
                operacao="actualizar_endereço",
                detalhes=f"actualizou o endereço do operador id: {id_alvo}")                                                                                   
    def desativar_operador(self, id_alvo:int) -> None:
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
      
          operador_id= self._perfil.id
          
          #verifica se o operador é ADM
          if self._perfil.ADM:
              try:
                # desativa o operador
                self._repo_operador.deletar(id_alvo)
                
                #registra auditoria
                self._auditoria.auditar(
                    operador_id, 
                    "desativar_operador",
                    f"desativou o operador com id:{id_alvo}")
                return
              except exc.EntityNotFoundError:
                 raise
              
          raise exc.PermissionDeniedError("somente ADM pode desativar operadores") 


    def reactivar_operador(self, email,codigo):
        if not self._perfil.ADM:
            logger.warning("falha: tentativa de reactivar um operador. permissao negada." )
            raise exc.PermissionDeniedError("somente ADM pode reactivar operadores")
        logger.debug("localizando operador")
        operador=self._repo_operador.buscar_inativo(email)
        id_alvo=operador.get("id")
        campo={"ativo": True}
        logger.debug("sucesso: operador localizado")
        if self._autenticador.verificar_otp(codigo):
            logger.debug("reactivando operador")
            self._repo_operador.reactivar(id_alvo)
            logger.info("sucesso: operador id: %d reactivado", id_alvo)
    
       
    def promover_operador(self, id_alvo):
        operador_id=self._perfil.id
        logger.debug("promovendo operador id: %d", id_alvo)
        if not self._perfil.ADM:
            logger.warning("falha ao promover operador. permissao negada")
            raise exc.PermissionDeniedError("apenas adm pode promover operadores")

        campo={"ADM": True}
        self._repo_operador.actualizar(id_alvo, campo)
        self._auditoria.auditar(
                operador_id,
                operacao="promover_operador",
                detalhes=f"promoveu o operador id: {id_alvo} a ADM") 
        logger.info("operador id: %d promovido a ADM", id_alvo)          
          
          
    def rebaixar_operador(self, id_alvo):
        operador_id= self._perfil.id
        logger.debug("rebaixando operador id: %d", id_alvo)
        if not self._perfil.ADM:
            logger.warning("falha ao rebaixar operador, permissao negada.")
            raise exc.PermissionDeniedError("apenas adm pode rebaixar operadores")

        campo={"ADM": False}
        self._repo_operador.actualizar(id_alvo, campo)
        
        self._auditoria.auditar(
                operador_id,
                operacao="rebaixar_operador",
                detalhes=f"rebaixou o operador id: {id_alvo} a operador comum") 
        logger.info("operador id: %d rebaixado a operador comum", id_alvo)
    
    
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
            EntityNotFoundError: lançado pelo repositorio se nao houver operdores que correspondam ao nome.
        """
        operador_id= self._perfil.id
        dados_prontos= list() #para acumular operadores.
        
        #busca operadores
        logger.debug("buscando operadores com nome similar a %s", nome)  
        dados= self._repo_operador.buscar_nome(nome)
        
        #verifica se é ADM e define filtros
        logger.debug("definindo filtros")
        if self._perfil.ADM:
            filtro=["senha"]
            logger.debug("definido: filtro ADM")
        else:
            filtro=["identificacao", "senha", "telefone", "endereco"]
            logger.debug("definido: filtro comum ")   
        
        #filtra os dados e adiciona a dados prontos.
        for operador in dados:
            dados_prontos.append(self.filtrar_dados(operador, filtro))
            
        #registra auditoria     
        self._auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_nome",
                    detalhes=f"pesquisou pelo operador com  nome parecido a :{nome}, resultados: {len(dados_prontos)} ")
        return dados_prontos
        
        
    def pesquisar_id(self, id:int) -> dict:
        """
        Busca operador do id fornecido.
        Filtra o resultado e omite a senha .
        Faz o registro de auditoria
        
        
        Args:
            id(int): id do operador alvo.
            
        Returns:
            dict:  dicionario com os dados do operador
            
        Raises:
            EntityNotFoundError: lançado pelo repositorio se nao encontrar o operdor do id fornecido.
            PermissionDeniedError: se o quem executa nao for ADM
        """
        operador_id= self._perfil.id
        filtro=["senha"]
        
        # verifica permissao e busca operador
        if not self._perfil.ADM:
            raise exc.PermissionDeniedError("operacao restrita. busca exclusiva a ADMs.")
        logger.debug("buscando operador com  id: %d", id)  
        dados= self._repo_operador.buscar_id(id)
        
        #registra auditoria     
        self._auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_id",
                    detalhes=f"pesquisou pelo operador com id:{id}")
                    
        return self.filtrar_dados(dados, filtro)
        
    @property
    def listar_operadores(self):
        """
        busca todos os operadores e filtra os dados removendo os campos ["identificacao", "senha", "telefone", "endereco"].
        """
        filtro=["identificacao", "senha", "telefone", "endereco"]
        operadores=self._repo_operador.buscar_tudo()
        return [self.filtrar_dados(operador) for operador in operadores]
        
        
    