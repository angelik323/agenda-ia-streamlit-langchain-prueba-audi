from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities import Event

class AgendaRepository(ABC):
    """Puerto de salida para la persistencia de la agenda."""
    
    @abstractmethod
    def save(self, event: Event) -> str:
        pass

    @abstractmethod
    def find_all(self) -> List[Event]:
        pass

    @abstractmethod
    def find_by_date(self, date: str) -> List[Event]:
        pass

    @abstractmethod
    def delete(self, event: str, date: Optional[str] = None) -> str:
        pass
