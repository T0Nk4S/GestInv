# --- Eliminar Producto ---
def eliminar_producto(id_producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM producto WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()

# --- Eliminar Proveedor ---
def eliminar_proveedor(id_proveedor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedor WHERE id = ?", (id_proveedor,))
    conn.commit()
    conn.close()
import sqlite3

import os
appdata = os.path.join(os.environ.get('APPDATA'), 'GestionInventario')
data_dir = os.path.join(appdata, 'data')
os.makedirs(data_dir, exist_ok=True)
DB_NAME = os.path.join(data_dir, 'tienda.db')

def conectar():
    return sqlite3.connect(DB_NAME)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proveedor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        ciudad TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        marca TEXT,
        categoria TEXT,
        descripcion TEXT,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        numero_serie TEXT,
        id_proveedor INTEGER,
        FOREIGN KEY(id_proveedor) REFERENCES proveedor(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        nombre_cliente TEXT NOT NULL,
        apellido_cliente TEXT NOT NULL,
        telefono_cliente TEXT,
        email_cliente TEXT,
        ci_nit_cliente TEXT,
        id_producto INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY(id_producto) REFERENCES producto(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        tipo TEXT NOT NULL, -- entrada, salida, devolucion
        cantidad INTEGER NOT NULL,
        id_producto INTEGER NOT NULL,
        nombre_producto TEXT,
        observacion TEXT,
        FOREIGN KEY(id_producto) REFERENCES producto(id)
    )
    """)

    conn.commit()
    conn.close()

# --- Proveedores ---

def listar_proveedores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, email, direccion, ciudad FROM proveedor")
    proveedores = cursor.fetchall()
    conn.close()
    return proveedores

def agregar_proveedor(nombre, telefono, email, direccion, ciudad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO proveedor (nombre, telefono, email, direccion, ciudad) VALUES (?, ?, ?, ?, ?)",
                   (nombre, telefono, email, direccion, ciudad))
    conn.commit()
    conn.close()

# --- Productos ---

def listar_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, modelo, marca, categoria, descripcion, precio, stock, numero_serie, id_proveedor FROM producto")
    productos = cursor.fetchall()
    conn.close()
    return productos

def agregar_producto(modelo, marca, categoria, descripcion, precio, stock, numero_serie, id_proveedor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO producto (modelo, marca, categoria, descripcion, precio, stock, numero_serie, id_proveedor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (modelo, marca, categoria, descripcion, precio, stock, numero_serie, id_proveedor))
    conn.commit()
    conn.close()

# --- Ventas ---

def registrar_venta(nombre_cliente, apellido_cliente, telefono_cliente, email_cliente, ci_nit_cliente,
                    id_producto, cantidad):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT precio, stock FROM producto WHERE id = ?", (id_producto,))
    resultado = cursor.fetchone()
    if not resultado:
        conn.close()
        raise Exception("Producto no encontrado")
    precio, stock_actual = resultado

    if stock_actual < cantidad:
        conn.close()
        raise Exception("Stock insuficiente para la venta")

    total = precio * cantidad

    cursor.execute("""
        INSERT INTO venta (
            nombre_cliente, apellido_cliente, telefono_cliente, email_cliente, ci_nit_cliente,
            id_producto, cantidad, total
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre_cliente, apellido_cliente, telefono_cliente, email_cliente, ci_nit_cliente,
          id_producto, cantidad, total))

    nuevo_stock = stock_actual - cantidad
    cursor.execute("UPDATE producto SET stock = ? WHERE id = ?", (nuevo_stock, id_producto))

    cursor.execute("SELECT modelo FROM producto WHERE id = ?", (id_producto,))
    resultado = cursor.fetchone()
    nombre_producto = resultado[0] if resultado else "Desconocido"
    cursor.execute("""
        INSERT INTO movimiento (tipo, cantidad, id_producto, nombre_producto, observacion)
        VALUES (?, ?, ?, ?, ?)
    """, ("salida", cantidad, id_producto, nombre_producto, "Venta"))

    conn.commit()
    conn.close()

def listar_ventas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.id, v.fecha, v.nombre_cliente, v.apellido_cliente, v.telefono_cliente, 
               v.email_cliente, v.ci_nit_cliente, p.modelo, p.marca, v.cantidad, v.total
        FROM venta v
        JOIN producto p ON v.id_producto = p.id
        ORDER BY v.fecha DESC
    """)
    ventas = cursor.fetchall()
    conn.close()
    return ventas

# --- Movimientos ---

def listar_movimientos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.tipo, m.cantidad, m.nombre_producto, m.observacion
        FROM movimiento m
        ORDER BY m.fecha DESC
    """)
    movimientos = cursor.fetchall()
    conn.close()
    return movimientos

def agregar_movimiento(tipo, cantidad, id_producto, observacion):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT modelo FROM producto WHERE id = ?", (id_producto,))
    resultado = cursor.fetchone()
    nombre_producto = resultado[0] if resultado else "Desconocido"
    cursor.execute("""
        INSERT INTO movimiento (tipo, cantidad, id_producto, nombre_producto, observacion)
        VALUES (?, ?, ?, ?, ?)
    """, (tipo, cantidad, id_producto, nombre_producto, observacion))
    conn.commit()
    conn.close()
