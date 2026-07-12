import sys, os
from unittest.mock import Mock, PropertyMock
import pytest

from Projeto_xirico.exc import InvalidOtpError
from Projeto_xirico.profile import Profile

class TestPfile:
    dados={'nome': 'umohau', 'identificacao': '83689772925', 'telefone': '852703882', 'email': 'muhauhara3@gmail.com', 'endereco': 'moamba, matadouro',
'senha':'muhau333',
'ADM':False, 'ativo':True}
    
    @pytest.fixture
    def sessao(self):
         mock=Mock()         
         type(mock).id=PropertyMock(return_value=1)
         return mock
         
    @pytest.fixture
    def mock_autenticador(self):
        mock=Mock()
        mock.verificar_otp.return_value=True
        return mock
        
    @pytest.fixture
    def mock_repo_operador(self):
         dados2={'nome': 'umohau', 'identificacao': '83689772925', 'telefone': '852703882', 'email': 'muhauhara3@gmail.com', 'endereco': 'moamba, matadouro',
'senha':'muhau333',
'ADM':False, 'ativo':True}
         mock=Mock()
         mock.actualizar.return_value=1
         mock.buscar_id.return_value=dados2
         return mock
         
    @pytest.fixture
    def mock_auditoria(self):
        return Mock()
    
    
    @pytest.fixture
    def perfil(self,sessao,  mock_repo_operador, mock_autenticador, mock_auditoria):
        return Profile (sessao, mock_repo_operador, mock_autenticador, mock_auditoria)
    
    
    def test_pegar_id(self, perfil):
        assert perfil.id==1
        
        
    def test_pegar_nome(self, perfil):
        assert perfil.nome== self.dados["nome"]
        
    def test_pegar_telefone(self, perfil):
        assert perfil.telefone==self.dados["telefone"]
        
        
    def test_pegar_email(self, perfil):
        assert perfil.email==self.dados["email"]
        
        
    def test_pegar_estado(self, perfil):
        assert perfil.estado==self.dados["ativo"]
        
        
    def test_adm(self, perfil):
        assert perfil.ADM==self.dados["ADM"]
        
        
    def test_editar_nome(self, perfil, mock_auditoria, mock_repo_operador):
        """
        Given:
            um perfil.
        When:
            o metodo editar_nome é chamado com um novo nome.
        Then:
          o metodo actualizar do repositorio deve ser chamado apenas uma vez e  auditoria deve registar a acao(mock_auditoria)
          
        
         fixtures:
             perfil: objeto perfil.
             mock_auditoria:
                 para verificar o registro de log de auditoria.
             mock_repo_operador:
                 para verificar se o nome do perfil é actualizado no repositorio.
        """
        perfil.editar_nome("joao")
        mock_repo_operador.actualizar.assert_called_once()
        mock_auditoria.auditar.assert_called_once()
        assert perfil._dados_cache==None
        
    def test_mudar_email(self, perfil, sessao, mock_autenticador, mock_repo_operador,mock_auditoria):
        """
        Given:
             objeto perfil com metodo mudar_email.
        
        When:
            o metodo mudar_email é chamado com um novo email e otp válido
        
        Then:
            o metodo verificar do autenticador deve ser chamado com o otp do usuario.
            o metodo actualizar do repositorio deve ser chamado com o id da sessao, o email (em dicionario), e auditoria deve registrar  a operacao.
            
         """
        
        email="muhau@gmail.com"
        otp= "0000"
        perfil.mudar_email(email, otp)
        
        #verifica se autenticador foi chamado
       
        mock_autenticador.verificar_otp.assert_called_with(otp)

        #verifica se o metodo actualizar do 
        #repositorio foi chamado  com o id e o novo email
        mock_repo_operador.actualizar.assert_called_with(
            sessao.id,
            {"email": email})
        mock_auditoria.auditar.assert_called_once()
        assert perfil._dados_cache==None

    def test_trocar_telefone(self, perfil, mock_repo_operador, mock_autenticador, mock_auditoria):
        """
        Given:
            um objeto perfil com o metodo trocar_telefone.
            
        When:
            o metodo trocar_telefone é chamado com um novo telefone e otp válido.
            
        Then:
            o metodo verificar_otp do autenticadot deve ser chamado apenas uma vez com o otp fornecido.
            o metodo actualizar do repositorio deve ser chamado apenas uma vez, e auditoria deve registrar  a accao.
            
        Fixtures:
            perfil: objeto Perfil
            mock_repo_operador: objeto repositorio, usado para verificar se o metodo actualizar foi chamado uma vez.
            
            mock_autenticador: usado para verificar se verificar_otp  é chamado com o otp fornecido
            
            mock_aditoria: usado para verificar se a accao é registrada em log de auditoria.
                
        """
        telefone="852703382"
        codigo="1111"
        perfil.trocar_telefone( telefone, codigo)
        
        mock_autenticador.verificar_otp.assert_called_once_with(codigo)
        mock_repo_operador.actualizar.assert_called_once()
        mock_auditoria.auditar.assert_called_once()
        assert perfil._dados_cache==None
        
    
    def test_mudar_email_otp_invalido(self,perfil, mock_repo_operador, mock_autenticador):
        """
        Given: um objeto perfil com o metodo mudar_email.
        
        when:
            o metodo mudar_email é chamado com novo email e um otp inválido.
        
        Then:
            o autenticador devevlevantar a excecao InvalidOtpError.
            o metodo actualizar do repositorio nao deve ser chamado.
            
        Fixtures:
            perfil: um objeto perfil
            mock_repo_operador: para verificar se actualozar nao foi chamado
            mock_autenticdor: configurado para levantar excessao (InvalidOtpError,  simulando otp invalido)
        """
        email="muhau@gmail.com"
        otp= "0000"
        mock_autenticador.verificar_otp.side_effect= InvalidOtpError("otp inválido")
        with pytest.raises(InvalidOtpError):
            perfil.mudar_email(email, otp)
        
        mock_repo_operador.actualizar.assert_not_called()
        
    
    def test_trocar_telefone_otp_invalido(self,perfil, mock_repo_operador, mock_autenticador):
     """
     Given: um objeto perfil com o metodo trocar telefone.
     
     When:
         o metodo trocar_telefone é chamado com um novo telefone e um otp inválido.
         
     Then:
         o autenticador deve lancar a excessao InvalidOtpError e o metodo actualizar do repositorio nao deve ser chamado.
     """
     telefone="85270382"
     otp="0000"
     mock_autenticador.verificar_otp.side_effect=InvalidOtpError("otp invalido")
     
     with pytest.raises(InvalidOtpError):
         perfil.trocar_telefone(telefone, otp)
     mock_repo_operador.actualizar.assert_not_called()
            