from models import Usuario
from functools import wraps
from flask import jsonify, request

#Se manda a llamar en Verificar para comprobar informacion
def obtenerInfo(tokens):
    if tokens:
        resp = Usuario.decode_auth_token(tokens)
        print(resp)
        user = Usuario.query.filter_by(id_usuario=resp["sub"]).first()
        print(user)
        if user:
            usuario = {
                "status": "success",
                "data": {
                    "user_id": user.id_usuario,
                    "email": user.nombre_usuario,
                    "admin": user.admin,
                    "registered_on": user.fecha_registro,
                    "sucursal_id":user.sucursal_id,
                },
            }
            return usuario
        else:
            error = {"status": "fail", "message": resp}
            return error


def tokenCheck(f):
    @wraps(f)
    def verificar(*args, **kwargs):
        token = None

        # Obtener el token del encabezado de la solicitud
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)

        if not token:
            return jsonify({"token": "Token no válido"})

        try:
            info = obtenerInfo(token)
            if info["status"] == "fail":
                return jsonify({"message": "Token inválido"})
        except Exception as e:
            print(e)
            return jsonify({"message": "Error al procesar el token"})

        # Puedes hacer algo con la información del token si es necesario

        return f(info["data"], *args, **kwargs)

    return verificar


#Se verifica a la hora de iniciar Sesion
def verificar(token):
    print(token)
    if not token:
        return jsonify({"token": "Token no valido"})
    try:
        info = obtenerInfo(token)
        if info["status"] == "fail":
            return jsonify({"message": "Token failed"})
    except Exception as e:
        print(e)
        return jsonify({"message": "Token invalid"})
    return info
