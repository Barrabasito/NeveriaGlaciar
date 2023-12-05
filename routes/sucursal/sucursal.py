from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from sqlalchemy import exc
from models import Sucursal,Telefono
from app import db, bcrypt
from auth import tokenCheck, verificar

appsucursal = Blueprint("appsucursal", __name__, template_folder="templates")

@appsucursal.route("/indexSucursal")
@tokenCheck
def indexSucursal(usuario):
    print(usuario)
    if usuario["admin"]:
        # Puedes agregar lógica específica para usuarios admin aquí, si es necesario
        return render_template("indexSucursal.html")
    else:
        print("No tienes permisos de administrador")
        # Redirige al usuario a una página específica para manejar la falta de permisos
        return redirect(url_for('sin_permisos'))

@appsucursal.route("/sin_permisos")
def sin_permisos():
    return render_template("error/sinPermisos.html")

@appsucursal.route("/agregarSucursal", methods=["GET", "POST"])
def add_sucursal():
    if request.method == "GET":
        return render_template("agregarSucursal.html")
    else:
        nombre = request.json.get("nombre")
        direccion = request.json.get("direccion")
        telefonos = request.json.get("telefonos", [])

        sucursal = Sucursal(nombre=nombre, direccion=direccion)

        for telefono_numero in telefonos:
            telefono = Telefono(numero=telefono_numero)
            sucursal.telefonos.append(telefono)

        try:
            db.session.add(sucursal)
            db.session.commit()
            responseObject = {"status": "success", "message": "Sucursal y teléfonos agregados correctamente"}
        except Exception as e:
            db.session.rollback()
            responseObject = {"status": "error", "message": str(e)}
        finally:
            db.session.close()

        return jsonify(responseObject)
    

@appsucursal.route("/listaSucursales")
def consulta_sucursales():
    sucursales = Sucursal.query.all()
    sucursales_data = []

    for sucursal in sucursales:
        telefonos = Telefono.query.filter_by(sucursal_id=sucursal.id_sucursal).all()
        telefonos_data = [{'numero': telefono.numero} for telefono in telefonos]

        sucursal_data = {
            'id_sucursal': sucursal.id_sucursal,
            'nombre': sucursal.nombre,
            'direccion': sucursal.direccion,
            'telefonos': telefonos_data
        }

        sucursales_data.append(sucursal_data)

    return jsonify({'sucursales': sucursales_data})

@appsucursal.route("/detalleSucursal/<int:sucursal_id>")
def ver_sucursal(sucursal_id):
    sucursal = Sucursal.query.get_or_404(sucursal_id)
    telefonos = Telefono.query.filter_by(sucursal_id=sucursal.id_sucursal).all()
    telefonos_data = [{'numero': telefono.numero} for telefono in telefonos]

    sucursal_data = {
        'id_sucursal': sucursal.id_sucursal,
        'nombre': sucursal.nombre,
        'direccion': sucursal.direccion,
        'telefonos': telefonos_data
    }
    print(sucursal_data)

    return render_template("detalleSucursal.html", sucursal=sucursal_data)


@appsucursal.route("/editarSucursal/<int:sucursal_id>", methods=["GET", "POST"])
def editar_sucursal(sucursal_id):
    try:
        sucursal = Sucursal.query.get_or_404(sucursal_id)

        if request.method == "GET":
            telefonos = [telefono.numero for telefono in sucursal.telefonos]
            return render_template("editarSucursal.html", sucursal=sucursal, telefonos=telefonos)

        else:
            nombre = request.json.get("nombre")
            direccion = request.json.get("direccion")
            telefonos = request.json.get("telefonos", [])

            print(nombre, direccion, telefonos)
            print(sucursal.nombre, sucursal.direccion, [telefono.numero for telefono in sucursal.telefonos])
            print(sucursal_id)
            
            sucursal.nombre = nombre
            sucursal.direccion = direccion

            # Iterar sobre los teléfonos existentes y actualizarlos según el JSON
            for i, telefono_existente in enumerate(sucursal.telefonos):
                if i < len(telefonos):
                    # Actualizar teléfono existente con el valor del JSON
                    telefono_existente.numero = telefonos[i]
                else:
                    break  # No hay más teléfonos en el JSON, salir del bucle
                
            # Mantener los teléfonos que están en la lista actual
            telefonos_actuales = [telefono.numero for telefono in sucursal.telefonos if telefono.numero in telefonos]

            # Eliminar los teléfonos que ya no están en la lista
            for telefono in sucursal.telefonos[:]:
                if telefono.numero not in telefonos:
                    db.session.delete(telefono)

            # Agregar nuevos teléfonos
            for telefono_numero in telefonos:
                if telefono_numero not in telefonos_actuales:
                    telefono = Telefono(numero=telefono_numero)
                    sucursal.telefonos.append(telefono)

            db.session.commit()
            responseObject = {"status": "success", "message": "Sucursal y teléfonos editados correctamente", "id_sucursal": sucursal.id_sucursal}
            return jsonify(responseObject)

    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
        return jsonify(responseObject)

    finally:
        db.session.close()

@appsucursal.route("/eliminarSucursal/<int:sucursal_id>", methods=["DELETE"])
def eliminar_sucursal(sucursal_id):
    try:
        sucursal = Sucursal.query.get_or_404(sucursal_id)

        # Elimina los teléfonos asociados a la sucursal
        for telefono in sucursal.telefonos:
            db.session.delete(telefono)

        # Elimina la sucursal
        db.session.delete(sucursal)
        db.session.commit()

        responseObject = {"status": "success", "message": "Sucursal y teléfonos asociados eliminados correctamente"}
    except Exception as e:
        db.session.rollback()
        responseObject = {"status": "error", "message": str(e)}
    finally:
        db.session.close()

    return jsonify(responseObject)
