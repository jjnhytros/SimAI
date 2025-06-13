# simai/core/world/ATHDateTime.py
import re
import math
from datetime import datetime, timezone, timedelta
from typing import Optional, Union, List, Dict, TYPE_CHECKING

from .ATHDateTimeInterface import ATHDateTimeInterface
from .ATHDateInterval import ATHDateInterval 
from .ATHDateTimeZone import ATHDateTimeZone 
from .ath_timezone_config import get_default_ath_timezone 

# from ..ath_helpers import get_default_ath_timezone 

if TYPE_CHECKING:
    from .ATHDateTimeZoneInterface import ATHDateTimeZoneInterface

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    ZoneInfo = None 
    ZoneInfoNotFoundError = type('ZoneInfoNotFoundError', (Exception,), {})


class ATHDateTime(ATHDateTimeInterface):
    """
    Implementazione concreta di ATHDateTimeInterface.
    Gestisce la conversione e la manipolazione delle date nel calendario Anthalys.
    Tutte le costanti del calendario (HXD, DXY, MONTH_NAMES, EPOCH, ecc.) 
    e le costanti di formato (FORMAT_DEFAULT, ecc.) sono ereditate 
    da ATHDateTimeInterface.
    """
    
    # Attributi d'istanza con type hints per chiarezza interna
    _earth_datetime_origin_utc: datetime 
    _earth_timestamp_origin: float
    _seconds_since_A_epoch: float
    _ath_timezone_obj: Optional['ATHDateTimeZoneInterface']
    _year: int
    _month_index: int
    _month_name: str
    _day: int
    _day_of_week_index: int
    _day_of_week_name: str
    _hour: int
    _minute: int
    _second: int
    _seconds_in_day: float

    def __init__(self, earth_date: Optional[datetime] = None, 
                ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None) -> None:
        
        effective_timezone_obj = ath_timezone_obj
        if effective_timezone_obj is None: effective_timezone_obj = get_default_ath_timezone()
        
        if earth_date is None: earth_date = datetime.now(timezone.utc)
        
        if earth_date.tzinfo is None: self._earth_datetime_origin_utc = earth_date.replace(tzinfo=timezone.utc)
        else: self._earth_datetime_origin_utc = earth_date.astimezone(timezone.utc)
            
        self._earth_timestamp_origin = self._earth_datetime_origin_utc.timestamp()
        self._seconds_since_A_epoch = self._earth_timestamp_origin - self.EPOCH 
        self._ath_timezone_obj = effective_timezone_obj
        self._calculate_local_components()

    @property
    def year(self) -> int: return self._year
    @property
    def month_name(self) -> str: return self._month_name
    @property
    def month_index(self) -> int: return self._month_index
    @property
    def day(self) -> int: return self._day
    @property
    def day_of_week_name(self) -> str: return self._day_of_week_name
    @property
    def hour(self) -> int: return self._hour
    @property
    def minute(self) -> int: return self._minute
    @property
    def second(self) -> int: return self._second
    @property
    def seconds_since_A_epoch(self) -> float: return self._seconds_since_A_epoch

    def _calculate_local_components(self) -> None:
        # _seconds_since_A_epoch è il numero totale di secondi TERRESTRI FISICI
        # trascorsi dall'epoca del CALENDARIO Anthalejano.
        # L'epoca stessa è calcolata usando DXY_CALENDAR e SXD_CALENDAR.
        display_seconds = self._seconds_since_A_epoch
        
        if self._ath_timezone_obj:
            # get_offset restituisce un offset in secondi TERRESTRI FISICI
            display_seconds += self._ath_timezone_obj.get_offset(self) 
        
        # Dividi i secondi fisici totali per la durata in secondi fisici di un
        # GIORNO DEL CALENDARIO (basato su HXD_CALENDAR=28) per ottenere
        # il numero assoluto di giorni DEL CALENDARIO trascorsi.
        absolute_calendar_days = int(display_seconds // ATHDateTimeInterface.SXD_CALENDAR)
        
        # I secondi rimanenti all'interno del giorno DEL CALENDARIO corrente.
        self._seconds_in_day = display_seconds % ATHDateTimeInterface.SXD_CALENDAR
        
        # Calcola l'anno DEL CALENDARIO.
        # DXY_CALENDAR è il numero di giorni in un anno DEL CALENDARIO (432).
        self._year = absolute_calendar_days // ATHDateTimeInterface.DXY_CALENDAR
        
        # Giorno dell'anno all'interno dell'anno DEL CALENDARIO (0-indexed).
        day_of_calendar_year = absolute_calendar_days % ATHDateTimeInterface.DXY_CALENDAR
        
        # Calcola l'indice del mese DEL CALENDARIO (0-indexed).
        # DXM è il numero di giorni in un mese DEL CALENDARIO.
        self._month_index = day_of_calendar_year // ATHDateTimeInterface.DXM_CALENDAR
        
        if not (0 <= self._month_index < ATHDateTimeInterface.MXY_CALENDAR): # MXY è il numero di mesi in un anno DEL CALENDARIO
            # L'error message dovrebbe includere il timezone name, se disponibile
            tz_name_for_error = 'ATZ' # Default
            if self._ath_timezone_obj and hasattr(self._ath_timezone_obj, 'get_name'):
                tz_name_for_error = self._ath_timezone_obj.get_name()
            
            raise ValueError(
                f"Indice mese calcolato ({self._month_index}) fuori range 0-{ATHDateTimeInterface.MXY_CALENDAR-1} "
                f"per istante terrestre {self._earth_timestamp_origin} "
                f"(TZ: {tz_name_for_error}). "
                f"display_seconds: {display_seconds}, absolute_calendar_days: {absolute_calendar_days}"
            )
        
        self._month_name = ATHDateTimeInterface.MONTH_NAMES[self._month_index]
        
        # Calcola il giorno del mese DEL CALENDARIO (1-indexed).
        self._day = (day_of_calendar_year % ATHDateTimeInterface.DXM_CALENDAR) + 1
        
        # Calcola l'indice del giorno della settimana DEL CALENDARIO (0-indexed).
        # DXW è il numero di giorni in una settimana DEL CALENDARIO.
        self._day_of_week_index = absolute_calendar_days % ATHDateTimeInterface.DXW_CALENDAR
        self._day_of_week_name = ATHDateTimeInterface.DAY_NAMES[self._day_of_week_index]
        
        # Calcola ora, minuto, secondo DEL CALENDARIO da self._seconds_in_day.
        # IXH e SXI sono i minuti per ora e secondi per minuto del CALENDARIO.
        self._hour = int(self._seconds_in_day // (ATHDateTimeInterface.IXH_CALENDAR * ATHDateTimeInterface.SXI_CALENDAR))
        self._minute = int((self._seconds_in_day % (ATHDateTimeInterface.IXH_CALENDAR * ATHDateTimeInterface.SXI_CALENDAR)) // ATHDateTimeInterface.SXI_CALENDAR)
        self._second = int(self._seconds_in_day % ATHDateTimeInterface.SXI_CALENDAR)

    @classmethod
    def from_components(cls, year: int, month_name: str, day: int,
                        hour: int = 0, minute: int = 0, second: int = 0,
                        ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None) -> 'ATHDateTime':
        
        effective_tz = ath_timezone_obj
        if effective_tz is None:
            effective_tz = get_default_ath_timezone() # Usa il default (ATZ)
        
        # ATHDateTimeInterface contiene MONTH_NAMES, DXM, HXD_CALENDAR, ecc.
        if month_name not in ATHDateTimeInterface.MONTH_NAMES:
            raise ValueError(f"Nome del mese Anthaleja non valido: {month_name}")
        month_idx = ATHDateTimeInterface.MONTH_NAMES.index(month_name)

        if not (1 <= day <= ATHDateTimeInterface.DXM_CALENDAR): # DXM è giorni nel mese CALENDARIALE
            raise ValueError(f"Giorno del mese Anthaleja non valido: {day} (deve essere 1-{ATHDateTimeInterface.DXM_CALENDAR})")
        if not (0 <= hour < ATHDateTimeInterface.HXD_CALENDAR): # Usa HXD_CALENDAR
            raise ValueError(f"Ora Anthaleja non valida: {hour} (deve essere 0-{ATHDateTimeInterface.HXD_CALENDAR-1})")
        if not (0 <= minute < ATHDateTimeInterface.IXH_CALENDAR):
            raise ValueError(f"Minuto Anthaleja non valido: {minute} (deve essere 0-{ATHDateTimeInterface.IXH_CALENDAR-1})")
        if not (0 <= second < ATHDateTimeInterface.SXI_CALENDAR):
            raise ValueError(f"Secondo Anthaleja non valido: {second} (deve essere 0-{ATHDateTimeInterface.SXI_CALENDAR-1})")

        # Calcola i giorni totali del CALENDARIO dall'anno 0 del CALENDARIO
        total_days_local_calendar = (year * ATHDateTimeInterface.DXY_CALENDAR) + \
                                    (month_idx * ATHDateTimeInterface.DXM_CALENDAR) + \
                                    (day - 1)
        
        # Secondi trascorsi nel giorno del CALENDARIO specificato
        total_seconds_in_day_local_calendar = (hour * ATHDateTimeInterface.IXH_CALENDAR * ATHDateTimeInterface.SXI_CALENDAR) + \
                                              (minute * ATHDateTimeInterface.SXI_CALENDAR) + second
        
        # Totale secondi "locali" (nel fuso orario `effective_tz`) dall'epoca 0 del CALENDARIO Anthalejano,
        # calcolati usando la struttura del CALENDARIO.
        seconds_local_in_effective_tz_from_calendar_epoch = \
            total_days_local_calendar * ATHDateTimeInterface.SXD_CALENDAR + \
            total_seconds_in_day_local_calendar
        
        # Per convertire in un timestamp assoluto (basato sull'EPOCH che è in ATZ),
        # dobbiamo normalizzare questi secondi locali a "secondi come se fossero in ATZ".
        seconds_equivalent_in_atz_from_calendar_epoch = seconds_local_in_effective_tz_from_calendar_epoch
        
        if effective_tz.get_name() != "ATZ": # Solo se il fuso orario non è già ATZ
            # Creiamo un ATHDateTime temporaneo basato sui secondi calcolati *come se fossero ATZ*
            # Questo serve per dare un contesto temporale a get_offset(), poiché l'offset
            # potrebbe (in teoria) dipendere dalla data/ora.
            temp_earth_ts_for_offset_calc = ATHDateTimeInterface.EPOCH + seconds_local_in_effective_tz_from_calendar_epoch
            temp_earth_dt_for_offset_calc = datetime.fromtimestamp(temp_earth_ts_for_offset_calc, tz=timezone.utc)
            
            # Usiamo None per il fuso orario dell'oggetto temporaneo, così usa il default (ATZ)
            # o passiamo ATHDateTimeZone("ATZ") esplicitamente se `get_default_ath_timezone()` potesse cambiare.
            # Dato che get_default_ath_timezone() è in ath_timezone_config.py e dovrebbe
            # restituire un oggetto ATZDateTimeZone, possiamo affidarci a quello.
            temp_ath_dt_for_offset_calc = cls(temp_earth_dt_for_offset_calc, ath_timezone_obj=None)
            
            offset_seconds = effective_tz.get_offset(temp_ath_dt_for_offset_calc)
            seconds_equivalent_in_atz_from_calendar_epoch -= offset_seconds
            
        # Ora `seconds_equivalent_in_atz_from_calendar_epoch` sono i secondi fisici
        # trascorsi dall'EPOCH (che è definita in ATZ) fino al momento specificato.
        final_earth_timestamp = ATHDateTimeInterface.EPOCH + seconds_equivalent_in_atz_from_calendar_epoch
        final_earth_dt_utc = datetime.fromtimestamp(final_earth_timestamp, tz=timezone.utc)
        
        # Creiamo l'istanza finale con il fuso orario effettivo richiesto.
        return cls(final_earth_dt_utc, ath_timezone_obj=effective_tz)

    @classmethod
    def create_from_format(cls, 
                        format_string: str, 
                        datetime_string: str,
                        ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None
                        ) -> Optional['ATHDateTime']:
        effective_tz = ath_timezone_obj
        if effective_tz is None: effective_tz = get_default_ath_timezone()
        # Mappa dei nuovi codici di formato Anthaleja a pattern regex
        format_to_regex_map = {
            'M':   r'(' + r'|'.join(map(re.escape, cls.MONTH_NAMES)) + r')',      
            'Mon': r'(' + r'|'.join(map(re.escape, cls.MONTH_ABBR.values())) + r')',
            'D':   r'(' + r'|'.join(map(re.escape, cls.DAY_NAMES)) + r')',        
            'DayN':r'(' + r'|'.join(map(re.escape, cls.DAY_ABBR_ATH.values())) + r')',
            'YYYY':r'(\d{4})', 'Y': r'(\d{1,4})', 'y': r'(\d{2})',                
            'NN':  r'(0[1-9]|1[0-8])', 'N': r'([1-9]|1[0-8])',                     
            'JJ':  r'(0[1-9]|1[0-9]|2[0-4])', 'J': r'([1-9]|1[0-9]|2[0-4])',     
            'HH':  r'(0[0-9]|1[0-9]|2[0-7])', 'G': r'([0-9]|1[0-9]|2[0-7])',      
            'II':  r'([0-5][0-9])', 'I': r'([0-9]|[1-5][0-9])',                   
            'SS':  r'([0-5][0-9])', 'S': r'([0-9]|[1-5][0-9])',                   
        }
        regex_parts = []
        component_order = [] # Per sapere a quale componente corrisponde ogni gruppo catturato
        
        current_format_idx = 0
        # Ordina per lunghezza decrescente per matchare prima i codici più lunghi
        sorted_format_codes = sorted(format_to_regex_map.keys(), key=len, reverse=True)

        temp_format_string = format_string # Usa una copia per il loop
        while temp_format_string:
            matched_code_in_loop = None
            for code in sorted_format_codes:
                if temp_format_string.startswith(code):
                    regex_parts.append(format_to_regex_map[code])
                    component_order.append(code) 
                    temp_format_string = temp_format_string[len(code):]
                    matched_code_in_loop = True
                    break
            if not matched_code_in_loop: # Carattere letterale
                regex_parts.append(re.escape(temp_format_string[0]))
                temp_format_string = temp_format_string[1:]
        
        full_regex_pattern = r'^' + r''.join(regex_parts) + r'$'
        
        try:
            match = re.match(full_regex_pattern, datetime_string)
            if not match: 
                return None

            extracted_values = match.groups()
            # Il tipo è Dict[str, Union[int, str]] perché alcuni componenti sono int (anno, giorno)
            # e month_name è str.
            parsed_components: Dict[str, Union[int, str]] = {} 

            if len(extracted_values) != len(component_order): 
                return None 
            
            for i, comp_code in enumerate(component_order):
                value_str = extracted_values[i]
                # Mappa i codici ATH ai nomi dei parametri per from_components
                if comp_code in ['YYYY', 'Y', 'y']: 
                    parsed_components['year'] = int(value_str)
                    # TODO: Logica per 'y' (anno a 2 cifre) se necessario (es. pivot year)
                elif comp_code == 'M': 
                    parsed_components['month_name'] = value_str # È già una stringa (nome completo)
                elif comp_code == 'Mon':
                    month_found = False
                    for name, abbr_val in cls.MONTH_ABBR.items():
                        if abbr_val == value_str: 
                            parsed_components['month_name'] = name # 'name' è una stringa
                            month_found = True
                            break
                    if not month_found: return None
                elif comp_code in ['NN', 'N']:
                    month_num = int(value_str)
                    if not (1 <= month_num <= cls.MXY_CALENDAR): return None
                    parsed_components['month_name'] = cls.MONTH_NAMES[month_num - 1] # Restituisce una stringa
                elif comp_code in ['JJ', 'J']: 
                    parsed_components['day'] = int(value_str)
                elif comp_code in ['HH', 'G']: 
                    parsed_components['hour'] = int(value_str)
                elif comp_code in ['II', 'I']: 
                    parsed_components['minute'] = int(value_str)
                elif comp_code in ['SS', 'S']: 
                    parsed_components['second'] = int(value_str)
            
            # Verifica che i componenti essenziali siano stati parsati
            if not all(k in parsed_components for k in ['year', 'month_name', 'day']):
                return None 
            
            # A questo punto, parsed_components['month_name'] DOVREBBE essere una stringa
            # grazie alla logica di parsing sopra.
            # Per essere ultra-sicuri con Pylance, possiamo fare un controllo esplicito
            # o un cast se fossimo incerti, ma la logica dovrebbe già garantire il tipo corretto.
            final_month_name = parsed_components['month_name']
            if not isinstance(final_month_name, str):
                # Questo indicherebbe un bug nella logica di parsing sopra se 'month_name' non è str
                return None # Fallback di sicurezza

            return cls.from_components( 
                year=int(parsed_components['year']), # Assicura int
                month_name=final_month_name,      # Ora Pylance sa che è str
                day=int(parsed_components['day']),    # Assicura int
                hour=int(parsed_components.get('hour', 0)), # Assicura int
                minute=int(parsed_components.get('minute', 0)), # Assicura int
                second=int(parsed_components.get('second', 0)), # Assicura int
                ath_timezone_obj=effective_tz 
            )
        except (re.error, ValueError, IndexError, TypeError): 
            return None

    @classmethod
    def from_rdn_offset_seconds(cls, rdn_offset_seconds: int,
                                ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None) -> 'ATHDateTime':
        effective_tz = ath_timezone_obj if ath_timezone_obj is not None else get_default_ath_timezone()
        target_unix_ts = cls.RDN_UNIX_TS + int(rdn_offset_seconds)
        earth_dt_utc = datetime.fromtimestamp(target_unix_ts, tz=timezone.utc)
        return cls(earth_dt_utc, ath_timezone_obj=effective_tz)

    @classmethod
    def from_array_state(cls, state_array: dict) -> 'ATHDateTime':
        if not isinstance(state_array, dict): raise TypeError("Input state_array deve essere un dizionario.")
        year = state_array.get('year'); month_name = state_array.get('month_name'); day = state_array.get('day')
        if year is None or month_name is None or day is None:
            raise ValueError("state_array deve contenere 'year', 'month_name', e 'day'.")
        
        ath_timezone_name = state_array.get('ath_timezone_name')
        tz_obj: Optional['ATHDateTimeZoneInterface'] = None
        if ath_timezone_name:
            try: tz_obj = ATHDateTimeZone(ath_timezone_name)
            except ValueError: pass 
        effective_tz = tz_obj
        if effective_tz is None: effective_tz = get_default_ath_timezone()

        return cls.from_components(
            year=int(year), month_name=str(month_name), day=int(day),
            hour=int(state_array.get('hour', 0)),
            minute=int(state_array.get('minute', 0)), 
            second=int(state_array.get('second', 0)),
            ath_timezone_obj=effective_tz )

    def format(self, format_string: str) -> str:
        """
        Formatta la data e l'ora secondo una stringa di formato in stile PHP.
        Versione corretta che calcola i valori mancanti.
        """
        output = []
        tz_obj = self.get_timezone()
        offset_val_seconds = tz_obj.get_offset(self) if tz_obj else 0
        
        day_of_week_map_1_7 = {
            'Nijahr': 7, 'Majahr': 1, 'Tucmahr': 2, 'Wejahr': 3, 
            'Þujahr': 4, 'Frijahr': 5, 'Ĝejahr': 6
        }

        # --- CALCOLI AGGIUNTIVI NECESSARI ---
        # Calcoliamo i valori che mancavano usando gli attributi esistenti
        day_of_year = (self.month_index * self.DXM_CALENDAR) + self.day
        week_of_year = ((day_of_year - 1) // self.DXW_CALENDAR) + 1
        days_in_month = self.DXM_CALENDAR # Nel tuo calendario, ogni mese ha lo stesso numero di giorni
        # --- FINE CALCOLI AGGIUNTIVI ---

        i = 0
        while i < len(format_string):
            char = format_string[i]
            
            # Controlla se il carattere è un codice di formato
            if char == 'd': output.append(str(self.day).zfill(2))
            elif char == 'D': output.append(self.DAY_ABBR_ATH.get(self.day_of_week_name, '??'))
            elif char == 'j': output.append(str(self.day))
            elif char == 'l': output.append(self.day_of_week_name)
            elif char == 'N': output.append(str(day_of_week_map_1_7.get(self.day_of_week_name, 0)))
            elif char == 'S': output.append('x')
            elif char == 'w': output.append(str(self._day_of_week_index)) # Usa l'attributo interno
            elif char == 'z': output.append(str(day_of_year - 1)) # Usa il valore calcolato
            elif char == 'W': output.append(str(week_of_year)) # Usa il valore calcolato
            elif char == 'F': output.append(self.month_name)
            elif char == 'm': output.append(str(self.month_index + 1).zfill(2))
            elif char == 'M': output.append(self.MONTH_ABBR.get(self.month_name, '???'))
            elif char == 'n': output.append(str(self.month_index + 1))
            elif char == 't': output.append(str(days_in_month)) # Usa il valore calcolato
            elif char == 'Y': output.append(str(self.year))
            elif char == 'y': output.append(str(self.year % 100).zfill(2))
            elif char == 'G': output.append(str(self.hour))
            elif char == 'H': output.append(str(self.hour).zfill(2))
            elif char == 'i': output.append(str(self.minute).zfill(2))
            elif char == 's': output.append(str(self.second).zfill(2))
            elif char == 'u': output.append(str(getattr(self._earth_datetime_origin_utc, 'microsecond', 0)).zfill(6))
            elif char == 'e': output.append(tz_obj.get_name() if tz_obj else "ATZ")
            elif char == 'P':
                sign = "+" if offset_val_seconds >= 0 else "-"
                offset_hours = abs(offset_val_seconds) // (self.IXH_CALENDAR * self.SXI_CALENDAR)
                offset_minutes = (abs(offset_val_seconds) % (self.IXH_CALENDAR * self.SXI_CALENDAR)) // self.SXI_CALENDAR
                output.append(f"{sign}{offset_hours:02d}:{offset_minutes:02d}")
            elif char == 'U': output.append(str(self.get_earth_timestamp())) # Usa get_earth_timestamp
            else:
                output.append(char)
            
            i += 1
            
        return "".join(output)

    def get_earth_timestamp(self) -> int: return int(self._earth_timestamp_origin)
    def get_timezone(self) -> Optional['ATHDateTimeZoneInterface']: return self._ath_timezone_obj

    def add(self, interval: ATHDateInterval) -> 'ATHDateTime':
        if not isinstance(interval, ATHDateInterval): raise TypeError("L'intervallo deve essere ATHDateInterval.")
        new_seconds_since_A_epoch = self._seconds_since_A_epoch + interval.total_earth_seconds()
        new_earth_dt_utc = datetime.fromtimestamp(self.EPOCH + new_seconds_since_A_epoch, tz=timezone.utc)
        return ATHDateTime(new_earth_dt_utc, ath_timezone_obj=self._ath_timezone_obj)

    def sub(self, interval: ATHDateInterval) -> 'ATHDateTime':
        if not isinstance(interval, ATHDateInterval): raise TypeError("L'intervallo deve essere ATHDateInterval.")
        inverted_interval = ATHDateInterval(
            interval.y, interval.m, interval.d, interval.h, interval.i, interval.s,
            int(interval.f * 1_000_000), invert=not interval.invert )
        return self.add(inverted_interval)

    def diff(self, target_object: ATHDateTimeInterface, 
            absolute: bool = False) -> ATHDateInterval:
        if not isinstance(target_object, ATHDateTimeInterface):
            raise TypeError("L'oggetto target deve implementare ATHDateTimeInterface.")
        
        # Differenza in secondi terrestri fisici
        difference_in_seconds_float = self._earth_timestamp_origin - target_object.get_earth_timestamp()
        
        should_invert_interval = False
        if difference_in_seconds_float < 0:
            should_invert_interval = True
        
        abs_diff_seconds = abs(difference_in_seconds_float)

        if absolute:
            should_invert_interval = False

        # Usa le costanti del CALENDARIO per convertire i secondi fisici in unità di intervallo
        sxi_calendar = ATHDateTimeInterface.SXI_CALENDAR
        ixh_calendar = ATHDateTimeInterface.IXH_CALENDAR
        sxd_calendar = ATHDateTimeInterface.SXD_CALENDAR # Secondi in un giorno del calendario
        dxm_calendar = ATHDateTimeInterface.DXM_CALENDAR      # Giorni in un mese del calendario
        dxy_calendar = ATHDateTimeInterface.DXY_CALENDAR # Giorni in un anno del calendario

        years, months, days, hours, minutes, seconds, microseconds = 0,0,0,0,0,0,0

        if abs_diff_seconds >= (dxy_calendar * sxd_calendar):
            years = math.floor(abs_diff_seconds / (dxy_calendar * sxd_calendar))
            abs_diff_seconds %= (dxy_calendar * sxd_calendar)

        if abs_diff_seconds >= (dxm_calendar * sxd_calendar):
            months = math.floor(abs_diff_seconds / (dxm_calendar * sxd_calendar))
            abs_diff_seconds %= (dxm_calendar * sxd_calendar)

        if abs_diff_seconds >= sxd_calendar:
            days = math.floor(abs_diff_seconds / sxd_calendar)
            abs_diff_seconds %= sxd_calendar

        if abs_diff_seconds >= (ixh_calendar * sxi_calendar):
            hours = math.floor(abs_diff_seconds / (ixh_calendar * sxi_calendar))
            abs_diff_seconds %= (ixh_calendar * sxi_calendar)

        if abs_diff_seconds >= sxi_calendar:
            minutes = math.floor(abs_diff_seconds / sxi_calendar)
            abs_diff_seconds %= sxi_calendar
        
        seconds_component_float = abs_diff_seconds
        seconds = math.floor(seconds_component_float)
        microseconds = int(round((seconds_component_float - seconds) * 1_000_000))

        return ATHDateInterval(
            years=int(years), 
            months=int(months), 
            days=int(days),
            hours=int(hours), 
            minutes=int(minutes), 
            seconds=int(seconds),
            microseconds=microseconds, 
            invert=should_invert_interval
        )

    def modify(self, modifier_string: str) -> Optional['ATHDateTime']:
        original_string = modifier_string
        modifier_string_lower = modifier_string.lower().strip()

        # 1. Gestione di "ieri", "oggi", "domani" (parole chiave del CALENDARIO)
        # ATHDateTime.from_components usa internamente le costanti _CALENDAR
        if modifier_string_lower == "embadan": # Oggi
            return ATHDateTime.from_components(self.year, self.month_name, self.day, 0,0,0, self._ath_timezone_obj)
        elif modifier_string_lower == "embadyl": # Ieri
            # ATHDateInterval(days=-1) si riferisce a giorni del CALENDARIO
            # .add() usa le costanti _CALENDAR per convertire l'intervallo in secondi
            yesterday_obj = self.add(ATHDateInterval(days=-1))
            return ATHDateTime.from_components(yesterday_obj.year, yesterday_obj.month_name, yesterday_obj.day, 0,0,0, self._ath_timezone_obj)
        elif modifier_string_lower == "embax": # Domani
            tomorrow_obj = self.add(ATHDateInterval(days=1))
            return ATHDateTime.from_components(tomorrow_obj.year, tomorrow_obj.month_name, tomorrow_obj.day, 0,0,0, self._ath_timezone_obj)

        # 2. Riferimenti a Parti Specifiche del Giorno/Mese/Anno (CALENDARIO)
        # ... (logica per pide, ymet, nalmek, etc.) ...
        # Quando si fa ATHDateTime.from_components, i valori HXD-1, IXH-1, SXI-1, DXM, MXY-1
        # devono riferirsi alle costanti del CALENDARIO.
        # Es. ymet jahr: HXD_CALENDAR-1, IXH-1, SXI-1
        # Es. ymet mai: DXM (calendariale)
        # Es. ymet nesdol: MONTH_NAMES[ATHDateTimeInterface.MXY-1] (calendariale)
        
        # Le costanti HXD, IXH, SXI, DXM, MXY nell'interfaccia sono quelle calendariali
        # se non specificato diversamente, quindi this.HXD, this.IXH etc. dovrebbero
        # già riferirsi implicitamente a HXD_CALENDAR ecc.
        # Per chiarezza:
        key_pide = "pide"; key_ymet = "ymet" 
        key_nalmek = "nalmek"; key_daja = "daja"; key_san = "san"; key_nahr = "nahr"
        key_jahr = "jahr"; key_mai = "mai"; key_nesdol = "nesdol"
        key_vedan = "vedan"; key_venahr = "venahr"; key_vekia = "vekia"
        
        day_part_start_hours = {key_nalmek: 7, key_daja: 14, key_san: 21, key_nahr: 26}
        
        parts = modifier_string_lower.split()
        new_year, new_month_name, new_day = self.year, self.month_name, self.day
        new_hour, new_minute, new_second = self.hour, self.minute, self.second

        if len(parts) == 1:
            keyword = parts[0]
            if keyword == key_vedan: new_hour,new_minute,new_second = 14,0,0
            elif keyword == key_venahr: new_hour,new_minute,new_second = 0,0,0
            elif keyword == key_vekia: # Aggiunge/sottrae mezz'ora. Per ora, interpretiamolo come "imposta a :30"
                                    # o se è :30, imposta a :00. Semplificazione: aggiungi 30 minuti.
                return self.add(ATHDateInterval(minutes=30)) # Usa 'minutes'
            elif keyword in day_part_start_hours: 
                new_hour = day_part_start_hours[keyword]; new_minute,new_second = 0,0
            else: # Potrebbe essere un offset semplice senza +/- (es. "10 giorni")
                offset_match_no_sign = re.match(rf"(\d+)\s*({self._get_unit_pattern_for_modify()})\b", modifier_string_lower)
                if offset_match_no_sign: parts.insert(0, ""); # Inserisci segno vuoto per riutilizzare logica sotto
                else: return None # Non riconosciuto come parola chiave singola
            
            if keyword in [key_vedan, key_venahr] or keyword in day_part_start_hours:
                return ATHDateTime.from_components(new_year, new_month_name, new_day, new_hour, new_minute, new_second, self._ath_timezone_obj)
        if len(parts) == 2: # Gestione "pide/ymet unità"
            action_word, unit_word = parts[0], parts[1]
            target_known = False
            if action_word == key_pide: 
                if unit_word == key_jahr: new_hour,new_minute,new_second = 0,0,0; target_known = True
                elif unit_word == key_mai: new_day=1; new_hour,new_minute,new_second = 0,0,0; target_known = True
                elif unit_word == key_nesdol: new_month_name=self.MONTH_NAMES[0]; new_day=1; new_hour,new_minute,new_second = 0,0,0; target_known = True
                elif unit_word in day_part_start_hours: new_hour = day_part_start_hours[unit_word]; new_minute,new_second = 0,0; target_known = True
            elif action_word == key_ymet: 
                if unit_word == key_jahr: new_hour,new_minute,new_second = ATHDateTimeInterface.HXD_CALENDAR-1, ATHDateTimeInterface.IXH_CALENDAR-1, ATHDateTimeInterface.SXI_CALENDAR-1; target_known = True
                elif unit_word == key_mai: new_day=ATHDateTimeInterface.DXM_CALENDAR; new_hour,new_minute,new_second = ATHDateTimeInterface.HXD_CALENDAR-1,ATHDateTimeInterface.IXH_CALENDAR-1,ATHDateTimeInterface.SXI_CALENDAR-1; target_known = True
                elif unit_word == key_nesdol: new_month_name=ATHDateTimeInterface.MONTH_NAMES[ATHDateTimeInterface.MXY_CALENDAR-1]; new_day=ATHDateTimeInterface.DXM_CALENDAR; new_hour,new_minute,new_second = ATHDateTimeInterface.HXD_CALENDAR-1,ATHDateTimeInterface.IXH_CALENDAR-1,ATHDateTimeInterface.SXI_CALENDAR-1; target_known = True
            if target_known:
                return ATHDateTime.from_components(new_year, new_month_name, new_day, new_hour, new_minute, new_second, self._ath_timezone_obj)

        # 3. Parsing degli Offset Semplici
        # ATHDateInterval è creato con unità calendariali.
        # Il metodo .add() lo gestirà correttamente.
        # ... (logica di parsing degli offset non cambia) ...
        #     interval = ATHDateInterval(years=y, months=mo, days=da, hours=ho, minutes=mi, seconds=se, microseconds=us, invert=invert)
        #     return self.add(interval)
        offset_match_full = re.match(rf"([+-]?)(\d+)\s*({self._get_unit_pattern_for_modify()})\b", modifier_string_lower)
        if offset_match_full:
            sign_str, value_str, unit_keyword_matched = offset_match_full.groups()
            value = int(value_str); invert = (sign_str == '-')
            y,mo,da,ho,mi,se,us = 0,0,0,0,0,0,0 
            uk = unit_keyword_matched.lower()
            if uk.startswith("nesdol") or uk.startswith("ann") or uk.startswith("year"): y = value
            elif uk.startswith("mai") or uk.startswith("mes") or uk.startswith("month"): mo = value
            elif uk.startswith("jahr") or uk.startswith("giorn") or uk.startswith("day"): da = value
            elif uk.startswith("ki") or uk.startswith("or") or uk.startswith("hour"): ho = value
            elif uk.startswith("redan") or uk.startswith("minut"): mi = value
            elif uk.startswith("dilka") or uk.startswith("second"): se = value
            else: return None 
            interval = ATHDateInterval(years=y, months=mo, days=da, hours=ho, minutes=mi, seconds=se, microseconds=us, invert=invert)
            return self.add(interval)
        
        # 4. Prossimo/Ultimo Giorno della Settimana (CALENDARIO)
        # DXW è giorni nella settimana del CALENDARIO
        day_names_pattern = "|".join(self.DAY_NAMES) 
        key_milo_val = "milo"; key_ymet_val = "ymet"; # Valori diretti
        day_modifier_match = re.match(rf"({key_milo_val}|{key_ymet_val})\s+({day_names_pattern})", original_string, re.IGNORECASE) 
        if day_modifier_match:
            direction_keyword, target_day_name_input = day_modifier_match.groups()
            direction = "prossimo" if direction_keyword.lower() == key_milo_val else "ultimo"
            target_day_name_official = ""; 
            for name in self.DAY_NAMES: 
                if name.lower() == target_day_name_input.lower(): target_day_name_official = name; break
            if not target_day_name_official: return None
            current_day_idx = self._day_of_week_index
            try: target_day_idx = self.DAY_NAMES.index(target_day_name_official)
            except ValueError: return None
            days_to_change = 0; new_date_obj: Optional[ATHDateTime] = None
            if direction == "prossimo":
                diff_days = (target_day_idx - current_day_idx + self.DXW_CALENDAR) % self.DXW_CALENDAR
                days_to_change = diff_days if diff_days != 0 else self.DXW_CALENDAR
            elif direction == "ultimo":
                diff_days = (current_day_idx - target_day_idx + self.DXW_CALENDAR) % self.DXW_CALENDAR
                days_to_change = diff_days if diff_days != 0 else self.DXW_CALENDAR
            else: return None 
            interval = ATHDateInterval(days=days_to_change, invert=(direction=="ultimo"))
            new_date_obj = self.add(interval)
            if new_date_obj:
                return ATHDateTime.from_components(
                    new_date_obj.year, new_date_obj.month_name, new_date_obj.day,
                    self.hour, self.minute, self.second, self._ath_timezone_obj )
            else: return None
        return None

    def _get_unit_pattern_for_modify(self) -> str: # Metodo helper per il pattern delle unità
        return (
            r"nesdolix|nesdol|ann(?:o|i)|year(?:s)?|" # Anno (ATH, IT, EN)
            r"maix|mai|mes(?:e|i)|month(?:s)?|" # Mese (ATH, IT, EN)
            r"jahrix|jahr|giorn(?:o|i)|day(?:s)?|" # Giorno (ATH, IT, EN)
            r"kie|kia|or(?:a|e)|hour(?:s)?|"   # Ora (ATH, IT, EN)        
            r"redanix|redan|minut(?:o|i)|minute(?:s)?|" # Minuto (ATH, IT, EN)
            r"dilkax|dilka|second(?:o|i)|second(?:s)?" # Secondo (ATH, IT, EN)
        )

    def set_date(self, year: int, month_input: Union[str, int], day: int) -> 'ATHDateTime':
        """
        Imposta una nuova data Anthaleja sull'oggetto, mantenendo l'ora originale.
        Restituisce una nuova istanza di ATHDateTime.
        month_input può essere il nome del mese (str), la sua abbreviazione (str), 
        o l'indice 1-based (int).
        """
        month_name_resolved: str = "" # <<< INIZIALIZZATA PER SICUREZZA E PER PYLANCE

        if isinstance(month_input, str):
            # Normalizza l'input del nome del mese per il confronto (es. prima lettera maiuscola)
            # e gestisce sia nomi completi che abbreviazioni.
            month_input_standardized = month_input.capitalize() if len(month_input) > 3 else month_input.lower()

            if month_input_standardized in self.MONTH_NAMES: # self.MONTH_NAMES ereditato
                month_name_resolved = month_input_standardized
            else: 
                # Prova a matchare con le abbreviazioni (case-insensitive)
                found_abbr = False
                for name, abbr in self.MONTH_ABBR.items(): # self.MONTH_ABBR ereditato
                    if abbr.lower() == month_input_standardized: # Confronto normalizzato
                        month_name_resolved = name
                        found_abbr = True
                        break
                if not found_abbr:
                    raise ValueError(f"Nome o abbreviazione del mese Anthaleja non valido: '{month_input}'")
        elif isinstance(month_input, int):
            if not (1 <= month_input <= self.MXY_CALENDAR): # self.MXY ereditato (numero di mesi)
                raise ValueError(f"Indice del mese Anthaleja non valido: {month_input} (deve essere 1-{self.MXY_CALENDAR})")
            month_name_resolved = self.MONTH_NAMES[month_input - 1] # self.MONTH_NAMES ereditato
        else:
            raise TypeError("Il parametro 'month_input' deve essere una stringa (nome/abbreviazione mese) o un intero (indice 1-18).")
        
        # Se month_name_resolved è rimasta vuota, c'è un errore logico sopra che non ha sollevato eccezione
        if not month_name_resolved: # Controllo di sicurezza aggiuntivo
            raise Exception("Errore logico interno: month_name_resolved non impostato.")

        if not (1 <= day <= self.DXM_CALENDAR): # self.DXM ereditato (giorni per mese)
            raise ValueError(f"Giorno del mese Anthaleja non valido: {day} (deve essere 1-{self.DXM_CALENDAR})")

        # Utilizza from_components mantenendo l'ora, i minuti e i secondi dell'istanza 'self'
        # e propagando il fuso orario.
        return ATHDateTime.from_components( 
            year=int(year), 
            month_name=month_name_resolved, 
            day=int(day),
            hour=self.hour,      
            minute=self.minute,  
            second=self.second,
            ath_timezone_obj=self._ath_timezone_obj 
        )

    def set_week_date(self, year: int, week: int, day_of_week: int = 1) -> Optional['ATHDateTime']:
        # Validazione basata sui limiti del CALENDARIO
        if not (1 <= day_of_week <= ATHDateTimeInterface.DXW_CALENDAR): # DXW è giorni nella settimana del CALENDARIO
            return None 
        
        # Calcola il numero del giorno nell'anno CALENDARIALE
        # DXW è giorni/settimana del CALENDARIO
        day_number_in_year = ((week - 1) * ATHDateTimeInterface.DXW_CALENDAR) + day_of_week
        
        # DXY_CALENDAR è giorni/anno del CALENDARIO
        if not (1 <= day_number_in_year <= ATHDateTimeInterface.DXY_CALENDAR): 
            return None 
        
        # Calcola mese e giorno del mese del CALENDARIO
        # DXM è giorni/mese del CALENDARIO
        month_A_idx = (day_number_in_year - 1) // ATHDateTimeInterface.DXM_CALENDAR
        day_A_in_month = ((day_number_in_year - 1) % ATHDateTimeInterface.DXM_CALENDAR) + 1
        
        # MXY è mesi/anno del CALENDARIO
        if not (0 <= month_A_idx < ATHDateTimeInterface.MXY_CALENDAR): 
            return None 
        
        try:
            month_A_name = ATHDateTimeInterface.MONTH_NAMES[month_A_idx]
            # from_components usa la logica del CALENDARIO
            return ATHDateTime.from_components(
                year, month_A_name, day_A_in_month,
                self.hour, self.minute, self.second, # Mantiene l'ora originale
                ath_timezone_obj=self._ath_timezone_obj )
        except Exception: # Più generico per coprire errori imprevisti
            return None

    def set_time(self, hour: int, minute: int, second: int = 0) -> 'ATHDateTime':
        # La validazione dei limiti di ora, minuto, secondo avviene in from_components,
        # che usa HXD_CALENDAR, IXH, SXI.
        # Qui passiamo i componenti dell'ora del CALENDARIO.
        return ATHDateTime.from_components(
            self.year, self.month_name, self.day, # Mantiene la data originale
            int(hour), int(minute), int(second),
            ath_timezone_obj=self._ath_timezone_obj 
        )

    def set_timezone(self, timezone: Optional['ATHDateTimeZoneInterface']) -> 'ATHDateTime':
        if timezone is not None and not isinstance(timezone, ATHDateTimeZoneInterface):
            raise TypeError("Il parametro 'timezone' deve essere un'istanza di ATHDateTimeZoneInterface o None.")
        return ATHDateTime(earth_date=self._earth_datetime_origin_utc, ath_timezone_obj=timezone)

    def set_timezone_by_name(self, timezone_name: Optional[str]) -> 'ATHDateTime':
        if timezone_name is None: return self.set_timezone(None)
        if not isinstance(timezone_name, str):
            raise TypeError("Il nome del fuso orario deve essere una stringa o None.")
        try:
            tz_obj: Optional['ATHDateTimeZoneInterface'] = ATHDateTimeZone(timezone_name) 
            return self.set_timezone(tz_obj)
        except ValueError as e: 
            raise ValueError(f"Impossibile impostare fuso orario: {timezone_name} - {e}")

    def to_array_state(self) -> dict:
        return {
            'year': self.year, 'month_name': self.month_name, 'day': self.day,
            'hour': self.hour, 'minute': self.minute, 'second': self.second,
            'ath_timezone_name': self._ath_timezone_obj.get_name() if self._ath_timezone_obj else None
        }

    def __repr__(self) -> str:
        # Usa le proprietà pubbliche per la rappresentazione
        tz_repr = f", timezone='{self.get_timezone().get_name()}'" if self.get_timezone() else "" #type: ignore
        return (f"ATHDateTime(Y={self.year},M={self.month_name},D={self.day}, "
                f"H={self.hour},Min={self.minute},S={self.second}{tz_repr}) "
                f"[EarthTS: {self._earth_timestamp_origin:.0f}]")

    def __str__(self) -> str:
        return self.format(self.FORMAT_DEFAULT)