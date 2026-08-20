
# EndPoints

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import xlsxwriter
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind = engine)
app = FastAPI()

# Se agrega este cors para que la api se pueda consumir desde otro puerto
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tipo

@app.post("/tipo/", response_model = schemas.Tipo)
def create_tipo(tipo: schemas.TipoBase, db: Session = Depends(get_db)):
    return crud.create_tipo(db=db, tipo=tipo)

@app.get("/tipo/", response_model=list[schemas.Tipo])
def read_tipo(skip: int=0, limit:int=100, db: Session= Depends(get_db)):
    tipos = crud.get_tipo(db, skip=skip, limit=limit)
    return tipos

@app.delete("/tipo/{tipo_id}")
def delete_tipo(tipo_id: int, db:Session=Depends(get_db)):
    success = crud.delete_tipo(db, tipo_id=tipo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tipo not found")
    return {"detail":"Tipo deleted successfully"}

@app.put("/tipo/{tipo_id}", response_model=schemas.Tipo)
def read_tipo(tipo_id: int, tipo: schemas.TipoBase, db:Session=Depends(get_db)):
    db_tipo = crud.update_tipo(db, tipo_id = tipo_id, tipo= tipo)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo not found")
    return db_tipo

# Tarea

@app.post("/tarea/", response_model = schemas.Tarea)
def create_tarea(tarea: schemas.TareaBase, db: Session = Depends(get_db)):
    return crud.create_tarea(db=db, tarea=tarea)

@app.get("/tarea/", response_model=list[schemas.Tarea])
def read_tarea(skip: int=0, limit:int=100, db: Session= Depends(get_db)):
    tareas = crud.get_tareas(db, skip=skip, limit=limit)
    return tareas

@app.get("/tarea/{tarea_id}", response_model=schemas.Tarea)
def read_tarea(tarea_id: int, db: Session= Depends(get_db)):
    tarea = crud.get_tarea(db, tarea_id = tarea_id )
    if tarea is None:
         raise HTTPException(status_code=404, detail="Tarea not found")
    return tarea


@app.put("/tarea/{tarea_id}", response_model=schemas.Tarea)
def read_tarea(tarea_id: int, tarea: schemas.TareaBase, db:Session=Depends(get_db)):
    db_tarea = crud.update_tarea(db, tarea_id = tarea_id, tarea= tarea)
    if db_tarea is None:
        raise HTTPException(status_code=404, detail="Tarea not found")
    return db_tarea

@app.delete("/tarea/{tarea_id}")
def delete_tarea(tarea_id: int, db:Session=Depends(get_db)):
    success = crud.delete_tarea(db, tarea_id=tarea_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea not found")
    return {"detail":"Tarea deleted successfully"}

# Estado

@app.put("/tarea/{tarea_id}/estad")
def cambiar_estado(tarea_id: int, estado: schemas.EstadoTarea, db:Session=Depends(get_db)):
    db_tarea = crud.update_estado(db, tarea_id = tarea_id, estado = estado.estado)
    if db_tarea is None:
        raise HTTPException(status_code=404, detail="Tarea not found")
    return db_tarea

@app.get("/exportar-excel")
def exportar_excel(db: Session = Depends(get_db)):
    tareas = crud.get_tareas(db, skip=0, limit=100)
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Tareas")
    
    header = workbook.add_format({
        "bold": True,
        "bg_color": "#4472C4",
        "font_color": "white",
        "border": 1
    })
    # Cabeceras
    worksheet.write("A1", "N", header)
    worksheet.write("B1", "Descripcion", header)
    worksheet.write("C1", "Tipo de Actividad", header)
    worksheet.write("D1", "Prioridad", header)
    worksheet.write("E1", "Estado", header)
    worksheet.write("F1", "Fecha de Creacion", header)
    
    
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
    # Registros
    
    for fila, tarea in enumerate(tareas, start=1):
        worksheet.write(fila, 0, fila)
        worksheet.write(fila, 1, tarea.description)
        worksheet.write(fila, 2, tarea.tipo.nombre)
        worksheet.write(fila, 3, tarea.prioridad)
        worksheet.write(fila, 4, tarea.estado)
        worksheet.write_datetime(
        fila,
        5,
        tarea.fecha_creacion,
        date_format
        )
        print("****************tareas*************")
        print(type(tarea.fecha_creacion))
        print("****************tareas*************")
    
    worksheet.set_column("A:A", 10)
    worksheet.set_column("B:B", 50)
    worksheet.set_column("C:C", 20)
    worksheet.set_column("D:D", 10)
    worksheet.set_column("E:E", 10)
    worksheet.set_column("F:F", 20)   
        
    workbook.close()

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=tareas.xlsx"
        }
    )
    

    