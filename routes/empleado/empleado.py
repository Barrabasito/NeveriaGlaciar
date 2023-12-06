from flask import Blueprint, request, jsonify, render_template, redirect, Response
from sqlalchemy import exc
from models import Empleado, Sucursal, Usuario, ImagenEmpleado
from app import db, bcrypt
from auth import tokenCheck, verificar
import base64

appempleado = Blueprint("appempleado", __name__, template_folder="templates")


def render_image(data):
    render_img = base64.b64encode(data).decode("ascii")
    return render_img


@appempleado.route("/indexEmpleado")
def indexEmpleado():
    return render_template("indexEmpleado.html")


@appempleado.route("/agregarEmpleado", methods=["GET", "POST"])
def agregar_empleado():
    if request.method == "GET":
        sucursales = Sucursal.query.all()

        usuarios_disponibles = Usuario.query.filter(Usuario.empleado == None).all()
        
        total_empleados = Empleado.query.filter(Empleado.clave.isnot(None)).count()

        siguiente_numero = total_empleados + 1
        # Formatea el número para que tenga 4 dígitos (rellenando con ceros a la izquierda)
        numero_formateado = f'{siguiente_numero:04}'
        nueva_clave = 'EMPNVG' + numero_formateado
        
        return render_template(
            "agregarEmpleado.html",
            sucursales=sucursales,
            usuarios_disponibles=usuarios_disponibles,
            nueva_clave=nueva_clave
        )
    else:
        try:
            # Obtener datos del formulario y cargar en JSON
            datos_empleado = {
                "clave": request.form["clave"],
                "RFC": request.form["RFC"],
                "nombres": request.form["nombres"],
                "apellidos": request.form["apellidos"],
                "fecha_nacimiento": request.form["fecha_nacimiento"],
                "edad": int(request.form["edad"]),
                "sueldo": float(request.form["sueldo"]),
                "area_laboral": request.form["area_laboral"],
                "email": request.form["email"],
                "usuario_id": int(request.form["usuario_id"]),
                "sucursal_id": int(request.form["sucursal_id"]),
            }

            # Verificar si la sucursal existe
            sucursal = Sucursal.query.get(datos_empleado["sucursal_id"])
            if not sucursal:
                return jsonify({"status": "error", "message": "La sucursal no existe"})

            # Crear una instancia de Empleado y asignar los valores
            empleado = Empleado(**datos_empleado)

            db.session.add(empleado)
            db.session.commit()

            # Manejar la carga de imágenes
            file = request.files["inputFile"]
            data = file.read()
            render_file = render_image(data)
            imagen_empleado = ImagenEmpleado(
                type="Empleado",
                rendered_data=render_file,
                data=data,
                clave=datos_empleado["clave"],
            )
            db.session.add(imagen_empleado)
            db.session.commit()

            responseObject = {
                "status": "success",
                "message": "Empleado y imagen agregados correctamente",
            }
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)


@appempleado.route("/listaEmpleados")
def consulta_empleados():
    empleados = Empleado.query.all()
    usuarios_disponibles = Usuario.query.filter(Usuario.empleado == None).all()
    cantidad_usuarios_disponibles = len(usuarios_disponibles)
    
    sucursales_disponibles = Sucursal.query.all()
    cantidad_sucursales_disponibles = len(sucursales_disponibles)
    
    print(cantidad_usuarios_disponibles)
    empleados_data = [
        {
            "clave": empleado.clave,
            "RFC": empleado.RFC,
            "nombres": empleado.nombres,
            "apellidos": empleado.apellidos,
            "fecha_nacimiento": empleado.fecha_nacimiento.strftime("%Y-%m-%d"),
            "edad": empleado.edad,
            "sueldo": empleado.sueldo,
            "area_laboral": empleado.area_laboral,
            "email": empleado.email,
            "usuario_id": empleado.usuario_id,
            "sucursal_id": empleado.sucursal_id,
        }
        for empleado in empleados
    ]
    return jsonify({
        "empleados": empleados_data,
        "usuarios_disponibles":cantidad_usuarios_disponibles,
        "sucursales_disponibles":cantidad_sucursales_disponibles
        })


