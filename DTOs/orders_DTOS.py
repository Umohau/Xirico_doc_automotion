import dataclasses

@dataclasses.dataclass
class DoneOrdersGetResponse:
    order_id: str
    date_of_regist: str
    sent_date: str
    manager: int
    client: int
    quantity: int
    bird: str
    status: str= 'Concluido'


@dataclasses.dataclass
class PendingOrdersGetResponse:
    order_id: str
    data_do_entrada: str
    gestor: int
    cliente: int
    quantidate: int
    ave: str
    estado: str= 'Pendente'


@dataclasses.dataclass
class CanceledOrdersGetResponse:
    order_id: str
    data_do_entrada: str
    gestor: int
    cliente: int
    quantidate: int
    ave: str
    estado: str= 'Canceledo'