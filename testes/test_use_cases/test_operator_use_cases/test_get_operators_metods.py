import pytest
from unittest.mock import PropertyMock
from Projeto_xirico.DTOs.operator_DTOs import OperatorGetByAdmResponse, OperatorGetInactiveResponse, OperatorGetResponse
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


def test_get_inactive_operator_sucess(
        get_inactive_operators,
        mock_repo,
        mock_audit
        ):
    inactives= get_inactive_operators.execute()
    mock_repo.search_inactive.assert_called_once()
    mock_audit.auditar.assert_called_once()
    assert len(inactives) == 2
    assert isinstance(inactives[1], OperatorGetInactiveResponse)



def test_get_inactive_operators_audit_failled(
        get_inactive_operators,
        mock_repo, mock_profile,
        mock_audit
        ):
    mock_audit.auditar.side_effect= FileNotFoundError
    inactives = get_inactive_operators.execute()
    mock_repo.search_inactive.assert_called()
    assert len(inactives) == 2
    assert isinstance(inactives[1],OperatorGetInactiveResponse )
    


def test_list_active_operators_ADM_profile(
        list_active_operators,
        mock_repo,
        mock_profile,
        mock_audit
        ):
    type(mock_profile).ADM= PropertyMock(return_value= True)
    result= list_active_operators.execute()
    mock_repo.search_all.assert_called_once()
    mock_audit.auditar.assert_called_once()
    assert len(result) == 2
    assert isinstance(result[0], OperatorGetByAdmResponse)
   

def test_list_active_operators_non_ADM_profile(
        list_active_operators,
        mock_repo, mock_op_dados,
        mock_profile,
        mock_audit
        ):
    type(mock_profile).ADM= PropertyMock(return_value= False)
    mock_op_dados['ADM']=False
    result= list_active_operators.execute()
    mock_repo.search_all.assert_called_once()
    mock_audit.auditar.assert_called_once()
    assert len(result) == 2
    assert isinstance(result[0], OperatorGetResponse)
    assert result[0].roll == 'operator'


def test_test_list_active_operators_audit_failled(
        list_active_operators,
        mock_repo,
        mock_profile,
        mock_audit
        ):
    type(mock_profile).ADM= PropertyMock(return_value= False)
    mock_audit.auditar.side_effect= FileNotFoundError
    result= list_active_operators.execute()
    mock_repo.search_all.assert_called_once()
    assert isinstance(result[0], OperatorGetResponse)


def test_search_by_id_sucess(
        search_by_id,
        mock_repo,
        mock_profile,
        mock_audit
        ):
    id=1
    result= search_by_id.execute(id)
    mock_repo.search_id.assert_called_with(id)
    mock_audit.auditar.assert_called_once()
    assert isinstance(result, OperatorGetByAdmResponse)


def test_search_by_name_Adm_profile(
        search_by_name,
        mock_repo,
        mock_profile,
        mock_audit):
    name='teste'
    type(mock_profile).ADM= PropertyMock(return_value= True)
    result= search_by_name.execute(name)
    mock_repo.search_name.assert_called_with(name)
    mock_audit.auditar.assert_called()
    assert isinstance(result[0], OperatorGetByAdmResponse)


def test_search_by_name_non_adm_profile(
        search_by_name,
        mock_repo,
        mock_profile,
        mock_audit,
        caplog
        ):
    name= 'teste'
    type(mock_profile).ADM= PropertyMock(return_value= False)
    result= search_by_name.execute(name)
    logs= caplog.records
    mock_repo.search_name.assert_called_with(name)
    mock_audit.auditar.assert_called()
    assert len(result)==2
    assert isinstance(result[0], OperatorGetResponse)
   
