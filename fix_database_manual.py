# fix_database_manual.py
import sqlite3
from app import app, db
from models import Insumo

def fix_database():
    print("🔧 Iniciando reparación de base de datos...")
    
    # Conectar directamente a SQLite
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    
    try:
        # 1. Agregar columna stock_minimo
        print("📝 Agregando columna stock_minimo...")
        cursor.execute('ALTER TABLE insumo ADD COLUMN stock_minimo FLOAT DEFAULT 0')
        
        # 2. Confirmar cambios
        conn.commit()
        print("✅ Columna stock_minimo agregada exitosamente")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  La columna stock_minimo ya existe")
        else:
            print(f"❌ Error: {e}")
            return
    
    # 3. Verificar la estructura actualizada
    cursor.execute("PRAGMA table_info(insumo)")
    columns = cursor.fetchall()
    
    print("\n📊 ESTRUCTURA ACTUALIZADA:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    
    # 4. Actualizar los modelos en la sesión actual
    with app.app_context():
        try:
            # Forzar recarga de la metadata
            db.metadata.clear()
            db.Model.metadata.reflect(db.engine)
            
            # Verificar que los insumos tengan el nuevo atributo
            insumos = Insumo.query.all()
            for insumo in insumos:
                if not hasattr(insumo, 'stock_minimo') or insumo.stock_minimo is None:
                    insumo.stock_minimo = 0.0
            
            db.session.commit()
            print("✅ Modelos actualizados en la sesión")
            
        except Exception as e:
            print(f"❌ Error actualizando modelos: {e}")
    
    print("\n🎉 Reparación completada!")

if __name__ == '__main__':
    fix_database()
