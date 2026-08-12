from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#creando motor de base de datos
engine = create_engine("mysql+pymysql://root:@localhost:3306/data_b_tareas")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Crear una clase Base que sera la base para nuestros modelos
Base = declarative_base()