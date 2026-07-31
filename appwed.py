import streamlit as st
import sqlite3
import pandas as pd
from database import DB_NAME, inicializar_bd, registrar_venta

st.set_page_config(page_title="Pilo POS", page_icon="🍔", layout="wide", initial_sidebar_state="collapsed")
PIN_ADMIN = "200423"
inicializar_bd()

if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# --- ESTILOS COMPACTOS ---
st.markdown("""
    <style>
    .pilo-header { background: linear-gradient(90deg, #d97724, #ea580c); padding: 12px 20px; border-radius: 10px; color: white; display: flex; justify-content: space-between; margin-bottom: 15px; }
    .total-display { background: #0f172a; color: #22c55e; padding: 10px; border-radius: 10px; text-align: center; font-size: 28px; font-weight: 900; border: 2px solid #22c55e; margin: 10px 0; }
    div[data-testid="stKey-btn_cobrar_top"] button { background-color: #16a34a !important; color: white !important; font-size: 22px !important; font-weight: 900 !important; height: 70px !important; }
    div[data-testid="stKey-btn_vaciar_top"] button { background-color: #dc2626 !important; color: white !important; font-size: 18px !important; height: 70px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="pilo-header"><h2 style="margin:0;">🍔 Pilo POS</h2><b>Sistema Touch</b></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛒 Punto de Venta", "📋 Ventas", "🔒 Caja"])

# --- RENDERIZAR BOTONES GRANDES ---
def renderizar_cat(categoria, color):
    conn = sqlite3.connect(DB_NAME)
    prods = conn.cursor().execute("SELECT id, nombre, precio, stock FROM productos WHERE categoria = ?", (categoria,)).fetchall()
    conn.close()
    
    for i in range(0, len(prods), 2):
        cols = st.columns(2)
        for col, (p_id, p_nom, p_precio, p_stock) in zip(cols, prods[i:i+2]):
            with col:
                st.markdown(f'<style>div[data-testid="stKey-p_{p_id}"] button {{ background:{color} !important; color:white !important; height:90px !important; font-size:16px !important; font-weight:bold !important; }}</style>', unsafe_allow_html=True)
                if st.button(f"{p_nom}\n\nS/ {p_precio:.2f} | Stock: {p_stock}", key=f"p_{p_id}", use_container_width=True):
                    st.session_state.carrito[p_id] = st.session_state.carrito.get(p_id, {"nombre": p_nom, "precio": p_precio, "cant": 0})
                    st.session_state.carrito[p_id]["cant"] += 1
                    st.rerun()

with tab1:
    col_menu, col_carrito = st.columns([1.5, 1])
    
    with col_menu:
        subtabs = st.tabs(["🍕 Pizzas", "🍗 Alitas", "🍔 Burgers", "🍟 Entradas", "➕ Extras", "🥤 Bebidas"])
        cats = [("Pizzas", "#2b5c8f"), ("Alitas", "#d97706"), ("Hamburguesas", "#d97724"), ("Entradas", "#2e7d32"), ("Extras", "#7e22ce"), ("Bebidas", "#0284c7")]
        for sub, (cat, col) in zip(subtabs, cats):
            with sub: renderizar_cat(cat, col)

    with col_carrito:
        c1, c2 = st.columns([1.8, 1])
        btn_cobrar = c1.button("🚀 COBRAR", key="btn_cobrar_top", use_container_width=True)
        btn_vaciar = c2.button("🗑️ VACIAR", key="btn_vaciar_top", use_container_width=True)
        
        total = sum(i["precio"] * i["cant"] for i in st.session_state.carrito.values())
        st.markdown(f'<div class="total-display">TOTAL: S/ {total:.2f}</div>', unsafe_allow_html=True)
        
        metodo = st.radio("Pago:", ["Efectivo", "Yape", "Plin", "Mixto"], horizontal=True)
        
        m_ef, m_dig = total, 0.0
        if metodo == "Efectivo":
            entregado = st.number_input("Entregado:", min_value=0.0, value=float(total))
            st.info(f"💵 Vuelto: S/ {max(0.0, entregado - total):.2f}")
        elif metodo == "Mixto":
            m_ef = st.number_input("Efectivo:", min_value=0.0, max_value=float(total), value=float(total/2))
            m_dig = total - m_ef
        else: m_dig = total

        if btn_vaciar:
            st.session_state.carrito = {}
            st.rerun()

        if btn_cobrar:
            if not st.session_state.carrito:
                st.warning("Carrito vacío")
            else:
                correlativo = registrar_venta(total, metodo, m_ef, m_dig, st.session_state.carrito)
                st.session_state.carrito = {}
                st.success(f"¡Venta {correlativo} Cobrada!")
                st.rerun()

        st.markdown("---")
        for p_id, item in list(st.session_state.carrito.items()):
            c_desc, c_m, c_cant, c_p = st.columns([3, 1, 1, 1])
            c_desc.write(f"**{item['nombre']}** (S/ {item['precio']:.2f})")
            if c_m.button("−", key=f"m_{p_id}"):
                item["cant"] -= 1
                if item["cant"] <= 0: del st.session_state.carrito[p_id]
                st.rerun()
            c_cant.write(f"**{item['cant']}**")
            if c_p.button("+", key=f"p_add_{p_id}"):
                item["cant"] += 1
                st.rerun()

with tab2:
    st.subheader("📋 Ventas del Día")
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT correlativo AS Boleta, detalle AS Detalle, total AS Total, metodo AS Método, fecha AS Fecha FROM ventas ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True)
    except: st.write("Sin ventas.")
    conn.close()

with tab3:
    st.subheader("🔒 Control de Caja")
    if st.text_input("Clave:", type="password") == PIN_ADMIN:
        st.success("Acceso Administrador Autorizado")
