from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional


class SchemaOperador(BaseModel):
    nome:str
    identificacao:str=Field(..., pattern=r'^\d{12}[A-Z]$')
    telefone: PhoneNumber
    email: EmailStr
    endereco: str=Field(min_length=6)
    senha: str=Field(min_length= 40)
    ADM: bool=False
    ativo: bool=True
    
    # nao é possivel adicionar operadores como adms
    @field_validator("ADM", mode='before')
    @classmethod
    def setar_adm(cls, valor):
        return False

    #garante que nao sejam adicionados operadorea inativos
    @field_validator("ativo", mode= 'before')
    @classmethod
    def set_ativo(cls, valor):
        return True


class SchemaCliente(BaseModel):
    nome: str=Field(min_length=3)
    dominio: Optional[str]=Field(min_length=8)
    telefone: PhoneNumber
    email: EmailStr
    endereco: str=Field(min_length=25)
