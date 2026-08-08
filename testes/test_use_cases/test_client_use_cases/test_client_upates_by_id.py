import pytest
from Projeto_xirico.use_cases.client_use_cases.client_update_address_by_id import ClientUpdateAdressById
from Projeto_xirico.use_cases.client_use_cases.client_update_domain_by_id import ClientUpdateDomainById
from Projeto_xirico.use_cases.client_use_cases.client_update_email import ClientUpdateEmail
from Projeto_xirico.use_cases.client_use_cases.client_update_name_by_id import ClientUpdateNameById
from Projeto_xirico.use_cases.client_use_cases.client_update_telephone_by_id import ClientUpdateTelephoneBYId


@pytest.fixture
def client_update_address_by_id(mock_repo, mock_profile, mock_audit):
    return ClientUpdateAdressById(repo= mock_repo, audit= mock_audit, profile= mock_profile)


@pytest.fixture
def client_update_domain_by_id(mock_audit, mock_repo, mock_profile):
    return ClientUpdateDomainById(repo= mock_repo, audit= mock_audit, profile= mock_profile)


@pytest.fixture
def client_update_email(mock_repo, mock_profile, mock_audit):
    return ClientUpdateEmail(repo= mock_repo, profile= mock_profile, audit= mock_audit)


@pytest.fixture
def client_update_name_by_id(mock_audit, mock_repo, mock_profile):
    return ClientUpdateNameById(repo= mock_repo, profile= mock_profile, audit= mock_audit)


@pytest.fixture
def client_update_telephone_by_id(mock_repo, mock_audit, mock_profile):
    return ClientUpdateTelephoneBYId(repo= mock_repo, audit= mock_audit, profile= mock_profile)


def test_update_client_address_by_id_sucess(client_update_address_by_id, mock_audit, mock_repo):
    addres={'addres': 'rua do teste 123'}
    id=1
    client_update_address_by_id.execute(client_id=1, adress= addres)
    mock_repo.update.assert_called_once_with(dados=addres, id= id)
    mock_audit.auditar.assert_called()


def test_update_domain_by_id_sucess(mock_repo, mock_audit, client_update_domain_by_id):
    domain= {'domain': 'domain_test'}
    id=1
    client_update_domain_by_id.execute(client_id= id, domain= domain)
    mock_repo.update.assert_called()
    mock_audit.auditar.assert_called()


def test_update_email_sucess(mock_audit, mock_repo, client_update_email):
    email= {'email': 'teste@gmail.test'}
    id=1
    client_update_email.execute(client_id= id, email= email)
    mock_repo.update.assert_called_once_with(dados= email, id= id)
    mock_audit.auditar.assert_called()


def test_update_name_by_id_sucess(mock_repo, mock_audit, client_update_name_by_id):
    nome={'nome':'teste'}
    id=1
    client_update_name_by_id.execute(client_id= id, nome= nome)
    mock_repo.update.assert_called_once_with(id=id, dados= nome)
    mock_audit.auditar.assert_called_once()


def test_update_telephone_by_id_sucess(client_update_telephone_by_id, mock_repo, mock_audit):
    telefone= {'telefone': "844040869"}
    id=1
    client_update_telephone_by_id.execute(client_id= id, telefone= telefone)
    mock_repo.update.assert_called_once_with(dados= telefone, id= id)
    mock_audit.auditar.assert_called()