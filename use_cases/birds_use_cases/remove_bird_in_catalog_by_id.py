from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class RemoveBirdsInCatalogById:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, id: int) -> int:
        nome_cientifico= self._repo.search_id(id).get('nome_cientifico')
        effect= self._repo.delete(id)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'remove_bird_in_catalog_by_id',
            detalhes= f'removeu a ave {nome_cientifico} do catalogo'
        )
        return effect
        