from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Venta,Producto,Producto_Vendido,Sucursal,Empleado
from app import db, bcrypt
from auth import tokenCheck, verificar
import datetime

appventa = Blueprint("appventa", __name__, template_folder="templates")

@appventa.route("/indexVenta")
def indexVenta():
    return render_template("indexVenta.html")


@appventa.route("/agregarVenta", methods=["GET", "POST"])
def agregar_venta():
    if request.method == "GET":
        # Cargar datos necesarios para el formulario, por ejemplo, empleados y sucursales
        empleados = Empleado.query.all()
        productos = Producto.query.all()
        sucursales = Sucursal.query.all()
        return render_template("agregarVenta.html", empleados=empleados, sucursales=sucursales, productos=productos)
    else:
        fecha_venta = datetime.datetime.now()
        monto = request.json.get("monto")
        forma_pago = request.json.get("forma_pago")
        sucursal_id = request.json.get("sucursal_id")
        clave_empleado = request.json.get("clave_empleado")
        productos_vendidos = request.json.get("productos_vendidos", [])

        venta = Venta(
            fecha_venta=fecha_venta,
            monto=monto,
            forma_pago=forma_pago,
            sucursal_id=sucursal_id,
            clave=clave_empleado
        )

        for producto_vendido_data in productos_vendidos:
            codigo_producto = producto_vendido_data.get("codigo_producto")
            cantidad = producto_vendido_data.get("cantidad")

            producto_vendido = Producto_Vendido(
                codigo_producto=codigo_producto,
                cantidad=cantidad
            )

            venta.productos_vendidos.append(producto_vendido)

        try:
            db.session.add(venta)
            db.session.commit()
            responseObject = {"status": "success", "message": "Venta y productos vendidos agregados correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)


    
@appventa.route("/listaVentas")
def consulta_ventas():
    ventas = Venta.query.all()
    ventas_data = []

    for venta in ventas:
        productos_vendidos = Producto_Vendido.query.filter_by(venta_id=venta.id_venta).all()
        productos_vendidos_data = [{'codigo_producto': producto_vendido.codigo_producto, 'cantidad': producto_vendido.cantidad} for producto_vendido in productos_vendidos]

        venta_data = {
            'id_venta': venta.id_venta,
            'fecha_venta': venta.fecha_venta.isoformat(),
            'monto': venta.monto,
            'forma_pago': venta.forma_pago,
            'sucursal_id': venta.sucursal_id,
            'clave_empleado': venta.clave,
            'productos_vendidos': productos_vendidos_data
        }

        ventas_data.append(venta_data)

    return jsonify({'ventas': ventas_data})

@appventa.route("/detalleVenta/<int:venta_id>")
def ver_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    productos_vendidos = Producto_Vendido.query.filter_by(venta_id=venta.id_venta).all()
    productos_vendidos_data = [{'codigo_producto': producto_vendido.codigo_producto, 'cantidad': producto_vendido.cantidad} for producto_vendido in productos_vendidos]

    venta_data = {
        'id_venta': venta.id_venta,
        'fecha_venta': venta.fecha_venta.isoformat(),
        'monto': venta.monto,
        'forma_pago': venta.forma_pago,
        'sucursal_id': venta.sucursal_id,
        'clave_empleado': venta.clave,
        'productos_vendidos': productos_vendidos_data
    }

    return render_template("detalleVenta.html", venta=venta_data)



@appventa.route("/eliminarVenta/<int:id_venta>", methods=["DELETE"])
def eliminar_venta(id_venta):
    try:
        venta = Venta.query.get_or_404(id_venta)

        # Elimina los productos vendidos asociados a la venta
        for producto_vendido in venta.productos_vendidos:
            db.session.delete(producto_vendido)

        # Elimina la venta
        db.session.delete(venta)
        db.session.commit()

        responseObject = {"status": "success", "message": "Venta y productos vendidos asociados eliminados correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)

