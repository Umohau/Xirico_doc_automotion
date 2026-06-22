import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import json
import jwt
from pathlib import Path
from unittest.mock import Mock,  PropertyMock
import pytest
from datetime import datetime
import exc
from segurança import SenhaMixIn, Auditoria, OtpMixIn, Autenticacao

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
    data=datetime.today().strftime("%d_%m_%Y")
    
    
    @pytest.fixture
    def auditoria(self):
        return Auditoria()
        
        
    def test_auditar(self, tmp_path, auditoria):
        """
        given:
            objeto auditoria que possua o metodo auditar.
            
        when:
            auditar é chamado com os argumentos completos(operador, operacao, detalhes).
            
        then:
            deve criar um arquivo jsonl e escrever os dados nele de auditoria nele. os dados escritos devem conter os dados esperados(definidos abixo na implementacao).
        """
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
            
            
    def test_historico_hoje(self, auditoria):
        """
        given:
            objeto auditoria com metodo historico_hoje, um registro jsonl nomeiado com a data de hoje.
            
        when:
            historico_hoje é chamado com um id do operador alvo existente.
            
        then:
            o retorno de hustorico_hoje deve conter os dados_esperados(definidos na implementacao).
        """
        dados_esperados={
            "operador_id":1,
            "operacao": "eliminar",
            "detalhes_operacao": "eliminou2"}
        
        dados=auditoria.historico_hoje(1)
        assert dados_esperados.items() <= dados[0].items()#verifica se dados_esperados esta contido em dadod.
        
        
    def test_historico_diario(self, auditoria):
        """
        given:
            objeto historico com metodo historico_diario.
            
        when:
            historico_diario é chamado com a data de um arquivo que existe, e um operador_id que possua regustro nesse arquivo.
            
        then:
            o retorno deve ser do tipo list contendo dicionarios.
        """
        operador_id=1
        a=auditoria.historico_diario(operador_id, self.data)
        arquivo=auditoria._base/"aud"/f"registro_{self.data}.jsonl"
        assert arquivo.exists()
        assert isinstance(a, list)
        assert isinstance(a[0], dict)
        
        
    def test_historico_hoje_arquivo_nao_encontrado(self, auditoria):
        """
        given:
            objeto auditar com metodo historico_diario.
            
        when:
            hustorico_diario é chamado com a data de um arquivo que nao existe.
            
        then:
            deve ser lenvatada a excecao FileNotFoundError.
        """
        data="20_13_2026"
        operador_id=1
        with pytest.raises(FileNotFoundError):
            auditoria.historico_diario(operador_id, data)
        arquivo=auditoria._base/"aud"/f"registro_{data}.jsonl"
        assert not arquivo.exists()
        
        
    def test_historico_hoje_sem_registros(self, auditoria):
        """
        given:
            objeto auditar com o metodo historico_diario.
            
        when:
            historico_diario é chamado com a data de um arquivo que existe, mas nao contem registros das actividades do operador do id fornecido.
            
        then:
            deve ser lancada a excecao EntityNotFoundError.
        """
        operador_id=4
        with pytest.raises(exc.EntityNotFoundError):
            auditoria.historico_diario(operador_id, self.data)
        arquivo=auditoria._base/"aud"/f"registro_{self.data}.jsonl"
        assert arquivo.exists()
        
        
