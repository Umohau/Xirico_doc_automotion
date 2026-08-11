from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from Projeto_xirico.exc import PermissionDeniedError, ProtectedEntityError
if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.Profile import Profile
    from Projeto_xirico.seguranca import Auditoria


logger= logging.getLogger(__name__)


class UpdateQuantityBirdOfOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, order_id: str, new_quantity: dict):
        logger.debug('recuperando os dados do pedido')
        order= self._repo.get_order_oid(order_id) #recupera os dados do pedido
        order_menager= order.get("gestor_id") #recupera o id do gestor do pedido
        operator_id= self._profile.id #guarda o id do operador logado
        order_status= order.get('estado') #guarda o estado do pedido

        #verifica a permissao para liberar edicao do pedido
        logger.debug('process: verificando permicao')
        if not order_menager == operator_id and not self._profile.ADM:
            logger.warnig('permissao negada ao operador: %s para trocar a quantidade aves do pedido %s',operator_id, order_id)
            raise PermissionDeniedError('sem permissao para editar este pedido, somente leitura!')

        #verifica o estado do pedido para liberar a edicao
        logger.debug('process: verificando estado do pedido')
        if order_status== 'concluido': 
            logger.warnig('entidate protegida accao barada ao operador: %s pedidos concluidos nao podem ser editados id: %s',operator_id, order_id)
            raise ProtectedEntityError('pedidos concluidos nao podem ser editados, somente leitura!')
        elif order_status == 'pendente':
            logger.debug('actualizando pedido %s', order_id)
            effect= self._repo.update(order_id= order_id, novos_dados= new_quantity) #executa a actualizacao
            logger.info('quantidade de aves do pedido: %s alterada com sucesso', order_id)
        elif order_status== 'cancelado':
            logger.warning('entidade projegida accao barrada. nao é possivel editar um pedido cancelado id: %s', order_id)
            raise ProtectedEntityError('pedidos cancelados nao podem ser editados somente leitura!')

        #registra a accao em log de auditoria
        logger.debug('process: auditando a accao')
        self._audit.auditar(
            operador= operator_id,
            operacao= 'update_quantity_bird_of_order',
            detalhes= f'''alterou a quantidade de aves do pedido: {order_id}
                         de: {order.get("quantidade")}
                         para: {new_quantity.get('quantidate')}'''
        )
        logger.debug('operacao de actualizacao concluida com sucesso')
        return effect
    