from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Usuario, Sucursal
from app import db, bcrypt
from auth import tokenCheck, verificar
from config import BaseConfig

appusuario = Blueprint("appusuario", __name__, template_folder="templates")


@appusuario.route("/usuarios", methods=["GET"])
@tokenCheck
def getUsers(usuario):
    print(usuario)
    if usuario["admin"]:
        output = []
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            usuarioData = {}
            usuarioData["id_usuario"] = usuario.id_usuario
            usuarioData["nombre_usuario"] = usuario.nombre_usuario
            usuarioData["password"] = usuario.password
            usuarioData["fecha_registro"] = usuario.fecha_registro
            output.append(usuarioData)
        return jsonify({"usuarios": output})
    else:
        print("no tienes permisos")


@appusuario.route("/inicio")
def Inicio():
    return render_template("inicio.html")


@appusuario.route("/indexUsuario")
def indexUsuario():
    return render_template("indexUsuario.html")

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
                response = {
                    "status": "success",
                    "message": "Login exitoso",
                    "auth_token": auth_token,
                }
                return jsonify(response)
        return jsonify({"message": "Datos incorrectos"})


@appusuario.route("/agregarUsuario", methods=["GET", "POST"])
def agregar_usuario():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        return render_template("agregarUsuario.html", sucursales=sucursales)
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


@appusuario.route("/listaUsuarios")
def consulta_usuarios():
    usuarios = Usuario.query.all()
    usuarios_data = [
        {
            "id_usuario": usuario.id_usuario,
            "nombre_usuario": usuario.nombre_usuario,
            "password": usuario.password,
            "fecha_registro": usuario.fecha_registro.isoformat(),
            "admin": usuario.admin,
            "sucursal_id": usuario.sucursal_id,
        }
        for usuario in usuarios
    ]
    return jsonify({"usuarios": usuarios_data})


@appusuario.route("/detalleUsuario/<int:id_usuario>")
def ver_usuario(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)

    usuario_data = {
        "id_usuario": usuario.id_usuario,
        "nombre_usuario": usuario.nombre_usuario,
        "password": usuario.password,
        "fecha_registro": usuario.fecha_registro.strftime(
            "%Y-%m-%d"
        ),  # Formatear la fecha como string
        "admin": usuario.admin,
        "sucursal_id": usuario.sucursal_id,
    }

    return render_template("detalleUsuario.html", usuario=usuario_data)


@appusuario.route("/editarUsuario/<int:id_usuario>", methods=["GET", "POST"])
def editar_usuario(id_usuario):
    try:
        usuario = Usuario.query.get_or_404(id_usuario)

        if request.method == "GET":
            # También obtenemos información sobre sucursales u otras variables que puedan ser necesarias
            sucursales = Sucursal.query.all()
            isAdmin = usuario.admin
            if isAdmin:
                isAdmin = 1
            else:
                isAdmin = 0
            print(isAdmin)
            return render_template(
                "editarUsuario.html",
                usuario=usuario,
                isAdmin=isAdmin,
                sucursales=sucursales,
            )

        else:
            nombre_usuario = request.json.get("nombre_usuario")
            password = request.json.get("password")
            admin = request.json.get("admin")
            sucursal_id = request.json.get("sucursal_id")

            # Verificar si el nuevo nombre de usuario ya existe
            existing_user = Usuario.query.filter(
                Usuario.nombre_usuario == nombre_usuario,
                Usuario.id_usuario != id_usuario,
            ).first()
            if existing_user:
                responseObject = {
                    "status": "error",
                    "message": "El nombre de usuario ya está en uso",
                }
                return jsonify(responseObject)

            usuario.nombre_usuario = nombre_usuario
            usuario.password = bcrypt.generate_password_hash(
                password, BaseConfig.BCRYPT_LOG_ROUNDS
            ).decode()
            usuario.admin = admin
            usuario.sucursal_id = sucursal_id

            db.session.commit()
            responseObject = {
                "status": "success",
                "message": "Usuario editado correctamente",
                "id_usuario": usuario.id_usuario,
            }
            return jsonify(responseObject)

    except IntegrityError as e:
        db.session.rollback()
        responseObject = {
            "status": "error",
            "message": "Error de integridad en la base de datos",
        }
        return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()


@appusuario.route("/eliminarUsuario/<int:id_usuario>", methods=["DELETE"])
def eliminar_categoria(id_usuario):
    try:
        Usuarios = Usuario.query.get_or_404(id_usuario)

        # Eliminar la categoría
        db.session.delete(Usuarios)
        db.session.commit()

        responseObject = {
            "status": "success",
            "message": "Categoría eliminada correctamente",
        }
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)
