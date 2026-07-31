import streamlit as st

def aplicar_estilos_css(cat_activa="Pizzas"):
    css = """
    <style>
        /* Fondo negro total */
        .stApp { background-color: #0b0c0e !important; }

        /* Ocultar espacios vacíos de Streamlit */
        header[data-testid="stHeader"], footer { display: none !important; }
        .main .block-container { padding-top: 0.5rem !important; max-width: 100% !important; }

        /* Tarjetas de productos oscuras y con texto claro */
        div[data-testid="stVerticalBlock"] div.stButton > button {
            background-color: #161922 !important;
            color: #ffffff !important;
            border: 1px solid #232734 !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            min-height: 60px !important;
        }

        /* Total en Verde Neón */
        .stMarkdown div[data-testid="stMarkdownContainer"] h1, 
        .stMarkdown div[data-testid="stMarkdownContainer"] h2 {
            color: #22c55e !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
