import pytest
from unittest.mock import Mock, PropertyMock
from Projeto_xirico.infra import Conector
from Projeto_xirico.repositories.operator_repository import OperatorRepository

@pytest.fixture
def mock_op_dados():
    return{
        'id': 1,
        'nome': 'umohau',
        'identificacao': '83689772925',
        'telefone': '852703882',
        'email': 'muhauhara3@gmail.com',
        'endereco': 'moamba, matadouro',
        'senha':'muhau333',
        'ADM':True,
        'ativo':True}


@pytest.fixture
def mock_repo(mock_op_dados):
    repo= Mock()
    repo.search_inactive.return_value= [mock_op_dados, mock_op_dados]
    repo.search_all.return_value= [mock_op_dados, mock_op_dados]
    repo.search_id.return_value= mock_op_dados
    repo.search_name.return_value= [mock_op_dados, mock_op_dados]
    return repo


@pytest.fixture
def mock_profile():
    mock= Mock()
    type(mock).id= PropertyMock(return_value= 1)
    type(mock).ADM= PropertyMock(return_value= True)
    return mock


@pytest.fixture
def mock_message_box():
    return Mock()


@pytest.fixture
def mock_auth():
    mock= Mock()
    mock.verificar_otp.return_value= True
    return mock


@pytest.fixture
def mock_audit():
    return Mock()
