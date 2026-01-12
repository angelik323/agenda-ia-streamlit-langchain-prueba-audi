from abc import ABC, abstractmethod
from typing import Any

class AIAgentPort(ABC):
    """Puerto de salida para el motor de Inteligencia Artificial."""
    
    @abstractmethod
    def get_response(self, user_input: str, chat_history: Any) -> str:
        pass
