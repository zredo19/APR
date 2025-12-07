from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200))  # 30 días por defecto

# Contexto para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme para extraer el token del header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una contraseña en texto plano coincida con su hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña usando bcrypt.
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, rut: str, password: str):
    """
    Autentica un usuario verificando su RUT y contraseña.
    Retorna el usuario si las credenciales son correctas, None en caso contrario.
    """
    user = db.query(models.Usuario).filter(models.Usuario.rut == rut).first()
    
    if not user:
        return None
    
    # Verificar que el usuario tenga contraseña (solo admin/personal)
    if not user.hashed_password:
        return None
    
    # Verificar la contraseña
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crea un token JWT con los datos proporcionados y tiempo de expiración.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependencia que extrae y valida el token JWT.
    Retorna el usuario actual si el token es válido.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        rut: str = payload.get("sub")
        
        if rut is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    user = db.query(models.Usuario).filter(models.Usuario.rut == rut).first()
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: models.Usuario = Depends(get_current_user)):
    """
    Dependencia que verifica que el usuario actual esté activo.
    También verifica que tenga un rol administrativo (admin o personal).
    """
    # Verificar que el usuario tenga un rol administrativo
    if current_user.rol not in ["admin", "personal"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este recurso"
        )
    
    return current_user
