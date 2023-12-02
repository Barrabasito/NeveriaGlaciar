from flask import Blueprint, request, jsonify, render_template, redirect
from sqlalchemy import exc
from models import Categoria
from app import db, bcrypt
from auth import tokenCheck, verificar

appcategoria = Blueprint("appcategoria", __name__, template_folder="templates")

@appcategoria.route("/indexCategoria")
def indexCategoria():
    return render_template("indexCategoria.html")


@appcategoria.route("/agregarCategoria", methods=["GET", "POST"])
def add_categoria():
    if request.method == "GET":
        return render_template("agregarCategoria.html")
    else:
        # Obtener datos del formulario o solicitud JSON
        nombre_categoria = request.json.get("nombre_categoria")

       
        # Verificar si la categoría ya existe
        categoria_existente = Categoria.query.filter_by(nombre_categoria=nombre_categoria).first()
        if categoria_existente:
            return jsonify({"status": "error", "message": "La categoría ya existe"})

        # Crear una instancia de Categoria y asignar los valores
        nueva_categoria = Categoria(nombre_categoria=nombre_categoria)

        try:
            db.session.add(nueva_categoria)
            db.session.commit()
            responseObject = {"status": "success", "message": "Categoría agregada correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)
    
@appcategoria.route("/listaCategorias")
def consulta_categorias():
    categorias = Categoria.query.all()
    categorias_data = [
        {
            'id_categoria': categoria.id_categoria,
            'nombre_categoria': categoria.nombre_categoria
        } for categoria in categorias
    ]
    return jsonify({'categorias': categorias_data})



@appcategoria.route("/detalleCategoria/<int:id_categoria>")
def ver_categoria(id_categoria):
    categoria = Categoria.query.get_or_404(id_categoria)

    categoria_data = {
        'id_categoria': categoria.id_categoria,
        'nombre_categoria': categoria.nombre_categoria
    }

    return render_template("detalleCategoria.html", categoria=categoria_data)


@appcategoria.route("/editarCategoria/<int:id_categoria>", methods=["GET", "POST"])
def editar_categoria(id_categoria):
    try:
        categoria = Categoria.query.get_or_404(id_categoria)

        if request.method == "GET":
            return render_template("editarCategoria.html", categoria=categoria)

        else:
            nombre_categoria = request.json.get("nombre_categoria")

            categoria.nombre_categoria = nombre_categoria

            db.session.commit()
            responseObject = {"status": "success", "message": "Categoría editada correctamente", "id_categoria": categoria.id_categoria}
            return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()



@appcategoria.route("/eliminarCategoria/<int:id_categoria>", methods=["DELETE"])
def eliminar_categoria(id_categoria):
    try:
        categoria = Categoria.query.get_or_404(id_categoria)

        # Eliminar la categoría
        db.session.delete(categoria)
        db.session.commit()

        responseObject = {"status": "success", "message": "Categoría eliminada correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)
