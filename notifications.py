from __future__ import annotations
import os
import logging
import yagmail
from Projeto_xirico.exc import CredentialsError

logger=logging.getLogger(__name__)


class NotificatorEmail:
    def __init__(self, repo:OperatorRepository):
        self._repo=repo
        self._conta=os.getenv("EMAIL")
        self._senha_app=os.getenv("SENHA_EMAIL")
        
        if not self._conta or not self._senha_app:
                logger.critical("falha ao obter credenciais para envio de email")
                raise CredentialsError("credenciais de email imcopletas")
        self._email=yagmail.SMTP(self._conta, self._senha_app)                
        
        
    def notify_operator(self, destino, titulo, msg ):
        self._email.send(
            to=destino, 
            subject=titulo,
            contents=msg
            )
        
                    
    def notify_ADM(self, titulo, msg):
            adms=self._repo.get_ADMs()
            self._email.send(
                subject=titulo,
                contents=msg,
                bcc=adms
                )