import pytest
from unittest.mock import PropertyMock
from Projeto_xirico.exc import PermissionDeniedError
from Projeto_xirico.use_cases.operator_use_cases.demote_operator import DemoteOperator


@pytest.fixture
def demote_operator(mock_repo, mock_profile, mock_message_box, mock_audit):
    return DemoteOperator(
        message_box= mock_message_box,
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


def test_demote_operator_sucess(demote_operator, mock_audit, mock_repo, mock_message_box, mock_profile):
    id=1
    demote_operator.execute(id)
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()


def test_demote_operator_permission_denied(demote_operator, mock_repo, mock_profile):
    id=2
    type(mock_profile).ADM= PropertyMock(return_value= False) 
    with pytest.raises(PermissionDeniedError):
        demote_operator.execute(id)
    mock_repo.update.assert_not_called()
