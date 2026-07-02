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
    """
    Given:
         a repository 'repo' and a data dictionary 'dados'.
    
    When:
         the repository's `insert` method is called with new data.
    
    Then:
         `insert` must return ID 1, and the return value of `search_all` must be a subset of `dados`.
    """
    id=repo.insert(dados)
    dado=repo.search_id(id)
    assert set(dados.values()) <= set(dado.values())
    assert id==1
 
       
def test_insert_duplicate(repo, dados):
    """
    given:
        a repository 'repo' and a data dictionary 'dados'.
        
    when:
        the `insert` method is called with data that was previously inserted.
        
    then:
        `insert` must raise `DuplicateError`.
    """
    repo.insert(dados)
    with pytest.raises(exc.DuplicateError):
        id2=repo.insert(dados)
        
        
def test_delete_sucess(repo, dados):
    """
    given:
        a repository 'repo' with at least one client.
    
    when:
        `delete` is called with the ID of a client that exists in the repository.
    
    then:
        the return of `delete` must be 1, and `search_id` with the same `id` must raise `EntityNotFoundError`.
    """
    id=repo.insert(dados)
    quant_del=repo.delete(id)
    with pytest.raises(exc.EntityNotFoundError):
             repo.search_id(id)             
    assert quant_del==1
    
    
def test_delete_entity_not_found(repo):
    """
    given:
        a repository 'repo'
    
    when:
        `delete` is called with the ID of a client that does not exist in the repository.
    
    then:
        `EntityNotFoundError` must be raised.
    """
    with pytest.raises(exc.EntityNotFoundError):
        repo.delete(1)  
        
        
def test_delete_inative(repo, dados):
    """
    given:
        a repository with at least one inactive client.
    
    when:
        `delete` is called with the `id` of the inactive client.
    
    then:
        `EntityNotFoundError` must be raised.
    """
    id=repo.insert(dados)
    repo.delete(id)
    with pytest.raises(exc.EntityNotFoundError):
        repo.delete(id)
       
       
def test_reactivate_sucess(repo, dados):
    """
    given:
        a repository 'repo' that contains at least one inactive client.
            
    when:
        `reactivate` is called with the `id` of the inactive client.
            
    then:
        `search_id` must return the data of the now active client.
    """
    id=repo.insert(dados)
    repo.delete(id)
    repo.reactivate(dados.get("email"))
    cliente=repo.search_id(id)
    assert all(item in cliente.items()for item in dados.items())        
 
       
def test_reactivate_not_found(repo, dados):
    """
    given:
        a repository 'repo'
            
    when:
        `reactivate` is called with the `id` of a client that is not inactive.
        
    then:
        `EntityNotFound` must be raised.
    """
    with pytest.raises(exc.EntityNotFoundError):
        repo.reactivate(dados.get('email'))
        
        
def test_update_id_sucess(repo, dados):
    """
    given:
        a repository with at least one active record.
    
    when:
        `update` is called with the `id` of an active client.
    
    then:
        `search_id` must return the data with the target field updated to the new value - in this case, the `nome` field must be changed to 'jorge'.
    """
    dado={"nome":"jorge"}
    id=repo.insert(dados)
    repo.update(dados_=dado, id=id)
    cliente=repo.search_id(id)
    assert all(item in cliente.items() for item in dado.items())


def test_update_email_sucess(repo, dados):
    """
    given:
        a repository with at least one active record.
    
    when:
        `update` is called with the `email` of an active client.
    
    then:
        `search_id` must return the data with the target field updated to the new value - in this case, the `nome` field must be changed to 'lucas'.
    """
    dado={"nome":"lucas"}
    id=repo.insert(dados)
    repo.update(dados_=dado, email=dados.get('email'))
    cliente=repo.search_id(id)
    assert cliente.get("nome")==dado.get('nome')
    
    
def test_update_entity_not_found(repo):
    """
    given:
        a repository `repo`
    
    when:
        `update` is called with the `id` of a client that does not exist or is inactive.
    
    then:
        `EntityNotFoundError` must be raised.
    """
    dado={"nome":"jorge"}
    id=999
    with pytest.raises(exc.EntityNotFoundError):
        repo.update(dado, id)


def test_update_no_identifieres(repo, dados):
    """
    given:
        a repository `repo`
    
    when:
        `update` is called without passing either the `id` or the `email` of the target client.
    
    then:
        `IdentificatorError` must be raised.
    """
    dado={"nome":"jorge"}
    id=repo.insert(dados)
    with pytest.raises(exc.IdentificatorError):
        repo.update(dados_=dado)
        
        
def test_search_all_sucess(repo, dados):
    """
    given:
        a repository `repo` with at least one client.
    
    when:
        `search_all` is called.
    
    then:
        it must return a list of dictionaries containing the client data. In this case, there is only one client in the repository, so it must return a list with 1 dictionary/client.
    """
    repo.insert(dados)
    clientes=repo.search_all()
    assert isinstance(clientes, list)
    assert len(clientes)==1
    assert all(item in clientes[0].items() for item in dados.items())
    
def test_search_all_empty_table(repo):
    """
    given:
        a repository `repo` empty, with no clients.
    
    when:
        `search_all` is called.
    
    then:
        `EmptyTableError` must be raised.
    """
   
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