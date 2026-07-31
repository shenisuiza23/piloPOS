import streamlit as st

def aplicar_estilos_css(cat_activa="Pizzas"):
    css = """
    <style>
        /* Ocultar elementos predeterminados de Streamlit */
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }

        .main .block-container {
            padding-top: 0.3rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            max-width: 100% !important;
            background-color: #121212;
        }

        /* Banner superior naranja estilo Pilo POS */
        .pilo-header {
            background: linear-gradient(90deg, #FF4500 0%, #FF5722 100%);
            color: white;
            padding: 8px 15px;
            border-radius: 8px;
            margin-bottom: 10px !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0px 4px 10px rgba(255, 69, 0, 0.3);
        }

        .pilo-header h1 {
            font-size: 22px !important;
            font-weight: 900;
            margin: 0 !important;
            color: #FFFFFF !important;
            text-transform: uppercase;
        }

        /* Botones de Categorías con Colores Vibrantes */
        div[data-testid="stHorizontalBlock"] button[key*="cat_Pizzas"] {
            background-color: #007BFF !important; color: white !important; font-weight: bold; font-size: 15px !important; border-radius: 6px !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Alitas"] {
            background-color: #FF8C00 !important; color: white !important; font-weight: bold; font-size: 15px !important; border-radius: 6px !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Hamburguesas"] {
            background-color: #D97706 !important; color: white !important; font-weight: bold; font-size: 15px !important; border-radius: 6px !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Entradas"] {
            background-color: #E11D48 !important; color: white !important; font-weight: bold; font-size: 15px !important; border-radius: 6px !important;
        }
        div[data-testid="stHorizontalBlock"] button[key*="cat_Otros"] {
            background-color: #0EA5E9 !important; color: white !important; font-weight: bold; font-size: 15px !important; border-radius: 6px !important;
        }

        /* Tarjetas de Productos Oscuras con Bordes Azules */
        div[data-testid="stVerticalBlock"] div.stButton > button[key*="p_"] {
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            border: 1px solid #3B82F6 !important;
            border-radius: 10px !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            padding: 12px 8px !important;
            min-height: 65px !important;
            transition: all 0.2s ease-in-out;
        }

        div[data-testid="stVerticalBlock"] div.stButton > button[key*="p_"]:hover {
            background-color: #2563EB !important;
            color: white !important;
            transform: scale(1.02);
        }

        /* Botón de COBRAR Verde Fuerte */
        button[key="btn_cobrar"] {
            background-color: #22C55E !important;
            color: white !important;
            font-size: 18px !important;
            font-weight: 900 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            border: none !important;
        }

        /* Botón de VACIAR Rojo */
        button[key="btn_vaciar"] {
            background-color: #EF4444 !important;
            color: white !important;
            font-size: 16px !important;
            font-weight: 800 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            border: none !important;
        }

        /* Cuadro del Total en Verde Neón */
        .total-card {
            font-size: 28px !important;
            font-weight: 900 !important;
            color: #22C55E !important;
            background-color: #0F172A !important;
            padding: 10px;
            border-radius: 8px;
            text-align: right;
            margin: 10px 0;
            border: 1px solid #1E293B;
        }

        /* Botones de incremento y decremento en Carrito */
        button[key*="plus_"], button[key*="minus_"] {
            background-color: #334155 !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 5px !important;
        }

        button[key*="del_"] {
            background-color: #DC2626 !important;
            color: white !important;
            border-radius: 5px !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
