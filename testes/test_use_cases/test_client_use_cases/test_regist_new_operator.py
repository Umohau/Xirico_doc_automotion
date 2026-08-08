import pytest
from Projeto_xirico.exc import DuplicateError
from Projeto_xirico.use_cases.client_use_cases.regist_new_client import RegistNEwClient



@pytest.fixture
def regist_new_client(mock_repo, mock_profile, mock_audit):
    return RegistNEwClient(
        repo= mock_repo,
        audit= mock_audit,
        profile= mock_profile
    )

dados={'dados': 'de teste do operador'}

def test_regist_new_client_sucess(regist_new_client, mock_repo, mock_audit):
    regist_new_client.execute(dados)
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_called_once_with(dados)
    mock_audit.auditar.assert_called()


def test_regist_new_client_check_unique_failled(regist_new_client, mock_repo, mock_audit):
    mock_repo.check_unique.side_effect= DuplicateError
    with pytest.raises(DuplicateError):
        regist_new_client.execute(dados)
    mock_repo.insert.assert_not_called()
    mock_audit.auditar.assert_not_called()


def test_regist_new_client_audit_failled(mock_audit, mock_repo, regist_new_client):
    mock_audit.auditar.side_effect= FileNotFoundError
    with pytest.raises(FileNotFoundError):
        regist_new_client.execute(dados)
    mock_repo.check_unique.assert_called()
    mock_repo.insert.assert_called()
