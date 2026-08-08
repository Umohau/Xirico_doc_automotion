import pytest
from Projeto_xirico.use_cases.client_use_cases.search_client_by_name import SearchClietByName
from Projeto_xirico.use_cases.client_use_cases.search_client_by_id import SearchClientById
from Projeto_xirico.use_cases.client_use_cases.list_clients import ListClients


@pytest.fixture
def search_clients_by_name(mock_audit, mock_repo, mock_profile):
    return SearchClietByName(repo= mock_repo, audit= mock_audit, profile= mock_profile)


@pytest.fixture
def search_client_by_id(mock_audit, mock_repo, mock_profile):
    return SearchClientById(repo= mock_repo, profile= mock_profile, audit= mock_audit)

@pytest.fixture
def list_clients(mock_repo, mock_profile, mock_audit):
    return ListClients(repo= mock_repo, profile= mock_profile, audit= mock_audit)


def test_search_clients_by_name_sucess(search_clients_by_name, mock_repo, mock_audit):
    nome= 'nome de teste'
    search_clients_by_name.execute(nome)
    mock_repo.search_name.assert_called_once()
    mock_audit.auditar.assert_called_once()

def test_search_clients_by_name_audit_failled(search_clients_by_name, mock_repo, mock_audit):
    espected={'nome': 'cliente de teste'}
    nome= 'nome de teste'
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.search_name.return_value= espected
    now= search_clients_by_name.execute(nome)
    assert now== espected


def test_search_client_by_id_sucess(search_client_by_id, mock_repo, mock_audit):
    id= 1
    search_client_by_id.execute(id)
    mock_repo.search_by_id.assert_called()
    mock_audit.auditar.assert_called()


def test_sarch_by_id_audit_failled(search_client_by_id, mock_repo,  mock_audit):
    id=1
    espected={'client': 'cliente de teste'}
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.search_by_id.return_value= espected
    now= search_client_by_id.execute(id)
    assert now== espected


def test_list_clients_sucess(list_clients, mock_repo, mock_audit):
    list_clients.execute()
    mock_repo.search_all.assert_called_once()
    mock_audit.auditar.assert_called_once()


def test_list_clients_audit_failled(list_clients, mock_repo, mock_audit):
    espected={'cliente1':"teste1", 'cliente2': 'teste2'}
    mock_audit.auditar.side_effect= FileNotFoundError
    mock_repo.search_all.return_value= espected
    now= list_clients.execute()
    assert now == espected
    