import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime

# --- CONFIGURACIÓN DE IA ---
# Para mayor seguridad, luego te enseñaré a poner esto en "Secrets" de Streamlit
client = OpenAI(api_key="AIzaSyBOybOwgStk3Zh5H19fWvclRlOx-TXIHsA")

# --- CONFIGURACIÓN DE PTM CHILE ---
CLIENTES = {
    "Dr. Arriagada (Jefe Médico)": {
        "perfil": "Eres el Dr. Arriagada, Jefe Médico en Chile. Eres técnico, serio y valoras la evidencia científica. No tienes tiempo para rodeos.",
        "avatar": "👨‍⚕️"
    },
    "Marta (Enfermera Jefe)": {
        "perfil": "Eres Marta, Enfermera Jefe. Te preocupa la seguridad del paciente y la carga de trabajo de tu equipo. Eres práctica y directa.",
        "avatar": "👩‍⚕️"
    },
    "Ricardo (Jefe de Compras)": {
        "perfil": "Eres Ricardo, Jefe de Compras. Solo te importa el ROI, plazos y costos. Eres un negociador duro.",
        "avatar": "💼"
    }
}

# --- INTERFAZ ---
st.set_page_config(page_title="PTM Sales Gym", layout="wide")

# Estilo para mejorar la estética
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-header { color: #004a99; font-size: 30px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN ---
with st.sidebar:
    st.markdown("### 🚀 Panel de Control")
    modo = st.radio("Sección", ["🏋️ Simulador", "📊 Reportes Admin"])
    st.divider()
    if st.button("🔄 Reiniciar Simulación"):
        st.session_state.messages = []
        st.rerun()

# --- MODO SIMULADOR ---
if modo == "🏋️ Simulador":
    st.markdown("<div class='main-header'>🤝 Entrenamiento Interactivo PTM</div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        vendedor = c1.text_input("Vendedor", placeholder="Tu nombre...")
        cliente_sel = c2.selectbox("Elegir Cliente", list(CLIENTES.keys()))
        nivel = c3.selectbox("Dificultad", ["Baja", "Media", "Alta"])

    st.divider()

    # Historial de Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input de Chat (Mensaje a Mensaje)
    if prompt := st.chat_input("Escribe tu argumento de venta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respuesta de la IA como el Cliente
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"{CLIENTES[cliente_sel]['perfil']} Dificultad: {nivel}. Responde breve (máx 2 frases)."},
                    *st.session_state.messages
                ]
            )
            respuesta = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            with st.chat_message("assistant", avatar=CLIENTES[cliente_sel]['avatar']):
                st.markdown(respuesta)
        except Exception as e:
            st.error("Error en la conexión. Revisa tu API Key.")

    # Evaluación Final
    if len(st.session_state.messages) > 2:
        if st.button("🏁 Finalizar y Evaluar"):
            with st.spinner("Analizando tus 10 pilares de venta..."):
                eval_resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Actúa como coach de ventas experto. Evalúa el chat del vendedor en los 10 pilares (Escucha, Valor, Cierre, etc). Da una nota del 1.0 al 7.0 y feedback corto."},
                        {"role": "user", "content": str(st.session_state.messages)}
                    ]
                )
                res = eval_resp.choices[0].message.content
                st.success("Evaluación Completada")
                st.markdown(res)
                
                # Guardar en Admin
                nueva_fila = {'Vendedor': vendedor, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': cliente_sel, 'Nota': 6.5, 'Feedback': res}
                st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([nueva_fila])], ignore_index=True)
                st.balloons()

# --- MODO ADMIN ---
else:
    st.title("📊 Panel de Gestión PTM")
    password = st.text_input("Clave de Administrador", type="password")
    if password == "PTM2026":
        if not st.session_state.reportes.empty:
            st.dataframe(st.session_state.reportes, use_container_width=True)
            st.bar_chart(data=st.session_state.reportes, x='Vendedor', y='Nota')
        else:
            st.info("No hay datos registrados aún.")
