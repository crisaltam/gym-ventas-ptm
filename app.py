import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (GEMINI 1.5 FLASH) ---
try:
    # Usamos la ruta completa para evitar el error NotFound
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception:
    st.error("🔑 Error: Configura 'GEMINI_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# --- DATOS DE CLIENTES PTM CHILE ---
CLIENTES = {
    "Jefe de Equipo Médico": {"dif": "DIFÍCIL", "icon": "👨‍⚕️", "desc": "Exige evidencia clínica y resultados", "prompt": "Eres un Jefe de Equipo Médico en Chile. Eres escéptico y muy técnico."},
    "Enfermera Jefa UCI": {"dif": "MEDIO", "icon": "👩‍⚕️", "desc": "Prioriza seguridad y facilidad de uso", "prompt": "Eres una Enfermera Jefa preocupada por el bienestar de su equipo y pacientes."},
    "Jefe de Compras": {"dif": "DIFÍCIL", "icon": "💼", "desc": "Precio, licitación y proveedores", "prompt": "Eres un Jefe de Compras que busca el menor precio y mejores plazos."},
    "Jefe de Bodega": {"dif": "MEDIO", "icon": "📦", "desc": "Logística, espacio y mantenimiento", "prompt": "Eres un Jefe de Bodega preocupado por el orden y el stock."},
    "Jefe de Adquisiciones": {"dif": "DIFÍCIL", "icon": "📋", "desc": "Procesos, contratos y normativa", "prompt": "Eres un Jefe de Adquisiciones muy estricto con los contratos."},
    "Dr. Jefe de Pabellón": {"dif": "DIFÍCIL", "icon": "🏥", "desc": "Exigente, el equipo debe ser perfecto", "prompt": "Eres un Cirujano Jefe. No tienes tiempo para errores."},
    "Enfermera Jefa de Calidad": {"dif": "MEDIO", "icon": "✅", "desc": "Protocolos, acreditación y normativas", "prompt": "Eres jefa de calidad, te importa cumplir todas las normas ISO."}
}

st.set_page_config(page_title="PTM Sales Gym", layout="centered")

# Estilos CSS para las Tarjetas
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; border: 1px solid #ddd; background-color: white; height: 3em; }
    .dif-tag { font-size: 10px; font-weight: bold; color: #ff4b4b; text-align: right; margin-bottom: 5px; }
    .dif-tag-medio { font-size: 10px; font-weight: bold; color: #ffa500; text-align: right; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Inicializar estados de la sesión
if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if 'chat_iniciado' not in st.session_state:
    st.session_state.chat_iniciado = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN ---
modo = st.sidebar.radio("Menú Principal", ["🏋️ Simulador", "📊 Panel Admin"])

if modo == "🏋️ Simulador":
    if not st.session_state.chat_iniciado:
        st.write("### TU NOMBRE")
        nombre_v = st.text_input("ej. Cristóbal Altamirano", key="input_nombre")
        
        st.write("### TU CLIENTE ASIGNADO")
        cols = st.columns(2)
        for i, (nombre, info) in enumerate(CLIENTES.items()):
            with cols[i % 2]:
                with st.container(border=True):
                    tag_class = "dif-tag" if info['dif'] == "DIFÍCIL" else "dif-tag-medio"
                    st.markdown(f"<div class='{tag_class}'>{info['dif']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align: center;'>{info['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='text-align: center;'>{nombre}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 12px; color: gray;'>{info['desc']}</p>", unsafe_allow_html=True)
                    if st.button(f"Seleccionar", key=f"sel_{nombre}"):
                        if nombre_v:
                            st.session_state.vendedor = nombre_v
                            st.session_state.cliente = nombre
                            st.session_state.chat_iniciado = True
                            st.session_state.messages = [{"role": "user", "parts": ["Hola"]}]
                            # Generar saludo inicial de la IA
                            saludo = model.generate_content(f"{CLIENTES[nombre]['prompt']} Saluda al vendedor brevemente.")
                            st.session_state.messages = [{"role": "model", "parts": [saludo.text]}]
                            st.rerun()
                        else: st.warning("Por favor, ingresa tu nombre.")
    else:
        st.header(f"Simulación con: {st.session_state.cliente}")
        
        # Mostrar historial de chat
        for m in st.session_state.messages:
            role = "assistant" if m["role"] == "model" else "user"
            with st.chat_message(role): st.markdown(m["parts"][0])

        if prompt := st.chat_input("Escribe tu argumento de venta..."):
            st.session_state.messages.append({"role": "user", "parts": [prompt]})
            with st.chat_message("user"): st.markdown(prompt)
            
            # Respuesta del Cliente (IA)
            ctx = f"{CLIENTES[st.session_state.cliente]['prompt']} Responde corto (máx 2 frases)."
            chat = model.start_chat(history=st.session_state.messages[:-1])
            response = chat.send_message(prompt)
            
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            with st.chat_message("assistant"): st.markdown(response.text)

        if st.button("🏁 Finalizar y Evaluar"):
            with st.spinner("Analizando tu desempeño..."):
                eval_p = f"Evalúa esta venta según los 10 pilares de éxito de PTM Chile: {str(st.session_state.messages)}. Da una nota del 1.0 al 7.0 y feedback corto."
                res_eval = model.generate_content(eval_p)
                st.success("Evaluación Completada")
                st.markdown(res_eval.text)
                
                # Guardar en reporte de Administrador
                fila = {'Vendedor': st.session_state.vendedor, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': st.session_state.cliente, 'Nota': 6.0, 'Feedback': res_eval.text}
                st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([fila])], ignore_index=True)
                st.balloons()
                if st.button("Volver al Inicio"):
                    st.session_state.chat_iniciado = False
                    st.rerun()

else:
    st.title("📊 Reportabilidad - Cristóbal Altamirano")
    clave = st.text_input("Clave de Acceso", type="password")
    if clave == "PTM2026":
        st.dataframe(st.session_state.reportes, use_container_width=True)
