import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Pilo POS Mobile", page_icon="🍗", layout="wide")

PIN_ADMIN = "200423"

# --- BASE DE DATOS E INICIALIZACIÓN SEGURO ---
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
            metodo TEXT DEFAULT 'Efectivo',
            fecha TEXT
        )
    """)
    
    # Asegurar que la columna 'metodo' exista en bases de datos viejas
    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN metodo TEXT DEFAULT 'Efectivo'")
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    # Cargar productos base si está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_defecto = [
            ("Alitas 6 Pzs", 15.00, "Alitas"),
            ("Alitas 12 Pzs", 28.00, "Alitas"),
            ("Alitas 18 Pzs", 40.00, "Alitas"),
            ("Hamburguesa Hawaiana", 8.00, "Hamburguesas"),
            ("Hamburguesa Royal", 14.00, "Hamburguesas"),
            ("Hamburguesa Pilo", 9.00, "Hamburguesas"),
            ("Hamburguesa Mega Pilo", 16.00, "Hamburguesas"),
            ("Gaseosa 500ml", 4.00, "Bebidas"),
            ("Chicha Morada", 5.00, "Bebidas")
        ]
        cursor.executemany("INSERT INTO productos (nombre, precio, categoria) VALUES (?, ?, ?)", productos_defecto)
    
    conexion.commit()
    conexion.close()

inicializar_bd()

# --- ESTRUCTURA DE PESTAÑAS ---
st.title("🍗 piloPOS - Sistema de Ventas")

tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Punto de Venta", 
    "📋 Ventas del Día", 
    "🔒 Cierre de Turno", 
    "📊 Reporte Mensual"
])

# ---------------------------------------------------------
# PESTAÑA 1: PUNTO DE VENTA
# ---------------------------------------------------------
with tab1:
    conn = sqlite3.connect("base_datos.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT categoria FROM productos")
    cats = [row[0] for row in c.fetchall()]
    
    cat_sel = st.radio("Categorías", cats, horizontal=True) if cats else "Alitas"
    
    c.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?", (cat_sel,))
    prods = c.fetchall()
    conn.close()
    
    st.subheader("Menú de Productos")
    col1, col2 = st.columns(2)
    for i, (p_id, p_nom, p_precio) in enumerate(prods):
        col = col1 if i % 2 == 0 else col2
        if col.button(f"{p_nom}\nS/ {p_precio:.2f}", key=f"p_{p_id}", use_container_width=True):
            if "carrito" not in st.session_state:
                st.session_state.carrito = []
            st.session_state.carrito.append({"id": p_id, "nombre": p_nom, "precio": p_precio})
            st.toast(f"Agregado: {p_nom}")

    st.markdown("---")
    st.subheader("Detalle del Pedido")
    
    cliente = st.text_input("Nombre del Cliente / Mesa", placeholder="Ej: Mesa 3 o Juan")
    tipo = st.selectbox("Tipo de Pedido", ["Para Comer Aquí", "Para Llevar", "Delivery"])
    metodo_pago = st.radio("Método de Pago", ["Efectivo", "Yape", "Plin"], horizontal=True)
    
    if "carrito" in st.session_state and st.session_state.carrito:
        st.write("### Productos seleccionados:")
        for idx, item in enumerate(st.session_state.carrito):
            st.write(f"- {item['nombre']} (S/ {item['precio']:.2f})")
            
        total = sum(item["precio"] for item in st.session_state.carrito)
        st.markdown(f"### **Total a cobrar: S/ {total:.2f}**")
        
        c1, c2 = st.columns(2)
        if c1.button("🚀 Registrar Venta", use_container_width=True):
            conn = sqlite3.connect("base_datos.db")
            c = conn.cursor()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO ventas (cliente, tipo, total, metodo, fecha) VALUES (?, ?, ?, ?, ?)",
                      (cliente if cliente else "Cliente General", tipo, total, metodo_pago, fecha_actual))
            conn.commit()
            conn.close()
            st.session_state.carrito = []
            st.success(f"¡Venta registrada con éxito ({metodo_pago})!")
            st.rerun()
            
        if c2.button("🗑️ Vaciar Carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()
    else:
        st.info("El carrito está vacío. Haz clic en los productos arriba para agregarlos.")

# ---------------------------------------------------------
# PESTAÑA 2: VENTAS DEL DÍA
# ---------------------------------------------------------
with tab2:
    st.subheader("📋 Ventas Realizadas Hoy")
    try:
        conn = sqlite3.connect("base_datos.db")
        df_ventas = pd.read_sql_query("SELECT id AS ID, cliente AS Cliente, tipo AS Tipo, total AS 'Total S/', metodo AS Método, fecha AS Fecha FROM ventas ORDER BY id DESC", conn)
        conn.close()
        
        if not df_ventas.empty:
            st.dataframe(df_ventas, use_container_width=True)
            total_hoy = df_ventas["Total S/"].sum()
            st.metric("Total Recaudado Hoy", f"S/ {total_hoy:.2f}")
        else:
            st.write("Aún no hay ventas registradas.")
    except Exception as e:
        st.info("Aún no hay registros de ventas.")

# ---------------------------------------------------------
# PESTAÑA 3: CIERRE DE TURNO
# ---------------------------------------------------------
with tab3:
    st.subheader("🔒 Cierre del Turno")
    clave = st.text_input("Contraseña de Administrador", type="password", key="pass_cierre")
    if clave == PIN_ADMIN:
        st.success("Acceso concedido")
        try:
            conn = sqlite3.connect("base_datos.db")
            df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
            conn.close()
            
            if not df_ventas.empty:
                st.write("### Resumen del Turno:")
                tot_efectivo = df_ventas[df_ventas['metodo'] == 'Efectivo']['total'].sum() if 'metodo' in df_ventas.columns else 0
                tot_yape = df_ventas[df_ventas['metodo'] == 'Yape']['total'].sum() if 'metodo' in df_ventas.columns else 0
                tot_plin = df_ventas[df_ventas['metodo'] == 'Plin']['total'].sum() if 'metodo' in df_ventas.columns else 0
                tot_general = df_ventas['total'].sum()
                
                c1, c2, c3 = st.columns(3)
                c1.metric("💵 Efectivo", f"S/ {tot_efectivo:.2f}")
                c2.metric("📲 Yape", f"S/ {tot_yape:.2f}")
                c3.metric("📲 Plin", f"S/ {tot_plin:.2f}")
                st.metric("💰 Total General", f"S/ {tot_general:.2f}")
            else:
                st.write("No hay ventas registradas en este turno.")
        except Exception:
            st.write("Sin datos para mostrar.")
    elif clave:
        st.error("Contraseña incorrecta")

# ---------------------------------------------------------
# PESTAÑA 4: REPORTE MENSUAL
# ---------------------------------------------------------
with tab4:
    st.subheader("📊 Reporte Mensual")
    clave_rep = st.text_input("Contraseña de Administrador", type="password", key="pass_rep")
    if clave_rep == PIN_ADMIN:
        st.success("Acceso concedido")
        try:
            conn = sqlite3.connect("base_datos.db")
            df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
            conn.close()
            
            if not df_ventas.empty:
                st.dataframe(df_ventas, use_container_width=True)
            else:
                st.write("No hay datos registrados aún.")
        except Exception:
            st.write("Sin registros previos.")
    elif clave_rep:
        st.error("Contraseña incorrecta")
