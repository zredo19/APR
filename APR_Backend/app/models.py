from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Sector(Base):
    __tablename__ = "sectores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    
    # Estado actual
    tiene_corte = Column(Boolean, default=False)     
    mensaje_alerta = Column(String, nullable=True)
    
    # Para "Programar corte"
    inicio_corte_programado = Column(DateTime, nullable=True)
    fin_corte_programado = Column(DateTime, nullable=True)

    usuarios = relationship("Usuario", back_populates="sector")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String, unique=True, index=True)
    nombre_completo = Column(String)
    rol = Column(String, default="cliente") # 'cliente', 'admin', 'tecnico'
    direccion = Column(String)
    sector_id = Column(Integer, ForeignKey("sectores.id"))

    sector = relationship("Sector", back_populates="usuarios")
    cuentas = relationship("Cuenta", back_populates="usuario")
    reportes = relationship("Reporte", back_populates="usuario")
    chats = relationship("InteraccionChat", back_populates="usuario") # Nueva relación

class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    
    periodo = Column(String) # Ej: "2025-10" para identificar el mes cobrado
    monto = Column(Integer)
    fecha_emision = Column(DateTime(timezone=True), server_default=func.now())
    fecha_vencimiento = Column(DateTime)
    
    esta_pagada = Column(Boolean, default=False)
    fecha_pago = Column(DateTime, nullable=True) # Para saber cuándo pagó

    usuario = relationship("Usuario", back_populates="cuentas")

class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo = Column(String) # 'corte', 'reclamo', 'sugerencia'
    descripcion = Column(Text)
    estado = Column(String, default="pendiente") 
    respuesta_personal = Column(Text, nullable=True) # Para que el personal responda
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="reportes")

# --- NUEVA TABLA PARA IA ---
class InteraccionChat(Base):
    __tablename__ = "interacciones_chat"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Nullable por si habla un anónimo
    mensaje_usuario = Column(Text)
    respuesta_bot = Column(Text)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    es_util = Column(Boolean, nullable=True) # Para medir satisfacción (Rúbrica)

    usuario = relationship("Usuario", back_populates="chats")