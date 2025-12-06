from app.database import SessionLocal, engine
from app import models
from datetime import datetime, timedelta

# Aseguramos que las tablas existan
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def poblar_datos():
    # 1. Limpiar datos viejos
    db.query(models.InteraccionChat).delete()
    db.query(models.Reporte).delete()
    db.query(models.Cuenta).delete()
    db.query(models.Usuario).delete()
    db.query(models.Sector).delete()
    db.commit()

    print("Limpieza completa. Insertando datos...")

    # 2. Crear Sectores
    sec1 = models.Sector(nombre="Villa Los Heroes", mensaje_alerta="Sin incidentes")
    sec2 = models.Sector(nombre="Poblacion San Jose", tiene_corte=True, mensaje_alerta="Rotura de matriz en Av. Principal")
    db.add_all([sec1, sec2])
    db.commit()

    # 3. Crear Usuarios
    # Cliente con deuda
    user1 = models.Usuario(
        rut="12345678-9", 
        nombre_completo="Juan Perez", 
        direccion="Calle 1 #123", 
        sector_id=sec1.id
    )
    # Cliente al día
    user2 = models.Usuario(
        rut="98765432-1", 
        nombre_completo="Maria Gonzalez", 
        direccion="Av. San Jose #45", 
        sector_id=sec2.id
    )
    # Personal Administrativo
    admin = models.Usuario(
        rut="11111111-1",
        nombre_completo="Admin APR",
        direccion="Oficina Central",
        rol="admin",
        sector_id=sec1.id
    )
    db.add_all([user1, user2, admin])
    db.commit()

    # 4. Crear Cuentas (Deudas)
    # Deuda vencida para Juan
    cuenta1 = models.Cuenta(
        usuario_id=user1.id,
        periodo="2025-01",
        monto=15000,
        fecha_vencimiento=datetime.now() - timedelta(days=30), # Venció hace un mes
        esta_pagada=False
    )

    # Deuda actual para Jan
    cuenta2 = models.Cuenta(
        usuario_id=user1.id,
        periodo="2025-02",
        monto=12500,
        fecha_vencimiento=datetime.now() + timedelta(days=5),
        esta_pagada=False
    )
    db.add_all([cuenta1, cuenta2])
    db.commit()

    print("✅ Datos de prueba cargados exitosamente.")
    db.close()

if __name__ == "__main__":
    poblar_datos()