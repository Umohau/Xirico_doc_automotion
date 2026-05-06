from pathlib import Path
import os
from docxtpl import DocxTemplate
from infra import logger



class Documento:
    
    def carregar_modelo(self, caminho:str) ->DocxTemplate:
        """
        Verifica se o arquivo existe no caminho fornecido no init.
        Args:
            caminho(str): caminho do arquivo.
            
        Returns:
            DocxTemplante: uma instancia de DocxTemplante do modelo.
            
        Raises:
            FileNotFoundError: se o arquivo nao for encontrdo.
        """
       
   
        #verificando se o arquivo existe
        if not Path(caminho).exists():
            logger.error("erro ao caregar modelo.modelo nao encontrado em '%s'", caminho)
            raise FileNotFoundError(f"modelo nao encontrado em {caminho}")
            
            
        #tentando instaciar DocxTemplate  com o 
        #caminho se o aquivo existir
        try: 
            return DocxTemplate(caminho)
        except Exception as e:
            logger.error("erro inesperado ao caregar modelo em '%s' .\n erro: %s",caminho, exc_info=True)
            raise 
    
    
        
    def preencher(self,modelo: DocxTemplate, dados:dict) -> object:
        """
        Preeche os dados do docionario dados, nos templantes word no modelo.
        
        Args:
            modelo(DocxTemplate): modelo a ser preencido
            dados(dict): dicionario de dados preenchidos no formato {campo: dado}.
        
        Returns:
            DocxTemplate: um objeto de documento word preenchido
        """
        
        #preenchendo o modelo e retornando
        #o documento preenchido
        modelo.render(dados)
        return modelo
        
       
    def salvar(self, arquivo:object, caminho:str) -> bool:
        """
        Guarda o arquivo no disco.
        
        Args:
            arquivo(object): um arquivo que possa ser persistido (que possua o metodo save()).
            caminho(str): diretorio com onome do arquivo.
        Returns:
            True(bool):se o arquivo foi salvo
            
        Raises:
            OSError: se o disco estiver cheio.
            PermissionError: se nao tiver permissao.
            IOError: se nao for possivel escrever no disco.
        """
        try:
            arquivo.save(caminho)
            return True
        except PermissionError:
            logger.warning("erro de permissao ao salvar arquivo em %s", caminho)
            raise
        except OSError:
            logger.warning("erro ao salvar arquivo disco cheio")
            raise
        except IOError:
             logger.error("erro ao salvar arquivo, nao foi possiver escrever no disco: %s", caminho)
             raise
        except Exception as e:
            logger.error("ocorreu um erro inesperado ao salvar arquivo em %s", caminho , exc_info=True)
            raise
        
        
    def abrir(self, caminho: str) -> None:
        """
        Abre o arquivo no caminho fornecido.
        
        Args:
            caminho(str): caminho do arquivo a abrir.
            
        Returns:
            None
            
        Raises:
            FileNotFoundError: se o arquivo nao for encontrado
            PermissionError: se nao tiver permissao
        """
        try:
            os.startfile(caminho)
        except (FileNotFoundError, PermissionError) as e:
            logger.error("falha ao abrir arquivo em %s\nERRO: %s", caminho, e.strerror)
            raise
        

class Gerador:
    def __init__(self):
        self._documento=Documento()
        self._base=InfraGerador().base
        self._caminho_gerado=self._base/"documentos gerados"

        
    def gerar_pedido_quota(self, dados:dict) -> Path:
        nome=f"ped_quota{dados.get('data')}"
        caminho_modelo=str(self._base/modelos/"ped_quota_template.docx")
        caminho_nova_quota=self._caminho_gerado/"pedido_quota"/nome
        
        #carrega modelo
        modelo_quota= self._documento.carregar_modelo(caminho_modelo)
        
        #preenche modelo
        novo_pedido_quota= self._documento.preencher(modelo_quota, dados)
        
        #salva novo pedido de quota
        self._documento.salvar(novo_pedido_quota, str(caminho_nova_quota))
        return caminho_nova_quota    


    def gerar_recibo(self, dados: dict)->Path:
        nome=f"recibo{dados.get('data')}.docx" #nome dos recibos gerados
        caminho_modelo=self._base/modelos/"recibo_template.docx"
        caminho_novo_recibo= self._caminho_gerado/"recibos"/nome
        
        #carregando modelo
        modelo_rec=self._documento.carregar_modelo(str(caminho_modelo))
        #preenchendo modelo
        documento_gerado=self._documento.preencher(modelo_rec, dados)
        #salvando novo recibo
        self._documento.salvar(documento_gerado, str(caminho_novo_recibo))
        return caminho_novo_recibo
