import streamlit as st
import pandas as pd
import os
import logging
from datetime import datetime

from agenda_module.infrastructure.adapters.excel_repo import ExcelRepositoryAdapter
from agenda_module.infrastructure.adapters.ai_agent_adapter import LangChainAgentAdapter
from agenda_module.application.service import AgendaService
from agenda_module.tools import create_agenda_tools
from agenda_module.config import AGENDA_FILENAME, LOG_FILENAME, MODEL_OPTIONS

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Agenda Audifarma", page_icon="📅")

st.image("agenda_module/assets/logo.svg", width=200)
st.title("📅 Agenda Audifarma")
st.markdown("""
Bienvenido al gestor de agenda exclusivo para **Audifarma**.
Este asistente inteligente te permite gestionar tus eventos mediante lenguaje natural.
""")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    
    # Intento obtener la API Key de los secretos locales (secrets.toml)
    try:
        openai_api_key = st.secrets["secrets"]["OPENAI_API_KEY"]
        if openai_api_key == "TU_API_KEY_AQUI":
            st.warning("⚠️ Debes configurar tu OpenAI API Key en `.streamlit/secrets.toml`")
            openai_api_key = None
    except Exception:
        openai_api_key = None
        st.error("⚠️ No se encontró la configuración de secretos en `.streamlit/secrets.toml`")
    
    if st.button("Limpiar historial de chat"):
        st.session_state.agenda_messages = []
        st.rerun()

    st.divider()
    st.subheader("Modelo de IA")
    selected_model_display = st.selectbox(
        "Elige un modelo:",
        options=list(MODEL_OPTIONS.keys()),
        index=len(MODEL_OPTIONS) - 1
    )
    selected_model_id = MODEL_OPTIONS[selected_model_display]

    st.divider()
    st.subheader("Vista previa de la Agenda")
    
    # Inyección de dependencia manual para la vista previa
    repo_view = ExcelRepositoryAdapter()
    if os.path.exists(repo_view.file_path):
        try:
            df = pd.read_excel(repo_view.file_path)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error al leer la agenda: {e}")
    else:
        st.info("Aún no hay eventos programados.")
        
    st.divider()
    st.subheader("Reglas de Agenda")
    st.info("""
    - **Límite**: Máximo 1 año a futuro.
    - **Formato**: AAAA-MM-DD o lenguaje natural.
    - **Recurrencia**: El asistente puede agendar series (ej: cada lunes).
    - **Uso**: El asistente interpreta fechas naturales.
    """)

# --- Inicialización del Sistema (Inyección de Dependencias) ---
repository = ExcelRepositoryAdapter()
agent_adapter = None

# El servicio de aplicación coordina todo
agenda_service = AgendaService(repository, agent=None)

if openai_api_key:
    # Creamos las herramientas pasándole el servicio (Orquestador con lógica de negocio)
    tools = create_agenda_tools(agenda_service)
    # Adaptador para el motor de IA
    agent_adapter = LangChainAgentAdapter(openai_api_key, tools, model_name=selected_model_id)
    # Actualizamos el agente en el servicio
    agenda_service.agent = agent_adapter

# --- Manejo del Chat ---
if "agenda_messages" not in st.session_state:
    st.session_state.agenda_messages = []
    
    # Mensaje de bienvenida inteligente
    rules_reminder = "\n\n*Recuerda que agendamos con formato **AAAA-MM-DD o lenguaje natural**, soportamos **eventos recurrentes** y máximo **1 año** al futuro.*"
    try:
        events = agenda_service.list_all_events()
        if events:
            welcome = "¡Hola! Soy tu asistente de **Agenda Audifarma**. He verificado tu agenda y tienes eventos programados. ¿Qué te gustaría consultar?" + rules_reminder
        else:
            welcome = "¡Hola! Soy tu asistente de **Agenda Audifarma**. Tu agenda está lista pero vacía. ¿Te gustaría programar tu primer evento?" + rules_reminder
    except Exception:
        welcome = "¡Hola! Soy el asistente de Audifarma. ¿En qué puedo ayudarte hoy?" + rules_reminder
    
    st.session_state.agenda_messages.append({"role": "assistant", "content": welcome})

for message in st.session_state.agenda_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Qué quieres hacer hoy con tu agenda?"):
    st.session_state.agenda_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not openai_api_key:
        st.info("Por favor, configura tu OpenAI API Key en el archivo de propiedades `.streamlit/secrets.toml`.")
        st.stop()

    try:
        with st.chat_message("assistant"):
            # Delegamos la respuesta a la IA a través del servicio de aplicación
            response = agenda_service.ask_ai(prompt)
            st.markdown(response)
            st.session_state.agenda_messages.append({"role": "assistant", "content": response})
            st.rerun() 
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        st.error("⚠️ **Lo siento, ha ocurrido un problema técnico.** Revisa los logs para más detalle.")
