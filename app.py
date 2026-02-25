import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (ESTABLE) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usamos models/ para asegurar que la API lo encuentre
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception:
    st.error("🔑 Error: Revisa 'GEMINI_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# --- CLIENTES PTM CHILE ---
CLIENTES = {
    "Jefe de Equipo Médico": {"dif": "DIFÍCIL", "icon": "👨‍⚕️", "desc": "Exige evidencia clínica y resultados", "prompt": "Eres un Jefe de Equipo Médico técnico y exigente."},
    "Enfermera Jefa UCI": {"dif": "MEDIO", "icon": "👩‍⚕️", "desc": "Prioriza seguridad y facilidad de uso", "prompt": "Eres una Enfermera Jefa enfocada en su equipo."},
    "Jefe de Compras": {"dif": "DIFÍCIL", "icon": "💼", "desc": "Precio, licitación y proveedores", "prompt": "Eres un Jefe de Compras negociador."},
    "Jefe de Bodega": {"dif": "MEDIO", "icon": "📦", "desc": "Logística y stock", "prompt": "Eres un Jefe de Bodega preocupado por el espacio."},
    "Jefe de Adquisiciones": {"dif": "DIFÍCIL", "icon": "📋", "desc": "Contratos y normativa", "prompt": "Eres un Jefe de Adquisiciones estricto."},
    "Dr. Jefe de Pabellón": {"dif": "DIFÍCIL", "icon": "🏥", "desc": "El equipo debe ser perfecto", "prompt": "Eres un Cirujano Jefe con poco tiempo."},
    "Enfermera Jefa de Calidad": {"dif": "MEDIO", "icon": "✅", "desc": "Protocolos y acreditación", "prompt": "Eres jefa de calidad enfocada en normas."}
}

st.set_page_config(page_title="PTM Sales Gym", layout="centered")

# Estilos visuales
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; border: 1px solid #ddd; background-color: white; }
    .dif-tag { font-size: 10px; font-weight: bold; color: #ff4b4b; text-align: right; }
    .dif-tag-medio { font-size: 10px; font-weight: bold; color: #ffa500; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if 'chat_iniciado' not in st.session_state:
    st.session_state.chat_iniciado = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN ---
modo = st.sidebar.radio("Menú", ["🏋️ Simulador", "📊 Admin"])

if modo == "🏋️ Simulador":
    if not st.session_state.chat_iniciado:
        st.write("### TU NOMBRE")
        nombre_v = st.text_input("ej. Cristóbal Altamirano")
        
        st.write("### TU CLIENTE ASIGNADO")
        cols = st.columns(2)
        for i, (nombre, info) in enumerate(CLIENTES.items()):
            with cols[i % 2]:
                with st.container(border=True):
                    tag_class = "dif-tag" if info['dif'] == "DIFÍCIL" else "dif-tag-medio"
                    st.markdown(f"<div class='{tag_class}'>{info['dif']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align: center;'>{info['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='text-align: center;'>{nombre}</h4>", unsafe_allow_html=True)
                    if st.button(f"Seleccionar", key=f"btn_{nombre}"):
                        if nombre_v:
                            st.session_state.vendedor = nombre_v
                            st.session_state.cliente = nombre
                            st.session_state.chat_iniciado = True
                            st.session_state.messages = [{"role": "user", "parts": ["Hola"]}]
                            saludo = model.generate_content(f"{CLIENTES[nombre]['prompt']} Saluda brevemente.")
                            st.session_state.messages = [{"role": "model", "parts": [saludo.text]}]
                            st.rerun()
                        else: st.warning("Ingresa tu nombre.")
    else:
        st.header(f"Cliente: {st.session_state.cliente}")
        for m in st.session_state.messages:
            role = "assistant" if m["role"] == "model" else "user"
            with st.chat_message(role): st.markdown(m["parts"][0])

        if prompt := st.chat_input("Escribe tu argumento..."):
            st.session_state.messages.append({"role": "user", "parts": [prompt]})
            chat = model.start_chat(history=st.session_state.messages[:-1])
            response = chat.send_message(prompt)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            st.rerun()

        if st.button("🏁 Finalizar y Evaluar"):
            eval_p = f"Evalúa esta venta médica bajo los 10 pilares de PTM Chile: {str(st.session_state.messages)}. Da nota 1.0 a 7.0."
            res = model.generate_content(eval_p)
            st.success("Evaluación Completada")
            st.markdown(res.text)
            
            # Registro para el Admin
            fila = {'Vendedor': st.session_state.vendedor, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': st.session_state.cliente, 'Nota': 6.0, 'Feedback': res.text}
            st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([fila])], ignore_index=True)
            st.balloons()
            if st.button("Nueva Práctica"):
                st.session_state.chat_iniciado = False
                st.rerun()
else:
    st.title("📊 Panel Admin")
    if st.text_input("Clave", type="password") == "PTM2026":
        st.dataframe(st.session_state.reportes, use_container_width=True)
