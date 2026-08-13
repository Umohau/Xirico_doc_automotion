import dataclasses


@dataclasses.dataclass
class MessageBoxResponse:
    message_id: int
    chanel: str
    type: str
    retry_count: int
    to: str
    status: str 