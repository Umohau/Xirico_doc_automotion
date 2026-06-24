from operadoreschema import OperadorEnterSchema, OperadorResponseSchema, OperadorUpdateSchema
import exc
import logging


class OperadorCenter:
    def __init__(self, operador: Operador, perfil:Perfil, notificador:Notificacoes, autenticador: Autenticacao):
        self._operador=operador
        self._perfil=perfil
        self._notificador=notificador
        self._autenticador=autenticador


    def solicitar_otp(self, email: str) -> None:
        self._autenticador.gerar_otp()
        try:
            self._autenticador.enviar_codigo(email)
        except exc.CredentialsError:
            raise exc.InfraError("Erro na infra-estrutura. servico indisponivel contate o suporte")
        except Exception as e:
            logger.critical("erro inesperado ao solicitar Otp", exc_info=True)
            raise
        
        
    def registrar_operador(self, dados: OperadorEnterSchema, otp: str) -> int:
        try:
            id=self._operador.adicionar(dados.model_dump(), otp)
            self._notificador.notificar_operador(
                destino=dados.email,
                titulo="Bem vindo" ,
                msg="Bem vindo {dados.nome} ao programa Xirico. Agora faz parte do grupo de operadores da xirico, aceda ao seu perfil para comecar a operar.")
        except exc.PermissionDeniedError:
            self._notificador.notificar_ADM(
            titulo="Alerta de segurança", 
            msg=f"Foi registrada uma tentativa de registrar um novo operador por um perfil nao ADM,\nDetalhes da operacao:\n operador_id{self._perfil.id}\ndados:{dados}\nresultado:Permissao negada.")
            raise
        #deixa as outras excecoes subirem para  a GUI tratar
            

    def excluir_conta(self, id_alvo:int) -> None:
        email=self._operador.pesquisar_id(id).get('email')
        try:
            self._operador.desativar_operador(id_alvo)
            self._notificador.notificar_operador(
                destino=email,
                titulo="Alerta de seguranca" ,
                msg="Sua conta da Xirico foi desativada. Para mais informacoes entre em contacto com o sector Administrativo pelos contactos abaixo.")
        except PermissionDeniedError:
            self._notificador.notificar_ADM(
                titulo="Alerta de seguranca",
                msg= f"Tentativa de excluir operador, por nao operadorea\nDetalhes da operacao:\n operador_alvo:{id_alvo}\n operador id:{self._perfil.id}\n resultado: Permissao negada")
            raise


    def alterar_nome(self, nome:OperadorUpdateSchema) -> None:
        self._perfil.editar_nome(nome)
        
        
    def alterar_telefone(self, telefone:OperadorUpdateSchema, otp:str) -> None:
        self._perfil.mudar_telefone(telefone, otp)
        self._notificador.notificar_operador(
            destino=self._perfil.email,
            titulo="Alerta de seguranca",
            msg=f"Seu telefone foi alterado para {telefone}. Se nao efectuou  esta alteracao entre em contacro urgente com o sector Administrativo ou Suporte pelos contactos abaixo.")
        
    def alterar_email(self, email:str, otp:str) -> None:
        self._perfil.mudar_email(email, otp)
        self._notificador.notificar_operador(
            destino=self._perfil.email,
            titulo="Alerta de seguranca",
            msg=f"Seu email foi alterado para '{email}'. Se nao efectuou esta alteracao entre em contacro urgente com o sector Administrativo ou Suporte pelos contactos abaixo.")

                
    def alterar_identificacao(self, email:str, otp, identificacao) ->None:
        id_alvo=self._operador.pesquisar_email(email).get("id")
        try:
            self._operador.actualizar_identificacao(id_alvo, otp, identificacao)
            self._notificador.notificar_operador(
                destino=email,
                titulo="Alerta de seguranca",
                msg="Seu BI foi alterado se nao aprovou esta accao entre em contacro urgente com o sector Administrativo ou Suporte pelos contactos abaixo.")
        except exc.PermissionDeniedError:
            self._notificador.notificar_ADM(
                titulo="Alerta de seguranca",
                msg=f"Tentativa de alterar BI barrada por falta de permicao.",
                detalhes=f"Detalhes da operacao:\n operador: {self._perfil.id}\n operador alvo:{id_alvo}") 
            raise           
            
            
    def alterar_endereco(self, email:str, otp:str) -> None:
        id_alvo= self._operador.pesquisar_email(email).get("id")
        
        try:
            self._operador.actualizar_endereco(id_alvo, otp)
            self._notificador.notificar_operador(
                destino=email,
                titulo= "Alerta de seguranca",
                msg="Seu endereco foi alterado. Se nao autorizou esta accao entre em contacto urgente com o sector Administrativo ou suporte pelos contactos abaixo")
        except exc.PermissionDeniedError:
            self._notificador.notificar_ADM(
                titulo="Alerta de seguranca",
                msg=f"Tentativa de alterar Endereco barrada por falta de permicao.",
                detalhes=f"Detalhes da operacao:\n operador: {self._perfil.id}\n operador alvo:{id_alvo}") 
            raise
            
                     
    def recuperar_conta(self, email:str, otp:str) -> None:
        try:
            self._operador.reactivar_operador(email, otp)
            self._notificador.notificar_operador(
                destino=email,
                titulo="Recuperacao de conta",
                msg="Sua conta de operador na Xirico foi reactivada. Pode voltar a operador. Se nao aotorizou a reativacao contacte o sector Administrativo")
        except exc.PermissionDeniedError:
             self._notificador.notificar_ADM(
                titulo="Alerta de seguranca",
                msg=f"Tentativa de reativar operador barrada por falta de permicao.",
                detalhes=f"Detalhes da operacao:\n operador: {self._perfil.id}\n operador alvo:{email}") 
             raise
             
             
    def promover_operador(self, id_alvo) -> None:
        email= self.operador.pesquisar_id(id_alvo).get("email")
        try:
            self._operador.promover_operador(id_alvo)
            self._notificador.notificar_operador(
                destino=email,
                titulo="Promocacao ADM",
                msg="Parabens foi promovido a administrador do sistema, aceda ao programa para ver as novas funcionalidades.")
        except exc.PermissionDeniedError:
              self._notificador.notificar_ADM(
                titulo="Alerta de seguranca",
                msg=f"Tentativa de promover  operador barrada por falta de permicao.",
                detalhes=f"Detalhes da operacao:\n operador: {self._perfil.id}\n operador alvo:{id_alvo}") 
              raise
              
              
    def rebaixar_operador(self, id_alvo) -> None:
        email= self.operador.pesquisar_id(id_alvo).get("email")
        try:
            self._operador.rebaixar_operador(id_alvo)
            self._notificador.notificar_operador(
                destino=email,
                titulo="Ordem de rebaixamento",
                msg="Foi rebaixado de operador aADM a operador comum.")
        
        except exc.PermissionDeniedError:
            self._notificador.notificar_ADM(
                titulo="Alerta de seguranca",
                msg=f"Tentativa de rebaixar  operador barrada por falta de permicao.",
                detalhes=f"Detalhes da operacao:\n operador: {self._perfil.id}\n operador alvo:{id_alvo}") 
            raise
            
            
    def pesquisar_nome(self, nome:str) -> list[dict]:
        return self._operador.pesquisar_nome(nome)
        
    def pesquisar_id(self, id_alvo) -> dict:
        return self._operador.pesquisar_id(id_alvo)
        
        
    def pesquisar_email(self, email:str) -> dict:
        return self._operador.pesquisar_email(email)

  