from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Projeto_xirico.repositories.birds_repository import BirdsRepository


class SearchBirdByName:
    def __init__(self, repo: BirdsRepository):
        self._repo= repo
            
    
    
    def execute(self, nome: str) -> list[dict]:
        return self._repo.search_name(nome)


class SearchBirdById:
    def __init__(self, repo: BirdsRepository):
        self._repo= repo
            
    
    
    def execute(self, id: int) -> dict:
        return self._repo.search_id(id)
    