import dataclasses
from datetime import date

@dataclasses.dataclass
class DoneOrdersGetResponse:
    order_id: str
    date_of_regist: date
    sent_date: date
    manager: int
    client: int
    quantity: int
    bird: str
    status: str= 'Done'


@dataclasses.dataclass
class PendingOrdersGetResponse:
    order_id: str
    date_of_regist: date
    manager: int
    client: int
    quantity: int
    bird: str
    status: str= 'Pending'


@dataclasses.dataclass
class CanceledOrdersGetResponse:
    order_id: str
    date_of_regist: date
    manager: int
    client: int
    quantity: int
    bird: str
    status: str= 'canceled'