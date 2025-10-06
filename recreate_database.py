# recreate_database.py
from app import app, db
from models import Insumo, Usuario, Compra, Consumo
from datetime import datetime

def recreate_database():
    print("🗃️ Recreando base de datos desde cero...")
    
    with app.app_context():
        # 1. Eliminar todas las tablas existentes
        print("🧹 Limpiando base de datos...")
        db.drop_all()
        
        # 2. Crear todas las tablas con el nuevo esquema
        print("📦 Creando tablas...")
        db.create_all()
        
        # 3. Crear usuario admin por defecto
        print("👤 Creando usuario admin...")
        admin = Usuario(
            username="admin",
            rol="admin", 
            nombre="Administrador",
            email="admin@empresa.com"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        # 4. Crear algunos insumos de ejemplo con stock_minimo
        print("📦 Creando insumos de ejemplo...")
        insumos_ejemplo = [
            Insumo(
                denominacion="superassilex",
                tipo="peach", 
                modelo="k1500",
                cantidad_por_caja=25,
                precio_caja=129500.0,
                precio_unitario=5180.0,
                codigo_barras="49344446551139",
                stock_minimo=10.0  # ← NUEVO CAMPO
            ),
            Insumo(
                denominacion="super tack", 
                tipo="max film",
                modelo="p600",
                cantidad_por_caja=50,
                precio_caja=231600.0,
                precio_unitario=4632.0,
                codigo_barras="49344446356185", 
                stock_minimo=20.0  # ← NUEVO CAMPO
            ),
            Insumo(
                denominacion="super tack",
                tipo="pommax",
                modelo="p80", 
                cantidad_por_caja=50,
                precio_caja=219700.0,
                precio_unitario=4394.0,
                codigo_barras="4934446454294",
                stock_minimo=0.0  # ← NUEVO CAMPO (sin alerta)
            )
        ]
        
        for insumo in insumos_ejemplo:
            db.session.add(insumo)
        
        # 5. Guardar todos los cambios
        db.session.commit()
        
        print("✅ Base de datos recreada exitosamente!")
        print("📊 Datos creados:")
        print("   - 1 usuario admin (admin/admin123)")
        print("   - 3 insumos de ejemplo con stock_minimo")
        print("   - Esquema actualizado con alertas de stock")

if __name__ == '__main__':
    recreate_database()
