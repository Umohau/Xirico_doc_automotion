import dataclasses

@dataclasses.dataclass(frozen=True)
class OperatorGetResponse:
    id: int
    name: str
    roll: str
    status: str= "Activo"
    
@dataclasses.dataclass
class OperatorGetByAdmResponse:
    id: int
    name: str
    roll: str
    email: str
    telephone: str
    adress: str
    BI: str
    status: str= 'Activo'


@dataclasses.dataclass
class OperatorGetInactiveResponse:
    id: int
    nome: str
    roll: str
    email: str
    telefone: str
    adress: str
    BI: str
    status: str='Desactivado'
