from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from Projeto_xirico.exc import PermissionDeniedError, ProtectedEntityError
if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria

logger= logging.getLogger(__name__)


class DeleteOrder:
    def __init__(self, repo: OrdersRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, order_id: str) -> int:
        logger.debug('recuperando o gestor do pedido')
        order_menager= self._repo.get_order_oid(order_id).get("gestor_id")
        logger.debug('process: verificando permicao')
        if not order_menager == self._profile.id and not self._profile.ADM:
            logger.warnig('permissao negada para excluir o pedido: %s', order_id)
            raise PermissionDeniedError('nao foi possivel eliminar o pedido. permicao negada')
        logger.debug('process: deletando o pedido: %s', order_id)
        try:
            effect= self._repo.delete(order_id)
        except ProtectedEntityError:
            logger.warning('entidade protegida accao de delecao barada')
            raise
        logger.info('pedido: %s excluido com sucesso', order_id)
        logger.debug('process: auditando a accao')
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'delete_order',
            detalhes= f'eliminou o pedido id: {order_id}, gerenciado por {order_menager}'
        )
        logger.debug('sucess: processo de exclusao concluido')
        return effect
        