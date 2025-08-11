from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import pyqtSignal
import database


class ProveedoresTab(QWidget):
    def cargar_proveedores(self):
        self.tabla.setRowCount(0)
        proveedores = database.listar_proveedores()
        for prov in proveedores:
            # prov: (id, nombre, telefono, email, direccion)
            row_position = self.tabla.rowCount()
            self.tabla.insertRow(row_position)
            self.tabla.setItem(row_position, 0, QTableWidgetItem(str(prov[0])))
            self.tabla.setItem(row_position, 1, QTableWidgetItem(prov[1]))
            self.tabla.setItem(row_position, 2, QTableWidgetItem(prov[2] if prov[2] else ""))
            self.tabla.setItem(row_position, 3, QTableWidgetItem(prov[3] if prov[3] else ""))
            self.tabla.setItem(row_position, 4, QTableWidgetItem(prov[4] if prov[4] else ""))
            # Si hay columna ciudad en la tabla, mostrarla, si no, dejar vacía
            if self.tabla.columnCount() > 5:
                self.tabla.setItem(row_position, 5, QTableWidgetItem(prov[5] if len(prov) > 5 and prov[5] else ""))
    def agregar_proveedor(self):
        nombre = self.nombre_input.text().strip()
        telefono = self.telefono_input.text().strip()
        email = self.email_input.text().strip()
        direccion = self.direccion_input.text().strip()
        ciudad = self.ciudad_input.text().strip()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del proveedor es obligatorio.")
            return

        database.agregar_proveedor(nombre, telefono, email, direccion, ciudad)
        self.cargar_proveedores()
        self.nombre_input.clear()
        self.telefono_input.clear()
        self.email_input.clear()
        self.direccion_input.clear()
        self.ciudad_input.clear()
        QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente.")
        self.proveedor_agregado.emit()

    proveedor_agregado = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre proveedor")
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección")
        self.ciudad_input = QLineEdit()
        self.ciudad_input.setPlaceholderText("Ciudad")

        form_layout.addWidget(self.nombre_input)
        form_layout.addWidget(self.telefono_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.direccion_input)
        form_layout.addWidget(self.ciudad_input)

        layout.addLayout(form_layout)



        btns_layout = QHBoxLayout()
        btn_add = QPushButton("Agregar proveedor")
        btn_add.clicked.connect(self.agregar_proveedor)
        btns_layout.addWidget(btn_add)

        btn_delete = QPushButton("Eliminar proveedor seleccionado")
        btn_delete.clicked.connect(self.eliminar_proveedor_seleccionado)
        btns_layout.addWidget(btn_delete)

        layout.addLayout(btns_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Teléfono", "Email", "Dirección", "Ciudad"
        ])
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_proveedores()

    def eliminar_proveedor_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un proveedor para eliminar.")
            return
        id_proveedor = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        confirm = QMessageBox.question(self, "Confirmar eliminación", f"¿Seguro que deseas eliminar el proveedor '{nombre}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            import database
            database.eliminar_proveedor(id_proveedor)
            self.cargar_proveedores()
            self.proveedor_agregado.emit()
