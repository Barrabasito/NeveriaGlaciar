from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Empleado,Sucursal,Usuario
from app import db, bcrypt
from auth import tokenCheck, verificar

appempleado = Blueprint("appempleado", __name__, template_folder="templates")

@appempleado.route("/indexEmpleado")
def indexEmpleado():
    return render_template("indexEmpleado.html")


@appempleado.route("/agregarEmpleado", methods=["GET", "POST"])
def agregar_empleado():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        usuarios_disponibles = Usuario.query.filter(Usuario.empleado == None).all()
        return render_template("agregarEmpleado.html", sucursales=sucursales, usuarios_disponibles=usuarios_disponibles)
    else:
        # Obtener datos del formulario o solicitud JSON
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

        # Verificar si la sucursal existe
        sucursal = Sucursal.query.get(sucursal_id)
        if not sucursal:
            return jsonify({"status": "error", "message": "La sucursal no existe"})

        # Crear una instancia de Empleado y asignar los valores
        empleado = Empleado(
            clave=clave,
            RFC=rfc,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            edad=edad,
            sueldo=sueldo,
            area_laboral=area_laboral,
            email=email,
            usuario_id=usuario_id,
            sucursal_id=sucursal_id
        )

        try:
            db.session.add(empleado)
            db.session.commit()
            responseObject = {"status": "success", "message": "Empleado agregado correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)


@appempleado.route("/listaEmpleados")
def consulta_empleados():
    empleados = Empleado.query.all()
    empleados_data = [
        {
            'clave': empleado.clave,
            'RFC': empleado.RFC,
            'nombres': empleado.nombres,
            'apellidos': empleado.apellidos,
            'fecha_nacimiento': empleado.fecha_nacimiento.strftime('%Y-%m-%d'),
            'edad': empleado.edad,
            'sueldo': empleado.sueldo,
            'area_laboral': empleado.area_laboral,
            'email': empleado.email,
            'usuario_id': empleado.usuario_id,
            'sucursal_id': empleado.sucursal_id
        } for empleado in empleados
    ]
    return jsonify({'empleados': empleados_data})



@appempleado.route("/detalleEmpleado/<string:clave>")
def ver_empleado(clave):
    empleado = Empleado.query.filter_by(clave=clave).first_or_404()

    empleado_data = {
        'clave': empleado.clave,
        'RFC': empleado.RFC,
        'nombres': empleado.nombres,
        'apellidos': empleado.apellidos,
        'fecha_nacimiento': empleado.fecha_nacimiento,
        'edad': empleado.edad,
        'sueldo': empleado.sueldo,
        'area_laboral': empleado.area_laboral,
        'email': empleado.email,
        'usuario_id': empleado.usuario_id,
        'sucursal_id': empleado.sucursal_id
    }

    return render_template("detalleEmpleado.html", empleado=empleado_data)



@appempleado.route("/editarEmpleado/<string:clave>", methods=["GET", "POST"])
def editar_empleado(clave):
    try:
        empleado = Empleado.query.filter_by(clave=clave).first_or_404()

        if request.method == "GET":
            sucursales = Sucursal.query.all()
            usuarios_disponibles = Usuario.query.filter(Usuario.empleado == None).all()
            usuario_actual = Usuario.query.get(empleado.usuario_id)

            usuarios_disponibles.append(usuario_actual)
            
            return render_template("editarEmpleado.html", empleado=empleado, sucursales=sucursales, usuarios_disponibles=usuarios_disponibles, usuario_actual=usuario_actual)
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

            responseObject = {"status": "success", "message": "Empleado editado correctamente", "clave": empleado.clave}
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

        # Eliminar el empleado
        db.session.delete(empleado)
        db.session.commit()

        responseObject = {"status": "success", "message": "Empleado eliminado correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)