import pytest
from unittest.mock import Mock, PropertyMock
from Projeto_xirico.infra import Conector
from Projeto_xirico.repositories.operator_repository import OperatorRepository



@pytest.fixture
def mock_repo():
    return Mock()


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
