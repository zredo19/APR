from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# IMPORTANTE: Reemplaza 'postgres' y 'tu_contraseña' con tus credenciales reales.
# El formato es: postgresql://usuario:contraseña@servidor/nombre_base_datos
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/APR"

# Creamos el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creamos una sesión local para interactuar con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para nuestros modelos (tablas)
Base = declarative_base()

# Función de dependencia para obtener la sesión de BD en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()