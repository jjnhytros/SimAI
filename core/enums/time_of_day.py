# core/enums/time_of_day.py
from enum import Enum

class TimeOfDay(Enum):
    DAWN = 4      # Alba
    MORNING = 6   # Mattina
    AFTERNOON = 12  # Pomeriggio
    DUSK = 19     # Tramonto
    EVENING = 22  # Sera
    NIGHT = 26    # Notte
    
    @property
    def start_hour(self):
        """Restituisce l'ora di inizio della fase in formato numerico"""
        return self.value
    
    @property
    def display_name_it(self):
        """Restituisce il nome visualizzabile della fase"""
        names = {
            TimeOfDay.DAWN: "Alba",
            TimeOfDay.MORNING: "Mattina",
            TimeOfDay.AFTERNOON: "Pomeriggio",
            TimeOfDay.DUSK: "Tramonto",
            TimeOfDay.EVENING: "Sera",
            TimeOfDay.NIGHT: "Notte",
        }
        return names[self]
    
    @classmethod
    def get_current_phase(cls, current_hour: float):
        """
        Determina la fase corrente basata sull'ora.
        Gestisce correttamente il ciclo tra notte (26:00) e alba (4:00).
        """
        # Gestione caso speciale notte (26:00-28:00 e 0:00-4:00)
        if current_hour >= cls.NIGHT.start_hour or current_hour < cls.DAWN.start_hour:
            return cls.NIGHT
        
        # Fasi ordinate cronologicamente
        phases = [
            cls.DAWN,
            cls.MORNING,
            cls.AFTERNOON,
            cls.DUSK,
            cls.EVENING
        ]
        
        # Trova l'ultima fase iniziata prima dell'ora corrente
        current_phase = cls.DAWN  # Default
        for phase in phases:
            if current_hour >= phase.start_hour:
                current_phase = phase
            else:
                break
                
        return current_phase

    @classmethod
    def is_sleeping_time(cls, current_hour: float) -> bool:
        """Determina se è tipicamente ora di dormire"""
        current_phase = cls.get_current_phase(current_hour)
        return current_phase in [cls.NIGHT, cls.DAWN]
