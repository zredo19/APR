import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No se encontró la API KEY en el archivo .env")
else:
    genai.configure(api_key=api_key)
    print("✅ Conectado. Buscando modelos disponibles para tu clave...")
    try:
        hay_modelos = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
                hay_modelos = True
        
        if not hay_modelos:
            print("⚠️ No se encontraron modelos compatibles con 'generateContent'.")
    except Exception as e:
        print(f"❌ Error al listar modelos: {e}")