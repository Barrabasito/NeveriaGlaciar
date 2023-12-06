from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Encargo,Sucursal,Producto,Proveedor,Materia_Prima
from app import db, bcrypt
from auth import tokenCheck, verificar

appencargo = Blueprint("appencargo", __name__, template_folder="templates")

@appencargo.route("/indexEncargo")
def indexEncargo():
    url="indexEncargo"
    return render_template("indexEncargo.html",url=url)


@appencargo.route("/agregarEncargo", methods=["GET", "POST"])
def add_encargo():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        proveedores = Proveedor.query.all()
        materias_primas = Materia_Prima.query.all()
        url="agregarEncargo"
        return render_template("agregarEncargo.html", sucursales=sucursales, proveedores=proveedores, materias_primas=materias_primas,url=url)
    else:
        # Obtener datos del formulario o solicitud JSON
        codigo_materia = request.json.get("codigo_materia")
        cantidad_encargo = request.json.get("cantidad_encargo")
        cantidad_a_pagar = request.json.get("cantidad_a_pagar")
        forma_pago = request.json.get("forma_pago")
        fecha_encargo = request.json.get("fecha_encargo")
        proveedor_id = request.json.get("proveedor_id")
        sucursal_id = request.json.get("sucursal_id")

        # Verificar si la sucursal y el proveedor existen
        sucursal = Sucursal.query.get(sucursal_id)
        proveedor = Proveedor.query.get(proveedor_id)
        if not sucursal:
            return jsonify({"status": "error", "message": "La sucursal no existe"})
        if not proveedor:
            return jsonify({"status": "error", "message": "El proveedor no existe"})

        # Crear una instancia de Encargo y asignar los valores
        encargo = Encargo(
            codigo_materia=codigo_materia,
            cantidad_encargo=cantidad_encargo,
            cantidad_a_pagar=cantidad_a_pagar,
            forma_pago=forma_pago,
            fecha_encargo=fecha_encargo,
            proveedor_id=proveedor_id,
            sucursal_id=sucursal_id
        )

        try:
            db.session.add(encargo)
            db.session.commit()
            responseObject = {"status": "success", "message": "Encargo agregado correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)


@appencargo.route("/listaEncargos")
def consulta_encargos():
    encargos = Encargo.query.all()
    encargos_data = [
        {
            'id_encargo': encargo.id_encargo,
            'codigo_materia': encargo.codigo_materia,
            'cantidad_encargo': encargo.cantidad_encargo,
            'cantidad_a_pagar': encargo.cantidad_a_pagar,
            'forma_pago': encargo.forma_pago,
            'fecha_encargo': encargo.fecha_encargo.strftime('%Y-%m-%d'),
            'proveedor_id': encargo.proveedor_id,
            'sucursal_id': encargo.sucursal_id
        } for encargo in encargos
    ]
    return jsonify({'encargos': encargos_data})


@appencargo.route("/eliminarEncargo/<int:id_encargo>", methods=["DELETE"])
def eliminar_encargo(id_encargo):
    try:
        encargo = Encargo.query.get_or_404(id_encargo)

        # Eliminar el encargo
        db.session.delete(encargo)
        db.session.commit()

        responseObject = {"status": "success", "message": "Encargo eliminado correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)
