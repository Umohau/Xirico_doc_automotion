import pytest
import sqlalchemy as sa
from Projeto_xirico import exc
from Projeto_xirico.infra import InfraData
from Projeto_xirico.repositories.orders_repository import OrdersRepository

dados_cliente={'nome': 'umoh.au', 'dominio': 'muh0a37', 'telefone': '8827088389', 'email': 'muhauhar6a310@gmail.com', 'endereco': 'moamba, matadouro'}

dados_operador={'nome': 'umohau', 'identificacao': '83689772925', 'telefone': '852703882', 'email': 'muhauhara3@gmail.com', 'endereco': 'moamba, matadouro',
'senha':'muhau333',
'ADM':False, 'ativo':True}

dados_ave={ "nome_comum": "swinswisi", 
    "especie" :"critaghra", 
    "nome_cientifico" :"Crithagra mozambica", "preco":15}
        

def init_dependeces(dados, tabela, engine):
    stm=tabela.insert().values(dados)
    with engine.begin() as conexao:
        conexao.execute(stm)
    

@pytest.fixture
def repo(conector):
    infra=InfraData(conector)#cria a infraestrutura do banco
    clientes=conector.metadata.tables["clients"] #tabela de cli
    operadores=conector.metadata.tables["operators"] #tabela de operadores
    
    ave=conector.metadata.tables["birds"] #tabela de aves
    init_dependeces(dados_cliente, clientes, conector.engine) #povoamento da tabela clients 
    init_dependeces(dados_operador, operadores, conector.engine) #povoamento da tabela operators
    
    init_dependeces(dados_ave, ave, conector.engine)#povoamento da tabela birds
    return OrdersRepository(conector)


@pytest.fixture
def dados():
    dados={
        "cliente_id" :1, 
        "gestor_id":1,
        "ave_id":1,
        "quantidade":1300}  
    return dados 


def test_insert_sucess(repo, dados):
    id=repo.insert(dados)
    order=repo.get_order_oid(id)
    assert all(item in order.items() for item in dados.items())
    assert len(id) ==9
    
    
def test_delete_sucess(repo, dados):
    id=repo.insert(dados)
    repo.delete(id)
    with pytest.raises(exc.EntityNotFoundError):
        repo.get_order_oid(id)
    
    
def test_delete_protected_entity(repo, dados, conector, tmp_path):
    id=repo.insert(dados) #insere um pedido
   
    open(tmp_path/"teste.docx", "x")  #cria um docx para inserir no shipment
    with open(tmp_path/"teste.docx", "rb") as arquivo1:
        docs = arquivo1.read() #lê o arquivo criado acima e armazena em docs
       
     #dados do shipment     
    dados_ex={
    "order_id":id, #id gerado na insercao do pedido
    "processo_docs": docs}

    export=conector.metadata.tables["shipments"]# pega a tabela do metadata
    
    init_dependeces(dados_ex, export, conector.engine ) #povoa a tabela exportacoes para vincular o pedido inserido a esta exportacao.
    
    #verifica se  a excecao é lancada
    with pytest.raises(exc.ProtectedEntityError):
        repo.delete(id)
        
        
def test_delete_entity_not_found(repo):
    id="ORD897603"
    with pytest.raises(exc.EntityNotFoundError):
        repo.delete(id)
        
        
def test_update_sucess(repo, dados):
    quantidade={"quantidade":800}
    id=repo.insert(dados)
    repo.update(id, quantidade)
    quantidade_nova=repo.get_order_oid(id).get('quantidade')
    assert quantidade_nova==quantidade.get("quantidade")
            
            
def test_update_entity_not_found(repo):
    id="ORD145093"
    quantidade={"quantidade":800}
    with pytest.raises(exc.EntityNotFoundError):
        repo.update(id, quantidade)
        

def test_seach_orders_sucess(repo, dados):
    repo.insert(dados)
    pedido=repo.search_orders()
    assert isinstance(pedido, list)
    assert len(pedido)==1
    assert all(item in pedido[0].items() for item in dados.items())


def test_search_orders_empty_table(repo):
    with pytest.raises(exc.EmptyTableError):
        repo.search_orders()
        
        
def test_get_orders_cid_sucess(repo, dados):
    repo.insert(dados)
    id_cliente=dados.get("cliente_id")
    pedidos=repo.get_orders_cid(id_cliente)
    assert isinstance(pedidos, list)
    assert len(pedidos)==1
    assert all(item in pedidos[0].items() for item in dados.items())


def test_get_orders_cid_not_found(repo):
    with pytest.raises(exc.EntityNotFoundError):
        repo.get_orders_cid(1)
        
        
def test_get_orders_gid_sucess(repo, dados):
    repo.insert(dados)
    id_gestor=dados.get("gestor_id")
    pedidos=repo.get_orders_gid(id_gestor)
    assert isinstance(pedidos, list)
    assert len(pedidos)==1
    assert all(item in pedidos[0].items() for item in dados.items())
    

def test_get_orders_gid_not_found(repo):
    with pytest.raises(exc.EntityNotFoundError):
        repo.get_orders_gid(1)

              
def test_total_records(repo, dados):
    repo.insert(dados)
    repo.insert(dados)
    pedidos=repo.total_records()
    assert pedidos==2                       