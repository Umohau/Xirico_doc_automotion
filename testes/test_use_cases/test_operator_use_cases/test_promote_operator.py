import pytest
from unittest.mock import PropertyMock
from Projeto_xirico.exc import PermissionDeniedError, CredentialsError, EntityNotFoundError
from Projeto_xirico.use_cases.operator_use_cases.promote_operator import PromoteOperator

@pytest.fixture
def promote_operator(mock_message_box, mock_repo, mock_profile, mock_audit):
    return PromoteOperator(
        message_box= mock_message_box,
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit
    )


def test_promote_operator_sucess(promote_operator, mock_message_box, mock_audit, mock_profile, mock_repo):
    id=1
    promote_operator.execute(id) #executa o metodo a testar
    #verifica as chamadas aos componentes do use_case
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()


def test_promote_operator_permission_denied(promote_operator, mock_repo, mock_profile):
    id=2
    type(mock_profile).ADM= PropertyMock(return_value=False) #faz a property ADM e profile retornar False
    with pytest.raises(PermissionDeniedError):
        promote_operator.execute(id) #excute o metodo

    mock_repo.update.assert_not_called()


def test_promote_operator_message_box_fail(promote_operator, mock_audit, mock_message_box ,mock_repo):
    id= 1
    mock_message_box.add_.side_effect= CredentialsError
    with pytest.raises(CredentialsError):
        promote_operator.execute(id)
    #verifica se mesmo apos o erro de registro da mensagem a promocao nao e afectada
    mock_repo.update.assert_called_once()
    mock_audit.auditar.assert_called_once()


def test_promote_operator_auditar_failed(promote_operator, mock_audit, mock_repo, mock_message_box):
    id=1
    mock_audit.auditar.side_effect= FileNotFoundError
    with pytest.raises(FileNotFoundError):
        promote_operator.execute(id)
    mock_repo.update.assert_called_once()
    mock_message_box.add_.assert_not_called()


def test_promote_operator_repo_failed(promote_operator, mock_audit, mock_message_box, mock_repo):
    id=900
    mock_repo.update.side_effect= EntityNotFoundError
    with pytest.raises(EntityNotFoundError):
        promote_operator.execute(id)
    mock_audit.auditar.assert_not_called()
    mock_message_box.add_.assert_not_called()