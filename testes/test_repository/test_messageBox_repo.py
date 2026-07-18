import pytest
from Projeto_xirico.infra import Conector, InfraData
from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
from Projeto_xirico.exc import EntityNotFoundError
                
@pytest.fixture(scope="session")
def conector(tmp_path_factory):
    tmp=tmp_path_factory.mktemp("teste")
    con_str=tmp/"teste.db"
    db=f"sqlite:///{con_str}"
    return Conector(db)
    
@pytest.fixture(scope= 'session')
def dados():
    dados_ = {
    'channel': 'whatsapp',
    'title': 'Código de verificação',
    'message': 'Seu código é 123456',
    'retry': 0,
        }   
    return dados_ 
        
@pytest.fixture(scope= 'session')
def repo(conector):
    infra=InfraData(conector)
    return messageBoxRepository(conector)

        
def test_add_sucess(dados, repo):
    id= repo.add_(dados)
    message= repo.get_by_id(id)
    assert isinstance(message, dict)
    
    
def test_delete_by_status_sucess(repo):
    effect= repo.delete_by_status("pending")
    assert effect==1
    with pytest.raises(EntityNotFoundError):
        message=repo.get_by_id(1)


def test_delete_by_status_not_found(repo, dados):
    repo.add_(dados)
    effect=repo.delete_by_status('sent')
    assert effect ==0
    
    
def test_update_sucess(repo):
    dado={'status': 'sent'}
    id=1
    effect= repo.update(dado, id)
    message= repo.get_by_id(id)
    assert effect==1
    assert message.get('status') == dado.get('status')
    
    
def test_update_not_found(repo):
    dado={'status': 'sent'}
    id=3
    with pytest.raises(EntityNotFoundError):
        repo.update(dado, id)
        
        
def test_get_by_status_sucess(repo, dados):
    repo.add_(dados)
    messages= repo.get_by_status("pending")
    assert isinstance(messages, list)
    assert all(item in messages[0].items() for item in dados.items())
    
    
def test_get_by_status_empty(repo):
    messages= repo.get_by_status('failed')
    assert len(messages) == 0
    
    
def test_get_by_channel_sucess(repo, dados):
    messages= repo.get_by_channel('whatsapp')
    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0].get("channel") and messages[1].get("channel") == dados.get('channel')
    
    
def test_get_by_retrys_sucess(repo):
    messages= repo.get_by_retrys(limite=0)
    assert isinstance(messages, list)
    assert len(messages) == 2