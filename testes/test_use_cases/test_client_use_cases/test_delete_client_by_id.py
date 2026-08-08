import pytest
from Projeto_xirico.use_cases.client_use_cases.delete_client_by_id import DeleteClientById


@pytest.fixture
def delete_client_by_id(mock_audit, mock_repo, mock_profile):
    return DeleteClientById(
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )

id=1


def test_delete_cliente_by_id_sucess(delete_client_by_id, mock_repo, mock_audit):
    delete_client_by_id.execute(id)
    mock_repo.delete.assert_called()
    mock_audit.auditar.assert_called()


def test_delete_client_by_id_uadit_failled(delete_client_by_id, mock_repo, mock_audit):
    mock_audit.auditar.side_effect= FileNotFoundError
    with pytest.raises(FileNotFoundError):
        delete_client_by_id.execute(id)
    mock_repo.delete.assert_called_once()