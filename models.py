

from sqlalchemy import Boolean , Column, ForeignKey, Integer,String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from database import Base

class Tarea(Base):
    __tablename__ = "tarea"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    prioridad = Column(Text)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    foreig_id = Column(Integer, ForeignKey("tipo.id"))
    
    #relacion de la tabla items
    tipo = relationship("Tipo", back_populates="foreig") 
    
class Tipo(Base):
    __tablename__ = "tipo"
    id = Column(Integer, primary_key = True, index = True)
    nombre = Column(String(100), index = True)
    
    
    # Relacion con la tabla users
    foreig = relationship("Tarea", back_populates ="tipo")