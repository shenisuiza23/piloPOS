import sqlite3
from datetime import datetime
from config import DB_NAME

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_bd():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabla de Productos
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            tipo TEXT
        )
    ''')
    
    # Tabla de Ventas
    c.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlativo TEXT NOT NULL,
            total REAL NOT NULL,
            metodo TEXT NOT NULL,
            monto_efectivo REAL NOT NULL,
            monto_digital REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')

    # Tabla de Detalle de Ventas
    c.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlativo TEXT NOT NULL,
            producto_id INTEGER NOT NULL,
            producto_nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL
        )
    ''')

    # Tabla de Caja
    c.execute('''
        CREATE TABLE IF NOT EXISTS caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto_inicial REAL NOT NULL,
            fecha_apertura TEXT NOT NULL,
            fecha_cierre TEXT,
            monto_final REAL,
            estado TEXT NOT NULL
        )
    ''')

    # Insertar productos demo si la tabla está vacía
    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] == 0:
        productos_def = [
            ("Pizza Americana Familiar", "Pizzas", 45.00, 30, "Comida"),
            ("Pizza Hawaiana Familiar", "Pizzas", 45.00, 30, "Comida"),
            ("Pizza Pepperoni Familiar", "Pizzas", 45.00, 30, "Comida"),
            ("Pizza Pilo Familiar", "Pizzas", 50.00, 30, "Comida"),
            ("Alitas 6 piezas", "Alitas", 18.00, 50, "Comida"),
            ("Alitas 12 piezas", "Alitas", 32.00, 50, "Comida"),
            ("Hamburguesa Clásica", "Hamburguesas", 15.00, 40, "Comida"),
            ("Hamburguesa Pilo Royale", "Hamburguesas", 22.00, 40, "Comida"),
            ("Papas Fritas", "Entradas", 10.00, 60, "Comida"),
            ("Coca Cola 500ml", "Otros", 5.00, 100, "Bebida"),
            ("Chicha Morada", "Otros", 3.00, 100, "Bebida"),
        ]
        c.executemany("INSERT INTO productos (nombre, categoria, precio, stock, tipo) VALUES (?, ?, ?, ?, ?)", productos_def)

    conn.commit()
    conn.close()

def generar_correlativo_boleta():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ventas")
    num = c.fetchone()[0] + 1
    conn.close()
    return f"B001-{num:06d}"

def registrar_venta_completa(correlativo, total, metodo, monto_ef, monto_dig, carrito):
    conn = get_connection()
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar cabecera de la venta
    c.execute(
        "INSERT INTO ventas (correlativo, total, metodo, monto_efectivo, monto_digital, fecha) VALUES (?, ?, ?, ?, ?, ?)",
        (correlativo, total, metodo, monto_ef, monto_dig, fecha_actual)
    )

    # Guardar detalles y descontar stock
    for p_id, item in carrito.items():
        subt = item["precio"] * item["cant"]
        c.execute(
            "INSERT INTO detalle_ventas (correlativo, producto_id, producto_nombre, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
            (correlativo, p_id, item["nombre"], item["cant"], item["precio"], subt)
        )
        c.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (item["cant"], p_id)
        )

    conn.commit()
    conn.close()
    return fecha_actual
