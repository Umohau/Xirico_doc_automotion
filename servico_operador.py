import logging
from segurança import auditoria,gestor_sessao, PermissaoMixIn
from repositorios import RepositorioOperadores #para testes locais
from infra import DuplicateError,PermissionDeniedError, EntityNotFoundError, InfraBanco, Conector

logger1= logging.getLogger(__name__)
logging.basicConfig(
   format= '%(levelname)s: %(message)s: %(asctime)s',
   datefmt= '%H:%M',
   level=logging.DEBUG) 
   
class ServicoOperador(PermissaoMixIn):
    def __init__(self, repo_operador:RepositorioOperadores):
        self._repo_operador=repo_operador
        
        
    @property
    def operador(self):
        return gestor_sessao.operador
        
    def adicionar_operador(self, dados):
        """
        Adiciona um novo operador ao repositorio e registra auditoria.Apenas ADM pode adicionar operdores.
        
        Args:
            dados(dict): dicionario de dados do novo operador.
            
        Returns:
            int: id do operador adicionado
            
        Raises:
            PermissionDeniedError: se operador que chama o metodo nao for ADM
            DuplicateError: se existir operador com os dados fornecidos.
        """
        
       
        operador_id= self.operador["id_operador"]
        
        # verifica se o operador é ADM
        if self.permissao(self.operador):
            
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
            
        
    def pesquisar_operadores(self,operador_id: int, termo: int|str=None) -> dict|list[dict]:
        """
        pesquisa por operadores no repositorio operadores e registra logs de auditoria.
        
        Args:
            operador_id(int): id do operador.
            termo(int| str| None): termo a ser pesquisado pode ser um id ou nome parcial:
                -se for "int" a pesquisa busca por id.
                -se for "str" a pesquisa busca por nome (parcial).
                -se for "None" a pesquisa busca todos os clientes.

        Returns:
            dict: se a busca for por id -retorna dicionario com os dados do operador.
            list[dict]: se a pesquisa buscar tudo,ou nome parcial - lista de dicionarios com os dados do operador.
        
        Raises:
            EntityNotFoundError: se a busca por nome ou id nao nao encontrar operadores que correspondam.
            EmptyTableError: se a busca por todos nao encontrar operadores.
            TypeError: se o tipo do termo nao for str, int ou None.
        """
        if self.permissao(self._repo_operador, operador_id, "pesquisar operadores"):
            if isinstance(termo, int):
                auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_operadores",
                    detalhes=f"pesquisou por :{termo}, em operadores.")
                logger.debug("buscando por id")     
                return self._repo_operador.buscar_id(termo)
            
            elif isinstance(termo, str):
                auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_clientes",
                    detalhes=f"pesquisou pelo operador com  nome parecido a :{termo}")
                logger.debug("buscando operadores por nome similar")    
                return self._repo_operador.buscar_nome(termo)
            elif not termo:
                auditoria.auditar(
                    operador_id,
                    operacao="pesquisar_operadores",
                    detalhes=f"pesquisou por todos os operadores")
                logger.debug("buscando todos operadoreas")
                return self._repo_operador.buscar_tudo()
                
            else:
                raise TypeError("valor do argumento 'termo' invalido")
        raise PermissionDeniedError("apenas ADM pode pesquisar operadores")
        
        
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


    

