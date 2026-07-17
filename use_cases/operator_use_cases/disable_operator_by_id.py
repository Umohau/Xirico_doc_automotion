class DisebleOperatorByID:
     def __init__(
        self,
        repo: OperatorRepository,
        auth:Autententicacao,
        notificator: NotificatorEmail,
        profile: Profile,
        audit: Auditoria
        ):
        self._repo= repo
        self._auth= auth
        self._notificator= notificator
        self._profile= profile
        self._audit= audit
        
        
    def execute(id: int, otp: str) -> int:
        if not self._profile.ADM:
            raise PermissionDeniedError("nao ADMs nao podem desativar_operadores")
        
        self._auth.verificar_otp(otp) #verifica se o codigo otp é valido
        email= self._repo.search_id(id).get('email')
        self._repo.delete(id)
        try:
            self._notificator.notify_operator(
                destino= email,
                titulo="Desativacao de conta",
                msg='sua conta de operador na xirico foi desactivada. Se nao esta a par da accao, entre em contacto com o sector administrativo pelos contactos abaixo.')
        except CredentialsError:
            pass
        except Exception as e:
            logger.warning("falha no envio de email", exc_info=True)
            
        self._audit(
            operador= self._profile.id,
            operacao= "disable operator",
            detalhes= 'desativou o operador id {id}')