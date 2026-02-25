import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- SEGURIDAD: CONEXIÓN A GEMINI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("🔑 Error: Configura 'GEMINI_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# --- DATOS DE CLIENTES PTM ---
CLIENTES = {
    "Jefe de Equipo Médico": {"dif": "DIFÍCIL", "icon": "👨‍⚕️", "desc": "Exige evidencia clínica y resultados", "prompt": "Eres un Jefe de Equipo Médico en Chile, muy técnico y escéptico."},
    "Enfermera Jefa UCI": {"dif": "MEDIO", "icon": "👩‍⚕️", "desc": "Prioriza seguridad y facilidad de uso", "prompt": "Eres una Enfermera Jefa preocupada por la carga de trabajo de su equipo."},
    "Jefe de Compras": {"dif": "DIFÍCIL", "icon": "💼", "desc": "Precio, licitación y proveedores", "prompt": "Eres un Jefe de Compras que solo busca ahorrar presupuesto."},
    "Jefe de Bodega": {"dif": "MEDIO", "icon": "📦", "desc": "Logística, espacio y mantenimiento", "prompt": "Eres un Jefe de Bodega preocupado por el stock y el espacio."},
    "Jefe de Adquisiciones": {"dif": "DIFÍCIL", "icon": "📋", "desc": "Procesos, contratos y normativa", "prompt": "Eres un Jefe de Adquisiciones muy estricto con los papeles."},
    "Dr. Jefe de Pabellón": {"dif": "DIFÍCIL", "icon": "🏥", "desc": "Exigente, el equipo debe ser perfecto", "prompt": "Eres un Cirujano Jefe que no tiene tiempo para rodeos."},
    "Enfermera Jefa de Calidad": {"dif": "MEDIO", "icon": "✅", "desc": "Protocolos, acreditación y normativas", "prompt": "Eres una jefa enfocada en normativas y acreditación de salud."}
}

st.set_page_config(page_title="PTM Sales Gym", layout="centered")

# Estilos CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; border: 1px solid #ddd; background-color: white; color: black; }
    .dif-tag { font-size: 10px; font-weight: bold; color: #ff4b4b; text-align: right; }
    .dif-tag-medio { color: #ffa500; font-size: 10px; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if 'chat_iniciado' not in st.session_state:
    st.session_state.chat_iniciado = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN ---
modo = st.sidebar.radio("Menú", ["Simulador", "Admin"])

if modo == "Simulador":
    if not st.session_state.chat_iniciado:
        st.write("### TU NOMBRE")
        nombre_v = st.text_input("ej. Cristóbal Altamirano")
        
        st.write("### TU CLIENTE ASIGNADO")
        cols = st.columns(2)
        for i, (nombre, info) in enumerate(CLIENTES.items()):
            with cols[i % 2]:
                with st.container(border=True):
                    tag = "dif-tag" if info['dif'] == "DIFÍCIL" else "dif-tag-medio"
                    st.markdown(f"<div class='{tag}'>{info['dif']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align: center;'>{info['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='text-align: center;'>{nombre}</h4>", unsafe_allow_html=True)
                    if st.button(f"Seleccionar", key=nombre):
                        if nombre_v:
                            st.session_state.chat_iniciado = True
                            st.session_state.vendedor = nombre_v
                            st.session_state.cliente = nombre
                            st.session_state.messages = [{"role": "model", "parts": [f"Hola, soy el {nombre}. Cuéntame qué me traes hoy."]}]
                            st.rerun()
                        else: st.warning("Escribe tu nombre.")
    else:
        st.header(f"Cliente: {st.session_state.cliente}")
        for m in st.session_state.messages:
            role = "assistant" if m["role"] == "model" else "user"
            with st.chat_message(role): st.markdown(m["parts"][0])

        if prompt := st.chat_input("Escribe tu respuesta..."):
            st.session_state.messages.append({"role": "user", "parts": [prompt]})
            chat = model.start_chat(history=st.session_state.messages[:-1])
            response = chat.send_message(prompt)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            st.rerun()

        if st.button("Finalizar y Evaluar"):
            eval_prompt = f"Evalúa esta venta médica según los 10 pilares de PTM Chile (Mentalidad, Escucha, Valor, etc). Da nota 1 a 7: {str(st.session_state.messages)}"
            res = model.generate_content(eval_prompt)
            st.success("Evaluación Completada")
            st.markdown(res.text)
            
            # Guardar en reporte
            nueva_fila = {'Vendedor': st.session_state.vendedor, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': st.session_state.cliente, 'Nota': 6.0, 'Feedback': res.text}
            st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.balloons()
            if st.button("Nueva Práctica"):
                st.session_state.chat_iniciado = False
                st.rerun()

else:
    st.title("📊 Panel Admin")
    clave = st.text_input("Clave", type="password")
    if clave == "PTM2026":
        st.dataframe(st.session_state.reportes)
