from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from ui.productos_tab import ProductosTab
from ui.proveedores_tab import ProveedoresTab
from ui.ventas_tab import VentasTab
from ui.movimientos_tab import MovimientosTab
from ui.cotizacion import CotizacionTab
from ui.respaldo import RespaldoTab
import database
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tienda de Computadoras - Bolivia")
        self.resize(1200, 600)

        # Tab widget
        self.tabs = QTabWidget()

        # Crear pestañas
        self.productos_tab = ProductosTab()
        self.ventas_tab = VentasTab()
        self.proveedores_tab = ProveedoresTab()
        self.movimientos_tab = MovimientosTab()
        self.cotizacion_tab = CotizacionTab()
        self.respaldo_tab = RespaldoTab()

        # Añadir pestañas
        self.tabs.addTab(self.productos_tab, "Productos")
        self.tabs.addTab(self.proveedores_tab, "Proveedores")
        self.tabs.addTab(self.ventas_tab, "Ventas")
        self.tabs.addTab(self.movimientos_tab, "Movimientos")
        self.tabs.addTab(self.cotizacion_tab, "Cotización")
        self.tabs.addTab(self.respaldo_tab, "Respaldo")

        self.setCentralWidget(self.tabs)

        # Conectar señal para actualizar ventas al hacer una venta
        self.productos_tab.venta_realizada.connect(self.ventas_tab.refrescar)

        # Conectar señal para actualizar proveedores en ProductosTab
        self.proveedores_tab.proveedor_agregado.connect(self.productos_tab.cargar_proveedores)

        # Conectar señal para enviar producto seleccionado a CotizacionTab
        self.productos_tab.producto_enviado.connect(self.cotizacion_tab.agregar_producto)

        # Conectar señal para actualizar movimientos
        self.productos_tab.producto_cambiado.connect(self.movimientos_tab.cargar_movimientos)


def main():
    database.crear_tablas()
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
