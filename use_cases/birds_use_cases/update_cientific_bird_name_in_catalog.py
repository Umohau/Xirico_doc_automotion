from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class UpdateBirdCientificNameInCatalog:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def excute(self, nome_cientifico: str, id:int) -> int:
        dado= {'nome_cientifico': nome_cientifico}
        anterior= self._repo.search_id(id).get('nome_cientifico')
        effect= self._repo.update(dados= dado, id= id)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'update_bird_cientific_name_in_catalog',
            detalhes= f"actualizou o nome cientifico da ave id {id} de {anterior} para {nome_cientifico}"
        )
        return effect