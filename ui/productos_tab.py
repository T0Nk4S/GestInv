import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QInputDialog,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox
)
import database


class ProductoDialog(QDialog):
    def __init__(self, proveedores_map, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Nuevo Producto")
        self.proveedores_map = proveedores_map
        self.categorias = ["Monitores", "Teclados", "Procesadores", "Mouse", "Laptops", "Otros"]
        self.setup_ui()

    def setup_ui(self):
        from PyQt6.QtWidgets import QPushButton
        self.modelo_input = QLineEdit()
        self.marca_input = QLineEdit()
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(self.categorias)
        self.descripcion_input = QLineEdit()
        self.precio_input = QLineEdit()
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(1000000)
    # El campo de número de serie y escaneo solo se usan en el flujo uno por uno, no aquí
        self.proveedor_combo = QComboBox()
        for pid, nombre in self.proveedores_map.items():
            self.proveedor_combo.addItem(nombre, pid)

        layout = QFormLayout()
        layout.addRow("Modelo:", self.modelo_input)
        layout.addRow("Marca:", self.marca_input)
        layout.addRow("Categoría:", self.categoria_combo)
        layout.addRow("Descripción:", self.descripcion_input)
        layout.addRow("Precio:", self.precio_input)
        layout.addRow("Stock:", self.stock_input)
    # No mostrar campo de número de serie aquí
        layout.addRow("Proveedor:", self.proveedor_combo)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def escanear_codigo_barras(self):
        import cv2
        from pyzbar.pyzbar import decode
        cap = cv2.VideoCapture(0)
        codigo = None
        while True:
            ret, frame = cap.read()
            for barcode in decode(frame):
                codigo = barcode.data.decode('utf-8')
                cv2.rectangle(frame, (barcode.rect.left, barcode.rect.top),
                              (barcode.rect.left + barcode.rect.width, barcode.rect.top + barcode.rect.height),
                              (0, 255, 0), 2)
                cv2.putText(frame, codigo, (barcode.rect.left, barcode.rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                self.numero_serie_input.setText(codigo)
                cap.release()
                cv2.destroyAllWindows()
                return
            cv2.imshow('Escaneo de código de barras', frame)
            if cv2.waitKey(1) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def get_data(self):
        return {
            "modelo": self.modelo_input.text().strip(),
            "marca": self.marca_input.text().strip(),
            "categoria": self.categoria_combo.currentText(),
            "descripcion": self.descripcion_input.text().strip(),
            "precio": self.precio_input.text().strip(),
            "stock": self.stock_input.value(),
            "proveedor_id": self.proveedor_combo.currentData(),
        }


class VentaDialog(QDialog):
    def __init__(self, id_producto, nombre_producto, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Venta")
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.modelo = ""
        self.marca = ""
        self.proveedor = ""
        self.obtener_info_producto()
        self.setup_ui()

    def obtener_info_producto(self):
        import database
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT modelo, marca, id_proveedor FROM producto WHERE id = ?", (self.id_producto,))
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

        self.nombre_cliente_input = QLineEdit()
        self.apellido_cliente_input = QLineEdit()
        self.telefono_cliente_input = QLineEdit()
        self.email_cliente_input = QLineEdit()
        self.ci_nit_cliente_input = QLineEdit()
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setMinimum(1)
        self.cantidad_spin.setMaximum(10000)

        self.modelo_label = QTableWidgetItem(self.modelo)
        self.marca_label = QTableWidgetItem(self.marca)
        self.proveedor_label = QTableWidgetItem(self.proveedor)

        layout.addRow("Modelo:", QLineEdit(self.modelo))
        layout.itemAt(layout.rowCount()-1).widget().setReadOnly(True)
        layout.addRow("Marca:", QLineEdit(self.marca))
        layout.itemAt(layout.rowCount()-1).widget().setReadOnly(True)
        layout.addRow("Proveedor:", QLineEdit(self.proveedor))
        layout.itemAt(layout.rowCount()-1).widget().setReadOnly(True)

        layout.addRow("Nombre Cliente:", self.nombre_cliente_input)
        layout.addRow("Apellido Cliente:", self.apellido_cliente_input)
        layout.addRow("Teléfono:", self.telefono_cliente_input)
        layout.addRow("Email:", self.email_cliente_input)
        layout.addRow("CI/NIT:", self.ci_nit_cliente_input)
        layout.addRow(f"Cantidad a vender ({self.nombre_producto}):", self.cantidad_spin)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_data(self):
        return {
            "nombre_cliente": self.nombre_cliente_input.text().strip(),
            "apellido_cliente": self.apellido_cliente_input.text().strip(),
            "telefono_cliente": self.telefono_cliente_input.text().strip(),
            "email_cliente": self.email_cliente_input.text().strip(),
            "ci_nit_cliente": self.ci_nit_cliente_input.text().strip(),
            "cantidad": self.cantidad_spin.value(),
        }


class MovimientoDialog(QDialog):
    def __init__(self, productos_map, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Movimiento de Inventario")
        self.productos_map = productos_map
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["entrada", "salida", "devolucion"])

        self.producto_combo = QComboBox()
        for pid, nombre in self.productos_map.items():
            self.producto_combo.addItem(nombre, pid)

        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setMinimum(1)
        self.cantidad_spin.setMaximum(10000)

        self.observacion_input = QLineEdit()

        layout.addRow("Tipo de movimiento:", self.tipo_combo)
        layout.addRow("Producto:", self.producto_combo)
        layout.addRow("Cantidad:", self.cantidad_spin)
        layout.addRow("Observación:", self.observacion_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_data(self):
        return {
            "tipo": self.tipo_combo.currentText(),
            "id_producto": self.producto_combo.currentData(),
            "cantidad": self.cantidad_spin.value(),
            "observacion": self.observacion_input.text().strip(),
        }


class ProductosTab(QWidget):
    producto_enviado = pyqtSignal(dict)  # Señal para enviar producto a cotizar
    venta_realizada = pyqtSignal()
    producto_cambiado = pyqtSignal()  # Señal para actualizar movimientos

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        botones_layout = QHBoxLayout()

        self.btn_add = QPushButton("Agregar Producto")
        self.btn_add.clicked.connect(self.mostrar_dialogo_agregar)
        botones_layout.addWidget(self.btn_add)

        self.btn_vender = QPushButton("Vender producto seleccionado")
        self.btn_vender.clicked.connect(self.mostrar_dialogo_venta)
        botones_layout.addWidget(self.btn_vender)

        self.btn_eliminar = QPushButton("Eliminar producto seleccionado")
        self.btn_eliminar.clicked.connect(self.eliminar_producto_seleccionado)
        botones_layout.addWidget(self.btn_eliminar)

        self.btn_movimiento = QPushButton("Registrar Movimiento")
        self.btn_movimiento.clicked.connect(self.mostrar_dialogo_movimiento)
        botones_layout.addWidget(self.btn_movimiento)

        self.btn_cotizar = QPushButton("Cotizar producto seleccionado")
        self.btn_cotizar.clicked.connect(self.mostrar_dialogo_cotizar)
        botones_layout.addWidget(self.btn_cotizar)

        self.btn_exportar_excel = QPushButton("Exportar productos a Excel")
        self.btn_exportar_excel.clicked.connect(self.exportar_excel)
        botones_layout.addWidget(self.btn_exportar_excel)

        layout.addLayout(botones_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Modelo", "Marca", "Categoría", "Descripción", "Precio", "Stock", "Proveedor"
        ])
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.cargar_proveedores()
        self.cargar_productos()

    def exportar_excel(self):
        import pandas as pd
        from PyQt6.QtWidgets import QFileDialog
        import os
        productos = database.listar_productos()
        proveedores = database.listar_proveedores()
        proveedores_map = {p[0]: p[1] for p in proveedores}
        data = []
        for p in productos:
            data.append({
                "ID": p[0],
                "Modelo": p[1],
                "Marca": p[2],
                "Categoría": p[3],
                "Descripción": p[4],
                "Precio": p[5],
                "Stock": p[6],
                "N° Serie": p[7],
                "Proveedor": proveedores_map.get(p[8], "-")
            })
        df = pd.DataFrame(data)
        df = df.sort_values(by=["Categoría", "Marca", "Modelo"])
        categorias = df["Categoría"].unique()
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        ruta_defecto = os.path.join(escritorio, "productos.xlsx")
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", ruta_defecto, "Archivos Excel (*.xlsx)")
        if not file_path:
            return
        with pd.ExcelWriter(file_path) as writer:
            for cat in categorias:
                df_cat = df[df["Categoría"] == cat]
                df_cat.to_excel(writer, sheet_name=cat, index=False)
        QMessageBox.information(self, "Éxito", f"Productos exportados a {file_path}")




    def cargar_proveedores(self):
        self.proveedores_map = {}
        proveedores = database.listar_proveedores()
        for prov in proveedores:
            self.proveedores_map[prov[0]] = prov[1]

    def cargar_productos(self):
        self.tabla.setRowCount(0)
        productos = database.listar_productos()
        for producto in productos:
            row_position = self.tabla.rowCount()
            self.tabla.insertRow(row_position)
            self.tabla.setItem(row_position, 0, QTableWidgetItem(str(producto[0])))
            self.tabla.setItem(row_position, 1, QTableWidgetItem(producto[1]))  # modelo
            self.tabla.setItem(row_position, 2, QTableWidgetItem(producto[2]))  # marca
            self.tabla.setItem(row_position, 3, QTableWidgetItem(producto[3]))  # categoria
            self.tabla.setItem(row_position, 4, QTableWidgetItem(producto[4]))  # descripcion
            self.tabla.setItem(row_position, 5, QTableWidgetItem(str(producto[5])))  # precio
            self.tabla.setItem(row_position, 6, QTableWidgetItem(str(producto[6])))  # stock
            proveedor_nombre = self.proveedores_map.get(producto[7], "-")
            self.tabla.setItem(row_position, 7, QTableWidgetItem(proveedor_nombre))

    def mostrar_dialogo_agregar(self):
        from PyQt6.QtWidgets import QDialog
        dialogo = ProductoDialog(self.proveedores_map, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos = dialogo.get_data()
                modelo = datos["modelo"]
                marca = datos["marca"]
                categoria = datos["categoria"]
                descripcion = datos["descripcion"]
                precio_text = datos["precio"]
                stock = datos["stock"]
                proveedor_id = datos["proveedor_id"]

                if not modelo or not precio_text:
                    QMessageBox.warning(self, "Error", "Debe completar al menos modelo y precio")
                    return
                try:
                    precio = float(precio_text)
                except ValueError:
                    QMessageBox.warning(self, "Error", "Precio debe ser un número válido")
                    return

                # Diálogo uno por uno para números de serie
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton
                numero_series = []
                for i in range(stock):
                    serie_dialog = QDialog(self)
                    serie_dialog.setWindowTitle(f"Número de serie para unidad {i+1} de {stock}")
                    layout = QVBoxLayout()
                    label = QLabel(f"Ingresa o escanea el número de serie para la unidad {i+1}:")
                    serie_input = QLineEdit()
                    btn_scan = QPushButton("Escanear código de barras")
                    def escanear():
                        import cv2
                        from pyzbar.pyzbar import decode
                        cap = cv2.VideoCapture(0)
                        codigo = None
                        while True:
                            ret, frame = cap.read()
                            for barcode in decode(frame):
                                codigo = barcode.data.decode('utf-8')
                                cv2.rectangle(frame, (barcode.rect.left, barcode.rect.top),
                                            (barcode.rect.left + barcode.rect.width, barcode.rect.top + barcode.rect.height),
                                            (0, 255, 0), 2)
                                cv2.putText(frame, codigo, (barcode.rect.left, barcode.rect.top - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                                serie_input.setText(codigo)
                                cap.release()
                                cv2.destroyAllWindows()
                                return
                            cv2.imshow('Escaneo de código de barras', frame)
                            if cv2.waitKey(1) == 27:
                                break
                        cap.release()
                        cv2.destroyAllWindows()
                    btn_scan.clicked.connect(escanear)
                    layout.addWidget(label)
                    layout.addWidget(serie_input)
                    layout.addWidget(btn_scan)
                    btn_ok = QPushButton("Aceptar")
                    btn_ok.clicked.connect(serie_dialog.accept)
                    layout.addWidget(btn_ok)
                    serie_dialog.setLayout(layout)
                    if serie_dialog.exec() == QDialog.DialogCode.Accepted:
                        numero_series.append(serie_input.text().strip())
                    else:
                        QMessageBox.warning(self, "Error", "Debes ingresar el número de serie para cada unidad.")
                        return

                # Registrar cada producto con su número de serie
                for numero_serie in numero_series:
                    database.agregar_producto(modelo, marca, categoria, descripcion, precio, 1, numero_serie, proveedor_id)
                    productos = database.listar_productos()
                    id_producto = productos[-1][0] if productos else None
                    if id_producto:
                        database.agregar_movimiento("entrada", 1, id_producto, "Ingreso por nuevo producto")
                if self.parent_window and hasattr(self.parent_window, "movimientos_tab"):
                    self.parent_window.movimientos_tab.cargar_movimientos()
                    self.parent_window.movimientos_tab.update()
                self.cargar_productos()
                self.producto_cambiado.emit()
                QMessageBox.information(self, "Éxito", "Productos agregados correctamente")

    def eliminar_producto_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un producto para eliminar.")
            return
        id_producto = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        confirm = QMessageBox.question(self, "Confirmar eliminación", f"¿Seguro que deseas eliminar el producto '{nombre}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            database.eliminar_producto(id_producto)
            self.cargar_productos()
            self.producto_cambiado.emit()

    def mostrar_dialogo_venta(self):
        seleccion = self.tabla.currentRow()
        if seleccion < 0:
            QMessageBox.warning(self, "Error", "Debe seleccionar un producto para vender")
            return

        id_producto = int(self.tabla.item(seleccion, 0).text())
        nombre_producto = self.tabla.item(seleccion, 1).text()

        dialogo = VentaDialog(id_producto, nombre_producto, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.get_data()

            if not datos["nombre_cliente"] or not datos["apellido_cliente"]:
                QMessageBox.warning(self, "Error", "Debe ingresar nombre y apellido del cliente")
                return

            try:
                database.registrar_venta(
                    datos["nombre_cliente"],
                    datos["apellido_cliente"],
                    datos["telefono_cliente"],
                    datos["email_cliente"],
                    datos["ci_nit_cliente"],
                    id_producto,
                    datos["cantidad"]
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
                return

            QMessageBox.information(self, "Éxito", f"Venta de {datos['cantidad']} unidad(es) de '{nombre_producto}' registrada correctamente")
            self.cargar_productos()
            self.venta_realizada.emit()
            self.producto_cambiado.emit()

    def mostrar_dialogo_movimiento(self):
        # Obtener el producto seleccionado en la tabla
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un producto para registrar movimiento.")
            return
        id_producto = int(self.tabla.item(fila, 0).text())
        modelo = self.tabla.item(fila, 1).text()
        marca = self.tabla.item(fila, 2).text()
        proveedor = self.tabla.item(fila, 7).text()

        # Crear diálogo personalizado
        from PyQt6.QtWidgets import QDialog, QFormLayout, QComboBox, QSpinBox, QLineEdit, QDialogButtonBox
        class MovimientoDialogCustom(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Registrar Movimiento de Inventario")
                self.tipo_combo = QComboBox()
                self.tipo_combo.addItems(["entrada", "salida", "devolucion"])
                self.cantidad_spin = QSpinBox()
                self.cantidad_spin.setMinimum(1)
                self.cantidad_spin.setMaximum(10000)
                self.observacion_input = QLineEdit()
                self.modelo_info = QLineEdit(modelo)
                self.modelo_info.setReadOnly(True)
                self.marca_info = QLineEdit(marca)
                self.marca_info.setReadOnly(True)
                self.proveedor_info = QLineEdit(proveedor)
                self.proveedor_info.setReadOnly(True)
                layout = QFormLayout()
                layout.addRow("Tipo de movimiento:", self.tipo_combo)
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
            def get_data(self):
                return {
                    "tipo": self.tipo_combo.currentText(),
                    "cantidad": self.cantidad_spin.value(),
                    "observacion": self.observacion_input.text().strip(),
                }

        dialogo = MovimientoDialogCustom(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.get_data()
            try:
                conn = database.conectar()
                cursor = conn.cursor()
                cursor.execute("SELECT stock FROM producto WHERE id = ?", (id_producto,))
                resultado = cursor.fetchone()
                if not resultado:
                    raise Exception("Producto no encontrado")
                stock_actual = resultado[0]
                if datos["tipo"] == "entrada" or datos["tipo"] == "devolucion":
                    nuevo_stock = stock_actual + datos["cantidad"]
                elif datos["tipo"] == "salida":
                    if stock_actual < datos["cantidad"]:
                        raise Exception("Stock insuficiente para la salida")
                    nuevo_stock = stock_actual - datos["cantidad"]
                else:
                    raise Exception("Tipo de movimiento inválido")
                cursor.execute("UPDATE producto SET stock = ? WHERE id = ?", (nuevo_stock, id_producto))
                cursor.execute("SELECT modelo FROM producto WHERE id = ?", (id_producto,))
                modelo_row = cursor.fetchone()
                modelo_db = modelo_row[0] if modelo_row else modelo
                cursor.execute("""
                    INSERT INTO movimiento (tipo, cantidad, id_producto, nombre_producto, observacion)
                    VALUES (?, ?, ?, ?, ?)
                """, (datos["tipo"], datos["cantidad"], id_producto, modelo_db, datos["observacion"]))
                conn.commit()
                conn.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
                return
            QMessageBox.information(self, "Éxito", "Movimiento registrado correctamente")
            self.cargar_productos()
            if self.parent_window and hasattr(self.parent_window, "movimientos_tab"):
                self.parent_window.movimientos_tab.cargar_movimientos()
                self.parent_window.movimientos_tab.update()
            self.venta_realizada.emit()

    def mostrar_dialogo_cotizar(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Debe seleccionar un producto para cotizar")
            return
        
        try:
            stock = int(float(self.tabla.item(fila, 6).text()))
        except Exception:
            stock = 0
        if stock == 0:
            QMessageBox.warning(self, "Error", "El producto no tiene stock disponible")
            return

        cantidad, ok = QInputDialog.getInt(self, "Cantidad a Cotizar", 
                                           f"Ingrese cantidad a cotizar (stock disponible: {stock}):", 
                                           1, 1, stock)
        if not ok:
            return

        try:
            precio = float(self.tabla.item(fila, 5).text())
        except Exception:
            QMessageBox.warning(self, "Error", "El precio del producto no es válido.")
            return
        producto = {
            "id": int(self.tabla.item(fila, 0).text()),
            "modelo": self.tabla.item(fila, 1).text(),
            "marca": self.tabla.item(fila, 2).text(),
            "categoria": self.tabla.item(fila, 3).text(),
            "descripcion": self.tabla.item(fila, 4).text(),
            "precio": precio,
            "stock": stock,
            "proveedor": self.tabla.item(fila, 7).text(),
            "cantidad_cotizada": cantidad
        }
        self.producto_enviado.emit(producto)