from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class AddBirdToCatolog:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._audit= audit
        self._profile= profile


    def execute(self, dados: dict)-> int:
        id= self.repo.insert(dados)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'add_bird_to_catalog',
            detalhes= f'adicionou a ave {dados.get("nome_cientifico")} ao catalogo'
        )
        return id
        