import streamlit as st

def aplicar_estilos_css(cat_activa="Pizzas"):
    css = """
    <style>
        /* Fondo principal oscuro estilo POS */
        .stApp {
            background-color: #0d0f14 !important;
            color: #ffffff !important;
        }

        /* Ocultar barra superior por defecto de Streamlit */
        header[data-testid="stHeader"], footer {
            display: none !important;
        }

        .main .block-container {
            padding-top: 1rem !important;
            max-width: 100% !important;
        }

        /* Pestañas (Tabs) estilo naranja / activo */
        button[data-baseweb="tab"] {
            color: #9ca3af !important;
            font-weight: bold !important;
            font-size: 15px !important;
        }
        button[aria-selected="true"] {
            color: #ef4444 !important; /* Color naranja/rojo del tab activo */
            border-bottom-color: #ef4444 !important;
        }

        /* Tarjetas desplegables del historial de ventas */
        div[data-testid="stExpander"] {
            background-color: #141720 !important;
            border: 1px solid #232836 !important;
            border-radius: 8px !important;
            margin-bottom: 6px !important;
        }

        div[data-testid="stExpander"] summary {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 14px !important;
        }

        /* Totales en Grande (Efectivo / Ventas) */
        div[data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 900 !important;
            color: #ffffff !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
