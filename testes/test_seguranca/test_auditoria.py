from unittest.mock import Mock
import pytest
import json
from datetime import datetime
from pathlib import Path
from Projeto_xirico.seguranca import Auditoria

@pytest.fixture(scope= "session")
def auditoria(tmp_path_factory):
    aud= Auditoria()
    aud._arquivo= tmp_path_factory.mktemp('aud')/aud._nome
    return aud


@pytest.fixture(autouse= True)
def set_dir(tmp_path, mocker):
    return Path.mkdir(tmp_path/'aud')
   

def test_auditar_sucess(auditoria, set_dir, tmp_path, mocker):
    auditoria.auditar(1,"eliminar", "eliminou2") #executa o metodo auditar
    
    #espera-se que eles estejam escritos no arquivo json
    dados_esperados={
        "operador_id":1,
        "operacao": "eliminar",
        "detalhes_operacao": "eliminou2"}

    assert auditoria._arquivo.exists()
    #lê o arquivo jsonl
    with open(auditoria._arquivo, "r") as file:
        for linha in file:
            if linha.strip():
                a=json.loads(linha)
                break

        assert dados_esperados.items() <= a.items()


def test_historico_hoje_sucess(auditoria):
    dados_esperados={
                "operador_id":1,
                "operacao": "eliminar",
                "detalhes_operacao": "eliminou2"}
            
    dados=auditoria.historico_hoje(1)
    assert dados_esperados.items() <= dados[0].items()#verifica se dados_esperados esta contido em dados.

       
def test_historico_hoje_file_op_not_found(auditoria):
    dados=auditoria.historico_hoje(2)
    assert isinstance(dados, list)
    assert len(dados)==0


def tes_historico_diario_sucess(tmp_path, auditoria, mocker):
    """
    given:
        objeto historico com metodo historico_diario.
        
    when:
        historico_diario é chamado com a data de um arquivo que existe, e um operador_id que possua regustro nesse arquivo.
        
    then:
        o retorno deve ser do tipo list contendo dicionarios.
    """
    data=datetime.now().strftime('%d_%m_%Y')
    operador_id=1
    auditoria.ficheiro= tmp_path/'aud'/f'registro_{data}.jsonl'
    #auditoria.auditar(1,"eliminar", "eliminou2") #executa o metodo auditar
    a=auditoria.historico_diario(operador_id, data)
    #arquivo=auditoria._base/"aud"/f"registro_{data}.jsonl"
    #assert arquivo.exists()
    assert isinstance(a, list)
    assert isinstance(a[0], dict)