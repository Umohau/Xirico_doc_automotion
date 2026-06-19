import sys
import os
import json
from pathlib import Path
from unittest.mock import Mock
import pytest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from segurança import SenhaMixIn, Auditoria

@pytest.mark.password
class TestSenhaMixIn:
    @pytest.mark.slow
    def test_hasehar_e_verificar_senha(self):
        """
        given:
            um objeto SenhaMixIn com os metodos hashear e verificar.
            
        when:
            hashear e verificar sao chamados com o mesmo codigo.
            
        then:
            verificar deve retornar True
            o retorno de hashear deve ter 60 ou mais caracteres.
        """
        codigo='0000'
        a=SenhaMixIn().hashear(codigo)
        assert SenhaMixIn().verificar(codigo, a) is True
        assert len(a) >=60
        
        
    @pytest.mark.slow    
    def test_verificar_senha_errada(self):
        """
        given:
            objeto SenhaMixIn com o metodo verificar.
            
        when:
            verificar é chamado com um codigo diferente do hasheado (codigo errado).
            
        then:
            verificar deve retornar False
        """
        codigo='0000'
        a=SenhaMixIn().hashear(codigo)
        assert SenhaMixIn().verificar("8888", a) is False
        
        
class TestAuditoria:
    def test_auditar(self, tmp_path):
        """
        given:
            objeto auditoria que possua o metodo auditar.
            
        when:
            auditar é chamado com os argumentos completos(operador, operacao, detalhes).
            
        then:
            deve criar um arquivo jsonl e escrever os dados nele de auditoria nele. os dados escritos devem conter os dados esperados(definidos abixo na implementacao).
        """
        auditoria=Auditoria() #instancia Auditoria
        auditoria._base=tmp_path #sob-escreve a base do arquivo para o mock nativo.
        
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
                    
            assert dados_esperados.items() <= a.items() #verifica se dados_esperados esta contido em a(dados escritos no jsonl)