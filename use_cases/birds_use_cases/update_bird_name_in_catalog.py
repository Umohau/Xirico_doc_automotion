from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class UpdateBirdNameInCatalogById:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, nome: str, id:int) -> int:
        dado={'nome': nome}
        nome_anterior= self._repo.search_id(id).get('nome_comum')
        effect= self._repo.update(dados= dado, id= id)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'update_bird_name_in_catalog_by_id',
            detalhes= f'actualizou o nome da ave id {id}  de "{nome_anterior}" para "{nome}"'
        )
        return effect