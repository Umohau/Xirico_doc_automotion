import pytest
from unittest.mock import PropertyMock
from Projeto_xirico.exc import PermissionDeniedError, EntityNotFoundError, InvalidOtpError
from Projeto_xirico.use_cases.operator_use_cases.reactivate_operator_by_email import ReactivateOperatorByEmail


@pytest.fixture
def reactivate_operator_by_email(mock_audit, mock_auth, mock_message_box,  mock_profile, mock_repo):
    return ReactivateOperatorByEmail(
        message_box= mock_message_box,
        repo= mock_repo,
        profile= mock_profile,
        audit= mock_audit,
        auth= mock_auth
    )


def test_reactivate_operator_by_email_sucess(
        reactivate_operator_by_email,
        mock_audit,
        mock_auth,
        mock_message_box,
        mock_profile,
        mock_repo
    ):
    email= "emailTeste@gmial.teste"
    otp="00000000"
    reactivate_operator_by_email.execute(email= email, otp= otp)
    mock_auth.verificar_codigo.assert_called_once_with(otp)
    mock_repo.reactivate.assert_called_once_with(email)
    mock_repo.search_email.assert_called_once_with(email)
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()


def test_reativate_operator_by_email_permission_denied(
        reactivate_operator_by_email,
        mock_auth,
        mock_profile
):
    email= "emailTeste@gmial.teste"
    otp="00000000"
    type(mock_profile).ADM= PropertyMock(return_value=False)
    with pytest.raises(PermissionDeniedError):
        reactivate_operator_by_email.execute(email= email, otp= otp)
    mock_auth.verificar_codigo.assert_not_called()


def test_reactivate_operator_by_email_auth_failed(
        reactivate_operator_by_email,
        mock_auth,
        mock_repo,
        mock_message_box
):
    email= "emailTeste@gmial.teste"
    otp="00108040"
    mock_auth.verificar_codigo.side_effect= InvalidOtpError
    with pytest.raises(InvalidOtpError):
        reactivate_operator_by_email.execute(email= email, otp= otp)
    mock_repo.reactivate.assert_not_called()
    mock_message_box.add_.assert_not_called()


def test_reactivate_operator_by_email_repo_failed(
        reactivate_operator_by_email,
        mock_auth,
        mock_repo,
        mock_message_box
):
    email= "emailTeste@gmial.not_found"
    otp="00000000"
    mock_repo.reactivate.side_effect= EntityNotFoundError
    with pytest.raises(EntityNotFoundError):
        reactivate_operator_by_email.execute(email= email, otp= otp)
    mock_auth.verificar_codigo.assert_called_once_with(otp)
    mock_message_box.add_.assert_not_called()


def test_reactivate_operator_by_email_message_box_fail(
        reactivate_operator_by_email,
        mock_auth,
        mock_repo,
        mock_message_box,
        mock_audit
) :
    email= "emailTeste@gmial.not_found"
    otp="00000000"
    mock_message_box.add_.side_effect= RuntimeError
    with pytest.raises(RuntimeError):
        reactivate_operator_by_email.execute(email= email, otp= otp)
    mock_auth.verificar_codigo.assert_called_once_with(otp)
    mock_repo.reactivate.assert_called()
    mock_repo.search_email.assert_called()
    mock_audit.auditar.assert_called()

def test_reactivate_operator_by_email_audit_failed(
        reactivate_operator_by_email,
        mock_auth,
        mock_repo,
        mock_message_box,
        mock_audit
):
    email= "emailTeste@gmial.not_found"
    otp="00000000"
    mock_audit.auditar.side_effect= FileNotFoundError
    with pytest.raises(FileNotFoundError):
        reactivate_operator_by_email.execute(email= email, otp= otp)
    mock_auth.verificar_codigo.assert_called_with(otp)
    mock_repo.reactivate.assert_called_once_with(email)
    mock_message_box.add_assert_not_called()
    