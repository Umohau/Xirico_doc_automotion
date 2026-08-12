import pytest
from Projeto_xirico.exc import CredentialsError
import secrets

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv('SERVICO', 'programa_teste')
    monkeypatch.setenv('KEY_JWT', 'chave_de_teste')


@pytest.fixture
def autenticacao(set_env):
    from Projeto_xirico.seguranca import Autenticacao
    return Autenticacao()


def test_pegar_chave_jwt_sucess(autenticacao, mocker):
    chave_gerada= secrets.token_bytes(32)
    mock_get= mocker.patch('keyring.get_password', return_value= chave_gerada)
    mock_set= mocker.patch('keyring.set_password', return_value= True)
    chave_retornada= autenticacao._pegar_chave_jwt()
    mock_get.assert_called_once()
    mock_set.assert_not_called()
    assert chave_gerada == chave_retornada


def test__pegar_chave_jwt_nao_encontrada(autenticacao, mocker):
    mock_get= mocker.patch('keyring.get_password', return_value= None)
    mock_set= mocker.patch('keyring.set_password')
    chave_retornada= autenticacao._pegar_chave_jwt()
    mock_get.assert_called_once()
    mock_set.assert_called_once()
    assert len(chave_retornada) >= 43


def test_pegar_chave_jwt_incomplete_credentials(autenticacao, monkeypatch, mocker):
    monkeypatch.delenv('SERVICO')
    mock_get= mocker.patch('keyring.get_password', return_value= None)
    mock_set= mocker.patch('keyring.set_password')
    with pytest.raises(CredentialsError):
        autenticacao._pegar_chave_jwt()


def test_guardar_token_credenciais_incompletas(monkeypatch, autenticacao):
    """
    given:
        objeto autenticador com metodo guardar_token.
        
    when:
        quando a credencial servico nao foi encontrada ou é None no env.
        
    then:
        deve ser levantada a excecao CredentialsError.
    """
    token='tyeuh uetujeh eyij' #token a armazenar
    usuario='email@teste.com'  #usuario do token
    #remove a credencial servico para teste
    monkeypatch.delenv("SERVICO", raising=False)
    
    with pytest.raises(CredentialsError):
        autenticacao.guardar_token(usuario, token)
