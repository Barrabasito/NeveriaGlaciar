from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Usuario, Sucursal, Empleado
from app import db, bcrypt
from auth import tokenCheck, verificar
from config import BaseConfig

applogin = Blueprint("applogin", __name__, template_folder="templates")


@applogin.route("/")
@applogin.route("/main", methods=["GET"])
def main():
    return render_template("/main.html")


@applogin.route("/login", methods=["GET", "POST"])
def login_post():
    if request.method == "GET":
        token = request.args.get("token")
        if token:
            info = verificar(token)
            if info["status"] != "fail":
                responseObject = {
                    "status": "success",
                    "message": "valid_token",
                    "info": info,
                }
                return jsonify(responseObject)
        return render_template("/login.html")
    else:
        nombre_usuario = request.json["email"]
        password = request.json["password"]
        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            password=password,
            admin=True,
            # sucursal_id=None,
        )
        searchUser = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if searchUser:
            validation = bcrypt.check_password_hash(searchUser.password, password)
            if validation:
                auth_token = usuario.encode_auth_token(usuario_id=searchUser.id_usuario)
                usuario_data = {
                    "id_usuario": searchUser.id_usuario,
                    "nombre_usuario": searchUser.nombre_usuario,
                    "password": searchUser.password,
                    "fecha_registro": searchUser.fecha_registro.strftime(
                        "%Y-%m-%d"
                    ),  # Formatear la fecha como string
                    "admin": searchUser.admin,
                    # "sucursal_id": searchUser.sucursal_id,
                }

                empleado = Empleado.query.filter_by(
                    usuario_id=searchUser.id_usuario
                ).first()

                if empleado is not None:
                    empleado_data = {
                        "clave": empleado.clave,
                        "nombres": empleado.nombres,
                        "apellidos": empleado.apellidos,
                        "sucursal_id": empleado.sucursal_id,
                    }
                    sucursal = Sucursal.query.filter_by(
                        id_sucursal=empleado.sucursal_id
                    ).first()
                    sucursal_data = {
                        "id_sucursal": sucursal.id_sucursal,
                        "nombre": sucursal.nombre,
                    }
                else:
                    empleado_data = {
                        "clave": None,
                        "nombres": None,
                        "apellidos": None,
                        "sucursal_id": None,
                    }
                    sucursal_data = {"id_sucursal": None, "nombre": None}

                response = {
                    "status": "success",
                    "message": "Login exitoso",
                    "auth_token": auth_token,
                    "usuario": usuario_data,
                    "empleado": empleado_data,
                    "sucursal": sucursal_data,
                }
                # print(response)
                return jsonify(response)
        return jsonify({"message": "Datos incorrectos"})


@applogin.route("/verificarRol")
def verificarRol():
    if request.method == "GET":
        token = request.args.get("token")
        print(token)
        if token:
            info = verificar(token)
            print(info["data"]["admin"])
            if info["data"]["admin"] == True:
                responseObject = {"message": "esAdmin"}
                return jsonify(responseObject)
            else:
                responseObject = {"message": "noEsAdmin"}
                return jsonify(responseObject)
        return render_template("sinPermisos.html")
    return jsonify({"message": "Datos incorrectos"})


@applogin.route("/sinPermisos")
def sinPermisos():
    return render_template("sinPermisos.html")


@applogin.route("/agregarUsuarioExterno", methods=["GET", "POST"])
def agregar_usuario_externo():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        return render_template("agregarUsuarioExterno.html", sucursales=sucursales)
    else:
        nombre_usuario = request.json["nombre_usuario"]
        password = request.json["password"]
        admin = request.json.get(
            "admin", False
        )  # Puedes establecer un valor predeterminado si no se proporciona
        # sucursal_id = request.json.get(
        #   "sucursal_id", None
        # )  # Puedes establecer None si no se proporciona

        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            password=password,
            admin=admin,
            # sucursal_id=sucursal_id,
        )

        user_exists = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if not user_exists:
            try:
                db.session.add(usuario)
                db.session.commit()
                responseObject = {"status": "success", "message": "Registro Exitoso"}
            except Exception as e:
                db.session.rollback()
                responseObject = {"status": "error", "message": str(e)}
            finally:
                db.session.close()
        else:
            responseObject = {"status": "error", "message": "Ya existe el usuario"}

        return jsonify(responseObject)


@applogin.route("/<path:undefined_path>")
def undefined_path(**kwargs):
    # Puedes redirigir a la página de error directamente aquí si lo prefieres
    return render_template("404.html"), 404
