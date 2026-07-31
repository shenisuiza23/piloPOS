import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pilo POS - Punto de Venta",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PIN_ADMIN = "200423"
DB_NAME = "pilo_pos.db"

# --- ESTADO DE SESIÓN ---
if "carrito" not in st.session_state:
  st.session_state.carrito = {}

# --- ESTILOS CSS PARA REPLICAR LA INTERFAZ EXACTA DE LA IMAGEN ---
st.markdown(
    """
    <style>
    /* Fondo General Oscuro */
    .stApp {
        background-color: #121212;
        color: #ffffff;
    }
    
    /* Ocultar paddings por defecto de Streamlit */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 98%;
    }

    /* BARRA SUPERIOR PRINCIPAL (NARANJA) */
    .top-header {
        background: linear-gradient(90deg, #ff5722 0%, #e64a19 100%);
        padding: 10px 20px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 15px;
    }
    
    .brand-title {
        font-size: 24px;
        font-weight: 900;
        color: white;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .sub-brand {
        font-size: 11px;
        font-weight: bold;
        display: block;
        opacity: 0.9;
        margin-top: -4px;
    }

    /* Caja Info Superior */
    .caja-info {
        background-color: rgba(0,0,0,0.2);
        padding: 5px 15px;
        border-radius: 6px;
        text-align: right;
        font-size: 13px;
        color: white;
    }

    /* CARDS DE PRODUCTOS */
    .card-prod {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        border: 1px solid #2a2a2a;
        margin-bottom: 10px;
    }
    
    .img-placeholder {
        width: 100%;
        height: 80px;
        background-color: #2c2c2c;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        margin-bottom: 6px;
    }
    
    .prod-name {
        font-size: 12px;
        font-weight: 700;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    
    .prod-price {
        font-size: 13px;
        font-weight: 800;
        color: #29b6f6;
        margin: 4px 0;
    }

    /* DISPLAY DE TOTAL A PAGAR (VERDE) */
    .total-display-container {
        background-color: #0b140c;
        border: 1px solid #1b431e;
        padding: 10px 15px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 10px 0;
    }
    
    .total-title {
        font-size: 14px;
        font-weight: 800;
        color: #a5d6a7;
    }
    
    .total-amount {
        font-size: 32px;
        font-weight: 900;
        color: #4caf50;
    }

    /* DISPLAY DE VUELTO */
    .vuelto-container {
        background-color: #051923;
        border: 1px solid #004e64;
        padding: 8px 15px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
    }

    /* BOTONES COBRAR Y VACIAR */
    div[data-testid="stKey-btn_cobrar_header"] > button {
        background-color: #4caf50 !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        height: 48px !important;
        border-radius: 6px !important;
        border: none !important;
    }
    
    div[data-testid="stKey-btn_vaciar_header"] > button {
        background-color: #f44336 !important;
        color: white !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        height: 48px !important;
        border-radius: 6px !important;
        border: none !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- INICIALIZACIÓN DE LA BASE DE DATOS ---
def inicializar_bd():
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 50,
            emoji TEXT DEFAULT '🍔'
        )
    """)
  c.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlativo TEXT,
            total REAL,
            metodo TEXT,
            monto_efectivo REAL,
            monto_digital REAL,
            fecha TEXT,
            detalle TEXT
        )
    """)

  c.execute("SELECT COUNT(*) FROM productos")
  if c.fetchone()[0] == 0:
    prods = [
        ("Pizza Americana Personal", "Pizzas", 25.00, 50, "🍕"),
        ("Pizza Hawaiana Personal", "Pizzas", 25.00, 50, "🍕"),
        ("Pizza Pepperoni Personal", "Pizzas", 25.00, 50, "🍕"),
        ("Pizza Pilo Personal", "Pizzas", 28.00, 50, "🍕"),
        ("Pizza Americana Familiar", "Pizzas", 45.00, 50, "🍕"),
        ("Pizza Hawaiana Familiar", "Pizzas", 45.00, 50, "🍕"),
        ("Pizza Pepperoni Familiar", "Pizzas", 45.00, 50, "🍕"),
        ("Pizza Pilo Familiar", "Pizzas", 50.00, 50, "🍕"),
        ("Alitas Rebozadas", "Alitas", 20.00, 50, "🍗"),
        ("Alitas BBQ", "Alitas", 22.00, 50, "🍗"),
        ("Alitas Acevichadas", "Alitas", 22.00, 50, "🍗"),
        ("Alitas Búfalo", "Alitas", 22.00, 50, "🍗"),
        ("Hamburguesa Clásica", "Hamburguesas", 6.00, 50, "🍔"),
        ("Hamburguesa Pilo", "Hamburguesas", 9.00, 50, "🍔"),
        ("Salchipapa Clásica", "Entradas", 8.00, 50, "🍟"),
        ("Coca Cola", "Otros", 5.00, 50, "🥤"),
    ]
    c.executemany(
        "INSERT INTO productos (nombre, categoria, precio, stock, emoji) VALUES"
        " (?, ?, ?, ?, ?)",
        prods,
    )

  conn.commit()
  conn.close()


inicializar_bd()


# --- HEADER SUPERIOR COMPACTO TIPO RESTAURANTE ---
def render_header():
  st.markdown(
      """
        <div class="top-header">
            <div class="brand-title">
                🔥 PILO POS
                <span class="sub-brand">PUNTO DE VENTA</span>
            </div>
            <div class="caja-info">
                🟢 <b>Caja Abierta</b><br>
                <small>S/ 200.00 | Inicio: 08:00 AM</small>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )


