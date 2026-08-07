import pytest
from unittest.mock import PropertyMock
from Projeto_xirico.exc import PermissionDeniedError
from Projeto_xirico.use_cases.operator_use_cases.disable_operator_by_id import DisableOperatorByID

@pytest.fixture
def disable_operator_by_id(mock_repo, mock_profile, mock_audit, mock_message_box):
    return DisableOperatorByID(
        repo= mock_repo,
        message_box= mock_message_box,
        profile= mock_profile,
        audit= mock_audit
    )


def test_disable_operator_by_id_sucess(
    disable_operator_by_id,
    mock_repo,
    mock_message_box,
    mock_audit
):
    id=1
    disable_operator_by_id.execute(id)
    mock_repo.search_id.assert_called_once_with(id)
    mock_repo.delete.assert_called_once_with(id)
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()


def test_disable_operator_by_id_permission_denied(disable_operator_by_id, mock_profile, mock_repo):
    id=1
    type(mock_profile).ADM= PropertyMock(return_value=False)
    with pytest.raises(PermissionDeniedError):
        disable_operator_by_id.execute(id)
    mock_repo.search_id.assert_not_called()