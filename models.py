import jwt 
import datetime
from config import BaseConfig
from app import db, bcrypt

class Sucursal(db.Model):
    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(60), nullable=False)
    telefonos = db.relationship('Telefono', backref='sucursal', lazy=True)
    #usuarios = db.relationship('Usuario', backref='sucursal', lazy=True, cascade='save-update, merge, refresh-expire')
    productos = db.relationship('Producto', backref='sucursal', lazy=True)
    empleados = db.relationship('Empleado', backref='sucursal', lazy=True)
    clientes = db.relationship('Cliente', backref='sucursal', lazy=True)
    ventas = db.relationship('Venta', backref='sucursal', lazy=True)
    materias_primas = db.relationship('Materia_Prima', backref='Sucursal', lazy=True)
    encargos = db.relationship('Encargo', backref='sucursal', lazy=True)

class Telefono(db.Model):
    id_telefono = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(15), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'), nullable=False)

class Usuario(db.Model):
    #__tablename__ = "usuarios"
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    #sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'), nullable=True)
    empleado = db.relationship('Empleado', backref='usuario', uselist=False, cascade='save-update, merge, refresh-expire')

    def __init__(self, nombre_usuario, password, admin) -> None:
        self.nombre_usuario = nombre_usuario
        self.password = bcrypt.generate_password_hash(
            password, BaseConfig.BCRYPT_LOG_ROUNDS
        ).decode()

        self.fecha_registro = datetime.datetime.now()
        self.admin = admin
        #self.sucursal_id=sucursal_id

    def encode_auth_token(self, usuario_id):  # Encriptador de usuarios
        try:
            payload = {
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(
                    minutes=2
                ),  # Sirve para especificar la cantidad de tiempo que servira el token
                "iat": datetime.datetime.utcnow(),
                "sub": usuario_id,
            }
            return jwt.encode(payload, BaseConfig.SECRET_KEY, algorithm="HS256")
        except Exception as e:
            print("Error")
            print(e)
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token,BaseConfig.SECRET_KEY,algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError as e:
            return 'Signature Expired Please log in again'

        except jwt.InvalidTokenError as e:
            return 'Invalid token'

class Empleado(db.Model):
    clave = db.Column(db.String(10), primary_key=True)
    RFC = db.Column(db.String(10), nullable=False)
    nombres = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    sueldo = db.Column(db.Float, nullable=False)
    area_laboral = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), unique=True, nullable=True)
    ventas = db.relationship('Venta', backref='empleado', lazy=True)
    imagen = db.relationship('ImagenEmpleado', backref='empleado', lazy=True)
    # Relación con la sucursal
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'), nullable=False)

class Categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre_categoria = db.Column(db.String(30), nullable=False)
    categoria = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    codigo_producto = db.Column(db.String(10), primary_key=True)
    sabor = db.Column(db.String(30), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    imagen = db.relationship('ImagenProducto', backref='producto', lazy=True)
    # Relación con la categoría
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'), nullable=False)
    # Relación con la sucursal
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'), nullable=False)

class Cliente(db.Model):
    nombre_empresa = db.Column(db.String(50), primary_key=True)
    direccion = db.Column(db.String(50), nullable=False)
    codigo_producto = db.Column(db.String(10))
    cantidad_pedida = db.Column(db.Integer)
    costo_total = db.Column(db.Float)
    forma_pago = db.Column(db.String(30))
    fecha_registro = db.Column(db.Date)
    # Relación con Sucursal
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'))
    
class Venta(db.Model):
    id_venta = db.Column(db.Integer, primary_key=True)
    fecha_venta = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    forma_pago = db.Column(db.String(30))
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'), nullable=False)
    clave = db.Column(db.String(10), db.ForeignKey('empleado.clave'), nullable=False)
    # Relación con Producto_Vendido
    productos_vendidos = db.relationship('Producto_Vendido', backref='venta', lazy=True)
    
class Producto_Vendido(db.Model):
    __tablename__ = "producto_vendido"
    id_producto_vendido = db.Column(db.Integer, primary_key=True)
    codigo_producto = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id_venta'), nullable=False)
                         
class Materia_Prima(db.Model):
    __tablename__ = "materia_prima"
    codigo_materia = db.Column(db.String(10), primary_key=True)
    nombre_materia = db.Column(db.String(30), nullable=False)
    precio = db.Column(db.Float, nullable=False) 
    cantidad = db.Column(db.Integer, nullable=False) 
    encargos = db.relationship('Encargo', backref='materia_prima', lazy=True)
    imagen = db.relationship('ImagenMateriaPrima', backref='materia_prima', lazy=True)
    # Relación con Sucursal
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'), nullable=False)
    
class Proveedor(db.Model):
    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(50))
    telefono = db.Column(db.String(10))
    # Relación con Encargo
    encargos = db.relationship('Encargo', backref='proveedor', lazy=True)

class Encargo(db.Model):
    id_encargo = db.Column(db.Integer, primary_key=True)
    codigo_materia = db.Column(db.String(10), db.ForeignKey('materia_prima.codigo_materia'), nullable=False)
    cantidad_encargo = db.Column(db.Integer, nullable=False)
    cantidad_a_pagar = db.Column(db.Float, nullable=False)
    forma_pago = db.Column(db.String(30))
    fecha_encargo = db.Column(db.Date, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id_proveedor'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id_sucursal'), nullable=False)

class ImagenEmpleado(db.Model):
    id_imagenEmpleado = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    rendered_data = db.Column(db.Text, nullable=False)
    clave = db.Column(db.String(10), db.ForeignKey("empleado.clave"), nullable=False)
    
class ImagenProducto(db.Model):
    id_images = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    rendered_data = db.Column(db.Text, nullable=False)
    codigo_producto = db.Column(db.String(10), db.ForeignKey("producto.codigo_producto"), nullable=False)
    
class ImagenMateriaPrima(db.Model):
    id_images = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    rendered_data = db.Column(db.Text, nullable=False)
    codigo_materia = db.Column(db.String(10), db.ForeignKey("materia_prima.codigo_materia"), nullable=False)

