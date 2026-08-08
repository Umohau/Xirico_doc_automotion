import pytest
from Projeto_xirico.use_cases.client_use_cases.recovery_client import RecoveryClient

@pytest.fixture
def recovery_client(mock_repo, mock_profile, mock_audit):
    return RecoveryClient(repo= mock_repo, profile= mock_profile, audit= mock_audit)


def test_recovery_client_sucess(recovery_client, mock_audit, mock_repo):
    email= "clientedeteste@gmail.com"
    recovery_client.execute(email)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_called()
    mock_audit.auditar.assert_called()


def test_recovery_client_audit_failled(recovery_client, mock_repo, mock_audit):
    email= "clientedeteste@gmail.com"
    mock_audit.auditar.side_effect= FileNotFoundError
    with pytest.raises(FileNotFoundError):
        recovery_client.execute(email)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_called()