import streamlit as st
import sqlite3
from datetime import datetime

# Configuración de página para Celular / Web
st.set_page_config(page_title="Pilo POS Mobile", page_icon="🍕", layout="wide")

# --- BASE DE DATOS Y CARTA ---
def inicializar_bd():
    conexion = sqlite3.connect("base_datos.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT DEFAULT 'Otros',
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 50,
            tipo TEXT DEFAULT ''
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            cantidad INTEGER,
            total REAL,
            metodo_pago TEXT,
            fecha TEXT
        );
    """)

    carta_pilo = [
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
        ("Porción de Salchicha", "Otros", 3.00, 100, "Extra"),
        ("Carne de Hamburguesa", "Otros", 4.00, 100, "Extra"),
        ("Porción de Huevo", "Otros", 1.00, 100, "Extra"),
        ("Jamón y Tocino", "Otros", 2.00, 100, "Extra"),
        ("Porción de Piña", "Otros", 1.00, 100, "Extra"),
        ("Queso Hamburguesa", "Otros", 1.00, 100, "Extra"),
        ("Queso Pizza", "Otros", 3.00, 100, "Extra"),
        ("Agua Mineral", "Otros", 2.00, 100, "Bebida"),
        ("Agua Mineral San Luis", "Otros", 3.00, 100, "Bebida"),
        ("Inca Kola", "Otros", 5.00, 100, "Bebida"),
        ("Coca Cola", "Otros", 5.00, 100, "Bebida"),
        ("Chicha Morada", "Otros", 3.00, 100, "Bebida"),
        ("Cocina", "Otros", 3.00, 100, "Bebida")
    ]

    for p in carta_pilo:
        cursor.execute("SELECT id FROM productos WHERE nombre = ?;", (p[0],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO productos (nombre, categoria, precio, stock, tipo) VALUES (?, ?, ?, ?, ?);", p)
        else:
            cursor.execute("UPDATE productos SET categoria = ?, precio = ?, stock = ?, tipo = ? WHERE nombre = ?;", (p[1], p[2], p[3], p[4], p[0]))

    conexion.commit()
    conexion.close()

inicializar_bd()

# --- ESTADOS DE SESIÓN ---
if "caja_abierta" not in st.session_state:
    st.session_state.caja_abierta = False
if "monto_apertura" not in st.session_state:
    st.session_state.monto_apertura = 0.0
if "carrito" not in st.session_state:
    st.session_state.carrito = []

CLAVE_CAJA = "200423"

# --- INTERFAZ DE USUARIO ---
st.title("🍔 Pilo POS - Punto de Venta")

# Barra Superior / Control de Caja
col_caja1, col_caja2 = st.columns([2, 1])

with col_caja1:
    if st.session_state.caja_abierta:
        st.success(f"🟢 Caja ABIERTA (Monto inicial: S/ {st.session_state.monto_apertura:.2f})")
    else:
        st.error("🔴 Caja CERRADA")

with col_caja2:
    if not st.session_state.caja_abierta:
        with st.popover("🔓 Abrir Caja"):
            clave = st.text_input("Contraseña:", type="password")
            monto = st.number_input("Monto Inicial S/", min_value=0.0, step=10.0)
            if st.button("Confirmar Apertura"):
                if clave == CLAVE_CAJA:
                    st.session_state.caja_abierta = True
                    st.session_state.monto_apertura = monto
                    st.rerun()
                else:
                    st.error("Clave incorrecta")
    else:
        if st.button("🔒 Cerrar Caja"):
            st.session_state.caja_abierta = False
            st.session_state.carrito = []
            st.rerun()

st.divider()

# --- PESTAÑAS Y CARRITO ---
tab1, tab2 = st.tabs(["🛒 TOMAR PEDIDO", "📊 VER VENTAS DEL DÍA"])

with tab1:
    col_menu, col_carrito = st.columns([3, 2])

    with col_menu:
        cat_sel = st.radio("Categorías:", ["Pizzas", "Alitas", "Hamburguesas", "Entradas", "Otros"], horizontal=True)
        
        conexion = sqlite3.connect("base_datos.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?;", (cat_sel,))
        prods = cursor.fetchall()
        conexion.close()

        cols_grid = st.columns(2)
        for idx, (p_id, p_nom, p_pre) in enumerate(prods):
            with cols_grid[idx % 2]:
                if st.button(f"{p_nom}\nS/ {p_pre:.2f}", key=f"p_{p_id}", use_container_width=True):
                    if not st.session_state.caja_abierta:
                        st.warning("Abre caja primero con la clave.")
                    else:
                        # Agregar al carrito
                        encontrado = False
                        for item in st.session_state.carrito:
                            if item["id"] == p_id:
                                item["cant"] += 1
                                item["sub"] = item["cant"] * p_pre
                                encontrado = True
                                break
                        if not encontrado:
                            st.session_state.carrito.append({"id": p_id, "nom": p_nom, "pre": p_pre, "cant": 1, "sub": p_pre})
                        st.rerun()

    with col_carrito:
        st.subheader("🛒 Carrito")
        total_pago = 0.0
        
        if st.session_state.carrito:
            for i, item in enumerate(st.session_state.carrito):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{item['cant']}x** {item['nom']} - S/ {item['sub']:.2f}")
                if c2.button("❌", key=f"del_{i}"):
                    st.session_state.carrito.pop(i)
                    st.rerun()
                total_pago += item["sub"]
            
            st.markdown(f"### TOTAL: S/ {total_pago:.2f}")
            
            metodo = st.selectbox("Método de Pago:", ["Efectivo", "Yape", "Plin"])
            
            if st.button("💵 COBRAR", type="primary", use_container_width=True):
                fec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conexion = sqlite3.connect("base_datos.db")
                cursor = conexion.cursor()
                for item in st.session_state.carrito:
                    cursor.execute("INSERT INTO ventas (producto_id, cantidad, total, metodo_pago, fecha) VALUES (?, ?, ?, ?, ?);", 
                                   (item["id"], item["cant"], item["sub"], metodo, fec))
                conexion.commit()
                conexion.close()
                st.session_state.carrito = []
                st.success(f"¡Venta registrada con {metodo}!")
                st.rerun()
        else:
            st.info("El carrito está vacío.")

with tab2:
    st.subheader("Reporte de Ventas")
    hoy = datetime.now().strftime("%Y-%m-%d")
    conexion = sqlite3.connect("base_datos.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT v.id, p.nombre, v.cantidad, v.total, v.metodo_pago, v.fecha 
        FROM ventas v LEFT JOIN productos p ON v.producto_id = p.id 
        WHERE DATE(v.fecha) = ? ORDER BY v.id DESC;
    """, (hoy,))
    rows = cursor.fetchall()
    conexion.close()

    if rows:
        total_dia = sum(r[3] for r in rows)
        st.metric("Total Recaudado Hoy", f"S/ {total_dia:.2f}")
        st.dataframe(rows, column_config={"0": "ID", "1": "Producto", "2": "Cant", "3": "Total", "4": "Método", "5": "Fecha"})
    else:
        st.write("No hay ventas registradas hoy.")