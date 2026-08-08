from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository
    from Projeto_xirico.profile import Profile
    from Projeto_xirico.seguranca import Auditoria


class RecoveryBirdInCtalog:
    def __init__(self, repo: BirdsRepository, profile: Profile, audit: Auditoria):
        self._repo= repo
        self._profile= profile
        self._audit= audit


    def execute(self, id) -> int:
        effect= self._repo.recovery(id)
        self._audit.auditar(
            operador= self._profile.id,
            operacao= 'recovery_bird_in_catalog',
            detalhes= f'restaurou a ave de id {id} para o catalogo'
        )
        return effect