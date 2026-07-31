import streamlit as st
from estilos import aplicar_estilos_css

# 1. Configurar la página
st.set_page_config(page_title="PILO POS", layout="wide", initial_sidebar_state="collapsed")

# 2. Cargar los estilos CSS personalizados
aplicar_estilos_css()

# 3. Inicializar el estado de la sesión
if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'metodo_pago' not in st.session_state:
    st.session_state.metodo_pago = "Efectivo"

# 4. ENCABEZADO SUPERIOR (#F97316)
st.markdown("""
<div class="pilo-header">
    <div>
        <div class="pilo-title">🍗 PILO POS</div>
        <div class="pilo-subtitle">Punto de Venta</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. BOTONES PRINCIPALES DE ACCIÓN (COBRAR Y VACIAR)
col_top_cobrar, col_top_vaciar = st.columns([2.5, 1])

with col_top_cobrar:
    if st.button("💵 COBRAR", key="btn_cobrar", use_container_width=True):
        if st.session_state.carrito:
            st.success(f"¡Venta registrada exitosamente! ({st.session_state.metodo_pago})")
            st.session_state.carrito = []
        else:
            st.warning("El carrito está vacío.")

with col_top_vaciar:
    if st.button("🗑 VACIAR", key="btn_vaciar", use_container_width=True):
        st.session_state.carrito = []
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 6. ESTRUCTURA PRINCIPAL: CATÁLOGO (IZQ) Y PEDIDO (DER)
col_menu, col_pedido = st.columns([2.3, 1.1])

# --- COLUMNA IZQUIERDA: MENÚ DE PRODUCTOS ---
with col_menu:
    
    # LISTA OFICIAL DE PRODUCTOS (Nombre, Categoría, Precio, Key)
    PRODUCTOS = [
        # Pizzas (Azul #2563EB)
        ("Pizza Americana Personal", "Pizzas", 25.00, "p1"),
        ("Pizza Hawaiana Personal", "Pizzas", 25.00, "p2"),
        ("Pizza Peperoni Personal", "Pizzas", 25.00, "p3"),
        ("Pizza Pilo Personal", "Pizzas", 28.00, "p4"),
        ("Pizza Americana Familiar", "Pizzas", 45.00, "p5"),
        ("Pizza Hawaiana Familiar", "Pizzas", 45.00, "p6"),
        ("Pizza Peperoni Familiar", "Pizzas", 45.00, "p7"),
        ("Pizza Pilo Familiar", "Pizzas", 50.00, "p8"),

        # Alitas (Amarillo #EAB308)
        ("Alitas Rebozadas", "Alitas", 20.00, "a1"),
        ("Alitas BBQ", "Alitas", 22.00, "a2"),
        ("Alitas Acevichadas", "Alitas", 22.00, "a3"),
        ("Alitas Búfalo", "Alitas", 22.00, "a4"),
        ("Alitas Pilo", "Alitas", 24.00, "a5"),

        # Hamburguesas (Naranja #F97316)
        ("Hamb. Clásica", "Hamburguesas", 6.00, "h1"),
        ("Hamb. Hawaiana", "Hamburguesas", 8.00, "h2"),
        ("Hamb. Pilo", "Hamburguesas", 9.00, "h3"),
        ("Hamb. A lo pobre", "Hamburguesas", 10.00, "h4"),
        ("Hamb. Royal", "Hamburguesas", 14.00, "h5"),
        ("Hamb. Mega Pilo", "Hamburguesas", 16.00, "h6"),

        # Entradas (Verde #16A34A)
        ("Choripan", "Entradas", 6.00, "e1"),
        ("Salchipapa Clásica", "Entradas", 8.00, "e2"),
        ("Salchialita", "Entradas", 16.00, "e3"),

        # Otros y Bebidas (Celeste #0EA5E9)
        ("Porción de Papa", "Otros", 5.00, "o1"),
        ("Porción de Maduro", "Otros", 5.00, "o2"),
        ("Porción Alitas (x ud)", "Otros", 4.00, "o3"),
        ("Inca Kola 500ml", "Otros", 5.00, "o4"),
        ("Coca Cola 500ml", "Otros", 5.00, "o5"),
        ("Chicha Morada", "Otros", 3.00, "o6"),
    ]

    # CONFIGURACIÓN DE SECCIONES (Título, Clase CSS, Categoría, Columnas por fila)
    SECCIONES = [
        ("🍕 Pizzas", "prod-pizzas", "Pizzas", 4),
        ("🍗 Alitas", "prod-alitas", "Alitas", 3),
        ("🍔 Hamburguesas", "prod-burgers", "Hamburguesas", 3),
        ("🍟 Entradas", "prod-entradas", "Entradas", 3),
        ("🥤 Otros y Bebidas", "prod-otros", "Otros", 3)
    ]

    # RENDERIZADO AUTOMÁTICO DEL CATÁLOGO
    for titulo, css_class, cat, num_cols in SECCIONES:
        st.markdown(f"### {titulo}")
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        
        prods_cat = [p for p in PRODUCTOS if p[1] == cat]
        
        for i in range(0, len(prods_cat), num_cols):
            grupo = prods_cat[i:i + num_cols]
            cols = st.columns(num_cols)
            for col, (nombre, _, precio, key_id) in zip(cols, grupo):
                label_btn = f"{nombre}\n\nS/ {precio:.2f}"
                if col.button(label_btn, key=key_id, use_container_width=True):
                    st.session_state.carrito.append({"nombre": nombre, "precio": precio})
                    
        st.markdown('</div>', unsafe_allow_html=True)


# --- COLUMNA DERECHA: TARJETA DE PEDIDO ACTUAL ---
with col_pedido:
    total_pagar = sum(item['precio'] for item in st.session_state.carrito)
    
    st.markdown('<div class="cart-card">', unsafe_allow_html=True)
    st.markdown("### 🛒 Pedido Actual")
    st.markdown("---")
    
    if st.session_state.carrito:
        for item in st.session_state.carrito:
            st.markdown(f"""
            <div class="cart-item">
                <span>{item['nombre']}</span>
                <span>S/ {item['precio']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No hay elementos seleccionados.")
    
    st.markdown("---")
    st.markdown("#### Método de Pago")
    
    st.markdown('<div class="btn-pago">', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    if p1.button("💵 Efectivo", use_container_width=True):
        st.session_state.metodo_pago = "Efectivo"
    if p2.button("📱 Yape", use_container_width=True):
        st.session_state.metodo_pago = "Yape"
    if p3.button("💳 Plin", use_container_width=True):
        st.session_state.metodo_pago = "Plin"
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.caption(f"Seleccionado: **{st.session_state.metodo_pago}**")
    
    st.markdown("---")
    st.markdown("### Total a Pagar:")
    st.markdown(f'<div class="total-grande">S/ {total_pagar:.2f}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
