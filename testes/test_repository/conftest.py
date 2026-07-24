import pytest
from Projeto_xirico.infra import Conector


@pytest.fixture
def conector(tmp_path):
    #tmp=tmp_path/"teste"
    con_str=tmp_path/"teste.db"
    db=f"sqlite:///{con_str}"
    con=Conector(db)
    return con