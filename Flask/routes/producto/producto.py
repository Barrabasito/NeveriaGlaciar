from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Producto,Sucursal,Categoria
from app import db, bcrypt
from auth import tokenCheck, verificar

appproducto = Blueprint("appproducto", __name__, template_folder="templates")

@appproducto.route("/indexProducto")
def indexProducto():
    return render_template("indexProducto.html")


@appproducto.route("/agregarProducto", methods=["GET", "POST"])
def add_producto():
    if request.method == "GET":
        sucursales = Sucursal.query.all()
        categorias = Categoria.query.all()
        return render_template("agregarProducto.html", sucursales=sucursales, categorias=categorias)
    else:
        # Obtener datos del formulario o solicitud JSON
        codigo_producto = request.json.get("codigo_producto")
        sabor = request.json.get("sabor")
        precio = request.json.get("precio")
        cantidad = request.json.get("cantidad")
        categoria_id = request.json.get("categoria_id")
        sucursal_id = request.json.get("sucursal_id")

        # Verificar si la sucursal existe
        sucursal = Sucursal.query.get(sucursal_id)
        if not sucursal:
            return jsonify({"status": "error", "message": "La sucursal no existe"})

        # Crear una instancia de Producto y asignar los valores
        producto = Producto(
            codigo_producto=codigo_producto,
            sabor=sabor,
            precio=precio,
            cantidad=cantidad,
            categoria_id=categoria_id,
            sucursal_id=sucursal_id
        )

        try:
            db.session.add(producto)
            db.session.commit()
            responseObject = {"status": "success", "message": "Producto agregado correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)
    

@appproducto.route("/listaProductos")
def consulta_productos():
    productos = Producto.query.all()
    productos_data = [
        {
            'codigo_producto': producto.codigo_producto,
            'sabor': producto.sabor,
            'precio': producto.precio,
            'cantidad': producto.cantidad,
            'categoria_id': producto.categoria_id,
            'sucursal_id': producto.sucursal_id
        } for producto in productos
    ]
    return jsonify({'productos': productos_data})


@appproducto.route("/detalleProducto/<string:codigo_producto>")
def ver_producto(codigo_producto):
    producto = Producto.query.filter_by(codigo_producto=codigo_producto).first_or_404()

    producto_data = {
        'codigo_producto': producto.codigo_producto,
        'sabor': producto.sabor,
        'precio': producto.precio,
        'cantidad': producto.cantidad,
        'categoria_id': producto.categoria_id,
        'sucursal_id': producto.sucursal_id
    }

    return render_template("detalleProducto.html", producto=producto_data)



@appproducto.route("/editarProducto/<string:codigo_producto>", methods=["GET", "POST"])
def editar_producto(codigo_producto):
    try:
        producto = Producto.query.filter_by(codigo_producto=codigo_producto).first_or_404()

        if request.method == "GET":
            categorias = Categoria.query.all()
            sucursales = Sucursal.query.all()
           
            categoria = Categoria.query.get(producto.categoria_id)
            sucursal = Sucursal.query.get(producto.sucursal_id)
            
            return render_template("editarProducto.html", producto=producto, categoriaActual=categoria, sucursalActual=sucursal, categorias=categorias, sucursales=sucursales)

        else:
            sabor = request.json.get("sabor")
            precio = request.json.get("precio")
            cantidad = request.json.get("cantidad")
            categoria_id = request.json.get("categoria_id")
            sucursal_id = request.json.get("sucursal_id")

            producto.sabor = sabor
            producto.precio = precio
            producto.cantidad = cantidad
            producto.categoria_id = categoria_id
            producto.sucursal_id = sucursal_id

            db.session.commit()
            responseObject = {"status": "success", "message": "Producto editado correctamente", "codigo_producto": producto.codigo_producto}
            return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()


@appproducto.route("/eliminarProducto/<string:codigo_producto>", methods=["DELETE"])
def eliminar_producto(codigo_producto):
    try:
        producto = Producto.query.get_or_404(codigo_producto)

        # Eliminar el producto
        db.session.delete(producto)
        db.session.commit()

        responseObject = {"status": "success", "message": "Producto eliminado correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)