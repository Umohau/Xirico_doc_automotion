import sys, os
from unittest.mock import Mock, PropertyMock
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from operador import Operador
import exc

  
class Test_Operador:
    @pytest.fixture
    def mock_perfil(self):
        mock=Mock()
        type(mock).id=PropertyMock(return_value=1)
        type(mock).ADM=PropertyMock(return_value= True)
        
        return mock
        
    @pytest.fixture
    def mock_autenticador(self):
        mock=Mock()
        mock.verificar_otp.return_value=True
        return mock
        
    @pytest.fixture
    def  mock_auditoria(self):
        return Mock()

    @pytest.fixture
    def mock_repo_operador(self):
        mock=Mock()
        
        #dados usados como retorno dos metodos que precisam retornar dados.
        
               
        #configura o metodo de unividade para retornar True
        mock.verificar_unicidade.return_value=True
        
        #configura o metodo inserir para retornar 1 como novo id inserido
        mock.inserir.return_value=1
        
        #configura o metodo pesquisar_nome para retornr dados_brutos
        return mock
        
    @pytest.fixture
    def operador(self, mock_repo_operador, mock_autenticador, mock_auditoria, mock_perfil):
        return Operador(mock_repo_operador, mock_autenticador, mock_auditoria, mock_perfil)
        
    @pytest.mark.positive
    def test_adicionar_operador(self, operador, mock_repo_operador, mock_autenticador, mock_auditoria):
        """
        Given: um objeto operador com o metodo adicionar_operador.
        
        when:
            o metodo adicionar_operador é chamado  por um perfill ADM e com  um dicionario dados e otp validos.
            
        then:
            o metodo adicionar deve retornar 1
            o autenticador deve ser chamado uma unica vez para o otp informad
            o metodo inserir do repositorio chamado  uma vez para dados.
            auditar de auditoria deve ser chamado para registrar a acao
            
        
        fixtures:
            operdaor: objeto operdor usado para chamr o metodo adicionr_operador.
            
            mock_repo_operador:
                
                configurdo para retornar True na chamada de virificar_unicidade.
                simula o repositorio, usado para verificr se o repositerio é chamado para verificar_unicidade e persistir os dados.
            
            mock_autenticador:
                configurdo para retornar True á chamada do metodo verificar_otp.
                usado para verificar o metodo foi chamado uma vez com o otp fornercido.
           
           mock_auditoria:
               usado para verificar se auditar é chamado para registar a accao.
        """
        dados={"nome":"Umohau"}
        otp="3333"
        
        assert operador.adicionar_operador(dados, otp) ==1
        
        mock_autenticador.verificar_otp.assert_called_once_with(otp)
        
        mock_repo_operador.verificar_unicidade.assert_called()
        
        mock_repo_operador.inserir.assert_called_once_with(dados)
        mock_auditoria.auditar.assert_called_once()

      
    @pytest.mark.negative
    def test_adicionar_cliente_otp_errado(self, operador, mock_repo_operador, mock_autenticador):
        """
        given: um objeto operador com metodo adicionar_operador.
        
        when:
            o metodo adicionar operador é chamado com o otp invalido.
            
         then:
             autenticador(mock) deve lançar InvalidOtpError.
             o repositorio nao deve ser chamado nem para verificar_unicidade, sequer para inserir os dados.
        """
        #configa autenicador para levantar excessao (oto invalido)
        mock_autenticador.verificar_otp.side_effect=exc.InvalidOtpError("otp invalido")
        
        #dados simulados imcompletos
        dados={"nome":"Umohau"}
        otp="3333"
        
        with pytest.raises(exc.InvalidOtpError):
            operador.adicionar_operador(dados, otp)
            
       
        mock_repo_operador.verificar_unicidade.assert_not_called()
        mock_repo_operador.inserir.assert_not_called()
        
        
    @pytest.mark.negative
    def test_adicionar_operador_com_nao_Adm_(self, operador, mock_perfil,mock_autenticador):
        """
        given: objeto operador com metodo adicionar_operador.
        
        when:
            o metodo adicionar operador é chamado por um perfil sem permissao ADM.
            
        then:
            o metodo adicionar_operador deve levantar a excecao PermissionDeniedError
            e nao deve prosseguir para chamar autenticador.
        """
        
        #configura perfil para nao ADM(sem permissao de ADM)
        type(mock_perfil).ADM = PropertyMock(return_value=False)
        
        #dados simulados imcompletos
        dados={"nome":"Umohau"}
        otp="3333"
        
        with pytest.raises(exc.PermissionDeniedError):
            operador.adicionar_operador(dados, otp)
            
        mock_autenticador.verificar_otp.assert_not_called()
        
        
    @pytest.mark.negative
    def test_adicionar_operador_dados_existentes(self, operador, mock_repo_operador):
        """
        given: objeto operador com metodo adicionar_operador.
        
        when:
            adicionar_operador é chamado com um dicionario que contem dados duplicados.
            
        then:
            o metodo verificar_uicidade  deve levantar DuplicateError.
            o metodo inserir nao deve ser chamado.
        """
        
        #configura verificar_unicidade para levantar DuplicateError(dado nao unico)
        mock_repo_operador.verificar_unicidade.side_effect=exc.DuplicateError("existe operador com os dados fornecidos")
        
        #dados simulados imcompletos
        dados={"nome":"Umohau"}
        otp="3333"
        
        with pytest.raises(exc.DuplicateError):
            operador.adicionar_operador(dados, otp)
            
        mock_repo_operador.inserir.assert_not_called()
        
        
    @pytest.mark.positive
    def test_desativar_operador(self, operador, mock_repo_operador, mock_auditoria):
        """
        given: um objeto operador com metodo desativar_operador.
        
        when:
            o metodo desactivar operador é chamado passando um id_alvo que exuste no banco.
            
        then:
            o metodo deletar do repositorio deve ser chamado como id_alvo e retornar 1 .
            o metodo auditar deve ser chamadado para registar a accao.
        """
        id_alvo=2
        mock_repo_operador.deletar.return_value=1
        
        operador.desativar_operador(id_alvo)
        
        mock_repo_operador.deletar.assert_called_with(id_alvo)
        mock_auditoria.auditar.assert_called()
        
    
    @pytest.mark.negative
    def test_desativar_operador_alvo_nao_encontrado(self, operador, mock_repo_operador, mock_auditoria):
         
         """
         given: um objeto operador com o metodo desativar operador.
         
         when::
             o metodo desativar operador é chamado com um id que nao existe no banco ou ja se encontra inativo.
             
         then:
             o metodo deletar do repositoroio deve lançar EntityNotFound. e accao nao deve ser regustrada
         """
         mock_repo_operador.deletar.side_effect= exc.EntityNotFoundError("operador alvo nao encontrado")
         id_alvo=2
         with pytest.raises(exc.EntityNotFoundError):
            operador.desativar_operador(id_alvo)
         mock_auditoria.auditar.assert_not_called()
        
        
    @pytest.mark.negative
    def test_desativar_operador_com_perfil_nao_adm(self, operador, mock_repo_operador, mock_perfil):
        """
        given:
            um objeto operador com o metodo desativar_operador.
            
        when:
            o metodo desativar_operador  é chamado por um perfil que nao seja administrador.
            
        then:
            deve ser levantada a excessao PermissionDeniedError. e o repositorio nao deve ser chamado.
        """
        type(mock_perfil).ADM=PropertyMock(return_value=False)
        id_alvo=2
        with pytest.raises(exc.PermissionDeniedError):
            operador.desativar_operador(id_alvo)
            
        mock_repo_operador.deletar.assert_not_called()
        
        
    @pytest.mark.search
    def test_pesquisar_nome_com_perfil_ADM(self, operador, mock_repo_operador):
        """
        given:
            um objeto operador que possua o metodo pesquisar_nome.
            
        when:
            o metodo pesquisar_nome é chamado por um perfil administrador.
            
        then:
            os dados retornados devem ter a chave 'senha' removida.
        """
        dados_brutos=[{'nome': 'umohau',
               'identificacao': '83689772925',
               'telefone': '852703882',
               'email': 'muhauhara3@gmail.com',
               'endereco': 'moamba, matadouro',
               'senha':'muhau333',
               'ADM':False,
               'ativo':True}]

        dados_filtrados= {'nome': 'umohau', 'identificacao': '83689772925', 'telefone': '852703882', 'email': 'muhauhara3@gmail.com', 'endereco': 'moamba, matadouro',
'ADM':False, 'ativo':True}

        mock_repo_operador.buscar_nome.return_value= dados_brutos
        #executa a busca
        nome="umohau"
        a=operador.pesquisar_nome(nome)
        
        #verifica se o campo senha foi removido
        assert a[0]== dados_filtrados

 
    @pytest.mark.search
    def test_pesquisar_nome_com_pefil_n_ADM(self, operador, mock_repo_operador, mock_perfil):
        
        """
        given:
            um objeto operador que possua o metodo pesquisar_nome.
            
        when:
            o metodo pesquisar_nome é chamado por um perfil nao administrador.
            
        then:
            os dados retornados devem conter apenas as  chaves [nome, email, ADM, ativo]
        """
        dados_brutos=[{'nome': 'umohau',
               'identificacao': '83689772925',
               'telefone': '852703882',
               'email': 'muhauhara3@gmail.com',
               'endereco': 'moamba, matadouro',
               'senha':'muhau333',
               'ADM':False,
               'ativo':True}]

        dados_filtrados= {'nome': 'umohau', 'email': 'muhauhara3@gmail.com', 
'ADM':False, 'ativo':True}
        nome="umohau"

        mock_repo_operador.buscar_nome.return_value=dados_brutos
        type(mock_perfil).ADM=PropertyMock(return_value=False)
        
        a=operador.pesquisar_nome(nome)
        assert dados_filtrados==a[0]
        
        
    @pytest.mark.search
    def test_pesquisar_nome_nao_encontrado(self, operador, mock_repo_operador, mock_perfil):
        """
        given:
            um objeto operador com o metodo pesquisar_nome.
            
        when:
            quando o metodo pesquisar_nome é chamado, mas nao encontra correspondencia parcial ou total do nome firnecido no repositorio.
            
        then:
            o metodo deve ser lancada a excecao EntityNotFoundError.
        """
        nome="umohau"
        mock_repo_operador.buscar_nome.side_effect= exc.EntityNotFoundError("nenhuma correspondencia para: {nome}")
        
        with pytest.raises(exc.EntityNotFoundError):
            operador.pesquisar_nome(nome)

        
    @pytest.mark.search
    def test_pesquisar_id(self, operador, mock_repo_operador):
        """
        given:
            um objeto operador com o metodo pesquisar_id.
            
        when:
            o metodo pesquisar_id é chamado com um id que está no repositorio por um perfil ADM.
            
        then:
            o metodo buscar_id do repositorio deve ser chamado.
            os dados retornados devem ter o campo senha removido.
        """
        mock_repo_operador.buscar_id.return_value={"nome":"umohau", "senha":3333}
        esperado={"nome":"umohau"}
        a=operador.pesquisar_id(1)
        mock_repo_operador.buscar_id.assert_called()      
        assert a== esperado
                            
                            
    @pytest.mark.search
    def test_pesquisar_id_perfil_nao_ADM(self, operador, mock_perfil, mock_repo_operador):
        """
        given:
            um objeto operador com o metodo pesquisar_id.
            
        when:
            pesquisar_id  é chamado por um petfil nao ADM.
            
        then:
            deve lancar a excecao PermissionDeniedError e nao chamar o repositorio.
        """
        type(mock_perfil).ADM=PropertyMock(return_value=False)
        with pytest.raises(exc.PermissionDeniedError):
            operador.pesquisar_id(1)
        
        mock_repo_operador.buscar_id.assert_not_called()
                       
                                                                                   
    @pytest.mark.search
    def test_pesquisar_id_alvo_nao_encontrado(self, operador, mock_repo_operador):
        """
        given:
            um objeto operador com o metodo pesquisar_id.
            
        when:
            pesquisar_id é chamado com um id que existe no repositorio (o repositorio nao encontra o alvo).
            
        then:
            deve levantar a excecao EntityNotFoundError
        """                                      
        mock_repo_operador.buscar_id.side_effect= exc.EntityNotFoundError
        
        with pytest.raises(exc.EntityNotFoundError):
            operador.pesquisar_id(1)    
            
                                                                           
    @pytest.mark.update
    def test_actualizar_identificacao(self, operador, mock_autenticador,mock_repo_operador, mock_auditoria):
        """
        given:
            um objeto operador com o metodo actualizar_endereco.
            
        when:
            o metodo actualizar_identificacao é chamado por ADM, com um otp valido.
            
        then:
            o otp deve ser chamado com o codigo firnecido.
            o metodo actualizar do repsitorio deve ser chamado com o id e o dicionario com a identificacao, e  a operacao registrada .
        """
        ident="23557767733"
        cod="0000"
        
        #executa o  metodo
        operador.actualizar_identificacao(1, cod, ident)
        #verifica se o.otp foi verificado
        mock_autenticador.verificar_otp.assert_called_with(cod)
        #espera que o repositorio seja chamado
        mock_repo_operador.actualizar.assert_called_with(1, {"identificacao": ident})
        mock_auditoria.auditar.assert_called() #accao foi registrada
        

    @pytest.mark.update
    def test_actualizar_identificacao_otp_invalido(  self, operador, mock_autenticador, mock_repo_operador ):
        """
        given:
            objeto operador que tenha o metodo actualizar_iddntigicacao.
            
        when:
            o metodo é chamado com o otp invalido(errado).
            
        then:
            deve ser levantada a excecao InvalidOtpError e o repositorio nao deve ser chamado.
        """
        ident="23557767733"
        cod="1110"
        #configura verificar otp para lacar a excecao InvalidOtpError.
        mock_autenticador.verificar_otp.side_effect=exc.InvalidOtpError
        
        with pytest.raises(exc.InvalidOtpError):
            operador.actualizar_identificacao(1, cod, ident)
        mock_repo_operador.assert_not_called()
        
        
    @pytest.mark.update
    def test_actualizar_identificacao_perfil_n_ADM(self, operador, mock_perfil):
        """
        given:
            objeto operado com metodo actualizar.
            
        when:
            o metodo é chamado por um perfil nao administrador.
            
        then:
            devd ser levantada a excecao PermissionDeniedError.
        """
        ident="23557767733"
        cod="1110"
        #configura o atributo ADM do perfil para retornar False
        type(mock_perfil).ADM=PropertyMock(return_value=False)
        
        with pytest.raises(exc.PermissionDeniedError):
             operador.actualizar_identificacao(1, cod, ident)
             
             
    @pytest.mark.update
    def test_actualizar_endereco(self, operador, mock_autenticador, mock_repo_operador, mock_auditoria):
        """
        given:
            objeto operador com metodo actualizar_endereco.
            
        when:
            o metodo é chamado por um perfil ADM, com um id alvo existente e um otp valido.
            
        then:
            devem ser chamados: o autenticador, o repositorio. e a accao registrada em auditoria.
        """
        endereco="moamba"
        cod="0000"
        alvo=1
        
        operador.actualizar_endereco(alvo, endereco, cod)
        
        #verifica as chamadas 
        mock_autenticador.verificar_otp.assert_called_with(cod)
        mock_repo_operador.actualizar.assert_called()
        mock_auditoria.auditar.assert_called()
        
        
    @pytest.mark.update
    def test_actualizar_endereco_perfil_n_ADM(self, operador, mock_perfil, mock_repo_operador):
        """
        given:
            objeto operador com metodo actualizar_endereco.
            
        when:
            actualizar_endereco é chamado por um perfil nao ADM.
            
        then:
            deve ser lançada a excecao PermissionDeniedError e o repositorio nao chamado.
        """
        endereco="moamba"
        cod="0000"
        alvo=1
        type(mock_perfil).ADM=PropertyMock(return_value=False)
        
        with pytest.raises(exc.PermissionDeniedError):
            operador.actualizar_endereco(alvo, endereco, cod)
        mock_repo_operador.actualizar.assert_not_called()
        
        
    @pytest.mark.update
    def test_actualizar_endereco_otp_invalido(self, operador, mock_autenticador, mock_repo_operador):
         """
         given:
             objeto operador com metodo actualizar_endereco.
             
         when:
             actualizar_endereco é chamado com um otp invalido(errado).
             
         then:
             deve ser levantada a excecao InvalidOtpError e o repositorio nao chamado.
         """
         endereco="moamba"
         cod="0300"
         alvo=1
         mock_autenticador.verificar_otp.side_effect=exc.InvalidOtpError
        
         with pytest.raises(exc.InvalidOtpError):
            operador.actualizar_endereco(alvo, endereco, cod)
         mock_repo_operador.actualizar.assert_not_called()            

            
    @pytest.mark.update
    def test_actualizar_endereco_alvo_nao_encontrado(self, operador, mock_repo_operador):
        """
        given:
            objeto operador com o metodo actualizar_endereco.
            
        when:
            actualizar_endereco é chamado para um id alvo nao existente(nao encontrado).
            
        then:
            deve ser levantada a excecao EntityNotFoundError.
        """
        endereco="moamba"
        cod="0300"
        alvo=2
        mock_repo_operador.actualizar.side_effect=exc.EntityNotFoundError
        
        with pytest.raises(exc.EntityNotFoundError):
              operador.actualizar_endereco(alvo, endereco, cod)
              
              
    