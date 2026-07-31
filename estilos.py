import streamlit as st

def aplicar_estilos_css(cat_activa="Pizzas"):
    css = """
    <style>
        /* 1. CONFIGURACIÓN GENERAL Y FONDO MÁS SUAVE (Gris muy oscuro en lugar de negro puro) */
        header[data-testid="stHeader"], footer { display: none !important; }
        .main .block-container { 
            padding-top: 0px !important; 
            max-width: 100% !important; 
            padding-left: 10px; 
            padding-right: 10px; 
        }
        .stApp { background-color: #1a1d24 !important; color: white; }

        /* 2. ENCABEZADO PILO BURGER (#F97316) */
        .pilo-header {
            background-color: #F97316 !important;
            padding: 12px 20px;
            border-radius: 0 0 10px 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .pilo-title {
            font-size: 26px;
            font-weight: 900;
            color: #ffffff;
            margin: 0;
            line-height: 1.1;
        }
        .pilo-subtitle {
            font-size: 14px;
            font-weight: 600;
            color: #fff3eb;
        }

        /* 3. BOTÓN COBRAR (#22C55E, 65px alto, 24px letra) */
        div.stButton > button[key="btn_cobrar"] {
            background-color: #22C55E !important;
            color: #ffffff !important;
            font-size: 24px !important;
            font-weight: 900 !important;
            height: 65px !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4) !important;
        }
        div.stButton > button[key="btn_cobrar"]:hover {
            background-color: #4ade80 !important;
        }

        /* 4. BOTÓN VACIAR (#DC2626) */
        div.stButton > button[key="btn_vaciar"] {
            background-color: #DC2626 !important;
            color: #ffffff !important;
            font-size: 18px !important;
            font-weight: 800 !important;
            height: 65px !important;
            border-radius: 10px !important;
            border: none !important;
        }
        div.stButton > button[key="btn_vaciar"]:hover {
            background-color: #ef4444 !important;
        }

        /* 5. TARJETAS DE PRODUCTOS POR CATEGORÍA (85px alto, fondo de color, texto blanco) */

        /* 🍕 PIZZAS -> Azul #2563EB */
        .prod-pizzas button {
            background-color: #2563EB !important;
            color: #ffffff !important;
            height: 85px !important;
            border-radius: 10px !important;
            border: none !important;
        }
        .prod-pizzas button:hover { background-color: #3b82f6 !important; }

        /* 🍗 ALITAS -> Amarillo #EAB308 */
        .prod-alitas button {
            background-color: #EAB308 !important;
            color: #ffffff !important; /* O #000000 si prefieres más contraste visual */
            height: 85px !important;
            border-radius: 10px !important;
            border: none !important;
        }
        .prod-alitas button:hover { background-color: #facc15 !important; }

        /* 🍔 HAMBURGUESAS -> Naranja #F97316 */
        .prod-burgers button {
            background-color: #F97316 !important;
            color: #ffffff !important;
            height: 85px !important;
            border-radius: 10px !important;
            border: none !important;
        }
        .prod-burgers button:hover { background-color: #fb923c !important; }

        /* 🍟 ENTRADAS -> Verde #16A34A */
        .prod-entradas button {
            background-color: #16A34A !important;
            color: #ffffff !important;
            height: 85px !important;
            border-radius: 10px !important;
            border: none !important;
        }
        .prod-entradas button:hover { background-color: #22c55e !important; }

        /* 🥤 OTROS -> Celeste #0EA5E9 */
        .prod-otros button {
            background-color: #0EA5E9 !important;
            color: #ffffff !important;
            height: 85px !important;
            border-radius: 10px !important;
            border: none !important;
        }
        .prod-otros button:hover { background-color: #38bdf8 !important; }

        /* Estilo general para el texto dentro de cualquier botón de producto */
        div[data-testid="stVerticalBlock"] .stButton button p {
            font-size: 16px !important;
            font-weight: 800 !important;
            color: #ffffff !important;
        }

        /* 6. PANEL DEL PEDIDO ACTUAL (Tarjeta clara/Gris claro) */
        .cart-card {
            background-color: #f8fafc !important;
            color: #0f172a !important;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .cart-card h3 {
            color: #0f172a !important;
            margin-bottom: 10px;
        }
        
        /* Separadores de productos en el carrito */
        .cart-item {
            border-bottom: 1px solid #cbd5e1;
            padding: 8px 0;
            display: flex;
            justify-content: space-between;
            color: #1e293b;
            font-weight: 600;
        }

        /* Total Verde Grande */
        .total-grande {
            color: #16a34a !important;
            font-size: 40px !important;
            font-weight: 900 !important;
            text-align: right;
            margin-top: 10px;
        }

        /* Botones de Método de Pago Grandes */
        .btn-pago button {
            height: 50px !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            border-radius: 8px !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
