# check_database.py
import sqlite3
from app import app

def check_database():
    # Conectar directamente a SQLite
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    
    # Verificar la estructura de la tabla insumo
    cursor.execute("PRAGMA table_info(insumo)")
    columns = cursor.fetchall()
    
    print("📊 COLUMNAS DE LA TABLA INSUMO:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Verificar si stock_minimo existe
    stock_minimo_exists = any('stock_minimo' in col for col in columns)
    print(f"\n✅ stock_minimo existe: {stock_minimo_exists}")
    
    conn.close()

if __name__ == '__main__':
    with app.app_context():
        check_database()
