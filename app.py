import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime

# --- CONFIGURACIÓN DE IA ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("🔑 Error: Configura 'OPENAI_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# --- DATOS DE CLIENTES (Según tu imagen) ---
CLIENTES = {
    "Jefe de Equipo Médico": {"dif": "DIFÍCIL", "desc": "Exige evidencia clínica y resultados", "icon": "👨‍⚕️", "prompt": "Eres un Jefe de Equipo Médico muy técnico."},
    "Enfermera Jefa UCI": {"dif": "MEDIO", "desc": "Prioriza seguridad y facilidad de uso", "icon": "👩‍⚕️", "prompt": "Eres una Enfermera Jefa preocupada por su equipo."},
    "Jefe de Compras": {"dif": "DIFÍCIL", "desc": "Precio, licitación y proveedores", "icon": "💼", "prompt": "Eres un Jefe de Compras enfocado en costos."},
    "Jefe de Bodega": {"dif": "MEDIO", "desc": "Logística, espacio y mantenimiento", "icon": "📦", "prompt": "Eres un Jefe de Bodega preocupado por el espacio."},
    "Jefe de Adquisiciones": {"dif": "DIFÍCIL", "desc": "Procesos, contratos y normativa", "icon": "📋", "prompt": "Eres un Jefe de Adquisiciones muy estricto."},
    "Dr. Jefe de Pabellón": {"dif": "DIFÍCIL", "desc": "Exigente, el equipo debe ser perfecto", "icon": "🏥", "prompt": "Eres un Cirujano Jefe que no acepta errores."},
    "Enfermera Jefa de Calidad": {"dif": "MEDIO", "desc": "Protocolos, acreditación y normativas", "icon": "✅", "prompt": "Eres una jefa enfocada en normativas ISO/Acreditación."}
}

st.set_page_config(page_title="PTM Sales Gym", layout="centered")

# --- ESTILOS CSS PARA LAS TARJETAS ---
st.markdown("""
    <style>
    .cliente-card {
        border: 1px solid #ddd;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        background-color: white;
        height: 220px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .dif-tag {
        font-size: 10px;
        font-weight: bold;
        color: #ff4b4b;
        text-align: right;
        margin-bottom: 5px;
    }
    .dif-tag-medio { color: #ffa500; }
    </style>
    """, unsafe_allow_html=True)

if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if 'chat_iniciado' not in st.session_state:
    st.session_state.chat_iniciado = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- LÓGICA DE NAVEGACIÓN ---
modo = st.sidebar.radio("Ir a:", ["Simulador", "Admin"])

if modo == "Simulador":
    if not st.session_state.chat_iniciado:
        st.write("### TU NOMBRE")
        nombre_vendedor = st.text_input("ej. Carlos Rodríguez", key="v_name")
        
        st.write("### TU CLIENTE ASIGNADO")
        
        # Crear la cuadrícula de tarjetas
        cols = st.columns(2)
        for i, (nombre, info) in enumerate(CLIENTES.items()):
            with cols[i % 2]:
                with st.container(border=True):
                    color_clase = "dif-tag" if info['dif'] == "DIFÍCIL" else "dif-tag-medio"
                    st.markdown(f"<div class='{color_clase}'>{info['dif']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h1 style='text-align: center; font-size: 40px;'>{info['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='text-align: center;'>{nombre}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 12px; color: gray;'>{info['desc']}</p>", unsafe_allow_html=True)
                    if st.button(f"Seleccionar {nombre}", key=f"btn_{nombre}"):
                        if nombre_vendedor:
                            st.session_state.vendedor = nombre_vendedor
                            st.session_state.cliente_actual = nombre
                            st.session_state.chat_iniciado = True
                            st.session_state.messages = [{"role": "assistant", "content": f"Hola, soy el {nombre}. Cuéntame, ¿qué me traes hoy?"}]
                            st.rerun()
                        else:
                            st.warning("Por favor, ingresa tu nombre primero.")

    else:
        # PANTALLA DE CHAT
        st.header(f"Hablando con: {st.session_state.cliente_actual}")
        
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if prompt := st.chat_input("Escribe tu respuesta..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": CLIENTES[st.session_state.cliente_actual]['prompt']}, *st.session_state.messages]
            )
            res_text = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            st.rerun()

        if st.button("Finalizar y Evaluar"):
            # Lógica de evaluación basada en tus 10 pilares
            eval_p = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "Evalúa esta venta médica del 1.0 al 7.0 según los 10 pilares de PTM Chile."}, {"role": "user", "content": str(st.session_state.messages)}]
            )
            st.success("Evaluación recibida")
            st.markdown(eval_p.choices[0].message.content)
            
            # Guardar en Admin
            nueva_fila = {'Vendedor': st.session_state.vendedor, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': st.session_state.cliente_actual, 'Nota': 6.0, 'Feedback': eval_p.choices[0].message.content}
            st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([nueva_fila])], ignore_index=True)
            
            if st.button("Nueva Simulación"):
                st.session_state.chat_iniciado = False
                st.rerun()

else:
    st.title("📊 Panel Admin")
    clave = st.text_input("Clave", type="password")
    if clave == "PTM2026":
        st.dataframe(st.session_state.reportes, use_container_width=True)
