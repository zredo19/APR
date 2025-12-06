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

# --- CHAT (Nuevo) ---
class ChatCreate(BaseModel):
    usuario_id: Optional[int] = None
    mensaje_usuario: str
    respuesta_bot: str

class ChatLog(ChatCreate):
    id: int
    fecha: datetime
    
    class Config:
        from_attributes = True

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