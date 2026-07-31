import streamlit as st
from estilos import aplicar_estilos_css

# 1. Configurar la página
st.set_page_config(page_title="PILO POS", layout="wide", initial_sidebar_state="collapsed")

# 2. Cargar los estilos CSS personalizados
aplicar_estilos_css()

# 3. Inicializar el estado de la sesión para el carrito y método de pago
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
col_menu, col_pedido = st.columns([2.2, 1.2])

# --- COLUMNA IZQUIERDA: MENÚ DE PRODUCTOS ---
with col_menu:
    
    # 🍕 PIZZAS (Azul #2563EB)
    st.markdown("### 🍕 Pizzas")
    st.markdown('<div class="prod-pizzas">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Pizza Americana\n\nS/ 25.00", key="p1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Americana", "precio": 25.00})
    if c2.button("Pizza Hawayana\n\nS/ 25.00", key="p2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Hawayana", "precio": 25.00})
    if c3.button("Pizza Pepperoni\n\nS/ 28.00", key="p3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Pepperoni", "precio": 28.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🍗 ALITAS (Amarillo #EAB308)
    st.markdown("### 🍗 Alitas")
    st.markdown('<div class="prod-alitas">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Alitas BBQ\n\nS/ 22.00", key="a1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas BBQ", "precio": 22.00})
    if c2.button("Alitas Picantes\n\nS/ 22.00", key="a2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas Picantes", "precio": 22.00})
    if c3.button("Alitas Broaster\n\nS/ 20.00", key="a3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas Broaster", "precio": 20.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🍔 HAMBURGUESAS (Naranja #F97316)
    st.markdown("### 🍔 Hamburguesas")
    st.markdown('<div class="prod-burgers">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Hamb. Clásica\n\nS/ 12.00", key="h1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamb. Clásica", "precio": 12.00})
    if c2.button("Hamb. Royal\n\nS/ 15.00", key="h2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamb. Royal", "precio": 15.00})
    if c3.button("Hamb. Pilo\n\nS/ 18.00", key="h3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamb. Pilo", "precio": 18.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🍟 ENTRADAS (Verde #16A34A)
    st.markdown("### 🍟 Entradas")
    st.markdown('<div class="prod-entradas">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Salchipapa Clásica\n\nS/ 10.00", key="e1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Salchipapa Clásica", "precio": 10.00})
    if c2.button("Papas Fritas\n\nS/ 8.00", key="e2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Papas Fritas", "precio": 8.00})
    if c3.button("Tequeños (6u)\n\nS/ 12.00", key="e3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Tequeños (6u)", "precio": 12.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🥤 OTROS (Celeste #0EA5E9)
    st.markdown("### 🥤 Otros")
    st.markdown('<div class="prod-otros">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Inca Kola 500ml\n\nS/ 4.50", key="o1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Inca Kola 500ml", "precio": 4.50})
    if c2.button("Coca Cola 500ml\n\nS/ 4.50", key="o2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Coca Cola 500ml", "precio": 4.50})
    if c3.button("Agua Mineral\n\nS/ 3.00", key="o3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Agua Mineral", "precio": 3.00})
    st.markdown('</div>', unsafe_allow_html=True)


# --- COLUMNA DERECHA: TARJETA DE PEDIDO ACTUAL ---
with col_pedido:
    total_pagar = sum(item['precio'] for item in st.session_state.carrito)
    
    # Tarjeta clara para resaltar el detalle de la venta
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
    
    # Botones grandes de método de pago
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
