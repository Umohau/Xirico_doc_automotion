from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional


class OperadorEnterSchema(BaseModel):
    nome:str
    identificacao:str=Field(..., pattern=r'^\d{12}[A-Z]$')
    telefone: PhoneNumber
    email: EmailStr
    endereco: str=Field(min_length=6)
    senha: str=Field(min_length= 40)
   

class OperadorResponseEschema(BaseModel):
    nome:Optional[str]=None 
    identificacao:Optional[str]=Field(default=None, pattern=r'^\d{12}[A-Z]$')
    telefone: Optional[str]=None
    email:Optional[ EmailStr]=None
    endereco: Optional[str]=Field(default=None, min_length=6)
    

class OperadorUpdateSchema(BaseModel):
    nome:Optional[str]=None
    identificacao:Optional[str]=Field(default=None, pattern=r'^\d{12}[A-Z]$')
    telefone: Optional[PhoneNumber]=None
    email:Optional[ EmailStr]=None
    endereco: Optional[str]=Field(default=None, min_length=6)
    senha: Optional[str]=Field(default=None, min_length= 40)
    
    