import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página optimizada para pantallas táctiles/tablets
st.set_page_config(page_title="Pilo POS Tablet", page_icon="🍗", layout="wide", initial_sidebar_state="collapsed")

PIN_ADMIN = "200423"
DB_NAME = "pos_v5.db"

# Estilos CSS diseñados para pantallas táctiles (tablets y celulares)
st.markdown("""
    <style>
    /* Aumentar tamaño general de texto e inputs para pantallas táctiles */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    
    /* Botones de menú táctiles grandes */
    div.stButton > button {
        background-color: #FF8C00 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        padding: 12px 10px !important;
        border: none !important;
        margin-bottom: 8px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Efecto al presionar botón */
    div.stButton > button:active {
        transform: scale(0.97) !important;
    }
    
    /* Botón verde grande para Registrar Venta */
    .btn-cobrar > div.stButton > button {
        background-color: #28a745 !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        border-radius: 14px !important;
        box-shadow: 0px 5px 10px rgba(40, 167, 69, 0.4) !important;
    }
    
    /* Radio buttons para Método de Pago más amplios */
    div[role="radiogroup"] > label {
        padding: 8px 16px !important;
        background-color: #1e2229 !important;
        border-radius: 8px !important;
        margin-right: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS Y MENÚ COMPLETO ---
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
        cursor.executemany("INSERT INTO productos (nombre, categoria, precio, stock, tipo) VALUES (?, ?, ?, ?, ?)", productos_defecto)
    
    conexion.commit()
    conexion.close()

inicializar_bd()

# --- NAVEGACIÓN ---
st.title("🍗 piloPOS - Tablet POS")

tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Punto de Venta", 
    "📋 Ventas del Día", 
    "🔒 Control de Caja", 
    "📊 Reporte Mensual"
])

# ---------------------------------------------------------
# PESTAÑA 1: PUNTO DE VENTA
# ---------------------------------------------------------
with tab1:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
    caja_activa = c.fetchone()
    conn.close()

    if not caja_activa:
        st.warning("⚠️ La caja está CERRADA. Ingresa contraseña y monto inicial para empezar.")
        clave_apertura = st.text_input("Contraseña de Apertura", type="password", key="pass_open")
        monto_ini = st.number_input("Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0)
        
        if st.button("🔓 ABRIR CAJA E INICIAR VENTAS", use_container_width=True):
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
        
        # Obtener categorías
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT DISTINCT categoria FROM productos")
        cats = [row[0] for row in c.fetchall()]
        conn.close()

        st.write("### Selecciona Categoría:")
        if "cat_seleccionada" not in st.session_state or st.session_state.cat_seleccionada not in cats:
            st.session_state.cat_seleccionada = cats[0] if cats else "Alitas"
            
        cols_cat = st.columns(len(cats))
        for idx, cat in enumerate(cats):
            if cols_cat[idx].button(f"🟧 {cat}", key=f"cat_btn_{cat}", use_container_width=True):
                st.session_state.cat_seleccionada = cat

        st.markdown("---")
        
        # Layout dividido para Tablet: Menú a la izquierda (60%) y Carrito a la derecha (40%)
        col_menu, col_carrito = st.columns([1.3, 1])
        
        with col_menu:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?", (st.session_state.cat_seleccionada,))
            prods = c.fetchall()
            conn.close()
            
            st.subheader(f"Menú: {st.session_state.cat_seleccionada}")
            m_col1, m_col2 = st.columns(2)
            for i, (p_id, p_nom, p_precio) in enumerate(prods):
                col = m_col1 if i % 2 == 0 else m_col2
                if col.button(f"{p_nom}\nS/ {p_precio:.2f}", key=f"p_{p_id}", use_container_width=True):
                    if "carrito" not in st.session_state:
                        st.session_state.carrito = []
                    st.session_state.carrito.append({"id": p_id, "nombre": p_nom, "precio": p_precio})
                    st.toast(f"＋ {p_nom}")

        with col_carrito:
            st.subheader("🛒 Pedido Actual")
            metodo_pago = st.radio("Método de Pago:", ["Efectivo", "Yape", "Plin"], horizontal=True)
            st.markdown("---")
            
            if "carrito" in st.session_state and st.session_state.carrito:
                for item in st.session_state.carrito:
                    st.write(f"• **{item['nombre']}** — S/ {item['precio']:.2f}")
                    
                total = sum(item["precio"] for item in st.session_state.carrito)
                st.markdown(f"### **Total: S/ {total:.2f}**")
                
                st.markdown('<div class="btn-cobrar">', unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True)
                    
                if st.button("🗑️ Vaciar Carrito", use_container_width=True):
                    st.session_state.carrito = []
                    st.rerun()
            else:
                st.info("Toca un producto de la izquierda para agregarlo.")

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
            if st.button("🔒 CERRAR CAJA Y FINALIZAR TURNO", use_container_width=True):
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
