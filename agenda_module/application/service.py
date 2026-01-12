from typing import List, Any
from ..domain.entities import Event
from ..domain.ports.repository import AgendaRepository
from ..domain.ports.agent_port import AIAgentPort

class AgendaService:
    """Servicio de aplicación que orquesta los casos de uso de la agenda."""
    
    def __init__(self, repository: AgendaRepository, agent: AIAgentPort = None):
        self.repository = repository
        self.agent = agent

    def add_new_event(self, event: str, date: str, time: str) -> str:
        from datetime import datetime, timedelta
        
        try:
            event_date = datetime.strptime(date, "%Y-%m-%d").date()
            today = datetime.now().date()
            limit_date = today + timedelta(days=365)
            
            if event_date > limit_date:
                return f"⚠️ No puedes agendar eventos a más de un año en el futuro (Límite: {limit_date})."
                
            new_event = Event(name=event, date=date, time=time)
            return self.repository.save(new_event)
        except ValueError:
            return "⚠️ El formato de fecha debe ser YYYY-MM-DD."

    def list_all_events(self) -> List[Event]:
        return self.repository.find_all()

    def list_events_by_date(self, date: str) -> List[Event]:
        return self.repository.find_by_date(date)

    def remove_event(self, event: str, date: str = None) -> str:
        return self.repository.delete(event, date)

    def ask_ai(self, user_input: str) -> str:
        if not self.agent:
            return "El motor de IA no está configurado."
        return self.agent.get_response(user_input)
