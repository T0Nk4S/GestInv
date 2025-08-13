from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox
)
import database


class MovimientoDialog(QDialog):
    def __init__(self, productos_map, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Movimiento de Inventario")
        self.productos_map = productos_map
        self.modelo = ""
        self.marca = ""
        self.proveedor = ""
        self.id_producto = None
        self.setup_ui()

    def obtener_info_producto(self, id_producto):
        import database
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT modelo, marca, id_proveedor FROM producto WHERE id = ?", (id_producto,))
        resultado = cursor.fetchone()
        if resultado:
            self.modelo = resultado[0]
            self.marca = resultado[1]
            proveedor_id = resultado[2]
            cursor.execute("SELECT nombre FROM proveedor WHERE id = ?", (proveedor_id,))
            prov = cursor.fetchone()
            self.proveedor = prov[0] if prov else "-"
        conn.close()

    def setup_ui(self):
        layout = QFormLayout()

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["salida", "devolucion"])

        self.producto_combo = QComboBox()
        # Obtener info extendida de cada producto
        import database
        conn = database.conectar()
        cursor = conn.cursor()
        for pid in self.productos_map.keys():
            cursor.execute("SELECT modelo, marca, id_proveedor FROM producto WHERE id = ?", (pid,))
            resultado = cursor.fetchone()
            if resultado:
                modelo = resultado[0]
                marca = resultado[1]
                proveedor_id = resultado[2]
                cursor.execute("SELECT nombre FROM proveedor WHERE id = ?", (proveedor_id,))
                prov = cursor.fetchone()
                proveedor = prov[0] if prov else "-"
                texto = f"{modelo} | {marca} | {proveedor}"
                self.producto_combo.addItem(texto, pid)
        conn.close()
        self.producto_combo.currentIndexChanged.connect(self.actualizar_info_producto)

        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setMinimum(1)
        self.cantidad_spin.setMaximum(10000)

        self.observacion_input = QLineEdit()

        # Campos informativos
        self.modelo_info = QLineEdit()
        self.modelo_info.setReadOnly(True)
        self.marca_info = QLineEdit()
        self.marca_info.setReadOnly(True)
        self.proveedor_info = QLineEdit()
        self.proveedor_info.setReadOnly(True)

        layout.addRow("Tipo de movimiento:", self.tipo_combo)
        layout.addRow("Producto:", self.producto_combo)
        layout.addRow("Modelo:", self.modelo_info)
        layout.addRow("Marca:", self.marca_info)
        layout.addRow("Proveedor:", self.proveedor_info)
        layout.addRow("Cantidad:", self.cantidad_spin)
        layout.addRow("Observación:", self.observacion_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)
        # Inicializar info producto
        self.actualizar_info_producto()

    def actualizar_info_producto(self):
        id_producto = self.producto_combo.currentData()
        if id_producto:
            self.obtener_info_producto(id_producto)
            self.modelo_info.setText(self.modelo)
            self.marca_info.setText(self.marca)
            self.proveedor_info.setText(self.proveedor)

    def get_data(self):
        return {
            "tipo": self.tipo_combo.currentText(),
            "id_producto": self.producto_combo.currentData(),
            "cantidad": self.cantidad_spin.value(),
            "observacion": self.observacion_input.text().strip(),
        }


class MovimientosTab(QWidget):
    def __init__(self):
        super().__init__()
        self.productos_map = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        botones_layout = QHBoxLayout()
        self.btn_agregar_movimiento = QPushButton("Agregar Movimiento")
        self.btn_agregar_movimiento.clicked.connect(self.mostrar_dialogo_movimiento)
        botones_layout.addWidget(self.btn_agregar_movimiento)

        layout.addLayout(botones_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "ID Movimiento", "Tipo", "Cantidad", "Producto", "Observación"
        ])
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.cargar_productos()
        self.cargar_movimientos()

    def cargar_productos(self):
        self.productos_map.clear()
        productos = database.listar_productos()
        for producto in productos:
            self.productos_map[producto[0]] = producto[1]

    def cargar_movimientos(self):
        self.cargar_productos()  # Actualiza el mapa de productos antes de mostrar movimientos
        self.tabla.setRowCount(0)
        movimientos = database.listar_movimientos()  # mov = (id_movimiento, tipo, cantidad, nombre_producto, observacion)
        for mov in movimientos:
            row_position = self.tabla.rowCount()
            self.tabla.insertRow(row_position)
            self.tabla.setItem(row_position, 0, QTableWidgetItem(str(mov[0])))
            self.tabla.setItem(row_position, 1, QTableWidgetItem(mov[1]))
            self.tabla.setItem(row_position, 2, QTableWidgetItem(str(mov[2])))
            self.tabla.setItem(row_position, 3, QTableWidgetItem(mov[3]))  # Cambiado para usar nombre_producto directamente
            self.tabla.setItem(row_position, 4, QTableWidgetItem(mov[4]))

    def mostrar_dialogo_movimiento(self):
        dialogo = MovimientoDialog(self.productos_map, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.get_data()
            try:
                conn = database.conectar()
                cursor = conn.cursor()
                cursor.execute("SELECT stock, modelo FROM producto WHERE id = ?", (datos["id_producto"],))
                resultado = cursor.fetchone()
                if not resultado:
                    raise Exception("Producto no encontrado")
                stock_actual = resultado[0]
                nombre_producto = resultado[1]

                if datos["tipo"] == "entrada":
                    nuevo_stock = stock_actual + datos["cantidad"]
                elif datos["tipo"] in ("salida", "devolucion"):
                    if stock_actual < datos["cantidad"]:
                        raise Exception("Stock insuficiente para la salida/devolución")
                    nuevo_stock = stock_actual - datos["cantidad"]
                else:
                    raise Exception("Tipo de movimiento inválido")

                cursor.execute("UPDATE producto SET stock = ? WHERE id = ?", (nuevo_stock, datos["id_producto"]))
                cursor.execute("""
                    INSERT INTO movimiento (tipo, cantidad, id_producto, nombre_producto, observacion)
                    VALUES (?, ?, ?, ?, ?)
                """, (datos["tipo"], datos["cantidad"], datos["id_producto"], nombre_producto, datos["observacion"]))

                conn.commit()
                conn.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
                return

            QMessageBox.information(self, "Éxito", "Movimiento registrado correctamente")
            self.cargar_productos()
            self.cargar_movimientos()  # <-- Forzar actualización inmediata
