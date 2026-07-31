import pandas as pd
import streamlit as st
from database import get_connection

def generar_ticket_termico(correlativo, fecha, metodo, carrito, total, ancho_mm=58):
    caracteres_ancho = 32 if ancho_mm == 58 else 48
    sep = "-" * caracteres_ancho
    sep_double = "=" * caracteres_ancho

    lineas = [
        "PILO BURGER".center(caracteres_ancho),
        "Punto de Venta POS".center(caracteres_ancho),
        sep_double,
        f"Boleta: {correlativo}".ljust(caracteres_ancho),
        f"Fecha:  {fecha}".ljust(caracteres_ancho),
        f"Pago:   {metodo}".ljust(caracteres_ancho),
        sep,
    ]

    for item in carrito.values():
        nom = item["nombre"][:caracteres_ancho - 12]
        cant_p = f"{item['cant']}x S/{item['precio']:.2f}"
        subt = f"S/{item['precio']*item['cant']:.2f}"
        lineas.append(f"{nom:<18} {subt:>12}")
        lineas.append(f"   ({cant_p})")

    lineas.extend([
        sep_double,
        f"TOTAL: S/ {total:.2f}".rjust(caracteres_ancho),
        sep_double,
        "¡Gracias por su compra!".center(caracteres_ancho),
        "\n\n\n",
    ])

    return "\n".join(lineas)

def render_reportes(pin_admin):
    st.subheader("📊 Dashboard de Reportes Mensuales")
    clave = st.text_input("Contraseña Administrador", type="password", key="pass_rep_dash")

    if clave == pin_admin:
        conn = get_connection()
        # Filtrado exclusivamente del mes en curso
        query = """
            SELECT v.id, v.correlativo, v.total, v.metodo, v.fecha, dv.producto_id, dv.cantidad, p.nombre 
            FROM ventas v
            JOIN detalle_venta dv ON v.id = dv.venta_id
            JOIN productos p ON dv.producto_id = p.id
            WHERE strftime('%Y-%m', v.fecha) = strftime('%Y-%m', 'now', 'localtime')
        """
        df_mes = pd.read_sql_query(query, conn)
        conn.close()

        if not df_mes.empty:
            total_mes = df_mes["total"].unique().sum()
            num_pedidos = df_mes["id"].nunique()
            ticket_prom = total_mes / num_pedidos if num_pedidos > 0 else 0
            prod_mas_vendido = df_mes.groupby("nombre")["cantidad"].sum().idxmax()

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("💰 Ventas del Mes", f"S/ {total_mes:.2f}")
            kpi2.metric("📦 Cantidad de Pedidos", f"{num_pedidos}")
            kpi3.metric("🧾 Ticket Promedio", f"S/ {ticket_prom:.2f}")
            kpi4.metric("🏆 Producto Más Vendido", f"{prod_mas_vendido}")

            st.markdown("---")
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                st.markdown("### Ventas por Método de Pago")
                metodos_df = df_mes.drop_duplicates(subset=["id"])["metodo"].value_counts()
                st.bar_chart(metodos_df)
            with c_g2:
                st.markdown("### Top 5 Productos Más Vendidos")
                top_prods = df_mes.groupby("nombre")["cantidad"].sum().sort_values(ascending=False).head(5)
                st.bar_chart(top_prods)
        else:
            st.info("No se han registrado ventas en el mes actual.")
