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

# --- COLUMNA IZQUIERDA: MENÚ OFICIAL PILO BURGER ---
with col_menu:
    
    # 🍕 PIZZAS (Azul #2563EB)
    st.markdown("### 🍕 Pizzas")
    st.markdown('<div class="prod-pizzas">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Pizza Americana Personal\n\nS/ 25.00", key="p1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Americana Personal", "precio": 25.00})
    if c2.button("Pizza Hawaiana Personal\n\nS/ 25.00", key="p2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Hawaiana Personal", "precio": 25.00})
    if c3.button("Pizza Peperoni Personal\n\nS/ 25.00", key="p3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Peperoni Personal", "precio": 25.00})
    if c4.button("Pizza Pilo Personal\n\nS/ 28.00", key="p4", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Pilo Personal", "precio": 28.00})

    c5, c6, c7, c8 = st.columns(4)
    if c5.button("Pizza Americana Familiar\n\nS/ 45.00", key="p5", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Americana Familiar", "precio": 45.00})
    if c6.button("Pizza Hawaiana Familiar\n\nS/ 45.00", key="p6", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Hawaiana Familiar", "precio": 45.00})
    if c7.button("Pizza Peperoni Familiar\n\nS/ 45.00", key="p7", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Peperoni Familiar", "precio": 45.00})
    if c8.button("Pizza Pilo Familiar\n\nS/ 50.00", key="p8", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Pizza Pilo Familiar", "precio": 50.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🍗 ALITAS (Amarillo #EAB308)
    st.markdown("### 🍗 Alitas")
    st.markdown('<div class="prod-alitas">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Alitas Rebozadas\n\nS/ 20.00", key="a1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas Rebozadas", "precio": 20.00})
    if c2.button("Alitas BBQ\n\nS/ 22.00", key="a2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas BBQ", "precio": 22.00})
    if c3.button("Alitas Acevichadas\n\nS/ 22.00", key="a3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas Acevichadas", "precio": 22.00})
        
    c4, c5 = st.columns(2)
    if c4.button("Alitas Búfalo\n\nS/ 22.00", key="a4", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas Búfalo", "precio": 22.00})
    if c5.button("Alitas Pilo\n\nS/ 24.00", key="a5", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Alitas Pilo", "precio": 24.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🍔 HAMBURGUESAS (Naranja #F97316)
    st.markdown("### 🍔 Hamburguesas")
    st.markdown('<div class="prod-burgers">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Hamb. Clásica\n\nS/ 6.00", key="h1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamburguesa Clásica", "precio": 6.00})
    if c2.button("Hamb. Hawaiana\n\nS/ 8.00", key="h2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamburguesa Hawaiana", "precio": 8.00})
    if c3.button("Hamb. Pilo\n\nS/ 9.00", key="h3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamburguesa Pilo", "precio": 9.00})
        
    c4, c5, c6 = st.columns(3)
    if c4.button("Hamb. A lo pobre\n\nS/ 10.00", key="h4", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamburguesa A lo pobre", "precio": 10.00})
    if c5.button("Hamb. Royal\n\nS/ 14.00", key="h5", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamburguesa Royal", "precio": 14.00})
    if c6.button("Hamb. Mega Pilo\n\nS/ 16.00", key="h6", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Hamburguesa Mega Pilo", "precio": 16.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🍟 ENTRADAS (Verde #16A34A)
    st.markdown("### 🍟 Entradas")
    st.markdown('<div class="prod-entradas">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Choripan\n\nS/ 6.00", key="e1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Choripan", "precio": 6.00})
    if c2.button("Salchipapa Clásica\n\nS/ 8.00", key="e2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Salchipapa Clásica", "precio": 8.00})
    if c3.button("Salchialita\n\nS/ 16.00", key="e3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Salchialita", "precio": 16.00})
    st.markdown('</div>', unsafe_allow_html=True)

    # 🥤 OTROS Y BEBIDAS (Celeste #0EA5E9)
    st.markdown("### 🥤 Otros y Bebidas")
    st.markdown('<div class="prod-otros">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Porción de Papa\n\nS/ 5.00", key="o1", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Porción de Papa", "precio": 5.00})
    if c2.button("Porción de Maduro\n\nS/ 5.00", key="o2", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Porción de Maduro", "precio": 5.00})
    if c3.button("Porción Alitas (x ud)\n\nS/ 4.00", key="o3", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Porción de Alitas (x ud)", "precio": 4.00})
        
    c4, c5, c6 = st.columns(3)
    if c4.button("Inca Kola 500ml\n\nS/ 5.00", key="o4", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Inca Kola 500ml", "precio": 5.00})
    if c5.button("Coca Cola 500ml\n\nS/ 5.00", key="o5", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Coca Cola 500ml", "precio": 5.00})
    if c6.button("Chicha Morada\n\nS/ 3.00", key="o6", use_container_width=True):
        st.session_state.carrito.append({"nombre": "Chicha Morada", "precio": 3.00})
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
