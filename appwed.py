import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pilo POS Tablet", page_icon="🍗", layout="wide", initial_sidebar_state="collapsed")

PIN_ADMIN = "200423"
DB_NAME = "pos_v6.db"

# Estilos CSS personalizados con colores suaves y definidos por categoría
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 17px !important;
    }
    
    /* Botones generales de productos */
    div.stButton > button {
        background-color: #374151 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 17px !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: none !important;
        margin-bottom: 6px !important;
    }
    
    /* Botones Específicos por Categoría (Colores Suaves) */
    .btn-pizza > div.stButton > button { background-color: #2b5c8f !important; }
    .btn-alitas > div.stButton > button { background-color: #c69214 !important; }
    .btn-hamburguesa > div.stButton > button { background-color: #d97724 !important; }
    .btn-entradas > div.stButton > button { background-color: #2e7d32 !important; }
    .btn-otros > div.stButton > button { background-color: #0288d1 !important; }

    /* Botón Cobrar (Verde Grande) */
    .btn-cobrar > div.stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
        height: 3.2em !important;
        border-radius: 12px !important;
    }

    /* Botón Vaciar Carrito (Azul) */
    .btn-vaciar > div.stButton > button {
        background-color: #1e3a8a !important;
        color: white !important;
        font-size: 16px !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS Y MENÚ REAL ---
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
st.title("🍗 piloPOS - Punto de Venta")

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
        st.warning("⚠️ La caja está CERRADA. Abre caja para empezar las ventas.")
        clave_apertura = st.text_input("Contraseña para Abrir Caja", type="password", key="pass_open")
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
                st.error("Contraseña incorrecta")
    else:
        st.success(f"🟢 Caja Abierta con S/ {caja_activa[1]:.2f}")
        
        # Mapeo de categorías con colores
        cats_color = {
            "Pizzas": "btn-pizza",
            "Alitas": "btn-alitas",
            "Hamburguesas": "btn-hamburguesa",
            "Entradas": "btn-entradas",
            "Otros": "btn-otros"
        }

        st.write("### Categorías:")
        if "cat_seleccionada" not in st.session_state:
            st.session_state.cat_seleccionada = "Pizzas"
            
        cols_cat = st.columns(len(cats_color))
        for idx, (cat, css_class) in enumerate(cats_color.items()):
            with cols_cat[idx]:
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                if st.button(cat, key=f"cat_btn_{cat}", use_container_width=True):
                    st.session_state.cat_seleccionada = cat
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Layout principal de Venta
        col_menu, col_carrito = st.columns([1.2, 1])
        
        with col_menu:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?", (st.session_state.cat_seleccionada,))
            prods = c.fetchall()
            conn.close()
            
            st.subheader(f"Menú: {st.session_state.cat_seleccionada}")
            m_col1, m_col2 = st.columns(2)
            
            css_actual = cats_color.get(st.session_state.cat_seleccionada, "")
            
            for i, (p_id, p_nom, p_precio) in enumerate(prods):
                col = m_col1 if i % 2 == 0 else m_col2
                with col:
                    st.markdown(f'<div class="{css_actual}">', unsafe_allow_html=True)
                    if st.button(f"{p_nom}\nS/ {p_precio:.2f}", key=f"p_{p_id}", use_container_width=True):
                        if "carrito" not in st.session_state:
                            st.session_state.carrito = []
                        st.session_state.carrito.append({"id": p_id, "nombre": p_nom, "precio": p_precio})
                        st.toast(f"＋ {p_nom}")
                    st.markdown('</div>', unsafe_allow_html=True)

        with col_carrito:
            st.subheader("🛒 Pedido Actual")
            metodo_pago = st.radio("Método de Pago:", ["Efectivo", "Yape", "Plin", "Mixto"], horizontal=True)
            
            if "carrito" in st.session_state and st.session_state.carrito:
                for item in st.session_state.carrito:
                    st.write(f"• **{item['nombre']}** — S/ {item['precio']:.2f}")
                    
                total = sum(item["precio"] for item in st.session_state.carrito)
                st.markdown(f"### **Total: S/ {total:.2f}**")
                
                vuelto = 0.0
                if metodo_pago == "Efectivo":
                    monto_recibido = st.number_input("Monto Recibido (S/):", min_value=total, value=total, step=1.0)
                    vuelto = monto_recibido - total
                    st.info(f"💵 **Vuelto a entregar: S/ {vuelto:.2f}**")
                elif metodo_pago == "Mixto":
                    efectivo_part = st.number_input("Monto en Efectivo (S/):", min_value=0.0, max_value=total, value=total/2)
                    digital_part = total - efectivo_part
                    st.write(f"📲 Yape/Plin restante: **S/ {digital_part:.2f}**")
                
                st.markdown('<div class="btn-cobrar">', unsafe_allow_html=True)
                if st.button("🚀 COBRAR (Registrar Venta)", use_container_width=True):
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
                    
                st.markdown('<div class="btn-vaciar">', unsafe_allow_html=True)
                if st.button("🗑️ Vaciar Carrito", use_container_width=True):
                    st.session_state.carrito = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("El carrito está vacío.")

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
            tot_mixto = df_ventas[df_ventas['metodo'] == 'Mixto']['total'].sum() if not df_ventas.empty else 0
            tot_ventas = df_ventas['total'].sum() if not df_ventas.empty else 0
            
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💵 Efectivo", f"S/ {tot_efectivo:.2f}")
            c2.metric("📲 Yape", f"S/ {tot_yape:.2f}")
            c3.metric("📲 Plin", f"S/ {tot_plin:.2f}")
            c4.metric("🔀 Mixto", f"S/ {tot_mixto:.2f}")
            st.metric("💰 Total Ventas", f"S/ {tot_ventas:.2f}")
            st.metric("💵 Total Efectivo Esperado", f"S/ {(caja_activa[1] + tot_efectivo):.2f}")
            
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
