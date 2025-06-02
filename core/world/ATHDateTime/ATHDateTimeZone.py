# simai/core/world/ATHDateTimeZone.py

from typing import Dict, List, Optional, Union
from datetime import timedelta # per type hinting e calcoli differenza

from .ATHDateTimeZoneInterface import ATHDateTimeZoneInterface
from .ATHDateTimeInterface import IXH_CALENDAR, SXI_CALENDAR 


class ATHDateTimeZone(ATHDateTimeZoneInterface):
    _ANTHALEJA_TIMEZONE_DB_VERSION = "1.0.0-anthal"
    """
    Implementazione concreta di ATHDateTimeZoneInterface per i fusi orari Anthalejani.
    """
    # Dati placeholder per i fusi orari di Anthal.
    # 'offset_seconds_from_atz': Offset in secondi da ATZ.
    # 'group': Uno dei flag definiti in ATHDateTimeZoneInterface.
    # 'location': Un dizionario descrittivo.
    # 'abbrs': Possibili abbreviazioni.
    _timezones_data: Dict[str, Dict[str, Union[int, List[str], Dict[str, Union[str, float, int, None]], None]]] = {
        "ATZ": { 
            "offset_seconds_from_atz": 0, 
            "group": ATHDateTimeZoneInterface.ATZ | ATHDateTimeZoneInterface.ANTHAL,
            "location": {"country_code_A": "ANTHAL_N", "latitude_A": 12.0, "longitude_A": 0.0, "comments_A": "Anthalys, Meridiano di Riferimento Anthalejano"},
            "abbrs": ["ATZ", "AMT"] # Anthal Meridian Time
        },
        "Anthal/Meridia": { # Come da tua definizione precedente
            "offset_seconds_from_atz": 0,
            "group": ATHDateTimeZoneInterface.ANTHAL,
            "location": {"country_code_A": "ANTHAL_N", "latitude_A": 12.0, "longitude_A": 0.0, "comments_A": "Capitale di Anthal, su Meridiano Zero"},
            "abbrs": ["AMT", "AMST"] # Anthal Meridia Standard/Summer Time (placeholder per DST)
        },
        "Anthal/CostaEst": {
            "offset_seconds_from_atz": +1 * IXH_CALENDAR * SXI_CALENDAR, # +3600s
            "group": ATHDateTimeZoneInterface.ANTHAL,
            "location": {"country_code_A": "ANTHAL_E_REG", "latitude_A": None, "longitude_A": None, "comments_A": "Regioni Costiere Orientali di Anthal"},
            "abbrs": ["AET1"] # Anthal Eastern Time +1
        },
        "Anthal/MontagneOvest": {
            "offset_seconds_from_atz": -1 * IXH_CALENDAR * SXI_CALENDAR, # -3600s
            "group": ATHDateTimeZoneInterface.ANTHAL, 
            "location": {"country_code_A": "PIXINA", "latitude_A": None, "longitude_A": None, "comments_A": "Regioni Montuose Occidentali / Pixina Orientale"},
            "abbrs": ["AWT1"] # Anthal Western Time -1
        },
        "Anthal/Est+2": {
            "offset_seconds_from_atz": +2 * IXH_CALENDAR * SXI_CALENDAR,
            "group": ATHDateTimeZoneInterface.ANTHAL,
            "location": {"country_code_A": "ANTHAL_FE", "latitude_A": None, "longitude_A": None, "comments_A": "Estremo Oriente di Anthal"},
            "abbrs": ["AET2"]
        },
        "Anthal/Ovest-2": {
            "offset_seconds_from_atz": -2 * IXH_CALENDAR * SXI_CALENDAR,
            "group": ATHDateTimeZoneInterface.ANTHAL,
            "location": {"country_code_A": "PIXINA_W", "latitude_A": None, "longitude_A": None, "comments_A": "Estremo Occidente di Anthal"},
            "abbrs": ["AWT2"]
        },
        "Oceano/ProfondoBlu": { 
            "offset_seconds_from_atz": -5 * IXH_CALENDAR * SXI_CALENDAR,
            "group": ATHDateTimeZoneInterface.OCEAN,
            "location": {"country_code_A": "OCEAN_DB", "latitude_A": None, "longitude_A": None, "comments_A": "Fascia Oceanica Profondo Blu"},
            "abbrs": ["OPBT"]
        }
    }

    def __init__(self, timezone_identifier: str) -> None:
        normalized_identifier = timezone_identifier
        if normalized_identifier not in self._timezones_data:
            raise ValueError(f"Fuso orario Anthalejano non riconosciuto: {timezone_identifier}")
        self._identifier: str = normalized_identifier
        self._data = self._timezones_data[normalized_identifier]

    def get_location(self) -> Union[Dict[str, Union[str, float, int, None]], bool]:
        loc_data = self._data.get("location")
        if isinstance(loc_data, dict):
            return {
                "country_code_A": loc_data.get("country_code_A"),
                "latitude_A": loc_data.get("latitude_A"),
                "longitude_A": loc_data.get("longitude_A"),
                "comments_A": loc_data.get("comments_A")
            }
        return False

    def get_name(self) -> str:
        """Restituisce il nome dell'identificatore del fuso orario."""
        return self._identifier

    def get_offset(self, datetime_obj: 'ATHDateTimeInterface') -> int:
        """
        Restituisce l'offset del fuso orario da ATZ in secondi.
        Per ora, l'offset è fisso e datetime_obj non viene utilizzato.
        """
        # Il type hint per datetime_obj usa ATHDateTimeInterface_hint per evitare import circular
        # se ATHDateTimeInterface importasse ATHDateTimeZone.
        # In questo momento, ATHDateTimeInterface non usa direttamente ATHDateTimeZoneInterface
        # nei suoi type hints, ma è buona norma.
        
        offset_val = self._data.get("offset_seconds_from_atz")
        if isinstance(offset_val, int):
            return offset_val
        # Fallback ragionevole o errore se il dato è malformato
        # Per ora, assumiamo che i dati siano corretti e l'offset sia sempre un int.
        # Considerare di sollevare un'eccezione se l'offset non è un intero valido.
        return 0 

    def get_transitions(self, timestamp_begin: int = -250000000000, timestamp_end: int = 250000000000) -> List[Dict[str, Union[str, int, bool]]]:
        """
        Restituisce le transizioni del fuso orario (es. per ora legale) 
        in un dato intervallo di timestamp Unix.
        Per Anthal, attualmente non ci sono transizioni definite (no DST),
        quindi restituisce sempre una lista vuota.
        """
        # I parametri timestamp_begin e timestamp_end sono presenti per compatibilità
        # con l'interfaccia PHP, ma non sono usati nella logica attuale
        # dato che non ci sono transizioni definite nel sistema Anthaleja.
        return []

    @staticmethod
    def list_abbreviations() -> Dict[str, List[Dict[str, Union[str, int, bool]]]]:
        """
        Restituisce un dizionario di abbreviazioni dei fusi orari Anthalejani.
        Le chiavi sono le abbreviazioni (es. "AMT").
        I valori sono liste di dizionari, ognuno con 'offset', 'dst' (sempre False), 'timezone_id'.
        """
        abbreviations: Dict[str, List[Dict[str, Union[str, int, bool]]]] = {}
        
        # Accediamo a _timezones_data come attributo di classe
        for tz_name, tz_data in ATHDateTimeZone._timezones_data.items():
            offset_val = tz_data.get("offset_seconds_from_atz")
            #mypy: Value of type "Optional[Union[int, List[str], Dict[str, Union[str, float, int, None]], None]]" is not indexable
            #mypy: Argument 1 to "get" of "dict" has incompatible type "str"; expected "Union[int, List[str], Dict[str, Union[str, float, int, None]], None]"
            abbr_list_val = tz_data.get("abbrs") # type: ignore

            offset = offset_val if isinstance(offset_val, int) else 0
            abbr_list = abbr_list_val if isinstance(abbr_list_val, list) else []

            for abbr_item in abbr_list:
                abbr_str = str(abbr_item) # Assicura che sia una stringa
                if abbr_str not in abbreviations:
                    abbreviations[abbr_str] = []
                
                abbreviations[abbr_str].append({
                    "dst": False, # Anthal attualmente non ha DST
                    "offset": offset,
                    "timezone_id": tz_name 
                })
        return abbreviations

    @staticmethod
    def list_identifiers(timezone_group: int = ATHDateTimeZoneInterface.ALL, 
                        country_code: Optional[str] = None) -> List[str]:
        """
        Restituisce una lista di identificatori di fuso orario, opzionalmente filtrati.
        """
        # Se non ci sono filtri, restituisce tutti gli identificatori
        if timezone_group == ATHDateTimeZoneInterface.ALL and country_code is None:
            return list(ATHDateTimeZone._timezones_data.keys())
        
        identifiers = []
        for name, data_tz in ATHDateTimeZone._timezones_data.items():
            # Filtro per gruppo (usa l'operatore bitwise AND '&')
            passes_group_filter = False
            if timezone_group == ATHDateTimeZoneInterface.ALL:
                passes_group_filter = True
            else:
                tz_group_val = data_tz.get("group")
                if tz_group_val is not None and isinstance(tz_group_val, int) and (tz_group_val & timezone_group):
                    passes_group_filter = True
            
            # Filtro per country_code (se fornito)
            passes_country_filter = False
            if country_code is None:
                passes_country_filter = True
            else:
                loc_data = data_tz.get("location")
                if isinstance(loc_data, dict) and loc_data.get("country_code_A") == country_code:
                    passes_country_filter = True
            
            if passes_group_filter and passes_country_filter:
                identifiers.append(name)
        return identifiers
