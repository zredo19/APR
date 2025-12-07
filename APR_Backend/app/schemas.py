from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- SECTOR ---
class SectorBase(BaseModel):
    nombre: str
    mensaje_alerta: Optional[str] = None
    inicio_corte_programado: Optional[datetime] = None
    fin_corte_programado: Optional[datetime] = None

class SectorCreate(SectorBase):
    pass

class Sector(SectorBase):
    id: int
    tiene_corte: bool
    
    class Config:
        from_attributes = True

# --- USUARIO ---
class UsuarioBase(BaseModel):
    rut: str
    nombre_completo: str
    direccion: str
    rol: str = "cliente"

class UsuarioCreate(UsuarioBase):
    sector_id: int

class Usuario(UsuarioBase):
    id: int
    sector: Sector
    
    class Config:
        from_attributes = True

# --- CUENTA ---
class CuentaBase(BaseModel):
    periodo: str
    monto: int
    fecha_vencimiento: datetime

class CuentaCreate(CuentaBase):
    usuario_id: int

class Cuenta(CuentaBase):
    id: int
    fecha_emision: datetime
    esta_pagada: bool
    fecha_pago: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- CHAT (Actualizado con feedback) ---
class ChatCreate(BaseModel):
    usuario_id: Optional[int] = None
    mensaje_usuario: str
    respuesta_bot: str

class ChatResponse(BaseModel):
    """Respuesta del chat que incluye el ID de la interacción para feedback"""
    id: int
    respuesta: str
    mensaje_usuario: str
    
    class Config:
        from_attributes = True

class ChatLog(ChatCreate):
    id: int
    fecha: datetime
    es_util: Optional[bool] = None
    
    class Config:
        from_attributes = True

class FeedbackUpdate(BaseModel):
    """Esquema para actualizar el feedback de una interacción"""
    es_util: bool

# --- REPORTE (Cortes, Reclamos) ---
class ReporteBase(BaseModel):
    tipo: str # 'corte', 'reclamo'
    descripcion: str

class ReporteCreate(ReporteBase):
    usuario_id: int

class Reporte(ReporteBase):
    id: int
    estado: str
    fecha_creacion: datetime
    respuesta_personal: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- Esquema para Actualizar Sector (Admin) ---
class SectorUpdate(BaseModel):
    tiene_corte: Optional[bool] = None
    mensaje_alerta: Optional[str] = None
    inicio_corte_programado: Optional[datetime] = None
    fin_corte_programado: Optional[datetime] = None

# --- AUTENTICACIÓN JWT ---
class Token(BaseModel):
    """Respuesta del endpoint de login"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Datos decodificados del token JWT"""
    rut: Optional[str] = None

class UserInDB(UsuarioBase):
    """Usuario con contraseña hasheada (para uso interno)"""
    hashed_password: Optional[str] = None