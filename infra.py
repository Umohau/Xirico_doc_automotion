import sqlalchemy as sa
import sys
import os
import secrets
import string
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

logger=logging.getLogger(__name__)
logging.basicConfig(
    format= "%(levelname)s: %(name)s: %(message)s: %(asctime)s",
    datefmt="%H:%M",
    level= logging.DEBUG
    )
    
   
def localizar_app():
        """
        Obtem a base ou caminho onde o programa esta rodando
        
        Returns:
            Path: o caminho absoluto onde o pregrama esta rodando em objeto Path
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).parent
        

def setup_logging():
    load_dotenv("config.env")
    log_level_str = os.getenv("LOG_LEVEL", "DEBUG")
    log_level = getattr(logging, log_level_str, logging.DEBUG)  
    
    logging.basicConfig(
        format="%(levelname)s: %(name)s: %(message)s: %(asctime)s",
        datefmt="%H:%M:%S",
        level=log_level
    )

# Chama no start do programa
setup_logging()

def gerar_ord_id():
    u="".join(secrets.choice(string.digits) for _ in range(6))
    return "ORD"+u       
    
#conector     
class  Conector:
    """
    Fábrica de engine SQLAlchemy para conexão com banco de dados.

    Esta classe cria e mantém uma instância de `Engine` a partir de uma string
    de conexão. A engine é lazy (conexão real ocorre apenas no primeiro uso).
     A cada evento de conexao com a engine ativa as ForeignKeys.
    Também fornece um objeto `MetaData` para definição/reflexão de esquemas.

    Attributes:
        engine (sa.engine.Engine): Engine SQLAlchemy configurada.
        metadata (sa.MetaData): Objeto para gerenciar metadados do banco.

    Example:
        >>> con = Conector("sqlite:///meubanco.db")
        >>> with con.engine.begin() as conn:
        ...     conn.execute(sa.text("SELECT 1"))
    """
    
    
    def __init__(self, string_de_conexao:str):
        """
        Inicializa o conector e cria a engine.

        Args:
            string_de_conexao: URL do banco no formato aceito pelo SQLAlchemy.
                Exemplos: "sqlite:///db.sqlite", "postgresql://user:pass@localhost/db".

        Raises:
            ValueError: Se a string de conexão for inválida (ArgumentError do SQLAlchemy).
        """

        
        try:
            self._engine=sa.create_engine(string_de_conexao)
            logger.info("engine criada com sucesso para '%s' ", string_de_conexao)
        except sa.exc.ArgumentError:
            logger.critical("Falha ao  criar engine com a string '%s'", string_de_conexao)
            raise ValueError(" erro ao criar engine!\n nao foi possivel conectar ao banco de dados com a string de conexao fornecida \n verifique-a e tente novamente!")

        self._metadata= sa.MetaData()
        logger.debug("objeto metadata criado com sucesso")
            
    @property
    def metadata(self):
        return self._metadata
    
    #ativa automaticamente as 
    #ForeignKeys sempre que a engine abrir uma conexao
    @sa.event.listens_for(sa.Engine, "connect")
    def ativar_FK( dbapi_connection, connection_record):
        logger.debug("ativando as FK")
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            logger.debug("sucesso: Fk ativados")
        except sa.exc.SQLAlchemyError as e:
            logger.warning("falha ao ativar FK", exc_info=True)
            raise
            
            
    @property
    def engine(self):
        return self._engine
        
#infra-estrutura do banco                  
class InfraData:
    def __init__(self, conector:Conector):
        self.conector=conector
        self.engine=self.conector.engine#atalho
        self.metadata=self.conector.metadata #atalho para o metadata
        self.criar_tabelas()
        
        
    
    def criar_tabelas(self):
        """ Cria as tabelas no banco de dados 
        """
        self.operators= sa.Table("operators", self.metadata,
            sa.Column("id", sa.Integer, primary_key= True),
            sa.Column("nome", sa.String(50), nullable=False),
            sa.Column("identificacao", sa.String(13), unique=True, nullable=False),
            sa.Column("telefone", sa.String(15), unique= True, nullable=False),
            sa.Column("email", sa.String(255), unique= True, nullable=False),
            sa.Column("endereco", sa.String(300), nullable=False),
            sa.Column("senha", sa.String(250), nullable=False),
            sa.Column("ADM", sa.Boolean, nullable= False),
            sa.Column("ativo", sa.Boolean, nullable=False)
                            )

        self.clients= sa.Table("clients", self.metadata,
            sa.Column("id", sa.Integer, primary_key= True),
            sa.Column("nome", sa.String(50), nullable= False),
            sa.Column("dominio", sa.String(255), unique=True, nullable=True),
            sa.Column("telefone", sa.String(15), unique=True, nullable= False),
            sa.Column("email", sa.String(255), unique= True, nullable= False),
            sa.Column("endereco", sa.String(300), nullable=False),
            sa.Column("ativo", sa.Boolean(), default=True)
        )
        
        self.birds=sa.Table("birds", self.metadata,
            sa.Column("id",sa.Integer ,primary_key=True),
            sa.Column("nome_comum", sa.String(50), nullable=False),
            sa.Column("especie", sa.String(25), nullable=False),
            sa.Column("nome_cientifico", sa.String(60), nullable= False, unique=True),
            sa.Column("preco", sa.Integer, nullable=False),
            sa.Column("ativo", sa.Boolean(), default=True)         
        )
        
        
        self.orders= sa.Table("orders", self.metadata,
            sa.Column("order_id", sa.String(9), primary_key=True, nullable=False, default= gerar_ord_id),
            sa.Column("cliente_id", sa.Integer, sa.ForeignKey("clients.id"), nullable=False ),
            sa.Column("gestor_id", sa.Integer, sa.ForeignKey("operators.id"), nullable=False ),
            sa.Column("ave_id", sa.Integer, sa.ForeignKey("birds.id"), nullable=False),
            sa.Column("quantidade", sa.Integer, nullable=False),
            sa.Column("registado_at", sa.Date(), nullable=False, default= datetime.today),
            sa.Column("enviado_at", sa.Date()),
            sa.Column("estado", sa.String(10), default="Pendente") 
        )  
        
        
        self.shipments= sa.Table("shipments", self.metadata,
           sa.Column("exportacao_id", sa.Integer, primary_key=True),
           sa.Column('order_id', sa.Integer, sa.ForeignKey("orders.order_id"), nullable=False, index=True),
           sa.Column("processo_docs", sa.LargeBinary())    
        )
         
        try:
            self.metadata.create_all(self.engine)
            logger.info("tabelas criadas com sucesso")
        except Exception as e:
            logger.critical("erro inesperado ao tentar criar tabelas", exc_info=True)
            raise
        


#infra-estrutura do gerador
class InfraGerador:
    def __init__(self):
        self._base= localizar_app()
        self.inicialisar_caminhos()
        
        
    @property
    def base(self):
        return self._base

    
    def inicialisar_caminhos(self):
        caminhos=[
            'recibos',
            'certificados_sanitarios_P',
            'declaracaoes_non_cites_P',
            'certificados_origem_P',
            'pedidos_licenca', 
            'pedido_quota'
              ]
        
        for caminho in caminhos:
            try:
                (self._base/'documentos gerados'/caminho).mkdir(parents=True, exist_ok=True)
            except OSError as e: 
               logger.error("erro ao inicializar caminhos. ERRO: %s", e.errno)
               raise

               
class InfraAuditoria:
    def __init__(self):
        self._base= localizar_app()  
    
    def criar_pasta(self):
        try:
                (self._base/'aud').mkdir(parents=True, exist_ok=True)
        except OSError as e: 
               logger.error("erro ao criar pasta de auditoria. ERRO: %s", e.errno)
               raise
  