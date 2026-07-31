import streamlit as st
import sqlite3
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Pilo POS Mobile", page_icon="🍗", layout="wide")

PIN_ADMIN = "200423"

# --- BASE DE DATOS E INICIALIZACIÓN ---
def inicializar_bd():
    conexion = sqlite3.connect("base_datos.db")
    cursor = conexion.cursor()
    
    # Tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT DEFAULT 'Otros'
        )
    """)
    
    # Tabla de ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            tipo TEXT,
            total REAL,
            metodo TEXT,
            fecha TEXT
        )
    """)
    
    # Tabla de caja (Apertura y Cierre)
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
    
    # Cargar menú por defecto si la base de datos está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_defecto = [
            ("Alitas 6 Pzs", 15.00, "Alitas"),
            ("Alitas 12 Pzs", 28.00, "Alitas"),
            ("Alitas 18 Pzs", 40.00, "Alitas"),
            ("Gaseosa 500ml", 4.00, "Bebidas"),
            ("Inka Kola 1.5L", 9.00, "Bebidas"),
            ("Chicha Morada", 5.00, "Bebidas"),
            ("Papas Fritas", 7.00, "Extras"),
            ("Porción Arroz", 3.00, "Extras")
        ]
        cursor.executemany("INSERT INTO productos (nombre, precio, categoria) VALUES (?, ?, ?)", productos_defecto)
    
    conexion.commit()
    conexion.close()

inicializar_bd()

# --- INTERFAZ ---
st.title("🍗 piloPOS - Sistema de Ventas")

tab1, tab2, tab3 = st.tabs(["🛒 Punto de Venta", "🔒 Cierre del Turno (12pm-12pm)", "📊 Reporte Mensual"])

with tab1:
    # Verificación de Apertura de Caja
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
    caja_activa = c.fetchone()
    conn.close()
    
    if not caja_activa:
        st.warning("⚠️ La caja está cerrada. Debes realizar la apertura para empezar a vender.")
        monto_ini = st.number_input("Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0)
        if st.button("🔓 Abrir Caja"):
            conn = sqlite3.connect("base_datos.db")
            c = conn.cursor()
            c.execute("INSERT INTO caja (monto_inicial, fecha_apertura, estado) VALUES (?, ?, 'ABIERTA')", 
                      (monto_ini, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("¡Caja abierta con éxito!")
            st.rerun()
    else:
        st.success(f"🟢 Caja Abierta con S/ {caja_activa[1]:.2f}")
        
        # Categorías y Productos
        conn = sqlite3.connect("base_datos.db")
        c = conn.cursor()
        c.execute("SELECT DISTINCT categoria FROM productos")
        cats = [row[0] for row in c.fetchall()]
        
        cat_sel = st.radio("Categorías", cats, horizontal=True) if cats else "Alitas"
        
        c.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?", (cat_sel,))
        prods = c.fetchall()
        conn.close()
        
        st.subheader("Menú de Productos")
        col1, col2, col3 = st.columns(3)
        for i, (p_id, p_nom, p_precio) in enumerate(prods):
            col = [col1, col2, col3][i % 3]
            if col.button(f"{p_nom}\nS/ {p_precio:.2f}", key=f"p_{p_id}"):
                if "carrito" not in st.session_state:
                    st.session_state.carrito = []
                st.session_state.carrito.append({"id": p_id, "nombre": p_nom, "precio": p_precio})
                st.toast(f"Agregado: {p_nom}")

        st.markdown("---")
        st.subheader("Detalle del Pedido")
        cliente = st.text_input("Nombre del Cliente / Mesa", placeholder="Ej: Mesa 3 o Juan")
        tipo = st.selectbox("Tipo de Pedido", ["Para Comer Aquí", "Para Llevar", "Delivery"])
        
        if "carrito" in st.session_state and st.session_state.carrito:
            total = sum(item["precio"] for item in st.session_state.carrito)
            st.write(f"**Total a cobrar:** S/ {total:.2f}")
            if st.button("🚀 Registrar Venta"):
                conn = sqlite3.connect("base_datos.db")
                c = conn.cursor()
                c.execute("INSERT INTO ventas (cliente, tipo, total, metodo, fecha) VALUES (?, ?, ?, 'Efectivo', ?)",
                          (cliente, tipo, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.session_state.carrito = []
                st.success("¡Venta registrada exitosamente!")
                st.rerun()
        else:
            st.info("El carrito está vacío. Haz clic en los productos arriba para agregarlos.")

with tab2:
    st.subheader("Cierre de Turno")
    clave = st.text_input("Contraseña de Administrador", type="password", key="pass_cierre")
    if clave == PIN_ADMIN:
        st.success("Acceso concedido")
        # Lógica de cierre aquí
    elif clave:
        st.error("Contraseña incorrecta")

with tab3:
    st.subheader("Reporte Mensual")
    clave_rep = st.text_input("Contraseña de Administrador", type="password", key="pass_rep")
    if clave_rep == PIN_ADMIN:
        st.success("Acceso concedido")
        # Lógica de reportes aquí
    elif clave_rep:
        st.error("Contraseña incorrecta")
