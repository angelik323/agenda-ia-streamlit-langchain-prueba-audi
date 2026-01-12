from dataclasses import dataclass
from datetime import date, time

@dataclass
class Event:
    """Entidad pura de dominio que representa un evento de agenda."""
    name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
