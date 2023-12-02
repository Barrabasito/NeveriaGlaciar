from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Cliente,Sucursal
from app import db, bcrypt
from auth import tokenCheck, verificar
import datetime

appcliente = Blueprint("appcliente", __name__, template_folder="templates")

@appcliente.route("/indexCliente")
def indexCliente():
    return render_template("indexCliente.html")


@appcliente.route("/agregarCliente", methods=["GET", "POST"])
def add_cliente():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        return render_template("agregarCliente.html", sucursales=sucursales)
    else:
        # Obtener datos del formulario o solicitud JSON
        nombre_empresa = request.json.get("nombre_empresa")
        direccion = request.json.get("direccion")
        codigo_producto = request.json.get("codigo_producto")
        cantidad_pedida = request.json.get("cantidad_pedida")
        costo_total = request.json.get("costo_total")
        forma_pago = request.json.get("forma_pago")
        fecha_registro = datetime.datetime.now()
        sucursal_id = request.json.get("sucursal_id")

        # Verificar si la sucursal existe
        sucursal = Sucursal.query.get(sucursal_id)
        if not sucursal:
            return jsonify({"status": "error", "message": "La sucursal no existe"})

        # Crear una instancia de Cliente y asignar los valores
        cliente = Cliente(
            nombre_empresa=nombre_empresa,
            direccion=direccion,
            codigo_producto=codigo_producto,
            cantidad_pedida=cantidad_pedida,
            costo_total=costo_total,
            forma_pago=forma_pago,
            fecha_registro=fecha_registro,
            sucursal_id=sucursal_id
        )

        try:
            db.session.add(cliente)
            db.session.commit()
            responseObject = {"status": "success", "message": "Cliente agregado correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)


@appcliente.route("/listaClientes")
def lista_clientes():
    clientes = Cliente.query.all()
    clientes_data = [
        {
            'nombre_empresa': cliente.nombre_empresa,
            'direccion': cliente.direccion,
            'codigo_producto': cliente.codigo_producto,
            'cantidad_pedida': cliente.cantidad_pedida,
            'costo_total': cliente.costo_total,
            'forma_pago': cliente.forma_pago,
            'sucursal_id': cliente.sucursal_id
        } for cliente in clientes
    ]
    return jsonify({'clientes': clientes_data})

@appcliente.route("/detalleCliente/<string:nombre_empresa>")
def ver_cliente(nombre_empresa):
    cliente = Cliente.query.filter_by(nombre_empresa=nombre_empresa).first_or_404()

    cliente_data = {
        'nombre_empresa': cliente.nombre_empresa,
        'direccion': cliente.direccion,
        'codigo_producto': cliente.codigo_producto,
        'cantidad_pedida': cliente.cantidad_pedida,
        'costo_total': cliente.costo_total,
        'forma_pago': cliente.forma_pago,
        'fecha_registro': cliente.fecha_registro.strftime("%Y-%m-%d"),
        'sucursal_id': cliente.sucursal_id
    }

    return render_template("detalleCliente.html", cliente=cliente_data)



@appcliente.route("/editarCliente/<string:nombre_empresa>", methods=["GET", "POST"])
def editar_cliente(nombre_empresa):
    try:
        cliente = Cliente.query.filter_by(nombre_empresa=nombre_empresa).first_or_404()

        if request.method == "GET":
            sucursales = Sucursal.query.all()

            return render_template("editarCliente.html", cliente=cliente, sucursales=sucursales)

        else:
            direccion = request.json.get("direccion")
            codigo_producto = request.json.get("codigo_producto")
            cantidad_pedida = request.json.get("cantidad_pedida")
            costo_total = request.json.get("costo_total")
            forma_pago = request.json.get("forma_pago")
            sucursal_id = request.json.get("sucursal_id")

            cliente.direccion = direccion
            cliente.codigo_producto = codigo_producto
            cliente.cantidad_pedida = cantidad_pedida
            cliente.costo_total = costo_total
            cliente.forma_pago = forma_pago
            cliente.sucursal_id = sucursal_id

            db.session.commit()
            responseObject = {"status": "success", "message": "Cliente editado correctamente", "nombre_empresa": cliente.nombre_empresa}
            return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()



@appcliente.route("/eliminarCliente/<string:nombre_empresa>", methods=["DELETE"])
def eliminar_cliente(nombre_empresa):
    try:
        cliente = Cliente.query.get_or_404(nombre_empresa)

        # Eliminar el cliente
        db.session.delete(cliente)
        db.session.commit()

        responseObject = {"status": "success", "message": "Cliente eliminado correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)