class TestOtpMixIn:
    @pytest.fixture
    def OtpMixIn(self):
        return OtpMixIn()
        
    def test_gerar_otp(self, OtpMixIn):
        """
        given:
            objeto OtpMjxIn com o metodo gerar_otp.
            
        where:
            gerar_otp é chamado.
            
        then:
            o o otp gerado deve conter 8 digitos, e o otp armazenado deve ser um hash do otp com pelo menos 60 bytes.
        """
        
        codigo=OtpMixIn.gerar_otp()
        otp=OtpMixIn._otp["otp"]#otp armazenado
        assert len(otp) >=60
        assert isinstance(otp, bytes)
        assert len(codigo) ==8
        
       
    def test_verificar_otp(self, OtpMixIn):
        """
        given:
            objeto OtpMixIn com metodo verificar_otp.
            
        when:
            verificar_otp é chamado com um otp valido(dentro do prazo e correto).
            
        then:
            o retorno deve ser True.
        """
        codigo=OtpMixIn.gerar_otp()
        assert  OtpMixIn.verificar_otp(codigo) is True
        
        
    def test_verificar_otp_expirado(self, OtpMixIn, mocker):
        """
        given:
            objeto OtpMixIn com metodo verificar_otp.
            
        when:
            verificar_otp é chamado com um otp expirado.
            
        then:
            espera-se a excecao ExpiredOtpError.
        """
        #configura a property status_ para simular otp expirado
        type(OtpMixIn).status_=PropertyMock(return_value="expired")   
        
        codigo=OtpMixIn.gerar_otp() 
        with pytest.raises(exc.ExpiredOtpError):
            OtpMixIn.verificar_otp(codigo)
            
    @pytest.mark.slow       
    def test_verificar_otp_invalido(self, OtpMixIn):
        #configura a property status_ para simular otp valido(pendente)
        type(OtpMixIn).status_=PropertyMock(return_value="pending")   
        OtpMixIn.gerar_otp()
        codigo="12345678"
        with pytest.raises(exc.InvalidOtpError):
            OtpMixIn.verificar_otp(codigo)
        

    @pytest.mark.slow
    def test_verificar_otp_limite_de_tentativas(self, OtpMixIn):
        """
        given:
            objeto OtpMixIn com metodo verificar_otp.
            
        when:
            verificar_otp , é chamado 3 vezes com um otp errado.
            
        then:
            deve lançar AttemptsExcedError
        """
        OtpMixIn.gerar_otp()
        codigo="12345678"
        with pytest.raises(exc.AttemptsExcedError):
            for i in range(3):
                try:
                    OtpMixIn.verificar_otp(codigo)
                except exc.InvalidOtpError:
                    continue

    def test_verificar_otp_oto_nao_gerado(self, OtpMixIn):
        """
        given:
            objeto OtpMixIn com metodo verificar_otp.
            
        when:
            verificar_otp é chamado sem ter sido gerado um otp antes.
            
        then:
            deve ser lancada a excessao AttributeError.
        """
        codigo="12345678"
        with pytest.raises(AttributeError):
            OtpMixIn.verificar_otp(codigo)
            
            
    def test_enviar_codigo_credenciais_imcompletas(self, OtpMixIn, monkeypatch):
       """
       given:
           objeto OtpMixIn com metodo enviar_codigo.
           
       when:
           enviar_codigo é chamado  mas nao encontra as credenciais (Email ou SENHA_EMAIL).
           
       then:
           deve ser levantada a excecao CredentialsError.
       """
       #simula a ausencia de Email
       monkeypatch.delenv("EMAIL", raising=False)
       monkeypatch.delenv("SENHA_EMAIL", raising=False)
       destino="exemplo@gmail.com"
       with pytest.raises(exc.CredentialsError):
            OtpMixIn.enviar_codigo(destino)


