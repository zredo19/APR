from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORTANTE
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models, schemas
from typing import List
from app.chatbot_engine import procesar_mensaje
import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime

# Crear tablas (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Cooperativa APR")

# --- CONFIGURACIÓN CORS (Crucial para React) ---
origins = [
    "http://localhost:3000", # Puerto por defecto de React
    "http://localhost:5173", # Puerto por defecto de Vite (por si acaso)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RUTAS USUARIO FINAL ---

@app.get("/usuarios/{rut}/cuenta", response_model=List[schemas.Cuenta])
def ver_estado_cuenta(rut: str, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.rut == rut).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario.cuentas

@app.get("/usuarios/buscar/{rut}", response_model=schemas.Usuario)
def buscar_usuario(rut: str, db: Session = Depends(get_db)):
    # Endpoint auxiliar para obtener ID y Nombre desde el RUT
    usuario = db.query(models.Usuario).filter(models.Usuario.rut == rut).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.post("/reportes/", response_model=schemas.Reporte)
def crear_reporte(reporte: schemas.ReporteCreate, db: Session = Depends(get_db)):
    # 1. Validar usuario
    usuario = db.query(models.Usuario).filter(models.Usuario.id == reporte.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no existe")
    
    # 2. Crear reporte
    db_reporte = models.Reporte(**reporte.dict())
    db.add(db_reporte)
    db.commit()
    db.refresh(db_reporte)
    return db_reporte

@app.get("/info/estado-servicio")
def estado_servicio():
    return {
        "horario": "Lunes a Viernes 08:30 - 14:00",
        "fono_emergencia": "+569 9999 9999"
    }

# --- RUTAS PERSONAL/ADMIN ---

@app.get("/sectores/", response_model=List[schemas.Sector])
def ver_sectores(db: Session = Depends(get_db)):
    # Útil para "Ver estado por sector"
    return db.query(models.Sector).all()

@app.put("/sectores/{sector_id}", response_model=schemas.Sector)
def actualizar_sector(sector_id: int, datos: schemas.SectorUpdate, db: Session = Depends(get_db)):
    # Útil para "Marcar sector con problemas" o "Programar corte"
    db_sector = db.query(models.Sector).filter(models.Sector.id == sector_id).first()
    if not db_sector:
        raise HTTPException(status_code=404, detail="Sector no encontrado")
    
    # Actualizamos solo los campos que vengan en la petición
    if datos.tiene_corte is not None:
        db_sector.tiene_corte = datos.tiene_corte
    if datos.mensaje_alerta is not None:
        db_sector.mensaje_alerta = datos.mensaje_alerta
    if datos.inicio_corte_programado is not None:
        db_sector.inicio_corte_programado = datos.inicio_corte_programado
    if datos.fin_corte_programado is not None:
        db_sector.fin_corte_programado = datos.fin_corte_programado
    
    db.commit()
    db.refresh(db_sector)
    return db_sector

@app.get("/usuarios/personal", response_model=List[schemas.Usuario])
def ver_personal(db: Session = Depends(get_db)):
    return db.query(models.Usuario).filter(models.Usuario.rol != "cliente").all()

# --- RUTAS DE SOPORTE (Creación de datos base) ---
@app.post("/sectores/", response_model=schemas.Sector)
def crear_sector(sector: schemas.SectorCreate, db: Session = Depends(get_db)):
    db_sector = models.Sector(nombre=sector.nombre, mensaje_alerta=sector.mensaje_alerta)
    db.add(db_sector)
    db.commit()
    db.refresh(db_sector)
    return db_sector

@app.post("/usuarios/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = models.Usuario(**usuario.dict())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.post("/cuentas/", response_model=schemas.Cuenta)
def crear_cuenta(cuenta: schemas.CuentaCreate, db: Session = Depends(get_db)):
    db_cuenta = models.Cuenta(**cuenta.dict())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta

# --- RUTA CHATBOT (Registro de interacciones) ---
@app.post("/chat/interactuar")
def interactuar_chat(datos: schemas.ChatCreate, db: Session = Depends(get_db)):
    # 1. Buscamos el RUT si tenemos el ID de usuario (para personalizar la respuesta)
    rut_usuario = None
    if datos.usuario_id:
        user = db.query(models.Usuario).filter(models.Usuario.id == datos.usuario_id).first()
        if user:
            rut_usuario = user.rut

    # 2. Generamos la respuesta con el motor de IA
    respuesta_ia = procesar_mensaje(datos.mensaje_usuario, db, rut_usuario)

    # 3. Guardamos en historial (Requisito Rúbrica)
    interaccion = models.InteraccionChat(
        usuario_id=datos.usuario_id,
        mensaje_usuario=datos.mensaje_usuario,
        respuesta_bot=respuesta_ia
    )
    db.add(interaccion)
    db.commit()

    return {"respuesta": respuesta_ia}

# --- RUTA ADMIN: CARGA MASIVA DESDE EXCEL ---
@app.post("/admin/importar-excel")
async def importar_excel(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint para carga masiva de datos desde archivo Excel.
    
    Columnas esperadas: rut, nombre, direccion, sector, monto_deuda, periodo_deuda
    """
    # Validar que sea un archivo Excel
    if not archivo.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="El archivo debe ser formato Excel (.xlsx o .xls)")
    
    try:
        # Guardar archivo temporalmente
        temp_file = Path(f"temp_{archivo.filename}")
        with temp_file.open("wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)
        
        # Leer Excel con pandas
        df = pd.read_excel(temp_file)
        
        # Validar columnas requeridas
        columnas_requeridas = ['rut', 'nombre', 'direccion', 'sector', 'monto_deuda', 'periodo_deuda']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            temp_file.unlink()  # Eliminar archivo temporal
            raise HTTPException(
                status_code=400, 
                detail=f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}"
            )
        
        # Contadores para el resumen
        sectores_creados = 0
        usuarios_creados = 0
        usuarios_actualizados = 0
        cuentas_creadas = 0
        cuentas_actualizadas = 0
        
        # Procesar cada fila
        for index, row in df.iterrows():
            try:
                # 1. Verificar/Crear Sector
                sector_nombre = str(row['sector']).strip()
                sector = db.query(models.Sector).filter(models.Sector.nombre == sector_nombre).first()
                
                if not sector:
                    sector = models.Sector(nombre=sector_nombre)
                    db.add(sector)
                    db.flush()  # Para obtener el ID sin hacer commit
                    sectores_creados += 1
                
                # 2. Verificar/Crear/Actualizar Usuario
                rut = str(row['rut']).strip()
                usuario = db.query(models.Usuario).filter(models.Usuario.rut == rut).first()
                
                if usuario:
                    # Actualizar usuario existente
                    usuario.direccion = str(row['direccion']).strip()
                    usuario.sector_id = sector.id
                    usuarios_actualizados += 1
                else:
                    # Crear nuevo usuario
                    usuario = models.Usuario(
                        rut=rut,
                        nombre_completo=str(row['nombre']).strip(),
                        direccion=str(row['direccion']).strip(),
                        sector_id=sector.id,
                        rol="cliente"
                    )
                    db.add(usuario)
                    db.flush()  # Para obtener el ID
                    usuarios_creados += 1
                
                # 3. Procesar Deuda (si existe)
                monto_deuda = float(row['monto_deuda']) if pd.notna(row['monto_deuda']) else 0
                
                if monto_deuda > 0:
                    periodo_deuda = str(row['periodo_deuda']).strip()
                    
                    # Buscar si ya existe una cuenta para este periodo
                    cuenta_existente = db.query(models.Cuenta).filter(
                        models.Cuenta.usuario_id == usuario.id,
                        models.Cuenta.periodo == periodo_deuda
                    ).first()
                    
                    if cuenta_existente:
                        # Actualizar monto de cuenta existente
                        cuenta_existente.monto = int(monto_deuda)
                        cuenta_existente.esta_pagada = False
                        cuentas_actualizadas += 1
                    else:
                        # Crear nueva cuenta
                        # Calcular fecha de vencimiento (último día del mes del periodo)
                        try:
                            año, mes = periodo_deuda.split('-')
                            # Vencimiento: último día del mes
                            if int(mes) == 12:
                                fecha_venc = datetime(int(año) + 1, 1, 1)
                            else:
                                fecha_venc = datetime(int(año), int(mes) + 1, 1)
                        except:
                            # Si falla el parsing, usar fecha actual + 30 días
                            from datetime import timedelta
                            fecha_venc = datetime.now() + timedelta(days=30)
                        
                        nueva_cuenta = models.Cuenta(
                            usuario_id=usuario.id,
                            periodo=periodo_deuda,
                            monto=int(monto_deuda),
                            fecha_vencimiento=fecha_venc,
                            esta_pagada=False
                        )
                        db.add(nueva_cuenta)
                        cuentas_creadas += 1
                
            except Exception as e:
                # Si hay error en una fila, continuar con la siguiente
                print(f"Error procesando fila {index + 1}: {str(e)}")
                continue
        
        # Confirmar todos los cambios
        db.commit()
        
        # Eliminar archivo temporal
        temp_file.unlink()
        
        # Retornar resumen
        return {
            "mensaje": "Importación completada exitosamente",
            "resumen": {
                "filas_procesadas": len(df),
                "sectores_creados": sectores_creados,
                "usuarios_creados": usuarios_creados,
                "usuarios_actualizados": usuarios_actualizados,
                "cuentas_creadas": cuentas_creadas,
                "cuentas_actualizadas": cuentas_actualizadas
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Rollback en caso de error
        db.rollback()
        # Intentar eliminar archivo temporal si existe
        if temp_file.exists():
            temp_file.unlink()
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")