"""
Script temporal para crear un usuario administrador inicial con contraseña.
Ejecutar una sola vez para inicializar el sistema de autenticación.

Uso:
    python create_admin.py
"""

from app.database import SessionLocal
from app.models import Usuario, Sector
from app.auth import get_password_hash

def create_admin_user():
    """
    Crea un usuario administrador con contraseña hasheada.
    """
    db = SessionLocal()
    
    try:
        # Datos del administrador
        print("=== Crear Usuario Administrador ===\n")
        
        rut = input("Ingrese el RUT del administrador (ej: 12345678-9): ").strip()
        nombre = input("Ingrese el nombre completo: ").strip()
        password = input("Ingrese la contraseña: ").strip()
        direccion = input("Ingrese la dirección: ").strip()
        
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(Usuario.rut == rut).first()
        
        if existing_user:
            print(f"\n⚠️  El usuario con RUT {rut} ya existe.")
            actualizar = input("¿Desea actualizar su contraseña? (s/n): ").strip().lower()
            
            if actualizar == 's':
                # Actualizar contraseña del usuario existente
                existing_user.hashed_password = get_password_hash(password)
                existing_user.rol = "admin"  # Asegurar que sea admin
                db.commit()
                print(f"\n✅ Contraseña actualizada para {existing_user.nombre_completo}")
            else:
                print("\n❌ Operación cancelada.")
            
            return
        
        # Buscar o crear un sector por defecto
        sector = db.query(Sector).first()
        
        if not sector:
            print("\n⚠️  No hay sectores en la base de datos. Creando sector por defecto...")
            sector = Sector(nombre="Administración", mensaje_alerta=None)
            db.add(sector)
            db.flush()
        
        # Crear el usuario administrador
        hashed_password = get_password_hash(password)
        
        admin_user = Usuario(
            rut=rut,
            nombre_completo=nombre,
            direccion=direccion,
            rol="admin",
            sector_id=sector.id,
            hashed_password=hashed_password
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ Usuario administrador creado exitosamente!")
        print(f"   RUT: {admin_user.rut}")
        print(f"   Nombre: {admin_user.nombre_completo}")
        print(f"   Rol: {admin_user.rol}")
        print(f"\n💡 Ahora puedes hacer login en POST /token con:")
        print(f"   username: {admin_user.rut}")
        print(f"   password: [la contraseña que ingresaste]")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error al crear usuario: {str(e)}")
    
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
