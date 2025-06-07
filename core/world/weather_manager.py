# core/world/weather_manager.py
import random
from core.enums import WeatherType

class WeatherManager:
    """Gestisce il meteo della simulazione."""
    def __init__(self):
        # Per ora, il meteo inizia semplicemente sereno.
        self.current_weather: WeatherType = WeatherType.SUNNY
        # In futuro, qui ci sarà la logica per le transizioni e le previsioni.
    
    def update_weather(self):
        """Metodo placeholder per cambiare il meteo dinamicamente."""
        # Esempio molto semplice: 1% di probabilità di cambiare meteo ad ogni chiamata
        # if random.random() < 0.01:
        #     self.current_weather = random.choice(list(WeatherType))
        pass

    def is_raining(self) -> bool:
        """Restituisce True se sta piovendo o c'è un temporale."""
        return self.current_weather in {WeatherType.RAINING, WeatherType.STORM}