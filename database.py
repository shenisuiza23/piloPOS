import sqlite3
from datetime import datetime
from config import DB_NAME

def get_connection():
    return sqlite3.connect(DB_NAME)

def inicializar_bd():
    conn = get_connection()
    c = conn.cursor()

    # Tabla Productos
    c.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT DEFAULT 'Otros',
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 50,
            tipo TEXT DEFAULT 'Gral'
        )
    """)

    # Tabla Ventas Cabecera
    c.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlativo TEXT UNIQUE NOT NULL,
            total REAL NOT NULL,
            metodo TEXT NOT NULL,
            monto_efectivo REAL DEFAULT 0,
            monto_digital REAL DEFAULT 0,
            fecha TEXT NOT NULL
        )
    """)

    # Tabla Detalle Venta (Normalizada)
    c.execute("""
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    """)

    # Tabla Control de Caja
    c.execute("""
        CREATE TABLE IF NOT EXISTS caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto_inicial REAL NOT NULL,
            monto_final REAL,
            monto_efectivo REAL,
            monto_digital REAL,
            fecha_apertura TEXT NOT NULL,
            fecha_cierre TEXT,
            estado TEXT DEFAULT 'ABIERTA'
        )
    """)

    # Semilla de Menú Defecto si está vacía
    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] == 0:
        productos_defecto = [
            ("Pizza Americana Personal", "Pizzas", 25.00, 50, "Personal"),
            ("Pizza Hawaiana Personal", "Pizzas", 25.00, 50, "Personal"),
            ("Pizza Peperoni Personal", "Pizzas", 25.00, 50, "Personal"),
            ("Pizza Pilo Personal", "Pizzas", 28.00, 50, "Personal"),
            ("Pizza Americana Familiar", "Pizzas", 45.00, 50, "Familiar"),
            ("Pizza Hawaiana Familiar", "Pizzas", 45.00, 50, "Familiar"),
            ("Pizza Peperoni Familiar", "Pizzas", 45.00, 50, "Familiar"),
            ("Pizza Pilo Familiar", "Pizzas", 50.00, 50, "Familiar"),
            ("Alitas Rebozadas", "Alitas", 20.00, 50, "Porción"),
            ("Alitas BBQ", "Alitas", 22.00, 50, "Porción"),
            ("Alitas Acevichadas", "Alitas", 22.00, 50, "Porción"),
            ("Alitas Búfalo", "Alitas", 22.00, 50, "Porción"),
            ("Alitas Pilo", "Alitas", 24.00, 50, "Porción"),
            ("Hamburguesa Clásica", "Hamburguesas", 6.00, 50, "Clásica"),
            ("Hamburguesa Hawaiana", "Hamburguesas", 8.00, 50, "Hawaiana"),
            ("Hamburguesa Pilo", "Hamburguesas", 9.00, 50, "Pilo"),
            ("Hamburguesa A lo pobre", "Hamburguesas", 10.00, 50, "A lo pobre"),
            ("Hamburguesa Royal", "Hamburguesas", 14.00, 50, "Royal"),
            ("Hamburguesa Mega Pilo", "Hamburguesas", 16.00, 50, "Mega Pilo"),
            ("Choripan", "Entradas", 6.00, 50, "Tradicional"),
            ("Salchipapa Clásica", "Entradas", 8.00, 50, "Clásica"),
            ("Salchialita", "Entradas", 16.00, 50, "Especial"),
            ("Porción de Papa", "Otros", 5.00, 100, "Extra"),
            ("Porción de Maduro", "Otros", 5.00, 100, "Extra"),
            ("Porción de Alitas (x ud)", "Otros", 4.00, 100, "Extra"),
            ("Inca Kola 500ml", "Otros", 5.00, 100, "Bebida"),
            ("Coca Cola 500ml", "Otros", 5.00, 100, "Bebida"),
            ("Chicha Morada", "Otros", 3.00, 100, "Bebida"),
        ]
        c.executemany("INSERT INTO productos (nombre, categoria, precio, stock, tipo) VALUES (?, ?, ?, ?, ?)", productos_defecto)

    conn.commit()
    conn.close()

def registrar_venta_completa(correlativo, total, metodo, monto_ef, monto_dig, carrito):
    conn = get_connection()
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Insertar Cabecera
    c.execute(
        "INSERT INTO ventas (correlativo, total, metodo, monto_efectivo, monto_digital, fecha) VALUES (?, ?, ?, ?, ?, ?)",
        (correlativo, total, metodo, monto_ef, monto_dig, fecha_actual)
    )
    venta_id = c.lastrowid

    # 2. Insertar Detalle y Descontar Stock
    for p_id, item in carrito.items():
        c.execute(
            "INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (venta_id, p_id, item["cant"], item["precio"], item["precio"] * item["cant"])
        )
        # Descuento real de stock
        c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item["cant"], p_id))

    conn.commit()
    conn.close()
    return fecha_actual

def generar_correlativo_boleta():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ventas")
    num_ventas = c.fetchone()[0] + 1
    conn.close()
    return f"B001-{num_ventas:06d}"
