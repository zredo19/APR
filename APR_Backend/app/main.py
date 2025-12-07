from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import engine, get_db, SessionLocal
from app import models, schemas
from app.auth import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import List
from app.chatbot_engine import procesar_mensaje
import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import os
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

INSTRUCCIONES_SISTEMA = """
Eres el Asistente Virtual oficial de la Cooperativa de Agua APR Graneros.
Tu tono es amable, profesional y servicial.
Responde de forma concisa (máximo 3 oraciones si es posible).

INFORMACIÓN DE LA COOPERATIVA:
- Horario de atención: Lunes a Viernes de 08:30 a 14:00 hrs.
- Teléfono de emergencias: +569 9999 9999.
- Dirección: Calle Principal 123, Graneros.
- Cortes programados: No hay cortes programados para esta semana.
- Cómo pagar: Se puede pagar en la oficina o por transferencia bancaria (Cuenta Rut: 12.345.678-9).

REGLAS:
- Si te preguntan algo fuera del tema del agua o la cooperativa, responde amablemente que solo puedes ayudar con temas del APR.
- Si no sabes la respuesta, sugiere llamar al número de emergencias.
"""

# --- HERRAMIENTA (TOOL) PARA GEMINI ---
def consultar_deuda_rut(rut: str):
    """
    Consulta la deuda total de un usuario dado su RUT.
    Retorna un mensaje con el monto total y los periodos adeudados, o indica si no tiene deuda.
    """
    db = SessionLocal()
    try:
        # Buscar usuario
        usuario = db.query(models.Usuario).filter(models.Usuario.rut == rut).first()
        if not usuario:
            return f"No encontré ningún usuario con el RUT {rut}."
        
        # Buscar cuentas impagas
        cuentas_impagas = db.query(models.Cuenta).filter(
            models.Cuenta.usuario_id == usuario.id,
            models.Cuenta.esta_pagada == False
        ).all()
        
        if not cuentas_impagas:
            return f"El usuario {usuario.nombre_completo} no tiene deudas pendientes. ¡Está al día!"
        
        total_deuda = sum(c.monto for c in cuentas_impagas)
        periodos = [c.periodo for c in cuentas_impagas]
        
        return f"El usuario {usuario.nombre_completo} tiene una deuda total de ${total_deuda} correspondiente a los periodos: {', '.join(periodos)}."
        
    except Exception as e:
        return f"Ocurrió un error al consultar la deuda: {str(e)}"
    finally:
        db.close()

# model = genai.GenerativeModel(
#     model_name="gemini-2.5-flash",
#     system_instruction=INSTRUCCIONES_SISTEMA,
#     tools=[consultar_deuda_rut]
# )

# Crear tablas (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Cooperativa APR")

# Modelos de datos (Pydantic)
class ConsultaUsuario(BaseModel):
    mensaje: str # Lo que escribe el usuario

class RespuestaChat(BaseModel):
    respuesta: str
    mensaje_usuario: str # Agregamos esto para arreglar el error que tenías antes

# --- CONFIGURACIÓN CORS (Crucial para React) ---
origins = [
    "http://localhost:3000",  # Puerto por defecto de React
    "http://localhost:5173",  # Puerto por defecto de Vite (por si acaso)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTENTICACIÓN ---

@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint de login que recibe username (RUT) y password.
    Retorna un token JWT si las credenciales son correctas.
    """
    # El username será el RUT del usuario
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="RUT o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.rut},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

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
@app.post("/chat/interactuar", response_model=RespuestaChat)
async def interactuar(consulta: ConsultaUsuario):
    try:
        # Iniciamos el chat con Function Calling automático
        chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=INSTRUCCIONES_SISTEMA,
                tools=[consultar_deuda_rut],  # Function calling automático
            )
        )
        
        # Enviamos el mensaje del usuario
        response = chat.send_message(consulta.mensaje)
        
        # Obtenemos la respuesta final (texto)
        texto_respuesta = response.text

        # Retornamos la respuesta limpia
        return {
            "respuesta": texto_respuesta,
            "mensaje_usuario": consulta.mensaje
        }

    except Exception as e:
        print(f"Error en chat: {e}")
        return {
            "respuesta": "Lo siento, tuve un problema interno al procesar tu solicitud. Intenta de nuevo.",
            "mensaje_usuario": consulta.mensaje
        }

# --- RUTA FEEDBACK: Actualizar utilidad de una interacción ---
@app.put("/chat/{interaccion_id}/feedback")
def actualizar_feedback(interaccion_id: int, feedback: schemas.FeedbackUpdate, db: Session = Depends(get_db)):
    """
    Permite al usuario marcar si una respuesta del bot fue útil o no.
    Esto ayuda a mejorar el chatbot iterativamente.
    """
    interaccion = db.query(models.InteraccionChat).filter(models.InteraccionChat.id == interaccion_id).first()
    
    if not interaccion:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    
    interaccion.es_util = feedback.es_util
    db.commit()
    
    return {"mensaje": "Feedback registrado exitosamente", "es_util": feedback.es_util}

# --- RUTA ADMIN: Métricas del Chatbot ---
@app.get("/admin/metricas")
def obtener_metricas(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Endpoint para que los administradores vean métricas del chatbot:
    - Total de interacciones
    - Tasa de éxito (% de respuestas útiles)
    - Últimas 5 preguntas donde el bot falló
    """
    from sqlalchemy import func
    
    # 1. Total de interacciones
    total_interacciones = db.query(models.InteraccionChat).count()
    
    # 2. Tasa de éxito
    if total_interacciones > 0:
        # Contar interacciones útiles (es_util = True)
        interacciones_utiles = db.query(models.InteraccionChat).filter(
            models.InteraccionChat.es_util == True
        ).count()
        
        # Contar interacciones con feedback (es_util no es None)
        interacciones_con_feedback = db.query(models.InteraccionChat).filter(
            models.InteraccionChat.es_util.isnot(None)
        ).count()
        
        # Calcular tasa de éxito sobre las que tienen feedback
        if interacciones_con_feedback > 0:
            tasa_exito = round((interacciones_utiles / interacciones_con_feedback) * 100, 2)
        else:
            tasa_exito = 0.0
    else:
        tasa_exito = 0.0
        interacciones_con_feedback = 0
    
    # 3. Últimas 5 preguntas fallidas (es_util = False)
    preguntas_fallidas = db.query(models.InteraccionChat).filter(
        models.InteraccionChat.es_util == False
    ).order_by(models.InteraccionChat.fecha.desc()).limit(5).all()
    
    preguntas_fallidas_list = [
        {
            "id": p.id,
            "mensaje_usuario": p.mensaje_usuario,
            "respuesta_bot": p.respuesta_bot,
            "fecha": p.fecha.isoformat()
        }
        for p in preguntas_fallidas
    ]
    
    return {
        "total_interacciones": total_interacciones,
        "interacciones_con_feedback": interacciones_con_feedback,
        "tasa_exito": tasa_exito,
        "preguntas_fallidas": preguntas_fallidas_list
    }

# --- RUTA ADMIN: CARGA MASIVA DESDE EXCEL ---
@app.post("/admin/importar-excel")
async def importar_excel(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
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