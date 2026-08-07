from pydantic import BaseModel, EmailStr, Field
from typing import Optional
class RegistOperatorScheme(BaseModel):
    nome: str
    identificacao: str
    telefone: str
    email: str
    endereco: str
    senha: str
    ADM: bool = False
    ativo: bool = True