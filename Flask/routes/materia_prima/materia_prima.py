from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Materia_Prima,Sucursal
from app import db, bcrypt
from auth import tokenCheck, verificar

appmateria = Blueprint("appmateria", __name__, template_folder="templates")

@appmateria.route("/indexMateriaPrima")
def indexMateria():
    return render_template("indexMateriaPrima.html")


@appmateria.route("/agregarMateriaPrima", methods=["GET", "POST"])
def agregar_materia_prima():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        return render_template("agregarMateriaPrima.html", sucursales=sucursales)
    else:
        # Obtener datos del formulario o solicitud JSON
        codigo_materia = request.json.get("codigo_materia")
        nombre_materia = request.json.get("nombre_materia")
        precio = request.json.get("precio")
        cantidad = request.json.get("cantidad")
        sucursal_id = request.json.get("sucursal_id")

        # Verificar si la sucursal existe
        sucursal = Sucursal.query.get(sucursal_id)
        if not sucursal:
            return jsonify({"status": "error", "message": "La sucursal no existe"})

        # Crear una instancia de Materia_Prima y asignar los valores
        materia_prima = Materia_Prima(
            codigo_materia=codigo_materia,
            nombre_materia=nombre_materia,
            precio=precio,
            cantidad=cantidad,
            sucursal_id=sucursal_id
        )

        try:
            db.session.add(materia_prima)
            db.session.commit()
            responseObject = {"status": "success", "message": "Materia prima agregada correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)


@appmateria.route("/listaMateriasPrimas")
def consulta_materias_primas():
    materias_primas = Materia_Prima.query.all()
    materias_primas_data = [
        {
            'codigo_materia': materia_prima.codigo_materia,
            'nombre_materia': materia_prima.nombre_materia,
            'precio': materia_prima.precio,
            'cantidad': materia_prima.cantidad,
            'sucursal_id': materia_prima.sucursal_id
        } for materia_prima in materias_primas
    ]
    return jsonify({'materias_primas': materias_primas_data})


@appmateria.route("/detalleMateriaPrima/<string:codigo_materia>")
def ver_materia_prima(codigo_materia):
    materia_prima = Materia_Prima.query.filter_by(codigo_materia=codigo_materia).first_or_404()

    materia_prima_data = {
        'codigo_materia': materia_prima.codigo_materia,
        'nombre_materia': materia_prima.nombre_materia,
        'precio': materia_prima.precio,
        'cantidad': materia_prima.cantidad,
        'sucursal_id': materia_prima.sucursal_id
    }

    return render_template("detalleMateriaPrima.html", materia_prima=materia_prima_data)


@appmateria.route("/editarMateriaPrima/<string:codigo_materia>", methods=["GET", "POST"])
def editar_materia_prima(codigo_materia):
    try:
        materia_prima = Materia_Prima.query.filter_by(codigo_materia=codigo_materia).first_or_404()

        if request.method == "GET":
            sucursales = Sucursal.query.all()
            
            # Puedes agregar más consultas para obtener datos relacionados si es necesario

            return render_template("editarMateriaPrima.html", materia_prima=materia_prima, sucursales=sucursales)

        else:
            nombre_materia = request.json.get("nombre_materia")
            precio = request.json.get("precio")
            cantidad = request.json.get("cantidad")
            sucursal_id = request.json.get("sucursal_id")

            # Actualizar los atributos de la materia prima
            materia_prima.nombre_materia = nombre_materia
            materia_prima.precio = precio
            materia_prima.cantidad = cantidad
            materia_prima.sucursal_id = sucursal_id

            db.session.commit()
            responseObject = {"status": "success", "message": "Materia prima editada correctamente", "codigo_materia": materia_prima.codigo_materia}
            return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()



@appmateria.route("/eliminarMateriaPrima/<string:codigo_materia>", methods=["DELETE"])
def eliminar_materia_prima(codigo_materia):
    try:
        materia_prima = Materia_Prima.query.get_or_404(codigo_materia)

        # Eliminar la materia prima
        db.session.delete(materia_prima)
        db.session.commit()

        responseObject = {"status": "success", "message": "Materia prima eliminada correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)
