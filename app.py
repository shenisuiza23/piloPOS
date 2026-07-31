import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pilo POS v7", page_icon="🍔", layout="wide", initial_sidebar_state="collapsed")

PIN_ADMIN = "200423"
DB_NAME = "pos_v7.db"

# --- ESTADO DE SESIÓN ---
if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# --- ESTILOS CSS PERSONALIZADOS (PALETA ACTUALIZADA) ---
st.markdown("""
    <style>
    /* 1. Header Superior Naranja Pilo POS */
    .pilo-header {
        background: linear-gradient(90deg, #d97724 0%, #ea580c 100%);
        padding: 15px 25px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .pilo-title {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Base para botones de la app */
    div.stButton > button {
        font-weight: bold !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        padding: 8px !important;
        border: none !important;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.15) !important;
    }

    /* Colores por Categoría */
    .theme-pizzas div.stButton > button { background-color: #2b5c8f !important; color: white !important; height: 75px !important; }
    .theme-alitas div.stButton > button { background-color: #c69214 !important; color: white !important; height: 75px !important; }
    .theme-hamburguesas div.stButton > button { background-color: #d97724 !important; color: white !important; height: 75px !important; }
    .theme-entradas div.stButton > button { background-color: #2e7d32 !important; color: white !important; height: 75px !important; }
    .theme-extras div.stButton > button { background-color: #7e22ce !important; color: white !important; height: 75px !important; }
    .theme-bebidas div.stButton > button { background-color: #0284c7 !important; color: white !important; height: 75px !important; }

    /* Botones Principales de Acción */
    div[data-testid="stKey-btn_cobrar"] button {
        background-color: #16a34a !important;
        color: white !important;
        font-size: 22px !important;
        height: 60px !important;
    }

    div[data-testid="stKey-btn_vaciar"] button {
        background-color: #dc2626 !important;
        color: white !important;
    }

    /* Total Gigante */
    .total-display {
        background-color: #0f172a;
        color: #22c55e;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-size: 30px;
        font-weight: 900;
        margin: 15px 0;
        border: 2px solid #22c55e;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS Y CORRELATIVOS ---
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
            # 🍕 PIZZAS
            ("Pizza Americana Personal", "Pizzas", 25.00),
            ("Pizza Hawaiana Personal", "Pizzas", 25.00),
            ("Pizza Pepperoni Personal", "Pizzas", 25.00),
            ("Pizza Pilo Personal", "Pizzas", 28.00),
            ("Pizza Americana Familiar", "Pizzas", 45.00),
            ("Pizza Hawaiana Familiar", "Pizzas", 45.00),
            ("Pizza Pepperoni Familiar", "Pizzas", 45.00),
            ("Pizza Pilo Familiar", "Pizzas", 50.00),

            # 🍗 ALITAS
            ("Alitas Rebozadas", "Alitas", 20.00),
            ("Alitas BBQ", "Alitas", 22.00),
            ("Alitas Acevichadas", "Alitas", 22.00),
            ("Alitas Búfalo", "Alitas", 22.00),
            ("Alitas Pilo", "Alitas", 24.00),

            # 🍔 HAMBURGUESAS
            ("Hamburguesa Clásica", "Hamburguesas", 6.00),
            ("Hamburguesa Hawaiana", "Hamburguesas", 8.00),
            ("Hamburguesa A lo Pilo", "Hamburguesas", 9.00),
            ("Hamburguesa A lo Pobre", "Hamburguesas", 10.00),
            ("Hamburguesa Royal", "Hamburguesas", 14.00),
            ("Hamburguesa Mega Pilo", "Hamburguesas", 16.00),

            # 🍟 ENTRADAS
            ("Choripán", "Entradas", 6.00),
            ("Salchipapa Clásica", "Entradas", 8.00),
            ("Salchalita", "Entradas", 16.00),

            # ➕ PORCIONES / EXTRAS
            ("Porción de Papa", "Extras", 5.00),
            ("Porción de Maduro", "Extras", 5.00),
            ("Porción de Alita", "Extras", 4.00),
            ("Porción de Carne de Hamburguesa", "Extras", 3.00),
            ("Porción de Huevo", "Extras", 1.00),
            ("Porción de Tocino", "Extras", 1.00),
            ("Porción de Jamón", "Extras", 1.00),
            ("Porción de Queso", "Extras", 1.00),
            ("Porción de Papa para Hamburguesa", "Extras", 1.00),
            ("Porción de Maduro para Hamburguesa", "Extras", 1.00),

            # 🥤 BEBIDAS
            ("Inca Kola", "Bebidas", 5.00),
            ("Coca Cola", "Bebidas", 5.00),
            ("Chicha Morada", "Bebidas", 3.00),
            ("Cocona", "Bebidas", 3.00),
            ("Agua Mineral", "Bebidas", 2.00)
        ]
        # Inserción adaptada a la nueva estructura simplificada
        cursor.executemany("INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)", productos_defecto)
    
    conexion.commit()
    conexion.close()

def obtener_siguiente_correlativo():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ventas")
    num_ventas = c.fetchone()[0] + 1
    conn.close()
    return f"B001-{num_ventas:06d}"

def renderizar_grid_productos(categoria, css_theme_class, num_cols=3):
    """Renderiza los productos de una categoría en una cuadrícula dentro de un contenedor estilizado"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, nombre, precio FROM productos WHERE categoria = ?", (categoria,))
    prods = c.fetchall()
    conn.close()

    st.markdown(f'<div class="{css_theme_class}">', unsafe_allow_html=True)
    for i in range(0, len(prods), num_cols):
        grupo = prods[i:i + num_cols]
        cols = st.columns(num_cols)
        for col, (p_id, p_nom, p_precio) in zip(cols, grupo):
            with col:
                label = f"{p_nom}\nS/ {p_precio:.2f}"
                if st.button(label, key=f"prod_{p_id}", use_container_width=True):
                    if p_id in st.session_state.carrito:
                        st.session_state.carrito[p_id]["cant"] += 1
                    else:
                        st.session_state.carrito[p_id] = {"nombre": p_nom, "precio": p_precio, "cant": 1}
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Inicializar Base de Datos
inicializar_bd()

