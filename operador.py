import exc


class Operador:
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