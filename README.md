# Chatbot de atención al cliente — APR (Agua Potable Rural)

Asistente conversacional para una cooperativa de Agua Potable Rural. Responde
consultas de los socios sobre **estado de deuda, pagos, cortes de servicio,
subsidios y beneficios**, y le da al personal un panel para gestionar usuarios,
sectores y cuentas.

El chatbot combina dos capas: una **base de conocimiento con coincidencia
difusa** (`difflib` + keywords) para las preguntas frecuentes, y **Gemini con
function calling** para las consultas que requieren mirar la base de datos —
el modelo decide cuándo invocar la herramienta que consulta el saldo real del
socio en vez de inventar la respuesta.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI · SQLAlchemy · Pydantic |
| Base de datos | PostgreSQL |
| IA | Google Gemini (`google-genai`) con function calling |
| Auth | JWT (`python-jose`) + hash de contraseñas con bcrypt/passlib |
| Frontend | React 19 · Vite · Tailwind CSS · React Router · Axios |
| Datos masivos | pandas + openpyxl (importación desde Excel) |

## Funcionalidades

**Para el socio**
- Consulta de saldo y estado de cuenta por RUT
- Preguntas frecuentes: horarios, ubicación, medios de pago, requisitos de inscripción
- Orientación sobre subsidio estatal según Registro Social de Hogares
- Información del Fondo Solidario, becas escolares y aguinaldos
- Diagnóstico guiado de sobreconsumo (prueba de la llave de paso para detectar fugas internas)
- Reporte de emergencias y cortes por sector

**Para el personal**
- Login con JWT y roles
- ABM de usuarios, sectores y cuentas
- Actualización del estado del servicio por sector
- Importación masiva de cuentas desde planilla Excel
- Panel de métricas de uso del chatbot
- Feedback por interacción, para medir qué respuestas sirven y cuáles no

## Modelo de datos

`sectores` · `usuarios` · `cuentas` · `reportes` · `interacciones_chat`

## Levantar en local

Requisitos: Python 3.12+, Node 18+, PostgreSQL.

### Backend

```bash
cd APR_Backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # completar con tus credenciales
python seed.py                  # datos de ejemplo
python create_admin.py          # crear usuario administrador

uvicorn app.main:app --reload
```

API en `http://localhost:8000` · documentación interactiva en `http://localhost:8000/docs`

### Frontend

```bash
cd APR_Frontend
npm install
npm run dev
```

App en `http://localhost:5173`

## Variables de entorno

Ver `APR_Backend/.env.example`. Se necesita:

- `GEMINI_API_KEY` — clave de https://aistudio.google.com/apikey
- `DATABASE_URL` — cadena de conexión a PostgreSQL
- `SECRET_KEY` — clave para firmar los JWT (`openssl rand -hex 32`)

Ninguna de estas debe commitearse. El `.env` está en `.gitignore`.

## Endpoints principales

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/token` | Login del personal, devuelve JWT |
| `POST` | `/chat/interactuar` | Conversación con el asistente |
| `PUT` | `/chat/{id}/feedback` | Registrar si la respuesta sirvió |
| `GET` | `/usuarios/{rut}/cuenta` | Estado de cuenta del socio |
| `POST` | `/reportes/` | Reportar emergencia o corte |
| `GET` | `/info/estado-servicio` | Estado del servicio por sector |
| `PUT` | `/sectores/{id}` | Actualizar estado de un sector |
| `POST` | `/admin/importar-excel` | Carga masiva de cuentas |
| `GET` | `/admin/metricas` | Métricas de uso del chatbot |
