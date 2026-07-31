import pandas as pd
import streamlit as st
from database import get_connection

def render_inventario(pin_admin):
    st.subheader("📦 Control de Inventario y Stock")
    clave = st.text_input("Contraseña de Administrador", type="password", key="pass_inv")

    if clave == pin_admin:
        conn = get_connection()
        df_stock = pd.read_sql_query("SELECT id AS ID, nombre AS Producto, categoria AS Categoría, precio AS 'Precio S/', stock AS Stock FROM productos ORDER BY categoria, nombre", conn)
        conn.close()

        st.dataframe(df_stock, use_container_width=True)

        st.markdown("### ➕ Reabastecer Stock")
        c1, c2, c3 = st.columns([2, 1, 1])
        prod_sel = c1.selectbox("Seleccionar Producto", df_stock["Producto"].tolist())
        cant_sumar = c2.number_input("Cantidad a Añadir", min_value=1, value=10)

        if c3.button("Actualizar Stock", use_container_width=True):
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE productos SET stock = stock + ? WHERE nombre = ?", (cant_sumar, prod_sel))
            conn.commit()
            conn.close()
            st.success(f"Stock de {prod_sel} actualizado (+{cant_sumar})")
            st.rerun()