@appempleado.route("/detalleEmpleado/<string:clave>")
def ver_empleado(clave):
    empleado = Empleado.query.filter_by(clave=clave).first_or_404()

    # Obtener imágenes asociadas al empleado (ajusta según la lógica de tu aplicación)
    imagenes = ImagenEmpleado.query.filter_by(clave=empleado.clave).first()
    images = imagenes.rendered_data if imagenes else None

    empleado_data = {
        "clave": empleado.clave,
        "RFC": empleado.RFC,
        "nombres": empleado.nombres,
        "apellidos": empleado.apellidos,
        "fecha_nacimiento": empleado.fecha_nacimiento,
        "edad": empleado.edad,
        "sueldo": empleado.sueldo,
        "area_laboral": empleado.area_laboral,
        "email": empleado.email,
        "usuario_id": empleado.usuario_id,
        "sucursal_id": empleado.sucursal_id,
    }

    return render_template(
        "detalleEmpleado.html", empleado=empleado_data, imagenes=images
    )


@appempleado.route("/editarEmpleado/<string:clave>", methods=["GET", "POST"])
def editar_empleado(clave):
    try:
        empleado = Empleado.query.filter_by(clave=clave).first_or_404()

        if request.method == "GET":
            sucursales = Sucursal.query.all()
            usuarios_disponibles = Usuario.query.filter(Usuario.empleado == None).all()
            usuario_actual = Usuario.query.get(empleado.usuario_id)

            usuarios_disponibles.append(usuario_actual)

            return render_template(
                "editarEmpleado.html",
                empleado=empleado,
                sucursales=sucursales,
                usuarios_disponibles=usuarios_disponibles,
                usuario_actual=usuario_actual,
            )
        else:
            clave = request.json.get("clave")
            rfc = request.json.get("RFC")
            nombres = request.json.get("nombres")
            apellidos = request.json.get("apellidos")
            fecha_nacimiento = request.json.get("fecha_nacimiento")
            edad = request.json.get("edad")
            sueldo = request.json.get("sueldo")
            area_laboral = request.json.get("area_laboral")
            email = request.json.get("email")
            usuario_id = request.json.get("usuario_id")
            sucursal_id = request.json.get("sucursal_id")

            empleado.clave = clave
            empleado.RFC = rfc
            empleado.nombres = nombres
            empleado.apellidos = apellidos
            empleado.fecha_nacimiento = fecha_nacimiento
            empleado.edad = edad
            empleado.sueldo = sueldo
            empleado.area_laboral = area_laboral
            empleado.email = email
            empleado.usuario_id = usuario_id
            empleado.sucursal_id = sucursal_id

            db.session.commit()

            responseObject = {
                "status": "success",
                "message": "Empleado editado correctamente",
                "clave": empleado.clave,
            }
            return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()


@appempleado.route("/eliminarEmpleado/<string:clave>", methods=["DELETE"])
def eliminar_empleado(clave):
    try:
        empleado = Empleado.query.get_or_404(clave)
        imagen = ImagenEmpleado.query.filter_by(clave=empleado.clave).first()
        # Eliminar el empleado
        if imagen:
            db.session.delete(imagen)
        db.session.delete(empleado)
        db.session.commit()

        responseObject = {
            "status": "success",
            "message": "Empleado eliminado correctamente",
        }
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)


@appempleado.route("/modificarImagenEmpleado/<string:clave>", methods=["POST"])
def modificarImagen(clave):
    searchImage = ImagenEmpleado.query.filter_by(clave=clave).first()
    if searchImage:
        file = request.files["inputFile"]
        data = file.read()
        render_file = render_image(data)
        searchImage.rendered_data = render_file
        searchImage.data = data
        db.session.commit()
        return jsonify({"Message": "Imagen Actualizada"})
    else:
        file = request.files["inputFile"]
        data = file.read()
        render_file = render_image(data)
        newFile = ImagenEmpleado()
        newFile.type = "Producto"
        newFile.rendered_data = render_file
        newFile.data = data
        newFile.clave = clave
        db.session.add(newFile)
        db.session.commit()
        return jsonify({"Message": "Imagen agregada"})
