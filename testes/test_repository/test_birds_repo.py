import pytest
from Projeto_xirico.infra import InfraData
from Projeto_xirico.repositories.birds_repository import BirdsRepository
from Projeto_xirico import exc

@pytest.fixture
def repo(conector):
    infra=InfraData(conector)
    return BirdsRepository(conector)
    
 
@pytest.fixture
def dados():
    dados={ "nome_comum": "swinswisi", 
    "especie" :"critaghra", 
    "nome_cientifico" :"Crithagra mozambica", "preco":15}
    return dados
    
def test_insert_sucess(repo, dados):
    id=repo.insert(dados)
    ave= repo.search_id(id)
    assert id==1
    assert all(item in ave.items() for item in dados.items())
    
    
def test_insert_duplicate(repo, dados):
    repo.insert(dados)
    with pytest.raises(exc.DuplicateError):
        repo.insert(dados)
        
        
def test_delete_sucess(repo, dados):
    id=repo.insert(dados)
    repo.delete(id)
    with pytest.raises(exc.EntityNotFoundError):
        repo.search_id(id)
        
       
def test_delete_entity_not_found(repo):
    with pytest.raises(exc.EntityNotFoundError):
        repo.delete(999)

        
def test_recover_sucess(repo, dados):
    id=repo.insert(dados)
    repo.delete(id)
    assert repo.recover(dados.get("nome_cientifico")) is True
    ave= repo.search_id(id)
    assert all(item in ave.items() for item in dados.items())
    
    
def test_recover_entity_not_found(repo):
    nome_cientifico="nome_cientifico"
    with pytest.raises(exc.EntityNotFoundError):
        repo.recover(nome_cientifico)    


def test_update_with_id_sucess(repo, dados):
    dado={"preco":20}
    id=repo.insert(dados)
    repo.update(dado, id)
    ave=repo.search_id(id)
    assert ave.get("preco") == dado.get('preco')
    
    
def test_update_with_name(repo, dados):
    dado={"preco":25}
    nome_cientiffico=dados.get("nome_cientifico")
    id=repo.insert(dados)
    repo.update(dados_=dado, nome_cientifico=nome_cientiffico )
    ave=repo.search_id(id)
    assert ave.get("preco") == dado.get('preco')
    
    
def test_update_entity_not_found(repo):
    dado={"preco":25}
    with pytest.raises(exc.EntityNotFoundError):
        repo.update(dado, 1)
        
        
def test_update_no_identificators(repo):
    dado={"preco":25}
    with pytest.raises(exc.IdentificatorError):
        repo.update(dado)
        
        
def test_search_name_sucess(repo, dados):
    nome="swins"
    repo.insert(dados)
    aves=repo.search_name(nome)
    assert isinstance(aves, list)       
    assert all(item in aves[0].items() for item in dados.items())
    
    
def test_search_name_entity_not_found(repo):
    nome="swins"
    with pytest.raises(exc.EntityNotFoundError):
        repo.search_name(nome)
        
            
def test_search_all_sucess(repo, dados):
    repo.insert(dados)
    aves= repo.search_all()
    assert isinstance(aves, list)
    assert len(aves)==1


def test_search_all_empty_table(repo):
    with pytest.raises(exc.EmptyTableError):
        repo.search_all()
        
        
def test_total_records(repo, dados):
    repo.insert(dados)
    assert repo.total_records == 1