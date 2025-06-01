# simai/core/world/ATHDateTimeImmutable.py

from datetime import datetime, timezone, timedelta
from typing import Optional, Union, List, Dict, Type, TYPE_CHECKING # Rimosso TypeVar non più usato qui

# Import delle classi e interfacce necessarie
from .ATHDateTimeInterface import ATHDateTimeInterface
from .ATHDateTime import ATHDateTime # La nostra classe "base"
from .ATHDateInterval import ATHDateInterval
# ATHDateTimeZone sarà usata per i type hints e potenzialmente per l'istanza
if TYPE_CHECKING:
    from .ATHDateTimeZoneInterface import ATHDateTimeZoneInterface as ATHDateTimeZoneInterface_hint
    # Se ATHDateTimeZone fosse un'interfaccia a sé, si importerebbe quella.
    # Ma dato che ATHDateTimeZone è la nostra unica implementazione, va bene così.
else:
    # Per compatibilità runtime se TYPE_CHECKING è False, definiamo placeholder se necessario
    ATHDateTimeZoneInterface_hint = None 

# Non è più necessario _SelfATHDateTimeImmutable se usiamo 'ATHDateTimeImmutable' direttamente
# _SelfATHDateTimeImmutable = TypeVar("_SelfATHDateTimeImmutable", bound="ATHDateTimeImmutable")

