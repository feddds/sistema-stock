# check_users.py
from app import app, db
from models import Usuario

def check_users():
    print("👥 Verificando usuarios en la base de datos...")
    
    with app.app_context():
        usuarios = Usuario.query.all()
        
        if not usuarios:
            print("❌ No hay usuarios en la base de datos")
            return
        
        print("\n📋 USUARIOS ENCONTRADOS:")
        for usuario in usuarios:
            print(f"   👤 {usuario.username} -> Rol: {usuario.rol}")
            
        # Verificar usuario admin específicamente
        admin = Usuario.query.filter_by(username='admin').first()
        if admin:
            print(f"\n✅ Admin encontrado: {admin.username} (Rol: {admin.rol})")
            # Verificar contraseña
            if admin.check_password('admin123'):
                print("✅ Contraseña correcta")
            else:
                print("❌ Contraseña incorrecta")
        else:
            print("❌ Usuario admin no encontrado")

if __name__ == '__main__':
    check_users()