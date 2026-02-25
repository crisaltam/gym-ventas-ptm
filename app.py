import streamlit as st
import pandas as pd

# Tus 10 pilares de éxito
PILARES = ["Mentalidad de asesor", "Escucha activa", "Descubrimiento de necesidades", "Autoridad técnica", "Manejo de objeciones", "Seguridad emocional", "Urgencia", "Enfoque en valor", "Lectura del cliente", "Cierre natural"]

st.set_page_config(page_title="Gym de Ventas PTM", layout="wide")

if 'reporte' not in st.session_state:
    st.session_state.reporte = pd.DataFrame(columns=['Vendedor', 'Nota', 'Feedback'])

menu = st.sidebar.radio("Menú", ["Vendedor: Practicar", "Admin: Reportes"])

if menu == "Vendedor: Practicar":
    st.title("🏋️ Misión: Cerrar la Venta")
    nombre = st.text_input("Tu Nombre")
    chat = st.text_area("Pega el chat de tu simulación aquí:", height=300)
    if st.button("Finalizar y Evaluar"):
        nueva_data = {'Vendedor': nombre, 'Nota': 5.8, 'Feedback': "Buen manejo técnico. ¡Sigue así!"}
        st.session_state.reporte = pd.concat([st.session_state.reporte, pd.DataFrame([nueva_data])], ignore_index=True)
        st.success("¡Registrado! El administrador ya puede ver tu progreso.")

else:
    st.title("📊 Panel de Administrador")
    st.dataframe(st.session_state.reporte)
    if not st.session_state.reporte.empty:
        st.bar_chart(st.session_state.reporte.set_index('Vendedor')['Nota'])
