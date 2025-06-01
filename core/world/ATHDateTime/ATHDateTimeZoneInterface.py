# simai/core/world/ATHDateTimeZoneInterface.py

from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional # Per type hinting più precisi

# È necessario poter fare riferimento a ATHDateTimeInterface per il type hint in getOffset
# ma questo creerebbe un'importazione circolare se ATHDateTimeInterface importasse anche questa.
# Usiamo una stringa per il type hint o un forward reference.
from .ATHDateTimeInterface import ATHDateTimeInterface # Non qui per evitare circular import

class ATHDateTimeZoneInterface(ABC):
    """
    Interfaccia per la gestione dei fusi orari nel sistema Anthaleja.
    Ispirata a DateTimeZone di PHP.
    """

    # Costanti per i gruppi di fusi orari (valori interi arbitrari)
    # Questi corrispondono a DateTimeZone:: PAESE, CONTINENTE, ETC...
    # Per Anthal, potremmo avere qualcosa di specifico.
    # Ho usato i tuoi nomi, ma dovremo assegnare valori interi unici.
    ANTHAL: int = 1
    OCEAN: int = 2
    ATZ: int = 4          # Anthal Time Zero (equivalente a UTC per Anthal)
    ALL: int = 2047       # Valore tipico per tutti i gruppi
    ALL_WITH_BC: int = 4095 # Include obsoleti/storici (meno rilevante per un conlang inizialmente)
    PER_COUNTRY: int = 16 # Esempio, da adattare se Anthal ha "paesi"

    @abstractmethod
    def __init__(self, timezone_identifier: str) -> None: pass
    @abstractmethod
    def get_location(self) -> Union[Dict[str, Union[str, float, int, None]], bool]: pass
    @abstractmethod
    def get_name(self) -> str: pass
    @abstractmethod
    def get_offset(self, datetime_obj: 'ATHDateTimeInterface') -> int: pass
    @abstractmethod
    def get_transitions(self, timestamp_begin: int = -250000000000, timestamp_end: int = 250000000000) -> List[Dict[str, Union[str, int, bool]]]: pass
    @staticmethod
    @abstractmethod
    def list_abbreviations() -> Dict[str, List[Dict[str, Union[str, int, bool]]]]: pass
    @staticmethod
    @abstractmethod
    def list_identifiers(timezone_group: int = ALL, country_code: Optional[str] = None) -> List[str]: pass