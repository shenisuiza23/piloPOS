import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PILO POS",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PIN_ADMIN = "200423"
DB_NAME = "pos_v7.db"

# --- ESTADO DE SESIÓN ---
if "cat_seleccionada" not in st.session_state:
    st.session_state.cat_seleccionada = "Pizzas"
if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# --- PALETA DE COLORES FIJA ---
COLORES = {
    "Pizzas": {"bg": "#2b5c8f", "text": "#ffffff"},
    "Alitas": {"bg": "#c69214", "text": "#ffffff"},
    "Hamburguesas": {"bg": "#d97724", "text": "#ffffff"},
    "Entradas": {"bg": "#2e7d32", "text": "#ffffff"},
    "Otros": {"bg": "#0284c7", "text": "#ffffff"},
}

bg_actual = COLORES[st.session_state.cat_seleccionada]["bg"]
text_actual = COLORES[st.session_state.cat_seleccionada]["text"]

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }}
    
    .pilo-navbar {{
        background: linear-gradient(90deg, #ea580c 0%, #d97724 100%);
        color: white;
        padding: 14px 24px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }}
    .pilo-navbar h1 {{
        margin: 0;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 0.5px;
        color: white !important;
    }}

    div.stButton > button {{
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.15) !important;
        transition: all 0.15s ease-in-out !important;
    }}
    div.stButton > button:active {{
        transform: scale(0.97);
    }}

    div[data-testid="stKey-cat_btn_Pizzas"] button {{ background-color: #2b5c8f !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Alitas"] button {{ background-color: #c69214 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Hamburguesas"] button {{ background-color: #d97724 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Entradas"] button {{ background-color: #2e7d32 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Otros"] button {{ background-color: #0284c7 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}

    div[data-testid="stKey-prod_zone"] div.stButton > button {{
        background-color: {bg_actual} !important;
        color: {text_actual} !important;
        min-height: 85px !important;
        font-size: 17px !important;
        white-space: pre-wrap !important;
        line-height: 1.2 !important;
        width: 100% !important;
    }}

    div[data-testid="stKey-btn_cobrar"] button {{
        background-color: #16a34a !important;
        color: white !important;
        font-size: 20px !important;
        height: 55px !important;
        width: 100% !important;
    }}
    div[data-testid="stKey-btn_vaciar"] button {{
        background-color: #dc2626 !important;
        color: white !important;
        font-size: 16px !important;
        height: 55px !important;
        width: 100% !important;
    }}

    .total-box {{
        background-color: #15803d;
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 10px;
        text-align: center;
        font-size: 32px;
        font-weight: 900;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
    </style>
""",
    unsafe_allow_html=True,
)


# --- BASE DE DATOS ---
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


inicializar_bd()

# --- BARRA SUPERIOR NARANJA ---
st.markdown("""
    <div class="pilo-navbar">
        <h1>🍗 PILO POS - Punto de Venta</h1>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Punto de Venta",
    "📋 Ventas del Día",
    "🔒 Control de Caja",
    "📊 Reportes y Estadísticas",
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
        st.warning("⚠️ La caja está CERRADA. Abre caja en la pestaña 'Control de Caja' para iniciar ventas.")
        col_open1, col_open2 = st.columns(2)
        with col_open1:
            clave_apertura = st.text_input("Contraseña de Administrador", type="password", key="pass_open")
        with col_open2:
            monto_ini = st.number_input("Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0)

        if st.button("🔓 ABRIR CAJA", use_container_width=True):
            if clave_apertura == PIN_ADMIN:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO caja (monto_inicial, fecha_apertura, estado) VALUES (?, ?, 'ABIERTA')", (monto_ini, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("¡Caja abierta exitosamente!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    else:
        # BOTONES DE CATEGORÍAS
        cols_cat = st.columns(5)
        categorias = [
            ("🍕 Pizzas", "Pizzas"),
            ("🍗 Alitas", "Alitas"),
            ("🍔 Hamburguesas", "Hamburguesas"),
            ("🍟 Entradas", "Entradas"),
            ("🥤 Otros", "Otros"),
        ]

        for idx, (label, cat_key) in enumerate(categorias):
            with cols_cat[idx]:
                if st.button(label, key=f"cat_btn_{cat_key}", use_container_width=True):
                    st.session_state.cat_seleccionada = cat_key
                    st.rerun()

        st.markdown("---")

        col_menu, col_carrito = st.columns([1.3, 1])

        # CATÁLOGO DE PRODUCTOS
        with col_menu:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?", (st.session_state.cat_seleccionada,))
            prods = c.fetchall()
            conn.close()

            st.subheader(f"Menú: {st.session_state.cat_seleccionada}")

            with st.container(key="prod_zone"):
                m_col1, m_col2 = st.columns(2)
                for i, (p_id, p_nom, p_precio) in enumerate(prods):
                    col = m_col1 if i % 2 == 0 else m_col2
                    with col:
                        if st.button(f"{p_nom}\nS/ {p_precio:.2f}", key=f"p_{p_id}", use_container_width=True):
                            if p_id in st.session_state.carrito:
                                st.session_state.carrito[p_id]["cant"] += 1
                            else:
                                st.session_state.carrito[p_id] = {
                                    "nombre": p_nom,
                                    "precio": p_precio,
                                    "cant": 1,
                                }
                            st.rerun()

        # CARRITO DE COMPRAS
        with col_carrito:
            st.subheader("🛒 Pedido Actual")

            total_calculado = sum(item["precio"] * item["cant"] for item in st.session_state.carrito.values())

            col_actions_1, col_actions_2 = st.columns([2, 1])
            with col_actions_1:
                btn_cobrar_click = st.button("💰 COBRAR", key="btn_cobrar", use_container_width=True)
            with col_actions_2:
                if st.button("🗑 VACIAR", key="btn_vaciar", use_container_width=True):
                    st.session_state.carrito = {}
                    st.rerun()

            st.markdown(f'<div class="total-box">TOTAL: S/ {total_calculado:.2f}</div>', unsafe_allow_html=True)

            metodo_pago = st.radio("Método de Pago:", ["Efectivo", "Yape", "Plin", "Mixto"], horizontal=True)

            if metodo_pago == "Efectivo" and total_calculado > 0:
                monto_recibido = st.number_input("Monto Entregado (S/):", min_value=total_calculado, value=total_calculado, step=1.0)
                vuelto = monto_recibido - total_calculado
                st.info(f"💵 **Vuelto a entregar: S/ {vuelto:.2f}**")
            elif metodo_pago == "Mixto" and total_calculado > 0:
                efectivo_part = st.number_input("Monto en Efectivo (S/):", min_value=0.0, max_value=total_calculado, value=total_calculado / 2)
                digital_part = total_calculado - efectivo_part
                st.write(f"📲 Yape/Plin restante: **S/ {digital_part:.2f}**")

            if btn_cobrar_click:
                if not st.session_state.carrito:
                    st.error("El carrito está vacío.")
                else:
                    correlativo = obtener_siguiente_correlativo()
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    detalle_str = ", ".join([f"{item['cant']}x {item['nombre']}" for item in st.session_state.carrito.values()])

                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO ventas (correlativo, total, metodo, fecha, detalle) VALUES (?, ?, ?, ?, ?)",
                        (correlativo, total_calculado, metodo_pago, fecha_actual, detalle_str)
                    )
                    conn.commit()
                    conn.close()

                    st.session_state.ultima_venta = {
                        "correlativo": correlativo,
                        "total": total_calculado,
                        "metodo": metodo_pago,
                        "fecha": fecha_actual,
                        "detalle": st.session_state.carrito.copy(),
                    }

                    st.session_state.carrito = {}
                    st.success(f"Venta {correlativo} Registrada Con Éxito!")
                    st.rerun()

            st.markdown("---")

            if st.session_state.carrito:
                items_a_eliminar = []
                for p_id, item in list(st.session_state.carrito.items()):
                    subtotal = item["precio"] * item["cant"]
                    c_info, c_m, c_cant, c_p, c_del = st.columns([3, 0.8, 0.8, 0.8, 0.8])

                    with c_info:
                        st.markdown(f"**{item['nombre']}**\n<small>Unit: S/ {item['precio']:.2f} | Sub: S/ {subtotal:.2f}</small>", unsafe_allow_html=True)

                    if c_m.button("−", key=f"minus_{p_id}"):
                        st.session_state.carrito[p_id]["cant"] -= 1
                        if st.session_state.carrito[p_id]["cant"] <= 0:
                            items_a_eliminar.append(p_id)
                        st.rerun()

                    c_cant.markdown(f"**{item['cant']}**")

                    if c_p.button("+", key=f"plus_{p_id}"):
                        st.session_state.carrito[p_id]["cant"] += 1
                        st.rerun()

                    if c_del.button("🗑", key=f"del_{p_id}"):
                        items_a_eliminar.append(p_id)
                        st.rerun()

                for p_id in items_a_eliminar:
                    if p_id in st.session_state.carrito:
                        del st.session_state.carrito[p_id]
                        st.rerun()
            else:
                st.info("El carrito está vacío. Agrega productos seleccionándolos.")

            if "ultima_venta" in st.session_state:
                st.markdown("---")
                st.subheader("🧾 Última Boleta Emitida")
                uv = st.session_state.ultima_venta
                ticket_txt = f"""
================================
        PILO POS - BOLETA        
================================
Boleta: {uv['correlativo']}
Fecha: {uv['fecha']}
Método: {uv['metodo']}
--------------------------------
"""
                for item in uv["detalle"].values():
                    ticket_txt += f"{item['cant']}x {item['nombre']} - S/ {item['precio']*item['cant']:.2f}\n"
                ticket_txt += f"""--------------------------------
TOTAL: S/ {uv['total']:.2f}
================================"""

                st.code(ticket_txt, language="text")
                st.download_button("🖨️ Imprimir / Descargar Ticket", ticket_txt, file_name=f"ticket_{uv['correlativo']}.txt")

# ---------------------------------------------------------
# PESTAÑA 2: VENTAS DEL DÍA
# ---------------------------------------------------------
with tab2:
    st.subheader("📋 Registro de Ventas Realizadas")
    conn = sqlite3.connect(DB_NAME)
    df_ventas = pd.read_sql_query("SELECT correlativo AS Boleta, detalle AS Detalle, total AS 'Total S/', metodo AS Método, fecha AS Fecha FROM ventas ORDER BY id DESC", conn)
    conn.close()

    if not df_ventas.empty:
        st.dataframe(df_ventas, use_container_width=True)
        total_hoy = df_ventas["Total S/"].sum()
        st.metric("Total Recaudado Hoy", f"S/ {total_hoy:.2f}")
    else:
        st.info("Aún no hay ventas registradas el día de hoy.")

# ---------------------------------------------------------
# PESTAÑA 3: CONTROL DE CAJA
# ---------------------------------------------------------
with tab3:
    st.subheader("🔒 Apertura y Cierre de Caja")
    clave = st.text_input("Contraseña de Administrador", type="password", key="pass_cierre")

    if clave == PIN_ADMIN:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
        caja_activa = c.fetchone()

        df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
        conn.close()

        if caja_activa:
            st.success("🟢 La caja se encuentra ABIERTA")
            st.write(f"**Fecha Apertura:** {caja_activa[3]}")
            st.write(f"**Monto Inicial:** S/ {caja_activa[1]:.2f}")

            tot_efectivo = df_ventas[df_ventas["metodo"] == "Efectivo"]["total"].sum() if not df_ventas.empty else 0
            tot_yape = df_ventas[df_ventas["metodo"] == "Yape"]["total"].sum() if not df_ventas.empty else 0
            tot_plin = df_ventas[df_ventas["metodo"] == "Plin"]["total"].sum() if not df_ventas.empty else 0
            tot_mixto = df_ventas[df_ventas["metodo"] == "Mixto"]["total"].sum() if not df_ventas.empty else 0
            tot_ventas = df_ventas["total"].sum() if not df_ventas.empty else 0

            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💵 Efectivo", f"S/ {tot_efectivo:.2f}")
            c2.metric("📲 Yape", f"S/ {tot_yape:.2f}")
            c3.metric("📲 Plin", f"S/ {tot_plin:.2f}")
            c4.metric("🔀 Mixto", f"S/ {tot_mixto:.2f}")

            st.markdown("---")
            st.metric("💵 Total Efectivo Esperado en Caja", f"S/ {(caja_activa[1] + tot_efectivo):.2f}")

            if st.button("🔒 CERRAR CAJA Y FINALIZAR TURNO", use_container_width=True):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE caja SET monto_final = ?, fecha_cierre = ?, estado = 'CERRADA' WHERE id = ?", (caja_activa[1] + tot_ventas, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), caja_activa[0]))
                conn.commit()
                conn.close()
                st.success("¡Caja Cerrada con Éxito!")
                st.rerun()
        else:
            st.info("La caja actualmente está CERRADA.")
    elif clave:
        st.error("Contraseña incorrecta")

# ---------------------------------------------------------
# PESTAÑA 4: REPORTES Y ESTADÍSTICAS
# ---------------------------------------------------------
with tab4:
    st.subheader("📊 Reportes y Estadísticas de Ventas")
    clave_rep = st.text_input("Contraseña Administrador", type="password", key="pass_rep")

    if clave_rep == PIN_ADMIN:
        conn = sqlite3.connect(DB_NAME)
        df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
        conn.close()

        if not df_ventas.empty:
            total_ventas = df_ventas["total"])
    else:
        st.info("No hay datos de ventas registrados para generar repostes.")
elif clave_rep:
    st.error("contraseña incorrecta")
            
