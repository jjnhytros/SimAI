# core/enums/weather_types.py
from enum import Enum, auto

class WeatherType(Enum):
    """Rappresenta le condizioni meteorologiche."""
    SUNNY = auto()
    CLOUDY = auto()
    RAINING = auto()
    STORM = auto()      # Temporale
    SNOWING = auto()
    FOGGY = auto()      # Nebbia