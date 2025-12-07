"""
Script para migrar de google.generativeai a google-genai

Ejecutar: python migrate_to_genai.py
"""

import os
import re

# Leer el archivo main.py
with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Cambiar el import
content = content.replace(
    'import google.generativeai as genai',
    'from google import genai\nfrom google.genai import types'
)

# 2. Cambiar la configuración
old_config = '''load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") # O pega tu clave aquí directamente si solo estás probando, pero NO es recomendable para producción.

genai.configure(api_key=API_KEY)'''

new_config = '''load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Crear cliente de Gemini con google-genai
client = genai.Client(api_key=API_KEY)'''

content = content.replace(old_config, new_config)

# 3. Cambiar la inicialización del modelo
old_model = '''model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=INSTRUCCIONES_SISTEMA,
    tools=[consultar_deuda_rut]
)'''

new_model = '''# Configuración del modelo
MODEL_NAME = "gemini-2.5-flash"'''

content = content.replace(old_model, new_model)

# 4. Cambiar el endpoint del chat
old_chat = '''    try:
        # Iniciamos el chat con Function Calling automático
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        # Enviamos el mensaje del usuario
        response = chat.send_message(consulta.mensaje)
        
        # Obtenemos la respuesta final (texto)
        texto_respuesta = response.text'''

new_chat = '''    try:
        # Crear chat con google-genai
        chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=INSTRUCCIONES_SISTEMA,
                tools=[consultar_deuda_rut],  # Function calling automático
            )
        )
        
        # Enviar mensaje del usuario
        response = chat.send_message(consulta.mensaje)
        
        # Obtener la respuesta final (texto)
        texto_respuesta = response.text'''

content = content.replace(old_chat, new_chat)

# Guardar el archivo modificado
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Migración completada!")
print("\nCambios realizados:")
print("1. Import actualizado: from google import genai")
print("2. Cliente inicializado: client = genai.Client(api_key=API_KEY)")
print("3. Modelo configurado con MODEL_NAME")
print("4. Endpoint de chat actualizado para usar client.chats.create()")
print("\nAhora ejecuta: pip install google-genai")
