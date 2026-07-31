import streamlit as st

def aplicar_estilos_css(cat_activa="Pizzas"):
    css = """
    <style>
        /* Fondo general ultra oscuro */
        .stApp {
            background-color: #0d0e12 !important;
        }

        /* Ocultar elementos predeterminados */
        header[data-testid="stHeader"], footer {
            display: none !important;
        }

        .main .block-container {
            padding: 0.2rem 0.5rem !important;
            max-width: 100% !important;
        }

        /* BANNER SUPERIOR NARANJA (Pilo POS) */
        .header-pilo {
            background-color: #FF4500;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 15px;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        .header-title {
            color: white;
            font-size: 20px;
            font-weight: 900;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* BOTONES DE ACCIÓN SUPERIORES (COBRAR Y VACIAR) */
        button[key="btn_cobrar_top"] {
            background-color: #22c55e !important;
            color: white !important;
            font-weight: 800 !important;
            border: none !important;
            border-radius: 6px !important;
            height: 42px !important;
        }
        button[key="btn_vaciar_top"] {
            background-color: #ef4444 !important;
            color: white !important;
            font-weight: 800 !important;
            border: none !important;
            border-radius: 6px !important;
            height: 42px !important;
        }

        /* CATEGORÍAS EN BLOQUES DE COLORES */
        div[data-testid="stHorizontalBlock"] button[key*="cat_Pizzas"] {
            background-color: #007bff !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Alitas"] {
            background-color: #d97706 !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Hamburguesas"] {
            background-color: #b45309 !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Entradas"] {
            background-color: #dc2626 !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Otros"] {
            background-color: #0284c7 !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important;
        }

        /* TARJETAS DE PRODUCTO (Fondo oscuro, texto limpio) */
        .product-card {
            background-color: #1a1d24;
            border-radius: 8px;
            padding: 8px;
            text-align: center;
            border: 1px solid #2a2e39;
        }
        .product-title {
            color: #ffffff;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .product-price {
            color: #38bdf8;
            font-size: 14px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        /* CONTROLES + / - DENTRO DE LA TARJETA */
        button[key*="prod_minus_"], button[key*="prod_plus_"] {
            background-color: #007bff !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 4px !important;
            padding: 2px 8px !important;
            min-height: 28px !important;
            border: none !important;
        }

        /* RESUMEN DEL TOTAL Y VUELTO EN VERDE NEÓN */
        .total-display {
            font-size: 32px;
            font-weight: 900;
            color: #22c55e;
            text-align: right;
        }
        .vuelto-display {
            font-size: 26px;
            font-weight: 900;
            color: #22c55e;
            text-align: right;
        }

        /* BARRA INFERIOR DE ESTADO */
        .bottom-bar {
            background-color: #14171d;
            border-top: 1px solid #2a2e39;
            padding: 6px 12px;
            color: #9ca3af;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
