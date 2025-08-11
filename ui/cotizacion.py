from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QLabel
)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime


class CotizacionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Modelo", "Marca", "Categoría", "Descripción", "Precio", "Cantidad"
        ])
        layout.addWidget(self.tabla)

        btn_pdf = QPushButton("Generar PDF")
        btn_pdf.clicked.connect(self.exportar_pdf)
        layout.addWidget(btn_pdf)

        self.total_label = QLabel("Total: $0.00")
        layout.addWidget(self.total_label)

        self.setLayout(layout)

    def agregar_producto(self, producto):
        fila_pos = self.tabla.rowCount()
        self.tabla.insertRow(fila_pos)
        self.tabla.setItem(fila_pos, 0, QTableWidgetItem(str(producto["id"])))
        self.tabla.setItem(fila_pos, 1, QTableWidgetItem(producto["modelo"]))
        self.tabla.setItem(fila_pos, 2, QTableWidgetItem(producto.get("marca", "")))
        self.tabla.setItem(fila_pos, 3, QTableWidgetItem(producto["categoria"]))
        self.tabla.setItem(fila_pos, 4, QTableWidgetItem(producto["descripcion"]))
        self.tabla.setItem(fila_pos, 5, QTableWidgetItem(f"{producto['precio']:.2f}"))
        self.tabla.setItem(fila_pos, 6, QTableWidgetItem(str(producto.get("cantidad_cotizada", 1))))
        self.actualizar_total()

    def actualizar_total(self):
        total = 0.0
        for row in range(self.tabla.rowCount()):
            try:
                precio = float(self.tabla.item(row, 4).text())
                cantidad = int(self.tabla.item(row, 5).text())
                total += precio * cantidad
            except (ValueError, AttributeError):
                pass
        self.total_label.setText(f"Total: ${total:.2f}")

    def exportar_pdf(self):
        if self.tabla.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No hay productos en la cotización para exportar.")
            return

        import os
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = os.path.join(desktop, "cotizacion.pdf")

        try:
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            margen_izq = 0.7 * inch
            margen_der = width - 0.7 * inch
            margen_sup = height - 0.7 * inch
            margen_inf = 0.7 * inch

            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, margen_sup, "Cotización de Productos")
            c.setFont("Helvetica", 10)
            fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            c.drawRightString(margen_der, margen_sup - 20, f"Fecha: {fecha_str}")

            # Encabezados tabla
            c.setFont("Helvetica-Bold", 12)
            y = margen_sup - 50
            col_x = [
                margen_izq,
                margen_izq + 0.6*inch,
                margen_izq + 1.5*inch,
                margen_izq + 2.5*inch,
                margen_izq + 4.0*inch,
                margen_izq + 5.0*inch,
                margen_izq + 5.7*inch
            ]
            headers = ["ID", "Modelo", "Marca", "Categoría", "Descripción", "Precio", "Cantidad"]
            for i, header in enumerate(headers):
                c.drawString(col_x[i], y, header)

            y -= 18
            c.setFont("Helvetica", 10)

            for row in range(self.tabla.rowCount()):
                id_producto = self.tabla.item(row, 0).text()
                modelo = self.tabla.item(row, 1).text()
                marca = self.tabla.item(row, 2).text()
                categoria = self.tabla.item(row, 3).text()
                descripcion = self.tabla.item(row, 4).text()
                precio_text = self.tabla.item(row, 5).text()
                cantidad_text = self.tabla.item(row, 6).text()

                try:
                    precio = float(precio_text)
                    cantidad = int(cantidad_text)
                    subtotal = precio * cantidad
                except ValueError:
                    precio = 0
                    cantidad = 0
                    subtotal = 0

                if y < margen_inf + 30:
                    c.showPage()
                    y = margen_sup - 50
                    c.setFont("Helvetica-Bold", 12)
                    for i, header in enumerate(headers):
                        c.drawString(col_x[i], y, header)
                    y -= 18
                    c.setFont("Helvetica", 10)

                c.drawString(col_x[0], y, id_producto)
                c.drawString(col_x[1], y, modelo)
                c.drawString(col_x[2], y, marca)
                c.drawString(col_x[3], y, categoria)
                c.drawString(col_x[4], y, descripcion)
                c.drawRightString(col_x[5]+40, y, f"${precio:.2f}")
                c.drawRightString(col_x[6]+20, y, cantidad_text)
                y -= 16

            y -= 25
            c.setFont("Helvetica-Bold", 13)
            c.drawRightString(margen_der, y, self.total_label.text())

            c.save()
            QMessageBox.information(self, "Éxito", f"Cotización exportada a PDF:\n{filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo exportar PDF:\n{str(e)}")
