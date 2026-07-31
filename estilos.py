import streamlit as st

# Paleta de colores por categoría
COLORES_CATEGORIAS = {
    "Pizzas": {"bg": "#2563EB", "hover": "#3B82F6", "text": "#FFFFFF"},
    "Alitas": {"bg": "#EAB308", "hover": "#FACC15", "text": "#000000"},
    "Hamburguesas": {"bg": "#F97316", "hover": "#FB923C", "text": "#FFFFFF"},
    "Entradas": {"bg": "#16A34A", "hover": "#22C55E", "text": "#FFFFFF"},
    "Otros": {"bg": "#0EA5E9", "hover": "#38BDF8", "text": "#FFFFFF"},
}

def aplicar_estilos_css(cat_actual="Pizzas"):
    color_cat = COLORES_CATEGORIAS.get(cat_actual, COLORES_CATEGORIAS["Otros"])
    
    st.markdown(f"""
    <style>
    /* Estructura Global y Fondo Tema Oscuro Moderno */
    .stApp {{
        background-color: #111827;
        color: #F3F4F6;
    }}
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }}

    /* Header Pilo Burger */
    .pilo-header {{
        background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 14px;
        margin-bottom: 200px;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
    }}
    .pilo-header h1 {{
        margin: 0;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 0.5px;
        color: #FFFFFF !important;
    }}
    .pilo-header p {{
        margin: 2px 0 0 0;
        font-size: 13px;
        opacity: 0.9;
    }}

    /* Tarjetas de Trabajo */
    .pilo-card {{
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
    }}

    /* Botones Genéricos */
    div.stButton > button {{
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }}

    /* Botones Dinámicos de Productos */
    .st-key-prod_zone button {{
        background-color: {color_cat['bg']} !important;
        color: {color_cat['text']} !important;
        min-height: 85px !important;
        font-size: 17px !important;
        line-height: 1.3 !important;
        white-space: pre-wrap !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    }}
    .st-key-prod_zone button:hover {{
        background-color: {color_cat['hover']} !important;
        transform: translateY(-2px);
    }}

    /* Total en Pedido Actual (Verde Grande) */
    .total-card {{
        background-color: #059669;
        color: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        font-size: 34px;
        font-weight: 900;
        margin: 12px 0;
        box-shadow: 0 4px 10px rgba(5, 150, 105, 0.4);
    }}

    /* Botón Cobrar (24px, 65px alto, Verde) */
    .st-key-btn_cobrar button {{
        background-color: #22C55E !important;
        color: #FFFFFF !important;
        font-size: 24px !important;
        height: 65px !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4) !important;
    }}
    .st-key-btn_cobrar button:hover {{
        background-color: #16A34A !important;
    }}

    /* Botón Vaciar (Rojo) */
    .st-key-btn_vaciar button {{
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        font-size: 16px !important;
        height: 65px !important;
        width: 100% !important;
    }}
    .st-key-btn_vaciar button:hover {{
        background-color: #B91C1C !important;
    }}
    </style>
    """, unsafe_allow_html=True)
