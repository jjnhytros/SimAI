# core/modules/time_manager.py
from core.world.ATHDateTime.ATHDateTime import ATHDateTime
from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval
from core.world.ATHDateTime.ATHDateTimeZone import ATHDateTimeZone
from core.config import time_config
from core.enums import TimeOfDay # Importa l'enum TimeOfDay
from typing import Dict, Union, List, Optional, Tuple

class TimeManager:
    """Gestisce il tempo universale della simulazione usando ATHDateTime."""

    def __init__(self):
        """Inizializza il TimeManager con l'ora di inizio dalla configurazione."""
        self.total_ticks_sim_run: int = 0 # Un semplice contatore per i tick del loop di simulazione
        
        # Inizializzazione basata su ATHDateTime (il tuo codice è già corretto)
        tz_obj = ATHDateTimeZone(time_config.DEFAULT_TIMEZONE)
        start_month_index = time_config.SIMULATION_START_MONTH - 1
        start_month_name = time_config.MONTH_NAMES[start_month_index]
        self._current_time: ATHDateTime = ATHDateTime.from_components(
            year=time_config.SIMULATION_START_YEAR, month_name=start_month_name,
            day=time_config.SIMULATION_START_DAY, hour=time_config.SIMULATION_START_HOUR,
            minute=time_config.SIMULATION_START_MINUTE, second=time_config.SIMULATION_START_SECOND,
            ath_timezone_obj=tz_obj,
        )
        print(f"TimeManager inizializzato. Ora di inizio: {self.get_formatted_datetime_string()}")

    def advance_time(self, game_speed: float):
        """Avanza il tempo della simulazione ad ogni tick del gioco."""
        seconds_to_add = int(time_config.SECONDS_PER_SIMULATION_TICK * game_speed)
        interval = ATHDateInterval(seconds=seconds_to_add) # ATHDateTime può gestire secondi float
        self._current_time = self._current_time.add(interval)
        self.total_ticks_sim_run += 1

    def get_current_time(self) -> ATHDateTime:
        """Restituisce l'oggetto ATHDateTime corrente."""
        return self._current_time

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

    # --- METODI GETTER AGGIORNATI PER USARE _current_time ---
    def get_current_minute(self) -> int:
        return self._current_time.minute

    def get_current_hour(self) -> int:
        return self._current_time.hour

    def get_current_hour_float(self) -> float:
        """Restituisce l'ora corrente come float (es. 14.5 per le 14:30)."""
        # Assumendo che time_config.MXH contenga i minuti in un'ora (es. 60)
        return self._current_time.hour + (self._current_time.minute / time_config.IXH)

    def get_formatted_datetime_string(self) -> str:
        """Restituisce una stringa formattata con data e ora correnti."""
        # Usa i codici definiti nel tuo metodo ATHDateTime.format
        # 'DAY' per il nome del giorno, 'JJ' per il giorno del mese,
        # 'MONTH' per il nome del mese, 'HH' per l'ora, 'II' per i minuti.
        format_string = "DAY, JJ MONTH Y - HH:II"
        
        return self._current_time.format(format_string)

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
