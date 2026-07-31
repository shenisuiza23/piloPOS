import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================
PIN_ADMIN = "200423"  # Cambia esta clave si deseas


# ==========================================
# BASE DE DATOS Y TABLAS
# ==========================================
def init_db():
    conn = sqlite3.connect("pos_restaurante.db")
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            tipo TEXT,
            total REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS detalles_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            producto TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
        )
    """
    )

    c.execute("SELECT COUNT(*) FROM productos")
    if c.fetchone()[0] == 0:
        menu_inicial = [
            ("Alitas 6 Pzs", 15.0, "Alitas"),
            ("Alitas 12 Pzs", 28.0, "Alitas"),
            ("Alitas 18 Pzs", 40.0, "Alitas"),
            ("Gaseosa 500ml", 4.0, "Bebidas"),
            ("Chicha Morada 1L", 10.0, "Bebidas"),
            ("Agua Mineral", 3.0, "Bebidas"),
            ("Papas Fritas", 8.0, "Extras"),
            ("Cerveza Personal", 7.0, "Extras"),
        ]
        c.executemany(
            "INSERT INTO productos (nombre, precio, categoria) VALUES (?, ?, ?)",
            menu_inicial,
        )

    conn.commit()
    conn.close()


init_db()

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="PiloPOS", page_icon="🍗", layout="wide")

st.markdown(
    """
    <style>
    .stButton>button { width: 100%; height: 3em; font-weight: bold; }
    .total-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; color: #1f77b4; }
    </style>
""",
    unsafe_allow_html=True,
)

if "carrito" not in st.session_state:
    st.session_state.carrito = []

st.title("🍗 piloPOS - Sistema de Ventas")

# ==========================================
# PESTAÑAS PRINCIPALES
# ==========================================
tab_pos, tab_cierre, tab_mensual = st.tabs(
    ["🛒 Punto de Venta", "🔒 Cierre del Turno (12pm-12pm)", "📊 Reporte Mensual"]
)

# ------------------------------------------
# TAB 1: PUNTO DE VENTA
# ------------------------------------------
with tab_pos:
    col_menu, col_orden = st.columns([3, 2])

    with col_menu:
        st.subheader("Menú de Productos")

        conn = sqlite3.connect("pos_restaurante.db")
        df_prod = pd.read_sql_query("SELECT * FROM productos", conn)
        conn.close()

        categorias = df_prod["categoria"].unique()
        cat_seleccionada = st.radio("Categorías", categorias, horizontal=True)

        prods_cat = df_prod[df_prod["categoria"] == cat_seleccionada]

        cols_p = st.columns(2)
        for idx, row in prods_cat.iterrows():
            col_idx = idx % 2
            with cols_p[col_idx]:
                if st.button(
                    f"{row['nombre']}\nS/ {row['precio']:.2f}", key=row["id"]
                ):
                    st.session_state.carrito.append(
                        {
                            "id": row["id"],
                            "nombre": row["nombre"],
                            "precio": row["precio"],
                        }
                    )
                    st.toast(f"¡{row['nombre']} agregado!", icon="✅")

    with col_orden:
        st.subheader("Detalle del Pedido")

        nombre_cliente = st.text_input(
            "Nombre del Cliente / Mesa", placeholder="Ej: Mesa 3 o Juan"
        )
        tipo_pedido = st.selectbox(
            "Tipo de Pedido", ["Para Comer Aquí", "Para Llevar", "Delivery"]
        )

        if len(st.session_state.carrito) > 0:
            df_cart = pd.DataFrame(st.session_state.carrito)
            resumen = (
                df_cart.groupby(["nombre", "precio"])
                .size()
                .reset_index(name="cantidad")
            )
            resumen["subtotal"] = resumen["precio"] * resumen["cantidad"]

            st.dataframe(
                resumen[["nombre", "cantidad", "precio", "subtotal"]],
                use_container_width=True,
                hide_index=True,
            )

            total_pagar = resumen["subtotal"].sum()
            st.markdown(
                f'<div class="total-box">TOTAL: S/ {total_pagar:.2f}</div>',
                unsafe_allow_html=True,
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔴 Borrar Todo"):
                    st.session_state.carrito = []
                    st.rerun()

            with col_btn2:
                if st.button("🟢 REGISTRAR PEDIDO", type="primary"):
                    conn = sqlite3.connect("pos_restaurante.db")
                    c = conn.cursor()

                    # Guardar fecha exacta con hora actual
                    fecha_actual = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    c.execute(
                        "INSERT INTO pedidos (cliente, tipo, total, fecha) VALUES (?, ?, ?, ?)",
                        (
                            nombre_cliente
                            if nombre_cliente
                            else "Cliente General",
                            tipo_pedido,
                            total_pagar,
                            fecha_actual,
                        ),
                    )
                    pedido_id = c.lastrowid

                    for _, row in resumen.iterrows():
                        c.execute(
                            """
                            INSERT INTO detalles_pedido (pedido_id, producto, cantidad, precio_unitario, subtotal)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                pedido_id,
                                row["nombre"],
                                row["cantidad"],
                                row["precio"],
                                row["subtotal"],
                            ),
                        )

                    conn.commit()
                    conn.close()

                    st.session_state.carrito = []
                    st.success(f"¡Pedido #{pedido_id} registrado con éxito!")
                    st.rerun()
        else:
            st.info(
                "El carrito está vacío. Haz clic en los productos para agregarlos."
            )

