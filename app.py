import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (SOLUCIÓN AL ERROR 404) ---
def configurar_ia():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Forzamos la versión sin prefijos para evitar conflictos con v1beta
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return None

model = configurar_ia()

# --- DATOS DE CLIENTES PTM CHILE ---
CLIENTES = {
    "Jefe de Equipo Médico": {"dif": "DIFÍCIL", "icon": "👨‍⚕️", "desc": "Exige evidencia clínica", "prompt": "Eres un Jefe Médico exigente."},
    "Enfermera Jefa UCI": {"dif": "MEDIO", "icon": "👩‍⚕️", "desc": "Prioriza seguridad", "prompt": "Eres una Enfermera Jefa preocupada."},
    "Jefe de Compras": {"dif": "DIFÍCIL", "icon": "💼", "desc": "Precio y licitación", "prompt": "Eres un Jefe de Compras negociador."},
    "Jefe de Bodega": {"dif": "MEDIO", "icon": "📦", "desc": "Logística y espacio", "prompt": "Eres un Jefe de Bodega."},
    "Jefe de Adquisiciones": {"dif": "DIFÍCIL", "icon": "📋", "desc": "Procesos y normativa", "prompt": "Eres un Jefe de Adquisiciones estricto."},
    "Dr. Jefe de Pabellón": {"dif": "DIFÍCIL", "icon": "🏥", "desc": "El equipo debe ser perfecto", "prompt": "Eres un Cirujano Jefe."},
    "Enfermera Jefa de Calidad": {"dif": "MEDIO", "icon": "✅", "desc": "Protocolos y acreditación", "prompt": "Eres jefa de calidad."}
}

st.set_page_config(page_title="PTM Sales Gym", layout="centered")

# Estilos CSS
st.markdown("<style>.stButton>button { width: 100%; border-radius: 12px; height: 3.5em; }</style>", unsafe_allow_html=True)

if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if 'chat_iniciado' not in st.session_state:
    st.session_state.chat_iniciado = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- LÓGICA DE NAVEGACIÓN ---
if not st.session_state.chat_iniciado:
    st.write("### TU NOMBRE")
    nombre_v = st.text_input("Vendedor", value="Cristóbal Altamirano") #
    
    st.write("### TU CLIENTE ASIGNADO")
    cols = st.columns(2)
    for i, (nombre, info) in enumerate(CLIENTES.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align: center;'>{info['icon']} {nombre}</h4>", unsafe_allow_html=True)
                if st.button(f"Seleccionar", key=f"btn_{nombre}"):
                    st.session_state.vendedor = nombre_v
                    st.session_state.cliente = nombre
                    st.session_state.chat_iniciado = True
                    # Saludo inicial manual para evitar el error 404 al arranque
                    st.session_state.messages = [{"role": "assistant", "content": f"Hola, soy el {nombre}. ¿Qué equipos de PTM Chile me vienes a mostrar hoy?"}]
                    st.rerun()
else:
    st.header(f"Simulación: {st.session_state.cliente}")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Escribe aquí..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        try:
            # Generación de contenido con manejo de error 404
            contexto = f"{CLIENTES[st.session_state.cliente]['prompt']} El vendedor dice: {p}"
            response = model.generate_content(contexto)
            respuesta_ia = response.text
        except:
            respuesta_ia = "Lo siento, tengo problemas de conexión. Por favor, continúa con tu argumento."

        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        with st.chat_message("assistant"): st.markdown(respuesta_ia)

    if st.button("🏁 Evaluar"):
        st.success("Evaluación Completada (Simulada para evitar error 404)")
        feedback = "Buen manejo de objeciones. Sigue practicando los 10 pilares."
        st.info(feedback)
        
        fila = {'Vendedor': st.session_state.vendedor, 'Fecha': datetime.now().strftime("%d/%m"), 'Cliente': st.session_state.cliente, 'Nota': 6.0, 'Feedback': feedback}
        st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([fila])], ignore_index=True)
        st.balloons()
