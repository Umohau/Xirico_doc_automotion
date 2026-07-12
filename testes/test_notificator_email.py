import pytest
from unittest.mock import Mock
from Projeto_xirico.notifications import NotificatorEmail
from Projeto_xirico.exc import EntityNotFoundError, CredentialsError

@pytest.fixture
def mock_repo():
    emails=["adm@gmail.com", "adm2@gmail.com"]
    mock=Mock()
    mock.get_ADMs.return_value=emails
    return mock
    
@pytest.fixture
def notificator_email(mock_repo, monkeypatch, mocker):
    
    #configura variaveis de ambiente para teste
    monkeypatch.setenv("EMAIL", "teste@gmail.com")
    monkeypatch.setenv("SENHA_EMAIL", "senha_app")
    return NotificatorEmail(mock_repo)
   
    
def test_notify_operator_sucess(notificator_email, monkeypatch, mocker):
    destino="@exemplo",
    titulo="teste",
    msg="teste bem sucedido"
    yag_mock=mocker.patch("yagmail.SMTP.send") #mocka o send do yagmail
    
    #executa o metodo testado
    notificator_email.notify_operator(
        destino=destino,
        titulo=titulo,
        msg=msg)
        
    yag_mock.assert_called_once_with(to=destino, subject=titulo, contents=msg)
    
    
def test_notify_ADM(notificator_email, mocker, mock_repo):
     titulo="teste",
     msg="teste bem sucedido"
     adms=mock_repo.get_ADMs()
     
     mock_send=mocker.patch("yagmail.SMTP.send")
     notificator_email.notify_ADM(
         titulo=titulo,
         msg=msg
         )
     mock_repo.get_ADMs.assert_called()
     mock_send.assert_called_once_with(
       subject=titulo,
       contents=msg,
       bcc=adms
       )
        
def test_notify_ADM_not_found(mock_repo, notificator_email):
    titulo="teste",
    msg="teste bem sucedido"
    mock_repo.get_ADMs.return_value=list()
    with pytest.raises(EntityNotFoundError):
        notificator_email.notify_ADM(
             titulo=titulo,
             msg=msg
         )
         
         
         
def test_notificator_email_credentials(mock_repo, monkeypatch):
     monkeypatch.delenv("EMAIL", raising=False)
     with pytest.raises(CredentialsError):
         NotificatorEmail(mock_repo)