# ------------------------------------------
# TAB 2: CIERRE DE TURNO NOCTURNO (12:00 PM a 11:59 AM)
# ------------------------------------------
with tab_cierre:
    st.subheader("🔒 Cierre del Turno Operativo")

    pin_ingresado = st.text_input(
        "Ingresa la contraseña para ver las ventas del turno:",
        type="password",
        key="pin_turno",
    )

    if pin_ingresado == PIN_ADMIN:
        st.success("Acceso Autorizado.")

        # Cálculo del Rango Operativo (12:00 PM del día actual/anterior hasta 11:59 AM del día siguiente)
        ahora = datetime.now()
        if ahora.hour < 12:
            inicio_turno = (ahora - timedelta(days=1)).replace(
                hour=12, minute=0, second=0
            )
            fin_turno = ahora.replace(
                hour=11, minute=59, second=59
            )
        else:
            inicio_turno = ahora.replace(
                hour=12, minute=0, second=0
            )
            fin_turno = (ahora + timedelta(days=1)).replace(
                hour=11, minute=59, second=59
            )

        st.info(
            f"📅 **Turno Actual:** Desde `{inicio_turno.strftime('%d/%m/%Y %I:%M %p')}` Hasta `{fin_turno.strftime('%d/%m/%Y %I:%M %p')}`"
        )

        conn = sqlite3.connect("pos_restaurante.db")
        df_pedidos = pd.read_sql_query(
            """
            SELECT * FROM pedidos 
            WHERE fecha >= ? AND fecha <= ?
        """,
            conn,
            params=(
                inicio_turno.strftime("%Y-%m-%d %H:%M:%S"),
                fin_turno.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        if not df_pedidos.empty:
            pedidos_ids = tuple(df_pedidos["id"].tolist())
            query_detalles = f"SELECT * FROM detalles_pedido WHERE pedido_id IN ({','.join(['?']*len(pedidos_ids))})"
            df_detalles = pd.read_sql_query(
                query_detalles, conn, params=pedidos_ids
            )
        else:
            df_detalles = pd.DataFrame()

        conn.close()

        if not df_pedidos.empty:
            total_ventas = df_pedidos["total"].sum()
            cant_pedidos = len(df_pedidos)

            c1, c2 = st.columns(2)
            c1.metric("Total Cobrado en Turno", f"S/ {total_ventas:.2f}")
            c2.metric("Pedidos Atendidos", cant_pedidos)

            st.write("---")
            st.subheader("Productos Vendidos en este Turno")
            resumen_prod = (
                df_detalles.groupby("producto")["cantidad"]
                .sum()
                .reset_index()
            )
            st.dataframe(
                resumen_prod, use_container_width=True, hide_index=True
            )

            st.write("---")
            st.subheader("Detalle de Pedidos del Turno")
            st.dataframe(
                df_pedidos[["id", "cliente", "tipo", "total", "fecha"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("No hay registros de ventas para el turno en curso.")

# ------------------------------------------
# TAB 3: CONTROL Y REPORTE MENSUAL
# ------------------------------------------
with tab_mensual:
    st.subheader("📊 Historial de Ventas Mensuales")

    pin_mensual = st.text_input(
        "Ingresa la contraseña de administrador para ver reportes generales:",
        type="password",
        key="pin_mes",
    )

    if pin_mensual == PIN_ADMIN:
        st.success("Acceso Autorizado.")

        conn = sqlite3.connect("pos_restaurante.db")
        df_todas = pd.read_sql_query("SELECT * FROM pedidos", conn)
        conn.close()

        if not df_todas.empty:
            df_todas["fecha_dt"] = pd.to_datetime(df_todas["fecha"])
            df_todas["Mes_Año"] = df_todas["fecha_dt"].dt.strftime("%Y-%m")

            meses_disponibles = df_todas["Mes_Año"].unique()
            mes_sel = st.selectbox(
                "Selecciona el Mes a consultar:", meses_disponibles
            )

            df_mes = df_todas[df_todas["Mes_Año"] == mes_sel]

            total_mes = df_mes["total"].sum()
            total_pedidos_mes = len(df_mes)

            m1, m2 = st.columns(2)
            m1.metric(f"Venta Total ({mes_sel})", f"S/ {total_mes:.2f}")
            m2.metric("Total Pedidos del Mes", total_pedidos_mes)

            st.write("---")
            st.subheader("Listado de Ventas del Mes")
            st.dataframe(
                df_mes[["id", "cliente", "tipo", "total", "fecha"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Aún no hay ventas acumuladas en la base de datos.")
