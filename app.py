import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# Reemplaza 'TU_API_KEY_AQUI' con tu llave real
genai.configure(api_key="TU_API_KEY_AQUI")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURACIÓN DE NEGOCIO PTM ---
CLIENTES = {
    "Dr. Arriagada (Jefe Médico)": {
        "desc": "Médico Senior. Valora datos técnicos y evidencia científica.",
        "prompt": "Eres el Dr. Arriagada, Jefe Médico escéptico. Exiges precisión técnica y no tienes tiempo para rodeos.",
        "img": "👨‍⚕️"
    },
    "Marta (Enfermera Jefe)": {
        "desc": "Enfocada en seguridad del paciente y flujo de trabajo del equipo.",
        "prompt": "Eres Marta, Enfermera Jefe. Te preocupa la curva de aprendizaje y la seguridad. Eres práctica y directa.",
        "img": "👩‍⚕️"
    },
    "Ricardo (Jefe de Compras)": {
        "desc": "Enfocado en presupuestos, logística y servicio post-venta.",
        "prompt": "Eres Ricardo, Jefe de Compras. Solo te importa el ROI, plazos y costos. Eres duro negociando.",
        "img": "💼"
    }
}

DIFICULTADES = {
    "Baja": "El cliente está abierto a escuchar y es cordial.",
    "Media": "El cliente pone 2 objeciones antes de interesarse.",
    "Alta": "El cliente es hostil, te interrumpe y cuestiona tu autoridad."
}

# --- INTERFAZ Y ESTILO ---
st.set_page_config(page_title="Gym de Ventas PTM", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #004a99; color: white; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS TEMPORAL ---
if 'reportes' not in st.session_state:
    st.session_state.reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Nota', 'Feedback'])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN ---
with st.sidebar:
    st.title("PTM Sales Gym")
    menu = st.radio("Sección:", ["🏋️ Simulador", "📊 Admin (Reportes)"])
    st.divider()
    if st.button("🗑️ Reiniciar Chat"):
        st.session_state.messages = []
        st.rerun()

# --- MODO SIMULADOR ---
if menu == "🏋️ Simulador":
    st.title("🤝 Entrenamiento Interactivo PTM")
    
    # Header de Configuración
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            nombre = st.text_input("Nombre del Vendedor", placeholder="Ej: Cristóbal Altamirano")
        with col2:
            c_sel = st.selectbox("Elegir Cliente", list(CLIENTES.keys()))
        with col3:
            d_sel = st.selectbox("Dificultad", list(DIFICULTADES.keys()))

    st.divider()

    # Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    if prompt := st.chat_input("Escribe tu argumento..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # RESPUESTA DE GEMINI COMO CLIENTE
        ctx = f"{CLIENTES[c_sel]['prompt']} Dificultad: {DIFICULTADES[d_sel]}. Responde corto (máx 2 frases). Historial: {st.session_state.messages}"
        response = model.generate_content(ctx)
        
        with st.chat_message("assistant"):
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    # BOTÓN DE EVALUACIÓN
    if len(st.session_state.messages) > 2:
        if st.button("🏁 Finalizar y Evaluar con 10 Pilares"):
            with st.spinner("IA analizando tus 10 pilares de venta..."):
                eval_prompt = f"Analiza este chat de venta: {st.session_state.messages}. Evalúa del 1.0 al 7.0 los 10 pilares: Mentalidad, Escucha, Descubrimiento, Técnico, Objeciones, Emocional, Urgencia, Valor, Lectura y Cierre. Entrega nota final y feedback corto."
                eval_res = model.generate_content(eval_prompt)
                
                # Extraer nota (simulado por regex o IA, aquí simplificamos a 6.0 para el ejemplo funcional rápido)
                nota_final = 6.0 
                
                new_row = {'Vendedor': nombre, 'Fecha': datetime.now().strftime("%d/%m %H:%M"), 'Cliente': c_sel, 'Nota': nota_final, 'Feedback': eval_res.text}
                st.session_state.reportes = pd.concat([st.session_state.reportes, pd.DataFrame([new_row])], ignore_index=True)
                
                st.balloons()
                st.success(f"¡Evaluación completada para {nombre}!")
                st.markdown(eval_res.text)

# --- MODO ADMIN ---
else:
    st.title("📊 Panel de Administrador")
    clave = st.text_input("Clave de acceso", type="password")
    
    if clave == "PTM2026":
        if not st.session_state.reportes.empty:
            st.write("### Reportabilidad de Vendedores")
            st.dataframe(st.session_state.reportes, use_container_width=True)
            
            st.subheader("Rendimiento del Equipo")
            st.bar_chart(st.session_state.reportes.set_index('Vendedor')['Nota'])
        else:
            st.info("Aún no hay registros de entrenamiento.")
