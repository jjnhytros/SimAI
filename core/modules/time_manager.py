# core/modules/time_manager.py

# Importiamo ogni classe direttamente dal suo file specifico all'interno del package
from core.world.ATHDateTime.ATHDateTime import ATHDateTime
from core.world.ATHDateTime.ATHDateInterval import ATHDateInterval
from core.world.ATHDateTime.ATHDateTimeZone import ATHDateTimeZone
from core.config import time_config
from core import settings
from typing import Dict, Union, Tuple, List, Optional

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
        self.total_ticks: int = 0
        self.TXI: int = time_config.IXM             # Ticks per Minute
        self.TXH: int = self.TXI * time_config.IXH  # Ticks per Hour
        self.TXD: int = self.TXH * time_config.HXD  # Ticks per Day
        self.TXM: int = self.TXD * time_config.DXM  # Ticks per Month
        self.TXY: int = self.TXM * time_config.MXY  # Ticks per Year
        self.initial_year: int = time_config.RY     # Initial year
        self.day_names: List[str] = time_config.DAY_NAMES       # Day Names
        self.month_names: List[str] = time_config.MONTH_NAMES   # Month Names
        if len(self.day_names) != time_config.DXW:
            raise ValueError(f"DAY_NAMES in settings ({len(self.day_names)}) non corrisponde a DXW ({time_config.DXW})")
        if len(self.month_names) != time_config.MXY:
            raise ValueError(f"MONTH_NAMES in settings ({len(self.month_names)}) non corrisponde a MXY ({time_config.MXY})")

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
        self.total_ticks += 1

    def get_current_time(self) -> ATHDateTime:
        """
        Restituisce l'oggetto ATHDateTime corrente.
        """
        return self._current_time

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

    def get_current_minute(self) -> int:
        """Restituisce il minuto corrente nell'ora (0-MXH-1)."""
        return (self.total_ticks % self.TXH) // self.TXI

    def get_current_hour(self) -> int:
        """Restituisce l'ora corrente nel giorno (0-HXD-1)."""
        return (self.total_ticks % self.TXD) // self.TXH

    def get_current_day_of_week_index(self) -> int:
        """Restituisce l'indice del giorno corrente nella settimana (0-DXW-1)."""
        current_total_days = self.total_ticks // self.TXD
        return current_total_days % time_config.DXW

    def get_current_day_in_month(self) -> int:
        """Restituisce il giorno corrente nel mese (1-DXM)."""
        day_in_year = (self.total_ticks % self.TXY) // self.TXD
        return (day_in_year % time_config.DXM) + 1

    def get_current_month_index(self) -> int:
        """Restituisce l'indice del mese corrente nell'anno (0-MXY-1)."""
        day_in_year = (self.total_ticks % self.TXY) // self.TXD
        return day_in_year // time_config.DXM

    def get_current_year(self) -> int:
        """Restituisce l'anno corrente della simulazione."""
        return self.initial_year + (self.total_ticks // self.TXY)

    def get_formatted_datetime_string(self) -> str:
        """Restituisce una stringa formattata con data e ora correnti."""
        year = self.get_current_year()
        month_idx = self.get_current_month_index()
        month_name = self.month_names[month_idx] if 0 <= month_idx < len(self.month_names) else f"MeseScon.{month_idx+1}"
        day_in_month = self.get_current_day_in_month()
        
        day_of_week_idx = self.get_current_day_of_week_index()
        day_of_week_name = self.day_names[day_of_week_idx] if 0 <= day_of_week_idx < len(self.day_names) else f"GiornoScon.{day_of_week_idx+1}"
        
        hour = self.get_current_hour()
        minute = self.get_current_minute()

        return (f"Anno {year}, {day_in_month} {month_name} ({day_of_week_name}) - "
                f"{hour:02d}:{minute:02d}")

    def is_work_day(self, day_of_week_index: Optional[int] = None) -> bool:
        """Verifica se è un giorno lavorativo standard (es. non weekend). Da personalizzare."""
        if day_of_week_index is None:
            day_of_week_index = self.get_current_day_of_week_index()
        # Esempio: se i primi 5 giorni (0-4) sono lavorativi
        # Adatta questo ai giorni lavorativi specifici di Anthalys
        return 0 <= day_of_week_index < (time_config.DXW - 2) # Assumendo 2 giorni di weekend

    def is_school_day(self, day_of_week_index: Optional[int] = None) -> bool:
        """Verifica se è un giorno scolastico standard. Da personalizzare."""
        # Spesso coincide con i giorni lavorativi, ma potrebbe avere eccezioni
        return self.is_work_day(day_of_week_index)


    def __str__(self):
        """
        Restituisce una rappresentazione stringa dell'ora corrente usando i codici di formato di ATHDateTime.
        """
        return self.get_current_time().format('Y, JJ/NN G:II:SS TZN')