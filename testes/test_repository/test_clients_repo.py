import pytest
from Projeto_xirico.repositories.cliente_repository import ClientsRepository
from Projeto_xirico.infra import InfraData
from Projeto_xirico import exc

@pytest.fixture
def repo(conector):
    con=conector
    infra=InfraData(con)
    return ClientsRepository(con )
    
@pytest.fixture
def dados():
      dados={'nome': 'umoh.au', 'dominio': 'muh0a37', 'telefone': '8827088389', 'email': 'muhauhar6a310@gmail.com', 'endereco': 'moamba, matadouro'}
      return dados  
    
def test_insert_sucess(repo, dados):
    
    id=repo.insert(dados)
    dado=repo.search_id(id)
    assert set(dados.values()) <= set(dado.values())
    assert id==1
    
def test_insert_duplicate(repo, dados):
    repo.insert(dados)
    with pytest.raises(exc.DuplicateError):
        id2=repo.insert(dados)
        
        
def test_delete_sucess(repo, dados):
    id=repo.insert(dados)
    quant_del=repo.delete(id)
    with pytest.raises(exc.EntityNotFoundError):
             repo.search_id(id)             
    assert quant_del==1
    
    
def test_delete_entity_not_found(repo):
    with pytest.raises(exc.EntityNotFoundError):
        repo.delete(1)  
        
        
def test_delete_inative(repo, dados):
    id=repo.insert(dados)
    repo.delete(id)
    with pytest.raises(exc.EntityNotFoundError):
        repo.delete(id)
        
def test_reactivate_sucess(repo, dados):
    id=repo.insert(dados)
    repo.delete(id)
    repo.reactivate(dados.get("email"))
    cliente=repo.search_id(id)
    assert cliente.get("nome")==dados.get("nome")        
 
       
def test_reactivate_not_found(repo, dados):
    with pytest.raises(exc.EntityNotFoundError):
        repo.reactivate(dados.get('email'))
        
        
def test_update_id_sucess(repo, dados):
    dado={"nome":"jorge"}
    id=repo.insert(dados)
    repo.update(dados_=dado, id=id)
    cliente=repo.search_id(id)
    assert all(item in cliente.items() for item in dado.items())


def test_update_email_sucess(repo, dados):
    dado={"nome":"lucas"}
    id=repo.insert(dados)
    repo.update(dados_=dado, email=dados.get('email'))
    cliente=repo.search_id(id)
    assert cliente.get("nome")==dado.get('nome')
    
    
def test_update_entity_not_found(repo):
    dado={"nome":"jorge"}
    id=999
    with pytest.raises(exc.EntityNotFoundError):
        repo.update(dado, id)


def test_update_no_identifieres(repo, dados):
    dado={"nome":"jorge"}
    id=repo.insert(dados)
    with pytest.raises(exc.IdentificatorError):
        repo.update(dados_=dado)
        
        
def test_search_all_sucess(repo, dados):
    repo.insert(dados)
    clientes=repo.search_all()
    assert isinstance(clientes, list)
    assert all(item in clientes[0].items() for item in dados.items())
    
def test_search_all_empty_table(repo):
   with pytest.raises(exc.EmptyTableError):
        repo.search_all()
        
        
def test_search_name(repo, dados):
    repo.insert(dados)
    clientes=repo.search_name(dados.get('nome'))
    assert isinstance(clientes, list)
    assert all(item in clientes[0].items() for item in dados.items())
    
    
def test_search_name_entity_not_found(repo):
    nome='lucas'
    with pytest.raises(exc.EntityNotFoundError):
        repo.search_name(nome)
 
               
def test_total_records(repo, dados):
    repo.insert(dados)
    assert repo.total_records==1