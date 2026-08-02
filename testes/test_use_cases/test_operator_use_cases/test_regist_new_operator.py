import pytest
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
        

@pytest.fixture
def dados():
    dados_={'nome': 'umohau', 'identificacao': '83689772925', 'telefone': '852703882', 'email': 'muhauhara3@gmail.com', 'endereco': 'moamba, matadouro',
'senha':'muhau333'}
    return RegistOperatorScheme(**dados_)

def test_regist_operator_sucess(RegistOperator, dados):
    RegistOperator.execute(dados, '000000')
    mock_profile.assert_called_once()
    