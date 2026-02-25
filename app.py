import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA ---
try:
    # Usamos la configuración más simple posible
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Nombre de modelo limpio sin prefijos 'models/' ni 'v1beta'
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- DATOS DE CLIENTES PTM CHILE ---
CLIENTES = {
    "Jefe de Equipo Médico": {"dif": "DIFÍCIL", "icon": "👨‍⚕️", "desc": "Exige evidencia clínica y resultados", "prompt": "Eres un Jefe de Equipo Médico técnico."},
    "Enfermera Jefa UCI": {"dif": "MEDIO", "icon": "👩‍⚕️", "desc": "Prioriza seguridad y facilidad de uso", "prompt": "Eres una Enfermera Jefa preocupada por su equipo."},
    "Jefe de Compras": {"dif": "DIFÍCIL", "icon": "💼", "desc": "Precio, licitación y proveedores", "prompt": "Eres un Jefe de Compras enfocado en el ahorro."},
    "Jefe de Bodega": {"dif": "MEDIO", "icon": "📦", "desc": "Logística, espacio y mantenimiento", "prompt": "Eres un Jefe de Bodega preocupado por el orden."},
    "Jefe de Adquisiciones": {"dif": "DIFÍCIL", "icon": "📋", "desc": "Procesos, contratos y normativa", "prompt": "Eres un Jefe de Adquisiciones muy estricto."},
    "Dr. Jefe de Pabellón": {"dif": "DIFÍCIL", "icon": "🏥", "desc": "Exigente, el equipo debe ser perfecto", "prompt": "Eres un Cirujano Jefe con poco tiempo."},
    "Enfermera Jefa de Calidad": {"dif": "MEDIO", "icon": "✅", "desc": "Protocolos, acreditación y normativas", "prompt": "Eres jefa de calidad enfocada en acreditación."}
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
    nombre_v = st.text_input("ej. Cristóbal Altamirano", key="nombre_v", value="Cristóbal Altamirano") #
    
    st.write("### TU CLIENTE ASIGNADO")
    cols = st.columns(2)
    for i, (nombre, info) in enumerate(CLIENTES.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"<h1 style='text-align: center;'>{info['icon']}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center;'>{nombre}</h4>", unsafe_allow_html=True)
                if st.button(f"Seleccionar", key=f"btn_{nombre}"):
                    st.session_state.vendedor = nombre_v
                    st.session_state.cliente = nombre
                    st.session_state.chat_iniciado = True
                    # Generar saludo inicial sin start_chat para evitar el 404
                    try:
                        resp = model.generate_content(f"{info['prompt']} Saluda brevemente al vendedor.")
                        st.session_state.messages = [{"role": "model", "parts": [resp.text]}]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al iniciar: {e}")
else:
    st.header(f"Simulación: {st.session_state.cliente}")
    for m in st.session_state.messages:
        rol = "assistant" if m["role"] == "model" else "user"
        with st.chat_message(rol): st.markdown(m["parts"][0])

    if p := st.chat_input("Escribe tu argumento..."):
        st.session_state.messages.append({"role": "user", "parts": [p]})
        try:
            # Enviamos todo el historial como un solo texto para máxima estabilidad
            historial_texto = "\n".join([f"{msg['role']}: {msg['parts'][0]}" for msg in st.session_state.messages])
            full_prompt = f"{CLIENTES[st.session_state.cliente]['prompt']}\nHistorial:\n{historial_texto}\nCliente:"
            response = model.generate_content(full_prompt)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            st.rerun()
        except Exception as e:
            st.error(f"Error en la IA: {e}")

    if st.button("🏁 Finalizar y Evaluar"):
        eval_p = f"Evalúa esta venta médica bajo los 10 pilares de éxito: {str(st.session_state.messages)}. Nota 1.0 a 7.0."
        res = model.generate_content(eval_p)
        st.success("Evaluación Completada")
        st.markdown(res.text)
        
        # Guardar registro para tu panel de Admin
        fila = {'Vendedor': st.session_state.vendedor, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': st.session_state.cliente, 'Nota': 6.0, 'Feedback': res.text}
        st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([fila])], ignore_index=True)
        st.balloons()
