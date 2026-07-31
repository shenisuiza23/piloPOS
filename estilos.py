import streamlit as st

def aplicar_estilos_css(cat_activa="Pizzas"):
    css = """
    <style>
        /* Reducir espacio superior general de Streamlit */
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Encabezado compacto */
        .pilo-header {
            background-color: #FF5722;
            color: white;
            padding: 8px 15px;
            border-radius: 8px;
            margin-bottom: 10px !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .pilo-header h1 {
            font-size: 22px !important;
            font-weight: bold;
            margin: 0 !important;
            padding: 0 !important;
            color: white !important;
        }

        .pilo-header p {
            font-size: 13px !important;
            margin: 0 !important;
            color: #FFE0B2 !important;
        }

        /* Pestañas más grandes y legibles */
        button[data-baseweb="tab"] {
            font-size: 16px !important;
            font-weight: bold !important;
            padding: 8px 16px !important;
        }

        /* Botones de Categorías */
        div[data-testid="column"] button {
            font-size: 15px !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px 5px !important;
        }

        /* Botones de Productos (Tarjeta) */
        div[data-testid="stVerticalBlock"] div.stButton > button {
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 12px 8px !important;
            min-height: 55px !important;
        }

        /* Total y precios grandes */
        .total-card {
            font-size: 24px !important;
            font-weight: bold;
            color: #4CAF50;
            margin: 10px 0;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
