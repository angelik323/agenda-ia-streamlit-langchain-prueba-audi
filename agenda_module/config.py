import os

# Nombre del archivo de la agenda
# En la rama 'version-audi' podrías cambiar esto a 'agenda_audi.xlsx'
AGENDA_FILENAME = "agenda_audi.xlsx"

# Ruta al archivo del prompt (relativa a la raíz del módulo)
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.md")

# Ruta al archivo de logs (absoluta a la raíz del proyecto)
LOG_FILENAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.log")

# Opciones de modelos disponibles
MODEL_OPTIONS = {
    "gpt-5.2 — Alto rendimiento (texto & razonamiento)": "gpt-5.2",
    "gpt-5.1 — Razonamiento configurable": "gpt-5.1",
    "gpt-5 — Versión principal para producción": "gpt-5",
    "gpt-5-mini — Económico y rápido": "gpt-5-mini",
    "gpt-5-nano — Ultra-económico para respuestas simples": "gpt-5-nano",
    "gpt-3.5-turbo — Modelo estándar compatible": "gpt-3.5-turbo"
}
