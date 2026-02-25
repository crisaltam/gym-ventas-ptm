import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# REEMPLAZA ESTO CON TU API KEY REAL
API_KEY = "TU_API_KEY_AQUI"

try:
    genai.configure(api_key="AIzaSyBOybOwgStk3Zh5H19fWvclRlOx-TXIHsA")
    # Usamos el nombre de modelo con el prefijo 'models/' que es más estable
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Error al configurar la IA: {e}")

# --- CONFIGURACIÓN DE NEGOCIO PTM ---
CLIENTES = {
    "Dr. Arriagada (Jefe Médico)": {
        "prompt": "Eres el Dr. Arriagada, Jefe Médico en Chile. Eres escéptico, técnico y valoras la evidencia científica. Hablas de forma profesional pero directa.",
        "img": "👨‍⚕️"
    },
    "Marta (Enfermera Jefe)": {
        "prompt": "Eres Marta, Enfermera Jefe. Te preocupa la carga de trabajo y la seguridad del paciente. Eres práctica y algo impaciente.",
        "img": "👩‍⚕️"
    },
    "Ricardo (Jefe de Compras)": {
        "prompt": "Eres Ricardo, Jefe de Compras. Tu única prioridad es el presupuesto y los plazos. Eres duro negociando.",
        "img": "💼"
    }
}

# --- INTERFAZ ---
st.set_page_config(page_title="Gym de Ventas PTM", layout="wide")

if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN ---
with st.sidebar:
    st.title("PTM Sales Gym")
    menu = st.radio("Sección:", ["🏋️ Simulador", "📊 Admin (Reportes)"])
    if st.button("🗑️ Reiniciar Chat"):
        st.session_state.messages = []
        st.rerun()

# --- MODO SIMULADOR ---
if menu == "🏋️ Simulador":
    st.title("🤝 Entrenamiento Interactivo PTM")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        nombre = st.text_input("Vendedor:", placeholder="Tu nombre...")
    with col2:
        c_sel = st.selectbox("Cliente:", list(CLIENTES.keys()))

    st.divider()

    # Mostrar mensajes previos
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    # Chat Input
    if prompt := st.chat_input("Escribe aquí tu argumento..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        try:
            # Construcción del contexto para evitar el error NotFound
            contexto = f"{CLIENTES[c_sel]['prompt']} Responde de forma breve como si fueras el cliente en una reunión. El vendedor dice: {prompt}"
            response = model.generate_content(contexto)
            
            respuesta_ia = response.text
            with st.chat_message("assistant"):
                st.write(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        except Exception as e:
            st.error(f"La IA no pudo responder: {e}. Revisa si tu API Key es válida.")

    # Evaluación
    if len(st.session_state.messages) > 2:
        if st.button("🏁 Finalizar y Evaluar"):
            try:
                eval_prompt = f"Actúa como un experto en ventas. Evalúa esta conversación basándote en 10 pilares de venta: {st.session_state.messages}. Entrega una nota del 1.0 al 7.0 y un feedback breve."
                eval_res = model.generate_content(eval_prompt)
                
                st.subheader("Resultado de la Evaluación")
                st.markdown(eval_res.text)
                
                # Guardar registro para el Admin
                new_row = {'Vendedor': nombre, 'Fecha': datetime.now().strftime("%Y-%m-%d"), 'Cliente': c_sel, 'Nota': 0.0, 'Feedback': eval_res.text}
                st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([new_row])], ignore_index=True)
                st.balloons()
            except Exception as e:
                st.error(f"Error en la evaluación: {e}")

# --- MODO ADMIN ---
else:
    st.title("📊 Panel Administrador")
    clave = st.text_input("Clave", type="password")
    if clave == "PTM2026":
        st.dataframe(st.session_state.reportes)