# --- HEADER SUPERIOR COLOR NARANJA ---
st.markdown("""
    <div class="pilo-header">
        <div class="pilo-title">🍔 Pilo Burger & POS v7</div>
        <div style="font-size: 16px; font-weight: bold;">Sistema de Venta Rápida</div>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN PRINCIPAL ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Punto de Venta", 
    "📋 Ventas del Día", 
    "🔒 Control de Caja", 
    "📊 Reportes y Estadísticas"
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
        st.warning("⚠️ La caja está CERRADA. Inicia sesión de caja para empezar a vender.")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            clave_apertura = st.text_input("Contraseña Administrador", type="password", key="pass_open")
        with col_c2:
            monto_ini = st.number_input("Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0)
        
        if st.button("🔓 ABRIR CAJA", use_container_width=True):
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
        col_menu, col_carrito = st.columns([1.5, 1])
        
        # --- CATÁLOGO ORGANIZADO EN 6 PESTAÑAS Y CUADRÍCULAS ---
        with col_menu:
            subtab_pizzas, subtab_alitas, subtab_burgers, subtab_entradas, subtab_extras, subtab_bebidas = st.tabs([
                "🍕 Pizzas", "🍗 Alitas", "🍔 Hamburguesas", "🍟 Entradas", "➕ Extras", "🥤 Bebidas"
            ])

            with subtab_pizzas:
                renderizar_grid_productos("Pizzas", "theme-pizzas", num_cols=3)

            with subtab_alitas:
                renderizar_grid_productos("Alitas", "theme-alitas", num_cols=3)

            with subtab_burgers:
                renderizar_grid_productos("Hamburguesas", "theme-hamburguesas", num_cols=3)

            with subtab_entradas:
                renderizar_grid_productos("Entradas", "theme-entradas", num_cols=3)

            with subtab_extras:
                renderizar_grid_productos("Extras", "theme-extras", num_cols=3)

            with subtab_bebidas:
                renderizar_grid_productos("Bebidas", "theme-bebidas", num_cols=3)

        # --- CARRITO DE COMPRAS Y TICKET ---
        with col_carrito:
            st.subheader("🛒 Pedido Actual")
            metodo_pago = st.radio("Método de Pago:", ["Efectivo", "Yape", "Plin", "Mixto"], horizontal=True)
            
            if st.session_state.carrito:
                st.markdown("---")
                total = 0.0
                
                # Lista de items con control +, - y eliminar
                items_a_eliminar = []
                for p_id, item in st.session_state.carrito.items():
                    subtotal = item["precio"] * item["cant"]
                    total += subtotal
                    
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

                st.markdown(f'<div class="total-display">TOTAL: S/ {total:.2f}</div>', unsafe_allow_html=True)
                
                # Vuelto / Pagos
                vuelto = 0.0
                if metodo_pago == "Efectivo":
                    monto_recibido = st.number_input("Monto Entregado (S/):", min_value=total, value=total, step=1.0)
                    vuelto = monto_recibido - total
                    st.info(f"💵 **Vuelto a entregar: S/ {vuelto:.2f}**")
                elif metodo_pago == "Mixto":
                    efectivo_part = st.number_input("Monto en Efectivo (S/):", min_value=0.0, max_value=total, value=total/2)
                    digital_part = total - efectivo_part
                    st.write(f"📲 Yape/Plin restante: **S/ {digital_part:.2f}**")

                if st.button("🚀 COBRAR", key="btn_cobrar", use_container_width=True):
                    correlativo = obtener_siguiente_correlativo()
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    detalle_str = ", ".join([f"{item['cant']}x {item['nombre']}" for item in st.session_state.carrito.values()])
                    
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO ventas (correlativo, total, metodo, fecha, detalle) VALUES (?, ?, ?, ?, ?)",
                              (correlativo, total, metodo_pago, fecha_actual, detalle_str))
                    conn.commit()
                    conn.close()
                    
                    st.session_state.ultima_venta = {
                        "correlativo": correlativo,
                        "total": total,
                        "metodo": metodo_pago,
                        "fecha": fecha_actual,
                        "detalle": st.session_state.carrito.copy()
                    }
                    
                    st.session_state.carrito = {}
                    st.success(f"Venta {correlativo} Registrada!")
                    st.rerun()

                if st.button("🗑️ VACIAR CARRITO", key="btn_vaciar", use_container_width=True):
                    st.session_state.carrito = {}
                    st.rerun()
            else:
                st.info("El carrito está vacío. Selecciona productos del menú.")
                
            # Generación de Ticket de la última venta
            if "ultima_venta" in st.session_state:
                st.markdown("---")
                st.subheader("🧾 Último Ticket Emitido")
                uv = st.session_state.ultima_venta
                ticket_txt = f"""
================================
        PILO BURGER POS        
================================
Boleta: {uv['correlativo']}
Fecha: {uv['fecha']}
Método: {uv['metodo']}
--------------------------------
"""
                for item in uv['detalle'].values():
                    ticket_txt += f"{item['cant']}x {item['nombre']} - S/ {item['precio']*item['cant']:.2f}\n"
                ticket_txt += f"--------------------------------\nTOTAL: S/ {uv['total']:.2f}\n================================"
                
                st.code(ticket_txt, language="text")
                st.download_button("🖨️ Descargar Ticket", ticket_txt, file_name=f"ticket_{uv['correlativo']}.txt")

# ---------------------------------------------------------
# PESTAÑA 2: VENTAS DEL DÍA
# ---------------------------------------------------------
with tab2:
    st.subheader("📋 Ventas Realizadas")
    conn = sqlite3.connect(DB_NAME)
    try:
        df_ventas = pd.read_sql_query("SELECT correlativo AS Boleta, detalle AS Detalle, total AS 'Total S/', metodo AS Método, fecha AS Fecha FROM ventas ORDER BY id DESC", conn)
        if not df_ventas.empty:
            st.dataframe(df_ventas, use_container_width=True)
            total_hoy = df_ventas["Total S/"].sum()
            st.metric("Total Recaudado", f"S/ {total_hoy:.2f}")
        else:
            st.write("Aún no hay ventas registradas.")
    except Exception:
        st.write("Sin ventas registradas.")
    conn.close()

# ---------------------------------------------------------
# PESTAÑA 3: CONTROL DE CAJA
# ---------------------------------------------------------
with tab3:
    st.subheader("🔒 Control y Cierre de Caja")
    clave = st.text_input("Contraseña de Administrador", type="password", key="pass_cierre")
    
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
            
            tot_efectivo = df_ventas[df_ventas['metodo'] == 'Efectivo']['total'].sum() if not df_ventas.empty else 0
            tot_yape = df_ventas[df_ventas['metodo'] == 'Yape']['total'].sum() if not df_ventas.empty else 0
            tot_plin = df_ventas[df_ventas['metodo'] == 'Plin']['total'].sum() if not df_ventas.empty else 0
            tot_ventas = df_ventas['total'].sum() if not df_ventas.empty else 0
            
            c1, c2, c3 = st.columns(3)
            c1.metric("💵 Efectivo", f"S/ {tot_efectivo:.2f}")
            c2.metric("📲 Yape / Plin", f"S/ {(tot_yape + tot_plin):.2f}")
            c3.metric("💰 Total Ventas", f"S/ {tot_ventas:.2f}")
            
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
            st.info("La caja está CERRADA.")

# ---------------------------------------------------------
# PESTAÑA 4: REPORTES Y ESTADÍSTICAS
# ---------------------------------------------------------
with tab4:
    st.subheader("📊 Reportes y Estadísticas de Ventas")
    clave_rep = st.text_input("Contraseña Administrador", type="password", key="pass_rep")
    if clave_rep == PIN_ADMIN:
        conn = sqlite3.connect(DB_NAME)
        try:
            df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
            if not df_ventas.empty:
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown("### Métodos de Pago Más Usados")
                    st.bar_chart(df_ventas['metodo'].value_counts())
                with col_r2:
                    st.markdown("### Histórico de Ingresos")
                    st.line_chart(df_ventas['total'])
            else:
                st.write("No hay datos de ventas disponibles para gráficos.")
        except Exception:
            st.write("Sin datos disponibles.")
        conn.close()
