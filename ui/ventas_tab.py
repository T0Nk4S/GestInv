from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
import database

class VentasTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "ID Venta", "Fecha", "Nombre Cliente", "Apellido Cliente", "Teléfono", "Email", "CI/NIT",
            "Producto", "Marca", "Cantidad", "Total (Bs.)"
        ])
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)
        self.setLayout(layout)

        self.cargar_ventas()

    def cargar_ventas(self):
        ventas = database.listar_ventas()
        self.tabla.setRowCount(len(ventas))
        for row, venta in enumerate(ventas):
            # venta = (id, fecha, nombre_cliente, apellido_cliente, telefono, email, ci_nit, modelo, marca, cantidad, total)
            for col, valor in enumerate(venta):
                self.tabla.setItem(row, col, QTableWidgetItem(str(valor)))

    def refrescar(self):
        self.cargar_ventas()
