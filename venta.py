import sqlite3
import pandas as pd
import streamlit as st
from database import get_connection

def render_ventas_del_dia():
    st.subheader("📋 Ventas del Día de Hoy")
    conn = get_connection()
    
    query = """
        SELECT 
            v.correlativo AS 'N° Boleta',
            v.fecha AS 'Fecha / Hora',
            v.metodo AS 'Método Pago',
            v.total AS 'Total (S/)',
            GROUP_CONCAT(p.nombre || ' (x' || dv.cantidad || ')', ', ') AS 'Detalle Productos'
        FROM ventas v
        JOIN detalle_venta dv ON v.id = dv.venta_id
        JOIN productos p ON dv.producto_id = p.id
        WHERE date(v.fecha) = date('now', 'localtime')
        GROUP BY v.id
        ORDER BY v.id DESC
    """
    df_hoy = pd.read_sql_query(query, conn)
    conn.close()

    if not df_hoy.empty:
        st.dataframe(df_hoy, use_container_width=True)
        total_hoy = df_hoy["Total (S/)"].sum()
        st.success(f"💰 Total Recaudado Hoy: **S/ {total_hoy:.2f}** ({len(df_hoy)} ventas)")
    else:
        st.info("No hay ventas registradas el día de hoy.")

def render_control_caja(pin_admin):
    st.subheader("🔒 Control y Cierre de Caja")
    clave = st.text_input("Contraseña de Administrador", type="password", key="pass_cierre_caja")

    if clave == pin_admin:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
        caja_activa = c.fetchone()

        if caja_activa:
            caja_id, monto_inicial, _, _, _, fecha_apertura, _, _ = caja_activa
            st.success(f"🟢 Caja ABIERTA desde: **{fecha_apertura}**")
            st.write(f"💵 Monto Inicial en Caja: **S/ {monto_inicial:.2f}**")

            # Ventas de este turno en efectivo y digital
            query_ef = "SELECT SUM(monto_efectivo) FROM ventas WHERE fecha >= ?"
            query_dig = "SELECT SUM(monto_digital) FROM ventas WHERE fecha >= ?"
            
            c.execute(query_ef, (fecha_apertura,))
            tot_efectivo = c.fetchone()[0] or 0.0

            c.execute(query_dig, (fecha_apertura,))
            tot_digital = c.fetchone()[0] or 0.0

            conn.close()

            m1, m2, m3 = st.columns(3)
            m1.metric("💵 Ingresos Efectivo", f"S/ {tot_efectivo:.2f}")
            m2.metric("📲 Ingresos Digitales (Yape/Plin)", f"S/ {tot_digital:.2f}")
            
            # CORRECCIÓN CLAVE: El monto final físico en caja solo suma EFECTIVO
            efectivo_total_en_caja = monto_inicial + tot_efectivo
            m3.metric("💰 Efectivo Físico en Caja", f"S/ {efectivo_total_en_caja:.2f}")

            st.markdown("---")
            if st.button("🔒 CERRAR CAJA Y FINALIZAR TURNO", use_container_width=True):
                conn_close = get_connection()
                c_close = conn_close.cursor()
                fecha_cierre = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                c_close.execute(
                    "UPDATE caja SET monto_final = ?, monto_efectivo = ?, monto_digital = ?, fecha_cierre = ?, estado = 'CERRADA' WHERE id = ?",
                    (efectivo_total_en_caja, tot_efectivo, tot_digital, fecha_cierre, caja_id)
                )
                conn_close.commit()
                conn_close.close()
                st.success("¡Caja Cerrada Correctamente!")
                st.rerun()
        else:
            conn.close()
            st.info("La caja está CERRADA actualmente.")
    elif clave:
        st.error("Contraseña incorrecta")
