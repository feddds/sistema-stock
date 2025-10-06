# create_users.py
from app import app, db
from models import Usuario

def create_all_users():
    print("👥 Creando todos los usuarios de prueba...")
    
    with app.app_context():
        usuarios = [
            {
                'username': 'admin',
                'password': 'admin123', 
                'rol': 'admin',
                'nombre': 'Administrador Total',
                'email': 'admin@empresa.com'
            },
            {
                'username': 'compras',
                'password': 'compras123',
                'rol': 'compras', 
                'nombre': 'Responsable Compras',
                'email': 'compras@empresa.com'
            },
            {
                'username': 'stock',
                'password': 'stock123',
                'rol': 'stock',
                'nombre': 'Responsable Stock', 
                'email': 'stock@empresa.com'
            },
            {
                'username': 'basico',
                'password': 'basico123',
                'rol': 'basico',
                'nombre': 'Usuario Básico',
                'email': 'basico@empresa.com'
            }
        ]
        
        for user_data in usuarios:
            # Verificar si el usuario ya existe
            usuario_existente = Usuario.query.filter_by(username=user_data['username']).first()
            if not usuario_existente:
                usuario = Usuario(
                    username=user_data['username'],
                    rol=user_data['rol'],
                    nombre=user_data['nombre'],
                    email=user_data['email']
                )
                usuario.set_password(user_data['password'])
                db.session.add(usuario)
                print(f"✅ Usuario {user_data['username']} creado")
            else:
                print(f"ℹ️  Usuario {user_data['username']} ya existe")
        
        db.session.commit()
        print("\n🎉 Todos los usuarios creados!")
        print("\n📋 Credenciales disponibles:")
        for user in usuarios:
            print(f"   👤 {user['username']} / {user['password']} → {user['rol']}")

if __name__ == '__main__':
    create_all_users()
