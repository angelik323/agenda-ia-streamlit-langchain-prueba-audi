import pandas as pd
import os
import logging
from typing import List, Optional
from ...domain.entities import Event
from ...domain.ports.repository import AgendaRepository
from ...config import AGENDA_FILENAME

logger = logging.getLogger(__name__)

class ExcelRepositoryAdapter(AgendaRepository):
    """Adaptador de infraestructura que implementa persistencia en Excel."""
    
    COLUMNS = ["Evento", "Fecha", "Hora"]
    
    def __init__(self, file_path: str = None):
        if file_path is None:
            # Base path relative to the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.file_path = os.path.join(base_dir, AGENDA_FILENAME)
        else:
            self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=self.COLUMNS)
            df.to_excel(self.file_path, index=False)
            logger.info(f"Creado nuevo archivo de agenda en {self.file_path}")

    def save(self, event: Event) -> str:
        try:
            df = pd.read_excel(self.file_path)
            new_row = {"Evento": event.name, "Fecha": event.date, "Hora": event.time}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(self.file_path, index=False)
            return f"¡Listo! He agendado: '{event.name}' para el {event.date} a las {event.time}."
        except Exception as e:
            logger.error(f"Error al guardar evento: {str(e)}")
            return f"Error al guardar en Excel: {str(e)}"

    def find_all(self) -> List[Event]:
        try:
            df = pd.read_excel(self.file_path)
            events = []
            for _, row in df.iterrows():
                events.append(Event(name=row["Evento"], date=str(row["Fecha"]), time=str(row["Hora"])))
            return events
        except Exception as e:
            logger.error(f"Error al leer agenda: {str(e)}")
            return []

    def find_by_date(self, date: str) -> List[Event]:
        try:
            df = pd.read_excel(self.file_path)
            if df.empty:
                return []
            
            # Normalizar fechas para comparación
            df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.strftime("%Y-%m-%d")
            filtered_df = df[df["Fecha"] == date]
            
            events = []
            for _, row in filtered_df.iterrows():
                events.append(Event(name=row["Evento"], date=str(row["Fecha"]), time=str(row["Hora"])))
            return events
        except Exception as e:
            logger.error(f"Error al filtrar por fecha: {str(e)}")
            return []

    def delete(self, event: str, date: Optional[str] = None) -> str:
        try:
            df = pd.read_excel(self.file_path)
            if df.empty:
                return "La agenda está vacía."
            
            initial_count = len(df)
            if date:
                df = df[~((df["Evento"] == event) & (df["Fecha"].astype(str) == date))]
            else:
                df = df[df["Evento"] != event]
            
            if len(df) == initial_count:
                return f"No se encontró el evento '{event}'"
            
            df.to_excel(self.file_path, index=False)
            return f"Evento(s) '{event}' eliminado(s) con éxito."
        except Exception as e:
            logger.error(f"Error al eliminar: {str(e)}")
            return f"Error al eliminar en Excel: {str(e)}"
