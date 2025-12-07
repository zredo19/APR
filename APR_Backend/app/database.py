import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Cargar variables locales si existe el archivo .env (útil para tu PC)
load_dotenv()

# --- PASO 1: Obtener la URL ---
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- PASO 2: Diagnóstico y Fallback ---
if not SQLALCHEMY_DATABASE_URL:
    print("⚠️  PELIGRO: Render no encontró la variable DATABASE_URL.")
    print("⚠️  Usando configuración de 'localhost' por defecto (esto fallará en la nube).")
    # Configuración por defecto para desarrollo local (tu PC)
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost/apr_db"
else:
    print("✅  ÉXITO: Variable DATABASE_URL detectada correctamente.")

# --- PASO 3: Corrección obligatoria para Render ---
# Render entrega URLs que empiezan con "postgres://", pero SQLAlchemy requiere "postgresql://"
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- PASO 4: Crear la conexión ---
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
except Exception as e:
    print(f"❌ Error fatal al crear el engine de base de datos: {e}")
    raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función de dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()