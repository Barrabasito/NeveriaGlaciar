from flask import Flask
from flask_cors import CORS
from database import db
from encriptador import bcrypt
from flask_migrate import Migrate
from config import BaseConfig

from routes.usuario.usuario import appusuario
from routes.sucursal.sucursal import appsucursal
from routes.producto.producto import appproducto
from routes.categoria.categoria import appcategoria
from routes.empleado.empleado import appempleado
from routes.cliente.cliente import appcliente
from routes.encargo.encargo import appencargo
from routes.proveedor.proveedor import appproveedor
from routes.materia_prima.materia_prima import appmateria
from routes.venta.venta import appventa

from routes.imagen.imagen import ImagenEmpleadoUser
from routes.pdf.pdf import apppdf
from routes.csv.indexCsv import appcsv

app = Flask(__name__)
app.register_blueprint(appusuario)
app.register_blueprint(appsucursal)
app.register_blueprint(appproducto)
app.register_blueprint(appcategoria)
app.register_blueprint(appempleado)
app.register_blueprint(appcliente)
app.register_blueprint(appencargo)
app.register_blueprint(appproveedor)
app.register_blueprint(appmateria)
app.register_blueprint(appventa)


app.register_blueprint(ImagenEmpleadoUser)
app.register_blueprint(apppdf)
app.register_blueprint(appcsv)
app.config.from_object(BaseConfig)
CORS(app)  # Quita el error de cors
bcrypt.init_app(app)
db.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)
