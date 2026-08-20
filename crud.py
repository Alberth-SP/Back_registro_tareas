
from sqlalchemy.orm import Session
import models, schemas
from fastapi import HTTPException
from sqlalchemy.orm import joinedload


# Tipo

def get_tipo(db: Session, skip: int=0, limit: int=100):
    return db.query(models.Tipo).offset(skip).limit(limit).all()

def create_tipo(db: Session, tipo: schemas.TipoBase):
    db_tipo = models.Tipo(**tipo.dict())
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

def delete_tipo(db: Session, tipo_id: int):
    db_tipo = db.query(models.Tipo).filter(models.Tipo.id == tipo_id).first()
    if db_tipo is None:
        return None
    db.delete(db_tipo)
    db.commit()
    return True

def update_tipo(db: Session, tipo_id: int, tipo: schemas.TipoBase):
    db_tipo = db.query(models.Tipo).filter(models.Tipo.id == tipo_id).first()
    if db_tipo is None:
        return None
    
    for key, value in tipo.dict().items():
        setattr(db_tipo, key, value)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo
    
# Tarea

def create_tarea(db: Session, tarea: schemas.TareaBase):
    tipo = db.query(models.Tipo).filter(models.Tipo.id == tarea.foreig_id).first()
    
    if not tipo:
        raise HTTPException(status_code=404, detail="El tipo no existe")

    db_tarea = models.Tarea(**tarea.model_dump())
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

def get_tareas(db: Session, skip: int=0, limit: int | None = None):
    tipo_tem = db.query(models.Tarea).options(joinedload(models.Tarea.tipo)).all()
    print(tipo_tem[0].__dict__)
    return (db.query(models.Tarea)
        .options(joinedload(models.Tarea.tipo))
        .filter(models.Tarea.is_active == True)
        .offset(skip).limit(limit).all())

def get_tarea(db: Session, tarea_id: int):
    tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id, models.Tarea.is_active == True).first()
    if tarea is None:
        return None
    return tarea

def update_tarea(db: Session, tarea_id: int, tarea: schemas.TareaBase):
    db_tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id, models.Tarea.is_active == True).first()
    if db_tarea is None:
        return None
    
    for key, value in tarea.dict().items():
        setattr(db_tarea, key, value)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

def delete_tarea(db: Session, tarea_id: int):
    db_tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id).first()
    if db_tarea is None:
        return None
    db_tarea.is_active = False
    db.commit()
    return True

# Estado

def update_estado(db: Session, tarea_id: int, estado: schemas.EstadoTarea):
    db_tarea = db.query(models.Tarea).filter(models.Tarea.id == tarea_id, models.Tarea.is_active == True).first()
    print(db_tarea)
    if db_tarea is None:
        return None
    if db_tarea.estado == "pendiente" and estado == "en proceso":
        print("44444444444")
        db_tarea.estado = estado
        db.commit()
        db.refresh(db_tarea)
        return True
    if db_tarea.estado == "en proceso" and estado == "finalizado":
        print("5555555555555")
        db_tarea.estado = estado
        db.commit()
        db.refresh(db_tarea)
        return True
    else:
        return False
    
