import pytest
from Projeto_xirico.infra import Conector, InfraData
from Projeto_xirico.repositories.messageBox_repository import messageBoxRepository
from Projeto_xirico.exc import EntityNotFoundError
                
@pytest.fixture
def conector(tmp_path):
    #tmp=tmp_path/"teste"
    con_str=tmp_path/"teste.db"
    db=f"sqlite:///{con_str}"
    con=Conector(db)
    
    return con
    
@pytest.fixture(scope= 'session')
def dados():
    dados_ = {
    "message_id": 42,
    "channel": "email",
    "type": "welcome",
    "name": "joao",
    "to": "joao.silva@empresa.com",
}
    return dados_ 
        
@pytest.fixture
def repo(conector):
    infra=InfraData(conector)
    return messageBoxRepository(conector)

        
def test_add_sucess(dados, repo):
    id= repo.add_(dados)
    message= repo.get_by_id(id)
    assert isinstance(message, dict)
    
    
def test_delete_by_status_sucess(repo, dados):
    repo.add_(dados) 
    effect= repo.delete_by_status("pending")
    assert effect==1
    with pytest.raises(EntityNotFoundError):
        message=repo.get_by_id(1)


def test_delete_by_status_not_found(repo, dados):
    repo.add_(dados) 
    effect=repo.delete_by_status('sent')
    assert effect ==0
    
    
def test_update_sucess(repo, dados):
    id=repo.add_(dados)# insere um registro no banco
    dado={'status': 'sent'}
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
    repo.add_(dados)
    channel= dados.get('channel')
    messages= repo.get_by_channel(channel)
    assert isinstance(messages, list)
    assert len(messages) == 1
    assert messages[0].get("channel")  == dados.get('channel')
    
    
def test_get_by_retrys_sucess(repo, dados):
    repo.add_(dados)
    messages= repo.get_by_retrys(limite=0)
    assert isinstance(messages, list)
    assert len(messages) == 1