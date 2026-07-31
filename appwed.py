import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Pilo POS",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PIN_ADMIN = "200423"
DB_NAME = "pilo_pos.db"

# --- ESTADO DE SESIÓN ---
if "carrito" not in st.session_state:
  st.session_state.carrito = {}

# --- ESTILOS CSS ADAPTADOS PARA PANTALLA TÁCTIL ---
st.markdown(
    """
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #0b131f;
        color: #ffffff;
    }
    
    /* Barra Superior PILO POS Naranja */
    .pilo-header {
        background: linear-gradient(90deg, #d97724 0%, #ea580c 100%);
        padding: 15px 25px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0px 4px 12px rgba(234, 88, 12, 0.4);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .pilo-title {
        font-size: 26px;
        font-weight: 800;
        margin: 0;
    }
    
    /* Display del Total turquesa */
    .total-banner {
        background-color: #00f5d4;
        color: #000000;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-size: 28px;
        font-weight: 900;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0, 245, 212, 0.4);
    }
    
    /* Banner informativo de Vuelto */
    .vuelto-banner {
        background-color: #00b4d8;
        color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-size: 18px;
        font-weight: 700;
        margin-top: 10px;
    }

    /* Botón COBRAR gigante superior */
    div[data-testid="stKey-btn_cobrar_top"] > button {
        background-color: #16a34a !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 75px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 10px rgba(22, 163, 74, 0.4) !important;
    }

    /* Botón VACIAR grande superior */
    div[data-testid="stKey-btn_vaciar_top"] > button {
        background-color: #dc2626 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 75px !important;
        border-radius: 12px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- BASE DE DATOS E INICIALIZACIÓN ---
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
            monto_efectivo REAL DEFAULT 0.0,
            monto_digital REAL DEFAULT 0.0,
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
        # 🍕 PIZZAS
        ("Pizza Americana Personal", "Pizzas", 25.00, 50),
        ("Pizza Hawaiana Personal", "Pizzas", 25.00, 50),
        ("Pizza Pepperoni Personal", "Pizzas", 25.00, 50),
        ("Pizza Pilo Personal", "Pizzas", 28.00, 50),
        ("Pizza Americana Familiar", "Pizzas", 45.00, 50),
        ("Pizza Hawaiana Familiar", "Pizzas", 45.00, 50),
        ("Pizza Pepperoni Familiar", "Pizzas", 45.00, 50),
        ("Pizza Pilo Familiar", "Pizzas", 50.00, 50),
        # 🍗 ALITAS
        ("Alitas Rebozadas", "Alitas", 20.00, 50),
        ("Alitas BBQ", "Alitas", 22.00, 50),
        ("Alitas Acevichadas", "Alitas", 22.00, 50),
        ("Alitas Búfalo", "Alitas", 22.00, 50),
        ("Alitas Pilo", "Alitas", 24.00, 50),
        # 🍔 HAMBURGUESAS
        ("Hamburguesa Clásica", "Hamburguesas", 6.00, 50),
        ("Hamburguesa Hawaiana", "Hamburguesas", 8.00, 50),
        ("Hamburguesa A lo Pilo", "Hamburguesas", 9.00, 50),
        ("Hamburguesa A lo Pobre", "Hamburguesas", 10.00, 50),
        ("Hamburguesa Royal", "Hamburguesas", 14.00, 50),
        ("Hamburguesa Mega Pilo", "Hamburguesas", 16.00, 50),
        # 🍟 ENTRADAS
        ("Choripán", "Entradas", 6.00, 50),
        ("Salchipapa Clásica", "Entradas", 8.00, 50),
        ("Salchalita", "Entradas", 16.00, 50),
        # ➕ EXTRAS
        ("Porción de Papa", "Extras", 5.00, 50),
        ("Porción de Maduro", "Extras", 5.00, 50),
        ("Porción de Alita", "Extras", 4.00, 50),
        ("Porción de Carne de Hamburguesa", "Extras", 3.00, 50),
        ("Porción de Huevo", "Extras", 1.00, 50),
        ("Porción de Tocino", "Extras", 1.00, 50),
        ("Porción de Jamón", "Extras", 1.00, 50),
        ("Porción de Queso", "Extras", 1.00, 50),
        # 🥤 BEBIDAS
        ("Inca Kola", "Bebidas", 5.00, 50),
        ("Coca Cola", "Bebidas", 5.00, 50),
        ("Chicha Morada", "Bebidas", 3.00, 50),
        ("Cocona", "Bebidas", 3.00, 50),
        ("Agua Mineral", "Bebidas", 2.00, 50),
    ]
    cursor.executemany(
        "INSERT INTO productos (nombre, categoria, precio, stock) VALUES"
        " (?, ?, ?, ?)",
        productos_defecto,
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


# --- RENDERIZADO DE BOTONES TÁCTILES POR CATEGORÍA ---
def renderizar_grid_productos(categoria, color_hex, num_cols=2):
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute(
      "SELECT id, nombre, precio, stock FROM productos WHERE categoria = ?",
      (categoria,),
  )
  prods = c.fetchall()
  conn.close()

  if not prods:
    st.info(f"No hay productos en {categoria}.")
    return

  for i in range(0, len(prods), num_cols):
    grupo = prods[i : i + num_cols]
    cols = st.columns(num_cols)
    for col, (p_id, p_nom, p_precio, p_stock) in zip(cols, grupo):
      with col:
        # Estilo para convertir todo el botón del producto en una tarjeta táctil gigante del color seleccionado
        st.markdown(
            f"""
                    <style>
                    div[data-testid="stKey-prod_{p_id}"] button {{
                        background: {color_hex} !important;
                        color: white !important;
                        height: 95px !important;
                        white-space: pre-wrap !important;
                        font-size: 16px !important;
                        font-weight: 800 !important;
                        border: none !important;
                        box-shadow: 0px 4px 8px rgba(0,0,0,0.3) !important;
                        margin-bottom: 8px !important;
                    }}
                    </style>
                """,
            unsafe_allow_html=True,
        )

        # Al pulsar en CUALQUIER PARTE de la tarjeta se agrega directamente
        if st.button(
            f"{p_nom}\n\nS/ {p_precio:.2f}  |  Stock: {p_stock}",
            key=f"prod_{p_id}",
            use_container_width=True,
        ):
          if p_id in st.session_state.carrito:
            st.session_state.carrito[p_id]["cant"] += 1
          else:
            st.session_state.carrito[p_id] = {
                "nombre": p_nom,
                "precio": p_precio,
                "cant": 1,
            }
          st.rerun()


# Inicialización
inicializar_bd()

# --- HEADER SUPERIOR (COLOR NARANJA PILO) ---
st.markdown(
    """
    <div class="pilo-header">
        <div class="pilo-title">🍔 Pilo POS</div>
        <div style="font-size: 15px; font-weight: bold;">Sistema Touch de Venta</div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- NAVEGACIÓN ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["🛒 Punto de Venta", "📋 Ventas del Día", "🔒 Control de Caja", "📊 Reportes"]
)

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
    st.warning(
        "⚠️ La caja está CERRADA. Inicia sesión de caja para empezar a vender."
    )
    col_c1, col_c2 = st.columns(2)
    with col_c1:
      clave_apertura = st.text_input(
          "Contraseña Administrador", type="password", key="pass_open"
      )
    with col_c2:
      monto_ini = st.number_input(
          "Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0
      )

    if st.button("🔓 ABRIR CAJA", use_container_width=True):
      if clave_apertura == PIN_ADMIN:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO caja (monto_inicial, fecha_apertura, estado) VALUES"
            " (?, ?, 'ABIERTA')",
            (monto_ini, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        conn.close()
        st.success("¡Caja abierta exitosamente!")
        st.rerun()
      else:
        st.error("Contraseña incorrecta")
  else:
    col_menu, col_carrito = st.columns([1.6, 1])

    # --- MENÚ DE PRODUCTOS ---
    with col_menu:
      subtabs = st.tabs([
          "🍕 Pizzas",
          "🍗 Alitas",
          "🍔 Hamburguesas",
          "🍟 Entradas",
          "➕ Extras",
          "🥤 Bebidas",
      ])
      cats = [
          ("Pizzas", "linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)"),
          ("Alitas", "linear-gradient(135deg, #b45309 0%, #f59e0b 100%)"),
          ("Hamburguesas", "linear-gradient(135deg, #c2410c 0%, #ea580c 100%)"),
          ("Entradas", "linear-gradient(135deg, #15803d 0%, #22c55e 100%)"),
          ("Extras", "linear-gradient(135deg, #6b21a8 0%, #a855f7 100%)"),
          ("Bebidas", "linear-gradient(135deg, #0369a1 0%, #0ea5e9 100%)"),
      ]

      for subtab, (cat, color_hex) in zip(subtabs, cats):
        with subtab:
          renderizar_grid_productos(cat, color_hex, num_cols=2)

    # --- PANEL DE CARRITO ---
    with col_carrito:
      # --- BOTONES PRINCIPALES COBRAR Y VACIAR (EN LA PARTE SUPERIOR) ---
      col_b1, col_b2 = st.columns([1.8, 1])
      with col_b1:
        btn_cobrar = st.button(
            "🚀 COBRAR", key="btn_cobrar_top", use_container_width=True
        )
      with col_b2:
        btn_vaciar = st.button(
            "🗑️ VACIAR", key="btn_vaciar_top", use_container_width=True
        )

      total = sum(
          item["precio"] * item["cant"]
          for item in st.session_state.carrito.values()
      )

      st.markdown(
          f'<div class="total-banner">TOTAL A PAGAR: S/ {total:.2f}</div>',
          unsafe_allow_html=True,
      )

      metodo_pago = st.radio(
          "Método de Pago:", ["Efectivo", "Yape", "Plin", "Mixto"], horizontal=True
      )

      monto_efectivo = total
      monto_digital = 0.0
      vuelto = 0.0

      if metodo_pago == "Efectivo":
        monto_entregado = st.number_input(
            "Monto Entregado (S/):",
            min_value=0.0,
            value=float(total),
            step=1.0,
        )
        vuelto = max(0.0, monto_entregado - total)
        monto_efectivo = total
        st.markdown(
            '<div class="vuelto-banner">💵 Vuelto a Entregar: S/'
            f" {vuelto:.2f}</div>",
            unsafe_allow_html=True,
        )

      elif metodo_pago == "Mixto":
        monto_efectivo = st.number_input(
            "Monto en Efectivo (S/):",
            min_value=0.0,
            max_value=float(total),
            value=float(total / 2),
        )
        monto_digital = total - monto_efectivo
        st.info(f"📲 Yape / Plin a cobrar: S/ {monto_digital:.2f}")
      else:
        monto_digital = total
        monto_efectivo = 0.0

      # ACCIONES DE NAVEGACIÓN AL PRESIONAR BOTONES SUPERIORES
      if btn_vaciar:
        st.session_state.carrito = {}
        st.rerun()

      if btn_cobrar:
        if not st.session_state.carrito:
          st.warning("⚠️ El carrito está vacío.")
        else:
          correlativo = obtener_siguiente_correlativo()
          fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          detalle_str = ", ".join([
              f"{item['cant']}x {item['nombre']}"
              for item in st.session_state.carrito.values()
          ])

          conn = sqlite3.connect(DB_NAME)
          c = conn.cursor()

          c.execute(
              """
                        INSERT INTO ventas (correlativo, total, metodo, monto_efectivo, monto_digital, fecha, detalle) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  correlativo,
                  total,
                  metodo_pago,
                  monto_efectivo,
                  monto_digital,
                  fecha_actual,
                  detalle_str,
              ),
          )

          conn.commit()
          conn.close()

          st.session_state.ultima_venta = {
              "correlativo": correlativo,
              "total": total,
              "metodo": metodo_pago,
              "fecha": fecha_actual,
              "detalle": st.session_state.carrito.copy(),
          }
          st.session_state.carrito = {}
          st.success(f"¡Venta {correlativo} registrada correctamente!")
          st.rerun()

      # DETALLE DE PRODUCTOS SELECCIONADOS EN CARRITO
      st.markdown("---")
      if st.session_state.carrito:
        st.write("**Productos en Carrito:**")
        items_a_eliminar = []
        for p_id, item in st.session_state.carrito.items():
          c_desc, c_btn1, c_cant, c_btn2, c_del = st.columns([3, 1, 1, 1, 1])
          c_desc.write(f"**{item['nombre']}**\nS/ {item['precio']:.2f}")

          if c_btn1.button("−", key=f"minus_{p_id}"):
            st.session_state.carrito[p_id]["cant"] -= 1
            if st.session_state.carrito[p_id]["cant"] <= 0:
              items_a_eliminar.append(p_id)
            st.rerun()

          c_cant.write(f"**{item['cant']}**")

          if c_btn2.button("+", key=f"plus_{p_id}"):
            st.session_state.carrito[p_id]["cant"] += 1
            st.rerun()

          if c_del.button("🗑️", key=f"del_{p_id}"):
            items_a_eliminar.append(p_id)
            st.rerun()

        for p_id in items_a_eliminar:
          if p_id in st.session_state.carrito:
            del st.session_state.carrito[p_id]
            st.rerun()

# ---------------------------------------------------------
# PESTAÑA 2: VENTAS DEL DÍA
# ---------------------------------------------------------
with tab2:
  st.subheader("📋 Registro de Ventas")
  conn = sqlite3.connect(DB_NAME)
  try:
    df_ventas = pd.read_sql_query(
        "SELECT correlativo AS Boleta, detalle AS Detalle, total AS 'Total S/',"
        " metodo AS Método, fecha AS Fecha FROM ventas ORDER BY id DESC",
        conn,
    )
    if not df_ventas.empty:
      st.dataframe(df_ventas, use_container_width=True)
      total_hoy = df_ventas["Total S/"].sum()
      st.metric("Total Recaudado", f"S/ {total_hoy:.2f}")
    else:
      st.write("No hay ventas registradas aún.")
  except Exception:
    st.write("Sin registros de ventas.")
  conn.close()

# ---------------------------------------------------------
# PESTAÑA 3: CONTROL DE CAJA
# ---------------------------------------------------------
with tab3:
  st.subheader("🔒 Estado de Caja")
  clave = st.text_input(
      "Contraseña Administrador", type="password", key="pass_cierre"
  )

  if clave == PIN_ADMIN:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
    caja_activa = c.fetchone()

    df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
    conn.close()

    if caja_activa:
      st.write(f"**Apertura:** {caja_activa[3]}")
      st.write(f"**Monto Inicial:** S/ {caja_activa[1]:.2f}")

      tot_efectivo = (
          df_ventas[df_ventas["metodo"] == "Efectivo"]["total"].sum()
          if not df_ventas.empty
          else 0
      )
      tot_digital = (
          df_ventas[df_ventas["metodo"].isin(["Yape", "Plin"])]["total"].sum()
          if not df_ventas.empty
          else 0
      )
      tot_ventas = df_ventas["total"].sum() if not df_ventas.empty else 0

      c1, c2, c3 = st.columns(3)
      c1.metric("💵 Efectivo", f"S/ {tot_efectivo:.2f}")
      c2.metric("📲 Digital (Yape/Plin)", f"S/ {tot_digital:.2f}")
      c3.metric("💰 Total Recaudado", f"S/ {tot_ventas:.2f}")

      st.markdown("---")
      if st.button("🔒 CERRAR CAJA Y TURNO", use_container_width=True):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "UPDATE caja SET monto_final = ?, fecha_cierre = ?, estado ="
            " 'CERRADA' WHERE id = ?",
            (
                caja_activa[1] + tot_ventas,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                caja_activa[0],
            ),
        )
        conn.commit()
        conn.close()
        st.success("¡Caja cerrada correctamente!")
        st.rerun()
    else:
      st.info("La caja está CERRADA.")

# ---------------------------------------------------------
# PESTAÑA 4: REPORTES
# ---------------------------------------------------------
with tab4:
  st.subheader("📊 Reporte Visual de Ventas")
  clave_rep = st.text_input(
      "Contraseña Administrador", type="password", key="pass_rep"
  )
  if clave_rep == PIN_ADMIN:
    conn = sqlite3.connect(DB_NAME)
    try:
      df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
      if not df_ventas.empty:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
          st.markdown("### Métodos de Pago")
          st.bar_chart(df_ventas["metodo"].value_counts())
        with col_r2:
          st.markdown("### Histórico de Ingresos")
          st.line_chart(df_ventas["total"])
      else:
        st.write("Sin datos para graficar.")
    except Exception:
      st.write("Sin datos disponibles.")
    conn.close()
