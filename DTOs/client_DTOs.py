import dataclasses

@dataclasses.dataclass
class ClientGetResponse:
    client_id: int
    name: str
    email: str
    domain: str= None
    telephone: str
    address: str
