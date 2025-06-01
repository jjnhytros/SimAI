# simai/core/world/ATHDateTimeInterface.py

from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta # timedelta è per il tipo di ritorno di diff
from typing import List, Dict, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .ATHDateInterval import ATHDateInterval
    from .ATHDateTimeZoneInterface import ATHDateTimeZoneInterface

class ATHDateTimeInterface(ABC):
    """
    Interfaccia astratta che definisce il contratto per gli oggetti data/ora Anthaleja.
    Ispirata a DateTimeInterface di PHP.
    """

    # --- COSTANTI CALENDARIO ANTHALEJANO (PLACEHOLDER/SEMPLIFICATE) ---
    HXD_CALENDAR: int = 28          # Ore per giorno nel CALENDARIO
    IXH: int = 60                   # Minuti Anthalejani in un'ora Anthalejana (uguale per calendario e astronomia)
    SXI: int = 60                   # Secondi Anthalejani in un minuto Anthalejano (uguale per calendario e astronomia)
    
    SXD_CALENDAR: int = HXD_CALENDAR * IXH * SXI # Secondi in un giorno CALENDARIALE (100800)

    DXM: int = 24                   # Giorni Anthalejani in un mese CALENDARIALE
    MXY: int = 18                   # Mesi Anthalejani in un anno CALENDARIALE
    DXY_CALENDAR: int = MXY * DXM     # Giorni Anthalejani in un anno CALENDARIALE (432)

    DXW: int = 7                    # Giorni Anthalejani in una settimana CALENDARIALE

    # --- COSTANTI ASTRONOMICHE PRECISE (basate sulla fisica del pianeta) ---
    HXD_ASTRONOMICAL: float = 27.99951264782  # Durata precisa di un giorno Anthalejano in ore terrestri
    # IXH e SXI sono assunti uguali a quelli del calendario
    SXD_ASTRONOMICAL: float = HXD_ASTRONOMICAL * IXH * SXI # Secondi terrestri in un giorno Anthalejano REALE

    # Durata di un anno CALENDARIALE (432 giorni) espressa in secondi ASTRONOMICI REALI
    CALENDAR_YEAR_IN_ASTRONOMICAL_SECONDS: float = DXY_CALENDAR * SXD_ASTRONOMICAL

    # Periodo Orbitale Fisico di Anthaleja (ORA ALLINEATO CON DXY_CALENDAR)
    # Definiamo che l'orbita dura esattamente 432 giorni Anthalejani REALI.
    ORBITAL_PERIOD_EARTH_SECONDS: float = DXY_CALENDAR * SXD_ASTRONOMICAL
    
    # Periodo orbitale fisico espresso in giorni Anthalejani REALI
    # Questo ora sarà uguale a DXY_CALENDAR (cioè 432.0)
    EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS: float = ORBITAL_PERIOD_EARTH_SECONDS / SXD_ASTRONOMICAL

    MONTH_NAMES: List[str] = ['Arejal', 'Brukom', 'Ĉelal', 'Kebor', 'Duvol', 'Elumag', 'Fydrin', 'Ĝinuril', 'Itrekos', 'Jebrax', 'Letranat', 'Mulfus', 'Nylumer', 'Otlevat', 'Prax', 'Retlixen', 'Sajep', 'Xetul']
    DAY_NAMES: List[str] = ['Nijahr', 'Majahr', 'Bejahr', 'Ĉejahr', 'Dyjahr', 'Fejahr', 'Ĝejahr']
    MONTH_ABBR: Dict[str, str] = {name: (name[:2] + 'x' if name == "Prax" else name[:3]) for name in MONTH_NAMES}
    DAY_ABBR_ATH: Dict[str, str] = {name: name[:3] for name in DAY_NAMES}
    
    RDN_UNIX_TS: int = 951584400 
    SECONDS_IN_ANTHAL_UP_TO_RDN_YEAR_START: int = 5775 * (DXY_CALENDAR * SXD_CALENDAR)
    EPOCH: int = RDN_UNIX_TS - SECONDS_IN_ANTHAL_UP_TO_RDN_YEAR_START
    FORMAT_DEFAULT: str = "Y, d/M_ABBR H_ATH_NP:ii:ss"
    FORMAT_ATOM: str = "Y-MM-DDTHH_ATH:ii:ss"
    FORMAT_COOKIE: str = "DAY, DD-M_ABBR-Y HH_ATH:ii:ss"
    FORMAT_ISO8601: str = "Y-MM-DDTHH_ATH:ii:ss"
    FORMAT_ISO8601_EXPANDED: str = "Y-MM-DDTHH_ATH:ii:ss.uu" # .uu per millisecondi
    FORMAT_RFC822: str = "D_ABBR, DD M_ABBR YY HH_ATH:ii:ss ATH_OFFSET_S_COLON" # Aggiunto offset
    FORMAT_RFC2822: str = "D_ABBR, DD M_ABBR Y HH_ATH:ii:ss ATH_OFFSET_S_COLON" # Aggiunto offset
    FORMAT_RFC3339 = "Y-MM-DDTHH_ATH:ii:ss" 
    FORMAT_RFC3339_EXTENDED = "Y-MM-DDTHH_ATH:ii:ss.uu"
    FORMAT_RSS = "D_ABBR, DD M_ABBR Y HH_ATH:ii:ss"
    FORMAT_W3C = "Y-MM-DDTHH_ATH:ii:ss"
    
    @abstractmethod
    def __init__(self, earth_date: Optional[datetime] = None, 
                ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None) -> None: pass
    
    @classmethod
    @abstractmethod
    def from_components(cls, year: int, month_name: str, day: int, # Rinominato e parametri aggiornati
                        hour: int = 0, minute: int = 0, second: int = 0,
                        ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None) -> 'ATHDateTimeInterface': pass
    
    @classmethod
    @abstractmethod
    def create_from_format(cls, format_string: str, datetime_string: str, # Rinominato e parametri aggiornati
                        ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None) -> 'ATHDateTimeInterface | None': pass # Optional
    
    @classmethod
    @abstractmethod
    def from_rdn_offset_seconds(cls, rdn_offset_seconds: int, 
                                ath_timezone_obj: Optional['ATHDateTimeZoneInterface'] = None) -> 'ATHDateTimeInterface': pass
    
    @classmethod
    @abstractmethod
    def from_array_state(cls, state_array: dict) -> 'ATHDateTimeInterface': pass

    @abstractmethod
    def format(self, format_string: str) -> str: pass
    @abstractmethod
    def get_earth_timestamp(self) -> int: pass
    @abstractmethod
    def add(self, interval: 'ATHDateInterval') -> 'ATHDateTimeInterface': pass
    @abstractmethod
    def sub(self, interval: 'ATHDateInterval') -> 'ATHDateTimeInterface': pass
    @abstractmethod
    def diff(self, target_object: 'ATHDateTimeInterface', absolute: bool = False) -> 'ATHDateInterval': pass
    @abstractmethod
    def modify(self, modifier_string: str) -> 'ATHDateTimeInterface | None': pass # Optional
    
    @abstractmethod
    def set_date(self, year: int, month_input: Union[str, int], day: int) -> 'ATHDateTimeInterface': pass # Rinominato
    
    @abstractmethod
    def set_week_date(self, year: int, week: int, day_of_week: int = 1) -> 'ATHDateTimeInterface | None': pass # Rinominato, Optional
    
    @abstractmethod
    def set_time(self, hour: int, minute: int, second: int = 0) -> 'ATHDateTimeInterface': pass # Rinominato
    
    @abstractmethod
    def set_timezone(self, timezone: Optional['ATHDateTimeZoneInterface']) -> 'ATHDateTimeInterface': pass
    
    @abstractmethod
    def set_timezone_by_name(self, timezone_name: Optional[str]) -> 'ATHDateTimeInterface': pass # Rinominato
    
    @abstractmethod
    def get_timezone(self) -> Optional['ATHDateTimeZoneInterface']: pass
    
    @abstractmethod
    def to_array_state(self) -> dict: pass

    @abstractmethod
    def __str__(self) -> str: pass

    @abstractmethod
    def __repr__(self) -> str: pass

    @property
    @abstractmethod
    def year(self) -> int: pass

    @property
    @abstractmethod
    def month_name(self) -> str: pass
    
    @property
    @abstractmethod
    def month_index(self) -> int: pass

    @property
    @abstractmethod
    def day(self) -> int: pass
    
    @property
    @abstractmethod
    def day_of_week_name(self) -> str: pass

    @property
    @abstractmethod
    def hour(self) -> int: pass

    @property
    @abstractmethod
    def minute(self) -> int: pass

    @property
    @abstractmethod
    def second(self) -> int: pass

    @property
    @abstractmethod
    def seconds_since_A_epoch(self) -> float: pass
