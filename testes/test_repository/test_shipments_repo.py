import pytest
import sqlalchemy as sa
from datetime import datetime
from Projeto_xirico import exc
from Projeto_xirico import infra
from Projeto_xirico.infra import  Conector
from Projeto_xirico.repositories.shipment_repository import ShipmentRepository




dados_cliente={
    'nome': 'umoh.au',
    'dominio': 'muh0a37',
    'telefone': '8827088389',
    'email': 'muhauhar6a310@gmail.com',
    'endereco': 'moamba, matadouro'
    }

dados_operador={
    'nome': 'umohau',
     'identificacao': '83689772925',
     'telefone': '852703882',
     'email': 'muhauhara3@gmail.com',
     'endereco': 'moamba, matadouro',
     'senha':'muhau333',
     'ADM':False,
     'ativo':True
     }

dados_ave={
     "nome_comum": "swinswisi",
     "especie" :"critaghra", 
     "nome_cientifico" :"Crithagra mozambica",
     "preco":15
     }
   
dados_orders={
        "cliente_id" :1, 
        "gestor_id":1,
        "ave_id":1,
        "quantidade":1300
        }
        
        
def init_dependeces(dados, tabela, engine):
    stm=tabela.insert().values(dados)
    with engine.begin() as conexao:
        res=conexao.execute(stm)
        return res.inserted_primary_key

                
@pytest.fixture(scope="session")
def conector(tmp_path_factory):
    tmp=tmp_path_factory.mktemp("teste")
    con_str=tmp/"teste.db"
    db=f"sqlite:///{con_str}"
    return Conector(db)
    
                    
@pytest.fixture
def repo(conector):
    return ShipmentRepository(conector)

    
@pytest.fixture(autouse=True, scope='session')
def iniciar_banco(conector):
   #inicializa a infraestrutura do banco
    infra_=infra.InfraData(conector) 
    clientes=conector.metadata.tables["clients"] #tabela de clientes
    operadores=conector.metadata.tables["operators"] #tabela de operadores
    ave=conector.metadata.tables["birds"] #tabela de aves
    
    init_dependeces(dados_cliente, clientes, conector.engine) #povoamento da tabela clients 
    init_dependeces(dados_operador, operadores, conector.engine) #povoamento da tabela operators
    
    init_dependeces(dados_ave, ave, conector.engine)#povoamento da tabela birds
   
   
@pytest.fixture()
def order_id(conector):
    pedido=conector.metadata.tables["orders"] #tabela de pedidos
    order_id=init_dependeces(dados_orders, pedido, conector.engine)
    return order_id[0]

@pytest.fixture
def docs_process(tmp_path):
    open(tmp_path/"teste.docx", "x")
    with open(tmp_path/"teste.docx", "rb") as arquivo:
        documento= arquivo.read()
    return documento

            
@pytest.fixture
def dados(docs_process, order_id):
    dados_ex={
    "order_id":order_id,
    "processo_docs": docs_process}
    return dados_ex

def test_insert_sucess(repo, dados):
    id=repo.insert(dados)
    assert id==1
    
    
def test_update_sucess(repo, dados):
    dado=dados.copy()
    efect= repo.update(dado, 1)
    assert efect==1
    
    
def test_search_epoc_sucess(repo):
   data_inicio=datetime.now().strftime("%D/%M/%Y") #apartir do dia da execucao
   data_fim= datetime.now() #até o momento da execucao
   epoc=repo.search_epoc(data_inicio, data_fim) 
   docs=epoc[0].get("processo_docs")
   assert isinstance(epoc, list)
   assert len(epoc)==1
   assert isinstance(docs, bytes)
   
   
def test_search_epoc_entity_not_found(repo):
   data_inicio=datetime.now() #apartir do momento da execucao
   data_fim= datetime.now() #até o momento da execucao
   
   with pytest.raises(exc.EntityNotFoundError):
        repo.search_epoc(data_inicio, data_fim)
        
        
def test_get_shipmets_cl_sucess(repo, dados):
    repo.insert(dados)
    cliente_id=1
    exp=repo.get_shipments_cl(cliente_id) #executa o metodo que é testado
    assert isinstance(exp, list)
    assert len(exp)==2


def test_get_shipmets_cl_not_found(repo):
    cliente_id=999
    with pytest.raises(exc.EntityNotFoundError):
        repo.get_shipments_cl(cliente_id)
        
        
def test_get_shipments_oid_sucess(repo):
    oid=repo.get_shipments_cl(1)[0].get("order_id") #pega o id do primeiro pedido do cliente 1
    
    exp=repo.get_shipment_oid(oid) #executa o metodo testado
    assert isinstance(exp, dict) 
    
    
def test_get_shipments_oid_not_found(repo):
    oid="ORDTest980"
    with pytest.raises(exc.EntityNotFoundError):
        exp=repo.get_shipment_oid(oid) #executa o metodo testado
        
        
def test_get_shipments_gid_sucess(repo):
    gestor_id=1 
    exp=repo.get_shipments_gid(gestor_id)
    assert isinstance(exp, list)
    assert len(exp)==2
    
           
def test_get_shipments_gid_not_found(repo):
    gestor_id=999
    with pytest.raises(exc.EntityNotFoundError):
        exp=repo.get_shipments_gid(gestor_id)                         