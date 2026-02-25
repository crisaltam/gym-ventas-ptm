import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PTM CHILE ---
# Personajes con personalidades únicas
CLIENTES = {
    "Dr. Arriagada (Jefe Médico)": "Eres un médico jefe técnico, escéptico y con poco tiempo. Valoras la evidencia científica y el respaldo clínico.",
    "Marta (Enfermera Jefe)": "Te importa la seguridad del paciente y que el equipo no tenga más carga de trabajo. Buscas soluciones prácticas.",
    "Ricardo (Jefe de Compras)": "Eres un negociador frío. Solo te importa el presupuesto, plazos de entrega y comparativa de costos."
}

DIFICULTADES = {
    "Baja (Interesado)": "El cliente es amable y te da oportunidades para explicar.",
    "Media (Dudoso)": "El cliente pone 2 o 3 objeciones técnicas antes de avanzar.",
    "Alta (Hostil)": "El cliente es difícil, te interrumpe y cuestiona el valor de PTM."
}

PILARES_VENTA = [
    "1. Mentalidad de asesor", "2. Escucha activa", "3. Descubrimiento",
    "4. Dominio técnico", "5. Objeciones", "6. Control emocional",
    "7. Urgencia", "8. Enfoque en valor", "9. Lectura del cliente", "10. Cierre natural"
]

# --- INICIALIZACIÓN ---
st.set_page_config(page_title="PTM Sales Gym", layout="wide", page_icon="🚀")

# Simulación de base de datos (Persistente durante la sesión)
if 'db_reportes' not in st.session_state:
    st.session_state.db_reportes = pd.DataFrame(columns=['Vendedor', 'Fecha', 'Cliente', 'Dificultad', 'Nota', 'Feedback'])

# Memoria del chat interactivo
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NAVEGACIÓN LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3222/3222800.png", width=100)
st.sidebar.title("Menú Principal")
modo = st.sidebar.radio("Selecciona una opción:", ["🏋️ Simulador de Ventas", "📊 Panel Administrador"])

# --- MODO: SIMULADOR ---
if modo == "🏋️ Simulador de Ventas":
    st.title("🤝 Entrenamiento de Ventas PTM Chile")
    
    # 1. Ajustes iniciales
    with st.expander("⚙️ Configura tu entrenamiento", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            nombre_vendedor = st.text_input("Tu Nombre Completo")
        with col2:
            cliente_sel = st.selectbox("¿A quién le vendes hoy?", list(CLIENTES.keys()))
        with col3:
            nivel_reto = st.selectbox("Nivel de dificultad", list(DIFICULTADES.keys()))
        
        if st.button("🚀 Iniciar / Reiniciar Simulación"):
            st.session_state.messages = [{"role": "assistant", "content": f"Hola {nombre_vendedor}, soy {cliente_sel}. Tengo poco tiempo, cuéntame por qué me contactaste."}]
            st.rerun()

    st.divider()

    # 2. Área de Chat Dinámico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Escribe tu argumento de venta aquí..."):
        # Guardar mensaje del vendedor
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Respuesta automática del cliente (Simulando lógica de IA)
        with st.chat_message("assistant"):
            respuesta_bot = f"[{cliente_sel}]: Interesante, pero necesito que seas más específico con el valor para PTM. ¿Cómo manejas el tema del costo?"
            st.write(respuesta_bot)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_bot})

    # 3. Botón de Cierre y Evaluación
    if len(st.session_state.messages) > 2:
        if st.button("🏁 Finalizar y Evaluar"):
            st.subheader("📝 Evaluación de los 10 Pilares")
            
            # Aquí la IA procesaría el historial. Por ahora generamos resultado de gestión.
            nota_simulada = 5.8
            feedback_ia = "Buen manejo de la autoridad técnica, pero podrías mejorar el descubrimiento de dolores específicos del cliente."
            
            # Guardar en la base de datos para el Administrador
            nuevo_registro = {
                'Vendedor': nombre_vendedor, 
                'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'Cliente': cliente_sel, 
                'Dificultad': nivel_reto, 
                'Nota': nota_simulada, 
                'Feedback': feedback_ia
            }
            st.session_state.db_reportes = pd.concat([st.session_state.db_reportes, pd.DataFrame([nuevo_registro])], ignore_index=True)
            
            # Mostrar resultado al vendedor
            col_a, col_b = st.columns(2)
            col_a.metric("Tu Nota Final", f"{nota_simulada} / 7.0")
            col_b.write(f"**Feedback para {nombre_vendedor}:**\n{feedback_ia}")
            st.balloons()

# --- MODO: ADMINISTRADOR (PROTEGIDO) ---
else:
    st.title("📊 Panel de Reportabilidad - Cristóbal Altamirano")
    
    # Bloqueo de seguridad
    password = st.text_input("Introduce la clave de acceso para ver reportes", type="password")
    
    if password == "PTM2026": # Tú puedes cambiar esta clave
        st.success("Acceso autorizado.")
        
        if not st.session_state.db_reportes.empty:
            st.write("### Historial de Simulaciones")
            st.dataframe(st.session_state.db_reportes, use_container_width=True)
            
            st.divider()
            st.write("### Análisis de Desempeño por Vendedor")
            # Gráfico de barras interactivo
            st.bar_chart(data=st.session_state.db_reportes, x='Vendedor', y='Nota')
        else:
            st.info("Aún no hay datos. Los reportes aparecerán cuando los vendedores completen sus simulaciones.")
    
    elif password != "":
        st.error("Clave incorrecta. Solo el Administrador puede ver esta sección.")
