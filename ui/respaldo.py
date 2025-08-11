from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
import os
import shutil
from datetime import datetime

class RespaldoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.password = "admin123"  # Puedes cambiarla
        self.codigo = "987654"      # Puedes cambiarlo
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Contraseña:", self.pass_input)

        self.code_input = QLineEdit()
        form.addRow("Código de seguridad:", self.code_input)

        self.btn_backup = QPushButton("Eliminar y respaldar base de datos")
        self.btn_backup.clicked.connect(self.respaldar_bd)
        layout.addLayout(form)
        layout.addWidget(self.btn_backup)
        self.setLayout(layout)

    def respaldar_bd(self):
        if self.pass_input.text() != self.password or self.code_input.text() != self.codigo:
            QMessageBox.warning(self, "Error", "Contraseña o código incorrecto.")
            return
        try:
            appdata = os.path.join(os.environ.get('APPDATA'), 'GestionInventario')
            db_path = os.path.join(appdata, "data", "tienda.db")
            backup_dir = os.path.join(appdata, "backup")
            os.makedirs(backup_dir, exist_ok=True)
            fecha = datetime.now().strftime("%Y-%m-%d _ %H-%M-%S")
            backup_path = os.path.join(backup_dir, f"tienda_backup_{fecha}.db")
            shutil.copy2(db_path, backup_path)
            os.remove(db_path)
            QMessageBox.information(self, "Respaldo", f"Respaldo creado y base de datos eliminada:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo respaldar/eliminar la base de datos:\n{str(e)}")
