import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pilo POS Mobile", page_icon="🍗", layout="wide")

PIN_ADMIN = "200423"
DB_NAME = "pos_v2.db"

# Estilos personalizados (Botón verde llamativo)
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #28a745 !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        height: 3em !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS ---
def inicializar_bd():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT DEFAULT 'Otros'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL,
            metodo TEXT,
            fecha TEXT
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
            ("Alitas 6 Pzs", 15.00, "Alitas"),
            ("Alitas 12 Pzs", 28.00, "Alitas"),
            ("Alitas 18 Pzs", 40.00, "Alitas"),
            ("Hamburguesa Clásica", 6.00, "Hamburguesas"),
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

# --- NAVEGACIÓN ---
st.title("🍗 piloPOS - Sistema de Ventas")

tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Punto de Venta", 
    "📋 Ventas del Día", 
    "🔒 Control de Caja", 
    "📊 Reporte Mensual"
])

# ---------------------------------------------------------
# PESTAÑA 1: PUNTO DE VENTA (CON APERTURA DE CAJA)
# ---------------------------------------------------------
with tab1:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
    caja_activa = c.fetchone()
    conn.close()

    if not caja_activa:
        st.warning("⚠️ La caja está CERRADA. Debes realizar la apertura con contraseña para empezar a vender.")
        clave_apertura = st.text_input("Contraseña para Abrir Caja", type="password", key="pass_open")
        monto_ini = st.number_input("Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0)
        
        if st.button("🔓 ABRIR CAJA E INICIAR VENTAS"):
            if clave_apertura == PIN_ADMIN:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO caja (monto_inicial, fecha_apertura, estado) VALUES (?, ?, 'ABIERTA')", 
                          (monto_ini, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("¡Caja abierta exitosamente!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta para abrir caja.")
    else:
        st.success(f"🟢 Caja Abierta con S/ {caja_activa[1]:.2f}")
        
        conn = sqlite3.connect(DB_NAME)
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
        metodo_pago = st.radio("Método de Pago", ["Efectivo", "Yape", "Plin"], horizontal=True)
        
        if "carrito" in st.session_state and st.session_state.carrito:
            st.write("### Productos seleccionados:")
            for item in st.session_state.carrito:
                st.write(f"- {item['nombre']} (S/ {item['precio']:.2f})")
                
            total = sum(item["precio"] for item in st.session_state.carrito)
            st.markdown(f"## **Total a cobrar: S/ {total:.2f}**")
            
            if st.button("🚀 REGISTRAR VENTA", use_container_width=True):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO ventas (total, metodo, fecha) VALUES (?, ?, ?)",
                          (total, metodo_pago, fecha_actual))
                conn.commit()
                conn.close()
                st.session_state.carrito = []
                st.success(f"¡Venta Registrada! ({metodo_pago})")
                st.rerun()
                
            if st.button("🗑️ Vaciar Carrito", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()
        else:
            st.info("El carrito está vacío. Elige un producto arriba.")

# ---------------------------------------------------------
# PESTAÑA 2: VENTAS DEL DÍA
# ---------------------------------------------------------
with tab2:
    st.subheader("📋 Ventas Realizadas hoy")
    conn = sqlite3.connect(DB_NAME)
    try:
        df_ventas = pd.read_sql_query("SELECT id AS ID, total AS 'Total S/', metodo AS Método, fecha AS Fecha FROM ventas ORDER BY id DESC", conn)
        if not df_ventas.empty:
            st.dataframe(df_ventas, use_container_width=True)
            total_hoy = df_ventas["Total S/"].sum()
            st.metric("Total Recaudado Hoy", f"S/ {total_hoy:.2f}")
        else:
            st.write("Aún no hay ventas registradas.")
    except Exception:
        st.write("Sin ventas por ahora.")
    conn.close()

# ---------------------------------------------------------
# PESTAÑA 3: CONTROL DE CAJA Y CIERRE
# ---------------------------------------------------------
with tab3:
    st.subheader("🔒 Control y Cierre de Caja")
    clave = st.text_input("Contraseña de Administrador", type="password", key="pass_cierre")
    
    if clave == PIN_ADMIN:
        st.success("Acceso concedido")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
        caja_activa = c.fetchone()
        
        df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
        conn.close()
        
        if caja_activa:
            st.write(f"**Caja iniciada el:** {caja_activa[3]}")
            st.write(f"**Monto Inicial:** S/ {caja_activa[1]:.2f}")
            
            tot_efectivo = df_ventas[df_ventas['metodo'] == 'Efectivo']['total'].sum() if not df_ventas.empty else 0
            tot_yape = df_ventas[df_ventas['metodo'] == 'Yape']['total'].sum() if not df_ventas.empty else 0
            tot_plin = df_ventas[df_ventas['metodo'] == 'Plin']['total'].sum() if not df_ventas.empty else 0
            tot_ventas = df_ventas['total'].sum() if not df_ventas.empty else 0
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("💵 Efectivo", f"S/ {tot_efectivo:.2f}")
            c2.metric("📲 Yape", f"S/ {tot_yape:.2f}")
            c3.metric("📲 Plin", f"S/ {tot_plin:.2f}")
            st.metric("💰 Total Ventas", f"S/ {tot_ventas:.2f}")
            st.metric("💵 Total Efectivo en Caja Esperado", f"S/ {(caja_activa[1] + tot_efectivo):.2f}")
            
            st.markdown("---")
            if st.button("🔒 CERRAR CAJA Y FINALIZAR TURNO"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE caja SET monto_final = ?, fecha_cierre = ?, estado = 'CERRADA' WHERE id = ?",
                          (caja_activa[1] + tot_ventas, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), caja_activa[0]))
                conn.commit()
                conn.close()
                st.success("¡Caja Cerrada con Éxito!")
                st.rerun()
        else:
            st.info("La caja actualmente está CERRADA.")
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
        conn = sqlite3.connect(DB_NAME)
        try:
            df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
            if not df_ventas.empty:
                st.dataframe(df_ventas, use_container_width=True)
            else:
                st.write("No hay datos de ventas registrados.")
        except Exception:
            st.write("Sin datos disponibles.")
        conn.close()
    elif clave_rep:
        st.error("Contraseña incorrecta")
