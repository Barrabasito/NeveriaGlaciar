from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Usuario, Sucursal, Empleado
from app import db, bcrypt
from auth import tokenCheck, verificar
from config import BaseConfig

applogin = Blueprint("applogin", __name__, template_folder="templates")


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
            sucursal_id=None,
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
                    "sucursal_id": searchUser.sucursal_id,
                }

                response = {
                    "status": "success",
                    "message": "Login exitoso",
                    "auth_token": auth_token,
                    "usuario": usuario_data,
                }
                print(response)
                return jsonify(response)
        return jsonify({"message": "Datos incorrectos"})


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
        sucursal_id = request.json.get(
            "sucursal_id", None
        )  # Puedes establecer None si no se proporciona

        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            password=password,
            admin=admin,
            sucursal_id=sucursal_id,
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
