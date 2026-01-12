from langchain.tools import StructuredTool
from .application.service import AgendaService
from .domain.entities import Event
from pydantic import BaseModel, Field
from typing import Optional

class AddEventInput(BaseModel):
    event: str = Field(description="Nombre o descripción del evento")
    date: str = Field(description="Fecha en formato YYYY-MM-DD")
    time: str = Field(description="Hora en formato HH:MM")

class SearchEventInput(BaseModel):
    date: Optional[str] = Field(None, description="Fecha en formato YYYY-MM-DD para filtrar eventos")

class DeleteEventInput(BaseModel):
    event: str = Field(description="Nombre del evento a eliminar")
    date: Optional[str] = Field(None, description="Fecha en formato YYYY-MM-DD para ser más específico")

def create_agenda_tools(service: AgendaService):
    """
    Creates the LangChain tools for the agenda manager using StructuredTool.
    """
    
    def add_event_wrapper(event: str, date: str, time: str) -> str:
        return service.add_new_event(event, date, time)
    
    def list_events_wrapper(date: Optional[str] = None) -> str:
        # Si no se provee fecha, listamos todo
        if not date:
            events = service.list_all_events()
        else:
            events = service.list_events_by_date(date)
        
        if not events:
            return "No hay eventos para mostrar."
        
        res = "Eventos encontrados:\n"
        for e in events:
            res += f"- {e.name} el {e.date} a las {e.time}\n"
        return res

    def delete_event_wrapper(event: str, date: Optional[str] = None) -> str:
        return service.remove_event(event, date)
    
    return [
        StructuredTool.from_function(
            func=add_event_wrapper,
            name="AddAgendaEvent",
            description="Agrega un nuevo evento a la agenda con nombre, fecha y hora. Para eventos recurrentes o series, llama a esta herramienta varias veces (una por cada fecha).",
            args_schema=AddEventInput
        ),
        StructuredTool.from_function(
            func=list_events_wrapper,
            name="ListAgendaEvents",
            description="Consulta los eventos de la agenda. Puede filtrar por fecha.",
            args_schema=SearchEventInput
        ),
        StructuredTool.from_function(
            func=delete_event_wrapper,
            name="DeleteAgendaEvent",
            description="Elimina un evento de la agenda por su nombre y opcionalmente por fecha.",
            args_schema=DeleteEventInput
        )
    ]

