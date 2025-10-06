from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Insumo, Compra, Consumo, Usuario
from datetime import datetime
from functools import wraps
#from flask_migrate import Migrate
import os

app = Flask(__name__)
# POR ESTA (para producción):
if os.environ.get('FLASK_ENV') == 'production':
    # En producción (PythonAnywhere) usa path absoluto
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
else:
    # En desarrollo local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SECRET_KEY'] = 'clave_secreta_stock_app_2024'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

db.init_app(app)

# migrate = Migrate(app, db)

# === DECORADORES DE SEGURIDAD ===
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))
            
            #user = Usuario.query.get(session['user_id'])
            user = db.session.get(Usuario, session['user_id'])
            if user.rol not in roles:
                flash('No tienes permisos para acceder a esta función.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# === RUTAS DE AUTENTICACIÓN ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.query.filter_by(username=username, activo=True).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_rol'] = user.rol
            session['user_nombre'] = user.nombre
            
            flash(f'¡Bienvenido {user.nombre}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required  # ← AGREGAR ESTA LÍNEA
def index():
    return render_template('index.html')

@app.route('/crear-insumo', methods=['GET', 'POST'])
@login_required  # ← AGREGAR ESTA LÍNEA
@role_required(['admin'])  # ← AGREGAR ESTA LÍNEA - Solo admin puede crear insumos
def crear_insumo():
    if request.method == 'POST':
        try:
            nuevo_insumo = Insumo(
                denominacion=request.form['denominacion'],
                tipo=request.form['tipo'],
                modelo=request.form['modelo'],
                cantidad_por_caja=int(request.form['cantidad_por_caja']),
                precio_caja=float(request.form['precio_caja']),
                precio_unitario=float(request.form['precio_unitario']),
                codigo_barras=request.form['codigo_barras'] or None
            )
            
            db.session.add(nuevo_insumo)
            db.session.commit()
            flash('Insumo creado exitosamente!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear insumo: {str(e)}', 'danger')
    
    return render_template('crear_insumo.html')

@app.route('/registrar-compra', methods=['GET', 'POST'])
@login_required  # ← AGREGAR ESTA LÍNEA
@role_required(['compras', 'admin'])  # ← AGREGAR ESTA LÍNEA - Compras y admin
def registrar_compra():
    insumos = Insumo.query.all()
    
    if request.method == 'POST':
        try:
            fecha_vencimiento = request.form['fecha_vencimiento']
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date() if fecha_vencimiento else None
            
            nueva_compra = Compra(
                insumo_id=int(request.form['insumo_id']),
                cantidad_cajas=float(request.form['cantidad_cajas']),
                precio_caja_compra=float(request.form['precio_caja_compra']),
                proveedor=request.form['proveedor'],
                lote=request.form['lote'],
                fecha_vencimiento=fecha_vencimiento
            )
            
            db.session.add(nueva_compra)
            db.session.commit()
            flash('Compra registrada exitosamente!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar compra: {str(e)}', 'danger')
    
    return render_template('registrar_compra.html', insumos=insumos)

@app.route('/registrar-consumo', methods=['GET', 'POST'])
@login_required  # ← AGREGAR ESTA LÍNEA
@role_required(['stock', 'admin'])  # ← AGREGAR ESTA LÍNEA - Stock y admin
def registrar_consumo():
    insumos = Insumo.query.all()
    
    if request.method == 'POST':
        try:
            nuevo_consumo = Consumo(
                insumo_id=int(request.form['insumo_id']),
                cantidad_unidades=float(request.form['cantidad_unidades']),
                proyecto=request.form['proyecto'],
                observaciones=request.form['observaciones'],
                responsable=request.form['responsable']
            )
            
            db.session.add(nuevo_consumo)
            db.session.commit()
            flash('Consumo registrado exitosamente!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar consumo: {str(e)}', 'danger')
    
    return render_template('registrar_consumo.html', insumos=insumos)

@app.route('/reporte-stock')
@login_required  # ← AGREGAR ESTA LÍNEA
@role_required(['basico', 'stock', 'compras', 'admin'])  # ← AGREGAR ESTA LÍNEA - Todos pueden ver
def reporte_stock():
    insumos = Insumo.query.all()
    reporte = []
    
    for insumo in insumos:
        total_unidades_compradas = sum(
            compra.cantidad_cajas * insumo.cantidad_por_caja 
            for compra in insumo.compras
        )
        
        total_unidades_consumidas = sum(
            consumo.cantidad_unidades for consumo in insumo.consumos
        )
        
        stock_actual_unidades = total_unidades_compradas - total_unidades_consumidas
        cajas_completas = stock_actual_unidades // insumo.cantidad_por_caja
        unidades_sueltas = stock_actual_unidades % insumo.cantidad_por_caja
        valor_stock = stock_actual_unidades * insumo.precio_unitario
        
        reporte.append({
            'insumo': insumo,
            'total_unidades_compradas': total_unidades_compradas,
            'total_unidades_consumidas': total_unidades_consumidas,
            'stock_actual_unidades': stock_actual_unidades,
            'cajas_completas': int(cajas_completas),
            'unidades_sueltas': unidades_sueltas,
            'valor_stock': valor_stock
        })
    
    return render_template('reporte_stock.html', reporte=reporte)

# app.py - Agregar estas rutas

@app.route('/gestion_insumos')
def gestion_insumos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Solo admin puede gestionar insumos
    if session.get('user_rol') != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('index'))
    
    insumos = Insumo.query.order_by(Insumo.denominacion, Insumo.tipo).all()
    return render_template('gestion_insumos.html', insumos=insumos)

