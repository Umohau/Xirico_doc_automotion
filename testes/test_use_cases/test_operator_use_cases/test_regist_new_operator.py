import pytest
from unittest.mock import PropertyMock
from Projeto_xirico.use_cases.operator_use_cases.regist_new_operator import RegistNewOperator
from Projeto_xirico.schemes.operator_schemes import RegistOperatorScheme
from Projeto_xirico.exc import PermissionDeniedError
@pytest.fixture
def regis_new_operator(mock_repo, mock_audit, mock_auth, mock_profile, mock_message_box):
    return RegistNewOperator(
        repo= mock_repo,
        auth= mock_auth,
        message_box= mock_message_box,
        profile= mock_profile,
        audit= mock_audit
    )

@pytest.fixture
def dados():
    dados_={'nome': 'umohau', 'identificacao': '83689772925', 'telefone': '852703882', 'email': 'muhauhara3@gmail.com', 'endereco': 'moamba, matadouro',
'senha':'muhau333'}
    return RegistOperatorScheme(**dados_)


def test_regist_new_operator_sucess(
        regis_new_operator,
        mock_repo,
        mock_auth,
        mock_audit,
        mock_profile,
        mock_message_box,
        dados
):
    otp= "00000000"
    regis_new_operator.execute(dados, otp)
    mock_repo.check_unique.assert_called()
    mock_auth.verificar_otp.assert_called_with(otp)
    mock_repo.insert.assert_called_once()
    mock_audit.auditar.assert_called_once()
    mock_message_box.add_.assert_called_once()


def test_regist_new_operator_permissio_denied(
    regis_new_operator,
    mock_repo,
    mock_profile,
    mock_message_box,
    dados
):
    otp="00000000"
    type(mock_profile).ADM= PropertyMock(return_value= False)
    with pytest.raises(PermissionDeniedError):
        regis_new_operator.execute(dados, otp)
    mock_repo.check_unique.assert_not_called()
    mock_message_box.add_.assert_not_called()
