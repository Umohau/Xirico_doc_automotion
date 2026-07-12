from __future__ import annotations
import os
import logging
import yagmail
from Projeto_xirico.exc import CredentialsError, EntityNotFoundError4d

logger=logging.getLogger(__name__)


class NotificatorEmail:
    def __init__(self, repo:OperatorRepository):
        """
       Initialize the email notification service.

        Loads email credentials from environment variables and establishes a
        connection to the SMTP server using the yagmail library.😁
        
        Args:
            repo (OperatorRepository): Operator repository used for querying
                recipient (ADMs) lists.
        
        Raises:
            CredentialsError: If the environment variables EMAIL or SENHA_EMAIL
                are not set or are empty.
            yagmail.YagConnectionError: If the connection to the SMTP server
                fails.
        
        Environment Variables:
            EMAIL (str): Email address used for sending.
            SENHA_EMAIL (str): Email password or app token.
        """
        self._repo=repo
        self._conta=os.getenv("EMAIL")
        self._senha_app=os.getenv("SENHA_EMAIL")
        
        if not self._conta or not self._senha_app:
                logger.critical("falha ao obter credenciais para envio de email")
                raise CredentialsError("credenciais de email imcopletas")
        self._email=yagmail.SMTP(self._conta, self._senha_app)                
        
        
    def notify_operator(self, destino, titulo, msg ):
        """
        Notify an operator via email.

        Args:
            destino (str): Email of the target operator.
            titulo (str): Email subject.
            msg (str): Message content.
        
        Returns:
            None
        """
        self._email.send(
            to=destino, 
            subject=titulo,
            contents=msg
            )
        
                    
    def notify_ADM(self, titulo, msg):
        """
        Notify all administrators via email.

        Retrieves the list of administrator email addresses from the repository
        and sends a message to all of them using blind carbon copy (BCC).
        
        Args:
            titulo (str): Subject of the email to be sent.
            msg (str): Message content in the email body.
        
        Returns:
            None
            
        Raises:
            EntityNotFoundError : if the system does not have ADM
        """
        adms=self._repo.get_ADMs()
        if len(adms)==0:
            raise EntityNotFoundError("nao foram encontrados ADMs no sistema")
        self._email.send(
              subject=titulo,
              contents=msg,
              bcc=adms
                )