@app.route('/get_insumo/<int:insumo_id>')
def get_insumo(insumo_id):
    if 'user_id' not in session or session.get('user_rol') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    insumo = Insumo.query.get_or_404(insumo_id)
    return jsonify({
        'id': insumo.id,
        'denominacion': insumo.denominacion,
        'tipo': insumo.tipo,
        'modelo': insumo.modelo,
        'cantidad_por_caja': insumo.cantidad_por_caja,
        'precio_caja': float(insumo.precio_caja),
        'precio_unitario': float(insumo.precio_unitario),
        'codigo_barras': insumo.codigo_barras,
        'stock_minimo': float(insumo.stock_minimo),
        'stock_actual': float(insumo.stock_actual),
        'stock_en_cajas': int(insumo.stock_en_cajas),
        'unidades_sueltas': int(insumo.unidades_sueltas),
        'valor_stock_actual': float(insumo.valor_stock_actual),
        'necesita_reposicion': insumo.necesita_reposicion,
        'porcentaje_stock': float(insumo.porcentaje_stock)
    })

# Actualizar la ruta de edición para manejar stock_minimo
@app.route('/editar_insumo', methods=['POST'])
def editar_insumo():
    if 'user_id' not in session or session.get('user_rol') != 'admin':
        flash('No tienes permisos para esta acción', 'danger')
        return redirect(url_for('index'))
    
    try:
        insumo_id = request.form.get('id')
        insumo = Insumo.query.get_or_404(insumo_id)
        
        # Manejar denominación
        denominacion = request.form.get('denominacion')
        if denominacion == 'otro':
            denominacion = request.form.get('otra_denominacion', '').strip()
        
        # Actualizar datos (incluyendo el nuevo campo)
        insumo.denominacion = denominacion
        insumo.tipo = request.form.get('tipo')
        insumo.modelo = request.form.get('modelo')
        insumo.cantidad_por_caja = int(request.form.get('cantidad_por_caja'))
        insumo.precio_caja = float(request.form.get('precio_caja'))
        insumo.precio_unitario = float(request.form.get('precio_unitario'))
        insumo.codigo_barras = request.form.get('codigo_barras') or None
        insumo.stock_minimo = float(request.form.get('stock_minimo', 0))
        
        db.session.commit()
        flash('✅ Insumo actualizado correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('❌ Error al actualizar el insumo', 'danger')
        print(f"Error: {e}")
    
    return redirect(url_for('gestion_insumos'))

@app.route('/eliminar_insumo/<int:insumo_id>', methods=['POST'])
def eliminar_insumo(insumo_id):
    if 'user_id' not in session or session.get('user_rol') != 'admin':
        return jsonify({'success': False, 'error': 'No autorizado'}), 403
    
    try:
        insumo = Insumo.query.get_or_404(insumo_id)
        
        # Verificar si hay stock antes de eliminar
        if insumo.stock_actual > 0:
            return jsonify({
                'success': False, 
                'error': 'No se puede eliminar un insumo con stock existente'
            })
        
        db.session.delete(insumo)
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/listado-consumos')
@login_required  # ← AGREGAR ESTA LÍNEA
@role_required(['stock', 'admin'])  # ← AGREGAR ESTA LÍNEA - Stock y admin
def listado_consumos():
    # Obtener todos los consumos ordenados por fecha más reciente primero
    consumos = Consumo.query.order_by(Consumo.fecha_consumo.desc()).all()
    return render_template('listado_consumos.html', consumos=consumos)

@app.route('/alertas_stock')
def alertas_stock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener todos los insumos
    insumos = Insumo.query.all()
    
    # Filtrar por diferentes estados
    alertas_criticas = [i for i in insumos if i.stock_minimo > 0 and i.necesita_reposicion]
    insumos_con_alerta = [i for i in insumos if i.stock_minimo > 0]
    insumos_ok = [i for i in insumos_con_alerta if not i.necesita_reposicion]
    insumos_sin_alerta = [i for i in insumos if i.stock_minimo == 0]
    
    return render_template('alertas_stock.html',
                         alertas_criticas=alertas_criticas,
                         insumos_con_alerta=insumos_con_alerta,
                         insumos_ok=insumos_ok,
                         insumos_sin_alerta=insumos_sin_alerta)


@app.route('/listado-compras')
@login_required  # ← AGREGAR ESTA LÍNEA
@role_required(['compras', 'admin'])  # ← AGREGAR ESTA LÍNEA - Compras y admin
def listado_compras():
    # Obtener todas las compras ordenadas por fecha más reciente primero
    compras = Compra.query.order_by(Compra.fecha_compra.desc()).all()
    return render_template('listado_compras.html', compras=compras)

def crear_usuarios_prueba():
    """Crear usuarios de prueba si no existen"""
    with app.app_context():
        if Usuario.query.count() == 0:
            usuarios = [
                {'username': 'admin', 'password': 'admin123', 'rol': 'admin', 'nombre': 'Administrador Principal'},
                {'username': 'compras', 'password': 'compras123', 'rol': 'compras', 'nombre': 'Responsable Compras'},
                {'username': 'stock', 'password': 'stock123', 'rol': 'stock', 'nombre': 'Responsable Stock'},
                {'username': 'basico', 'password': 'basico123', 'rol': 'basico', 'nombre': 'Usuario Básico'}
            ]
            
            for user_data in usuarios:
                usuario = Usuario(
                    username=user_data['username'],
                    rol=user_data['rol'],
                    nombre=user_data['nombre']
                )
                usuario.set_password(user_data['password'])
                db.session.add(usuario)
            
            db.session.commit()
            print("Usuarios de prueba creados exitosamente!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        crear_usuarios_prueba()  # ← Esta línea crea los usuarios automáticamente
    app.run(debug=True)