from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Usuario(BaseModel):
  id: int = Field(default=0)
  nome: Optional[str] = ""
  senha: Optional[str] = ""

class Registro(BaseModel):
  id: int
  usuario_id: int
  data_hora: datetime
  peso: int