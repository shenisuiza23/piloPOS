import streamlit as st
import sqlite3
from datetime import datetime
from config import DB_NAME
from database import get_connection

def render_ventas_del_dia():
    st.markdown("### 📋 Historial de Ventas del Día")
    
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_connection()
    c = conn.cursor()
    
    # Consultar ventas del día actual
    c.execute("""
        SELECT correlativo, total, metodo, monto_efectivo, monto_digital, fecha 
        FROM ventas 
        WHERE fecha LIKE ? 
        ORDER BY id DESC
    """, (f"{fecha_hoy}%",))
    
    ventas = c.fetchall()
    
    if not ventas:
        st.info("ℹ️ Aún no se han registrado ventas el día de hoy.")
    else:
        # Resumen rápido del día
        total_dia = sum(v["total"] for v in ventas)
        efectivo_dia = sum(v["monto_efectivo"] for v in ventas)
        digital_dia = sum(v["monto_digital"] for v in ventas)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Vendido Hoy", f"S/ {total_dia:.2f}")
        c2.metric("Total Efectivo", f"S/ {efectivo_dia:.2f}")
        c3.metric("Total Digital (Yape/Plin)", f"S/ {digital_dia:.2f}")
        
        st.markdown("---")
        
        # Tabla de ventas
        for v in ventas:
            with st.expander(f"🧾 {v['correlativo']} — S/ {v['total']:.2f} ({v['metodo']}) — 🕒 {v['fecha'].split(' ')[1]}"):
                st.write(f"**Método de Pago:** {v['metodo']}")
                st.write(f"**Efectivo:** S/ {v['monto_efectivo']:.2f} | **Digital:** S/ {v['monto_digital']:.2f}")
                
                # Detalle de productos de esta venta
                c.execute("""
                    SELECT producto_nombre, cantidad, precio_unitario, subtotal 
                    FROM detalle_ventas 
                    WHERE correlativo = ?
                """, (v['correlativo'],))
                detalles = c.fetchall()
                
                st.markdown("**Productos:**")
                for d in detalles:
                    st.write(f"• {d['producto_nombre']} x{d['cantidad']} — S/ {d['subtotal']:.2f} (S/ {d['precio_unitario']:.2f} c/u)")
                    
    conn.close()


def render_control_caja(pin_admin):
    st.markdown("### 🔒 Control y Arqueo de Caja")
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM caja WHERE estado = 'ABIERTA'")
    caja_activa = c.fetchone()
    
    if caja_activa:
        st.success(f"🟢 **CAJA ABIERTA** desde: {caja_activa['fecha_apertura']}")
        st.write(f"**Monto Inicial en Caja:** S/ {caja_activa['monto_inicial']:.2f}")
        
        # Calcular ventas acumuladas durante este turno
        fecha_apertura = caja_activa['fecha_apertura']
        c.execute("SELECT SUM(total), SUM(monto_efectivo), SUM(monto_digital) FROM ventas WHERE fecha >= ?", (fecha_apertura,))
        res_ventas = c.fetchone()
        
        tot_ventas = res_ventas[0] if res_ventas[0] else 0.0
        tot_ef = res_ventas[1] if res_ventas[1] else 0.0
        tot_dig = res_ventas[2] if res_ventas[2] else 0.0
        
        efectivo_esperado = caja_activa['monto_inicial'] + tot_ef
        
        st.markdown("---")
        st.markdown("#### 📊 Arqueo en Tiempo Real")
        col1, col2, col3 = st.columns(3)
        col1.metric("Ventas Totales Turno", f"S/ {tot_ventas:.2f}")
        col2.metric("Efectivo Esperado en Caja", f"S/ {efectivo_esperado:.2f}")
        col3.metric("Digital (Yape/Plin)", f"S/ {tot_dig:.2f}")
        
        st.markdown("---")
        st.markdown("#### 🔴 Cierre de Caja")
        monto_real_ef = st.number_input("Monto de Efectivo Real Contado en Caja (S/):", min_value=0.0, value=efectivo_esperado)
        pin_ingresado = st.text_input("PIN de Administrador para Cerrar:", type="password", key="pin_close")
        
        if st.button("🔒 CERRAR CAJA Y REPORTE", use_container_width=True):
            if pin_ingresado == pin_admin:
                fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""
                    UPDATE caja 
                    SET fecha_cierre = ?, monto_final = ?, estado = 'CERRADA' 
                    WHERE id = ?
                """, (fecha_cierre, monto_real_ef, caja_activa['id']))
                conn.commit()
                st.success("¡Caja cerrada correctamente!")
                st.rerun()
            else:
                st.error("❌ PIN Incorrecto")
    else:
        st.warning("🔴 **LA CAJA SE ENCUENTRA CERRADA**")
        st.markdown("#### 🔓 Abrir Turno de Caja")
        
        c1, c2 = st.columns(2)
        monto_ini = c1.number_input("Monto Inicial en Caja (S/):", min_value=0.0, value=0.0, step=5.0)
        pin_ingresado = c2.text_input("PIN de Administrador:", type="password", key="pin_open")
        
        if st.button("🔓 ABRIR CAJA", use_container_width=True):
            if pin_ingresado == pin_admin:
                fecha_ap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""
                    INSERT INTO caja (monto_inicial, fecha_apertura, estado) 
                    VALUES (?, ?, 'ABIERTA')
                """, (monto_ini, fecha_ap))
                conn.commit()
                st.success("¡Caja abierta exitosamente!")
                st.rerun()
            else:
                st.error("❌ PIN Incorrecto")
                
    conn.close()
