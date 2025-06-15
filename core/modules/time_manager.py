# core/modules/time_manager.py
from core.world.ATHDateTime.ATHDateTime import ATHDateTime
from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval
from core.world.ATHDateTime.ATHDateTimeZone import ATHDateTimeZone
from core.config import time_config
from core.enums import TimeOfDay # Importa l'enum TimeOfDay
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union
import time
import threading

if TYPE_CHECKING:
    from core.simulation import Simulation


class TimeManager:
    """Gestisce il tempo universale della simulazione usando ATHDateTime."""

    def __init__(self, simulation_context: 'Simulation', start_date: Optional[ATHDateTime] = None):
        self.simulation_context = simulation_context
        self._current_time: ATHDateTime = start_date or ATHDateTime.from_components(
            year=5775, month_name="Arejal", day=1, hour=27
        )
        self.total_ticks_sim_run: int = 0
        self._last_hour_checked = self.get_current_hour()
        print(f"TimeManager inizializzato. Ora di inizio: {self.get_formatted_datetime_string()}")

    def get_current_time(self) -> ATHDateTime:
        return self._current_time

    def get_current_minute(self) -> int:
        return self._current_time.minute

    def get_current_hour(self) -> int:
        return self._current_time.hour

    def get_current_hour_float(self) -> float:
        return self._current_time.hour + (self._current_time.minute / time_config.IXH)

    def advance_time(self, ticks: int = 1):
        if ticks <= 0: return
        total_seconds_to_advance = ticks * time_config.SECONDS_PER_SIMULATION_TICK
        interval = ATHDateInterval(seconds=total_seconds_to_advance)
        self._current_time = self._current_time.add(interval)
        self.total_ticks_sim_run += ticks

        # --- NUOVA LOGICA DI DEBUG ---
        # Controlla se l'ora è cambiata dall'ultimo tick
        new_hour = self.get_current_hour()
        if new_hour != self._last_hour_checked:
            print(f"--- [TimeManager DEBUG] È passata un'ora di gioco. Ora attuale: {self.get_formatted_datetime_string()} ---")
            self._last_hour_checked = new_hour
        # --- FINE NUOVA LOGICA ---

    def get_formatted_datetime_string(self) -> str:
        format_string = "l, d F Y - H:i"
        return self._current_time.format(format_string)

    def get_ath_detailed_datetime(self) -> Dict[str, Union[int, str]]:
        """
        Restituisce un dizionario con i componenti dettagliati dell'ATHDateTime corrente,
        formattato come si aspetta il Renderer.
        """
        return {
            'year': self._current_time.year,
            'month_of_year': self._current_time.month_index + 1,
            'day_of_month': self._current_time.day,
            'hour': self._current_time.hour,
            'minute': self._current_time.minute,
            'second': self._current_time.second,
            'day_name': self._current_time.day_of_week_name,
            'month_name': self._current_time.month_name
        }


    def is_night(self) -> bool:
        """Restituisce True se è notte."""
        night_start_hour = getattr(time_config, 'NIGHT_START_HOUR', 26)
        night_end_hour = getattr(time_config, 'NIGHT_END_HOUR', 4)
        current_hour = self.get_current_hour()
        
        if night_start_hour > night_end_hour:
            return current_hour >= night_start_hour or current_hour < night_end_hour
        else:
            return night_start_hour <= current_hour < night_end_hour

    def get_time_of_day_info(self) -> Tuple[TimeOfDay, TimeOfDay, float]:
        """
        Restituisce la fase attuale, la fase successiva e il progresso (0.0-1.0) verso di essa.
        """
        current_hour_float = self._current_time.hour + (self._current_time.minute / time_config.IXH)
        
        # Ordina le fasi per ora di inizio
        sorted_phases = sorted(time_config.TIME_OF_DAY_START_HOURS.items(), key=lambda item: item[1])
        
        # Trova la fase attuale e la successiva
        current_phase = sorted_phases[-1][0] # Inizia con l'ultima fase come default (NIGHT)
        next_phase = sorted_phases[0][0]     # La successiva è la prima del giorno dopo
        
        for i in range(len(sorted_phases)):
            if current_hour_float >= sorted_phases[i][1]:
                current_phase = sorted_phases[i][0]
                # La fase successiva è la prossima nella lista, o la prima se siamo all'ultima
                next_phase = sorted_phases[(i + 1) % len(sorted_phases)][0]
            else:
                break
        
        # Calcola il progresso all'interno della fase corrente
        start_hour = time_config.TIME_OF_DAY_START_HOURS[current_phase]
        end_hour = time_config.TIME_OF_DAY_START_HOURS[next_phase]
        
        # Gestisce il caso della notte che scavalca il giorno (es. da 26 a 4)
        if end_hour < start_hour:
            end_hour += time_config.HXD # Aggiunge 28 ore
            if current_hour_float < start_hour:
                current_hour_float += time_config.HXD # Normalizza anche l'ora corrente

        phase_duration = end_hour - start_hour
        time_into_phase = current_hour_float - start_hour
        
        progress = time_into_phase / phase_duration if phase_duration > 0 else 0
        
        return current_phase, next_phase, max(0.0, min(1.0, progress))

