
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
def read_tarea(skip: int=0, limit: int | None = None, db: Session= Depends(get_db)):
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
    tareas = crud.get_tareas(db, skip=0, limit = None)
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Tareas")
    
    header = workbook.add_format({
        "bold": True,
        "bg_color": "#4472C4",
        "font_color": "white",
        "border": 4,
        "align": "center",
        "border_color": "#D9E1F2"
    })
    
    # Celdas normales
    cell_format_1 = workbook.add_format({
        "border": 1,
        "border_color": "#000000",
        "valign": "vcenter"
    })
    
    cell_format_2 = workbook.add_format({
        "border": 1,
        "border_color": "#000000",
        "bg_color": "#D3D3D3",
        "valign": "vcenter"
    })
    
    title_format = workbook.add_format({
        "bold": True,
        "font_size": 22,
        "font_color": "black",
        "bg_color": "white",
        "align": "center",
        "valign": "vcenter"
    })
    
    # Cabeceras
    worksheet.merge_range("A3:F3", "REPORTE DE TAREAS", title_format)
    worksheet.write("A5", "N", header)
    worksheet.write("B5", "Descripcion", header)
    worksheet.write("C5", "Tipo de Actividad", header)
    worksheet.write("D5", "Prioridad", header)
    worksheet.write("E5", "Estado", header)
    worksheet.write("F5", "Fecha de Creacion", header)
    
    
    date_format_1 = workbook.add_format({
        'num_format': 'dd/mm/yyyy hh:mm',
        "border": 1,
        "border_color": "#000000",
        "valign": "vcenter"
    })
    
    date_format_2 = workbook.add_format({
        'num_format': 'dd/mm/yyyy hh:mm',
        "border": 1,
        "border_color": "#000000",
        "bg_color": "#D3D3D3",
        "valign": "vcenter"
    })
    
    # Registros
    fila = 5
    for tarea in tareas:
        argumento = None
        formato_fech = None
        if fila % 2 == 0:
            argumento = cell_format_2
            formato_fech = date_format_2 
        else:
            argumento = cell_format_1
            formato_fech = date_format_1 
        
        worksheet.write(fila, 0, fila-4, argumento)
        worksheet.write(fila, 1, tarea.description, argumento)
        worksheet.write(fila, 2, tarea.tipo.nombre, argumento)
        worksheet.write(fila, 3, tarea.prioridad, argumento)
        worksheet.write(fila, 4, tarea.estado, argumento)
        worksheet.write_datetime(fila, 5, tarea.fecha_creacion, formato_fech)
        fila += 1
    
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
    

@app.get("/tareas/prioridad-estado")
def exportar_excel(db: Session = Depends(get_db)):
    tareas = crud.get_tareas(db, skip=0, limit = None)
    diccionario = {}
    estados = ["pendiente", "en proceso", "finalizado"]
    prioridad = ["baja", "media", "alta"]
    clave = ""
    for tarea in tareas:
        clave = tarea.prioridad + tarea.estado
        if(a is not diccionario):
            diccionario[clave] = diccionario.get(clave, 0) + 1
        else:
            diccionario[clave] = diccionario.get(clave, 0) + 1
   
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Tareas")
    
    header = workbook.add_format({
        "bold": True,
        "bg_color": "#4472C4",
        "font_color": "white",
        "border": 4,
        "align": "center",
        "border_color": "#D9E1F2"
    })
    
    # Celdas normales
    cell_format_1 = workbook.add_format({
        "border": 1,
        "border_color": "#000000",
        "valign": "vcenter"
    })
    
    title_format = workbook.add_format({
        "bold": True,
        "font_size": 22,
        "font_color": "black",
        "bg_color": "white",
        "align": "center",
        "valign": "vcenter"
    })
    
    # Cabeceras
    worksheet.merge_range("A3:F3", "REPORTE", title_format)
    worksheet.write("B6", "PENDIENTE", header)
    worksheet.write("C6", "EN PROCESO", header)
    worksheet.write("D6", "FINALIZADO", header) 
    worksheet.write("E6", "TOTAL", header)
    
    worksheet.write("A7", "BAJA", header)
    worksheet.write("A8", "MEDIA", header)
    worksheet.write("A9", "ALTA", header) 
    worksheet.write("D10", "TOTALES", header)

    # Registros
    fila = 6
    columna = 1
    suma_1 = 0
    suma_total = 0
    for p in prioridad:
        for e in estados:
            worksheet.write(fila, columna, diccionario[p+e], cell_format_1)
            suma_1 += diccionario[p+e]
            columna += 1
        worksheet.write(fila, len(prioridad) + 1, suma_1, cell_format_1)
        suma_total += suma_1
        suma_1 = 0
        columna = 1  
        fila += 1
    worksheet.write(len(estados) + 6, len(prioridad) + 1, suma_total, cell_format_1)
    

    worksheet.set_column("A:A", 20)
    worksheet.set_column("B:B", 20)
    worksheet.set_column("C:C", 20)
    worksheet.set_column("D:D", 20)
 
    workbook.close()

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=tareas.xlsx"
        }
    )
    
    
    
    
      
          
       