import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from database import DB_NAME, inicializar_bd, obtener_siguiente_correlativo

st.set_page_config(page_title="PILO POS", page_icon="🍗", layout="wide", initial_sidebar_state="collapsed")

PIN_ADMIN = "200423"

if "cat_seleccionada" not in st.session_state:
    st.session_state.cat_seleccionada = "Pizzas"
if "carrito" not in st.session_state:
    st.session_state.carrito = {}

COLORES = {
    "Pizzas": {"bg": "#2b5c8f", "text": "#ffffff"},
    "Alitas": {"bg": "#c69214", "text": "#ffffff"},
    "Hamburguesas": {"bg": "#d97724", "text": "#ffffff"},
    "Entradas": {"bg": "#2e7d32", "text": "#ffffff"},
    "Otros": {"bg": "#0284c7", "text": "#ffffff"},
}

bg_actual = COLORES[st.session_state.cat_seleccionada]["bg"]
text_actual = COLORES[st.session_state.cat_seleccionada]["text"]

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }}
    .pilo-navbar {{ background: linear-gradient(90deg, #ea580c 0%, #d97724 100%); color: white; padding: 14px 24px; border-radius: 12px; margin-bottom: 15px; }}
    .pilo-navbar h1 {{ margin: 0; font-size: 26px; font-weight: 900; color: white !important; }}
    div.stButton > button {{ font-weight: bold !important; border-radius: 10px !important; border: none !important; }}
    div[data-testid="stKey-cat_btn_Pizzas"] button {{ background-color: #2b5c8f !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Alitas"] button {{ background-color: #c69214 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Hamburguesas"] button {{ background-color: #d97724 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Entradas"] button {{ background-color: #2e7d32 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-cat_btn_Otros"] button {{ background-color: #0284c7 !important; color: white !important; font-size: 18px !important; height: 50px !important; }}
    div[data-testid="stKey-prod_zone"] div.stButton > button {{ background-color: {bg_actual} !important; color: {text_actual} !important; min-height: 85px !important; font-size: 17px !important; width: 100% !important; }}
    div[data-testid="stKey-btn_cobrar"] button {{ background-color: #16a34a !important; color: white !important; font-size: 20px !important; height: 55px !important; width: 100% !important; }}
    div[data-testid="stKey-btn_vaciar"] button {{ background-color: #dc2626 !important; color: white !important; font-size: 16px !important; height: 55px !important; width: 100% !important; }}
    .total-box {{ background-color: #15803d; color: #ffffff; padding: 12px; border-radius: 10px; text-align: center; font-size: 32px; font-weight: 900; margin: 10px 0; }}
    </style>
""", unsafe_allow_html=True)

inicializar_bd()

st.markdown('<div class="pilo-navbar"><h1>🍗 PILO POS - Punto de Venta</h1></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Punto de Venta", "📋 Ventas del Día", "🔒 Control de Caja", "📊 Reportes"])

# --- TAB 1 ---
with tab1:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
    caja_activa = c.fetchone()
    conn.close()

    if not caja_activa:
        st.warning("⚠️ La caja está CERRADA. Abre caja para iniciar.")
        c1, c2 = st.columns(2)
        clave_apertura = c1.text_input("Contraseña Administrador", type="password", key="pass_open")
        monto_ini = c2.number_input("Monto Inicial (S/):", min_value=0.0, value=0.0)

        if st.button("🔓 ABRIR CAJA", use_container_width=True):
            if clave_apertura == PIN_ADMIN:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO caja (monto_inicial, fecha_apertura, estado) VALUES (?, ?, 'ABIERTA')", (monto_ini, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("¡Caja abierta!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    else:
        cols_cat = st.columns(5)
        categorias = [("🍕 Pizzas", "Pizzas"), ("🍗 Alitas", "Alitas"), ("🍔 Hamburguesas", "Hamburguesas"), ("🍟 Entradas", "Entradas"), ("🥤 Otros", "Otros")]
        for idx, (label, cat_key) in enumerate(categorias):
            if cols_cat[idx].button(label, key=f"cat_btn_{cat_key}", use_container_width=True):
                st.session_state.cat_seleccionada = cat_key
                st.rerun()

        st.markdown("---")
        col_menu, col_carrito = st.columns([1.3, 1])

        with col_menu:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?", (st.session_state.cat_seleccionada,))
            prods = c.fetchall()
            conn.close()

            st.subheader(f"Menú: {st.session_state.cat_seleccionada}")
            with st.container(key="prod_zone"):
                m1, m2 = st.columns(2)
                for i, (p_id, p_nom, p_precio) in enumerate(prods):
                    col = m1 if i % 2 == 0 else m2
                    if col.button(f"{p_nom}\nS/ {p_precio:.2f}", key=f"p_{p_id}", use_container_width=True):
                        if p_id in st.session_state.carrito:
                            st.session_state.carrito[p_id]["cant"] += 1
                        else:
                            st.session_state.carrito[p_id] = {"nombre": p_nom, "precio": p_precio, "cant": 1}
                        st.rerun()

        with col_carrito:
            st.subheader("🛒 Pedido Actual")
            total_calculado = sum(item["precio"] * item["cant"] for item in st.session_state.carrito.values())

            c_act1, c_act2 = st.columns([2, 1])
            btn_cobrar = c_act1.button("💰 COBRAR", key="btn_cobrar", use_container_width=True)
            if c_act2.button("🗑 VACIAR", key="btn_vaciar", use_container_width=True):
                st.session_state.carrito = {}
                st.rerun()

            st.markdown(f'<div class="total-box">TOTAL: S/ {total_calculado:.2f}</div>', unsafe_allow_html=True)
            metodo_pago = st.radio("Método de Pago:", ["Efectivo", "Yape", "Plin", "Mixto"], horizontal=True)

            if metodo_pago == "Efectivo" and total_calculado > 0:
                monto_rec = st.number_input("Monto Entregado (S/):", min_value=total_calculado, value=total_calculado)
                st.info(f"💵 Vuelto: S/ {monto_rec - total_calculado:.2f}")

            if btn_cobrar:
                if not st.session_state.carrito:
                    st.error("Carrito vacío")
                else:
                    correlativo = obtener_siguiente_correlativo()
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    detalle_str = ", ".join([f"{item['cant']}x {item['nombre']}" for item in st.session_state.carrito.values()])

                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO ventas (correlativo, total, metodo, fecha, detalle) VALUES (?, ?, ?, ?, ?)", (correlativo, total_calculado, metodo_pago, fecha_actual, detalle_str))
                    conn.commit()
                    conn.close()

                    st.session_state.ultima_venta = {"correlativo": correlativo, "total": total_calculado, "metodo": metodo_pago, "fecha": fecha_actual, "detalle": st.session_state.carrito.copy()}
                    st.session_state.carrito = {}
                    st.success("¡Venta Registrada!")
                    st.rerun()

            st.markdown("---")
            if st.session_state.carrito:
                for p_id, item in list(st.session_state.carrito.items()):
                    c_inf, c_m, c_cant, c_p, c_del = st.columns([3, 0.8, 0.8, 0.8, 0.8])
                    c_inf.markdown(f"**{item['nombre']}**\n<small>S/ {item['precio']:.2f}</small>", unsafe_allow_html=True)
                    if c_m.button("−", key=f"m_{p_id}"):
                        st.session_state.carrito[p_id]["cant"] -= 1
                        if st.session_state.carrito[p_id]["cant"] <= 0:
                            del st.session_state.carrito[p_id]
                        st.rerun()
                    c_cant.markdown(f"**{item['cant']}**")
                    if c_p.button("+", key=f"p_{p_id}"):
                        st.session_state.carrito[p_id]["cant"] += 1
                        st.rerun()
                    if c_del.button("🗑", key=f"d_{p_id}"):
                        del st.session_state.carrito[p_id]
                        st.rerun()

# --- TAB 2 ---
with tab2:
    st.subheader("📋 Ventas Realizadas")
    conn = sqlite3.connect(DB_NAME)
    df_v = pd.read_sql_query("SELECT correlativo AS Boleta, detalle AS Detalle, total AS 'Total S/', metodo AS Método, fecha AS Fecha FROM ventas ORDER BY id DESC", conn)
    conn.close()

    if not df_v.empty:
        st.dataframe(df_v, use_container_width=True)
        st.metric("Total Hoy", f"S/ {df_v['Total S/'].sum():.2f}")
    else:
        st.info("Sin ventas aún.")

# --- TAB 3 ---
with tab3:
    st.subheader("🔒 Control de Caja")
    if st.text_input("Contraseña Admin", type="password", key="p_caja") == PIN_ADMIN:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
        caja_activa = c.fetchone()
        df_v = pd.read_sql_query("SELECT * FROM ventas", conn)
        conn.close()

        if caja_activa:
            st.success("🟢 Caja ABIERTA")
            tot_v = df_v["total"].sum() if not df_v.empty else 0
            if st.button("🔒 CERRAR CAJA", use_container_width=True):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE caja SET monto_final = ?, fecha_cierre = ?, estado = 'CERRADA' WHERE id = ?", (caja_activa[1] + tot_v, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), caja_activa[0]))
                conn.commit()
                conn.close()
                st.success("Caja Cerrada")
                st.rerun()

# --- TAB 4 ---
with tab4:
    st.subheader("📊 Reportes")
    if st.text_input("Contraseña Admin", type="password", key="p_rep") == PIN_ADMIN:
        conn = sqlite3.connect(DB_NAME)
        df_v = pd.read_sql_query("SELECT * FROM ventas", conn)
        conn.close()
        if not df_v.empty:
            st.metric("Ventas Totales", f"S/ {df_v['total'].sum():.2f}")
            st.bar_chart(df_v["metodo"].value_counts())
