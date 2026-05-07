import sqlalchemy as sa
import sys
import logging
from pathlib import Path

logger=logging.getLogger(__name__)
logging.basicConfig(
    format= "%(levelname)s: %(name)s: %(message)s: %(asctime)s",
    datefmt="%H:%M",
    level= logging.DEBUG
    )
    
    
#conector     
class  Conector:
    """
    Fábrica de engine SQLAlchemy para conexão com banco de dados.

    Esta classe cria e mantém uma instância de `Engine` a partir de uma string
    de conexão. A engine é lazy (conexão real ocorre apenas no primeiro uso).
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
    
    @property
    def engine(self):
        return self._engine
        
#infra-estrutura do banco                  
class InfraBanco:
    def __init__(self, conector:Conector):
        self.conector=conector
        self.engine=self.conector.engine#atalho
        self.metadata=self.conector.metadata #atalho para o metadata
        self.criar_tabelas()
        
        
    
    def criar_tabelas(self):
        """ Cria as tabelas no banco de dados 
        """
        self.operadores= sa.Table("operadores", self.metadata,
            sa.Column("id", sa.Integer, primary_key= True),
            sa.Column("nome", sa.String(50), nullable=False),
            sa.Column("identificacao", sa.String(13), unique=True, nullable=False),
            sa.Column("telefone", sa.String(15), unique= True, nullable=False),
            sa.Column("email", sa.String(255), unique= True, nullable=False),
            sa.Column("senha", sa.String(250), nullable=False),
            sa.Column("ADM", sa.Boolean, nullable= False),
            sa.Column("ativo", sa.Boolean, nullable=False)
                            )

        self.clientes= sa.Table("clientes", self.metadata,
            sa.Column("id", sa.Integer, primary_key= True),
            sa.Column("nome", sa.String(50), nullable= False),
            sa.Column("dominio", sa.String(255), unique=True, nullable=True),
            sa.Column("telefone", sa.String(15), unique=True, nullable= False),
            sa.Column("email", sa.String(255), unique= True, nullable= False),
            sa.Column("endereco", sa.String(300), nullable=False)
        )
        
        self.aves=sa.Table("aves", self.metadata,
            sa.Column("id",sa.Integer ,primary_key=True),
            sa.Column("nome_comum", sa.String(50), nullable=False),
            sa.Column("especie", sa.String(25), nullable=False),
            sa.Column("nome_cientifico", sa.String(60), nullable= False, unique=True)              
        )
        try:
            self.metadata.create_all(self.engine)
            logger.info("tabelas criadas com sucesso")
        except Exception as e:
            logger.critical("erro inesperado ao tentar criar tabelas", exc_info=True)
            raise
        
# Excepcoes personalizadas do programa
class EntityNotFoundError(Exception):
    pass
    
class DuplicateError(Exception):
    pass
    
class EmptyTableError(Exception):
    pass


#infra-estrutura do gerador
class InfraGerador:
    def __init__(self):
        self._base= self.localizar_app()
        
    @property
    def base(self):
        return self._base
        
    def localizar_app(self):
        """
        Obtem a base ou caminho onde o programa esta rodando
        
        Returns:
            Path: o caminho absoluto onde o pregrama esta rodando em objeto Path
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).parent
    
    
    def inicialisar_caminhos(self):
        caminhos=[
            'recibos',
            'certificados_sanitarios_P',
            'declaracaoes_non_cites_P',
            'certificados_origem_P',
            'pedidos_licenca', 'pedido_quota'
              ]
        
        for caminho in caminhos:
            try:
                (self._base/'documentos gerados'/caminho).mkdir(parents=True, exist_ok=True)
            except OSError as e: 
               logger.error("erro ao inicializar caminhos. ERRO: %s", e.errno)
               raise
i=InfraGerador()
i.inicialisar_caminhos()