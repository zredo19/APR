# APR Backend

Este es el backend de la aplicación APR, construido con FastAPI y Python.

## Requisitos Previos

- Python (versión 3.8 o superior)
- PostgreSQL (asegúrate de tener una instancia corriendo)

## Configuración del Entorno

1.  Navega al directorio del backend:
    ```bash
    cd APR_Backend
    ```

2.  Crea un entorno virtual:
    ```bash
    python -m venv venv
    ```

3.  Activa el entorno virtual:
    - En Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - En macOS/Linux:
      ```bash
      source venv/Scripts/activate
      ```

## Instalación

Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Configuración de la Base de Datos

Asegúrate de que tu base de datos PostgreSQL esté corriendo y accesible. Es posible que necesites configurar variables de entorno para la conexión a la base de datos si el proyecto lo requiere (revisar `database.py` o archivos `.env` si existen).

## Ejecución

Para iniciar el servidor de desarrollo:

```bash
uvicorn app.main:app --reload
```

El servidor estará corriendo en `http://127.0.0.1:8000`.

## Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva de la API en:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
