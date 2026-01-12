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

st.title("📅 Agenda Audifarma")
st.markdown("""
Bienvenido al gestor de agenda exclusivo para **Audifarma**.
Este asistente inteligente te permite gestionar tus eventos mediante lenguaje natural.
""")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
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

# --- Inicialización del Servicio (Core del Sistema) ---
# Usamos un adaptador para el repositorio
repository = ExcelRepositoryAdapter()
agent_adapter = None

if openai_api_key:
    # Creamos las herramientas pasándole el repo (puerto)
    tools = create_agenda_tools(repository)
    # Adaptador para el motor de IA
    agent_adapter = LangChainAgentAdapter(openai_api_key, tools, model_name=selected_model_id)

# El servicio de aplicación coordina todo
agenda_service = AgendaService(repository, agent=agent_adapter)

# --- Manejo del Chat ---
if "agenda_messages" not in st.session_state:
    st.session_state.agenda_messages = []
    
    # Mensaje de bienvenida inteligente
    try:
        events = agenda_service.list_all_events()
        if events:
            welcome = "¡Hola! Soy tu asistente de **Agenda Audifarma**. He verificado tu agenda y tienes eventos programados. ¿Qué te gustaría consultar?"
        else:
            welcome = "¡Hola! Soy tu asistente de **Agenda Audifarma**. Tu agenda está lista pero vacía. ¿Te gustaría programar tu primer evento?"
    except Exception:
        welcome = "¡Hola! Soy el asistente de Audifarma. ¿En qué puedo ayudarte hoy?"
    
    st.session_state.agenda_messages.append({"role": "assistant", "content": welcome})

for message in st.session_state.agenda_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Qué quieres hacer hoy con tu agenda?"):
    st.session_state.agenda_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not openai_api_key:
        st.info("Por favor, introduce tu OpenAI API Key en la barra lateral.")
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
