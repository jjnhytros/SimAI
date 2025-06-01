# simai/core/world/ATHDatePeriod.py

import re # Necessario per il parsing della stringa ISO
from typing import Optional, Union, Iterator, TYPE_CHECKING
from datetime import timezone, datetime

# Import delle classi e interfacce necessarie
if TYPE_CHECKING:
    from .ATHDateTime import ATHDateTime # Importa l'implementazione concreta per istanziare
    from .ATHDateInterval import ATHDateInterval
    from .ATHDateTimeInterface import ATHDateTimeInterface
else: 
    ATHDateTime = None
    ATHDateInterval = None
    ATHDateTimeInterface = None

from .ATHDateTimeInterface import ATHDateTimeInterface as BaseATHDateTimeInterface
from .ATHDateInterval import ATHDateInterval as BaseATHDateInterval
from .ATHDatePeriodInterface import ATHDatePeriodInterface


class ATHDatePeriod(ATHDatePeriodInterface):
    """
    Rappresenta un periodo di date/ore e permette l'iterazione.
    """
    # Opzioni per il costruttore
    # EXCLUDE_START_DATE = 1 (ereditata da ATHDatePeriodInterface)
    # INCLUDE_END_DATE = 2 (ereditata da ATHDatePeriodInterface)

    _start: 'BaseATHDateTimeInterface'
    _interval: 'BaseATHDateInterval'
    _end: Optional['BaseATHDateTimeInterface']
    _recurrences: Optional[int]
    _options: int
    _current_during_iteration: Optional['BaseATHDateTimeInterface'] # Per la proprietà 'current'

    def __init__(self, 
                start_date: 'BaseATHDateTimeInterface', 
                interval: 'BaseATHDateInterval', 
                end_or_recurrences: Union['BaseATHDateTimeInterface', int], 
                options: int = 0):
        global ATHDateTime, ATHDateInterval 
        if ATHDateTime is None: from .ATHDateTime import ATHDateTime
        if ATHDateInterval is None: from .ATHDateInterval import ATHDateInterval

        if not isinstance(start_date, ATHDateTime):
            raise TypeError("start_date deve essere un'istanza di ATHDateTime.")
        if not isinstance(interval, ATHDateInterval):
            raise TypeError("interval deve essere un'istanza di ATHDateInterval.")

        self._start = start_date
        self._interval = interval
        self._options = options
        self._current_during_iteration = None

        if isinstance(end_or_recurrences, int):
            if end_or_recurrences < 0:
                raise ValueError("Il numero di ricorrenze non può essere negativo.")
            self._recurrences = end_or_recurrences
            self._end = None
        elif isinstance(end_or_recurrences, ATHDateTime):
            self._end = end_or_recurrences
            self._recurrences = None
            # Controlli di validità per start/end/interval
            if self._start.get_earth_timestamp() > self._end.get_earth_timestamp() and self._interval.total_earth_seconds() >= 0:
                pass 
            elif self._start.get_earth_timestamp() < self._end.get_earth_timestamp() and self._interval.total_earth_seconds() < 0:
                pass
        else:
            raise TypeError("end_or_recurrences deve essere un intero (ricorrenze) o un oggetto ATHDateTime (data di fine).")

    @property
    def start_date(self) -> 'BaseATHDateTimeInterface': return self._start
    @property
    def current_date(self) -> Optional['BaseATHDateTimeInterface']: return self._current_during_iteration
    @property
    def end_date(self) -> Optional['BaseATHDateTimeInterface']: return self._end
    @property
    def date_interval(self) -> 'BaseATHDateInterval': return self._interval
    @property
    def recurrences(self) -> Optional[int]: return self._recurrences
        
    def get_start_date(self) -> 'BaseATHDateTimeInterface': return self._start
    def get_date_interval(self) -> 'BaseATHDateInterval': return self._interval
    def get_end_date(self) -> Optional['BaseATHDateTimeInterface']: return self._end
    def get_recurrences(self) -> Optional[int]: return self._recurrences

    def __iter__(self) -> Iterator['BaseATHDateTimeInterface']:
        current_dt = self._start
        if not (self._options & self.EXCLUDE_START_DATE):
            self._current_during_iteration = current_dt
            yield current_dt
        num_yielded_after_start = 0
        
        # Se recurrences è 0 e start è incluso, si produce solo lo start.
        # Se recurrences è 0 e start è escluso, non si produce nulla.
        if self._recurrences == 0 and not (self._options & self.EXCLUDE_START_DATE):
            return # Già prodotto lo start, 0 ricorrenze significa 0 applicazioni dell'intervallo
        if self._recurrences == 0 and (self._options & self.EXCLUDE_START_DATE):
            return # Niente da produrre
        count = 0
        while True:
            count +=1
            if self._recurrences is not None and count > 1000: # Safety break per recurrences infinite
                # print("Safety break per recurrences potenzialmente infinite senza end_date")
                break
            next_dt = current_dt.add(self._interval)
            if self._recurrences is not None:
                num_yielded_after_start += 1
                # Il numero di ricorrenze è il numero di volte che l'intervallo è applicato
                if num_yielded_after_start > self._recurrences :
                    break
            elif self._end is not None:
                next_ts = next_dt.get_earth_timestamp()
                end_ts = self._end.get_earth_timestamp()
                interval_seconds = self._interval.total_earth_seconds()
                if interval_seconds >= 0: # Intervallo positivo o zero
                    if next_ts > end_ts: break
                    if next_ts == end_ts and not (self._options & self.INCLUDE_END_DATE): break
                else: # Intervallo negativo
                    if next_ts < end_ts: break
                    if next_ts == end_ts and not (self._options & self.INCLUDE_END_DATE): break
            else:
                raise ValueError("ATHDatePeriod deve avere un numero di ricorrenze o una data di fine per l'iterazione.")
            current_dt = next_dt
            self._current_during_iteration = current_dt
            yield current_dt
        self._current_during_iteration = None

    @classmethod
    def create_from_iso_rrule_string(cls, iso_rrule_string: str, options: int = 0) -> 'ATHDatePeriod':
        """
        Crea un ATHDatePeriod da una stringa di ricorrenza ISO 8601.
        Formati supportati:
        - "R<ricorrenze>/<start_iso>/<periodo_iso>"
        - "<start_iso>/<periodo_iso>/<fine_iso>"
        Le date ISO sono interpretate come UTC.
        """
        global ATHDateTime, ATHDateInterval # Per accedere alle classi concrete
        if ATHDateTime is None: from .ATHDateTime import ATHDateTime
        if ATHDateInterval is None: from .ATHDateInterval import ATHDateInterval

        # Pattern per R<ricorrenze>/<start>/<periodo>
        # Es: R4/2012-07-01T00:00:00Z/P7D
        #    R indica ricorrenze, seguita da un numero.
        #    La data di inizio è una stringa ISO 8601.
        #    Il periodo è una stringa di durata ISO 8601 (P...).
        pattern_recurr = re.compile(
            r"R(\d*)/"                 # R<ricorrenze> (ricorrenze possono essere omesse per infinito, non supportato qui)
            r"([^/]+)/"                # <start_datetime_iso>
            r"(.+)"                    # <period_duration_iso>
        )

        # Pattern per <start>/<periodo>/<fine>
        # Es: 2023-01-01T00:00:00Z/P1D/2023-01-05T00:00:00Z
        pattern_start_end = re.compile(
            r"([^/]+)/"                # <start_datetime_iso>
            r"([^/]+)/"                # <period_duration_iso>
            r"(.+)"                    # <end_datetime_iso>
        )

        start_dt_obj: Optional[BaseATHDateTimeInterface] = None
        interval_obj: Optional[BaseATHDateInterval] = None
        end_or_rec: Union[BaseATHDateTimeInterface, int, None] = None

        match_recurr = pattern_recurr.fullmatch(iso_rrule_string)
        match_start_end = pattern_start_end.fullmatch(iso_rrule_string)

        if match_recurr:
            recurrences_str = match_recurr.group(1)
            start_iso_str = match_recurr.group(2)
            period_iso_str = match_recurr.group(3)

            if not recurrences_str: # R/ non è supportato, PHP richiede un numero o un end
                raise ValueError("Numero di ricorrenze mancante nel formato R.../.../...")
            
            recurrences = int(recurrences_str)
            
            # Converti stringhe ISO a oggetti ATHDateTime e ATHDateInterval
            # Assumiamo che le date ISO siano UTC.
            # create_from_earth_format usa strptime, che ha bisogno di un formato Python
            # Per le stringhe ISO 8601 standard, datetime.fromisoformat è più semplice.
            try:
                # PHP DateTime considera Z come UTC.
                # Python fromisoformat gestisce Z e offset +HH:MM
                start_earth_dt = datetime.fromisoformat(start_iso_str.replace('Z', '+00:00'))
                start_dt_obj = ATHDateTime(start_earth_dt) # Crea ATHDateTime da datetime terrestre
            except ValueError:
                raise ValueError(f"Formato data di inizio ISO non valido: {start_iso_str}")

            try:
                interval_obj = ATHDateInterval.from_iso_duration_string(period_iso_str)
            except ValueError:
                raise ValueError(f"Formato durata ISO non valido: {period_iso_str}")
            
            end_or_rec = recurrences

        elif match_start_end:
            start_iso_str = match_start_end.group(1)
            period_iso_str = match_start_end.group(2)
            end_iso_str = match_start_end.group(3)

            try:
                start_earth_dt = datetime.fromisoformat(start_iso_str.replace('Z', '+00:00'))
                start_dt_obj = ATHDateTime(start_earth_dt)
            except ValueError:
                raise ValueError(f"Formato data di inizio ISO non valido: {start_iso_str}")

            try:
                interval_obj = ATHDateInterval.from_iso_duration_string(period_iso_str)
            except ValueError:
                raise ValueError(f"Formato durata ISO non valido: {period_iso_str}")

            try:
                end_earth_dt = datetime.fromisoformat(end_iso_str.replace('Z', '+00:00'))
                end_dt_obj = ATHDateTime(end_earth_dt)
                end_or_rec = end_dt_obj
            except ValueError:
                raise ValueError(f"Formato data di fine ISO non valido: {end_iso_str}")
        else:
            raise ValueError(f"Formato stringa specifica ISO 8601 non riconosciuto: {iso_rrule_string}")

        if start_dt_obj is None or interval_obj is None or end_or_rec is None:
            # Questo non dovrebbe accadere se uno dei pattern matcha e non ci sono errori
            raise ValueError("Errore interno nel parsing della stringa ISO.")

        return cls(start_date=start_dt_obj, 
                interval=interval_obj, 
                end_or_recurrences=end_or_rec, 
                options=options)

    def __str__(self) -> str:
        # Una semplice rappresentazione, potrebbe essere migliorata
        s = f"ATHDatePeriod start: {self._start.format(ATHDateTime.FORMAT_DEFAULT)}"
        if self._interval:
            s += f", interval: {self._interval}"
        if self._end:
            s += f", end: {self._end.format(ATHDateTime.FORMAT_DEFAULT)}"
        elif self._recurrences is not None:
            s += f", recurrences: {self._recurrences}"
        if self._options & self.EXCLUDE_START_DATE: s += " (exclude start)"
        if self._options & self.INCLUDE_END_DATE and self._end : s += " (include end)"
        return s

    def __repr__(self) -> str:
        """Rappresentazione non ambigua dell'oggetto."""
        end_or_rec_repr: str
        if self._end is not None:
            end_or_rec_repr = f"{self._end!r}"
        elif self._recurrences is not None:
            end_or_rec_repr = str(self._recurrences)
        else:
            # Caso anomalo se né _end né _recurrences sono impostati, 
            # il costruttore dovrebbe prevenirlo.
            end_or_rec_repr = "None" 
            
        return (f"ATHDatePeriod(start_date={self._start!r}, interval={self._interval!r}, "
                f"end_or_recurrences={end_or_rec_repr}, options={self._options})")
