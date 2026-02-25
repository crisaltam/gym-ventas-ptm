import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (VERSIÓN ESTABLE 2026) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Cambiamos la forma de declarar el modelo para evitar el error 404 de v1beta
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"🔑 Error en los Secrets de Streamlit: {e}")
    st.stop()

# --- DATOS DE CLIENTES PTM CHILE ---
CLIENTES = {
    "Jefe de Equipo Médico": {"dif": "DIFÍCIL", "icon": "👨‍⚕️", "desc": "Exige evidencia clínica y resultados", "prompt": "Eres un Jefe de Equipo Médico técnico y directo en Chile."},
    "Enfermera Jefa UCI": {"dif": "MEDIO", "icon": "👩‍⚕️", "desc": "Prioriza seguridad y facilidad de uso", "prompt": "Eres una Enfermera Jefa preocupada por el bienestar de su equipo."},
    "Jefe de Compras": {"dif": "DIFÍCIL", "icon": "💼", "desc": "Precio, licitación y proveedores", "prompt": "Eres un Jefe de Compras enfocado 100% en el presupuesto."},
    "Jefe de Bodega": {"dif": "MEDIO", "icon": "📦", "desc": "Logística, espacio y mantenimiento", "prompt": "Eres un Jefe de Bodega preocupado por el orden y stock."},
    "Jefe de Adquisiciones": {"dif": "DIFÍCIL", "icon": "📋", "desc": "Procesos, contratos y normativa", "prompt": "Eres un Jefe de Adquisiciones muy estricto con las normas."},
    "Dr. Jefe de Pabellón": {"dif": "DIFÍCIL", "icon": "🏥", "desc": "Exigente, el equipo debe ser perfecto", "prompt": "Eres un Cirujano Jefe con muy poco tiempo disponible."},
    "Enfermera Jefa de Calidad": {"dif": "MEDIO", "icon": "✅", "desc": "Protocolos, acreditación y normativas", "prompt": "Eres jefa de calidad enfocada en acreditaciones de salud."}
}

st.set_page_config(page_title="PTM Sales Gym", layout="centered")

# Estilos CSS para las Tarjetas (Fieles a tu imagen)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; border: 1px solid #ddd; background-color: white; color: black; height: 3.5em; }
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
modo = st.sidebar.radio("Menú Principal", ["🏋️ Simulador", "📊 Admin"])

if modo == "🏋️ Simulador":
    if not st.session_state.chat_iniciado:
        st.write("### TU NOMBRE")
        # Por defecto Cristóbal Altamirano
        nombre_v = st.text_input("ej. Cristóbal Altamirano", key="nombre_v_input", value="Cristóbal Altamirano")
        
        st.write("### TU CLIENTE ASIGNADO")
        cols = st.columns(2)
        for i, (nombre, info) in enumerate(CLIENTES.items()):
            with cols[i % 2]:
                with st.container(border=True):
                    clase_tag = "dif-tag" if info['dif'] == "DIFÍCIL" else "dif-tag-medio"
                    st.markdown(f"<div class='{clase_tag}'>{info['dif']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align: center;'>{info['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='text-align: center;'>{nombre}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 11px; color: gray;'>{info['desc']}</p>", unsafe_allow_html=True)
                    if st.button(f"Seleccionar {nombre}", key=f"btn_{nombre}"):
                        if nombre_v:
                            st.session_state.vendedor = nombre_v
                            st.session_state.cliente = nombre
                            st.session_state.chat_iniciado = True
                            
                            # Generación de saludo inicial sin usar v1beta explícito
                            try:
                                saludo = model.generate_content(f"{info['prompt']} Saluda al vendedor de forma muy breve.")
                                st.session_state.messages = [{"role": "model", "parts": [saludo.text]}]
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al iniciar el modelo: {e}. Intenta refrescar la página.")
                        else:
                            st.warning("Por favor, ingresa tu nombre antes de elegir un cliente.")
    else:
        # PANTALLA DE CHAT INTERACTIVO
        st.header(f"Simulación con: {st.session_state.cliente}")
        for m in st.session_state.messages:
            rol = "assistant" if m["role"] == "model" else "user"
            with st.chat_message(rol):
                st.markdown(m["parts"][0])

        if p := st.chat_input("Escribe tu argumento de venta..."):
            st.session_state.messages.append({"role": "user", "parts": [p]})
            try:
                # Usamos el historial acumulado para dar continuidad a la conversación
                chat_session = model.start_chat(history=st.session_state.messages[:-1])
                response = chat_session.send_message(p)
                st.session_state.messages.append({"role": "model", "parts": [response.text]})
                st.rerun()
            except Exception as e:
                st.error(f"Error en la respuesta de la IA: {e}")

        if st.button("🏁 Finalizar y Evaluar"):
            try:
                eval_p = f"Actúa como un experto en ventas médicas. Evalúa este chat según los 10 pilares de venta de PTM Chile: {str(st.session_state.messages)}. Da una nota del 1.0 al 7.0."
                res_eval = model.generate_content(eval_p)
                st.success("Evaluación Generada con Éxito")
                st.markdown(res_eval.text)
                
                # Registro para el panel de Admin de Cristóbal
                fila = {'Vendedor': st.session_state.vendedor, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': st.session_state.cliente, 'Nota': 6.0, 'Feedback': res_eval.text}
                st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([fila])], ignore_index=True)
                st.balloons()
            except Exception as e:
                st.error(f"Error al generar la evaluación: {e}")

else:
    st.title("📊 Panel Administrativo - PTM Chile")
    # Clave de seguridad establecida anteriormente
    if st.text_input("Clave de Acceso", type="password") == "PTM2026":
        st.dataframe(st.session_state.reportes, use_container_width=True)
