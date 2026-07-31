import sqlite3
from datetime import datetime

DB_NAME = "pos_v7.db"

def inicializar_bd():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT DEFAULT 'Otros',
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 50,
            tipo TEXT DEFAULT 'Gral'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlativo TEXT,
            total REAL,
            metodo TEXT,
            fecha TEXT,
            detalle TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto_inicial REAL,
            monto_final REAL,
            fecha_apertura TEXT,
            fecha_cierre TEXT,
            estado TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
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
        cursor.executemany(
            "INSERT INTO productos (nombre, categoria, precio, stock, tipo) VALUES (?, ?, ?, ?, ?)",
            productos_defecto
        )

    conexion.commit()
    conexion.close()

def obtener_siguiente_correlativo():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ventas")
    num_ventas = c.fetchone()[0] + 1
    conn.close()
    return f"B001-{num_ventas:06d}"
