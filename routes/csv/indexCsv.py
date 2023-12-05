from flask import Blueprint, Response, render_template, request, jsonify
from models import *

appcsv = Blueprint("appcsv", __name__, template_folder="templates")


@appcsv.route("/Archivos")
def MostrarArchivos():
    return render_template("indexCSV.html")


def generate_csv(empleados):
    # Verifica si hay empleados antes de generar el CSV
    if not empleados:
        return Response("No hay empleados para exportar", status=400)

    # Crear encabezados del CSV
    csv_data = [
        [
            "Clave",
            "RFC",
            "Nombres",
            "Apellidos",
            "Fecha de Nacimiento",
            "Edad",
            "Sueldo",
            "Área Laboral",
            "Email",
            "ID de Usuario",
            "ID de Sucursal",
        ]
    ]

    # Agregar datos de empleados al CSV
    for empleado in empleados:
        empleado_data = [
            empleado.clave,
            empleado.RFC,
            empleado.nombres,
            empleado.apellidos,
            empleado.fecha_nacimiento.strftime("%Y-%m-%d"),
            empleado.edad,
            empleado.sueldo,
            empleado.area_laboral,
            empleado.email,
            empleado.usuario_id,
            empleado.sucursal_id,
        ]
        csv_data.append(empleado_data)

    # Crear un generador para las filas del CSV
    def generate():
        for row in csv_data:
            yield ",".join(map(str, row)) + "\n"

    # Configurar encabezados de respuesta para indicar contenido CSV
    headers = {
        "Content-Disposition": "attachment; filename=empleados.csv",
        "Content-Type": "text/csv",
    }

    # Devolver un objeto de respuesta de Flask con el generador CSV
    return Response(generate(), headers=headers)


def generate_csv_usuarios(usuarios):
    # Verifica si hay usuarios antes de generar el CSV
    if not usuarios:
        return Response("No hay usuarios para exportar", status=400)

    # Crear encabezados del CSV
    csv_data = [
        [
            "ID de Usuario",
            "Nombre de Usuario",
            "Contraseña",
            "Fecha de Registro",
            "Administrador",
            "ID de Sucursal",
        ]
    ]

    # Agregar datos de usuarios al CSV
    for usuario in usuarios:
        usuario_data = [
            usuario.id_usuario,
            usuario.nombre_usuario,
            usuario.password,
            usuario.fecha_registro.isoformat(),
            usuario.admin,
            usuario.sucursal_id,
        ]
        csv_data.append(usuario_data)

    # Crear un generador para las filas del CSV
    def generate():
        for row in csv_data:
            yield ",".join(map(str, row)) + "\n"

    # Configurar encabezados de respuesta para indicar contenido CSV
    headers = {
        "Content-Disposition": "attachment; filename=usuarios.csv",
        "Content-Type": "text/csv",
    }

    # Devolver un objeto de respuesta de Flask con el generador CSV
    return Response(generate(), headers=headers)


def generate_csv_productos(productos):
    # Verifica si hay productos antes de generar el CSV
    if not productos:
        return Response("No hay productos para exportar", status=400)

    # Crear encabezados del CSV
    csv_data = [
        [
            "Código de Producto",
            "Sabor",
            "Precio",
            "Cantidad",
            "ID de Categoría",
            "ID de Sucursal",
        ]
    ]

    # Agregar datos de productos al CSV
    for producto in productos:
        producto_data = [
            producto.codigo_producto,
            producto.sabor,
            producto.precio,
            producto.cantidad,
            producto.categoria_id,
            producto.sucursal_id,
        ]
        csv_data.append(producto_data)

    # Crear un generador para las filas del CSV
    def generate():
        for row in csv_data:
            yield ",".join(map(str, row)) + "\n"

    # Configurar encabezados de respuesta para indicar contenido CSV
    headers = {
        "Content-Disposition": "attachment; filename=productos.csv",
        "Content-Type": "text/csv",
    }

    # Devolver un objeto de respuesta de Flask con el generador CSV
    return Response(generate(), headers=headers)


