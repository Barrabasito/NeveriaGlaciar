from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Proveedor,Producto,Sucursal,Categoria
from app import db, bcrypt
from auth import tokenCheck, verificar

appproveedor = Blueprint("appproveedor", __name__, template_folder="templates")

@appproveedor.route("/indexProveedor")
def indexProveedor():
    return render_template("indexProveedor.html")


@appproveedor.route("/agregarProveedor", methods=["GET", "POST"])
def agregar_proveedor():
    if request.method == "GET":
        # En el caso de GET, simplemente renderiza el formulario
        return render_template("agregarProveedor.html")
    else:
        # En el caso de POST, obtén los datos del formulario o solicitud JSON
        nombres = request.json.get("nombres")
        apellidos = request.json.get("apellidos")
        direccion = request.json.get("direccion")
        telefono = request.json.get("telefono")

        # Verificar si el proveedor ya existe
        proveedor_existente = Proveedor.query.filter_by(nombres=nombres, apellidos=apellidos).first()
        if proveedor_existente:
            return jsonify({"status": "error", "message": "El proveedor ya existe"})

        # Crear una instancia de Proveedor y asignar los valores
        nuevo_proveedor = Proveedor(
            nombres=nombres,
            apellidos=apellidos,
            direccion=direccion,
            telefono=telefono
        )

        try:
            db.session.add(nuevo_proveedor)
            db.session.commit()
            responseObject = {"status": "success", "message": "Proveedor agregado correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)


@appproveedor.route("/listaProveedores")
def lista_proveedores():
    proveedores = Proveedor.query.all()
    proveedores_data = [
        {
            'id_proveedor': proveedor.id_proveedor,
            'nombres': proveedor.nombres,
            'apellidos': proveedor.apellidos,
            'direccion': proveedor.direccion,
            'telefono': proveedor.telefono
        } for proveedor in proveedores
    ]
    return jsonify({'proveedores': proveedores_data})



@appproveedor.route("/detalleProveedor/<int:id_proveedor>")
def detalle_proveedor(id_proveedor):
    proveedor = Proveedor.query.get_or_404(id_proveedor)

    proveedor_data = {
        'id_proveedor': proveedor.id_proveedor,
        'nombres': proveedor.nombres,
        'apellidos': proveedor.apellidos,
        'direccion': proveedor.direccion,
        'telefono': proveedor.telefono
    }

    return render_template("detalleProveedor.html", proveedor=proveedor_data)



@appproveedor.route("/editarProveedor/<int:id_proveedor>", methods=["GET", "POST"])
def editar_proveedor(id_proveedor):
    try:
        proveedor = Proveedor.query.get_or_404(id_proveedor)

        if request.method == "GET":
            return render_template("editarProveedor.html", proveedor=proveedor)

        else:
            nombres = request.json.get("nombres")
            apellidos = request.json.get("apellidos")
            direccion = request.json.get("direccion")
            telefono = request.json.get("telefono")

            # Actualizar los valores del proveedor
            proveedor.nombres = nombres
            proveedor.apellidos = apellidos
            proveedor.direccion = direccion
            proveedor.telefono = telefono

            db.session.commit()

            responseObject = {"status": "success", "message": "Proveedor editado correctamente", "id_proveedor": proveedor.id_proveedor}
            return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()


@appproveedor.route("/eliminarProveedor/<int:id_proveedor>", methods=["DELETE"])
def eliminar_proveedor(id_proveedor):
    try:
        proveedor = Proveedor.query.get_or_404(id_proveedor)

        # Eliminar el proveedor
        db.session.delete(proveedor)
        db.session.commit()

        responseObject = {"status": "success", "message": "Proveedor eliminado correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)
