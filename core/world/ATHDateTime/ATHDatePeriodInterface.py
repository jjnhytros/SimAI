# simai/core/world/ATHDatePeriodInterface.py

from abc import ABC, abstractmethod
from typing import Optional, Union, Iterator, TYPE_CHECKING
from collections.abc import Iterable # Per IteratorAggregate -> Iterable

if TYPE_CHECKING:
    from .ATHDateTimeInterface import ATHDateTimeInterface
    from .ATHDateInterval import ATHDateInterval

class ATHDatePeriodInterface(Iterable['ATHDateTimeInterface'], ABC): # Implementa Iterable
    """
    Interfaccia per rappresentare un periodo di tempo e iterare su di esso.
    Ispirata a DatePeriod di PHP.
    """

    # Costanti per le opzioni di costruzione
    EXCLUDE_START_DATE: int = 1
    INCLUDE_END_DATE: int = 2 # Utile se si usa una data di fine

    @property
    @abstractmethod
    def start_date(self) -> 'ATHDateTimeInterface': pass
    @property
    @abstractmethod
    def current_date(self) -> Optional['ATHDateTimeInterface']: pass
    @property
    @abstractmethod
    def end_date(self) -> Optional['ATHDateTimeInterface']: pass
    @property
    @abstractmethod
    def date_interval(self) -> 'ATHDateInterval': pass
    @property
    @abstractmethod
    def recurrences(self) -> Optional[int]: pass

    @classmethod
    @abstractmethod
    def create_from_iso_rrule_string(cls, iso_rrule_string: str, options: int = 0) -> 'ATHDatePeriodInterface': pass
    @abstractmethod
    def get_date_interval(self) -> 'ATHDateInterval': pass
    @abstractmethod
    def get_end_date(self) -> Optional['ATHDateTimeInterface']: pass
    @abstractmethod
    def get_recurrences(self) -> Optional[int]: pass
    @abstractmethod
    def get_start_date(self) -> 'ATHDateTimeInterface': pass
    @abstractmethod
    def __iter__(self) -> Iterator['ATHDateTimeInterface']: pass