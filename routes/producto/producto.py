from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Producto, Sucursal, Categoria
from app import db, bcrypt
from auth import tokenCheck, verificar
from models import ImagenProducto
import base64

appproducto = Blueprint("appproducto", __name__, template_folder="templates")


def render_image(data):
    render_img = base64.b64encode(data).decode("ascii")
    return render_img


@appproducto.route("/indexProducto")
def indexProducto():
    return render_template("indexProducto.html")


@appproducto.route("/agregarProducto", methods=["GET", "POST"])
def agregar_producto():
    if request.method == "GET":
        # Consulta de todas las sucursales y categorias dentro de la base de datos
        # se manda a la vista agregarproducto
        sucursales = Sucursal.query.all()
        categorias = Categoria.query.all()
        return render_template(
            "agregarProducto.html", sucursales=sucursales, categorias=categorias
        )
    else:
        try:
            # Obtener datos del formulario y cargar en JSON
            datos_producto = {
                "codigo_producto": request.form["codigo_producto"],
                "sabor": request.form["sabor"],
                "precio": float(request.form["precio"]),
                "cantidad": int(request.form["cantidad"]),
                "categoria_id": int(request.form["categoria_id"]),
                "sucursal_id": int(request.form["sucursal_id"]),
            }

            # Verificar si la sucursal existe
            sucursal = Sucursal.query.get(datos_producto["sucursal_id"])
            if not sucursal:
                return jsonify({"status": "error", "message": "La sucursal no existe"})

            # Crear una instancia de Producto y asignar los valores
            producto = Producto(**datos_producto)

            db.session.add(producto)
            db.session.commit()
            # Manejar la carga de imágenes
            file = request.files["inputFile"]
            data = file.read()
            render_file = render_image(data)
            imagen_producto = ImagenProducto(
                type="Producto",
                rendered_data=render_file,
                data=data,
                codigo_producto=datos_producto["codigo_producto"],
            )
            db.session.add(imagen_producto)
            db.session.commit()

            responseObject = {
                "status": "success",
                "message": "Producto y imagen agregados correctamente",
            }
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
            "codigo_producto": producto.codigo_producto,
            "sabor": producto.sabor,
            "precio": producto.precio,
            "cantidad": producto.cantidad,
            "categoria_id": producto.categoria_id,
            "sucursal_id": producto.sucursal_id,
        }
        for producto in productos
    ]
    return jsonify({"productos": productos_data})


@appproducto.route("/detalleProducto/<string:codigo_producto>")
def ver_producto(codigo_producto):
    producto = Producto.query.filter_by(codigo_producto=codigo_producto).first_or_404()
    imagenes = ImagenProducto.query.filter_by(
        codigo_producto=producto.codigo_producto
    ).first()
    images = imagenes.rendered_data
    producto_data = {
        "codigo_producto": producto.codigo_producto,
        "sabor": producto.sabor,
        "precio": producto.precio,
        "cantidad": producto.cantidad,
        "categoria_id": producto.categoria_id,
        "sucursal_id": producto.sucursal_id,
    }
    return render_template(
        "detalleProducto.html", producto_data=producto_data, imagens=images
    )


@appproducto.route("/editarProducto/<string:codigo_producto>", methods=["GET", "POST"])
def editar_producto(codigo_producto):
    try:
        producto = Producto.query.filter_by(
            codigo_producto=codigo_producto
        ).first_or_404()
        if request.method == "GET":
            categorias = Categoria.query.all()
            sucursales = Sucursal.query.all()
            categoria = Categoria.query.get(producto.categoria_id)
            sucursal = Sucursal.query.get(producto.sucursal_id)
            return render_template(
                "editarProducto.html",
                producto=producto,
                categoriaActual=categoria,
                sucursalActual=sucursal,
                categorias=categorias,
                sucursales=sucursales,
            )
        elif request.method == "POST":
            # Obtener datos del formulario y cargar en JSON
            datos_producto = {
                "sabor": request.form["sabor"],
                "precio": float(request.form["precio"]),
                "cantidad": int(request.form["cantidad"]),
                "categoria_id": int(request.form["categoria_id"]),
                "sucursal_id": int(request.form["sucursal_id"]),
            }

            # Actualizar los datos del producto
            for key, value in datos_producto.items():
                setattr(producto, key, value)

            # Manejar la carga de la nueva imagen si se proporciona
            nueva_imagen = request.files.get("nueva_imagen")
            if nueva_imagen:
                nueva_imagen_data = nueva_imagen.read()
                render_file = render_image(nueva_imagen_data)
                imagen_producto = ImagenProducto(
                    type="Producto",
                    rendered_data=render_file,
                    data=nueva_imagen_data,
                    codigo_producto=codigo_producto,
                )
                db.session.add(imagen_producto)
            db.session.commit()
            responseObject = {
                "status": "success",
                "message": "Producto editado correctamente",
                "codigo_producto": producto.codigo_producto,
            }
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
        imagen = ImagenProducto.query.filter_by(
            codigo_producto=producto.codigo_producto
        ).first()
        if imagen:
            db.session.delete(imagen)
        # Eliminar el producto
        db.session.delete(producto)
        db.session.commit()
        responseObject = {
            "status": "success",
            "message": "Producto eliminado correctamente",
        }
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()
    return jsonify(responseObject)


@appproducto.route(
    "/modificarImagenProducto/<string:codigo_producto>", methods=["POST"]
)
def modificarImagen(codigo_producto):
    searchImage = ImagenProducto.query.filter_by(
        codigo_producto=codigo_producto
    ).first()
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
        newFile = ImagenProducto()
        newFile.type = "Producto"
        newFile.rendered_data = render_file
        newFile.data = data
        newFile.codigo_producto = codigo_producto
        db.session.add(newFile)
        db.session.commit()
        return jsonify({"Message": "Imagen agregada"})
