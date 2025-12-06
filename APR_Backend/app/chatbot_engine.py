import difflib
from sqlalchemy.orm import Session
from app import models
import re

# Base de Conocimiento Estática (FAQs)
FAQS = {
    "horario": "Nuestro horario de atención es de Lunes a Viernes de 08:30 a 14:00 hrs.",
    "ubicacion": "Estamos ubicados en Calle Principal 123, Graneros.",
    "telefono": "Nuestro fono de emergencias es +569 9999 9999.",
    "pagar": "Puedes pagar tu cuenta presencialmente o mediante transferencia a la cuenta vista del Banco Estado.",
    "requisitos": "Para inscribirte necesitas: Fotocopia de Carnet y Certificado de Dominio Vigente."
}

KEYWORDS = {
    "saldo": ["saldo", "deuda", "cuanto debo", "cuenta"],
    "corte": ["corte", "sin agua", "no tengo agua", "fuga"],
    "estado": ["estado", "servicio", "hay agua"]
}

def normalizar(texto: str) -> str:
    return texto.lower().strip()

def buscar_similitud_faq(mensaje: str):
    # Busca la pregunta más parecida en las FAQs
    claves = list(FAQS.keys())
    coincidencia = difflib.get_close_matches(mensaje, claves, n=1, cutoff=0.6)
    if coincidencia:
        return FAQS[coincidencia[0]]
    return None

def procesar_mensaje(mensaje: str, db: Session, rut_usuario: str = None) -> str:
    msg = normalizar(mensaje)

    # 1. SALUDOS
    if any(x in msg for x in ["hola", "buenas", "aló"]):
        return "¡Hola! Soy el asistente virtual del APR. Puedo ayudarte con horarios, saldos o reportes de cortes."

    # 2. CONSULTAS DE SALDO (Conexión a BD)
    if any(x in msg for x in KEYWORDS["saldo"]):
        if not rut_usuario:
            return "Para ver tu saldo, necesito que inicies sesión o me digas tu RUT primero."
        
        # Buscamos al usuario en la BD
        usuario = db.query(models.Usuario).filter(models.Usuario.rut == rut_usuario).first()
        if not usuario:
            return "No encuentro un usuario con ese RUT."
        
        # Calculamos deuda total
        deuda_total = sum(c.monto for c in usuario.cuentas if not c.esta_pagada)
        if deuda_total == 0:
            return "¡Excelente! No tienes deudas pendientes. 🌟"
        else:
            return f"Actualmente tienes una deuda total de ${deuda_total:,}. ¿Deseas información sobre cómo pagar?"

    # 3. CONSULTAS DE CORTES (Conexión a BD)
    if any(x in msg for x in KEYWORDS["corte"] + KEYWORDS["estado"]):
        if rut_usuario:
            usuario = db.query(models.Usuario).filter(models.Usuario.rut == rut_usuario).first()
            if usuario and usuario.sector.tiene_corte:
                return f"⚠️ Atención: Tu sector '{usuario.sector.nombre}' presenta un corte reportado: {usuario.sector.mensaje_alerta}"
            elif usuario:
                return f"Tu sector '{usuario.sector.nombre}' está operando con normalidad. Si no tienes agua, por favor revisa tu llave de paso interna."
        
        # Si no sabemos quién es, damos info general
        sectores_con_corte = db.query(models.Sector).filter(models.Sector.tiene_corte == True).all()
        if sectores_con_corte:
            nombres = ", ".join([s.nombre for s in sectores_con_corte])
            return f"Actualmente tenemos cortes programados o emergencias en: {nombres}."
        else:
            return "El servicio está operando normalmente en todos los sectores."

    # 4. BUSQUEDA POR SIMILITUD (FAQs generales)
    # Intentamos matchear palabras clave de las FAQs dentro del mensaje
    for key, respuesta in FAQS.items():
        if key in msg: # Búsqueda simple
            return respuesta
    
    # 5. FALLBACK (No entendí)
    return "Disculpa, no entendí bien tu consulta. Prueba preguntando por 'horario', 'saldo' o 'cortes'."