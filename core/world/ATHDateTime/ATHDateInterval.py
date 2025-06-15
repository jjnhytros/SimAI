# File: simai/core/world/ATHDateInterval.py
import re
from .ATHDateTimeInterface import ATHDateTimeInterface # Per le costanti SXD, DXY, ecc.
from typing import Optional, Tuple

class ATHDateInterval:
    """Rappresenta un intervallo di tempo (durata) nel calendario Anthaleja."""
    def __init__(self, 
                years: int = 0, months: int = 0, days: int = 0,  # Parametri rinominati
                hours: int = 0, minutes: int = 0, seconds: int = 0, 
                microseconds: int = 0, 
                invert: bool = False,
                from_string_info: Optional[Tuple[bool, str]] = None): 
        self.y = int(years)
        self.m = int(months)
        self.d = int(days)
        self.h = int(hours)
        self.i = int(minutes)
        self.s = int(seconds)
        self.f = float(microseconds) / 1_000_000 
        self.invert = bool(invert)
        self.from_string: bool = from_string_info[0] if from_string_info else False
        self.date_string: str | None = from_string_info[1] if from_string_info else None

    def total_earth_seconds(self) -> float:
        # Per accedere alle costanti, se ATHDateTimeInterface è importata nel modulo
        # che usa questa classe, o se sono definite globalmente.
        # Per ora, assumiamo che le costanti siano accessibili (es. tramite un import ATHDateTimeInterface)
        # from .ATHDateTimeInterface import ATHDateTimeInterface # Importazione locale
        total_seconds = 0.0
        total_seconds += self.s + self.f 
        total_seconds += self.i * ATHDateTimeInterface.SXI_CALENDAR # Secondi per Minuto (calendariale)
        total_seconds += self.h * ATHDateTimeInterface.IXH_CALENDAR * ATHDateTimeInterface.SXI_CALENDAR # Secondi per Ora (calendariale)
        total_seconds += self.d * ATHDateTimeInterface.SXD_CALENDAR 
        total_seconds += self.m * ATHDateTimeInterface.DXM_CALENDAR * ATHDateTimeInterface.SXD_CALENDAR
        total_seconds += self.y * ATHDateTimeInterface.DXY_CALENDAR * ATHDateTimeInterface.SXD_CALENDAR
        return -total_seconds if self.invert else total_seconds

    @property
    def total_days(self) -> float:
        """
        Calcola il numero totale di giorni Anthalejani equivalenti (basati sul calendario)
        nell'intervallo.
        """
        # Importazione locale, anche se potrebbe essere a livello di modulo
        # se ATHDateTimeInterface è usata in più metodi.
        from .ATHDateTimeInterface import ATHDateTimeInterface
        
        # total_earth_seconds() converte l'intervallo (definito in unità calendariali)
        # in secondi terrestri totali usando le costanti _CALENDAR.
        total_physical_seconds = self.total_earth_seconds()
        
        # Per ottenere il numero di "giorni Anthalejani" equivalenti,
        # dividiamo per la durata di un gi`orno del CALENDARIO Anthalejano.
        return total_physical_seconds / ATHDateTimeInterface.SXD_CALENDAR

    @classmethod
    def from_iso_duration_string(cls, duration_string: str) -> 'ATHDateInterval':
        # ... (logica invariata, ma i parametri passati a cls() alla fine saranno rinominati) ...
        if not isinstance(duration_string, str): raise TypeError("Durata deve essere stringa.")
        original_string = duration_string; invert = False
        if duration_string.startswith('-'): invert = True; duration_string = duration_string[1:]
        if not duration_string.startswith('P'): raise ValueError("Durata ISO non valida: manca 'P'.")
        duration_string = duration_string[1:]
        y,m,d,h,i,s,us = 0,0,0,0,0,0,0
        pattern = re.compile(r"(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:[.,]\d+)?)S)?)?")
        match = pattern.fullmatch(duration_string)
        if not match: raise ValueError(f"Formato durata ISO non valido: {original_string}")
        gs = match.groups()
        if gs[0]: y = int(gs[0]); 
        if gs[1]: m = int(gs[1]); 
        if gs[2]: d += int(gs[2]) * 7
        if gs[3]: d += int(gs[3]); 
        if gs[4]: h = int(gs[4]); 
        if gs[5]: i = int(gs[5])
        if gs[6]:
            s_val_str = gs[6].replace(',', '.'); parts = s_val_str.split('.')
            s = int(parts[0])
            if len(parts) > 1: us_str = parts[1][:6].ljust(6, '0'); us = int(us_str)
        return cls(years=y, months=m, days=d, hours=h, minutes=i, seconds=s, # Parametri rinominati
                microseconds=us, invert=invert, from_string_info=(True, original_string))

    @classmethod
    def from_relative_ath_string(cls, relative_string: str) -> 'ATHDateInterval':
        """
        Crea un ATHDateInterval da una stringa relativa in termini Anthalejani
        (es. "+10 giorni", "-3 mesi"). 
        Le unità riconosciute sono varianti di: anno, mese, giorno, ora, minuto, secondo.
        """
        original_string = relative_string
        mod_string = relative_string.lower().strip()
        
        # Pattern per "+/- N unità" 
        # Le unità possono essere singolari/plurali, in italiano o inglese base.
        unit_pattern = (
            # Anthaleja (forme specifiche e abbreviazioni prima)
            #r"nesdo(?:l|lix)|n|"   # Anno/i
            #r"ma(?:i|ix)|m|"       # Mese/i
            #r"ik(?:a|e)|i|"        # Settimana/e
            #r"jah(?:r|rix)|j|"     # Giorno/i
            #r"ki(?:a|e)|k|"        # Ora/e
            #r"reda(?:n|nix)|r|"    # Minuto/i
            #r"dilk(?:a|ax)|d|"     # Secondo/i
            r"nesdolix|nesdol|n|"  # Anno
            r"maix|mai|m|"         # Mese
            r"jahrix|jahr|j|"      # Giorno
            r"kie|kia|k|"          # Ora
            r"redanix|redan|r|"    # Minuto
            r"dilkax|dilka|d|"     # Secondo
            # Italiano generico
            r"ann(?:o|i)|"
            r"mes(?:e|i)|"
            r"giorn(?:o|i)|"
            r"or(?:a|e)|"          
            r"minut(?:o|i)|"
            r"second(?:o|i)|"
            # Inglese generico
            r"year(?:s)?|"
            r"month(?:s)?|"
            r"day(?:s)?|"
            r"hour(?:s)?|"
            r"minute(?:s)?|"
            r"second(?:s)?"
        )
        pattern_str = rf"([+-]?)(\d+)\s*({unit_pattern})\b"
        match = re.match(pattern_str, mod_string)
        
        if not match:
            raise ValueError(f"Stringa relativa non riconosciuta o formato non supportato: '{original_string}'")

        sign_str = match.group(1)       # Segno (+, -, o stringa vuota)
        value_str = match.group(2)      # Valore numerico come stringa
        unit_keyword = match.group(3)   # La parola chiave esatta per l'unità (es. "giorni", "month")
        
        value = int(value_str)
        invert = (sign_str == '-')
        
        # Inizializza tutti i componenti a zero
        years, months, days, hours, minutes, seconds, microseconds = 0,0,0,0,0,0,0
        
        # Assegna il valore al componente corretto in base alla parola chiave dell'unità
        if unit_keyword.startswith("ann") or unit_keyword.startswith("year"):
            years = value
        elif unit_keyword.startswith("mes") or unit_keyword.startswith("month"):
            months = value
        elif unit_keyword.startswith("giorn") or unit_keyword.startswith("day"):
            days = value
        elif unit_keyword.startswith("or") or unit_keyword.startswith("hour"):
            hours = value
        elif unit_keyword.startswith("minut"): # Cattura "minuto", "minuti", "minute", "minutes"
            minutes = value
        elif unit_keyword.startswith("second"): # Cattura "secondo", "secondi", "second", "seconds"
            seconds = value
        else:
            # Questo blocco non dovrebbe essere raggiunto se il regex ha funzionato correttamente
            # e ha catturato una delle unità valide.
            raise ValueError(f"Unità non riconosciuta '{unit_keyword}' nella stringa relativa: '{original_string}'")
        
        # Chiama il costruttore della classe con i componenti identificati.
        # microseconds sono 0 perché questo formato semplice non li gestisce.
        return cls(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds, 
                   microseconds=microseconds, invert=invert, from_string_info=(True, original_string))

    def format(self, format_spec: str) -> str:
        output = format_spec; sign_R = "+" if not self.invert else "-"; sign_r = "-" if self.invert else ""
        microseconds_int = int(round(self.f * 1_000_000))
        replacements = {
            "%%": "%", "%Y": str(self.y).zfill(2), "%y": str(self.y), "%M": str(self.m).zfill(2), "%m": str(self.m),
            "%D": str(self.d).zfill(2), "%d": str(self.d), "%H": str(self.h).zfill(2), "%h": str(self.h),
            "%I": str(self.i).zfill(2), "%i": str(self.i), "%S": str(self.s).zfill(2), "%s": str(self.s),
            "%F": str(microseconds_int).zfill(6), "%R": sign_R, "%r": sign_r,
        }
        output = output.replace("%%", "__PERCENT_LITERAL__")
        for code in sorted(replacements.keys(), key=len, reverse=True):
            if code == "%%": continue
            output = output.replace(code, replacements[code])
        return output.replace("__PERCENT_LITERAL__", "%")

    def __str__(self):
        if not any([self.y, self.m, self.d, self.h, self.i, self.s, self.f]): return "PT0S" 
        date_parts = []; time_parts = []; result = "P"
        if self.y: date_parts.append(f"{self.y}Y"); # ... (altre parti) ...
        seconds_str_part = ""
        if self.s != 0 or self.f != 0:
            total_s = self.s + self.f
            if total_s == int(total_s): seconds_str_part = f"{int(total_s)}S"
            else: formatted_s = f"{total_s:.6f}".rstrip('0'); seconds_str_part = f"{(formatted_s[:-1] if formatted_s.endswith('.') else formatted_s)}S"
        if seconds_str_part: time_parts.append(seconds_str_part)
        date_str = "".join(date_parts); time_str = "".join(time_parts)
        if date_str: result += date_str
        if time_str: result += "T" + time_str
        elif not date_str and not time_str: return "PT0S"
        elif not date_str and time_str: result = "PT" + time_str # Es. PT5S
        elif date_str and not time_str and result == "P": result = "P0D" # Per P senza nulla
        return f"{'-' if self.invert and result not in ['PT0S', 'P0D'] else ''}{result}"

    def __repr__(self):
        return (f"ATHDateInterval(years={self.y}, months={self.m}, days={self.d}, " # Rinominato
                f"hours={self.h}, minutes={self.i}, seconds={self.s}, "
                f"microseconds={int(round(self.f * 1_000_000))}, invert={self.invert})")
