from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Materia_Prima, Sucursal, ImagenMateriaPrima
from app import db, bcrypt
from auth import tokenCheck, verificar
import base64

appmateria = Blueprint("appmateria", __name__, template_folder="templates")


def render_image(data):
    render_img = base64.b64encode(data).decode("ascii")
    return render_img


@appmateria.route("/indexMateriaPrima")
def indexMateria():
    return render_template("indexMateriaPrima.html")


@appmateria.route("/agregarMateriaPrima", methods=["GET", "POST"])
def agregar_materia_prima():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        return render_template("agregarMateriaPrima.html", sucursales=sucursales)
    else:
        try:
            # Obtener datos del formulario o solicitud JSON
            codigo_materia = request.form["codigo_materia"]
            nombre_materia = request.form["nombre_materia"]
            precio = float(request.form["precio"])
            cantidad = int(request.form["cantidad"])
            sucursal_id = int(request.form["sucursal_id"])

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
                sucursal_id=sucursal_id,
            )

            db.session.add(materia_prima)
            db.session.commit()

            # Manejar la carga de imágenes
            file = request.files["inputFile"]
            data = file.read()
            render_file = render_image(data)
            imagen_materia_prima = ImagenMateriaPrima(
                type="Materia Prima",
                rendered_data=render_file,
                data=data,
                codigo_materia=codigo_materia,
            )
            db.session.add(imagen_materia_prima)
            db.session.commit()

            responseObject = {
                "status": "success",
                "message": "Materia prima y imagen agregadas correctamente",
            }
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
            "codigo_materia": materia_prima.codigo_materia,
            "nombre_materia": materia_prima.nombre_materia,
            "precio": materia_prima.precio,
            "cantidad": materia_prima.cantidad,
            "sucursal_id": materia_prima.sucursal_id,
        }
        for materia_prima in materias_primas
    ]
    return jsonify({"materias_primas": materias_primas_data})


@appmateria.route("/detalleMateriaPrima/<string:codigo_materia>")
def ver_materia_prima(codigo_materia):
    materia_prima = Materia_Prima.query.filter_by(
        codigo_materia=codigo_materia
    ).first_or_404()
    imagen_materia_prima = ImagenMateriaPrima.query.filter_by(
        codigo_materia=codigo_materia
    ).first()
    imagen = imagen_materia_prima.rendered_data if imagen_materia_prima else None

    materia_prima_data = {
        "codigo_materia": materia_prima.codigo_materia,
        "nombre_materia": materia_prima.nombre_materia,
        "precio": materia_prima.precio,
        "cantidad": materia_prima.cantidad,
        "sucursal_id": materia_prima.sucursal_id,
    }

    return render_template(
        "detalleMateriaPrima.html", materia_prima=materia_prima_data, imagens=imagen
    )


@appmateria.route(
    "/editarMateriaPrima/<string:codigo_materia>", methods=["GET", "POST"]
)
def editar_materia_prima(codigo_materia):
    try:
        materia_prima = Materia_Prima.query.filter_by(
            codigo_materia=codigo_materia
        ).first_or_404()

        if request.method == "GET":
            sucursales = Sucursal.query.all()

            # Puedes agregar más consultas para obtener datos relacionados si es necesario

            return render_template(
                "editarMateriaPrima.html",
                materia_prima=materia_prima,
                sucursales=sucursales,
            )

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
            responseObject = {
                "status": "success",
                "message": "Materia prima editada correctamente",
                "codigo_materia": materia_prima.codigo_materia,
            }
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

        # Eliminar la imagen asociada a la materia prima
        imagen_materia_prima = ImagenMateriaPrima.query.filter_by(
            codigo_materia=codigo_materia
        ).first()
        if imagen_materia_prima:
            db.session.delete(imagen_materia_prima)
            db.session.commit()

        responseObject = {
            "status": "success",
            "message": "Materia prima y su imagen asociada eliminadas correctamente",
        }
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)


@appmateria.route(
    "/modificarImagenMateriaPrima/<string:codigo_materia>", methods=["POST"]
)
def modificar_imagen_materia_prima(codigo_materia):
    search_image = ImagenMateriaPrima.query.filter_by(
        codigo_materia=codigo_materia
    ).first()

    if search_image:
        file = request.files["inputFile"]
        data = file.read()
        render_file = render_image(data)
        search_image.rendered_data = render_file
        search_image.data = data
        db.session.commit()
        return jsonify({"Message": "Imagen Actualizada"})
    else:
        file = request.files["inputFile"]
        data = file.read()
        render_file = render_image(data)
        new_file = ImagenMateriaPrima()
        new_file.type = "Materia Prima"
        new_file.rendered_data = render_file
        new_file.data = data
        new_file.codigo_materia = codigo_materia
        db.session.add(new_file)
        db.session.commit()
        return jsonify({"Message": "Imagen agregada"})
