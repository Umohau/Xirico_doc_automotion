from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from datetime import datetime
from Projeto_xirico.exc import PermissionDeniedError, ProtectedEntityError
if TYPE_CHECKING:
    from Projeto_xirico.repositories.orders_repository import OrdersRepository
    from Projeto_xirico.repositories.shipment_repository import ShipmentRepository
    from Projeto_xirico.Profile import Profile
    from Projeto_xirico.seguranca import Auditoria, Autenticacao


logger= logging.getLogger(__name__)


class DoneOrder:
    def __init__(self,
        repo: OrdersRepository,
        profile: Profile,
        audit: Auditoria,
        shipment: ShipmentRepository
    ):
        self._repo= repo
        self._profile= profile
        self._audit= audit
        self._shipment= shipment


    def execute(self, data_de_envio: datetime, shipment_process: dict):
        done= {'enviado_at': data_de_envio, 'estado': 'concluido'}
        order_id= shipment_process.get('order_id')
        logger.debug('process: registrando o processo da exportacao do pedido %s', order_id)
        id= self._shipment.insert(shipment_process)
        logger.info('shipment do pedido: %s foi registrado com id: %s', id)
        logger.debug('process: actualizando o estado do pedido %s', order_id)
        self._repo.update(order_id= order_id, novos_dados= done)
        logger.info('pedido: %s actualizado com sucesso', order_id)

        #registra log de auditoria
        logger.debug('process: auditando a accao')
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'done_order',
            detalhes= f'concluiu o pedido: {order_id}'
        )
        logger.debug('pedido concluido com sucesso')