class ATHDateTimeImmutable(ATHDateTime, ATHDateTimeInterface): # Eredita da ATHDateTime e ri-dichiara ATHDateTimeInterface
    """
    Versione immutabile di ATHDateTime.
    Tutti i metodi che sembrerebbero modificare la data/ora restituiscono 
    una nuova istanza di ATHDateTimeImmutable.
    La maggior parte della logica di calcolo è ereditata da ATHDateTime.
    """

    def __init__(self, 
                 earth_date: Optional[datetime] = None, 
                 ath_timezone_obj: Optional['ATHDateTimeZoneInterface_hint'] = None):
        super().__init__(earth_date, ath_timezone_obj)

    # --- Override dei Metodi Factory per restituire 'ATHDateTimeImmutable' ---

    @classmethod
    def from_components(cls, # cls qui è Type[ATHDateTimeImmutable]
                        year: int, month_name: str, day: int, 
                        hour: int = 0, minute: int = 0, second: int = 0,
                        ath_timezone_obj: Optional['ATHDateTimeZoneInterface_hint'] = None) -> 'ATHDateTimeImmutable':
        base_instance = ATHDateTime.from_components(year, month_name, day, 
                                                    hour, minute, second, 
                                                    ath_timezone_obj)
        return cls(base_instance._earth_datetime_origin_utc, base_instance.get_timezone())

    @classmethod
    def create_from_format(cls, 
                        format_string: str, datetime_string: str,
                        ath_timezone_obj: Optional['ATHDateTimeZoneInterface_hint'] = None
                        ) -> Optional['ATHDateTimeImmutable']:
        base_instance_or_none = ATHDateTime.create_from_format(format_string, datetime_string, ath_timezone_obj)
        if isinstance(base_instance_or_none, ATHDateTime):
            return cls(base_instance_or_none._earth_datetime_origin_utc, base_instance_or_none.get_timezone())
        return None

    @classmethod
    def from_rdn_offset_seconds(cls, 
                                rdn_offset_seconds: int,
                                ath_timezone_obj: Optional['ATHDateTimeZoneInterface_hint'] = None
                                ) -> 'ATHDateTimeImmutable':
        base_instance = ATHDateTime.from_rdn_offset_seconds(rdn_offset_seconds, ath_timezone_obj)
        return cls(base_instance._earth_datetime_origin_utc, base_instance.get_timezone())

    @classmethod
    def from_array_state(cls, state_array: dict) -> 'ATHDateTimeImmutable':
        base_instance = ATHDateTime.from_array_state(state_array)
        return cls(base_instance._earth_datetime_origin_utc, base_instance.get_timezone())
        
    # --- Override dei Metodi di "Modifica" per garantire ritorno di ATHDateTimeImmutable ---
    # La logica di calcolo è in ATHDateTime.add(), che restituisce ATHDateTime.
    # Qui "riavvolgiamo" il risultato in ATHDateTimeImmutable.

    def add(self, interval: ATHDateInterval) -> 'ATHDateTimeImmutable':
        new_base_instance = super().add(interval) 
        return self.__class__(new_base_instance._earth_datetime_origin_utc, new_base_instance.get_timezone())

    def sub(self, interval: ATHDateInterval) -> 'ATHDateTimeImmutable':
        new_base_instance = super().sub(interval)
        return self.__class__(new_base_instance._earth_datetime_origin_utc, new_base_instance.get_timezone())

    def modify(self, modifier_string: str) -> Optional['ATHDateTimeImmutable']:
        modified_base_or_none = super().modify(modifier_string)
        if isinstance(modified_base_or_none, ATHDateTime):
            return self.__class__(modified_base_or_none._earth_datetime_origin_utc, modified_base_or_none.get_timezone())
        return None

    def set_date(self, year: int, month_input: Union[str, int], day: int) -> 'ATHDateTimeImmutable':
        new_base_instance = super().set_date(year, month_input, day)
        return self.__class__(new_base_instance._earth_datetime_origin_utc, new_base_instance.get_timezone())

    def set_week_date(self, year: int, week: int, day_of_week: int = 1) -> Optional['ATHDateTimeImmutable']:
        new_base_or_none = super().set_week_date(year, week, day_of_week)
        if isinstance(new_base_or_none, ATHDateTime):
            return self.__class__(new_base_or_none._earth_datetime_origin_utc, new_base_or_none.get_timezone())
        return None

    def set_time(self, hour: int, minute: int, second: int = 0) -> 'ATHDateTimeImmutable':
        new_base_instance = super().set_time(hour, minute, second)
        return self.__class__(new_base_instance._earth_datetime_origin_utc, new_base_instance.get_timezone())

    def set_timezone(self, timezone: Optional['ATHDateTimeZoneInterface_hint']) -> 'ATHDateTimeImmutable':
        new_base_instance = super().set_timezone(timezone) 
        return self.__class__(new_base_instance._earth_datetime_origin_utc, new_base_instance.get_timezone())

    def set_timezone_by_name(self, timezone_name: Optional[str]) -> 'ATHDateTimeImmutable':
        new_base_instance = super().set_timezone_by_name(timezone_name)
        return self.__class__(new_base_instance._earth_datetime_origin_utc, new_base_instance.get_timezone())

    # --- Nuovi Metodi Statici da DateTimeImmutable ---
    @classmethod
    def create_from_interface(cls: Type['ATHDateTimeImmutable'],
                            dt_interface_obj: ATHDateTimeInterface) -> 'ATHDateTimeImmutable':
        if not isinstance(dt_interface_obj, ATHDateTimeInterface):
            raise TypeError("L'oggetto deve implementare ATHDateTimeInterface.")
        
        earth_ts = dt_interface_obj.get_earth_timestamp()
        original_tz = dt_interface_obj.get_timezone()
        earth_dt_utc = datetime.fromtimestamp(earth_ts, tz=timezone.utc)
        
        return cls(earth_date=earth_dt_utc, ath_timezone_obj=original_tz)

    @classmethod
    def create_from_mutable(cls: Type['ATHDateTimeImmutable'], 
                            mutable_object: ATHDateTime) -> 'ATHDateTimeImmutable': 
        if not isinstance(mutable_object, ATHDateTime):
            raise TypeError("L'oggetto deve essere un'istanza di ATHDateTime.")
        
        return cls(earth_date=mutable_object._earth_datetime_origin_utc, 
                ath_timezone_obj=mutable_object.get_timezone())

    @staticmethod
    def get_last_errors() -> Union[List[str], bool]: 
        return False

    # I metodi getter (format, get_offset, get_timestamp, get_timezone, diff, ecc.)
    # e i metodi speciali (__str__, __repr__, to_array_state) sono ereditati da ATHDateTime
    # e non necessitano di override qui, poiché leggono solo lo stato e
    # il loro comportamento è già appropriato.
