import streamlit as st
import pandas as pd

# Tus 10 pilares de éxito para PTM Chile
PILARES = ["Mentalidad de asesor", "Escucha activa", "Descubrimiento de necesidades", "Autoridad técnica", "Manejo de objeciones", "Seguridad emocional", "Urgencia", "Enfoque en valor", "Lectura del cliente", "Cierre natural"]

st.set_page_config(page_title="Gym de Ventas PTM", layout="wide")

# Almacenamiento local para el reporte (se reinicia al cerrar la sesión)
if 'reporte' not in st.session_state:
    st.session_state.reporte = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Nota', 'Feedback'])

st.sidebar.title("Navegación")
modo = st.sidebar.radio("Ir a:", ["Simulador (Vendedores)", "Reportes (Administrador)"])

if modo == "Simulador (Vendedores)":
    st.title("🏋️ Misión: Cerrar la Venta")
    nombre = st.text_input("Ingresa tu nombre")
    cliente = st.selectbox("Cliente:", ["Jefe de Equipo Médico", "Enfermera Jefa UCI", "Jefe de Compras"])
    st.info("Pega el chat de tu simulación abajo para ser evaluado:")
    chat_input = st.text_area("Chat completo:", height=250)
    
    if st.button("Finalizar y Evaluar"):
        # Registro de prueba para que veas la reportabilidad
        nueva_fila = {'Vendedor': nombre, 'Fecha': "25/02/2026", 'Nota': 5.5, 'Feedback': "Buen manejo técnico, falta cierre natural."}
        st.session_state.reporte = pd.concat([st.session_state.reporte, pd.DataFrame([nueva_fila])], ignore_index=True)
        st.success("¡Simulación registrada! El administrador ya puede ver tu nota.")

else:
    st.title("📊 Panel de Administrador - PTM Chile")
    if not st.session_state.reporte.empty:
        st.write("Resumen de desempeño del equipo:")
        st.dataframe(st.session_state.reporte, use_container_width=True)
        st.subheader("Gráfico de Notas")
        st.bar_chart(data=st.session_state.reporte, x='Vendedor', y='Nota')
    else:
        st.warning("Aún no hay datos de simulaciones.")
