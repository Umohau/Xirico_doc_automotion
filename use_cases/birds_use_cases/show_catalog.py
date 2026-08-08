from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository


class ShowCatalog:
    def __init__(self, repo: BirdsRepository):
        self._repo= repo
        


    def execute(self) -> list[dict]:
        return self._repo.search_all()
