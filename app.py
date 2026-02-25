import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DEL SIMULADOR ---
CLIENTES = {
    "Dr. Arriagada (Jefe Médico)": "Eres un médico jefe técnico, escéptico y con poco tiempo. Valoras la evidencia científica.",
    "Marta (Enfermera Jefe)": "Te importa la seguridad del paciente y que el equipo no tenga más carga de trabajo.",
    "Ricardo (Comprador)": "Solo te importa el presupuesto, plazos y comparativa de costos."
}

DIFICULTADES = {
    "Baja (Interesado)": "Eres amable y haces preguntas fáciles.",
    "Media (Dudoso)": "Pones 2 o 3 objeciones técnicas antes de ceder.",
    "Alta (Hostil)": "Eres muy difícil, cuestionas todo y tratas de cortar la llamada rápido."
}

st.set_page_config(page_title="PTM Sales Gym", layout="wide")

# Inicializar almacenamiento de reportes para el Admin
if 'db_reportes' not in st.session_state:
    st.session_state.db_reportes = pd.DataFrame(columns=['Vendedor', 'Cliente', 'Dificultad', 'Nota', 'Feedback'])

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN LATERAL ---
st.sidebar.title("Configuración")
modo = st.sidebar.radio("Ir a:", ["Simulador", "Panel Admin"])

if modo == "Simulador":
    st.title("🤝 Simulador de Ventas Interactivo")
    
    # Configuración de la partida
    with st.expander("Configura tu Simulación", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            nombre = st.text_input("Tu Nombre")
        with col2:
            cliente_sel = st.selectbox("Elegir Cliente", list(CLIENTES.keys()))
        with col3:
            nivel = st.selectbox("Dificultad", list(DIFICULTADES.keys()))
        
        if st.button("Iniciar / Reiniciar Simulación"):
            st.session_state.messages = [{"role": "assistant", "content": f"Hola, soy {cliente_sel}. Cuéntame rápido, ¿para qué me buscas?"}]
            st.rerun()

    # Mostrar el Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Entrada de texto del vendedor
    if prompt := st.chat_input("Escribe tu respuesta aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Respuesta del "Cliente" (Aquí es donde la IA respondería de verdad)
        respuesta_ia = f"[{cliente_sel} - {nivel}]: Entiendo, pero necesito saber por qué debería elegir a PTM y no a la competencia."
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        with st.chat_message("assistant"):
            st.write(respuesta_ia)

    # Botón de Evaluación
    if st.button("Finalizar y Evaluar"):
        st.divider()
        st.subheader("📊 Tu Evaluación de Desempeño")
        
        # Simulación de nota basada en los 10 pilares
        nota = 5.8
        feedback = "Excelente dominio técnico, pero podrías mejorar el Cierre Natural."
        
        # Guardar en la tabla de reportes para el Admin
        nuevo_registro = {
            'Vendedor': nombre, 'Cliente': cliente_sel, 
            'Dificultad': nivel, 'Nota': nota, 'Feedback': feedback
        }
        st.session_state.db_reportes = pd.concat([st.session_state.db_reportes, pd.DataFrame([nuevo_registro])], ignore_index=True)
        
        st.metric("Nota Final", f"{nota} / 7.0")
        st.write(f"**Feedback:** {feedback}")

elif modo == "Panel Admin":
    st.title("📊 Reportabilidad PTM Chile")
    if not st.session_state.db_reportes.empty:
        st.dataframe(st.session_state.db_reportes, use_container_width=True)
        st.bar_chart(data=st.session_state.db_reportes, x='Vendedor', y='Nota')
    else:
        st.info("Aún no hay simulaciones registradas.")
