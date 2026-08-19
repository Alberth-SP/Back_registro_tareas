

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class TipoBase(BaseModel):
    nombre: str
    
class Tipo(TipoBase):
    id: int
    class Config:
        orm_mode = True
        
class TareaBase(BaseModel):
    description: Optional[str] = None
    foreig_id : int
    prioridad : str

class EstadoTarea(BaseModel):
    estado: str
    
class Tarea(TareaBase, EstadoTarea):
    id: int
    is_active: bool
    fecha_creacion: datetime
    tipo : Tipo
    class Config:
        orm_mode = True