render_header()

# --- DISPOSICIÓN EN DOS COLUMNAS (MENÚ IZQUIERDA / PEDIDO DERECHA) ---
col_menu, col_pedido = st.columns([1.5, 1])

# ---------------------------------------------------------
# COLUMNA IZQUIERDA: CATÁLOGO Y PRODUCTOS
# ---------------------------------------------------------
with col_menu:
  tabs = st.tabs(
      ["🍕 PIZZAS", "🍗 ALITAS", "🍔 HAMBURGUESAS", "🍟 ENTRADAS", "🥤 OTROS"]
  )
  categorias = ["Pizzas", "Alitas", "Hamburguesas", "Entradas", "Otros"]

  for tab, cat in zip(tabs, categorias):
    with tab:
      conn = sqlite3.connect(DB_NAME)
      c = conn.cursor()
      prods = c.execute(
          "SELECT id, nombre, precio, emoji FROM productos WHERE categoria = ?",
          (cat,),
      ).fetchall()
      conn.close()

      # Grid de 4 columnas como en la imagen
      for i in range(0, len(prods), 4):
        cols = st.columns(4)
        for col, (p_id, p_nom, p_precio, p_emoji) in zip(cols, prods[i : i + 4]):
          with col:
            st.markdown(
                f"""
                            <div class="card-prod">
                                <div class="img-placeholder">{p_emoji}</div>
                                <div class="prod-name">{p_nom}</div>
                                <div class="prod-price">S/ {p_precio:.2f}</div>
                            </div>
                        """,
                unsafe_allow_html=True,
            )

            # Controles de incremento (+ / -) por producto en catálogo
            c1, c2, c3 = st.columns([1, 1, 1])
            if c1.button("−", key=f"cat_m_{p_id}"):
              if (
                  p_id in st.session_state.carrito
                  and st.session_state.carrito[p_id]["cant"] > 0
              ):
                st.session_state.carrito[p_id]["cant"] -= 1
                if st.session_state.carrito[p_id]["cant"] == 0:
                  del st.session_state.carrito[p_id]
                st.rerun()

            cant_actual = (
                st.session_state.carrito[p_id]["cant"]
                if p_id in st.session_state.carrito
                else 0
            )
            c2.markdown(
                f"<div style='text-align:center; font-weight:bold; padding-top:4px;'>{cant_actual}</div>",
                unsafe_allow_html=True,
            )

            if c3.button("+", key=f"cat_p_{p_id}"):
              if p_id in st.session_state.carrito:
                st.session_state.carrito[p_id]["cant"] += 1
              else:
                st.session_state.carrito[p_id] = {
                    "nombre": p_nom,
                    "precio": p_precio,
                    "cant": 1,
                    "emoji": p_emoji,
                }
              st.rerun()

