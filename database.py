from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os


load_dotenv(encoding="utf-8")  # Charger les variables d'environnement à partir du fichier .env

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "taches_db")

database_url = URL.create(
    drivername="postgresql", 
    username=DB_USER, 
    password=DB_PASSWORD, 
    host=DB_HOST,
    database=DB_NAME,
    query={"client_encoding": "utf8"})

if not database_url:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie")

engine = create_engine(database_url, connect_args={})
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()