def generate_csv_materias_primas(materias_primas):
    # Verifica si hay materias primas antes de generar el CSV
    if not materias_primas:
        return Response("No hay materias primas para exportar", status=400)

    # Crear encabezados del CSV
    csv_data = [
        [
            "Código de Materia",
            "Nombre de Materia",
            "Precio",
            "Cantidad",
            "ID de Sucursal",
        ]
    ]

    # Agregar datos de materias primas al CSV
    for materia_prima in materias_primas:
        materia_prima_data = [
            materia_prima.codigo_materia,
            materia_prima.nombre_materia,
            materia_prima.precio,
            materia_prima.cantidad,
            materia_prima.sucursal_id,
        ]
        csv_data.append(materia_prima_data)

    # Crear un generador para las filas del CSV
    def generate():
        for row in csv_data:
            yield ",".join(map(str, row)) + "\n"

    # Configurar encabezados de respuesta para indicar contenido CSV
    headers = {
        "Content-Disposition": "attachment; filename=materias_primas.csv",
        "Content-Type": "text/csv",
    }

    # Devolver un objeto de respuesta de Flask con el generador CSV
    return Response(generate(), headers=headers)


def generate_csv_ventas(ventas):
    # Verifica si hay ventas antes de generar el CSV
    if not ventas:
        return Response("No hay ventas para exportar", status=400)

    # Crear encabezados del CSV
    csv_data = [
        [
            "ID de Venta",
            "Fecha de Venta",
            "Monto",
            "Forma de Pago",
            "ID de Sucursal",
            "Clave de Empleado",
            "Código de Producto",
            "Cantidad",
        ]
    ]

    # Agregar datos de ventas al CSV
    for venta in ventas:
        productos_vendidos_data = venta.get("productos_vendidos", [])
        for producto_vendido in productos_vendidos_data:
            venta_data = [
                venta["id_venta"],
                venta["fecha_venta"],
                venta["monto"],
                venta["forma_pago"],
                venta["sucursal_id"],
                venta["clave_empleado"],
                producto_vendido["codigo_producto"],
                producto_vendido["cantidad"],
            ]
            csv_data.append(venta_data)

    # Crear un generador para las filas del CSV
    def generate():
        for row in csv_data:
            yield ",".join(map(str, row)) + "\n"

    # Configurar encabezados de respuesta para indicar contenido CSV
    headers = {
        "Content-Disposition": "attachment; filename=ventas.csv",
        "Content-Type": "text/csv",
    }

    # Devolver un objeto de respuesta de Flask con el generador CSV
    return Response(generate(), headers=headers)


def generate_csv_encargos(encargos):
    # Verifica si hay encargos antes de generar el CSV
    if not encargos:
        return Response("No hay encargos para exportar", status=400)

    # Crear encabezados del CSV
    csv_data = [
        [
            "ID de Encargo",
            "Código de Materia",
            "Cantidad de Encargo",
            "Cantidad a Pagar",
            "Forma de Pago",
            "Fecha de Encargo",
            "ID de Proveedor",
            "ID de Sucursal",
        ]
    ]

    # Agregar datos de encargos al CSV
    for encargo in encargos:
        encargo_data = [
            encargo.id_encargo,
            encargo.codigo_materia,
            encargo.cantidad_encargo,
            encargo.cantidad_a_pagar,
            encargo.forma_pago,
            encargo.fecha_encargo.strftime("%Y-%m-%d"),
            encargo.proveedor_id,
            encargo.sucursal_id,
        ]
        csv_data.append(encargo_data)

    # Crear un generador para las filas del CSV
    def generate():
        for row in csv_data:
            yield ",".join(map(str, row)) + "\n"

    # Configurar encabezados de respuesta para indicar contenido CSV
    headers = {
        "Content-Disposition": "attachment; filename=encargos.csv",
        "Content-Type": "text/csv",
    }

    # Devolver un objeto de respuesta de Flask con el generador CSV
    return Response(generate(), headers=headers)


@appcsv.route("/descargarcsvempleados")
def descargar_csv_empleados():
    Empleados = Empleado.query.all()
    return generate_csv(Empleados)


@appcsv.route("/descargarcsvusuarios")
def descargar_csv_usuarios():
    Usuarios = Usuario.query.all()
    return generate_csv_usuarios(Usuarios)


@appcsv.route("/descargarcsvencargos")
def descargar_csv_encargos():
    Encargos = Encargo.query.all()
    return generate_csv_encargos(Encargos)


@appcsv.route("/descargarcsvproductos")
def descargar_csv_productos():
    Productos = Producto.query.all()
    return generate_csv_productos(Productos)


@appcsv.route("/descargarcsvmateriasprimas")
def descargar_csv_materiasprimas():
    MateriasPrimas = Materia_Prima.query.all()
    return generate_csv_materias_primas(MateriasPrimas)


@appcsv.route("/descargarcsvventas")
def descargar_csv_ventas():
    Ventas = Venta.query.all()
    return generate_csv_ventas(Ventas)