# ---------------------------------------------------------
# COLUMNA DERECHA: PEDIDO ACTUAL Y METODOS DE PAGO
# ---------------------------------------------------------
with col_pedido:
  # Botones SUPERIORES COBRAR Y VACIAR
  col_b1, col_b2 = st.columns([1.6, 1])
  btn_cobrar = col_b1.button(
      "💵 COBRAR", key="btn_cobrar_header", use_container_width=True
  )
  btn_vaciar = col_b2.button(
      "🗑️ VACIAR CARRITO", key="btn_vaciar_header", use_container_width=True
  )

  if btn_vaciar:
    st.session_state.carrito = {}
    st.rerun()

  st.markdown(
      "<div style='font-size:13px; font-weight:bold; color:#888;"
      " margin-top:10px;'>PEDIDO ACTUAL</div>",
      unsafe_allow_html=True,
  )

  # TABLA DE PRODUCTOS SELECCIONADOS
  if st.session_state.carrito:
    for p_id, item in list(st.session_state.carrito.items()):
      subtotal = item["precio"] * item["cant"]
      c_img, c_info, c_m, c_cant, c_p, c_del = st.columns(
          [0.8, 3, 0.8, 0.8, 0.8, 0.8]
      )

      c_img.write(item["emoji"])
      c_info.markdown(
          f"<div style='font-size:12px; font-weight:bold;'>{item['nombre']}<br><span"
          f" style='color:#888;'>S/ {item['precio']:.2f}</span></div>",
          unsafe_allow_html=True,
      )

      if c_m.button("−", key=f"ped_m_{p_id}"):
        item["cant"] -= 1
        if item["cant"] <= 0:
          del st.session_state.carrito[p_id]
        st.rerun()

      c_cant.markdown(
        f"<div style='text-align:center; font-size:13px; margin-top:4px;'>{item['cant']}</div>",
        unsafe_allow_html=True,
      )

      if c_p.button("+", key=f"ped_p_{p_id}"):
        item["cant"] += 1
        st.rerun()

      if c_del.button("🗑️", key=f"ped_del_{p_id}"):
        del st.session_state.carrito[p_id]
        st.rerun()
  else:
    st.info("El carrito está vacío.")

  # TOTAL A PAGAR
  total = sum(
      item["precio"] * item["cant"]
      for item in st.session_state.carrito.values()
  )
  st.markdown(
      f"""
        <div class="total-display-container">
            <span class="total-title">TOTAL A PAGAR</span>
            <span class="total-amount">S/ {total:.2f}</span>
        </div>
    """,
      unsafe_allow_html=True,
  )

  # MÉTODO DE PAGO
  metodo = st.radio(
      "MÉTODO DE PAGO",
      ["💵 EFECTIVO", "📲 YAPE", "📲 PLIN", "💳 MIXTO"],
      horizontal=True,
  )

  monto_recibido = total
  vuelto = 0.0

  if "EFECTIVO" in metodo:
    c_monto, c_vuelto = st.columns(2)
    with c_monto:
      monto_recibido = st.number_input(
          "MONTO RECIBIDO", min_value=0.0, value=float(total), step=1.0
      )
    vuelto = max(0.0, monto_recibido - total)
    with c_vuelto:
      st.markdown(
          f"""
                <div class="vuelto-container">
                    <span style="font-size:11px; font-weight:bold; color:#81d4fa;">VUELTO</span>
                    <span style="font-size:20px; font-weight:900; color:#29b6f6;">S/ {vuelto:.2f}</span>
                </div>
            """,
          unsafe_allow_html=True,
      )

  # PROCESAR VENTA
  if btn_cobrar:
    if not st.session_state.carrito:
      st.warning("Agrega productos antes de cobrar.")
    else:
      st.success(f"¡Venta procesada con éxito! Total: S/ {total:.2f}")
      st.session_state.carrito = {}
      st.rerun()
