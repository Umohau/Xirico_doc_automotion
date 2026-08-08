import pytest
<<<<<<< HEAD
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
=======
from unittest.mock import Mock, PropertyMock
from Projeto_xirico.use_cases.operator_use_cases.regist_new_operator import RegistNewOperator
from Projeto_xirico.schemes.operator_schemes import RegistOperatorScheme

mock_repo=Mock()
mock_auditoria= Mock()
mock_autenticacao=Mock()
mock_message_Box=Mock()

@pytest.fixture
def mock_profile():
    mock=Mock()
    type(mock).ADM= PropertyMock(return_value= True)
    return mock

@pytest.fixture
def mock_autenticacao():
    mock=Mock()
    mock.verificar_otp.return_value=True
    return mock        
    
@pytest.fixture
def RegistOperator(mock_profile, mock_autenticacao):
    return RegistNewOperator(
        repo= mock_repo,
        auth= mock_autenticacao,
        message_box= mock_message_Box,
        profile=mock_profile,
        audit= mock_auditoria)
        
>>>>>>> 76dbedb9878217a0782217c1c93f8da950a9b9d9

@pytest.fixture
def dados():
    dados_={'nome': 'umohau', 'identificacao': '83689772925', 'telefone': '852703882', 'email': 'muhauhara3@gmail.com', 'endereco': 'moamba, matadouro',
'senha':'muhau333'}
    return RegistOperatorScheme(**dados_)

<<<<<<< HEAD

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


=======
def test_regist_operator_sucess(RegistOperator, dados):
    RegistOperator.execute(dados, '000000')
    mock_profile.assert_called_once()
    
>>>>>>> 76dbedb9878217a0782217c1c93f8da950a9b9d9
