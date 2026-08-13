import dataclasses

@dataclasses.dataclass
class BirdGetResponse:
    bird_id:int
    usual_name: str
    cientific_name: str
    especie: str
    price: int
    status: str= 'Disponivel'
