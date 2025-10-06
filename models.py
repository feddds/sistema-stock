from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'basico', 'stock', 'compras', 'admin'
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.username} - {self.rol}>'

class Insumo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Campos del Excel
    denominacion = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    cantidad_por_caja = db.Column(db.Integer, nullable=False)
    precio_caja = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    codigo_barras = db.Column(db.String(50), unique=True)
    
    # NUEVO: Stock mínimo para alertas
    stock_minimo = db.Column(db.Float, default=0.0)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    compras = db.relationship('Compra', backref='insumo', lazy=True, cascade='all, delete-orphan')
    consumos = db.relationship('Consumo', backref='insumo', lazy=True, cascade='all, delete-orphan')
    
    # Propiedades calculadas
    @property
    def stock_actual(self):
        """Calcula el stock actual en unidades"""
        total_compras = sum(compra.cantidad_unidades for compra in self.compras)
        total_consumos = sum(consumo.cantidad_unidades for consumo in self.consumos)
        return total_compras - total_consumos
    
    @property
    def stock_en_cajas(self):
        """Calcula cuántas cajas completas hay"""
        return self.stock_actual // self.cantidad_por_caja if self.cantidad_por_caja > 0 else 0
    
    @property
    def unidades_sueltas(self):
        """Calcula las unidades sueltas (resto)"""
        return self.stock_actual % self.cantidad_por_caja if self.cantidad_por_caja > 0 else 0
    
    @property
    def valor_stock_actual(self):
        """Calcula el valor total del stock actual"""
        return self.stock_actual * self.precio_unitario
    
# NUEVA: Propiedad para alertas
    @property
    def necesita_reposicion(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo

    @property
    def porcentaje_stock(self):
        """Calcula el porcentaje de stock restante (si stock_minimo > 0)"""
        if self.stock_minimo > 0 and self.stock_actual > 0:
            return (self.stock_actual / self.stock_minimo) * 100
        return 0
        

    def __repr__(self):
        return f'<Insumo {self.denominacion} - {self.tipo} ({self.modelo})>'


class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con insumo
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumo.id'), nullable=False)
    
    # Datos de la compra
    cantidad_cajas = db.Column(db.Float, nullable=False)
    precio_caja_compra = db.Column(db.Float, nullable=False)
    proveedor = db.Column(db.String(100))
    lote = db.Column(db.String(50))
    fecha_vencimiento = db.Column(db.Date)
    
    # Metadata
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Propiedades calculadas
    @property
    def cantidad_unidades(self):
        """Calcula la cantidad total de unidades compradas"""
        if self.insumo and self.insumo.cantidad_por_caja:
            return self.cantidad_cajas * self.insumo.cantidad_por_caja
        return 0
    
    @property
    def costo_total(self):
        """Calcula el costo total de la compra"""
        return self.cantidad_cajas * self.precio_caja_compra
    
    @property
    def precio_unitario_compra(self):
        """Calcula el precio unitario al momento de la compra"""
        if self.cantidad_unidades > 0:
            return self.costo_total / self.cantidad_unidades
        return 0
    
    def __repr__(self):
        return f'<Compra {self.insumo.denominacion} - {self.cantidad_cajas} cajas>'


class Consumo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con insumo
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumo.id'), nullable=False)
    
    # Datos del consumo
    cantidad_unidades = db.Column(db.Float, nullable=False)
    proyecto = db.Column(db.String(100))
    observaciones = db.Column(db.String(200))
    responsable = db.Column(db.String(100), nullable=False)
    
    # Metadata
    fecha_consumo = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Propiedades calculadas
    @property
    def costo_consumo(self):
        """Calcula el costo del consumo basado en el precio unitario del insumo"""
        if self.insumo:
            return self.cantidad_unidades * self.insumo.precio_unitario
        return 0
    
    @property
    def cantidad_cajas_equivalentes(self):
        """Calcula a cuántas cajas equivale el consumo"""
        if self.insumo and self.insumo.cantidad_por_caja > 0:
            return self.cantidad_unidades / self.insumo.cantidad_por_caja
        return 0
    
    def __repr__(self):
        return f'<Consumo {self.insumo.denominacion} - {self.cantidad_unidades} unidades>'