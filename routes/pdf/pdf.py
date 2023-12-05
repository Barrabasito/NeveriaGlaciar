# pip install reportlab
from flask import Blueprint, make_response, render_template
from models import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Image,
    Flowable,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Image,
    PageTemplate,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime

apppdf = Blueprint("apppdf", __name__, template_folder="templates")


@apppdf.route("/generatePdfUsers")
def generate_pdf():
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate("users.pdf", pagesize=letter)

    # Fetch usuarios data
    usuarios = Usuario.query.all()

    # Define data for the table
    listaUsuarios = [["ID", "USUARIO", "REGISTRADO", "ADMIN"]]
    for usuario in usuarios:
        listaUsuarios.append(
            [
                usuario.id_usuario,
                usuario.nombre_usuario,
                usuario.fecha_registro,
                usuario.admin,
            ]
        )

    # Create the table
    table = Table(listaUsuarios)

    # Define the style for the table
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 16),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Apply the style to the table
    table.setStyle(style)

    # Create a paragraph object for the message
    message = "Listado de usuarios"

    # Create a Paragraph object for the message
    style_message = getSampleStyleSheet()["Normal"]
    style_message.alignment = 1  # Center alignment
    paragraph_message = Paragraph(message, style_message)

    # Create a Paragraph object for the watermark (logo)
    watermark = Image("static/image/NeveriaGlaciar.png", width=100, height=100)

    # Create a Paragraph object for the date
    date_paragraph = Paragraph(f"Created on: {current_date}", style_message)

    # Build the PDF with the elements
    elements = [watermark, date_paragraph, paragraph_message, table]

    # Set the coordinates for the elements
    watermark_x = 0  # Adjust the X-coordinate for the logo
    watermark_y = doc.height - 800  # Adjust the Y-coordinate for the logo
    date_x = doc.width - 800  # Adjust the X-coordinate for the date
    date_y = doc.height - 40  # Adjust the Y-coordinate for the date

    # Set the positions for the elements
    positions = [
        (watermark_x, watermark_y),
        (date_x, date_y),
        None,  # Placeholder for paragraph_message, as it doesn't have specific coordinates
        None,  # Placeholder for table, as it doesn't have specific coordinates
    ]

    # Add the positions to the elements
    elements += positions

    # # Set the style for the watermark
    # watermark_style = getSampleStyleSheet()["Normal"]
    # # watermark_style.alignment = 1  # Center alignment
    # watermark = Paragraph(f"Created on: {current_date}", watermark_style)
    # Eliminar elementos que no son Flowable
    elements = [element for element in elements if isinstance(element, Flowable)]
    #    Build the PDF with the elements
    doc.build(elements)

    # Create a response with the PDF file
    response = make_response(open("users.pdf", "rb").read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=users.pdf"
    return response


@apppdf.route("/generatePdfEmpleados")
def generate_pdf_empleados():
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate("employees.pdf", pagesize=letter)

    # Fetch employees data
    empleados = Empleado.query.all()

    # Define data for the table
    listaEmpleados = [
        [
            "Clave",
            "RFC",
            "Nombres",
            "Apellidos",
            "Fecha Nacimiento",
            "Sueldo",
            "Area Laboral",
        ]
    ]

    for empleado in empleados:
        listaEmpleados.append(
            [
                empleado.clave,
                empleado.RFC,
                empleado.nombres,
                empleado.apellidos,
                empleado.fecha_nacimiento.strftime("%Y-%m-%d"),
                empleado.sueldo,
                empleado.area_laboral,
            ]
        )

    # Create the table
    table = Table(listaEmpleados)

    # Define the style for the table
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 16),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Apply the style to the table
    table.setStyle(style)

    # Create a paragraph object for the message
    message = "Listado de empleados"

    # Create a Paragraph object for the message
    style_message = getSampleStyleSheet()["Normal"]
    style_message.alignment = 1  # Center alignment
    paragraph_message = Paragraph(message, style_message)

    # Create a Paragraph object for the watermark (logo)
    watermark = Image("static/image/NeveriaGlaciar.png", width=100, height=100)

    # Create a Paragraph object for the date
    date_paragraph = Paragraph(f"Created on: {current_date}", style_message)

    # Build the PDF with the elements
    elements = [watermark, date_paragraph, paragraph_message, table]

    # Set the coordinates for the elements
    watermark_x = 0  # Adjust the X-coordinate for the logo
    watermark_y = doc.height - 800  # Adjust the Y-coordinate for the logo
    date_x = doc.width - 800  # Adjust the X-coordinate for the date
    date_y = doc.height - 40  # Adjust the Y-coordinate for the date

    # Set the positions for the elements
    positions = [
        (watermark_x, watermark_y),
        (date_x, date_y),
        None,  # Placeholder for paragraph_message, as it doesn't have specific coordinates
        None,  # Placeholder for table, as it doesn't have specific coordinates
    ]

    # Add the positions to the elements
    elements += positions

    # Eliminar elementos que no son Flowable
    elements = [element for element in elements if isinstance(element, Flowable)]

    # Build the PDF with the elements
    doc.build(elements)

    # Create a response with the PDF file
    response = make_response(open("employees.pdf", "rb").read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=employees.pdf"
    return response


@apppdf.route("/generatePdfProductos")
def generate_pdf_productos():
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate("productos.pdf", pagesize=letter)

    # Fetch productos data
    productos = Producto.query.all()

    # Define data for the table
    listaProductos = [
        [
            "Código Producto",
            "Sabor",
            "Precio",
            "Cantidad",
            "Categoría ID",
            "Sucursal ID",
        ]
    ]

    for producto in productos:
        listaProductos.append(
            [
                producto.codigo_producto,
                producto.sabor,
                producto.precio,
                producto.cantidad,
                producto.categoria_id,
                producto.sucursal_id,
            ]
        )

    # Create the table
    table = Table(listaProductos)

    # Define the style for the table
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 16),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Apply the style to the table
    table.setStyle(style)

    # Create a paragraph object for the message
    message = "Listado de productos"

    # Create a Paragraph object for the message
    style_message = getSampleStyleSheet()["Normal"]
    style_message.alignment = 1  # Center alignment
    paragraph_message = Paragraph(message, style_message)

    # Create a Paragraph object for the watermark (logo)
    watermark = Image("static/image/NeveriaGlaciar.png", width=100, height=100)

    # Create a Paragraph object for the date
    date_paragraph = Paragraph(f"Created on: {current_date}", style_message)

    # Build the PDF with the elements
    elements = [watermark, date_paragraph, paragraph_message, table]

    # Set the coordinates for the elements
    watermark_x = 0  # Adjust the X-coordinate for the logo
    watermark_y = doc.height - 800  # Adjust the Y-coordinate for the logo
    date_x = doc.width - 800  # Adjust the X-coordinate for the date
    date_y = doc.height - 40  # Adjust the Y-coordinate for the date

    # Set the positions for the elements
    positions = [
        (watermark_x, watermark_y),
        (date_x, date_y),
        None,  # Placeholder for paragraph_message, as it doesn't have specific coordinates
        None,  # Placeholder for table, as it doesn't have specific coordinates
    ]

    # Add the positions to the elements
    elements += positions

    # Eliminar elementos que no son Flowable
    elements = [element for element in elements if isinstance(element, Flowable)]

    # Build the PDF with the elements
    doc.build(elements)

    # Create a response with the PDF file
    response = make_response(open("productos.pdf", "rb").read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=productos.pdf"
    return response


@apppdf.route("/generatePdfMateriaprimas")
def generate_pdf_materias_primas():
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate("materias_primas.pdf", pagesize=letter)

    # Fetch materias primas data
    materias_primas = Materia_Prima.query.all()

    # Define data for the table
    listaMateriasPrimas = [
        [
            "Código",
            "Nombre",
            "Precio",
            "Cantidad",
            "Sucursal ID",
        ]
    ]

    for materia_prima in materias_primas:
        listaMateriasPrimas.append(
            [
                materia_prima.codigo_materia,
                materia_prima.nombre_materia,
                materia_prima.precio,
                materia_prima.cantidad,
                materia_prima.sucursal_id,
            ]
        )

    # Create the table
    table = Table(listaMateriasPrimas)

    # Define the style for the table
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 16),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Apply the style to the table
    table.setStyle(style)

    # Create a paragraph object for the message
    message = "Listado de materias primas"

    # Create a Paragraph object for the message
    style_message = getSampleStyleSheet()["Normal"]
    style_message.alignment = 1  # Center alignment
    paragraph_message = Paragraph(message, style_message)

    # Create a Paragraph object for the watermark (logo)
    watermark = Image("static/image/NeveriaGlaciar.png", width=100, height=100)

    # Create a Paragraph object for the date
    date_paragraph = Paragraph(f"Created on: {current_date}", style_message)

    # Build the PDF with the elements
    elements = [watermark, date_paragraph, paragraph_message, table]

    # Set the coordinates for the elements
    watermark_x = 0  # Adjust the X-coordinate for the logo
    watermark_y = doc.height - 800  # Adjust the Y-coordinate for the logo
    date_x = doc.width - 800  # Adjust the X-coordinate for the date
    date_y = doc.height - 40  # Adjust the Y-coordinate for the date

    # Set the positions for the elements
    positions = [
        (watermark_x, watermark_y),
        (date_x, date_y),
        None,  # Placeholder for paragraph_message, as it doesn't have specific coordinates
        None,  # Placeholder for table, as it doesn't have specific coordinates
    ]

    # Add the positions to the elements
    elements += positions

    # Eliminar elementos que no son Flowable
    elements = [element for element in elements if isinstance(element, Flowable)]

    # Build the PDF with the elements
    doc.build(elements)

    # Create a response with the PDF file
    response = make_response(open("materias_primas.pdf", "rb").read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=materias_primas.pdf"
    return response


@apppdf.route("/generatePdfVentas")
def generate_pdf_ventas():
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate("ventas.pdf", pagesize=letter)

    # Fetch ventas data
    ventas = Venta.query.all()

    # Define data for the table
    listaVentas = [
        [
            "ID",
            "Fecha",
            "Monto",
            "Forma Pago",
            "Empleado",
            "Productos Vendidos",
        ]
    ]

    for venta in ventas:
        productos_vendidos = Producto_Vendido.query.filter_by(
            venta_id=venta.id_venta
        ).all()
        productos_vendidos_data = [
            f"{producto_vendido.codigo_producto} ({producto_vendido.cantidad})"
            for producto_vendido in productos_vendidos
        ]

        venta_data = [
            venta.id_venta,
            venta.fecha_venta.isoformat(),
            venta.monto,
            venta.forma_pago,
            venta.clave,
            ", ".join(productos_vendidos_data),
        ]

        listaVentas.append(venta_data)

    # Create the table
    table = Table(listaVentas)

    # Define the style for the table
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 16),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Apply the style to the table
    table.setStyle(style)

    # Create a paragraph object for the message
    message = "Listado de ventas"

    # Create a Paragraph object for the message
    style_message = getSampleStyleSheet()["Normal"]
    style_message.alignment = 1  # Center alignment
    paragraph_message = Paragraph(message, style_message)

    # Create a Paragraph object for the watermark (logo)
    watermark = Image("static/image/NeveriaGlaciar.png", width=100, height=100)

    # Create a Paragraph object for the date
    date_paragraph = Paragraph(f"Created on: {current_date}", style_message)

    # Build the PDF with the elements
    elements = [watermark, date_paragraph, paragraph_message, table]

    # Set the coordinates for the elements
    watermark_x = 0  # Adjust the X-coordinate for the logo
    watermark_y = doc.height - 800  # Adjust the Y-coordinate for the logo
    date_x = doc.width - 800  # Adjust the X-coordinate for the date
    date_y = doc.height - 40  # Adjust the Y-coordinate for the date

    # Set the positions for the elements
    positions = [
        (watermark_x, watermark_y),
        (date_x, date_y),
        None,  # Placeholder for paragraph_message, as it doesn't have specific coordinates
        None,  # Placeholder for table, as it doesn't have specific coordinates
    ]

    # Add the positions to the elements
    elements += positions

    # Eliminar elementos que no son Flowable
    elements = [element for element in elements if isinstance(element, Flowable)]

    # Build the PDF with the elements
    doc.build(elements)

    # Create a response with the PDF file
    response = make_response(open("ventas.pdf", "rb").read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=ventas.pdf"
    return response


@apppdf.route("/generatePdfEncargos")
def generate_pdf_encargos():
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate("encargos.pdf", pagesize=letter)

    # Fetch encargos data
    encargos = Encargo.query.all()

    # Define data for the table
    listaEncargos = [
        [
            "ID",
            "",
            "Cantidad",
            "Total",
            "Forma Pago",
            "Fecha",
            "Proveedor",
            "Sucursal",
        ]
    ]

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
        listaEncargos.append(encargo_data)

    # Create the table
    table = Table(listaEncargos)

    # Define the style for the table
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 16),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Apply the style to the table
    table.setStyle(style)

    # Create a paragraph object for the message
    message = "Listado de encargos"

    # Create a Paragraph object for the message
    style_message = getSampleStyleSheet()["Normal"]
    style_message.alignment = 1  # Center alignment
    paragraph_message = Paragraph(message, style_message)

    # Create a Paragraph object for the watermark (logo)
    watermark = Image("static/image/NeveriaGlaciar.png", width=100, height=100)

    # Create a Paragraph object for the date
    date_paragraph = Paragraph(f"Created on: {current_date}", style_message)

    # Build the PDF with the elements
    elements = [watermark, date_paragraph, paragraph_message, table]

    # Set the coordinates for the elements
    watermark_x = 0  # Adjust the X-coordinate for the logo
    watermark_y = doc.height - 800  # Adjust the Y-coordinate for the logo
    date_x = doc.width - 800  # Adjust the X-coordinate for the date
    date_y = doc.height - 40  # Adjust the Y-coordinate for the date

    # Set the positions for the elements
    positions = [
        (watermark_x, watermark_y),
        (date_x, date_y),
        None,  # Placeholder for paragraph_message, as it doesn't have specific coordinates
        None,  # Placeholder for table, as it doesn't have specific coordinates
    ]

    # Add the positions to the elements
    elements += positions

    # Eliminar elementos que no son Flowable
    elements = [element for element in elements if isinstance(element, Flowable)]

    # Build the PDF with the elements
    doc.build(elements)

    # Create a response with the PDF file
    response = make_response(open("encargos.pdf", "rb").read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=encargos.pdf"
    return response
