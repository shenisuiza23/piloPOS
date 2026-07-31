import sqlite3
from datetime import datetime

DB_NAME = "pilo_pos.db"

def inicializar_bd():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT DEFAULT 'Otros',
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 50
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlativo TEXT, total REAL, metodo TEXT,
            monto_efectivo REAL, monto_digital REAL, fecha TEXT, detalle TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto_inicial REAL, monto_final REAL,
            fecha_apertura TEXT, fecha_cierre TEXT, estado TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        prods = [
            ("Pizza Americana Personal", "Pizzas", 25.00), ("Pizza Hawaiana Personal", "Pizzas", 25.00),
            ("Pizza Pepperoni Personal", "Pizzas", 25.00), ("Pizza Pilo Personal", "Pizzas", 28.00),
            ("Pizza Americana Familiar", "Pizzas", 45.00), ("Pizza Hawaiana Familiar", "Pizzas", 45.00),
            ("Pizza Pepperoni Familiar", "Pizzas", 45.00), ("Pizza Pilo Familiar", "Pizzas", 50.00),
            ("Alitas Rebozadas", "Alitas", 20.00), ("Alitas BBQ", "Alitas", 22.00),
            ("Alitas Acevichadas", "Alitas", 22.00), ("Alitas Búfalo", "Alitas", 22.00),
            ("Alitas Pilo", "Alitas", 24.00), ("Hamburguesa Clásica", "Hamburguesas", 6.00),
            ("Hamburguesa Hawaiana", "Hamburguesas", 8.00), ("Hamburguesa A lo Pilo", "Hamburguesas", 9.00),
            ("Hamburguesa A lo Pobre", "Hamburguesas", 10.00), ("Hamburguesa Royal", "Hamburguesas", 14.00),
            ("Hamburguesa Mega Pilo", "Hamburguesas", 16.00), ("Choripán", "Entradas", 6.00),
            ("Salchipapa Clásica", "Entradas", 8.00), ("Salchalita", "Entradas", 16.00),
            ("Porción de Papa", "Extras", 5.00), ("Porción de Maduro", "Extras", 5.00),
            ("Inca Kola", "Bebidas", 5.00), ("Coca Cola", "Bebidas", 5.00), ("Chicha Morada", "Bebidas", 3.00)
        ]
        cursor.executemany("INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)", prods)
    
    conexion.commit()
    conexion.close()

def registrar_venta(total, metodo, monto_ef, monto_dig, carrito):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ventas")
    correlativo = f"B001-{(c.fetchone()[0] + 1):06d}"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detalle = ", ".join([f"{item['cant']}x {item['nombre']}" for item in carrito.values()])
    
    c.execute("INSERT INTO ventas (correlativo, total, metodo, monto_efectivo, monto_digital, fecha, detalle) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (correlativo, total, metodo, monto_ef, monto_dig, fecha, detalle))
    conn.commit()
    conn.close()
    return correlativo
