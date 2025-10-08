# script_carga_centros.py
from datetime import datetime
from models import db, CentroConsumo, Trabajador

def cargar_centros_y_trabajadores():
    """Carga los centros de consumo y trabajadores iniciales"""
    
    # Datos de centros de consumo
    centros_data = [
        {'nombre': 'Preparación', 'descripcion': 'Área de preparación de vehículos'},
        {'nombre': 'Lustrado', 'descripcion': 'Área de lustrado y pulido'},
        {'nombre': 'Cabinas', 'descripcion': 'Cabinas de pintura'},
        {'nombre': 'Terminación', 'descripcion': 'Área de terminación y detalles finales'}
    ]
    
    # Datos de trabajadores por centro
    trabajadores_data = [
        # Preparación
        {'codigo': 'P1', 'nombre': 'Correa Juan', 'centro_nombre': 'Preparación'},
        {'codigo': 'P2', 'nombre': 'Girardello Claudio', 'centro_nombre': 'Preparación'},
        # Lustrado
        {'codigo': 'L1', 'nombre': 'Muñoz Jeremias', 'centro_nombre': 'Lustrado'},
        {'codigo': 'L2', 'nombre': 'Buchin Juan Manuel', 'centro_nombre': 'Lustrado'},
        # Cabinas
        {'codigo': 'C1', 'nombre': 'Muñoz Maximiliano', 'centro_nombre': 'Cabinas'},
        {'codigo': 'C2', 'nombre': 'Llanos Efrain', 'centro_nombre': 'Cabinas'},
        # Terminación
        {'codigo': 'T1', 'nombre': 'Orellano Cristian', 'centro_nombre': 'Terminación'}
    ]
    
    try:
        print("Iniciando carga de centros de consumo y trabajadores...")
        
        # Crear centros de consumo
        centros_dict = {}
        for centro_info in centros_data:
            # Verificar si el centro ya existe
            centro_existente = CentroConsumo.query.filter_by(nombre=centro_info['nombre']).first()
            if not centro_existente:
                centro = CentroConsumo(
                    nombre=centro_info['nombre'],
                    descripcion=centro_info['descripcion'],
                    activo=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(centro)
                db.session.flush()  # Para obtener el ID
                centros_dict[centro_info['nombre']] = centro
                print(f"✅ Centro creado: {centro_info['nombre']}")
            else:
                centros_dict[centro_info['nombre']] = centro_existente
                print(f"⚠️ Centro ya existe: {centro_info['nombre']}")
        
        # Crear trabajadores
        for trabajador_info in trabajadores_data:
            # Verificar si el trabajador ya existe por código
            trabajador_existente = Trabajador.query.filter_by(codigo=trabajador_info['codigo']).first()
            if not trabajador_existente:
                centro = centros_dict.get(trabajador_info['centro_nombre'])
                if centro:
                    trabajador = Trabajador(
                        codigo=trabajador_info['codigo'],
                        nombre=trabajador_info['nombre'],
                        centro_consumo_id=centro.id,
                        activo=True,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(trabajador)
                    print(f"✅ Trabajador creado: {trabajador_info['nombre']} ({trabajador_info['codigo']})")
                else:
                    print(f"❌ Error: No se encontró el centro {trabajador_info['centro_nombre']}")
            else:
                print(f"⚠️ Trabajador ya existe: {trabajador_info['nombre']} ({trabajador_info['codigo']})")
        
        # Confirmar todos los cambios
        db.session.commit()
        print("🎉 Carga completada exitosamente!")
        
        # Mostrar resumen
        print("\n📊 Resumen de carga:")
        print(f"Centros de consumo: {CentroConsumo.query.count()}")
        print(f"Trabajadores: {Trabajador.query.count()}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error durante la carga: {str(e)}")
        return False

def verificar_carga():
    """Verifica que los datos se hayan cargado correctamente"""
    print("\n🔍 Verificando carga de datos...")
    
    centros = CentroConsumo.query.all()
    for centro in centros:
        print(f"\n🏭 Centro: {centro.nombre}")
        trabajadores = Trabajador.query.filter_by(centro_consumo_id=centro.id).all()
        for trab in trabajadores:
            print(f"   👷 Trabajador: {trab.codigo} - {trab.nombre}")

# Para ejecutar el script directamente
if __name__ == '__main__':
    from app import app  # Ajusta según tu estructura
    
    with app.app_context():
        if cargar_centros_y_trabajadores():
            verificar_carga()