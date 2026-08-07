import pytest
from unittest.mock import PropertyMock
from Projeto_xirico.use_cases.operator_use_cases.get_inactive_operators import GetInactiveOperators
from Projeto_xirico.use_cases.operator_use_cases.list_active_operators import ListActiveOperators
from Projeto_xirico.use_cases.operator_use_cases.search_by_id import SearchByID
from Projeto_xirico.use_cases.operator_use_cases.search_by_name import SearchByName


@pytest.fixture
def get_inactive_operators(
    mock_repo,
    mock_profile,
    mock_audit
):
    return GetInactiveOperators(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


@pytest.fixture
def list_active_operators(mock_repo, mock_profile, mock_audit):   
    return ListActiveOperators(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


@pytest.fixture
def search_by_id(
    mock_repo,
    mock_profile,
    mock_audit):
    return SearchByID(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


@pytest.fixture
def search_by_name(mock_repo, mock_profile, mock_audit):
    return SearchByName(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


def test_get_inactive_operator_sucess(get_inactive_operators, mock_repo, mock_audit):
    get_inactive_operators.execute()
    mock_repo.search_inactive.assert_called_once()
    mock_audit.auditar.assert_called_once()


def test_get_inactive_operators_audit_failled(get_inactive_operators, mock_repo, mock_profile, mock_audit):
    espected= {"dado": 123}
    mock_repo.search_inactive.return_value= espected
    mock_audit.auditar.side_effect= FileNotFoundError
    ret= get_inactive_operators.execute()
    mock_repo.search_inactive.assert_called()
    assert ret == espected


def test_list_active_operators_sucess(list_active_operators, mock_repo, mock_profile, mock_audit):
    list_active_operators.execute()
    mock_repo.search_all.assert_called_once()
    mock_audit.auditar.assert_called_once()


def test_test_list_active_operators_audit_failled(list_active_operators, mock_repo, mock_profile, mock_audit):
    mock_audit.auditar.side_effect= FileNotFoundError
    list_active_operators.execute()
    mock_repo.search_all.assert_called_once()


def test_search_by_id_sucess(search_by_id, mock_repo, mock_profile, mock_audit):
    id=1
    search_by_id.execute(id)
    mock_repo.search_id.assert_called_with(id)
    mock_audit.auditar.assert_called_once()


def test_search_by_name_sucess(search_by_name, mock_repo, mock_profile, mock_audit):
    name='teste'
    search_by_name.execute(name)
    mock_repo.search_name.assert_called_with(name)
    mock_audit.auditar.assert_called()