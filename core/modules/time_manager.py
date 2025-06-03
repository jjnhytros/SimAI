# core/modules/time_manager.py

# Importiamo ogni classe direttamente dal suo file specifico all'interno del package
from core.world.ATHDateTime.ATHDateTime import ATHDateTime
from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval
from core.world.ATHDateTime.ATHDateTimeZone import ATHDateTimeZone
from core.config import time_config
from typing import Dict, Union

class TimeManager:
    """
    Gestisce il tempo universale all'interno della simulazione.
    Utilizza la libreria ATHDateTime per una gestione precisa di data e ora
    nel mondo di gioco.
    """
    def __init__(self):
        """
        Inizializza il TimeManager, impostando l'ora di inizio della simulazione
        basandosi sulla configurazione.
        """
        self.total_simulation_ticks: int = 0
        try:
            # Crea l'oggetto fuso orario
            tz_obj = ATHDateTimeZone(time_config.DEFAULT_TIMEZONE)
        except ValueError as e:
            print(f"Errore CRITICO: Fuso orario non valido '{time_config.DEFAULT_TIMEZONE}' in time_config.py.")
            raise SystemExit(e) from e

        # Ottiene il nome del mese dalla lista in config, usando l'indice - 1
        try:
            start_month_index = time_config.SIMULATION_START_MONTH - 1
            start_month_name = time_config.MONTH_NAMES[start_month_index]
        except IndexError:
            print(f"Errore CRITICO: SIMULATION_START_MONTH ({time_config.SIMULATION_START_MONTH}) non è un indice valido per MONTH_NAMES in time_config.py.")
            raise SystemExit()

        self._current_time = ATHDateTime.from_components(
            year=time_config.SIMULATION_START_YEAR,
            month_name=start_month_name,
            day=time_config.SIMULATION_START_DAY,
            hour=time_config.SIMULATION_START_HOUR,
            minute=time_config.SIMULATION_START_MINUTE,
            second=time_config.SIMULATION_START_SECOND,
            ath_timezone_obj=tz_obj,
        )
        print(f"TimeManager inizializzato. Ora di inizio simulazione: {str(self._current_time)}")

    def get_current_time(self) -> ATHDateTime:
        """
        Restituisce l'oggetto ATHDateTime corrente.
        """
        return self._current_time

    def advance_time(self, game_speed: float):
        """
        Avanza il tempo della simulazione ad ogni tick.
        """
        seconds_to_add_float = time_config.SECONDS_PER_SIMULATION_TICK * game_speed
        integer_seconds = int(seconds_to_add_float)
        fractional_seconds = seconds_to_add_float - integer_seconds
        microseconds = int(fractional_seconds * 1_000_000)

        interval = ATHDateInterval(
            seconds=integer_seconds,
            microseconds=microseconds
        )
        self._current_time = self._current_time.add(interval)
        self.total_simulation_ticks += 1 # AGGIUNGI/VERIFICA QUESTA RIGA

    def get_ath_detailed_datetime(self) -> Dict[str, Union[int, str, None]]:
        """
        Restituisce un dizionario con i componenti dettagliati dell'ATHDateTime corrente,
        formattato come si aspetta il Renderer.
        """
        current_ath_time = self.get_current_time()
        if current_ath_time:
            return {
                'year': current_ath_time.year,
                'month_of_year': current_ath_time.month_index + 1, # ATHDateTime.month_index è 0-based
                'day_of_month': current_ath_time.day,
                'hour': current_ath_time.hour,
                'minute': current_ath_time.minute,
                'second': current_ath_time.second,
                'day_name': current_ath_time.day_of_week_name,
                'month_name': current_ath_time.month_name
            }
        return { # Fallback nel caso _current_time non sia inizializzato (improbabile dopo __init__)
                'year': 0, 'month_of_year': 0, 'day_of_month': 0,
                'hour': 0, 'minute': 0, 'second': 0,
                'day_name': "N/D", 'month_name': "N/D"
            }

    def __str__(self):
        """
        Restituisce una rappresentazione stringa dell'ora corrente usando i codici di formato di ATHDateTime.
        """
        return self.get_current_time().format('Y, JJ/NN G:II:SS TZN')