class TestAutenticacao:
    @pytest.fixture
    def autenticador(self):
        return Autenticacao()
        
        
    def test_pegar_chave_jwt_nao_encontrada(self, monkeypatch, autenticador, mocker):
        """
        given:
            objeto autenticador com metodo _pegar_chave_jwt.
            
        when:
            _pegar_chave_jwt é chamado, busca a chave  no confre do SO e nao a encontra.
            
        then:
            deve gerar uma nova chave com mais de 40 carecteres e retornar-la.
        """
        
        #modifica as credenciais da chave_jwt para testes
        monkeypatch.setenv("SERVICO", "Xirico_program_test")
        monkeypatch.setenv("KEY_JWT", "programa_xirico_test")
        
        #recupera as chaves de teste do env
        servico=os.getenv("SERVICO")
        key=os.getenv("KEY_JWT")
        
        #forca get_password de keyrings a retornar None(nao encontrou a chave)
        mock_get= mocker.patch("keyring.get_password", return_value=None)
        
        #substitue o set_password por um mock, para nao poluir o confre de chaves
        mock_set= mocker.patch("keyring.set_password")
        
        #executa o metodo buscar_chave
        chave=autenticador._pegar_chave_jwt()
        
        #checa se os mocks get e set foram chamados
        mock_get.assert_called_once_with(servico, key)
        mock_set.assert_called_once()
        
        assert len(chave) > 40 #verifica se a chave tem mais de 40 caracteres
        
        
    def test_pegar_chave_jwt_encontrada(self, autenticador, mocker, monkeypatch):
        """
        given:
            objeto autentucador com o metodo _pegar_chave_jwt.
            
        when:
            pegar_chave_jwt é chamado e encontra a chave no confre do SO.
            
        then:
            nao deve ser criada ou armazenada uma nova chave. 
        """
        #modifica as credenciais da chave_jwt para testes
        monkeypatch.setenv("SERVICO", "Xirico_program_test")
        monkeypatch.setenv("KEY_JWT", "programa_xirico_test")
        
        #recupera as chaves de teste do env
        servico=os.getenv("SERVICO")
        key=os.getenv("KEY_JWT")
        
        #substitue  set e get password de keyrings para nao poluir o confre.
        mock_get= mocker.patch("keyring.get_password", return_value=42) #forca o retorno de 42 (simula chave encontrada)
        mock_set= mocker.patch("keyring.set_password")
        
        autenticador._pegar_chave_jwt() #executa o metodo pegar_chave_jwt
        
        mock_get.assert_called_once_with(servico, key)
        mock_set.assert_not_called()


    def test_pegar_chave_jwt_CredentialsError(self,autenticador, monkeypatch):
        """
        given:
            objeto autenticador com metodo _pegar_chave_jwt.
            
        when:
            pegar_chave_jwt é chamado mas as credenciais no env estao incompletas.
            
        then:
            deve ser lancada a excecao CredentialsError.
        """
        monkeypatch.delenv("SERVICO", raising=False) #simula falta da credencial SERVICO
        
        with pytest.raises(exc.CredentialsError):
            autenticador._pegar_chave_jwt()


    def test_descodificar_token(self, autenticador, monkeypatch):
        """
        given:
            objeto autenticador  com metodo descodificar_token.
            
        when:
            o token é valido (chave correta , dentro do prazo)
            
        then:
            os dados esperados devem estar contidos no retorno
        """
        #credenciais para testes
        monkeypatch.setenv("SERVICO", "Xirico_program_test")
        monkeypatch.setenv("KEY_JWT", "programa_xirico_test")
        esperado={"id":1}
        token=autenticador.gerar_token(esperado)
        dados= autenticador.descodificar_token(token)
        assert esperado.items() <= dados.items()
        
        
    def test_descodificar_token_assinatura_invalida(self, autenticador):
        """
        given:
            objeto autenticador  com metodo descodificar_token.
            
        when:
            a assinatura do token é invalida(errada).
            
        then:
            deve ser levantada a excecao InvalidSignatureError.
        """
        
        token=autenticador.gerar_token({"id":1}) #gera o token
        
        #sobreescreve o atributo chave_jwt(torna a chave errada)
        autenticador._chave_jwt=b'$2b$12$7ZWzcnnJ.ehI.FGaOJZyT.rnkvYGosIHbggigt1DqH9k6Zi1UT9eC'
        
        with pytest.raises( jwt.exceptions.InvalidSignatureError):
            autenticador.descodificar_token(token)


    def test_descodificar_token_expirado(self, autenticador, mocker):
        """
        given:
            objeto autenticador  com metodo descodificar_token.
            
        when:
            o token descodificado já expirou.
            
        then:
            deve levantar_se a excecao ExpiredSignatureError.
        """
        token=autenticador.gerar_token({"id":1}) #gera o token
        
        #força o metodo decode do jwt a a levantar ExpiredSignatureError
        #simula otp expirado
        mocker_decode= mocker.patch("jwt.decode", side_effect= jwt.exceptions.ExpiredSignatureError)
        
        with pytest.raises(jwt.exceptions.ExpiredSignatureError):
            autenticador.descodificar_token(token)
        mocker_decode.assert_called() 
        

    def test_guardar_token(self, autenticador, mocker, monkeypatch):
        """
        given:
            objeto autenticador com metodo guardar_token.
            
        when:
            quando as credenciais e o confre SO estao disponiveis.
            
        then:
            set_password deve ser chamado uma vez , sem levatar excevoea.
        """
        mock_set=mocker.patch("keyring.set_password") #mocka o metodo set_password
        
        monkeypatch.setenv("SERVICO", "Xirico_program_test") #configura o env SERVICO para teste
        
        
        token='tyeuh uetujeh eyij' #token a armazenar
        usuario='email@teste.com'  #usuario do token
        
        autenticador.guardar_token(usuario, token)
        mock_set.assert_called_once()
        
        
    def test_guardar_token_credenciais_incompletas(self, monkeypatch, autenticador):
        """
        given:
            objeto autenticador com metodo guardar_token.
            
        when:
            quando a credencial servico nao foi encontrada ou é None no env.
            
        then:
            deve ser levantada a excecao CredentialsError.
        """
        token='tyeuh uetujeh eyij' #token a armazenar
        usuario='email@teste.com'  #usuario do token
        #remove a credencial servico para teste
        monkeypatch.delenv("SERVICO", raising=False)
        
        with pytest.raises(exc.CredentialsError):
            autenticador.guardar_token(usuario, token)
            