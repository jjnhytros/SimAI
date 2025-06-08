# core/enums/time_of_day.py
from enum import Enum, auto

class TimeOfDay(Enum):
    """Rappresenta le diverse fasi del giorno di 28 ore di Anthalys."""
    DAWN = auto()      # Alba
    MORNING = auto()   # Mattina
    AFTERNOON = auto() # Pomeriggio
    DUSK = auto()      # Tramonto
    EVENING = auto()   # Sera
    NIGHT = auto()     # Notte