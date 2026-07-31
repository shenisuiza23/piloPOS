from datetime import datetime
import sqlite3
import streamlit as st

# --- IMPORTACIONES DEL PROYECTO ---
from config import DB_NAME, PIN_ADMIN
from database import (
    get_connection,
    inicializar_bd,
    registrar_venta_completa,
    generar_correlativo_boleta,
)
from estilos import COLORES_CATEGORIAS, aplicar_estilos_css
from inventario import render_inventario
from reportes import generar_ticket_termico, render_reportes
from ventas import render_control_caja, render_ventas_del_dia

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="PILO POS",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inicialización de la Base de Datos y Sesión
inicializar_bd()

if "cat_seleccionada" not in st.session_state:
    st.session_state.cat_seleccionada = "Pizzas"
if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# Aplicar estilos CSS táctiles para tabletas
aplicar_estilos_css(st.session_state.cat_seleccionada)

# Encabezado Pilo Burger
st.markdown(
    """
    <div class="pilo-header">
        <h1>🍗 PILO POS</h1>
        <p>Punto de Venta para Tablet — Pilo Burger</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Pestañas principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛒 Punto de Venta",
    "📋 Ventas del Día",
    "🔒 Control de Caja",
    "📦 Inventario",
    "📊 Reportes",
])

# ---------------------------------------------------------
# PESTAÑA 1: PUNTO DE VENTA
# ---------------------------------------------------------
with tab1:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
    caja_activa = c.fetchone()
    conn.close()

    if not caja_activa:
        st.warning("⚠️ La caja se encuentra CERRADA. Inicie turno para vender.")
        c1, c2 = st.columns(2)
        pass_open = c1.text_input(
            "Contraseña de Administrador", type="password", key="pass_open_main"
        )
        monto_ini = c2.number_input(
            "Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0
        )

        if st.button("🔓 ABRIR CAJA E INICIAR TURNO", use_container_width=True):
            if pass_open == PIN_ADMIN:
                conn_op = get_connection()
                c_op = conn_op.cursor()
                c_op.execute(
                    "INSERT INTO caja (monto_inicial, fecha_apertura, estado) VALUES (?, ?, 'ABIERTA')",
                    (monto_ini, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                )
                conn_op.commit()
                conn_op.close()
                st.success("¡Caja abierta exitosamente!")
                st.rerun()
            else:
                st.error("PIN de Administrador Incorrecto")
    else:
        # Botones de Selección de Categorías
        cols_cat = st.columns(5)
        categorias = [
            ("🍕 Pizzas", "Pizzas"),
            ("🍗 Alitas", "Alitas"),
            ("🍔 Hamburguesas", "Hamburguesas"),
            ("🍟 Entradas", "Entradas"),
            ("🥤 Otros", "Otros"),
        ]

        for idx, (label, cat_key) in enumerate(categorias):
            es_activa = st.session_state.cat_seleccionada == cat_key
            if cols_cat[idx].button(
                label, key=f"cat_{cat_key}", use_container_width=True
            ):
                st.session_state.cat_seleccionada = cat_key
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        col_menu, col_carrito = st.columns([1.3, 1])

        # Catálogo de Productos según Categoría
        with col_menu:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "SELECT id, nombre, precio, stock FROM productos WHERE categoria = ?",
                (st.session_state.cat_seleccionada,),
            )
            prods = c.fetchall()
            conn.close()

            st.markdown(f"### Menú: {st.session_state.cat_seleccionada}")
            with st.container(key="prod_zone"):
                m1, m2 = st.columns(2)
                for i, (p_id, p_nom, p_precio, p_stock) in enumerate(prods):
                    col = m1 if i % 2 == 0 else m2
                    label_prod = f"{p_nom}\nS/ {p_precio:.2f} | Stock: {p_stock}"

                    if col.button(
                        label_prod,
                        key=f"p_{p_id}",
                        use_container_width=True,
                        disabled=(p_stock <= 0),
                    ):
                        if p_id in st.session_state.carrito:
                            if st.session_state.carrito[p_id]["cant"] < p_stock:
                                st.session_state.carrito[p_id]["cant"] += 1
                            else:
                                st.toast(
                                    f"Stock máximo alcanzado para {p_nom}"
                                )
                        else:
                            st.session_state.carrito[p_id] = {
                                "nombre": p_nom,
                                "precio": p_precio,
                                "cant": 1,
                            }
                        st.rerun()

        # Pedido Actual y Carrito
        with col_carrito:
            st.markdown('<div class="pilo-card">', unsafe_allow_html=True)
            st.markdown("### 🛒 Pedido Actual")

            total_calculado = sum(
                item["precio"] * item["cant"]
                for item in st.session_state.carrito.values()
            )

            # Botones Principales (Cobrar Verde 65px / Vaciar Rojo)
            c_cob, c_vac = st.columns([2, 1])
            btn_cobrar = c_cob.button("💰 COBRAR", key="btn_cobrar")
            if c_vac.button("🗑 VACIAR", key="btn_vaciar"):
                st.session_state.carrito = {}
                st.rerun()

            st.markdown(
                f'<div class="total-card">TOTAL: S/ {total_calculado:.2f}</div>',
                unsafe_allow_html=True,
            )
            metodo_pago = st.radio(
                "Método de Pago:",
                ["Efectivo", "Yape", "Plin", "Mixto"],
                horizontal=True,
            )

            monto_ef = 0.0
            monto_dig = 0.0

            if metodo_pago == "Efectivo":
                monto_ef = total_calculado
                if total_calculado > 0:
                    monto_rec = st.number_input(
                        "Monto Entregado (S/):",
                        min_value=total_calculado,
                        value=total_calculado,
                        step=1.0,
                    )
                    st.info(
                        f"💵 **Vuelto a Entregar: S/ {monto_rec - total_calculado:.2f}**"
                    )
            elif metodo_pago in ["Yape", "Plin"]:
                monto_dig = total_calculado
            elif metodo_pago == "Mixto" and total_calculado > 0:
                monto_ef = st.number_input(
                    "Monto en Efectivo (S/):",
                    min_value=0.0,
                    max_value=total_calculado,
                    value=total_calculado / 2,
                )
                monto_dig = total_calculado - monto_ef
                st.write(
                    f"📲 Pago Digital Restante (Yape/Plin): **S/ {monto_dig:.2f}**"
                )

            # Acción para procesar cobro
            if btn_cobrar:
                if not st.session_state.carrito:
                    st.error("El carrito se encuentra vacío.")
                else:
                    correlativo = generar_correlativo_boleta()
                    fecha_reg = registrar_venta_completa(
                        correlativo,
                        total_calculado,
                        metodo_pago,
                        monto_ef,
                        monto_dig,
                        st.session_state.carrito,
                    )

                    st.session_state.ultima_venta = {
                        "correlativo": correlativo,
                        "total": total_calculado,
                        "metodo": metodo_pago,
                        "fecha": fecha_reg,
                        "detalle": st.session_state.carrito.copy(),
                    }
                    st.session_state.carrito = {}
                    st.success(f"Venta {correlativo} Registrada!")
                    st.rerun()

            st.markdown("---")

            # Lista estructurada de productos (+ / - / Borrar)
            if st.session_state.carrito:
                for p_id, item in list(st.session_state.carrito.items()):
                    subt = item["precio"] * item["cant"]
                    c_inf, c_m, c_cant, c_p, c_del = st.columns(
                        [3, 0.7, 0.7, 0.7, 0.7]
                    )
                    c_inf.markdown(
                        f"**{item['nombre']}**\n<small>S/ {item['precio']:.2f} x {item['cant']} = S/ {subt:.2f}</small>",
                        unsafe_allow_html=True,
                    )

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
            else:
                st.info("Seleccione productos del menú para agregar al pedido.")

            st.markdown("</div>", unsafe_allow_html=True)

            # Emisión e impresión de Ticket Térmico
            if "ultima_venta" in st.session_state:
                st.markdown("---")
                st.subheader("🖨️ Imprimir Ticket Térmico")
                uv = st.session_state.ultima_venta
                ancho_paper = st.selectbox(
                    "Ancho de Impresora:", [58, 80], index=0
                )
                ticket_str = generar_ticket_termico(
                    uv["correlativo"],
                    uv["fecha"],
                    uv["metodo"],
                    uv["detalle"],
                    uv["total"],
                    ancho_mm=ancho_paper,
                )
                st.code(ticket_str, language="text")
                st.download_button(
                    "📥 Descargar Ticket para Impresora",
                    ticket_str,
                    file_name=f"Ticket_{uv['correlativo']}.txt",
                )

# ---------------------------------------------------------
# OTRAS PESTAÑAS
# ---------------------------------------------------------
with tab2:
    render_ventas_del_dia()

with tab3:
    render_control_caja(PIN_ADMIN)

with tab4:
    render_inventario(PIN_ADMIN)

with tab5:
    render_reportes(PIN_ADMIN)
