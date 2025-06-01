# simai/core/world/ath_helpers.py
"""
Modulo helper per funzioni astronomiche e di utilità per il sistema data/ora Anthaleja.

Questo modulo contiene:
- Importazioni necessarie e configurazione iniziale.
- Costanti globali e dizionari di parametri per i corpi celesti (Nijel, Anthal, Leea, Mirahn).
- Funzioni helper per calcoli astronomici (posizioni, eventi, fasi, eclissi).
- Funzioni di utility per la formattazione dell'output (es. la dashboard celeste).
- Funzioni che forniscono un'API simile a quelle date/time di PHP, adattate per Anthaleja.
Principi di Design per le Funzioni di Calcolo Astronomico:
- Distinzione tra costanti "calendariali" (per l'orologio e la rappresentazione del tempo
    basata su un giorno di ATHDateTimeInterface.HXD_CALENDAR ore) e costanti "astronomiche"
    (per la fisica orbitale e rotazionale precisa, basate su HXD_ASTRONOMICAL
    e periodi orbitali fisici).
- I calcoli tentano di raggiungere un buon livello di precisione astronomica,
    tenendo conto di fenomeni come l'eccentricità orbitale, l'equazione del tempo,
    la deriva del perielio, la precessione nodale delle lune, e le coordinate eclittiche 3D.
- Gli orari degli eventi sono generalmente restituiti in ATZ (Anthalys Time Zero)
    o nel fuso orario specificato dall'oggetto ATHDateTimeInterface di input.
"""

import re
import math
import time # Usato per time.time() in alcune funzioni helper di alto livello
from typing import Dict, Any, Optional, Union, List, Tuple, Type # Aggiunto Type per i classmethod
from datetime import datetime, timezone
# Importazioni dalle classi e interfacce definite localmente
from .ATHDateTime.ATHDateTimeInterface import ATHDateTimeInterface
from .ATHDateTime.ATHDateTime import ATHDateTime
from .ATHDateTime.ATHDateTimeImmutable import ATHDateTimeImmutable
from .ATHDateTime.ATHDateInterval import ATHDateInterval
from .ATHDateTime.ATHDateTimeZone import ATHDateTimeZone
from .ATHDateTime.ATHDateTimeZoneInterface import ATHDateTimeZoneInterface # Alias per type hint
# Importa la funzione per impostare/ottenere il default dal modulo di configurazione dedicato
from .ATHDateTime.ath_timezone_config import get_default_ath_timezone, set_default_ath_timezone as ath_date_default_timezone_set

# --- Variabile di Modulo per il Fuso Orario di Default Globale ---
# Questa variabile (`_current_default_ath_timezone_obj`) dovrebbe essere definita e
# inizializzata preferibilmente nel modulo 'ath_timezone_config.py' per centralizzare
# la gestione del fuso orario di default. Se definita qui, assicurarsi che
# ATHDateTimeZone sia già completamente definita.
# Il blocco try-except gestisce la sua inizializzazione.
_current_default_ath_timezone_obj: Optional[ATHDateTimeZoneInterface] = None
try:
    _current_default_ath_timezone_obj = ATHDateTimeZone("ATZ")
except ValueError as e_val:
    print(f"ATTENZIONE INIZIALIZZAZIONE (ath_helpers.py): Fuso orario di default ATZ non valido. "
        f"Verificare ATHDateTimeZone._timezones_data. Errore: {e_val}")
except Exception as e_gen:
    print(f"ATTENZIONE INIZIALIZZAZIONE (ath_helpers.py): Errore imprevisto con fuso di default ATZ: {e_gen}")

# --- Disponibilità Libreria Dateutil ---
# Controlla se la libreria 'python-dateutil' è disponibile per un parsing più flessibile
# delle stringhe di data terrestri nella funzione 'ath_date_parse'.
try:
    from dateutil import parser as dateutil_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    # Un avviso qui è utile se si prevede un uso intensivo di ath_date_parse con formati complessi.
    # print("Avviso (ath_helpers.py): Libreria 'python-dateutil' non trovata. "
    #       "La funzione ath_date_parse avrà capacità di parsing limitate a ISO 8601 base.")

# --- Costanti per le Opzioni di Visualizzazione della Dashboard ---
# Utilizzate come bitmask per controllare quali sezioni della dashboard astronomica vengono generate.
NIJEL_INFO: int = 1              # La Stella Primaria Nijel
BENTEROX_INFO: int = 2           # Implementazione Futura
PANTONEA_INFO: int = 4           # Implementazione Futura
ANTHAL_INFO: int = 8             # Informazioni sul pianeta Anthal
LEEA_INFO: int = 16              # Luna 1 di Anthal
MIRAHN_INFO: int = 32            # Luna 2 di Anthal
DOUBEILAN_INFO: int = 64         # Implementazione Futura (Pianeta 4)
MELEO_INFO: int = 128            # Implementazione Futura (Pianeta 5)
FASCIA_ASTEROIDI_INFO: int = 256 # Implementazione Futura
PONEA_INFO: int = 512            # Implementazione Futura (Pianeta 6)
LOPYR_INFO: int = 1024           # Implementazione Futura (Pianeta 7)
VYDEL_INFO: int = 2048           # Implementazione Futura (Pianeta 8)
ALL_INFO: int = NIJEL_INFO | ANTHAL_INFO | LEEA_INFO | MIRAHN_INFO

# --- Costanti Astronomiche e di Conversione Globali ---
# Epoca di riferimento per i parametri orbitali delle lune (timestamp Unix terrestre).
# Corrisponde al 1° giorno di Arejal, Anno 5775, 00:00:00 ATZ.
EPOCH_LUNAR_PARAMS_UNIX_TS: int = ATHDateTimeInterface.RDN_UNIX_TS

# Rifrazione atmosferica standard approssimata (in gradi).
# Usata per calcolare l'alba/tramonto considerando la deviazione della luce nell'atmosfera.
REFRACTION_DEG_COMMON: float = 0.58

# Fattori di conversione da unità astronomiche standard a metri.
AU_TO_METERS: float = 149597870700.0      # Unità Astronomica in metri
RSOL_TO_METERS: float = 695700000.0       # Raggio Solare in metri

# --- Dizionari dei Parametri per i Corpi Celesti ---
# NIJEL_PARAMS: Contiene i parametri fisici della stella Nijel.
NIJEL_PARAMS: Dict[str, Any] = {
    "name": "Nijel",
    "physical_radius_m": 1.13019660008202 * RSOL_TO_METERS, # R_star
    # Potremmo aggiungere qui la massa di Nijel o la sua luminosità se servissero per altri calcoli.
}

# ANTHAL_PARAMS: Contiene i parametri fisici di Anthal e i parametri della sua orbita attorno a Nijel.
ANTHAL_PARAMS: Dict[str, Any] = {
    "name": "Anthal",
    # Parametri Fisici di Anthal
    "physical_radius_m": 6714971.758,
    "flattening": (1 / 349.9307771),
    "axial_tilt_deg": 28.550432150493,       # ε (inclinazione assiale)
    
    # Parametri Orbitali di Anthal attorno a Nijel
    "eccentricity": (1 / 55.19049588),      # e
    "semi_major_axis_m": 1.33139851864811 * AU_TO_METERS, # a
    
    # Parametri per la Deriva e l'Orientamento del Perielio di Anthal
    "base_perihelion_days_after_arejal1": 4.006965972222222, # Giorno base del perielio (0-idx, CALIBRATO)
    "base_days_arejal1_past_winter_solstice": 4.0,           # Riferimento base per l'orientamento del solstizio (0-idx)
    "reference_year": 5775,                                  # Anno di riferimento per i parametri base
    "max_annual_perihelion_shift_s": 5.0,                    # Massimo scostamento annuale del perielio (s)
    "perihelion_shift_cycle_years": 15432                    # Periodo del ciclo di deriva del perielio (anni Anthaleja)
}

# Parametri orbitali per la luna Leea
LEEA_PARAMS: Dict[str, Any] = {
    "name": "Leea", 
    "P_s": 1133942.85762992,            # Periodo orbitale sidereo (secondi terrestri)
    "a_m": 258699455.189651,            # Semiasse maggiore dell'orbita lunare (metri)
    "R_phys_m": 51784.8647960295,       # Raggio fisico della luna (metri)
    "M0_deg": 129.439844960672,         # Anomalia Media (M₀) all'epoca (gradi)
    "e": 0.010514306412,                # Eccentricità (e) dell'orbita lunare
    "i_deg": 2.15412345691,             # Inclinazione orbitale (i) rispetto all'eclittica di Anthal (gradi)
    "omega0_deg": 317.328694056024,     # Argomento del Periasse (ω₀) all'epoca (CALIBRATO, gradi)
                                        # (Angolo dal nodo ascendente al periasse, nel piano orbitale della luna)
    "initial_ascending_node_lon_deg": 125.066905836354,             # Longitudine del Nodo Ascendente (Ω₀) all'epoca (gradi)
    "nodal_precession_rate_deg_per_anthaleja_year": -7.939771474583 # Tasso di precessione nodale (gradi/anno Anthaleja), negativo per retrograda
}

# Parametri orbitali per la luna Mirahn
MIRAHN_PARAMS: Dict[str, Any] = {
    "name": "Mirahn", 
    "P_s": 2411277.73430203,        # Periodo orbitale sidereo (secondi terrestri)
    "a_m": 430186792.121963,        # Semiasse maggiore dell'orbita lunare (metri)
    "R_phys_m": 2066009.27133688,   # Raggio fisico della luna (metri)
    "M0_deg": 72.535072414236,      # Anomalia Media (M₀) all'epoca (gradi)
    "e": 0.032100621872,            # Eccentricità (e) dell'orbita lunare
    "i_deg": 5.256598234885,        # Inclinazione orbitale (i) rispetto all'eclittica di Anthal (gradi)
    "omega0_deg": 30.678037284612,  # Argomento del Periasse (ω₀) all'epoca (MANTENUTO, gradi)
    "initial_ascending_node_lon_deg": 167.623342872972, # Longitudine del Nodo Ascendente (Ω₀) all'epoca (gradi)
    "nodal_precession_rate_deg_per_anthaleja_year": -15.794371529463 # Tasso di precessione nodale (gradi/anno Anthaleja), negativo per retrograda
}

# Dizionario aggregato per un facile accesso ai parametri delle lune
ALL_MOON_PARAMS: Dict[str, Dict[str, Any]] = {
    "Leea": LEEA_PARAMS,
    "Mirahn": MIRAHN_PARAMS
}

# --- Inizio Definizioni Funzioni Helper ---
# (Qui seguiranno le definizioni di solve_kepler_equation, 
#  calculate_angular_radius_deg, ecc., fino a format_ath_celestial_dashboard)
def ath_checkdate(
    month_input: Union[int, str], 
    day: int, 
    year: int
) -> bool:
    """
    Valida una data nel calendario Anthaleja.
    """
    # Validazione Anno
    if not isinstance(year, int):
        return False

    # Validazione Mese
    valid_month_number = -1
    if isinstance(month_input, int):
        if 1 <= month_input <= ATHDateTimeInterface.MXY: # Usa la costante dall'interfaccia
            valid_month_number = month_input
    elif isinstance(month_input, str):
        month_input_normalized = month_input.capitalize() if len(month_input) > 3 else month_input.lower()
        if month_input_normalized in ATHDateTimeInterface.MONTH_NAMES:
            valid_month_number = ATHDateTimeInterface.MONTH_NAMES.index(month_input_normalized) + 1
        else:
            for name, abbr in ATHDateTimeInterface.MONTH_ABBR.items():
                if abbr.lower() == month_input_normalized:
                    valid_month_number = ATHDateTimeInterface.MONTH_NAMES.index(name) + 1
                    break

    if valid_month_number == -1:
        return False

    # Validazione Giorno
    if not isinstance(day, int) or not (1 <= day <= ATHDateTimeInterface.DXM): # Usa la costante
        return False
    return True

def ath_date(format_string: str, earth_unix_timestamp: Optional[int] = None) -> str:
    """
    Formatta una data/ora Anthaleja, simile alla funzione date() di PHP.

    Args:
        format_string: La stringa di formato da usare (utilizza i codici definiti
                    in ATHDateTimeInterface, es. ATHDateTimeInterface.FORMAT_DEFAULT).
        earth_unix_timestamp: Un timestamp Unix Terrestre opzionale (secondi dall'epoca Unix).
                            Se None, viene usata l'ora corrente (interpretata come ATZ).

    Returns:
        La stringa della data/ora Anthaleja formattata.
    """
    dt_obj: ATHDateTime

    if earth_unix_timestamp is None:
        # Usa l'ora corrente. ATHDateTime() di default crea un oggetto basato su datetime.now(timezone.utc)
        # e se nessun fuso orario ATH è specificato, i suoi componenti sono calcolati come se fosse in ATZ.
        dt_obj = ATHDateTime() 
    else:
        # Crea un oggetto datetime Terrestre UTC a partire dal timestamp fornito
        earth_dt_utc = datetime.fromtimestamp(earth_unix_timestamp, tz=timezone.utc)
        # Crea l'oggetto ATHDateTime, che sarà in ATZ se non specificato diversamente
        dt_obj = ATHDateTime(earth_dt_utc) 
    
    return dt_obj.format(format_string)

def ath_date_add(
    ath_datetime_obj: ATHDateTimeInterface, 
    ath_date_interval_obj: ATHDateInterval
) -> ATHDateTimeInterface:
    """
    Aggiunge un ATHDateInterval a un oggetto ATHDateTimeInterface e 
    restituisce un nuovo oggetto ATHDateTimeInterface risultato.
    Alias funzionale per ath_datetime_obj.add(ath_date_interval_obj).

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface a cui aggiungere l'intervallo.
        ath_date_interval_obj: L'oggetto ATHDateInterval da aggiungere.

    Returns:
        Un nuovo oggetto ATHDateTimeInterface con l'intervallo aggiunto.
        
    Raises:
        TypeError: Se gli oggetti forniti non sono dei tipi corretti.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError("Il primo argomento (ath_datetime_obj) deve essere un'istanza che implementa ATHDateTimeInterface.")
    if not isinstance(ath_date_interval_obj, ATHDateInterval):
        raise TypeError("Il secondo argomento (ath_date_interval_obj) deve essere un'istanza di ATHDateInterval.")
        
    # Chiama il metodo add dell'oggetto.
    # L'interfaccia ATHDateTimeInterface.add() dichiara di restituire ATHDateTimeInterface.
    # Le implementazioni concrete (ATHDateTime, ATHDateTimeImmutable) restituiranno il loro tipo specifico.
    return ath_datetime_obj.add(ath_date_interval_obj)

def ath_date_create(
    datetime_input: Union[str, datetime, int, float, None] = "now", 
    ath_timezone_obj: Optional[ATHDateTimeZoneInterface] = None
) -> Optional[ATHDateTime]:
    """
    Crea un nuovo oggetto ATHDateTime, simile alla funzione date_create() di PHP.

    Args:
        datetime_input:
            - "now" (stringa, default) o None: crea un oggetto per l'ora corrente.
            - Un oggetto datetime di Python: lo usa per l'inizializzazione.
            - Un int o float: interpretato come timestamp Unix Terrestre (secondi dall'epoca UTC).
            - Una stringa di data/ora Terrestre in formato ISO 8601 comune 
            (es. "YYYY-MM-DDTHH:MM:SS" o "YYYY-MM-DD HH:MM:SS").
            Per formati Anthaleja specifici o altri formati terrestri, usare
            ATHDateTime.create_from_format() o ATHDateTime.create_from_earth_format().
        ath_timezone_obj: Un oggetto ATHDateTimeZone opzionale per l'istanza creata.
                        Se non fornito, l'oggetto ATHDateTime sarà in ATZ (o senza TZ esplicito).

    Returns:
        Un oggetto ATHDateTime o None in caso di fallimento nell'interpretazione dell'input.
    """
    try:
        if datetime_input is None or (isinstance(datetime_input, str) and datetime_input.lower() == "now"):
            # ATHDateTime() senza 'earth_date' usa datetime.now(timezone.utc)
            return ATHDateTime(earth_date=None, ath_timezone_obj=ath_timezone_obj)
            
        elif isinstance(datetime_input, datetime):
            return ATHDateTime(earth_date=datetime_input, ath_timezone_obj=ath_timezone_obj)
            
        elif isinstance(datetime_input, (int, float)): # Assume Unix timestamp
            earth_dt_utc = datetime.fromtimestamp(datetime_input, tz=timezone.utc)
            return ATHDateTime(earth_date=earth_dt_utc, ath_timezone_obj=ath_timezone_obj)
            
        elif isinstance(datetime_input, str):
            # Tentativo di parsing per stringhe ISO 8601 comuni (terrestri)
            # datetime.fromisoformat è abbastanza flessibile per YYYY-MM-DD[THH:MM[:SS[.ffffff]][Z or +/-HH:MM]]
            try:
                # Sostituisci lo spazio con T per formati come "YYYY-MM-DD HH:MM:SS"
                iso_string_standardized = datetime_input.replace(" ", "T")
                parsed_earth_dt = datetime.fromisoformat(iso_string_standardized)
                
                # fromisoformat può restituire un datetime naive se non c'è info TZ nella stringa.
                # ATHDateTime.__init__ gestisce la conversione a UTC se è naive.
                return ATHDateTime(earth_date=parsed_earth_dt, ath_timezone_obj=ath_timezone_obj)
            except ValueError:
                # Il formato non è un ISO standard riconosciuto da fromisoformat
                return None # Fallimento del parsing
            
    except Exception: # Qualsiasi altro errore durante la creazione
        return None
            
    return None # Tipo di input non gestito

def ath_date_create_from_format(
    format_string: str, 
    datetime_string: str,
    ath_timezone_obj: Optional[ATHDateTimeZoneInterface] = None
) -> Optional[ATHDateTime]:
    """
    Interpreta una stringa di data/ora Anthaleja secondo un formato specifico
    e crea un nuovo oggetto ATHDateTime.
    Alias funzionale per ATHDateTime.create_from_format().

    Args:
        format_string: La stringa di formato che descrive datetime_string
                    (deve usare i codici di formato Anthaleja come Y, MONTH, JJ, HH, ecc.).
        datetime_string: La stringa della data/ora Anthaleja da interpretare.
        ath_timezone_obj: Un oggetto ATHDateTimeZone opzionale.

    Returns:
        Un oggetto ATHDateTime in caso di successo, None altrimenti.
    """
    # Chiama il metodo di classe rinominato (create_from_format) di ATHDateTime
    # Questo metodo restituisce già Optional[ATHDateTime]
    return ATHDateTime.create_from_format(
        format_string=format_string,
        datetime_string=datetime_string,
        ath_timezone_obj=ath_timezone_obj
    )

def ath_date_create_immutable(
    datetime_input: Union[str, datetime, int, float, None] = "now", 
    ath_timezone_obj: Optional[ATHDateTimeZoneInterface] = None
) -> Optional[ATHDateTimeImmutable]:
    """
    Crea un nuovo oggetto ATHDateTimeImmutable, simile a date_create_immutable() di PHP.

    Args:
        datetime_input:
            - "now" (stringa, default) o None: crea un oggetto per l'ora corrente.
            - Un oggetto datetime di Python: lo usa per l'inizializzazione.
            - Un int o float: interpretato come timestamp Unix Terrestre (secondi dall'epoca UTC).
            - Una stringa di data/ora Terrestre in formato ISO 8601 comune.
        ath_timezone_obj: Un oggetto ATHDateTimeZone opzionale per l'istanza creata.

    Returns:
        Un oggetto ATHDateTimeImmutable o None in caso di fallimento.
    """
    try:
        if datetime_input is None or (isinstance(datetime_input, str) and datetime_input.lower() == "now"):
            # Il costruttore di ATHDateTimeImmutable accetta gli stessi argomenti di ATHDateTime
            return ATHDateTimeImmutable(earth_date=None, ath_timezone_obj=ath_timezone_obj) 
            
        elif isinstance(datetime_input, datetime):
            return ATHDateTimeImmutable(earth_date=datetime_input, ath_timezone_obj=ath_timezone_obj)
            
        elif isinstance(datetime_input, (int, float)): # Assume Unix timestamp
            earth_dt_utc = datetime.fromtimestamp(datetime_input, tz=timezone.utc)
            return ATHDateTimeImmutable(earth_date=earth_dt_utc, ath_timezone_obj=ath_timezone_obj)
            
        elif isinstance(datetime_input, str):
            # Tentativo di parsing per stringhe ISO 8601 comuni (terrestri)
            # Per un parsing più avanzato o formati specifici, si dovrebbero usare i metodi
            # ATHDateTimeImmutable.create_from_format() o .create_from_earth_format() (se esistesse).
            # Il metodo ATHDateTimeImmutable.create_from_ath_format è per stringhe Anthaleja.
            try:
                iso_string_standardized = datetime_input.replace(" ", "T")
                # Python 3.11+ gestisce 'Z' in fromisoformat. Per versioni precedenti,
                # una sostituzione di 'Z' con '+00:00' potrebbe essere più robusta se necessario.
                if iso_string_standardized.endswith('Z'):
                    iso_string_standardized = iso_string_standardized[:-1] + "+00:00"

                parsed_earth_dt = datetime.fromisoformat(iso_string_standardized)
                
                return ATHDateTimeImmutable(earth_date=parsed_earth_dt, ath_timezone_obj=ath_timezone_obj)
            except ValueError:
                return None # Parsing fallito
            
    except Exception: # Qualsiasi altro errore durante la creazione
        return None
            
    return None # Tipo di input non gestito

def ath_date_date_set(
    ath_datetime_obj: ATHDateTimeInterface, 
    year: int, 
    month_input: Union[str, int], 
    day: int
) -> ATHDateTimeInterface:
    """
    Imposta una nuova data su un oggetto ATHDateTimeInterface, mantenendo l'ora originale.
    Restituisce un nuovo oggetto ATHDateTimeInterface con la data modificata.
    Alias funzionale per ath_datetime_obj.set_date(year, month_input, day).

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface su cui basare la modifica.
        year: L'anno Anthaleja.
        month_input: Il mese Anthaleja (nome completo, abbreviazione come stringa, 
                    o indice numerico 1-18).
        day: Il giorno Anthaleja (1-24).

    Returns:
        Un nuovo oggetto ATHDateTimeInterface con la data impostata e l'ora originale.
        
    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
        ValueError: Se i componenti della data (anno, mese, giorno) non sono validi 
                    (sollevato dal metodo .set_date() sottostante).
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError("Il primo argomento (ath_datetime_obj) deve essere un'istanza che implementa ATHDateTimeInterface.")
    
    # Chiama il metodo set_date dell'oggetto.
    # Il metodo set_date in ATHDateTimeInterface è dichiarato per restituire ATHDateTimeInterface.
    # Le implementazioni concrete (ATHDateTime, ATHDateTimeImmutable) restituiranno il loro tipo specifico.
    return ath_datetime_obj.set_date(year, month_input, day)

def ath_date_default_timezone_get() -> str:
    """
    Restituisce l'identificatore del fuso orario Anthaleja considerato di default.

    Attualmente, il sistema Anthaleja non ha un default "impostabile" a livello globale.
    Le istanze di ATHDateTime create senza un fuso orario specifico
    sono effettivamente rappresentate in ATZ (Anthal Time Zero), che è il nostro
    fuso orario di riferimento (analogo a UTC).
    Questa funzione quindi restituisce "ATZ".
    """
    return "ATZ"

def ath_date_default_timezone_set(timezone_id: str) -> bool:
    """
    Imposta il fuso orario Anthaleja di default usato dalle funzioni data/ora.
    Simile a date_default_timezone_set() di PHP.

    Args:
        timezone_id_A: L'identificatore del fuso orario Anthaleja da impostare come default
                    (es. "ATZ", "Anthal/CostaEst").

    Returns:
        True in caso di successo, False se l'identificatore del fuso orario non è valido.
    """
    global _current_default_ath_timezone_obj # Permette di modificare la variabile di modulo
    try:
        new_default_tz = ATHDateTimeZone(timezone_id)
        _current_default_ath_timezone_obj = new_default_tz
        return True
    except ValueError: # Sollevato da ATHDateTimeZone.__init__ per ID non valido
        return False

def ath_date_diff(
    datetime_obj1: ATHDateTimeInterface,
    datetime_obj2: ATHDateTimeInterface,
    absolute: bool = False
) -> ATHDateInterval:
    """
    Calcola la differenza tra due oggetti ATHDateTimeInterface (datetime_obj1 - datetime_obj2)
    e restituisce un ATHDateInterval.
    Alias funzionale per datetime_obj1.diff(datetime_obj2, absolute).

    Args:
        datetime_obj1: Il primo oggetto ATHDateTimeInterface (il minuendo).
        datetime_obj2: Il secondo oggetto ATHDateTimeInterface (il sottraendo).
        absolute: Se True, l'intervallo restituito sarà sempre positivo.

    Returns:
        Un oggetto ATHDateInterval che rappresenta la differenza.
        
    Raises:
        TypeError: Se gli oggetti forniti non implementano ATHDateTimeInterface.
    """
    if not isinstance(datetime_obj1, ATHDateTimeInterface):
        raise TypeError("Il primo argomento (datetime_obj1) deve implementare ATHDateTimeInterface.")
    if not isinstance(datetime_obj2, ATHDateTimeInterface):
        raise TypeError("Il secondo argomento (datetime_obj2) deve implementare ATHDateTimeInterface.")
        
    return datetime_obj1.diff(datetime_obj2, absolute)

def ath_date_format(
    ath_datetime_obj: ATHDateTimeInterface, 
    format_string: str
) -> str:
    """
    Formatta un oggetto ATHDateTimeInterface secondo la stringa di formato fornita.
    Alias funzionale per ath_datetime_obj.format(format_string).

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface da formattare.
        format_string: La stringa di formato da usare (utilizza i codici definiti
                    in ATHDateTimeInterface e implementati in ATHDateTime.format(), 
                    es. Y, MONTH, JJ, HH, TZN).

    Returns:
        La stringa della data/ora Anthaleja formattata.
        
    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError("Il primo argomento (ath_datetime_obj) deve essere un'istanza che implementa ATHDateTimeInterface.")
    
    # Chiama il metodo format dell'oggetto.
    return ath_datetime_obj.format(format_string)

def ath_date_get_last_errors() -> Union[List[str], bool]:
    """
    Restituisce gli errori dall'ultima operazione di parsing di data/ora.
    Alias funzionale per ATHDateTimeImmutable.get_last_errors().

    Nel nostro sistema attuale, il parsing solleva eccezioni (ValueError, TypeError) 
    immediatamente piuttosto che accumulare errori. Pertanto, questo metodo, 
    per coerenza con la firma PHP e l'implementazione di 
    ATHDateTimeImmutable.get_last_errors(), restituisce False.
    """
    return ATHDateTimeImmutable.get_last_errors()

def ath_date_interval_create_from_date_string(relative_string: str) -> Optional[ATHDateInterval]:
    """
    Crea un oggetto ATHDateInterval da una stringa di data relativa.
    Alias funzionale per ATHDateInterval.from_relative_ath_string().

    Args:
        relative_string: La stringa che descrive la durata relativa
                        (es. "+2 giorni", "-1 mese", "3 ore", ecc., 
                        riconosce unità in Anthaleja, Italiano, Inglese).

    Returns:
        Un oggetto ATHDateInterval in caso di successo, None altrimenti (se la stringa
        non è parsabile o l'unità non è riconosciuta).
    """
    try:
        return ATHDateInterval.from_relative_ath_string(relative_string)
    except ValueError: # ATHDateInterval.from_relative_ath_string solleva ValueError
        return None

def ath_date_interval_format(
    ath_date_interval_obj: ATHDateInterval,
    format_spec: str
) -> str:
    """
    Formatta un oggetto ATHDateInterval secondo la stringa di formato specificata.
    Alias funzionale per ath_date_interval_obj.format(format_spec).

    Args:
        ath_date_interval_obj: L'oggetto ATHDateInterval da formattare.
        format_spec: La stringa di formato da usare (utilizza codici come 
                    %Y, %M, %D, %H, %I, %S, %F, %R, %r).

    Returns:
        La stringa dell'intervallo formattata.
        
    Raises:
        TypeError: Se ath_date_interval_obj non è un'istanza di ATHDateInterval.
    """
    if not isinstance(ath_date_interval_obj, ATHDateInterval):
        raise TypeError("Il primo argomento (ath_date_interval_obj) deve essere un'istanza di ATHDateInterval.")
    
    return ath_date_interval_obj.format(format_spec)

def ath_date_isodate_set(
    ath_datetime_obj: ATHDateTimeInterface,
    year: int,
    week: int,
    day_of_week: int = 1  # Default a 1 (Nijahr, il primo giorno della settimana ATH)
) -> Optional[ATHDateTimeInterface]:
    """
    Imposta la data su un oggetto ATHDateTimeInterface basandosi sull'anno Anthaleja,
    il numero della settimana e il giorno della settimana, mantenendo l'ora originale.
    Restituisce un nuovo oggetto ATHDateTimeInterface con la data modificata, 
    o None in caso di fallimento (es. settimana o giorno non validi).
    Alias funzionale per ath_datetime_obj.set_week_date(year, week, day_of_week).

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface da modificare.
        year: L'anno Anthaleja.
        week: Il numero della settimana Anthaleja all'interno dell'anno 
            (es. 1 per la prima settimana).
        day_of_week: Il giorno della settimana Anthaleja (1 per Nijahr, 
                    2 per Majahr, ..., 7 per Ĝejahr). Default a 1.

    Returns:
        Un nuovo oggetto ATHDateTimeInterface con la data impostata, 
        o None se i parametri della data settimanale non sono validi.
        
    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError("Il primo argomento (ath_datetime_obj) deve essere un'istanza che implementa ATHDateTimeInterface.")
    
    # Chiama il metodo set_week_date dell'oggetto.
    # Questo metodo in ATHDateTimeInterface è dichiarato per restituire Optional[ATHDateTimeInterface].
    return ath_datetime_obj.set_week_date(year, week, day_of_week)

def ath_date_modify(
    ath_datetime_obj: ATHDateTimeInterface,
    modifier_string: str
) -> Optional[ATHDateTimeInterface]:
    """
    Modifica un oggetto ATHDateTimeInterface in base alla stringa di modifica fornita.
    Restituisce un nuovo oggetto ATHDateTimeInterface con la modifica, o None in caso di fallimento.
    Alias funzionale per ath_datetime_obj.modify(modifier_string).

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface da modificare.
        modifier_string: La stringa che descrive la modifica relativa
                        (es. "+2 giorni", "embax", "milo Nijahr", "inizio mese").
                        Le unità e le parole chiave devono essere quelle riconosciute
                        dal metodo ATHDateTime.modify().

    Returns:
        Un nuovo oggetto ATHDateTimeInterface con la modifica applicata, 
        o None se la stringa di modifica non è riconosciuta o l'operazione fallisce.
        
    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError("Il primo argomento (ath_datetime_obj) deve essere un'istanza che implementa ATHDateTimeInterface.")
    
    # Chiama il metodo modify dell'oggetto.
    # Il metodo modify in ATHDateTimeInterface è dichiarato per restituire Optional[ATHDateTimeInterface].
    return ath_datetime_obj.modify(modifier_string)

def ath_date_offset_get(ath_datetime_obj: ATHDateTimeInterface) -> int:
    """
    Restituisce l'offset del fuso orario dell'oggetto ATHDateTimeInterface da ATZ, in secondi.
    Alias funzionale per una combinazione di ath_datetime_obj.get_timezone() 
    e ATHDateTimeZone.get_offset().

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface di cui ottenere l'offset.

    Returns:
        L'offset in secondi da ATZ. Se l'oggetto non ha un fuso orario esplicito
        (cioè è in ATZ), l'offset è 0.
        
    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError("L'argomento (ath_datetime_obj) deve essere un'istanza che implementa ATHDateTimeInterface.")
    
    timezone_obj = ath_datetime_obj.get_timezone()
    
    if timezone_obj:
        # Il metodo get_offset() in ATHDateTimeZone accetta un oggetto datetime
        # per future implementazioni di DST, anche se attualmente non lo usa
        # per calcolare l'offset fisso che abbiamo.
        return timezone_obj.get_offset(ath_datetime_obj)
    else:
        # Se non c'è un fuso orario esplicito, l'oggetto è considerato in ATZ,
        # che ha un offset di 0 da sé stesso.
        return 0

def ath_date_parse(datetime_string: str) -> Dict[str, Any]:
    """
    Interpreta una stringa di data/ora, riconoscendo sia formati Anthaleja che terrestri,
    e restituisce un dizionario di informazioni sulla data interpretata.
    Simile a date_parse() di PHP, ma esteso per il sistema Anthaleja e senza dipendenze esterne.

    La funzione tenta prima di interpretare la stringa usando formati comuni Anthaleja.
    Se fallisce, tenta di interpretarla usando formati terrestri comuni (es. ISO 8601).

    Args:
        datetime_string: La stringa di data/ora da interpretare (può essere in formato
                        Anthaleja o Terrestre).

    Returns:
        Un dizionario con i componenti della data, avvisi ed errori.
        Contiene sia i componenti terrestri ('year', 'month', etc.) sia quelli
        Anthaleja ('ath_year', 'ath_month_name', etc.), calcolati in modo incrociato.
    """
    # Struttura di base del risultato, simile a PHP date_parse
    result: Dict[str, Any] = {
        "year": None, "month": None, "day": None, "hour": None, "minute": None,
        "second": None, "fraction": 0.0, "warning_count": 0, "warnings": {},
        "error_count": 0, "errors": {}, "is_localtime": False, "zone_type": 0,
        "zone": "", "is_dst": False, "ath_year": None, "ath_month_name": None,
        "ath_month_index": None, "ath_day": None, "ath_hour": None,
        "ath_minute": None, "ath_second": None, "ath_day_of_week_name": None,
        "ath_timezone_name": "ATZ"
    }

    # --- TENTATIVO 1: PARSING COME DATA ANTHALEJA ---
    ath_formats_to_try = [
        "YYYY, MONTH JJ, HH:II:SS",
        "YYYY-NN-JJ HH:II:SS",
        "YYYY-NN-JJ",
    ]
    ath_dt_obj = None
    for fmt in ath_formats_to_try:
        try:
            parsed_obj = ATHDateTime.create_from_format(fmt, datetime_string)
            if parsed_obj:
                ath_dt_obj = parsed_obj
                break
        except Exception:
            continue

    if ath_dt_obj:
        # SUCCESSO: La stringa era una data Anthaleja. Popoliamo il dizionario.
        result["ath_year"] = ath_dt_obj.year
        result["ath_month_name"] = ath_dt_obj.month_name
        result["ath_month_index"] = ath_dt_obj.month_index
        result["ath_day"] = ath_dt_obj.day
        result["ath_hour"] = ath_dt_obj.hour
        result["ath_minute"] = ath_dt_obj.minute
        result["ath_second"] = ath_dt_obj.second
        result["ath_day_of_week_name"] = ath_dt_obj.day_of_week_name
        if (tz_obj := ath_dt_obj.get_timezone()) is not None:
            result["ath_timezone_name"] = tz_obj.get_name()

        earth_equivalent_dt = ath_dt_obj._earth_datetime_origin_utc
        result["year"] = earth_equivalent_dt.year
        result["month"] = earth_equivalent_dt.month
        result["day"] = earth_equivalent_dt.day
        result["hour"] = earth_equivalent_dt.hour
        result["minute"] = earth_equivalent_dt.minute
        result["second"] = earth_equivalent_dt.second
        result["fraction"] = earth_equivalent_dt.microsecond / 1_000_000.0
        return result

    # --- TENTATIVO 2: PARSING COME DATA TERRESTRE (FALLBACK) ---
    try:
        parsed_earth_dt = _parse_earth_datestring(datetime_string)

        # SUCCESSO: La stringa era una data Terrestre. Popoliamo il dizionario.
        result["year"] = parsed_earth_dt.year
        result["month"] = parsed_earth_dt.month
        result["day"] = parsed_earth_dt.day
        result["hour"] = parsed_earth_dt.hour
        result["minute"] = parsed_earth_dt.minute
        result["second"] = parsed_earth_dt.second
        result["fraction"] = parsed_earth_dt.microsecond / 1_000_000.0
        if parsed_earth_dt.tzinfo:
            result["is_localtime"] = True
            tz_offset = parsed_earth_dt.tzinfo.utcoffset(parsed_earth_dt)
            if tz_offset is not None:
                result["zone_type"] = 1
                result["zone"] = int(tz_offset.total_seconds() / 60)

        # Calcoliamo i dati Anthaleja equivalenti
        ath_dt_obj_from_earth = ATHDateTime(parsed_earth_dt)
        result["ath_year"] = ath_dt_obj_from_earth.year
        result["ath_month_name"] = ath_dt_obj_from_earth.month_name
        result["ath_month_index"] = ath_dt_obj_from_earth.month_index
        result["ath_day"] = ath_dt_obj_from_earth.day
        result["ath_hour"] = ath_dt_obj_from_earth.hour
        result["ath_minute"] = ath_dt_obj_from_earth.minute
        result["ath_second"] = ath_dt_obj_from_earth.second
        result["ath_day_of_week_name"] = ath_dt_obj_from_earth.day_of_week_name
        if (tz_obj := ath_dt_obj_from_earth.get_timezone()) is not None:
            result["ath_timezone_name"] = tz_obj.get_name()
        return result

    except ValueError as e:
        # Se entrambi i tentativi falliscono, restituiamo l'errore.
        result["error_count"] = 1
        result["errors"] = {0: f"La stringa non corrisponde a nessun formato noto. Errore: {e}"}
        return result

def ath_date_parse_from_format(ath_format_string: str, ath_datetime_string: str) -> Dict[str, Any]:
    """
    Interpreta una stringa di data/ora Anthaleja secondo un formato specifico
    e restituisce un dizionario con i componenti della data e informazioni su errori/avvisi.
    Simile a date_parse_from_format() di PHP, ma per date e formati Anthaleja.

    Args:
        ath_format_string: La stringa di formato che usa i codici Anthaleja
                        (es. Y, MONTH, Mon, NN, N, JJ, J, DAY, DayN, HH, G, II, I, SS, S).
        ath_datetime_string: La stringa della data/ora Anthaleja da interpretare.

    Returns:
        Un dizionario con i componenti della data interpretati (year, month, day, hour, 
        minute, second, month_name_A, day_of_week_name_A), più 
        warning_count, warnings, error_count, errors. 
        Se il parsing fallisce, i campi data saranno None e error_count > 0.
    """
    
    result: Dict[str, Any] = {
        "year": None, "month": None, "day": None, # Numero mese 1-18
        "hour": None, "minute": None, "second": None,
        "fraction": 0.0, # Attualmente non gestiamo frazioni di secondo nel parsing
        "warning_count": 0, "warnings": {},
        "error_count": 0, "errors": {},
        "is_localtime": False, # Concetto meno rilevante qui, dato che parsiamo una stringa
        "zone_type": 0, 
        "zone": "ATZ", # Default, non parsiamo info TZ da queste stringhe ATH per ora
        "is_dst": False,
        "month_name_A": None, # Nome del mese Anthaleja
        "day_of_week_name_A": None # Nome del giorno della settimana Anthaleja
    }
    errors_list: List[str] = []

    # Mappa dei codici di formato Anthaleja a pattern regex (da ATHDateTime)
    format_to_regex_map = {
        'MONTH': r'(' + r'|'.join(map(re.escape, ATHDateTimeInterface.MONTH_NAMES)) + r')',
        'Mon':   r'(' + r'|'.join(map(re.escape, ATHDateTimeInterface.MONTH_ABBR.values())) + r')',
        'DAY':   r'(' + r'|'.join(map(re.escape, ATHDateTimeInterface.DAY_NAMES)) + r')',
        'DayN':  r'(' + r'|'.join(map(re.escape, ATHDateTimeInterface.DAY_ABBR_ATH.values())) + r')',
        'YYYY':  r'(\d{4})', 'Y': r'(\d{1,4})', 'y': r'(\d{2})',
        'NN':    r'(0[1-9]|1[0-8])', 'N': r'([1-9]|1[0-8])',
        'JJ':    r'(0[1-9]|1[0-9]|2[0-4])', 'J': r'([1-9]|1[0-9]|2[0-4])',
        'HH':    r'(0[0-9]|1[0-9]|2[0-7])', 'G': r'([0-9]|1[0-9]|2[0-7])',
        'II':    r'([0-5][0-9])', 'I': r'([0-9]|[1-5][0-9])',
        'SS':    r'([0-5][0-9])', 'S': r'([0-9]|[1-5][0-9])',
    }

    regex_parts = []
    component_order = [] # Tiene traccia dei tipi di componenti nell'ordine del formato
    
    temp_format_string = ath_format_string
    sorted_format_codes = sorted(format_to_regex_map.keys(), key=len, reverse=True)

    while temp_format_string:
        matched_code_in_loop = None
        for code in sorted_format_codes:
            if temp_format_string.startswith(code):
                regex_parts.append(format_to_regex_map[code])
                component_order.append(code)
                temp_format_string = temp_format_string[len(code):]
                matched_code_in_loop = True
                break
        if not matched_code_in_loop:
            regex_parts.append(re.escape(temp_format_string[0]))
            temp_format_string = temp_format_string[1:]
    
    full_regex_pattern = r'^' + r''.join(regex_parts) + r'$'

    try:
        match = re.fullmatch(full_regex_pattern, ath_datetime_string) # Usare fullmatch per corrispondenza intera
        if not match:
            errors_list.append(f"La stringa '{ath_datetime_string}' non corrisponde al formato '{ath_format_string}'.")
        else:
            extracted_values = match.groups()
            if len(extracted_values) != len(component_order):
                errors_list.append("Discordanza tra valori estratti e componenti di formato.")
            else:
                temp_parsed_components: Dict[str, Union[int, str]] = {}
                for i, comp_code in enumerate(component_order):
                    value_str = extracted_values[i]
                    # Mappa i codici ATH ai nomi dei campi del dizionario 'result'
                    if comp_code in ['YYYY', 'Y', 'y']: 
                        result['year'] = int(value_str)
                        # Nota: la logica per 'y' (anno a 2 cifre) andrebbe gestita se si vuole inferire il secolo.
                    elif comp_code == 'M': # MONTH (Nome completo)
                        result['month_name_A'] = value_str
                        result['month'] = ATHDateTimeInterface.MONTH_NAMES.index(value_str) + 1
                    elif comp_code == 'Mon': # M_ABBR (Nome abbreviato)
                        month_found = False
                        for name, abbr_val in ATHDateTimeInterface.MONTH_ABBR.items():
                            if abbr_val == value_str:
                                result['month_name_A'] = name
                                result['month'] = ATHDateTimeInterface.MONTH_NAMES.index(name) + 1
                                month_found = True; break
                        if not month_found: errors_list.append(f"Abbreviazione mese non valida: {value_str}")
                    elif comp_code in ['NN', 'N']: # Mese numerico
                        month_num = int(value_str)
                        if not (1 <= month_num <= ATHDateTimeInterface.MXY):
                            errors_list.append(f"Numero mese non valido: {month_num}")
                        else:
                            result['month'] = month_num
                            result['month_name_A'] = ATHDateTimeInterface.MONTH_NAMES[month_num - 1]
                    elif comp_code in ['JJ', 'J']: # Giorno del mese
                        result['day'] = int(value_str)
                    elif comp_code in ['HH', 'G']: # Ora
                        result['hour'] = int(value_str)
                    elif comp_code in ['II', 'I']: # Minuti
                        result['minute'] = int(value_str)
                    elif comp_code in ['SS', 'S']: # Secondi
                        result['second'] = int(value_str)
                    elif comp_code == 'DAY': # Nome giorno settimana
                        result['day_of_week_name_A'] = value_str
                    elif comp_code == 'DayN': # Nome giorno settimana abbreviato
                        day_found = False
                        for name, abbr_val in ATHDateTimeInterface.DAY_ABBR_ATH.items():
                            if abbr_val == value_str:
                                result['day_of_week_name_A'] = name
                                day_found = True; break
                        if not day_found: errors_list.append(f"Abbreviazione giorno sett. non valida: {value_str}")
                
                # Validazione finale dei componenti essenziali se sono stati parsati e sono None
                # (dovrebbero essere riempiti se il formato li richiedeva e il match è avvenuto)
                if result['year'] is None or result['month'] is None or result['day'] is None:
                    if not errors_list: # Se non c'erano errori di parsing più specifici
                        errors_list.append("Componenti data essenziali (anno, mese, giorno) non trovati o non validi nel formato fornito.")

    except (re.error, ValueError, IndexError, TypeError) as e:
        errors_list.append(f"Errore critico durante il parsing: {str(e)}")

    result["error_count"] = len(errors_list)
    result["errors"] = {i: error for i, error in enumerate(errors_list)}
    # result["warning_count"] e result["warnings"] non sono attivamente popolati ora
    
    return result

def ath_date_sub(
    ath_datetime_obj: ATHDateTimeInterface, 
    ath_date_interval_obj: ATHDateInterval
) -> ATHDateTimeInterface:
    """
    Sottrae un ATHDateInterval da un oggetto ATHDateTimeInterface e 
    restituisce un nuovo oggetto ATHDateTimeInterface risultato.
    Alias funzionale per ath_datetime_obj.sub(ath_date_interval_obj).

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface da cui sottrarre l'intervallo.
        ath_date_interval_obj: L'oggetto ATHDateInterval da sottrarre.

    Returns:
        Un nuovo oggetto ATHDateTimeInterface con l'intervallo sottratto.
        
    Raises:
        TypeError: Se gli oggetti forniti non sono dei tipi corretti.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError("Il primo argomento (ath_datetime_obj) deve essere un'istanza che implementa ATHDateTimeInterface.")
    if not isinstance(ath_date_interval_obj, ATHDateInterval):
        raise TypeError("Il secondo argomento (ath_date_interval_obj) deve essere un'istanza di ATHDateInterval.")
        
    # Chiama il metodo sub dell'oggetto.
    # Il metodo sub in ATHDateTimeInterface è dichiarato per restituire ATHDateTimeInterface.
    return ath_datetime_obj.sub(ath_date_interval_obj)

def ath_date_astronomy_info(
    ath_date_for_calculations: ATHDateTimeInterface,
    latitude_A: float,
    longitude_A: float,
    display_options: int = ALL_INFO,
    current_time_for_dashboard: Optional[ATHDateTimeInterface] = None # Passato a format_ath_celestial_dashboard
) -> Dict[str, Any]:
    """
    Funzione orchestratrice principale per calcolare e aggregare dati astronomici
    per il sistema Anthal-Nijel e le sue lune (Leea, Mirahn).

    Questa funzione raccoglie informazioni per:
    - Il pianeta Anthal: parametri fisici e orbitali.
    - La stella Nijel: fenomeni apparenti visti da Anthal (alba/tramonto, transito,
        declinazione, EoT, raggio angolare dinamico, distanza) ed eventi stagionali
        (anno tropicale, solstizi, equinozi, cross-quarter days).
    - Le lune Leea e Mirahn: posizione 3D, fase, distanza, apsidi, prossime fasi
        principali, e potenziali eclissi solari.

    I dati sono restituiti in un dizionario strutturato, pronti per essere utilizzati
    da funzioni di visualizzazione come `format_ath_celestial_dashboard`.
    La quantità di dati calcolati è controllata dal parametro `display_options`.

    Args:
        ath_date_for_calculations (ATHDateTimeInterface): L'istante (basato sul calendario
            Anthaleja) per cui eseguire i calcoli.
        latitude_A (float): Latitudine dell'osservatore su Anthal (in gradi).
        longitude_A (float): Longitudine dell'osservatore su Anthal (in gradi).
        display_options (int): Un intero (bitmask) che specifica quali set di dati
                            calcolare (vedi costanti NIJEL_INFO, ANTHAL_INFO, ecc.).
                            Default a ALL_INFO.
        current_time_for_dashboard (Optional[ATHDateTimeInterface]): Istante che rappresenta
            l'ora corrente, passato a `format_ath_celestial_dashboard` per l'intestazione.
            Non influenza i calcoli astronomici principali, che si basano su
            `ath_date_for_calculations`.

    Returns:
        Dict[str, Any]: Un dizionario (`raw_celestial_data`) contenente sotto-dizionari
                        per "anthal", "nijel", "leea", "mirahn" (se richiesti da
                        `display_options`), ognuno con i rispettivi dati astronomici.
    """
    raw_celestial_data: Dict[str, Any] = {} # Dizionario principale per i risultati

    # Fuso orario dell'oggetto data di input, usato per default negli output di eventi giornalieri
    ref_tz_for_daily_events = ath_date_for_calculations.get_timezone()
    # Fuso orario ATZ per eventi astronomici "assoluti" (solstizi, fasi, ecc.)
    atz_timezone = ATHDateTimeZone("ATZ") # Assumendo che ATHDateTimeZone sia importato/definito

    # --- Sezione 1: Dati del Pianeta Anthal ---
    # Questi dati sono in gran parte "statici" o derivati dai parametri orbitali di Anthal.
    if display_options & ANTHAL_INFO:
        anthal_data: Dict[str, Any] = {
            "name": "Anthal", # Nome del pianeta
            "physical_radius_m": ANTHAL_PARAMS.get("physical_radius_m"),
            "flattening": ANTHAL_PARAMS.get("flattening"),
            "axial_tilt_deg": ANTHAL_PARAMS.get("axial_tilt_deg"), # Inclinazione assiale
            "astronomical_day_duration_s": ATHDateTimeInterface.SXD_ASTRONOMICAL, # Durata giorno fisico
            # Parametri dell'orbita di Anthal attorno a Nijel
            "orbital_period_around_nijel_earth_s": ATHDateTimeInterface.ORBITAL_PERIOD_EARTH_SECONDS,
            "orbital_period_around_nijel_ath_days": ATHDateTimeInterface.EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS,
            "semi_major_axis_m": ANTHAL_PARAMS.get("semi_major_axis_m"),
            "eccentricity": ANTHAL_PARAMS.get("eccentricity"),
            # I seguenti verranno popolati dopo il calcolo dei dati di Nijel, se disponibili
            "current_distance_to_nijel_m": None,
            "nijel_apparent_angular_radius_deg": None
        }
        raw_celestial_data["anthal"] = anthal_data

    # --- Sezione 2: Dati di Nijel (Stella) ed Eventi Stagionali di Anthal ---
    nijel_calculated_data: Optional[Dict[str, Any]] = None # Dati restituiti da _internal_calculate_nijel_info
    nijel_core_data_for_moons: Dict[str, Any] = {}     # Dati di Nijel essenziali per le lune

    # Determina se è necessario calcolare i dati di Nijel.
    # Servono se è richiesto NIJEL_INFO, o ANTHAL_INFO (per distanza/raggio apparente di Nijel),
    # o se sono richieste le lune (per la loro elongazione/fase e offset di transito).
    needs_nijel_calculation = bool(
        (display_options & NIJEL_INFO) or \
        (display_options & ANTHAL_INFO) or \
        (display_options & LEEA_INFO) or \
        (display_options & MIRAHN_INFO)
    )

    if needs_nijel_calculation:
        try:
            # _internal_calculate_nijel_info ora accetta ANTHAL_PARAMS e NIJEL_PARAMS
            # Se questi sono definiti globalmente/nel modulo, la funzione può accedervi.
            # Se la firma di _internal_calculate_nijel_info li richiede esplicitamente:
            # nijel_calculated_data = _internal_calculate_nijel_info(
            #     ath_date_obj=ath_date_for_calculations, latitude_A=latitude_A, longitude_A=longitude_A,
            #     anthal_params=ANTHAL_PARAMS, nijel_star_params=NIJEL_PARAMS,
            #     ref_timezone_for_output=ref_tz_for_daily_events
            # )
            # Per ora, assumo che _internal_calculate_nijel_info acceda ai PARAMS globali/di modulo
            # come abbiamo fatto nella sua ultima revisione.
            nijel_calculated_data = _internal_calculate_nijel_info(
                ath_date_obj=ath_date_for_calculations,
                latitude_A=latitude_A,
                longitude_A=longitude_A,
                # I parametri ANTHAL_PARAMS e NIJEL_PARAMS sono usati internamente dalla funzione
                ref_timezone_for_output=ref_tz_for_daily_events
            )
        except Exception as e_nijel_calc:
            error_message_nijel = f"Calcolo dati Nijel fallito: {e_nijel_calc}"
            print(f"ERRORE (ath_date_astronomy_info): {error_message_nijel}")
            nijel_calculated_data = {"error": error_message_nijel, "notes": [error_message_nijel]}

        if nijel_calculated_data and not nijel_calculated_data.get("error"):
            nijel_internals = nijel_calculated_data.get("internals", {})
            
            # Se ANTHAL_INFO è richiesto, aggiorna con i dati dinamici relativi a Nijel
            if display_options & ANTHAL_INFO and "anthal" in raw_celestial_data:
                raw_celestial_data["anthal"]["current_distance_to_nijel_m"] = nijel_internals.get("current_distance_anthal_nijel_m")
                raw_celestial_data["anthal"]["nijel_apparent_angular_radius_deg"] = nijel_internals.get("dynamic_angular_radius_nijel_deg")

            # Estrai i dati di Nijel necessari per i calcoli delle lune
            nijel_core_data_for_moons = {
                "true_ecliptic_longitude_rad_nijel": nijel_internals.get("true_ecliptic_longitude_rad_nijel"),
                "transit_true_dt_nijel_obj": nijel_calculated_data.get("transit_true_local") # Oggetto ATHDateTime
            }
            
            # Se richiesto NIJEL_INFO, calcola e aggiungi gli eventi stagionali e l'anno tropicale
            if display_options & NIJEL_INFO:
                try:
                    target_year = ath_date_for_calculations.year
                    nijel_calculated_data["tropical_year_duration_interval"] = calculate_tropical_year_duration(target_year, atz_timezone)
                    
                    seasonal_markers = find_seasonal_markers(target_year, atz_timezone)
                    nijel_calculated_data["seasonal_markers"] = seasonal_markers
                    if seasonal_markers: # Calcola cross-quarters solo se i marker sono disponibili
                        nijel_calculated_data["cross_quarter_days"] = calculate_cross_quarter_days(seasonal_markers, atz_timezone)
                    else:
                        nijel_calculated_data["cross_quarter_days"] = {} # Assicura che la chiave esista
                    
                    # Prossimo evento stagionale globale per la dashboard
                    next_sol_eq_name, next_sol_eq_dt = find_next_solstice_or_equinox(ath_date_for_calculations)
                    nijel_calculated_data["next_global_seasonal_event"] = (next_sol_eq_name, next_sol_eq_dt)

                except Exception as e_seasonal:
                    error_message_seasonal = f"Errore calcolo eventi stagionali per Nijel: {e_seasonal}"
                    print(f"ERRORE (ath_date_astronomy_info): {error_message_seasonal}")
                    nijel_calculated_data.setdefault("notes", []).append(error_message_seasonal)
                    nijel_calculated_data.update({ # Inizializza campi per evitare KeyError
                        "tropical_year_duration_interval": None, "seasonal_markers": {},
                        "cross_quarter_days": {}, "next_global_seasonal_event": ("Errore Stagionale", None)
                    })
                raw_celestial_data["nijel"] = nijel_calculated_data # Assegna i dati completi di Nijel
        else: # Fallimento nel calcolo di nijel_data
            if display_options & NIJEL_INFO: 
                raw_celestial_data["nijel"] = nijel_calculated_data if nijel_calculated_data else {"error": "Dati Nijel non calcolati o falliti."}
            if display_options & ANTHAL_INFO and "anthal" in raw_celestial_data: # Popola con N/D se Nijel fallisce
                 raw_celestial_data["anthal"]["current_distance_to_nijel_m"] = "N/D (Errore Nijel)"
                 raw_celestial_data["anthal"]["nijel_apparent_angular_radius_deg"] = "N/D (Errore Nijel)"

    # --- Sezione 3: Dati delle Lune (Leea e Mirahn) ---
    # ALL_MOON_PARAMS è il dizionario globale/di modulo che contiene LEEA_PARAMS e MIRAHN_PARAMS
    for moon_name_iter, moon_data_dict_ref_key in [("Leea", "leea"), ("Mirahn", "mirahn")]:
        process_this_moon = False
        if moon_name_iter == "Leea" and (display_options & LEEA_INFO): process_this_moon = True
        elif moon_name_iter == "Mirahn" and (display_options & MIRAHN_INFO): process_this_moon = True

        if process_this_moon:
            # Verifica che i dati di Nijel necessari per le lune siano stati popolati
            if not nijel_core_data_for_moons.get("true_ecliptic_longitude_rad_nijel") or \
               not nijel_core_data_for_moons.get("transit_true_dt_nijel_obj"):
                raw_celestial_data[moon_data_dict_ref_key] = {
                    "error": f"Dati di Nijel dipendenti mancanti per il calcolo di {moon_name_iter}.",
                    "notes": [f"Dati Nijel dipendenti mancanti per {moon_name_iter}."]
                }
                continue # Passa alla prossima luna

            # Calcola i dati base della luna (posizione, fase, distanza, eventi giornalieri)
            # _internal_calculate_moon_info usa ANTHAL_PARAMS["axial_tilt_deg"] tramite il parametro
            planet_axial_tilt_deg = ANTHAL_PARAMS["axial_tilt_deg"]
            moon_base_data = _internal_calculate_moon_info(
                moon_name=moon_name_iter,
                ath_date_obj=ath_date_for_calculations,
                latitude_A=latitude_A,
                axial_tilt_deg_planet=planet_axial_tilt_deg,
                nijel_data_for_moon_calc=nijel_core_data_for_moons,
                moon_orbital_params=ALL_MOON_PARAMS[moon_name_iter],
                ref_timezone_for_output=ref_tz_for_daily_events
            )
            raw_celestial_data[moon_data_dict_ref_key] = moon_base_data
            
            # Aggiungi informazioni sul prossimo Apside
            try:
                apsis_name, apsis_dt, apsis_dist = find_next_moon_apsis(
                    moon_name_iter, ath_date_for_calculations, ALL_MOON_PARAMS, atz_timezone)
                moon_base_data["next_apsis"] = {"name": apsis_name, "date_atz": apsis_dt, "distance_m": apsis_dist}
            except Exception as e_apsis:
                moon_base_data["next_apsis"] = {"name": f"Errore Apside: {type(e_apsis).__name__}", "date_atz": None, "distance_m": 0.0}

            # Aggiungi informazioni sulle prossime Fasi Lunari Principali
            moon_base_data["upcoming_phases"] = []
            temp_date_for_phase_search = ath_date_for_calculations
            try:
                for _ in range(4): # Trova le prossime 4 fasi
                    phase_name, phase_dt = find_next_moon_major_phase(
                        moon_name_iter,
                        temp_date_for_phase_search,
                        ANTHAL_PARAMS,
                        ALL_MOON_PARAMS,
                        atz_timezone
                    )
                    moon_base_data["upcoming_phases"].append({"name": phase_name, "date_atz": phase_dt})
                    temp_date_for_phase_search = phase_dt.add(ATHDateInterval(hours=12))
            except Exception as e_phase:
                if not moon_base_data.get("upcoming_phases"): 
                    moon_base_data["upcoming_phases"] = [{"name": f"Errore Fasi: {type(e_phase).__name__}", "date_atz": None}]
            
            # Aggiungi Informazioni sulla Prossima Eclissi Solare causata da questa luna
            try:
                # find_next_solar_eclipse usa ANTHAL_PARAMS, NIJEL_PARAMS, e ALL_MOON_PARAMS globalmente
                solar_eclipse_info = find_next_solar_eclipse(
                    moon_name=moon_name_iter, start_date=ath_date_for_calculations,
                    moon_params_dict=ALL_MOON_PARAMS, 
                    nijel_params=NIJEL_PARAMS, # Vecchia firma
                    anthal_params=ANTHAL_PARAMS, # Vecchia firma
                    atz_timezone=atz_timezone)
                moon_base_data["next_solar_eclipse_by_this_moon"] = solar_eclipse_info
            except Exception as e_eclipse:
                error_message_eclipse = f"Errore calcolo eclissi solare per {moon_name_iter}: {e_eclipse}"
                print(f"ERRORE (ath_date_astronomy_info): {error_message_eclipse}")
                moon_base_data.setdefault("notes", []).append(error_message_eclipse)
                moon_base_data["next_solar_eclipse_by_this_moon"] = None
    
    # Il risultato è il dizionario grezzo; la formattazione è gestita da format_ath_celestial_dashboard.
    # La variabile current_time_for_dashboard viene passata direttamente a format_ath_celestial_dashboard.
    return raw_celestial_data

def ath_date_time_set(
    ath_datetime_obj: ATHDateTimeInterface,
    hour: int,
    minute: int,
    second: int = 0
) -> ATHDateTimeInterface:
    """
    Imposta una nuova ora sull'oggetto ATHDateTimeInterface, mantenendo la data originale.
    Restituisce un nuovo oggetto ATHDateTimeInterface con l'ora modificata (anche se
    l'oggetto originale era mutabile, il pattern corrente delle classi restituisce
    una nuova istanza per coerenza con la versione immutabile).

    Analogo a DateTime::setTime() di PHP.

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface su cui basare la modifica.
        hour: L'ora Anthaleja da impostare (intervallo 0-HXD-1, es. 0-27).
        minute: Il minuto Anthaleja da impostare (intervallo 0-IXH-1, es. 0-59).
        second: Il secondo Anthaleja da impostare (intervallo 0-SXI-1, es. 0-59),
                opzionale, default 0.

    Returns:
        Un nuovo oggetto ATHDateTimeInterface con l'ora impostata.

    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
        ValueError: Se i componenti dell'ora non sono validi (sollevato dal
                    metodo .set_time() sottostante).
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError(
            "Il primo argomento (ath_datetime_obj) deve implementare ATHDateTimeInterface."
        )
    
    # Chiama il metodo set_time dell'oggetto.
    # Il metodo set_time in ATHDateTimeInterface è dichiarato per restituire ATHDateTimeInterface.
    return ath_datetime_obj.set_time(hour, minute, second)

def ath_date_get_timestamp(
    ath_datetime_obj: ATHDateTimeInterface
) -> int:
    """
    Restituisce il timestamp Anthaleja, ovvero il numero di secondi
    terrestri trascorsi dal momento RDN_UNIX_TS (Refoundation Day Number epoch,
    che corrisponde al timestamp terrestre 951584400) per l'oggetto
    ATHDateTimeInterface fornito.

    Questa è la funzione "standard" per ottenere un timestamp nel sistema Anthaleja.

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface.

    Returns:
        Il timestamp Anthaleja (secondi trascorsi da RDN_UNIX_TS) come intero.

    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError(
            "L'argomento (ath_datetime_obj) deve implementare ATHDateTimeInterface."
        )
    
    # RDN_UNIX_TS è una costante definita in ATHDateTimeInterface
    # Rappresenta il momento zero del conteggio RDN in termini di timestamp Unix.
    current_earth_ts = ath_datetime_obj.get_earth_timestamp()
    return current_earth_ts - ATHDateTimeInterface.RDN_UNIX_TS

def ath_date_set_timestamp(
    ath_datetime_obj: ATHDateTimeInterface,
    anthalean_timestamp: int
) -> ATHDateTimeInterface:
    """
    Crea una NUOVA istanza di ATHDateTimeInterface impostata a un dato
    timestamp Anthaleja, preservando il fuso orario e il tipo
    (mutabile/immutabile) dell'oggetto originale.

    Il timestamp Anthaleja è il numero di secondi terrestri trascorsi
    dal momento RDN_UNIX_TS (951584400).

    Analogo concettualmente a DateTime::setTimestamp() di PHP, ma invece di
    modificare l'oggetto originale, restituisce una nuova istanza.

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface di riferimento da cui
                        derivare il fuso orario e il tipo (mutabile/immutabile)
                        per la nuova istanza.
        anthalean_timestamp: Il timestamp Anthaleja (secondi da RDN_UNIX_TS).

    Returns:
        Un nuovo oggetto ATHDateTimeInterface (del tipo di ath_datetime_obj)
        impostato al nuovo timestamp.

    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError(
            "Il primo argomento (ath_datetime_obj) deve implementare ATHDateTimeInterface."
        )

    # 1. Determina il fuso orario da usare per il nuovo oggetto.
    #    Sarà quello dell'oggetto originale. Se l'originale non ne ha uno esplicito,
    #    il costruttore di ATHDateTime/ATHDateTimeImmutable applicherà il default (ATZ).
    target_ath_tz = ath_datetime_obj.get_timezone()

    # 2. Converti il timestamp Anthaleja (secondi da RDN_UNIX_TS)
    #    in un timestamp Unix terrestre (secondi dal 1/1/1970 UTC).
    earth_unix_timestamp = anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS

    # 3. Crea un oggetto datetime terrestre UTC.
    earth_dt_utc = datetime.fromtimestamp(earth_unix_timestamp, tz=timezone.utc)

    # 4. Crea e restituisci una nuova istanza del tipo corretto (mutabile o immutabile)
    #    usando il datetime terrestre calcolato e il fuso orario dell'oggetto originale.
    if isinstance(ath_datetime_obj, ATHDateTimeImmutable):
        return ATHDateTimeImmutable(earth_dt_utc, ath_timezone_obj=target_ath_tz)
    # Per default o se è ATHDateTime, restituiamo ATHDateTime
    # (o una classe mutabile futura che potrebbe estendere ATHDateTimeInterface)
    else:
        return ATHDateTime(earth_dt_utc, ath_timezone_obj=target_ath_tz)

def ath_date_timezone_get(
    ath_datetime_obj: ATHDateTimeInterface
) -> Optional[ATHDateTimeZoneInterface]:
    """
    Restituisce l'oggetto fuso orario associato all'oggetto ATHDateTimeInterface fornito.

    Analogo a DateTime::getTimezone() di PHP.

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface.

    Returns:
        Un oggetto ATHDateTimeZoneInterface che rappresenta il fuso orario
        dell'oggetto, o None se nessun fuso orario specifico è impostato e
        si utilizza il default (es. ATZ implicito).

    Raises:
        TypeError: Se ath_datetime_obj non è del tipo corretto.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError(
            "L'argomento (ath_datetime_obj) deve implementare ATHDateTimeInterface."
        )
    
    return ath_datetime_obj.get_timezone()

def ath_date_timezone_set(
    ath_datetime_obj: ATHDateTimeInterface,
    ath_timezone_obj: ATHDateTimeZoneInterface
) -> ATHDateTimeInterface:
    """
    Imposta un nuovo fuso orario sull'oggetto ATHDateTimeInterface.
    Restituisce un NUOVO oggetto ATHDateTimeInterface con il fuso orario modificato.
    Il momento esatto nel tempo (UTC) rappresentato dall'oggetto non cambia,
    ma i suoi componenti di data/ora locali (anno, mese, giorno, ora, etc.)
    verranno ricalcolati in base al nuovo fuso orario.

    Analogo a DateTime::setTimezone() di PHP, ma restituisce una nuova istanza.

    Args:
        ath_datetime_obj: L'oggetto ATHDateTimeInterface su cui basare la modifica.
        ath_timezone_obj: L'oggetto ATHDateTimeZoneInterface che rappresenta
                        il nuovo fuso orario da impostare.

    Returns:
        Un nuovo oggetto ATHDateTimeInterface con il fuso orario impostato.

    Raises:
        TypeError: Se gli argomenti non sono dei tipi corretti.
    """
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError(
            "Il primo argomento (ath_datetime_obj) deve implementare ATHDateTimeInterface."
        )
    if not isinstance(ath_timezone_obj, ATHDateTimeZoneInterface):
        raise TypeError(
            "Il secondo argomento (ath_timezone_obj) deve essere un'istanza di ATHDateTimeZoneInterface."
        )

    # Chiama il metodo set_timezone dell'oggetto.
    # Questo metodo in ATHDateTimeInterface e nelle sue implementazioni
    # restituisce una nuova istanza.
    return ath_datetime_obj.set_timezone(ath_timezone_obj)

def ath_getdate(
    anthalean_timestamp: Optional[int] = None
) -> Dict[Union[str, int], Any]:
    """
    Restituisce un dizionario di informazioni sulla data/ora Anthaleja,
    analogo alla funzione getdate() di PHP, ma per il sistema Anthaleja.

    Se nessun timestamp è fornito, utilizza l'ora corrente nel fuso orario
    Anthaleja di default (ATZ).
    Se un timestamp è fornito, viene interpretato come un timestamp Anthaleja
    (secondi trascorsi da RDN_UNIX_TS).

    Args:
        anthalean_timestamp: Timestamp Anthaleja opzionale (secondi da RDN_UNIX_TS).

    Returns:
        Un dizionario associativo contenente le informazioni sulla data.
        Le chiavi includono:
        'seconds', 'minutes', 'hours', 'mday' (giorno del mese),
        'wday' (giorno della settimana numerico, 0 per Nijahr),
        'mon' (mese numerico, 1-18), 'year',
        'yday' (giorno dell'anno numerico, 0-431),
        'weekday' (nome del giorno della settimana),
        'month' (nome del mese),
        0 (il timestamp Anthaleja usato per i calcoli).
    """
    ath_dt_obj: ATHDateTime

    input_timestamp_for_result = 0 # Default se nessun timestamp è fornito

    if anthalean_timestamp is None:
        # Usa l'ora corrente nel fuso orario di default (ATZ)
        ath_dt_obj = ATHDateTime(datetime.now(timezone.utc)) # Il costruttore applica il default TZ
        # Per il campo '0' del risultato, calcoliamo il timestamp Anthaleja corrente
        current_earth_ts = ath_dt_obj.get_earth_timestamp()
        input_timestamp_for_result = current_earth_ts - ATHDateTimeInterface.RDN_UNIX_TS
    else:
        # Converte il timestamp Anthaleja fornito in un oggetto ATHDateTime
        earth_unix_timestamp = anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS
        earth_dt_utc = datetime.fromtimestamp(earth_unix_timestamp, tz=timezone.utc)
        # Crea l'oggetto ATHDateTime (il costruttore applicherà il default TZ, es. ATZ)
        ath_dt_obj = ATHDateTime(earth_dt_utc)
        input_timestamp_for_result = anthalean_timestamp

    # Calcola il giorno dell'anno (0-indexed)
    # ath_dt_obj.month_index è 0-17, ath_dt_obj.day è 1-24
    day_of_year = (ath_dt_obj.month_index * ATHDateTimeInterface.DXM) + (ath_dt_obj.day - 1)

    return {
        "seconds": ath_dt_obj.second,
        "minutes": ath_dt_obj.minute,
        "hours": ath_dt_obj.hour,
        "mday": ath_dt_obj.day,
        "wday": ath_dt_obj._day_of_week_index, # Accediamo all'attributo interno per l'indice 0-6
        "mon": ath_dt_obj.month_index + 1,     # Mese 1-18
        "year": ath_dt_obj.year,
        "yday": day_of_year,                   # Giorno dell'anno 0-431
        "weekday": ath_dt_obj.day_of_week_name,
        "month": ath_dt_obj.month_name,
        0: input_timestamp_for_result
    }

def ath_gettimeofday(
    as_float: bool = False
) -> Union[Dict[str, int], float]:
    """
    Restituisce informazioni dettagliate sull'ora corrente nel sistema Anthaleja,
    analogo alla funzione gettimeofday() di PHP.

    Args:
        as_float: Se True, restituisce un float che rappresenta il timestamp
                Anthaleja corrente (secondi da RDN_UNIX_TS) con
                precisione al microsecondo.
                Se False (default), restituisce un dizionario associativo.

    Returns:
        Un dizionario o un float, a seconda del parametro as_float.
        Il dizionario contiene:
        - 'sec': Timestamp Anthaleja (secondi interi da RDN_UNIX_TS).
        - 'usec': Microsecondi della frazione di secondo corrente.
        - 'minuteswest': Minuti a ovest del "Meridiano Primo Anthaleja".
                        Attualmente 0, assumendo ATZ come riferimento.
        - 'dsttime': Tipo di correzione per l'ora legale (attualmente 0,
                    nessuna ora legale implementata).
    """
    # Ottieni il timestamp terrestre corrente con precisione al microsecondo
    current_earth_float_ts = time.time()

    # Calcola il timestamp Anthaleja (secondi da RDN_UNIX_TS) come float
    anthalean_float_ts = current_earth_float_ts - ATHDateTimeInterface.RDN_UNIX_TS

    if as_float:
        return anthalean_float_ts
    else:
        # Separa la parte intera (secondi) e la parte frazionaria (microsecondi)
        anthalean_sec_int = int(anthalean_float_ts)
        anthalean_usec_int = int((anthalean_float_ts - anthalean_sec_int) * 1_000_000)

        # Per 'minuteswest':
        # Questo dovrebbe riflettere l'offset del fuso orario di default
        # del sistema Anthaleja dal suo "UTC" o meridiano primo.
        # Se ATZ è il meridiano primo, l'offset è 0.
        # Altrimenti, dovremmo ottenere l'offset del default_timezone.
        default_ath_tz = get_default_ath_timezone() # Funzione che abbiamo già
        minuteswest = 0 # Default se non c'è offset o ATZ è il riferimento

        # Nota: L'offset in ATHDateTimeZone è in secondi.
        # PHP 'minuteswest' è minuti OVEST di Greenwich.
        # Un offset positivo in secondi (EST di ATZ) => minuteswest negativo.
        # Un offset negativo in secondi (OVEST di ATZ) => minuteswest positivo.
        # Il get_offset() nel nostro sistema attuale richiede un oggetto datetime
        # per DST future, ma per offset fissi possiamo prenderlo dal _data.
        # Per semplicità, assumiamo che ATZ sia il riferimento e non abbia offset.
        # Se avessimo un sistema di fusi orari più complesso con un "AUT" (Anthal Universal Time)
        # e ATZ fosse, per esempio, AUT+2, allora minuteswest per ATZ sarebbe -120.
        # Per ora, manteniamo 0 per ATZ.
        # Se si volesse l'offset del fuso orario di default:
        # offset_seconds = default_ath_tz._data.get("offset_seconds_from_atz", 0)
        # minuteswest = - (offset_seconds // 60)

        return {
            "sec": anthalean_sec_int,
            "usec": anthalean_usec_int,
            "minuteswest": minuteswest, # Minuti a ovest del Meridiano Primo Anthaleja (ATZ)
            "dsttime": 0  # Tipo di correzione DST (0 = nessuna ora legale)
        }

def ath_atzdate(  # Equivalente di gmdate()
    format_string: str,
    anthalean_timestamp: Optional[int] = None
) -> str:
    """
    Formatta una data/ora Anthaleja come se fosse nel fuso orario ATZ
    (Anthalys Time Zero).

    Se nessun timestamp è fornito, utilizza l'ora corrente.
    Se un timestamp è fornito, viene interpretato come un timestamp Anthaleja
    (secondi trascorsi da RDN_UNIX_TS).

    Args:
        format_string: La stringa di formato da usare (utilizza i codici
                    definiti in ATHDateTime.format()).
        anthalean_timestamp: Timestamp Anthaleja opzionale
                            (secondi da RDN_UNIX_TS).

    Returns:
        Una stringa contenente la data/ora Anthaleja formattata in ATZ.
    """
    ath_dt_obj_in_atz: ATHDateTime

    atz_timezone = ATHDateTimeZone("ATZ") 

    if anthalean_timestamp is None:
        current_earth_utc_dt = datetime.now(timezone.utc)
        ath_dt_obj_in_atz = ATHDateTime(current_earth_utc_dt, ath_timezone_obj=atz_timezone)
    else:
        earth_unix_timestamp = anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS
        earth_dt_utc = datetime.fromtimestamp(earth_unix_timestamp, tz=timezone.utc)
        ath_dt_obj_in_atz = ATHDateTime(earth_dt_utc, ath_timezone_obj=atz_timezone)

    return ath_dt_obj_in_atz.format(format_string)

def ath_atzmktime(  # Equivalente di gmmktime()
    hour: int,
    minute: Optional[int] = None,
    second: Optional[int] = None,
    month: Optional[int] = None, # Mese Anthaleja 1-18
    day: Optional[int] = None,   # Giorno Anthaleja 1-24
    year: Optional[int] = None
) -> Union[int, bool]:
    """
    Restituisce un timestamp Anthaleja (secondi da RDN_UNIX_TS) per una data
    e ora specificate, interpretando i componenti come se fossero nel fuso orario ATZ.

    I parametri mancanti (None) vengono impostati ai valori correnti in ATZ.
    Questo è l'equivalente di gmmktime() di PHP, adattato per il sistema Anthaleja.

    Args:
        hour: L'ora Anthaleja (0-27).
        minute: Il minuto Anthaleja opzionale (0-59).
        second: Il secondo Anthaleja opzionale (0-59).
        month: Il mese Anthaleja opzionale (1-18).
        day: Il giorno Anthaleja opzionale (1-24).
        year: L'anno Anthaleja opzionale.

    Returns:
        Il timestamp Anthaleja come intero, o False in caso di errore
        (es. data non valida).
    """
    try:
        atz_timezone = ATHDateTimeZone("ATZ")
        
        # Se i componenti della data/ora non sono forniti, prendi quelli correnti in ATZ
        # Questo assicura che i valori non specificati siano coerenti con ATZ
        current_moment_in_atz_for_defaults = ATHDateTime(datetime.now(timezone.utc), ath_timezone_obj=atz_timezone)
            
        if year is None:
            year = current_moment_in_atz_for_defaults.year
        if month is None: # month è 1-based
            month = current_moment_in_atz_for_defaults.month_index + 1
        if day is None:
            day = current_moment_in_atz_for_defaults.day
        # L'ora è un parametro obbligatorio, quindi non ha bisogno di default
        if minute is None:
            minute = current_moment_in_atz_for_defaults.minute
        if second is None:
            second = current_moment_in_atz_for_defaults.second

        # Validazione del mese e conversione a nome del mese per from_components
        if not (1 <= month <= ATHDateTimeInterface.MXY):
            raise ValueError(f"Mese Anthaleja non valido: {month}")
        month_name = ATHDateTimeInterface.MONTH_NAMES[month - 1]

        # Crea un oggetto ATHDateTime usando i componenti, specificando che sono in ATZ.
        # ATHDateTime.from_components costruisce l'oggetto interpretando i componenti
        # come se fossero nel fuso orario specificato (ATZ in questo caso).
        ath_dt_in_atz = ATHDateTime.from_components(
            year=year,
            month_name=month_name,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            ath_timezone_obj=atz_timezone
        )

        # Ottieni il timestamp Anthaleja (secondi da RDN_UNIX_TS)
        # Questo si basa sul momento UTC assoluto rappresentato da ath_dt_in_atz.
        earth_ts_equivalent = ath_dt_in_atz.get_earth_timestamp()
        return earth_ts_equivalent - ATHDateTimeInterface.RDN_UNIX_TS

    except (ValueError, IndexError) as e:
        # In caso di data non valida (es. giorno 30 in un mese da 24)
        # o mese non valido, from_components solleverà un errore.
        # PHP gmmktime restituirebbe false.
        # print(f"Errore in ath_atzmktime: {e}") # Log opzionale
        return False

def ath_idate(
    format_code: str,
    anthalean_timestamp: Optional[int] = None
) -> Union[int, bool]:
    """
    Restituisce un intero che rappresenta un componente specifico di una data/ora
    Anthaleja, basato su un codice di formato.

    Analogo a idate() di PHP, ma per il sistema e i codici di formato Anthaleja.
    Se nessun timestamp è fornito, utilizza l'ora corrente nel fuso orario
    Anthaleja di default (ATZ).
    Se un timestamp è fornito, viene interpretato come un timestamp Anthaleja
    (secondi trascorsi da RDN_UNIX_TS).

    Args:
        format_code: Un singolo carattere che specifica il componente da restituire.
                    Codici supportati: 'd', 'h', 'H', 'i', 'I', 'L', 'm', 's',
                    't', 'U', 'w', 'W', 'y', 'Y', 'z', 'Z'.
        anthalean_timestamp: Timestamp Anthaleja opzionale (secondi da RDN_UNIX_TS).

    Returns:
        Un intero che rappresenta il componente richiesto, o False se il
        codice di formato non è valido o si verifica un errore.
    """
    ath_dt_obj: ATHDateTime

    try:
        if anthalean_timestamp is None:
            ath_dt_obj = ATHDateTime(datetime.now(timezone.utc))
        else:
            earth_unix_timestamp = anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS
            earth_dt_utc = datetime.fromtimestamp(earth_unix_timestamp, tz=timezone.utc)
            ath_dt_obj = ATHDateTime(earth_dt_utc)

        if format_code == 'd': return ath_dt_obj.day
        elif format_code == 'h': # Ora in formato 1-14 (ciclo di 14 ore)
            current_hour = ath_dt_obj.hour # 0-27
            display_hour = current_hour % 14
            return 14 if display_hour == 0 else display_hour
        elif format_code == 'H': return ath_dt_obj.hour # Ora in formato 0-27
        elif format_code == 'i': return ath_dt_obj.minute
        elif format_code == 'I': return 0 # Anthaleja non ha ora legale definita
        elif format_code == 'L': return 0 # Il calendario Anthaleja non ha anni bisestili definiti
        elif format_code == 'm': return ath_dt_obj.month_index + 1 # Mese 1-18
        elif format_code == 's': return ath_dt_obj.second
        elif format_code == 't': return ATHDateTimeInterface.DXM # Numero di giorni nel mese corrente (fisso)
        elif format_code == 'U':
            if anthalean_timestamp is None:
                current_earth_ts = ath_dt_obj.get_earth_timestamp()
                return current_earth_ts - ATHDateTimeInterface.RDN_UNIX_TS
            return anthalean_timestamp
        elif format_code == 'w': return ath_dt_obj._day_of_week_index # Giorno della settimana, 0 per Nijahr (Domenica), ..., 6 per Ĝejahr (Sabato)
        elif format_code == 'W':
            # Numero della settimana dell'anno "semplice".
            # La settimana 1 inizia con il primo giorno dell'anno.
            day_of_year = (ath_dt_obj.month_index * ATHDateTimeInterface.DXM) + (ath_dt_obj.day - 1) # 0-indexed
            return (day_of_year // ATHDateTimeInterface.DXW) + 1 # 1-indexed
        elif format_code == 'y': return ath_dt_obj.year % 100
        elif format_code == 'Y': return ath_dt_obj.year
        elif format_code == 'z': return (ath_dt_obj.month_index * ATHDateTimeInterface.DXM) + (ath_dt_obj.day - 1) # 0-indexed
        elif format_code == 'Z':
            tz_obj = ath_dt_obj.get_timezone()
            if tz_obj: return tz_obj.get_offset(ath_dt_obj)
            return 0 # Default a ATZ se nessun fuso orario specifico
        else:
            return False # Codice di formato non valido
    except Exception:
        return False

def ath_localtime(
    anthalean_timestamp: Optional[int] = None,
    associative: bool = False
) -> Union[List[int], Dict[str, int]]:
    """
    Restituisce informazioni sulla data/ora "locale" Anthaleja.
    "Locale" si riferisce al fuso orario di default del sistema Anthaleja (ATZ).

    Se nessun timestamp è fornito, utilizza l'ora corrente.
    Se un timestamp è fornito, viene interpretato come un timestamp Anthaleja
    (secondi trascorsi da RDN_UNIX_TS).

    Analogo a localtime() di PHP, ma adattato per Anthaleja.

    Args:
        anthalean_timestamp: Timestamp Anthaleja opzionale
                            (secondi da RDN_UNIX_TS).
        associative: Se True, restituisce un dizionario associativo.
                    Se False (default), restituisce una lista indicizzata numericamente
                    seguendo l'ordine tm_sec, tm_min, tm_hour, tm_mday, tm_mon,
                    tm_year, tm_wday, tm_yday, tm_isdst.

    Returns:
        Una lista o un dizionario contenente i componenti della data/ora.
    """
    ath_dt_obj: ATHDateTime

    # 1. Determina l'oggetto ATHDateTime da usare.
    #    Verrà creato nel fuso orario di default del sistema (ATZ).
    if anthalean_timestamp is None:
        # Il costruttore ATHDateTime() senza argomenti specifici di data
        # userà datetime.now(timezone.utc) e il fuso orario di default di Anthaleja.
        ath_dt_obj = ATHDateTime()
    else:
        earth_unix_timestamp = anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS
        earth_dt_utc = datetime.fromtimestamp(earth_unix_timestamp, tz=timezone.utc)
        # Il costruttore ATHDateTime() applicherà il fuso orario di default di Anthaleja.
        ath_dt_obj = ATHDateTime(earth_dt_utc)

    # 2. Calcola i componenti necessari
    # Giorno dell'anno (0-indexed, es. 0 fino a DXY-1)
    day_of_year = (ath_dt_obj.month_index * ATHDateTimeInterface.DXM) + (ath_dt_obj.day - 1)

    tm_sec = ath_dt_obj.second
    tm_min = ath_dt_obj.minute
    tm_hour = ath_dt_obj.hour
    tm_mday = ath_dt_obj.day
    tm_mon = ath_dt_obj.month_index  # 0 per Arejal, ..., MXY-1
    tm_year = ath_dt_obj.year       # Anno Anthaleja completo
    tm_wday = ath_dt_obj._day_of_week_index # 0 per Nijahr (Domenica), ..., DXW-1
    tm_yday = day_of_year
    tm_isdst = 0                    # Anthaleja non ha ora legale

    # 3. Restituisci l'array/lista nel formato richiesto
    if associative:
        return {
            "tm_sec": tm_sec,
            "tm_min": tm_min,
            "tm_hour": tm_hour,
            "tm_mday": tm_mday,
            "tm_mon": tm_mon,
            "tm_year": tm_year,
            "tm_wday": tm_wday,
            "tm_yday": tm_yday,
            "tm_isdst": tm_isdst,
        }
    else:
        # Ordine standard della struct tm
        return [
            tm_sec,
            tm_min,
            tm_hour,
            tm_mday,
            tm_mon,
            tm_year,
            tm_wday,
            tm_yday,
            tm_isdst,
        ]

def ath_microtime(
    as_float: bool = False
) -> Union[str, float]:
    """
    Restituisce il timestamp Anthaleja corrente con microsecondi.
    Analogo alla funzione microtime() di PHP, ma basato sul timestamp Anthaleja
    (secondi trascorsi da RDN_UNIX_TS).

    Args:
        as_float: Se True, restituisce il timestamp come float con precisione
                al microsecondo.
                Se False (default), restituisce una stringa nel formato
                "msec sec", dove 'sec' è il timestamp Anthaleja intero e
                'msec' è la parte dei microsecondi (es. "0.123456").

    Returns:
        Una stringa o un float, a seconda del parametro as_float.
    """
    # Ottieni il timestamp terrestre corrente con precisione al microsecondo
    current_earth_float_ts = time.time()

    # Calcola il timestamp Anthaleja (secondi da RDN_UNIX_TS) come float
    anthalean_float_ts = current_earth_float_ts - ATHDateTimeInterface.RDN_UNIX_TS

    if as_float:
        return anthalean_float_ts
    else:
        # Separa la parte intera (secondi) e la parte frazionaria (microsecondi)
        anthalean_sec_int = int(anthalean_float_ts)
        # La parte microsecondi, come frazione di secondo (es. 0.123456)
        microsecond_part_float = anthalean_float_ts - anthalean_sec_int
        
        # Formatta la stringa "msec sec"
        # PHP microtime() formatta la parte msec come "0.micros"
        # Per ottenere solo i microsecondi come intero:
        # anthalean_usec_int = int(microsecond_part_float * 1_000_000)
        # Ma per replicare il formato stringa "0.micros secs":
        return f"{microsecond_part_float:.6f} {anthalean_sec_int}"

def ath_mktime(
    hour: int,
    minute: Optional[int] = None,
    second: Optional[int] = None,
    month: Optional[int] = None, # Mese Anthaleja 1-18
    day: Optional[int] = None,   # Giorno Anthaleja 1-24
    year: Optional[int] = None
) -> Union[int, bool]:
    """
    Restituisce un timestamp Anthaleja (secondi da RDN_UNIX_TS) per una data
    e ora specificate, interpretando i componenti come se fossero nel fuso orario
    di default del sistema Anthaleja (attualmente ATZ).

    Analogo a mktime() di PHP, ma per il sistema e il timestamp Anthaleja.
    I parametri mancanti (None) vengono impostati ai valori correnti nel fuso
    orario di default del sistema Anthaleja.

    Args:
        hour: L'ora Anthaleja (0-27).
        minute: Il minuto Anthaleja opzionale (0-59).
        second: Il secondo Anthaleja opzionale (0-59).
        month: Il mese Anthaleja opzionale (1-18).
        day: Il giorno Anthaleja opzionale (1-24).
        year: L'anno Anthaleja opzionale.

    Returns:
        Il timestamp Anthaleja come intero, o False in caso di errore
        (es. data non valida).
    """
    try:
        # Ottieni il fuso orario di default del sistema Anthaleja
        default_system_tz = get_default_ath_timezone() # Restituisce ATZ nel setup attuale

        # Se i componenti della data/ora non sono forniti, prendi quelli correnti
        # nel fuso orario di default del sistema Anthaleja.
        if year is None or month is None or day is None or \
        minute is None or second is None:
            # Crea un oggetto ATHDateTime per l'istante corrente,
            # il costruttore applicherà il fuso orario di default (es. ATZ).
            now_in_default_tz = ATHDateTime(datetime.now(timezone.utc))
            
            if year is None:
                year = now_in_default_tz.year
            if month is None: # month è 1-based
                month = now_in_default_tz.month_index + 1
            if day is None:
                day = now_in_default_tz.day
            # L'ora è un parametro obbligatorio
            if minute is None:
                minute = now_in_default_tz.minute
            if second is None:
                second = now_in_default_tz.second

        # Validazione del mese e conversione a nome del mese
        if not (1 <= month <= ATHDateTimeInterface.MXY):
            raise ValueError(f"Mese Anthaleja non valido: {month}")
        month_name = ATHDateTimeInterface.MONTH_NAMES[month - 1]

        # Crea un oggetto ATHDateTime usando i componenti, interpretandoli
        # come se fossero nel fuso orario di default del sistema Anthaleja.
        ath_dt_in_default_tz = ATHDateTime.from_components(
            year=year,
            month_name=month_name,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            ath_timezone_obj=default_system_tz # Usa il default del sistema
        )

        # Ottieni il timestamp Anthaleja (secondi da RDN_UNIX_TS)
        earth_ts_equivalent = ath_dt_in_default_tz.get_earth_timestamp()
        return earth_ts_equivalent - ATHDateTimeInterface.RDN_UNIX_TS

    except (ValueError, IndexError) as e:
        # print(f"Errore in ath_mktime: {e}") # Log opzionale
        return False

def ath_strtotime(
    datetime_string: str,
    base_anthalean_timestamp: Optional[int] = None
) -> Union[int, bool]:
    """
    Interpreta una stringa testuale di data/ora Anthaleja (relativa o assoluta)
    e la converte in un timestamp Anthaleja (secondi da RDN_UNIX_TS).

    Analogo a strtotime() di PHP, ma per il sistema e i formati Anthaleja.
    Le stringhe relative sono calcolate rispetto al base_anthalean_timestamp
    o all'ora corrente in ATZ se non fornito.

    Args:
        datetime_string: La stringa testuale della data/ora da interpretare.
                        Supporta:
                        - "now_atz" (ora corrente in ATZ)
                        - Parole chiave Anthaleja (es. "embadan", "embax", "pide mai")
                        - Formati relativi (es. "+5 jahrix", "-1 nesdol")
                        - Formati assoluti riconoscibili da ath_date_parse().
        base_anthalean_timestamp: Timestamp Anthaleja opzionale (secondi da
                                    RDN_UNIX_TS) da usare come base per
                                    i calcoli relativi. Se None, usa l'ora corrente.

    Returns:
        Il timestamp Anthaleja come intero in caso di successo,
        o False in caso di fallimento nel parsing.
    """
    base_dt_obj: ATHDateTime
    atz_timezone = ATHDateTimeZone("ATZ")

    # 1. Determina l'oggetto ATHDateTime di base (in ATZ)
    if base_anthalean_timestamp is None:
        base_dt_obj = ATHDateTime(datetime.now(timezone.utc), ath_timezone_obj=atz_timezone)
    else:
        earth_unix_timestamp = base_anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS
        earth_dt_utc = datetime.fromtimestamp(earth_unix_timestamp, tz=timezone.utc)
        base_dt_obj = ATHDateTime(earth_dt_utc, ath_timezone_obj=atz_timezone)

    # --- Strategie di Parsing ---
    # Normalizza la stringa di input
    normalized_datetime_string = datetime_string.strip().lower()
    result_dt_obj: Optional[ATHDateTimeInterface] = None

    # Strategia 1: Keyword "now_atz"
    if normalized_datetime_string == "now_atz":
        result_dt_obj = base_dt_obj # Se base_timestamp è None, base_dt_obj è già "now in ATZ"
                                # Se base_timestamp è fornito, "now_atz" ignora la base e usa l'ora corrente effettiva.
                                # Per coerenza, "now_atz" dovrebbe sempre dare l'ora corrente.
        result_dt_obj = ATHDateTime(datetime.now(timezone.utc), ath_timezone_obj=atz_timezone)


    # Strategia 2: Prova con ATHDateTime.modify() (per keyword Anthaleja e offset semplici)
    if result_dt_obj is None:
        try:
            # Il metodo modify() delle classi ATHDateTime/Immutable restituisce una nuova istanza.
            modified_dt = base_dt_obj.modify(datetime_string) # Usa la stringa originale, non normalizzata per case
            if modified_dt:
                result_dt_obj = modified_dt
        except (ValueError, TypeError):
            pass # Il formato potrebbe non essere per modify()

    # Strategia 3: Prova con ATHDateInterval.from_relative_ath_string() per formati come "+N units"
    # Questo si sovrappone un po' a modify(), ma può essere più specifico.
    # ATHDateTime.modify() ora usa ATHDateInterval internamente per gli offset,
    # quindi questa strategia potrebbe essere ridondante se modify() è completo.
    # La manteniamo per ora se ci sono formati che solo from_relative_ath_string gestisce.
    if result_dt_obj is None:
        try:
            interval = ATHDateInterval.from_relative_ath_string(datetime_string) # Usa la stringa originale
            result_dt_obj = base_dt_obj.add(interval)
        except (ValueError, TypeError):
            pass

    # Strategia 4: Prova a interpretarla come data assoluta usando ath_date_parse
    if result_dt_obj is None:
        parsed_info = ath_date_parse(datetime_string) # Usa la stringa originale
        if parsed_info and parsed_info.get("error_count", 1) == 0 and parsed_info.get("ath_year") is not None:
            # Abbiamo parsato con successo una data assoluta (Anthaleja o Terrestre convertita)
            # Dobbiamo creare un oggetto ATHDateTime da questi componenti, assicurandoci che sia in ATZ
            # se non ha un fuso orario specifico già interpretato come ATZ.
            # ath_date_parse già tende a restituire componenti come se fossero in ATZ se non specificato.
            
            # Se ath_date_parse ha restituito componenti validi, possiamo ricostruire.
            # Nota: ath_date_parse restituisce componenti numerici terrestri e ath stringa/numero
            try:
                result_dt_obj = ATHDateTime.from_components(
                    year=parsed_info["ath_year"],
                    month_name=parsed_info["ath_month_name"],
                    day=parsed_info["ath_day"],
                    hour=parsed_info["ath_hour"],
                    minute=parsed_info["ath_minute"],
                    second=parsed_info["ath_second"],
                    ath_timezone_obj=atz_timezone # Forziamo ATZ per coerenza con gm*
                )
            except (TypeError, ValueError, KeyError):
                result_dt_obj = None # Fallimento nella ricostruzione

    # --- Ottieni il Timestamp Finale ---
    if result_dt_obj:
        # Assicuriamoci che l'oggetto finale sia in ATZ prima di calcolare il timestamp
        needs_timezone_adjustment = True
        if (current_tz := result_dt_obj.get_timezone()) is not None:
            if current_tz.get_name() == "ATZ":
                needs_timezone_adjustment = False
        
        if needs_timezone_adjustment:
            # Se non ha un fuso orario o non è ATZ, lo impostiamo ad ATZ
            # (atz_timezone è definito all'inizio della funzione)
            result_dt_obj_atz = result_dt_obj.set_timezone(atz_timezone)
        else:
            result_dt_obj_atz = result_dt_obj
        
        earth_ts = result_dt_obj_atz.get_earth_timestamp()
        return earth_ts - ATHDateTimeInterface.RDN_UNIX_TS
    else:
        return False # Nessuna strategia di parsing ha funzionato

def ath_time() -> int:
    """
    Restituisce il timestamp Anthaleja corrente.

    Il timestamp Anthaleja è il numero di secondi trascorsi
    dal momento RDN_UNIX_TS (951584400 in timestamp Unix terrestre).

    Analogo alla funzione time() di PHP, ma restituisce un timestamp
    basato sull'epoca di Anthaleja invece dell'epoca Unix.

    Returns:
        int: Il timestamp Anthaleja corrente.
    """
    # Ottieni il timestamp Unix terrestre corrente (secondi dal 1/1/1970 UTC)
    current_earth_unix_timestamp_float = time.time()
    current_earth_unix_timestamp_int = int(current_earth_unix_timestamp_float)

    # Sottrai RDN_UNIX_TS per ottenere il timestamp Anthaleja
    anthalean_timestamp = current_earth_unix_timestamp_int - ATHDateTimeInterface.RDN_UNIX_TS
    
    return anthalean_timestamp

def ath_timezone_abbreviations_list() -> List[Dict[str, Union[bool, int, Optional[str]]]]:
    """
    Restituisce una lista di tutte le abbreviazioni dei fusi orari Anthaleja conosciuti,
    con informazioni aggiuntive per ciascuna.

    Analogo a DateTimeZone::listAbbreviations() di PHP.
    Ogni elemento della lista è un dizionario con le seguenti chiavi:
    - "dst": bool (sempre False, Anthaleja non ha DST)
    - "offset": int (offset in secondi da ATZ)
    - "timezone_id": Optional[str] (l'identificatore del fuso orario Anthaleja)

    Returns:
        List[Dict[str, Union[bool, int, Optional[str]]]]:
            Una lista di dizionari, ognuno rappresentante una variante di abbreviazione.
    """
    # Chiama il metodo statico esistente nella classe ATHDateTimeZone
    # che restituisce un Dict[str, List[Dict[...]]]
    abbreviations_dict = ATHDateTimeZone.list_abbreviations()

    # Riformatta l'output per corrispondere alla struttura di PHP:
    # una lista di dizionari, dove ogni dizionario è una "riga" di dati.
    style_list: List[Dict[str, Union[bool, int, Optional[str]]]] = []

    # L'output di ATHDateTimeZone.list_abbreviations() è:
    # { "ABBR1": [ {"dst": bool, "offset": int, "timezone_id": str}, ... ], ... }
    # Dobbiamo "appiattire" questo in una lista.
    for abbr, details_list in abbreviations_dict.items():
        for detail_dict in details_list:
            # Ogni detail_dict è già nel formato {"dst": ..., "offset": ..., "timezone_id": ...}
            # Il PHP originale a volte ha 'timezone_id' come null se l'abbr. non è canonica.
            # La nostra implementazione ha sempre un timezone_id.
            style_list.append({
                "abbr": abbr,
                "dst": detail_dict["dst"],
                "offset": detail_dict["offset"],
                "timezone_id": detail_dict["timezone_id"] 
            })

    return style_list

def ath_timezone_identifiers_list(
    timezone_group: int = ATHDateTimeZoneInterface.ALL, # Usiamo la costante come default
    country_code: Optional[str] = None
) -> List[str]:
    """
    Restituisce una lista di tutti gli identificatori dei fusi orari Anthaleja
    conosciuti, opzionalmente filtrati per gruppo o codice paese (Anthaleja).

    Analogo a DateTimeZone::listIdentifiers() di PHP.

    Args:
        timezone_group: Un bitmask di costanti definite in ATHDateTimeZoneInterface
                        (es. ATHDateTimeZoneInterface.ANTHAL,
                        ATHDateTimeZoneInterface.OCEAN, ATHDateTimeZoneInterface.ALL).
                        Default a ATHDateTimeZoneInterface.ALL.
        country_code: Un codice paese Anthaleja (definito in _timezones_data)
                    per filtrare i fusi orari di quel "paese".

    Returns:
        List[str]: Una lista di stringhe, ognuna rappresentante un identificatore
                di fuso orario Anthaleja.
    """
    # Chiama direttamente il metodo statico della classe ATHDateTimeZone
    return ATHDateTimeZone.list_identifiers(timezone_group, country_code)

def ath_timezone_location_get(
    ath_timezone_obj: ATHDateTimeZoneInterface
) -> Union[Dict[str, Union[str, float, int, None]], bool]:
    """
    Restituisce le informazioni sulla posizione geografica per il fuso orario
    Anthaleja specificato.

    Analogo al metodo DateTimeZone::getLocation() di PHP.
    Le chiavi del dizionario restituito sono mappate per assomigliare
    a quelle di PHP: "country_code", "latitude", "longitude", "comments".

    Args:
        ath_timezone_obj: L'oggetto ATHDateTimeZoneInterface per cui ottenere
                        le informazioni sulla posizione.

    Returns:
        Un dizionario associativo con le informazioni sulla posizione,
        o False se il fuso orario non ha informazioni sulla posizione.
        Il dizionario contiene:
        - "country_code": Codice paese Anthaleja (es. "ANTHAL_N").
        - "latitude": Latitudine (float o None).
        - "longitude": Longitudine (float o None).
        - "comments": Commenti sulla posizione (stringa o None).
    """
    if not isinstance(ath_timezone_obj, ATHDateTimeZoneInterface):
        raise TypeError(
            "L'argomento (ath_timezone_obj) deve essere un'istanza di ATHDateTimeZoneInterface."
        )

    location_data = ath_timezone_obj.get_location()

    if isinstance(location_data, dict):
        # Mappa le chiavi specifiche di Anthaleja a quelle generiche usate da PHP
        return {
            "country_code": location_data.get("country_code_A"),
            "latitude": location_data.get("latitude_A"),
            "longitude": location_data.get("longitude_A"),
            "comments": location_data.get("comments_A")
        }
    else:
        # get_location() restituisce False se non ci sono dati di locazione
        return False

def ath_timezone_name_from_abbr(
    abbr: str,
    atz_offset: int = -1,
    is_dst: int = -1
) -> Union[str, bool]:
    """
    Restituisce il nome canonico del fuso orario Anthaleja a partire
    da una sua abbreviazione, un offset da ATZ e lo stato DST.
    (resto del docstring invariato)
    """
    normalized_abbr = abbr.upper()

    if is_dst == 1:
        return False

    for tz_id, tz_data in ATHDateTimeZone._timezones_data.items():
        # 1. Controlla le abbreviazioni in modo sicuro
        raw_abbrs_value = tz_data.get("abbrs") # Ottieni il valore grezzo

        # Assicurati che raw_abbrs_value sia una lista e i suoi elementi siano stringhe
        if isinstance(raw_abbrs_value, list):
            # Converti le abbreviazioni definite in maiuscolo per il confronto
            # e assicurati che ogni elemento sia una stringa prima di chiamare .upper()
            processed_defined_abbrs = []
            for item in raw_abbrs_value:
                if isinstance(item, str):
                    processed_defined_abbrs.append(item.upper())
                # else: potresti voler loggare un avviso se un'abbreviazione non è una stringa

            if normalized_abbr not in processed_defined_abbrs:
                continue # L'abbreviazione non matcha, passa al prossimo fuso orario
        else:
            # Se "abbrs" non è una lista (o è mancante e .get() ha restituito None,
            # anche se abbiamo defaultato a [] in precedenza, questo è più robusto)
            # allora questo fuso orario non ha abbreviazioni valide da controllare.
            continue # Passa al prossimo fuso orario

        # 2. Controlla l'offset se specificato
        if atz_offset != -1:
            current_tz_offset = tz_data.get("offset_seconds_from_atz", None)
            if not isinstance(current_tz_offset, int) or current_tz_offset != atz_offset:
                continue # L'offset non matcha o non è un intero, passa al prossimo

        # 3. Stato DST è implicitamente gestito (tutti i nostri TZ sono non-DST)

        return tz_id # Match trovato

    return False # Nessun fuso orario trovato

def ath_timezone_name_get(
    ath_timezone_obj: ATHDateTimeZoneInterface
) -> str:
    """
    Restituisce il nome canonico del fuso orario Anthaleja specificato.

    Analogo al metodo DateTimeZone::getName() di PHP.

    Args:
        ath_timezone_obj: L'oggetto ATHDateTimeZoneInterface per cui ottenere
                        il nome.

    Returns:
        Una stringa che rappresenta il nome canonico del fuso orario
        (es. "ATZ", "Anthal/Meridia").

    Raises:
        TypeError: Se ath_timezone_obj non è del tipo corretto.
    """
    if not isinstance(ath_timezone_obj, ATHDateTimeZoneInterface):
        raise TypeError(
            "L'argomento (ath_timezone_obj) deve essere un'istanza di ATHDateTimeZoneInterface."
        )

    return ath_timezone_obj.get_name()

def ath_timezone_offset_get(
    ath_timezone_obj: ATHDateTimeZoneInterface,
    ath_datetime_obj: ATHDateTimeInterface
) -> int:
    """
    Restituisce l'offset del fuso orario Anthaleja specificato da ATZ
    (Anthalys Time Zero), per un dato momento.

    Analogo al metodo DateTimeZone::getOffset() di PHP.
    Nel sistema Anthaleja attuale, l'offset è fisso e non dipende
    dall'oggetto ath_datetime_obj fornito (non c'è DST).

    Args:
        ath_timezone_obj: L'oggetto ATHDateTimeZoneInterface per cui ottenere l'offset.
        ath_datetime_obj: L'oggetto ATHDateTimeInterface che rappresenta il momento
                        specifico per cui calcolare l'offset (attualmente ignorato
                        a causa degli offset fissi in Anthaleja).

    Returns:
        L'offset in secondi da ATZ. Positivo se a est di ATZ, negativo se a ovest.

    Raises:
        TypeError: Se gli argomenti non sono dei tipi corretti.
    """
    if not isinstance(ath_timezone_obj, ATHDateTimeZoneInterface):
        raise TypeError(
            "Il primo argomento (ath_timezone_obj) deve essere un'istanza di ATHDateTimeZoneInterface."
        )
    if not isinstance(ath_datetime_obj, ATHDateTimeInterface):
        raise TypeError(
            "Il secondo argomento (ath_datetime_obj) deve implementare ATHDateTimeInterface."
        )

    return ath_timezone_obj.get_offset(ath_datetime_obj)

def ath_timezone_open(
    anthalejatimezone_id: str
) -> Union[ATHDateTimeZone, bool]: # PHP returns DateTimeZone|false
    """
    Crea un nuovo oggetto ATHDateTimeZone a partire da un identificatore
    di fuso orario Anthaleja.

    Analogo a timezone_open() (alias di DateTimeZone::__construct()) di PHP.

    Args:
        anthalejatimezone_id: L'identificatore del fuso orario Anthaleja
                                (es. "ATZ", "Anthal/Meridia", "Anthal/CostaEst").

    Returns:
        Un'istanza di ATHDateTimeZone in caso di successo, o False se
        l'identificatore del fuso orario non è valido.
    """
    try:
        # Tenta di creare un'istanza della classe ATHDateTimeZone
        return ATHDateTimeZone(anthalejatimezone_id)
    except ValueError:
        # Se ATHDateTimeZone.__init__ solleva un ValueError (es. per ID non valido),
        # restituisci False per analogia con PHP.
        return False

def ath_timezone_transitions_get(
    ath_timezone_obj: ATHDateTimeZoneInterface,
    begin_anthalean_timestamp: Optional[int] = None,
    end_anthalean_timestamp: Optional[int] = None
) -> Union[List[Dict[str, Any]], bool]: # PHP returns array|false
    """
    Restituisce le transizioni del fuso orario Anthaleja per un dato
    intervallo di tempo.

    Analogo al metodo DateTimeZone::getTransitions() di PHP.
    Nel sistema Anthaleja attuale, i fusi orari hanno offset fissi e
    non c'è ora legale, quindi questa funzione restituirà tipicamente
    False (poiché ATHDateTimeZone.get_transitions() restituisce una lista vuota).

    Args:
        ath_timezone_obj: L'oggetto ATHDateTimeZoneInterface per cui ottenere
                        le transizioni.
        begin_anthalean_timestamp: Timestamp Anthaleja opzionale (secondi da
                                    RDN_UNIX_TS) per l'inizio dell'intervallo.
                                    Se None, viene usato un default molto ampio.
        end_anthalean_timestamp: Timestamp Anthaleja opzionale (secondi da
                                RDN_UNIX_TS) per la fine dell'intervallo.
                                Se None, viene usato un default molto ampio.

    Returns:
        Una lista di dizionari, ognuno rappresentante una transizione,
        o False se non ci sono transizioni o in caso di errore.
        Ogni dizionario di transizione contiene:
        - "ts": Timestamp Anthaleja della transizione.
        - "time": Data e ora della transizione in formato stringa ATZ.
        - "offset": Offset del fuso orario in secondi da ATZ *dopo* la transizione.
        - "isdst": Booleano (sempre False per Anthaleja) che indica se l'ora legale
                   è attiva *dopo* la transizione.
        - "abbr": Abbreviazione del fuso orario *dopo* la transizione.
    """
    if not isinstance(ath_timezone_obj, ATHDateTimeZoneInterface):
        raise TypeError(
            "Il primo argomento (ath_timezone_obj) deve essere un'istanza di ATHDateTimeZoneInterface."
        )

    # Converti i timestamp Anthaleja (opzionali) in timestamp Unix terrestri
    # per il metodo sottostante, se forniti.
    # ATHDateTimeZone.get_transitions() si aspetta timestamp Unix terrestri.
    
    begin_earth_ts: Optional[int] = None
    if begin_anthalean_timestamp is not None:
        begin_earth_ts = begin_anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS

    end_earth_ts: Optional[int] = None
    if end_anthalean_timestamp is not None:
        end_earth_ts = end_anthalean_timestamp + ATHDateTimeInterface.RDN_UNIX_TS

    # Usa i default del metodo sottostante se i timestamp non sono forniti
    # (o se i nostri valori convertiti sono ancora None)
    args_for_get_transitions = {}
    if begin_earth_ts is not None:
        args_for_get_transitions["timestamp_begin"] = begin_earth_ts
    if end_earth_ts is not None:
        args_for_get_transitions["timestamp_end"] = end_earth_ts
        
    transitions_list = ath_timezone_obj.get_transitions(**args_for_get_transitions)

    if not transitions_list:
        return False  # Nessuna transizione, comportamento analogo a PHP
    
    # Se ci fossero transizioni, dovremmo convertire i loro timestamp "ts"
    # da Unix terrestre (come restituito da ATHDateTimeZone.get_transitions)
    # a timestamp Anthaleja per la coerenza dell'output di questa funzione helper.
    # Ma dato che la lista è sempre vuota per ora, questo codice non verrà eseguito.
    # Se in futuro ATHDateTimeZone.get_transitions() restituisse transizioni reali,
    # questo blocco andrebbe implementato.
    #
    # anthalean_transitions = []
    # for trans_earth in transitions_list:
    #     anth_ts = trans_earth["ts"] - ATHDateTimeInterface.RDN_UNIX_TS
    #     anthalean_transitions.append({
    #         "ts": anth_ts,
    #         "time": trans_earth["time"], # Questo 'time' sarebbe formattato da ATHDateTimeZone
    #         "offset": trans_earth["offset"],
    #         "isdst": trans_earth["isdst"],
    #         "abbr": trans_earth["abbr"],
    #     })
    # return anthalean_transitions
    
    return transitions_list # Che al momento è sempre una lista vuota.

def ath_timezone_version_get() -> str:
    """
    Restituisce la versione del "database" dei fusi orari personalizzato
    utilizzato dal sistema Anthaleja.

    Analogo a timezone_version_get() di PHP, ma specifico per i dati
    timezone interni di Anthaleja.

    Returns:
        str: Una stringa che rappresenta la versione dei dati dei fusi orari
            Anthaleja.
    """
    # Restituisce una versione definita per il tuo sistema
    return ATHDateTimeZone._ANTHALEJA_TIMEZONE_DB_VERSION











## --- Funzioni Helper Matematiche e Geometriche di Base --- ##
def solve_kepler_equation(mean_anomaly_rad: float, 
                            eccentricity: float, 
                            iterations: int = 12,
                            tolerance: float = 1e-9) -> float:
    """
    Risolve l'Equazione di Keplero M = E - e * sin(E) per l'Anomalia Eccentrica E,
    utilizzando il metodo iterativo di Newton-Raphson.
    L'anomalia media (M) e l'anomalia eccentrica (E) sono in radianti.
    L'eccentricità (e) è un valore adimensionale tra 0 (orbita circolare) e <1 (orbita ellittica).
    Args:
        mean_anomaly_rad: L'anomalia media in radianti.
        eccentricity: L'eccentricità dell'orbita (0 <= e < 1).
        iterations: Il numero massimo di iterazioni da eseguire per la convergenza.
                    Un valore tra 8 e 10 è solitamente sufficiente per la maggior parte
                    delle eccentricità.
        tolerance: La soglia di tolleranza per la convergenza. L'iterazione si ferma
                se il cambiamento in E (|delta_E|) è inferiore a questo valore.
    Returns:
        float: L'Anomalia Eccentrica (E) calcolata in radianti.
    Raises:
        ValueError: Se l'eccentricità non è compresa tra 0 e 1 (non gestito qui,
                    ma l'input dovrebbe essere validato a monte se necessario).
    """
    # Se l'orbita è circolare (e=0), l'anomalia eccentrica è uguale all'anomalia media.
    if eccentricity == 0:
        return mean_anomaly_rad
    
    # Assicura che l'anomalia media sia nell'intervallo [0, 2*pi) per la stima iniziale,
    # anche se matematicamente Newton-Raphson converge anche da altri punti.
    # Questo non è strettamente necessario ma può aiutare la stabilità della stima iniziale.
    # M = mean_anomaly_rad % (2 * math.pi) # Opzionale normalizzazione di M
    M = mean_anomaly_rad # Usiamo M come fornito, dato che sin(M) gestisce angoli multipli

    # Stima iniziale per l'Anomalia Eccentrica (E)
    # Per basse eccentricità (e < 0.8), E ≈ M + e*sin(M) è una buona stima.
    # Per eccentricità più alte, M stesso è una stima di partenza migliore,
    # o si potrebbe usare E = pi se M è vicino a pi.
    if eccentricity < 0.8:
        E = M + eccentricity * math.sin(M)
    else:
        E = math.pi if M > math.pi * 0.5 and M < math.pi * 1.5 else M # Stima alternativa per alta e

    # Metodo iterativo di Newton-Raphson
    # f(E) = E - e*sin(E) - M
    # f'(E) = 1 - e*cos(E)
    # E_next = E_current - f(E_current) / f'(E_current)
    for _ in range(iterations):
        f_E = E - eccentricity * math.sin(E) - M
        f_prime_E = 1 - eccentricity * math.cos(E)

        # Se la derivata è molto vicina a zero, potremmo avere problemi di convergenza
        # o divisione per zero. Questo può accadere per eccentricità molto vicine a 1.
        if abs(f_prime_E) < tolerance: # Usiamo la stessa tolleranza per evitare instabilità
            break 
            
        delta_E = f_E / f_prime_E
        E -= delta_E # Aggiorna E: E_next = E - delta_E

        # Controlla la convergenza
        if abs(delta_E) < tolerance:
            break
    return E

def calculate_angular_radius_deg(physical_radius_m: float, distance_m: float) -> float:
    """
    Calcola il raggio angolare apparente di un corpo celeste, visto da un osservatore,
    espresso in gradi.
    Il raggio angolare è l'angolo sotteso dal raggio del corpo celeste
    alla distanza dell'osservatore.
    Args:
        physical_radius_m: Il raggio fisico (medio o equatoriale) del corpo celeste,
                        in metri. Deve essere un valore positivo.
        distance_m: La distanza dall'osservatore al centro del corpo celeste,
                    in metri. Deve essere un valore positivo.
    Returns:
        float: Il raggio angolare in gradi. Se la distanza è minore o uguale a zero,
            restituisce 90.0 gradi (implicando che l'osservatore è all'interno
            o esattamente sul corpo, che riempirebbe metà del cielo),
            anche se questo è un caso limite che solitamente indica un errore
            nei dati di input.
    Raises:
        # Nessuna eccezione esplicita viene sollevata, ma si potrebbe considerare
        # un ValueError se distance_m è <= 0 invece di restituire 90.0.
        pass
    """
    # Caso limite: se la distanza è zero o negativa (osservatore all'interno o al centro del corpo),
    # il corpo occuperebbe almeno un emisfero del cielo. Restituire 90° è una convenzione
    # per indicare una dimensione angolare massima.
    # In alternativa, si potrebbe sollevare un ValueError.
    if distance_m <= 0:
        # Potenziale log di avviso qui se questo caso non è atteso:
        # print(f"Attenzione: Distanza non positiva ({distance_m}m) in calculate_angular_radius_deg.")
        return 90.0 

    # La formula per il semidiametro angolare (alpha) è: alpha = atan(R / D)
    # dove R è il raggio fisico e D è la distanza.
    # math.atan restituisce l'angolo in radianti.
    alpha_rad = math.atan(physical_radius_m / distance_m)
    
    # Converte l'angolo da radianti a gradi per il valore di ritorno.
    return math.degrees(alpha_rad)

def calculate_ecliptic_angular_separation_deg(
    lon1_deg: float, lat1_deg: float, # Coordinate eclittiche del primo corpo
    lon2_deg: float, lat2_deg: float  # Coordinate eclittiche del secondo corpo
) -> float:
    """
    Calcola la separazione angolare tra due corpi celesti date le loro
    coordinate eclittiche (longitudine e latitudine), espresse in gradi.
    La formula utilizzata è la legge sferica dei coseni, che fornisce la
    distanza angolare più breve lungo un cerchio massimo sulla sfera celeste.
    Args:
        lon1_deg: Longitudine eclittica del primo corpo (in gradi).
        lat1_deg: Latitudine eclittica del primo corpo (in gradi).
        lon2_deg: Longitudine eclittica del secondo corpo (in gradi).
        lat2_deg: Latitudine eclittica del secondo corpo (in gradi).
    Returns:
        float: La separazione angolare tra i due corpi, in gradi.
            Il valore sarà compreso tra 0 e 180 gradi.
    """
    # Passo 1: Converti tutte le coordinate angolari da gradi a radianti,
    # poiché le funzioni trigonometriche di Python (math.sin, math.cos, math.acos)
    # operano con radianti.
    lon1_rad = math.radians(lon1_deg)
    lat1_rad = math.radians(lat1_deg)
    lon2_rad = math.radians(lon2_deg)
    lat2_rad = math.radians(lat2_deg)

    # Passo 2: Calcola la differenza di longitudine tra i due corpi.
    delta_lon_rad = lon1_rad - lon2_rad # In radianti

    # Passo 3: Applica la legge sferica dei coseni.
    # Se theta è la separazione angolare, allora:
    # cos(theta) = sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(delta_lon)
    cos_theta = (math.sin(lat1_rad) * math.sin(lat2_rad) +
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon_rad))

    # Passo 4: Gestione di potenziali errori di precisione in virgola mobile.
    # A causa di arrotondamenti, cos_theta potrebbe risultare marginalmente
    # al di fuori dell'intervallo valido [-1.0, 1.0] per math.acos.
    # Facciamo un "clamp" del valore per evitare un ValueError.
    if cos_theta > 1.0: cos_theta = 1.0
    elif cos_theta < -1.0: cos_theta = -1.0
        
    # Passo 5: Calcola la separazione angolare in radianti usando l'arcocoseno.
    # math.acos restituisce un valore tra 0 e pi radianti (0 e 180 gradi).
    theta_rad = math.acos(cos_theta)
    
    # Passo 6: Converti il risultato da radianti a gradi.
    return math.degrees(theta_rad)

## --- Funzioni Helper per il Calcolo della Posizione di Nijel --- ##
def _get_true_ecliptic_longitude_at_moment(
    ath_date_obj: ATHDateTimeInterface,
    anthal_params: Dict[str, Any]
) -> float:
    """
    Calcola la longitudine eclittica vera di Nijel per una data e ora specifica
    di Anthal.
    Questa funzione determina la posizione angolare di Nijel lungo l'eclittica
    (il piano orbitale di Anthal attorno a Nijel), misurata da un punto di
    riferimento standard (come l'Equinozio Vernale definito per il sistema).
    Tiene conto dell'eccentricità dell'orbita di Anthal e della deriva annuale
    del perielio del pianeta.
    Args:
        ath_date_obj: L'oggetto ATHDateTimeInterface che rappresenta l'istante
                    specifico (basato sul calendario Anthaleja) per cui
                    calcolare la longitudine.
        NIJEL_PARAMS: Un dizionario contenente i parametri orbitali e fisici
                    necessari per Nijel e l'orbita di Anthal. Chiavi attese:
                    - "eccentricity": Eccentricità dell'orbita di Anthal.
                    - "base_perihelion_days_after_arejal1": Giorno calendariale base
                        (0-indexed da Arejal 1) del perielio per l'anno di riferimento.
                    - "base_days_arejal1_past_winter_solstice": Giorno calendariale base
                        (0-indexed da Arejal 1) usato come riferimento per l'orientamento
                        dell'asse del solstizio d'inverno (per definire l'origine delle longitudini).
                    - "reference_year": L'anno Anthaleja per cui i valori "base_" sono validi.
                    - "max_annual_perihelion_shift_s": Massimo scostamento annuale del
                        perielio in secondi terrestri (+/- questo valore).
                    - "perihelion_shift_cycle_years": Durata in anni Anthaleja del ciclo
                        di fluttuazione della deriva del perielio.
    Returns:
        float: La longitudine eclittica vera di Nijel in gradi (0-360).
    """
    # Estrarre i parametri orbitali e di deriva dal dizionario
    # Estrae i parametri orbitali e di deriva di Anthal
    ECCENTRICITY_ANTHAL_ORBIT = anthal_params["eccentricity"]
    BASE_PERIHELION_DAYS_AFTER_AREJAL1 = anthal_params["base_perihelion_days_after_arejal1"]
    BASE_DAYS_AREJAL1_PAST_WS = anthal_params["base_days_arejal1_past_winter_solstice"]
    REFERENCE_YEAR = anthal_params["reference_year"]
    MAX_ANNUAL_SHIFT_S = anthal_params["max_annual_perihelion_shift_s"]
    SHIFT_CYCLE_YEARS = anthal_params.get("perihelion_shift_cycle_years", 100)
    if SHIFT_CYCLE_YEARS == 0: SHIFT_CYCLE_YEARS = 1
    current_year = ath_date_obj.year

    # 1. Calcolo della deriva accumulata del perielio e del riferimento del solstizio
    # La deriva totale in secondi terrestri rispetto all'anno di riferimento.
    total_accumulated_drift_seconds = 0.0
    delta_years_from_ref = current_year - REFERENCE_YEAR
    if delta_years_from_ref > 0:
        for year_offset in range(delta_years_from_ref):
            # L'angolo per la sinusoide dipende dall'offset dall'anno di riferimento
            angle = (2.0 * math.pi / SHIFT_CYCLE_YEARS) * year_offset
            drift_for_this_year_s = MAX_ANNUAL_SHIFT_S * math.sin(angle)
            total_accumulated_drift_seconds += drift_for_this_year_s
    elif delta_years_from_ref < 0:
        for year_offset_abs in range(abs(delta_years_from_ref)):
            # year_offset_for_calc va da -1, -2, ... all'indietro dall'anno di riferimento
            year_offset_for_calc = -1 - year_offset_abs
            angle = (2.0 * math.pi / SHIFT_CYCLE_YEARS) * year_offset_for_calc
            drift_for_this_year_s = MAX_ANNUAL_SHIFT_S * math.sin(angle)
            # Sottraiamo la deriva perché stiamo andando indietro nel tempo rispetto al riferimento
            total_accumulated_drift_seconds -= drift_for_this_year_s

    # Converti la deriva accumulata da secondi fisici a giorni Anthaleja REALI
    accumulated_drift_days = total_accumulated_drift_seconds / ATHDateTimeInterface.SXD_ASTRONOMICAL
    
    # Giorno *calendariale* effettivo del perielio (0-indexed da Arejal 1)
    effective_perihelion_calendar_day = BASE_PERIHELION_DAYS_AFTER_AREJAL1 + accumulated_drift_days
    # Giorno *calendariale* effettivo del riferimento per il solstizio d'inverno (0-indexed da Arejal 1)
    effective_ws_reference_calendar_day = BASE_DAYS_AREJAL1_PAST_WS + accumulated_drift_days

    # 2. Calcolo dell'Anomalia Media di Anthal attorno a Nijel
    # Componenti della data dall'oggetto ath_date_obj (basato sul calendario HXD_CALENDAR=28)
    month_idx_calendar = ath_date_obj.month_index # 0-17
    day_in_month_calendar = ath_date_obj.day     # 1-24
    # Giorno dell'anno nel CALENDARIO (0-indexed, 0 a DXY_CALENDAR-1)
    dn_calendar_0_indexed = month_idx_calendar * ATHDateTimeInterface.DXM + (day_in_month_calendar - 1)

    # Tempo trascorso (in giorni *calendariali*) dall'ultimo passaggio al perielio
    # (che è anch'esso un giorno *calendariale* effettivo).
    # DXY_CALENDAR è 432 (giorni nel calendario).
    time_since_perihelion_in_calendar_days = (dn_calendar_0_indexed - effective_perihelion_calendar_day + ATHDateTimeInterface.DXY_CALENDAR) % ATHDateTimeInterface.DXY_CALENDAR
    
    # L'anomalia media è la frazione dell'orbita REALE percorsa.
    # EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS è la durata dell'orbita in giorni REALI (ora 432.0).
    mean_anomaly_rad_nijel = (time_since_perihelion_in_calendar_days / ATHDateTimeInterface.EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS) * (2.0 * math.pi)
    # Normalizza l'anomalia media a [0, 2*pi)
    mean_anomaly_rad_nijel = mean_anomaly_rad_nijel % (2.0 * math.pi)
    if mean_anomaly_rad_nijel < 0:
         mean_anomaly_rad_nijel += (2.0 * math.pi)

    # 3. Calcolo dell'Anomalia Eccentrica e Vera
    eccentric_anomaly_rad_nijel = solve_kepler_equation(mean_anomaly_rad_nijel, ECCENTRICITY_ANTHAL_ORBIT)
    
    cos_E = math.cos(eccentric_anomaly_rad_nijel)
    sin_E = math.sin(eccentric_anomaly_rad_nijel)
    true_anomaly_rad_nijel_y_comp = math.sqrt(1 - ECCENTRICITY_ANTHAL_ORBIT**2) * sin_E
    true_anomaly_rad_nijel_x_comp = cos_E - ECCENTRICITY_ANTHAL_ORBIT
    true_anomaly_rad_nijel = math.atan2(true_anomaly_rad_nijel_y_comp, true_anomaly_rad_nijel_x_comp)
    if true_anomaly_rad_nijel < 0: # atan2 restituisce [-pi, pi]
        true_anomaly_rad_nijel += (2.0 * math.pi) # Normalizza a [0, 2pi)

    # 4. Calcolo della Longitudine del Perielio (rispetto all'Equinozio Vernale)
    # Questo definisce l'orientamento dell'orbita nello spazio.
    # Gradi orbitali percorsi per giorno REALE di Anthal.
    angle_per_REAL_anthaleja_day_deg = 360.0 / ATHDateTimeInterface.EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS
    
    # Longitudine di Arejal 1 (inizio del calendario) rispetto all'Equinozio Vernale (VE).
    # Il Solstizio d'Inverno è a 270° dal VE.
    # effective_ws_reference_calendar_day è il giorno *calendariale* (0-indexed) del rif. solstizio.
    longitude_arejal1_from_VE_deg = (270.0 + (effective_ws_reference_calendar_day * angle_per_REAL_anthaleja_day_deg)) % 360.0
    
    # Longitudine del perielio rispetto ad Arejal 1 (convertendo il giorno calendariale del perielio in angolo).
    longitude_perihelion_from_arejal1_deg = effective_perihelion_calendar_day * angle_per_REAL_anthaleja_day_deg
    
    # Longitudine del Perielio (dal VE) = Longitudine di Arejal1 (dal VE) + Longitudine del Perielio (da Arejal1)
    longitude_of_perihelion_from_VE_deg = (longitude_arejal1_from_VE_deg + longitude_perihelion_from_arejal1_deg) % 360.0
    longitude_of_perihelion_from_VE_rad = math.radians(longitude_of_perihelion_from_VE_deg)

        
    # 5. Longitudine Eclittica Vera di Nijel (λ_star)
    # È la somma dell'anomalia vera e della longitudine del perielio.
#    true_ecliptic_longitude_rad_nijel = (true_anomaly_rad_nijel + longitude_of_perihelion_from_VE_rad) % (2.0 * math.pi)
    # Il risultato di % è già normalizzato in [0, 2*pi) se il dividendo è positivo,
    # o in (-2*pi, 0] se negativo. Per sicurezza, anche se non strettamente necessario qui
    # con la normalizzazione precedente di true_anomaly e longitude_of_perihelion.
#    if true_ecliptic_longitude_rad_nijel < 0:
#        true_ecliptic_longitude_rad_nijel += (2.0 * math.pi)
    #    Per un osservatore su Anthal, la longitudine di Nijel è opposta alla longitudine eliocentrica di Anthal.
    #    Longitudine eliocentrica di Anthal (L_Anthal) = Anomalia Vera di Anthal (ν_Anthal) + Longitudine del Perielio di Anthal (ϖ_Anthal)
    #    Longitudine geocentrica di Nijel (λ_star) = L_Anthal + 180° (o π radianti)
    #    Tuttavia, per coerenza con i calcoli precedenti e per i solstizi/equinozi,
    #    la 'true_ecliptic_longitude_rad_nijel' è stata finora calcolata come ν + ϖ.
    #    Questo rappresenta la longitudine eliocentrica di Anthal.
    #    Se questa funzione deve restituire la longitudine *di Nijel vista da Anthal*,
    #    dovremmo aggiungere PI (180 gradi).
    #    MA, se questa longitudine viene usata per calcolare la declinazione di Nijel come
    #    sin(δ) = sin(ε)sin(λ), allora λ deve essere la longitudine di Nijel sull'eclittica
    #    come vista dal centro di Anthal, che è la stessa della longitudine eliocentrica di Anthal.
    #    (Pensando al sistema solare: la Terra ha longitudine L, il Sole visto dalla Terra ha longitudine L+180.
    #    Le stagioni dipendono da L. La declinazione del Sole è sin(eps)*sin(L_sole_apparente),
    #    dove L_sole_apparente è la longitudine eclittica del Sole. Se L è la long. della Terra,
    #    L_sole_apparente = L_terra + 180. sin(L_terra+180) = -sin(L_terra).
    #    Quindi sin(delta_sole) = -sin(eps)sin(L_terra).
    #    La nostra formula per delta_nijel in _internal_calculate_nijel_info usa:
    #    sin_delta_nijel = math.sin(axial_tilt_rad) * math.sin(true_ecliptic_longitude_rad_nijel)
    #    Questo implica che 'true_ecliptic_longitude_rad_nijel' calcolata qui è la
    #    longitudine apparente di Nijel (L_stella). Quindi, il calcolo corrente (ν + ϖ)
    #    è corretto se interpretato come L_stella (o L_pianeta se il riferimento è quello).
    #    Per evitare ambiguità, la chiameremo "longitudine orbitale di riferimento".
    
    orbital_reference_longitude_rad = (true_anomaly_rad_nijel + longitude_of_perihelion_from_VE_rad) % (2.0 * math.pi)
    if orbital_reference_longitude_rad < 0:
        orbital_reference_longitude_rad += (2.0 * math.pi)
        
    return math.degrees(orbital_reference_longitude_rad)

def _calculate_nijel_altitude_at_solar_noon(latitude_deg: float, nijel_declination_deg: float) -> float:
    """
    Calcola l'altitudine massima di Nijel sopra l'orizzonte,
    espressa in gradi, al momento del mezzogiorno solare locale su Anthal.
    Il mezzogiorno solare locale è l'istante in cui Nijel attraversa
    il meridiano dell'osservatore e raggiunge la sua massima altitudine giornaliera.
    Args:
        latitude_deg: La latitudine geografica dell'osservatore su Anthal,
                    in gradi. Valori positivi per l'emisfero nord, negativi per il sud.
        nijel_declination_deg: La declinazione di Nijel per il giorno specificato,
                            in gradi. Positiva se Nijel è a nord dell'equatore celeste,
                            negativa se a sud.
    Returns:
        float: L'altitudine di Nijel in gradi (0-90). Se Nijel è sotto l'orizzonte
            anche a mezzogiorno solare, restituisce 0.0.
    """
    # La formula a = 90 - |latitudine - declinazione| deriva dalla semplificazione
    # della formula generale dell'altitudine quando l'angolo orario è zero (mezzogiorno solare).
    altitude_deg = 90.0 - abs(latitude_deg - nijel_declination_deg)

    # L'altitudine non può essere negativa.
    return max(0.0, altitude_deg)

def _calculate_event_times_for_body_internal(
        h_deg_target: float,                       # Altitudine target del centro del corpo (gradi)
        delta_rad_body: float,                     # Declinazione del corpo (radianti)
        transit_dt_body_ref: ATHDateTime,          # Oggetto ATHDateTime del transito del corpo (basato sul CALENDARIO)
        lat_rad: float,                            # Latitudine dell'osservatore (radianti)
        body_name_str: str,                        # Nome del corpo per i messaggi di log/note
        ref_timezone_for_output: Optional[ATHDateTimeZoneInterface] # Fuso orario per gli oggetti ATHDateTime restituiti
    ) -> Tuple[Optional[ATHDateTime], Optional[ATHDateTime], List[str]]:
    """
    Calcola gli orari approssimativi in cui il centro di un corpo celeste raggiunge
    una specifica altitudine (h_deg_target), una volta al mattino (salendo) e una
    alla sera (scendendo). Restituisce gli orari sull'orologio del CALENDARIO.
    Args:
        h_deg_target: Altitudine target in gradi (es. ~ -0.833 per alba/tramonto standard,
                    valori negativi più grandi per i crepuscoli).
        delta_rad_body: Declinazione del corpo in radianti.
        transit_dt_body_ref: Istante ATHDateTime (basato sul calendario) del transito
                            superiore del corpo, usato come riferimento temporale.
        lat_rad: Latitudine dell'osservatore in radianti.
        body_name_str: Nome del corpo, usato per generare note descrittive.
        ref_timezone_for_output: Fuso orario desiderato per gli oggetti ATHDateTime
                                restituiti. Se None, verrà usato il default.
    Returns:
        Tuple[Optional[ATHDateTime], Optional[ATHDateTime], List[str]]:
            - ATHDateTime per l'evento del mattino (es. corpo che sale attraverso h_deg_target) o None.
            - ATHDateTime per l'evento della sera (es. corpo che scende attraverso h_deg_target) o None.
            - Una lista di stringhe contenente note descrittive (es. se il corpo è circumpolare).
    """
    h_rad_target = math.radians(h_deg_target) # Converte l'altitudine target in radianti

    # Calcola il numeratore e il denominatore per il coseno dell'angolo orario (H o omega)
    # Formula: cos(H) = (sin(alt) - sin(lat) * sin(decl)) / (cos(lat) * cos(decl))
    cos_omega_num = math.sin(h_rad_target) - (math.sin(lat_rad) * math.sin(delta_rad_body))
    cos_omega_den = math.cos(lat_rad) * math.cos(delta_rad_body)

    event_morning_dt: Optional[ATHDateTime] = None
    event_evening_dt: Optional[ATHDateTime] = None
    event_notes: List[str] = []

    # Controlla casi speciali (es. osservatore ai poli, corpo all'equatore celeste, ecc.)
    # Se cos_omega_den è molto piccolo, l'osservatore è vicino a un polo o il corpo ha declinazione +-90°.
    if abs(cos_omega_den) < 1e-12: # Tolleranza per evitare divisione per zero
        # Il corpo è circumpolare o mai visibile rispetto a questa altitudine.
        # Se sin(lat) * sin(decl) > sin(h_target), il corpo è sempre più basso di h_target (per h_target > 0)
        # o sempre più alto di h_target (per h_target < 0 e molto negativo).
        # Questo confronto determina se il cerchio diurno del corpo interseca il cerchio di altitudine h_target.
        if math.sin(lat_rad) * math.sin(delta_rad_body) > math.sin(h_rad_target):
            event_notes.append(f"{body_name_str} sempre sotto altitudine {h_deg_target:.1f}°.")
        elif math.sin(lat_rad) * math.sin(delta_rad_body) < math.sin(h_rad_target):
            event_notes.append(f"{body_name_str} sempre sopra altitudine {h_deg_target:.1f}°.")
        else:
            # Caso limite in cui l'altitudine massima/minima è esattamente h_deg_target
            event_notes.append(f"Situazione polare/limite per {body_name_str} ad altitudine {h_deg_target:.1f}°. L'evento coincide con il transito.")
            # In questo caso, potremmo considerare l'evento mattutino e serale coincidenti con il transito
            # event_morning_dt = transit_dt_body_ref
            # event_evening_dt = transit_dt_body_ref
    else:
        # Calcola il coseno dell'angolo orario
        cos_omega = cos_omega_num / cos_omega_den

        if cos_omega > 1.0:  # Valore fuori range per acos, il corpo non raggiunge l'altitudine da sotto
            event_notes.append(f"{body_name_str} non raggiunge (salendo) altitudine {h_deg_target:.1f}° (rimane più basso).")
        elif cos_omega < -1.0: # Valore fuori range, il corpo non scende fino a questa altitudine dall'alto
            event_notes.append(f"{body_name_str} non scende (scendendo) fino ad altitudine {h_deg_target:.1f}° (rimane più alto).")
        else:
            # Angolo orario (omega o H) in radianti. È la metà dell'arco diurno sopra h_deg_target.
            # math.acos restituisce un valore in [0, pi].
            omega_rad_val_h = math.acos(cos_omega)

            # Converte l'angolo orario (frazione della rotazione di 2*pi)
            # in una durata in secondi DELL'OROLOGIO DEL CALENDARIO.
            # ATHDateTimeInterface.SXD_CALENDAR è la durata di un giorno del calendario in secondi.
            delta_t_clock_seconds = (omega_rad_val_h / (2.0 * math.pi)) * ATHDateTimeInterface.SXD_CALENDAR

            # Il tempo del transito (transit_dt_body_ref) è il riferimento.
            # La sua proprietà .seconds_since_A_epoch è calcolata usando EPOCH,
            # che è definito usando costanti _CALENDAR. Quindi, è un conteggio di secondi
            # fisici equivalenti a giorni/ore/minuti del calendario dall'epoca.
            transit_ref_abs_sec_A_epoch_calendar = transit_dt_body_ref.seconds_since_A_epoch
            
            # Calcola i secondi (dall'epoca del calendario) per l'evento del mattino e della sera
            morning_abs_sec_A_epoch_calendar = transit_ref_abs_sec_A_epoch_calendar - delta_t_clock_seconds
            evening_abs_sec_A_epoch_calendar = transit_ref_abs_sec_A_epoch_calendar + delta_t_clock_seconds

            # Converti questi "secondi dall'epoca del calendario" in timestamp Unix terrestri
            # per poter creare nuovi oggetti datetime e poi ATHDateTime.
            # ATHDateTimeInterface.EPOCH è il timestamp Unix dell'inizio del calendario Anthaleja.
            morning_earth_ts = ATHDateTimeInterface.EPOCH + morning_abs_sec_A_epoch_calendar
            evening_earth_ts = ATHDateTimeInterface.EPOCH + evening_abs_sec_A_epoch_calendar
            
            # Crea gli oggetti ATHDateTime per gli eventi, usando il fuso orario di output specificato.
            # Il costruttore di ATHDateTime prenderà il datetime UTC e lo convertirà
            # al fuso orario Anthalejano specificato (o al default ATZ).
            try:
                event_morning_dt = ATHDateTime(datetime.fromtimestamp(morning_earth_ts, tz=timezone.utc), ath_timezone_obj=ref_timezone_for_output)
            except Exception as e_morn:
                event_notes.append(f"Errore creazione data evento mattino per {body_name_str} (ts: {morning_earth_ts}): {e_morn}")
                event_morning_dt = None # Assicura che sia None in caso di errore

            try:
                event_evening_dt = ATHDateTime(datetime.fromtimestamp(evening_earth_ts, tz=timezone.utc), ath_timezone_obj=ref_timezone_for_output)
            except Exception as e_even:
                event_notes.append(f"Errore creazione data evento sera per {body_name_str} (ts: {evening_earth_ts}): {e_even}")
                event_evening_dt = None # Assicura che sia None in caso di errore
            
    return event_morning_dt, event_evening_dt, event_notes

def _internal_calculate_nijel_info(
    ath_date_obj: ATHDateTimeInterface,
    latitude_A: float,
    longitude_A: float,
    ref_timezone_for_output: Optional[ATHDateTimeZoneInterface]
) -> Dict[str, Any]:
    """
    Calcola informazioni astronomiche dettagliate per Nijel (la stella del sistema)
    per una data e ora specifica di Anthaleja.

    Questa funzione è il motore principale per i calcoli relativi alla stella e include:
    - Posizione orbitale di Anthal attorno a Nijel:
        - Anomalia Media (M)
        - Anomalia Eccentrica (E)
        - Anomalia Vera (ν, nu)
        - Longitudine Eclittica Vera (λ, lambda)
    - Deriva annuale del perielio di Anthal.
    - Distanza istantanea Anthal-Nijel (r).
    - Raggio angolare dinamico di Nijel (α, alpha).
    - Declinazione di Nijel (δ, delta).
    - Equazione del Tempo (EoT).
    - Orario del transito solare (mezzogiorno solare vero locale).
    - Orari di alba, tramonto e vari crepuscoli.
    - Orario della mezzanotte solare.

    Utilizza costanti astronomiche precise per la fisica orbitale (es. SXD_ASTRONOMICAL,
    EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS) e costanti calendariali (es. HXD_CALENDAR,
    SXD_CALENDAR) per la rappresentazione del tempo sull'orologio e per lo scaling.

    Args:
        ath_date_obj: L'oggetto ATHDateTimeInterface (basato sul calendario Anthaleja)
                    per cui eseguire i calcoli.
        latitude_A: Latitudine dell'osservatore su Anthal (gradi). Positiva per Nord.
        longitude_A: Longitudine dell'osservatore su Anthal (gradi). Positiva per Est.
        NIJEL_PARAMS: Dizionario dei parametri. Chiavi attese includono:
                    "eccentricity" (e), "semi_major_axis_m" (a),
                    "physical_radius_m" (R_nijel), "axial_tilt_deg" (ε),
                    "base_perihelion_days_after_arejal1", "reference_year",
                    "max_annual_perihelion_shift_s", "perihelion_shift_cycle_years",
                    e parametri per i crepuscoli come "H_GOLDEN_LOWER_ATH".
        ref_timezone_for_output: Il fuso orario Anthaleja per gli oggetti ATHDateTime
                                restituiti (es. transito, alba).

    Returns:
        Dict[str, Any]: Un dizionario con i risultati dei calcoli, incluse note
                        e un sotto-dizionario "internals" con valori intermedi.
    """
    nijel_results: Dict[str, Any] = {"notes": []}

    nijel_results: Dict[str, Any] = {"notes": []}

    # --- Estrazione Parametri e Costanti Fondamentali ---
    # Parametri orbitali e fisici di Anthal (dal dizionario globale/di modulo)
    ECCENTRICITY_ANTHAL_ORBIT = ANTHAL_PARAMS["eccentricity"]         # e_anthal
    SEMI_MAJOR_AXIS_ANTHAL_ORBIT_M = ANTHAL_PARAMS["semi_major_axis_m"] # a_anthal
    AXIAL_TILT_DEG_PLANET = ANTHAL_PARAMS["axial_tilt_deg"]           # ε_anthal
    
    # Parametri fisici di Nijel (dal dizionario globale/di modulo)
    NIJEL_PHYSICAL_RADIUS_M = NIJEL_PARAMS["physical_radius_m"]      # R_nijel
    
    # Costanti di tempo e orbitali dall'interfaccia (già tengono conto della distinzione)
    HXD_CALENDAR = ATHDateTimeInterface.HXD_CALENDAR
    SXD_CALENDAR = ATHDateTimeInterface.SXD_CALENDAR
    IXH_CALENDAR = ATHDateTimeInterface.IXH
    SXI_CALENDAR = ATHDateTimeInterface.SXI
    # EFFECTIVE_ORBITAL_PERIOD_DAYS è già 432.0 (uguale a DXY_CALENDAR)

    lat_rad = math.radians(latitude_A)                          # φ (phi)
    axial_tilt_rad_planet = math.radians(AXIAL_TILT_DEG_PLANET) # ε (epsilon)

    current_year = ath_date_obj.year
    
    # --- 1. Calcolo della Longitudine Eclittica Vera di Nijel (λ_star) ---
    #    e altri dati orbitali intermedi di Anthal.
    #    Questa funzione ora usa ANTHAL_PARAMS per i dati orbitali di Anthal.
    #    La longitudine restituita è quella apparente di Nijel (o la L eliocentrica di Anthal).
    true_ecliptic_longitude_deg_nijel_apparent = _get_true_ecliptic_longitude_at_moment(
        ath_date_obj, ANTHAL_PARAMS
    )
    true_ecliptic_longitude_rad_nijel_apparent = math.radians(true_ecliptic_longitude_deg_nijel_apparent)

    # Per calcolare la distanza e il raggio angolare, abbiamo bisogno dell'anomalia eccentrica (E)
    # e dell'anomalia media (M) di Anthal, che _get_true_ecliptic_longitude_at_moment
    # calcola internamente. Per evitare ricalcoli, potremmo far restituire a quella funzione
    # anche E, oppure ricalcolare M ed E qui. Per ora, ricalcoliamo M ed E.
    # (Questo è un punto di potenziale ottimizzazione: _get_true_ecliptic_longitude_at_moment
    #  potrebbe restituire un dizionario con M, E, nu, e lambda).

    # Ricalcolo semplificato di M ed E per la distanza (logica da _get_true_ecliptic_longitude_at_moment)
    # Questo è ridondante se _get_true_ecliptic_longitude_at_moment potesse restituire più valori.
    # Assumiamo per ora che la precisione della distanza e del raggio angolare non cambi
    # drasticamente se usiamo l'anomalia media calcolata qui, anche se è leggermente
    # disaccoppiata dal calcolo fine della longitudine.
    # Per una soluzione più pulita, _get_true_ecliptic_longitude_at_moment dovrebbe essere
    # parte di una funzione che restituisce un set completo di elementi orbitali.
    
    # Logica per M ed E (copiata e adattata da _get_true_ecliptic_longitude_at_moment):
    BASE_PERIHELION_DAYS_AFTER_AREJAL1 = ANTHAL_PARAMS["base_perihelion_days_after_arejal1"]
    REFERENCE_YEAR = ANTHAL_PARAMS["reference_year"]
    MAX_ANNUAL_SHIFT_S = ANTHAL_PARAMS["max_annual_perihelion_shift_s"]
    SHIFT_CYCLE_YEARS = ANTHAL_PARAMS.get("perihelion_shift_cycle_years", 100)
    if SHIFT_CYCLE_YEARS == 0: SHIFT_CYCLE_YEARS = 1
    current_year = ath_date_obj.year
    total_accumulated_drift_seconds = 0.0 # Logica deriva identica...
    delta_years_from_ref = current_year - REFERENCE_YEAR
    if delta_years_from_ref > 0:
        for year_offset in range(delta_years_from_ref):
            angle = (2.0 * math.pi / SHIFT_CYCLE_YEARS) * year_offset; total_accumulated_drift_seconds += MAX_ANNUAL_SHIFT_S * math.sin(angle)
    elif delta_years_from_ref < 0:
        for year_offset_abs in range(abs(delta_years_from_ref)):
            year_offset_for_calc = -1 - year_offset_abs; angle = (2.0 * math.pi / SHIFT_CYCLE_YEARS) * year_offset_for_calc; total_accumulated_drift_seconds -= MAX_ANNUAL_SHIFT_S * math.sin(angle)
    accumulated_drift_days = total_accumulated_drift_seconds / ATHDateTimeInterface.SXD_ASTRONOMICAL
    effective_perihelion_calendar_day = BASE_PERIHELION_DAYS_AFTER_AREJAL1 + accumulated_drift_days
    
    month_idx_calendar = ath_date_obj.month_index
    day_in_month_calendar = ath_date_obj.day
    dn_calendar_0_indexed = month_idx_calendar * ATHDateTimeInterface.DXM + (day_in_month_calendar - 1)
    time_since_perihelion_in_calendar_days = (dn_calendar_0_indexed - effective_perihelion_calendar_day + ATHDateTimeInterface.DXY_CALENDAR) % ATHDateTimeInterface.DXY_CALENDAR
    
    # Questa è l'anomalia media di Anthal nella sua orbita attorno a Nijel
    mean_anomaly_rad_anthal = (time_since_perihelion_in_calendar_days / ATHDateTimeInterface.EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS) * (2.0 * math.pi)
    mean_anomaly_rad_anthal = mean_anomaly_rad_anthal % (2.0 * math.pi)
    if mean_anomaly_rad_anthal < 0: mean_anomaly_rad_anthal += (2.0 * math.pi)
    
    eccentric_anomaly_rad_anthal = solve_kepler_equation(mean_anomaly_rad_anthal, ECCENTRICITY_ANTHAL_ORBIT)
    # --- Fine ricalcolo M ed E ---

    # Distanza Istantanea Anthal-Nijel (r)
    current_distance_anthal_nijel_m = SEMI_MAJOR_AXIS_ANTHAL_ORBIT_M * \
                                     (1 - ECCENTRICITY_ANTHAL_ORBIT * math.cos(eccentric_anomaly_rad_anthal))
    nijel_results["current_distance_to_nijel_m"] = current_distance_anthal_nijel_m

    # Raggio Angolare Dinamico di Nijel (α_star)
    dynamic_angular_radius_nijel_deg = calculate_angular_radius_deg(
        NIJEL_PHYSICAL_RADIUS_M, current_distance_anthal_nijel_m
    )
    nijel_results["angular_radius_deg"] = dynamic_angular_radius_nijel_deg

    # --- 2. Declinazione di Nijel (δ_star) ---
    # sin(δ_star) = sin(ε_planet) * sin(λ_star_apparent)
    sin_delta_nijel = math.sin(axial_tilt_rad_planet) * math.sin(true_ecliptic_longitude_rad_nijel_apparent)
    delta_rad_nijel = math.asin(max(-1.0, min(1.0, sin_delta_nijel))) # Clamp
    nijel_results["declination_degrees"] = math.degrees(delta_rad_nijel)
    
    # --- 3. Equazione del Tempo (EoT) ---
    # EoT è una correzione all'ora DELL'OROLOGIO.
    y_eot_term = math.tan(axial_tilt_rad_planet / 2.0)**2
    # Per l'EoT, serve la longitudine del perielio di Anthal (ϖ_anthal),
    # che _get_true_ecliptic_longitude_at_moment calcola internamente.
    # La `true_ecliptic_longitude_rad_nijel_apparent` è (ν_anthal + ϖ_anthal).
    # L'anomalia media (M_anthal) è `mean_anomaly_rad_anthal`.
    # La longitudine eclittica media è (M_anthal + ϖ_anthal).
    # Dobbiamo estrarre ϖ_anthal o ricalcolarla qui.
    # Ricalcoliamo la longitudine del perielio di Anthal:
    effective_ws_reference_calendar_day = ANTHAL_PARAMS["base_days_arejal1_past_winter_solstice"] + accumulated_drift_days # già calcolata
    angle_per_REAL_anthaleja_day_deg = 360.0 / ATHDateTimeInterface.EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS
    longitude_arejal1_from_VE_deg = (270.0 + (effective_ws_reference_calendar_day * angle_per_REAL_anthaleja_day_deg)) % 360.0
    longitude_perihelion_from_arejal1_deg = effective_perihelion_calendar_day * angle_per_REAL_anthaleja_day_deg
    longitude_of_perihelion_from_VE_deg = (longitude_arejal1_from_VE_deg + longitude_perihelion_from_arejal1_deg) % 360.0
    longitude_of_perihelion_from_VE_rad_anthal = math.radians(longitude_of_perihelion_from_VE_deg)

    mean_ecliptic_longitude_rad_anthal = (mean_anomaly_rad_anthal + longitude_of_perihelion_from_VE_rad_anthal) % (2.0 * math.pi)
    
    eot_rad_angle = (y_eot_term * math.sin(2 * mean_ecliptic_longitude_rad_anthal) # Usa L_mean di Anthal
                  - 2 * ECCENTRICITY_ANTHAL_ORBIT * math.sin(mean_anomaly_rad_anthal) # Usa M di Anthal
                  + 4 * ECCENTRICITY_ANTHAL_ORBIT * y_eot_term * math.sin(mean_anomaly_rad_anthal) * math.cos(2 * mean_ecliptic_longitude_rad_anthal)
                  - 0.5 * y_eot_term**2 * math.sin(4 * mean_ecliptic_longitude_rad_anthal)
                  - 1.25 * ECCENTRICITY_ANTHAL_ORBIT**2 * math.sin(2 * mean_anomaly_rad_anthal))
    eot_seconds = eot_rad_angle * (SXD_CALENDAR / (2.0 * math.pi)) # Secondi dell'orologio
    nijel_results["equation_of_time_minutes_ATH"] = eot_seconds / SXI_CALENDAR

    # --- 4. Transito Solare (Mezzogiorno Solare Vero Locale) ---
    gradi_per_ora_CALENDAR = 360.0 / HXD_CALENDAR
    long_offset_hours_CALENDAR = longitude_A / gradi_per_ora_CALENDAR
    transit_mean_local_hour_float = (HXD_CALENDAR / 2.0) - long_offset_hours_CALENDAR
    transit_true_local_hour_float = transit_mean_local_hour_float - (eot_seconds / (IXH_CALENDAR * SXI_CALENDAR))
    transit_true_local_hour_float = transit_true_local_hour_float % HXD_CALENDAR
    if transit_true_local_hour_float < 0: transit_true_local_hour_float += HXD_CALENDAR
    
    transit_true_hour_int = int(transit_true_local_hour_float)
    transit_true_minute_float = (transit_true_local_hour_float - transit_true_hour_int) * IXH_CALENDAR
    transit_true_minute_int = int(transit_true_minute_float)
    transit_true_second_int = int(round((transit_true_minute_float - transit_true_minute_int) * SXI_CALENDAR))
    
    transit_true_dt_nijel = ATHDateTime.from_components(
        ath_date_obj.year, ath_date_obj.month_name, ath_date_obj.day, 
        transit_true_hour_int, transit_true_minute_int, transit_true_second_int, 
        ath_timezone_obj=ref_timezone_for_output
    )
    nijel_results["transit_true_local"] = transit_true_dt_nijel
    
    # --- 5. Eventi di Alba/Tramonto e Crepuscoli ---
    # REFRACTION_DEG_COMMON è una costante di modulo
    H_SUNRISE_SUNSET = -(REFRACTION_DEG_COMMON + dynamic_angular_radius_nijel_deg)
    
    # Recupera le altezze angolari dei crepuscoli da ANTHAL_PARAMS (o da un dizionario dedicato ai crepuscoli)
    # oppure usa valori di default se non presenti in anthal_params (per ora le leggo da NIJEL_PARAMS come prima)
    H_GOLDEN_LOWER_ATH = NIJEL_PARAMS.get("H_GOLDEN_LOWER_ATH", -4.666666666667) 
    H_GOLDEN_UPPER_ATH = NIJEL_PARAMS.get("H_GOLDEN_UPPER_ATH", 7.0)
    H_CIVIL_TWILIGHT_ATH = NIJEL_PARAMS.get("H_CIVIL_TWILIGHT_ATH", -7.0)
    H_BLUE_CLEAR_LOWER_ATH = H_CIVIL_TWILIGHT_ATH 
    H_BLUE_CLEAR_UPPER_ATH = H_GOLDEN_LOWER_ATH
    H_BLUE_DEEP_LOWER_ATH = NIJEL_PARAMS.get("H_BLUE_DEEP_LOWER_ATH", -9.333333333333)
    H_BLUE_DEEP_UPPER_ATH = H_CIVIL_TWILIGHT_ATH
    H_NAUTICAL_TWILIGHT_ATH = NIJEL_PARAMS.get("H_NAUTICAL_TWILIGHT_ATH", -14.0)
    H_ASTRONOMICAL_TWILIGHT_ATH = NIJEL_PARAMS.get("H_ASTRONOMICAL_TWILIGHT_ATH", -21.0)

    # Tutte le chiamate a _calculate_event_times_for_body_internal usano lat_rad (latitudine osservatore)
    # e transit_true_dt_nijel come riferimento temporale.
    sr_act, ss_act, n_act = _calculate_event_times_for_body_internal(H_SUNRISE_SUNSET, delta_rad_nijel, transit_true_dt_nijel, lat_rad, "Nijel-Ufficiale", ref_timezone_for_output)
    nijel_results["sunrise_actual"] = sr_act; nijel_results["sunset_actual"] = ss_act
    if not nijel_results.get("notes"): nijel_results["notes"] = []
    nijel_results["notes"].extend(n_act)
    
    # (Calcolo di tutti gli altri eventi crepuscolari come nella versione precedente, usando le H_... definite sopra)
    ghmbs_n, ghes_n, n_ghl = _calculate_event_times_for_body_internal(H_GOLDEN_LOWER_ATH, delta_rad_nijel, transit_true_dt_nijel, lat_rad, "Nijel-GoldenLow", ref_timezone_for_output); ghmes_n, ghbes_n, n_ghu = _calculate_event_times_for_body_internal(H_GOLDEN_UPPER_ATH, delta_rad_nijel, transit_true_dt_nijel, lat_rad, "Nijel-GoldenUp", ref_timezone_for_output)
    nijel_results.update({"golden_hour_morning_begin": ghmbs_n, "golden_hour_morning_end": ghmes_n, "golden_hour_evening_begin": ghbes_n, "golden_hour_evening_end": ghes_n}); nijel_results["notes"].extend(n_ghl); nijel_results["notes"].extend(n_ghu)
    bhc_m_begin, bhc_e_end, n_bhcl = _calculate_event_times_for_body_internal(H_BLUE_CLEAR_LOWER_ATH, delta_rad_nijel, transit_true_dt_nijel, lat_rad, "Nijel-BlueClearLow", ref_timezone_for_output)
    nijel_results.update({"blue_hour_clear_morning_begin": bhc_m_begin, "blue_hour_clear_morning_end": ghmbs_n, "blue_hour_clear_evening_begin": ghes_n, "blue_hour_clear_evening_end": bhc_e_end}); nijel_results["notes"].extend(n_bhcl)
    bhd_m_begin, bhd_e_end, n_bhdl = _calculate_event_times_for_body_internal(H_BLUE_DEEP_LOWER_ATH, delta_rad_nijel, transit_true_dt_nijel, lat_rad, "Nijel-BlueDeepLow", ref_timezone_for_output)
    nijel_results.update({"blue_hour_deep_morning_begin": bhd_m_begin, "blue_hour_deep_morning_end": bhc_m_begin, "blue_hour_deep_evening_begin": bhc_e_end, "blue_hour_deep_evening_end": bhd_e_end}); nijel_results["notes"].extend(n_bhdl)
    nijel_results.update({"civil_twilight_morning_end": bhc_m_begin, "civil_twilight_evening_begin": bhc_e_end})
    ntmes_n, ntbes_n, n_nt = _calculate_event_times_for_body_internal(H_NAUTICAL_TWILIGHT_ATH, delta_rad_nijel, transit_true_dt_nijel, lat_rad, "Nijel-Nautical", ref_timezone_for_output)
    nijel_results.update({"nautical_twilight_morning_end": ntmes_n, "nautical_twilight_evening_begin": ntbes_n}); nijel_results["notes"].extend(n_nt)
    atmes_n, atbes_n, n_at = _calculate_event_times_for_body_internal(H_ASTRONOMICAL_TWILIGHT_ATH, delta_rad_nijel, transit_true_dt_nijel, lat_rad, "Nijel-Astro", ref_timezone_for_output)
    nijel_results.update({"astronomical_twilight_morning_end": atmes_n, "astronomical_twilight_evening_begin": atbes_n}); nijel_results["notes"].extend(n_at)

    # --- 6. Mezzanotte Solare ---
    if transit_true_dt_nijel:
        half_day_interval_calendar = ATHDateInterval(hours = HXD_CALENDAR // 2)
        solar_midnight_dt_temp = transit_true_dt_nijel.add(half_day_interval_calendar)
        nijel_results["solar_midnight"] = ATHDateTime.from_components(
            solar_midnight_dt_temp.year, solar_midnight_dt_temp.month_name, solar_midnight_dt_temp.day,
            solar_midnight_dt_temp.hour, solar_midnight_dt_temp.minute, solar_midnight_dt_temp.second,
            ath_timezone_obj=ref_timezone_for_output)
    else:
        nijel_results["solar_midnight"] = None
        
    # --- Pulizia Note e Dati Interni per Altre Funzioni ---
    if not nijel_results.get("notes"): nijel_results["notes"] = []
    nijel_results["notes"].append(f"EoT={eot_seconds/SXI_CALENDAR:.2f} min_orologio_Anthaleja.")
    nijel_results["notes"] = sorted(list(set(nijel_results["notes"])))

    nijel_results["internals"] = {
        "true_ecliptic_longitude_rad_nijel": true_ecliptic_longitude_rad_nijel_apparent, # Longitudine apparente di Nijel
        "transit_true_dt_nijel_obj": transit_true_dt_nijel, # Oggetto ATHDateTime del transito
        "physical_radius_nijel_m": NIJEL_PHYSICAL_RADIUS_M, # Raggio fisico di Nijel
        "current_distance_anthal_nijel_m": current_distance_anthal_nijel_m, # Distanza attuale
        "dynamic_angular_radius_nijel_deg": dynamic_angular_radius_nijel_deg # Raggio angolare attuale
    }
    return nijel_results

## --- Funzioni Helper per il Calcolo della Posizione e degli Eventi delle Lune --- ##
def _get_moon_true_anomaly_at_moment(
    moon_name: str,
    ath_date_obj: ATHDateTimeInterface,
    moon_params_dict: Dict[str, Dict[str, Any]] # Es. {"Leea": LEEA_PARAMS, "Mirahn": MIRAHN_PARAMS}
) -> float:
    """
    Calcola l'anomalia vera (ν) di una luna (in gradi) per un dato istante.
    L'anomalia vera è l'angolo polare che descrive la posizione di un corpo
    orbitante attorno al fuoco principale dell'ellisse (il pianeta Anthal, in questo caso),
    rispetto alla direzione del periasse (il punto di minima distanza della luna da Anthal).
    È uno degli elementi orbitali che definisce la posizione della luna nella sua orbita.
    Args:
        moon_name: Il nome della luna (es. "Leea", "Mirahn").
        ath_date_obj: L'oggetto ATHDateTimeInterface che rappresenta l'istante
                    per cui calcolare l'anomalia vera.
        moon_params_dict: Un dizionario che mappa i nomi delle lune ai loro
                        rispettivi dizionari di parametri orbitali (es. LEEA_PARAMS).
                        Deve contenere chiavi come "P_s" (periodo sidereo in secondi),
                        "e" (eccentricità), "M0_deg" (anomalia media all'epoca).
    Returns:
        float: L'anomalia vera della luna in gradi, normalizzata nell'intervallo [0, 360).
    Raises:
        ValueError: Se i parametri orbitali per la luna specificata non vengono trovati.
    """
    moon_orbital_params = moon_params_dict.get(moon_name)
    if not moon_orbital_params:
        raise ValueError(f"Parametri orbitali non trovati per la luna: {moon_name} in moon_params_dict.")

    # Estrai i parametri orbitali fisici della luna
    P_s_earth_sec = moon_orbital_params["P_s"]       # Periodo orbitale sidereo in secondi TERRESTRI
    e_moon = moon_orbital_params["e"]                # Eccentricità dell'orbita lunare
    M0_deg_moon = moon_orbital_params["M0_deg"]      # Anomalia media della luna all'epoca definita

    # 1. Calcola il tempo trascorso (in secondi terrestri) dall'epoca
    #    definita per i parametri orbitali della luna.
    #    EPOCH_LUNAR_PARAMS_UNIX_TS è un timestamp Unix terrestre di riferimento.
    seconds_since_lunar_epoch = ath_date_obj.get_earth_timestamp() - EPOCH_LUNAR_PARAMS_UNIX_TS
    
    # 2. Calcola l'Anomalia Media (M) attuale della luna.
    #    M = M0 + n * (t - t0), dove n è il moto medio e (t - t0) è seconds_since_lunar_epoch.
    mean_motion_moon_rad_per_earth_sec = (2.0 * math.pi) / P_s_earth_sec # Moto medio in radianti/secondo
    M0_rad_moon = math.radians(M0_deg_moon) # Anomalia media all'epoca in radianti
    
    mean_anomaly_rad_moon = (M0_rad_moon + mean_motion_moon_rad_per_earth_sec * seconds_since_lunar_epoch)
    
    # Normalizza l'anomalia media all'intervallo [0, 2*pi) radianti
    mean_anomaly_rad_moon = mean_anomaly_rad_moon % (2.0 * math.pi)
    if mean_anomaly_rad_moon < 0: # Il modulo % in Python può restituire negativi se il dividendo è negativo
        mean_anomaly_rad_moon += (2.0 * math.pi)
    
    # 3. Risolvi l'Equazione di Keplero M = E - e*sin(E) per ottenere l'Anomalia Eccentrica (E).
    eccentric_anomaly_rad_moon = solve_kepler_equation(mean_anomaly_rad_moon, e_moon)
    
    # 4. Calcola l'Anomalia Vera (ν) dall'Anomalia Eccentrica (E).
    #    Si utilizza la formula basata su atan2 per una corretta determinazione del quadrante:
    #    ν = atan2( sqrt(1-e^2)*sin(E), cos(E)-e )
    cos_E = math.cos(eccentric_anomaly_rad_moon)
    sin_E = math.sin(eccentric_anomaly_rad_moon)
    
    # Componente y per atan2
    true_anomaly_rad_moon_y_component = math.sqrt(1 - e_moon**2) * sin_E
    # Componente x per atan2
    true_anomaly_rad_moon_x_component = cos_E - e_moon
    
    true_anomaly_rad_moon = math.atan2(true_anomaly_rad_moon_y_component, true_anomaly_rad_moon_x_component)
    
    # Normalizza l'anomalia vera all'intervallo [0, 2*pi) radianti,
    # poiché atan2 restituisce valori in [-pi, pi].
    if true_anomaly_rad_moon < 0:
        true_anomaly_rad_moon += (2.0 * math.pi)
        
    # 5. Converti l'anomalia vera da radianti a gradi per il valore di ritorno.
    return math.degrees(true_anomaly_rad_moon)

def _get_moon_elongation_at_moment(
    moon_name: str,
    ath_date_obj: ATHDateTimeInterface,
    moon_params_dict: Dict[str, Dict[str, Any]],
    anthal_params_for_nijel_lon: Dict[str, Any]
) -> float:
    """
    Calcola l'elongazione eclittica della luna (in gradi) rispetto a Nijel
    per un dato istante.
    L'elongazione è definita come (LongitudineEclitticaLuna - LongitudineEclitticaNijel).
    Un valore positivo indica che la luna si trova a Est di Nijel (longitudine maggiore)
    sull'eclittica. L'angolo è normalizzato nell'intervallo [0, 360).
    Fasi Lunari Approssimative basate sull'Elongazione:
    - Luna Nuova: ~0° (o ~360°)
    - Primo Quarto: ~90°
    - Luna Piena: ~180°
    - Ultimo Quarto: ~270°
    Args:
        moon_name: Il nome della luna (es. "Leea", "Mirahn").
        ath_date_obj: L'oggetto ATHDateTimeInterface che rappresenta l'istante
                    per cui calcolare l'elongazione.
        moon_params_dict: Un dizionario che mappa i nomi delle lune ai loro
                        rispettivi dizionari di parametri orbitali.
                        Deve contenere chiavi come "P_s", "e", "M0_deg", "omega0_deg".
    Returns:
        float: L'elongazione della luna in gradi, normalizzata a [0, 360).
    Raises:
        ValueError: Se i parametri orbitali per la luna specificata non vengono trovati.
    """
    moon_orbital_params = moon_params_dict.get(moon_name)
    if not moon_orbital_params:
        raise ValueError(f"Parametri orbitali non trovati per la luna: {moon_name} in moon_params_dict.")

    # 1. Calcola la longitudine eclittica vera di Nijel per l'istante corrente.
    #    _get_true_ecliptic_longitude_at_moment necessita di NIJEL_PARAMS.
    #    Assumiamo che NIJEL_PARAMS sia una variabile a livello di modulo o altrimenti accessibile.
    nijel_true_ecliptic_lon_deg = _get_true_ecliptic_longitude_at_moment(
        ath_date_obj,
        anthal_params_for_nijel_lon # Passa i parametri di Anthal per il calcolo della long. di Nijel
    )

    # 2. Calcola la longitudine eclittica vera della luna per l'istante corrente.
    #    Estrai i parametri orbitali fisici della luna.
    P_s_earth_sec = moon_orbital_params["P_s"]       # Periodo orbitale sidereo in secondi TERRESTRI
    e_moon = moon_orbital_params["e"]                # Eccentricità dell'orbita lunare
    M0_deg_moon = moon_orbital_params["M0_deg"]      # Anomalia media della luna all'epoca
    omega0_deg_moon = moon_orbital_params["omega0_deg"] # Longitudine del periasse della luna all'epoca,
                                                    # misurata dal punto vernale di riferimento.

    # Calcola il tempo trascorso (in secondi terrestri) dall'epoca dei parametri lunari.
    seconds_since_lunar_epoch = ath_date_obj.get_earth_timestamp() - EPOCH_LUNAR_PARAMS_UNIX_TS
    
    # Calcola l'Anomalia Media (M) attuale della luna.
    mean_motion_moon_rad_per_earth_sec = (2.0 * math.pi) / P_s_earth_sec
    M0_rad_moon = math.radians(M0_deg_moon)
    mean_anomaly_rad_moon = (M0_rad_moon + mean_motion_moon_rad_per_earth_sec * seconds_since_lunar_epoch)
    mean_anomaly_rad_moon = mean_anomaly_rad_moon % (2.0 * math.pi)
    if mean_anomaly_rad_moon < 0:
        mean_anomaly_rad_moon += (2.0 * math.pi)
    
    # Risolvi l'Equazione di Keplero per l'Anomalia Eccentrica (E).
    eccentric_anomaly_rad_moon = solve_kepler_equation(mean_anomaly_rad_moon, e_moon)
    
    # Calcola l'Anomalia Vera (ν) dall'Anomalia Eccentrica (E) usando atan2.
    cos_E = math.cos(eccentric_anomaly_rad_moon)
    sin_E = math.sin(eccentric_anomaly_rad_moon)
    true_anomaly_rad_moon_y_comp = math.sqrt(1 - e_moon**2) * sin_E
    true_anomaly_rad_moon_x_comp = cos_E - e_moon
    true_anomaly_rad_moon = math.atan2(true_anomaly_rad_moon_y_comp, true_anomaly_rad_moon_x_comp)
    if true_anomaly_rad_moon < 0: # Normalizza a [0, 2*pi)
        true_anomaly_rad_moon += (2.0 * math.pi)
        
    # Calcola la Longitudine Eclittica Vera della Luna (lambda_moon).
    # lambda_moon = Anomalia Vera (ν) + Longitudine del Periasse (omega_bar).
    # omega0_deg_moon (Long. del Periasse) è misurata dal punto vernale, come le altre longitudini.
    omega0_rad_moon = math.radians(omega0_deg_moon)
    true_ecliptic_longitude_rad_moon = (true_anomaly_rad_moon + omega0_rad_moon) % (2.0 * math.pi)
    # Non è necessaria un'ulteriore normalizzazione if <0 se i componenti sono già in [0, 2pi)
    # e % (2pi) viene applicato.
    
    # 3. Calcola l'elongazione.
    # Elongazione = LongitudineEclitticaLuna - LongitudineEclitticaNijel
    elongation_rad = true_ecliptic_longitude_rad_moon - math.radians(nijel_true_ecliptic_lon_deg)
    elongation_deg = math.degrees(elongation_rad)
    
    # Normalizza l'elongazione finale all'intervallo [0, 360) gradi.
    normalized_elongation_deg = elongation_deg % 360.0
    if normalized_elongation_deg < 0: # L'operatore % in Python può restituire risultati negativi.
        normalized_elongation_deg += 360.0
        
    return normalized_elongation_deg

def _internal_calculate_moon_info(
    moon_name: str,
    ath_date_obj: ATHDateTimeInterface, # Istante per cui calcolare
    latitude_A: float,                  # Latitudine dell'osservatore su Anthal (per rise/set)
    axial_tilt_deg_planet: float,       # Inclinazione assiale del pianeta Anthal (ε_planet)
    nijel_data_for_moon_calc: Dict[str, Any], # Dati precalcolati per Nijel per questo istante
    moon_orbital_params: Dict[str, Any],      # Parametri orbitali specifici della luna
    ref_timezone_for_output: Optional[ATHDateTimeZoneInterface] # Fuso per gli ATHDateTime restituiti
) -> Dict[str, Any]:
    """
    Calcola un set completo di informazioni astronomiche per una specifica luna
    (Leea o Mirahn) in un dato istante, come vista da Anthal.

    Questa funzione determina la posizione 3D della luna (longitudine λ e latitudine β
    eclittiche), la sua distanza (r), l'anomalia vera (ν), la posizione del suo nodo
    ascendente (Ω), l'elongazione rispetto a Nijel (per la fase), la percentuale di
    illuminazione, la declinazione equatoriale (δ), e gli orari approssimativi di
    levata, transito e tramonto sull'orologio del calendario Anthaleja.

    Args:
        moon_name: Nome della luna ("Leea" o "Mirahn").
        ath_date_obj: Istante ATHDateTimeInterface per cui effettuare i calcoli.
        latitude_A: Latitudine dell'osservatore su Anthal (in gradi), usata per
                    i calcoli di levata/tramonto.
        axial_tilt_deg_planet: Inclinazione assiale del pianeta Anthal (ε_planet, in gradi),
                            usata per convertire coordinate eclittiche in equatoriali (declinazione).
        nijel_data_for_moon_calc: Dizionario contenente dati di Nijel per l'istante corrente,
                                ottenuti da `_internal_calculate_nijel_info`. Deve contenere
                                almeno "true_ecliptic_longitude_rad_nijel" e
                                "transit_true_dt_nijel_obj".
        moon_orbital_params: Dizionario dei parametri orbitali e fisici della luna.
                            Chiavi attese: "P_s" (periodo sidereo), "e" (eccentricità),
                            "M0_deg" (Anomalia Media all'epoca),
                            "omega0_deg" (Argomento del Periasse all'epoca, ω₀, misurato dal nodo),
                            "i_deg" (Inclinazione orbitale, i),
                            "initial_ascending_node_lon_deg" (Long. Nodo Asc. all'epoca, Ω₀),
                            "nodal_precession_rate_deg_per_anthaleja_year" (tasso precessione Ω),
                            "R_phys_m" (Raggio fisico), "a_m" (Semiasse maggiore).
        ref_timezone_for_output: Fuso orario desiderato per gli oggetti ATHDateTime
                                restituiti (es. transito, levata, tramonto).

    Returns:
        Dict[str, Any]: Dizionario con i dati calcolati per la luna, incluse "notes"
                        e potenziali "error".
    """
    results_moon: Dict[str, Any] = {"notes": []}
    
    # Converte l'inclinazione assiale del pianeta e la latitudine dell'osservatore in radianti
    axial_tilt_rad_planet = math.radians(axial_tilt_deg_planet) # ε_planet
    lat_rad_observer = math.radians(latitude_A)                 # φ_obs

    # Estrae dati essenziali di Nijel (già calcolati per l'istante ath_date_obj)
    true_ecliptic_longitude_rad_nijel = nijel_data_for_moon_calc.get("true_ecliptic_longitude_rad_nijel") # λ_Nijel
    transit_true_dt_nijel: Optional[ATHDateTimeInterface] = nijel_data_for_moon_calc.get("transit_true_dt_nijel_obj")

    if true_ecliptic_longitude_rad_nijel is None or transit_true_dt_nijel is None:
        error_msg = f"Dati essenziali di Nijel (longitudine λ o transito) mancanti per calcolo luna {moon_name}."
        results_moon["error"] = error_msg
        results_moon["notes"].append(error_msg)
        return results_moon

    # Estrai parametri orbitali della luna
    P_s_earth_sec = moon_orbital_params["P_s"]      # P_sid (Periodo orbitale sidereo in secondi terrestri)
    e_moon = moon_orbital_params["e"]               # e (Eccentricità)
    M0_deg_moon = moon_orbital_params["M0_deg"]     # M₀ (Anomalia Media all'epoca, gradi)
    omega0_deg_moon = moon_orbital_params["omega0_deg"] # ω₀ (Argomento del Periasse all'epoca, gradi, misurato dal Nodo Ascendente)
    i_deg_moon = moon_orbital_params["i_deg"]        # i (Inclinazione orbitale rispetto all'eclittica di Anthal, gradi)
    initial_node_lon_deg = moon_orbital_params["initial_ascending_node_lon_deg"] # Ω₀ (Long. Nodo Asc. all'epoca, gradi)
    node_precession_rate_deg_per_year = moon_orbital_params["nodal_precession_rate_deg_per_anthaleja_year"] # dΩ/dt (gradi/anno Anthaleja)
    
    R_phys_m_moon = moon_orbital_params["R_phys_m"] # R_moon (Raggio fisico della luna, m)
    a_m_moon = moon_orbital_params["a_m"]           # a_moon (Semiasse maggiore dell'orbita lunare, m)

    # --- 1. Calcolo Posizione Orbitale della Luna (Anomalie) ---
    current_earth_timestamp = ath_date_obj.get_earth_timestamp()
    # Tempo (in secondi terrestri) trascorso dall'epoca definita per i parametri orbitali della luna.
    seconds_since_lunar_epoch = current_earth_timestamp - EPOCH_LUNAR_PARAMS_UNIX_TS # EPOCH_LUNAR_PARAMS_UNIX_TS è globale/di modulo
    
    # Moto medio (n_moon) in radianti/secondo terrestre
    mean_motion_rad_s_moon = (2.0 * math.pi) / P_s_earth_sec
    M0_rad_moon = math.radians(M0_deg_moon) # M₀ in radianti
    
    # Anomalia Media attuale (M_moon)
    mean_anomaly_rad_moon = (M0_rad_moon + mean_motion_rad_s_moon * seconds_since_lunar_epoch)
    mean_anomaly_rad_moon = mean_anomaly_rad_moon % (2.0 * math.pi) # Normalizza a [0, 2π)
    if mean_anomaly_rad_moon < 0: mean_anomaly_rad_moon += (2.0 * math.pi)
    
    # Anomalia Eccentrica (E_moon)
    eccentric_anomaly_rad_moon = solve_kepler_equation(mean_anomaly_rad_moon, e_moon)
    
    # Anomalia Vera (ν_moon, nu_moon)
    cos_E = math.cos(eccentric_anomaly_rad_moon); sin_E = math.sin(eccentric_anomaly_rad_moon)
    true_anomaly_rad_moon_y_comp = math.sqrt(1 - e_moon**2) * sin_E
    true_anomaly_rad_moon_x_comp = cos_E - e_moon
    true_anomaly_rad_moon = math.atan2(true_anomaly_rad_moon_y_comp, true_anomaly_rad_moon_x_comp)
    if true_anomaly_rad_moon < 0: true_anomaly_rad_moon += (2.0 * math.pi) # Normalizza a [0, 2π)

    # --- 2. Calcolo Coordinate Eclittiche della Luna (Longitudine λ_moon, Latitudine β_moon) ---
    # Argomento del Periasse (ω_moon) all'epoca (misurato dal Nodo Ascendente)
    omega0_rad_moon = math.radians(omega0_deg_moon) # ω₀ in radianti
    
    # Longitudine del Nodo Ascendente (Ω_moon) attuale, considerando la precessione.
    # ORBITAL_PERIOD_EARTH_SECONDS è la durata di un anno fisico di Anthal in secondi terrestri.
    years_since_lunar_epoch = seconds_since_lunar_epoch / ATHDateTimeInterface.ORBITAL_PERIOD_EARTH_SECONDS
    current_node_lon_deg = (initial_node_lon_deg + (years_since_lunar_epoch * node_precession_rate_deg_per_year)) % 360.0
    if current_node_lon_deg < 0: current_node_lon_deg += 360.0 # Normalizza a [0, 360)
    results_moon["current_ascending_node_lon_deg"] = current_node_lon_deg
    current_node_lon_rad = math.radians(current_node_lon_deg) # Ω_moon in radianti

    # Argomento della Latitudine (u_moon): angolo dalla LAN alla luna, nel piano orbitale della luna.
    # u_moon = Anomalia Vera (ν_moon) + Argomento del Periasse (ω_moon, misurato dal nodo).
    argument_of_latitude_rad_moon = (true_anomaly_rad_moon + omega0_rad_moon) % (2.0 * math.pi)
    
    # Inclinazione dell'orbita lunare (i_moon)
    i_rad_moon = math.radians(i_deg_moon)

    # Latitudine Eclittica (β_moon)
    # sin(β_moon) = sin(i_moon) * sin(u_moon)
    sin_beta_moon = math.sin(i_rad_moon) * math.sin(argument_of_latitude_rad_moon)
    # Clamp per sicurezza numerica prima di asin
    if sin_beta_moon > 1.0: sin_beta_moon = 1.0
    elif sin_beta_moon < -1.0: sin_beta_moon = -1.0
    beta_rad_moon = math.asin(sin_beta_moon)
    results_moon["ecliptic_latitude_deg"] = math.degrees(beta_rad_moon)

    # Longitudine Eclittica (λ_moon)
    # λ_moon = atan2(sin(u_moon)*cos(i_moon), cos(u_moon)) + Ω_moon
    # Dove u_moon è argument_of_latitude_rad_moon.
    y_for_lambda_moon = math.sin(argument_of_latitude_rad_moon) * math.cos(i_rad_moon)
    x_for_lambda_moon = math.cos(argument_of_latitude_rad_moon)
    lambda_from_node_rad = math.atan2(y_for_lambda_moon, x_for_lambda_moon)
    
    true_ecliptic_longitude_rad_moon = (lambda_from_node_rad + current_node_lon_rad) % (2.0 * math.pi)
    if true_ecliptic_longitude_rad_moon < 0: true_ecliptic_longitude_rad_moon += (2.0 * math.pi) # Normalizza
    results_moon["true_ecliptic_longitude_degrees"] = math.degrees(true_ecliptic_longitude_rad_moon)

    # --- 3. Calcoli Derivati (Fase, Declinazione Equatoriale, Distanza) ---
    # Elongazione rispetto a Nijel (Δλ)
    elongation_rad = (true_ecliptic_longitude_rad_moon - true_ecliptic_longitude_rad_nijel)
    # Normalizza l'elongazione a [-π, +π) per il calcolo della fase, poi a [0, 2π) per output
    elongation_for_phase_rad = elongation_rad % (2.0 * math.pi)
    if elongation_for_phase_rad > math.pi: elongation_for_phase_rad -= (2.0 * math.pi) # Range [-pi, pi]

    illuminated_fraction = (1 - math.cos(elongation_for_phase_rad)) / 2.0
    results_moon["phase_percent"] = illuminated_fraction * 100.0
    
    elongation_deg_output = math.degrees(elongation_rad) % 360.0 # Per output [0, 360)
    if elongation_deg_output < 0: elongation_deg_output += 360.0
    results_moon["elongation_degrees"] = elongation_deg_output
    
    # Declinazione Equatoriale della Luna (δ_moon)
    # sin(δ_moon) = sin(β_moon) * cos(ε_planet) + cos(β_moon) * sin(ε_planet) * sin(λ_moon)
    sin_decl_moon = math.sin(beta_rad_moon) * math.cos(axial_tilt_rad_planet) + \
                    math.cos(beta_rad_moon) * math.sin(axial_tilt_rad_planet) * math.sin(true_ecliptic_longitude_rad_moon)
    if sin_decl_moon > 1.0: sin_decl_moon = 1.0 # Clamp
    elif sin_decl_moon < -1.0: sin_decl_moon = -1.0
    delta_rad_moon = math.asin(sin_decl_moon)
    results_moon["declination_degrees"] = math.degrees(delta_rad_moon)

    # Distanza attuale da Anthal (r_moon) e distanze teoriche agli apsidi
    # r_moon = a_moon * (1 - e_moon^2) / (1 + e_moon * cos(ν_moon))
    current_distance_m = a_m_moon * (1 - e_moon**2) / (1 + e_moon * math.cos(true_anomaly_rad_moon)) # Usa true_anomaly_rad_moon
    results_moon["current_distance_meters"] = current_distance_m
    results_moon["distance_perianthal_meters"] = a_m_moon * (1 - e_moon) # r_periasse = a(1-e)
    results_moon["distance_apoanthal_meters"] = a_m_moon * (1 + e_moon)   # r_apoasse = a(1+e)

    # --- 4. Orari di Transito, Levata e Tramonto (sull'orologio del CALENDARIO) ---
    if transit_true_dt_nijel: # Verifica che il transito di Nijel sia stato calcolato
        # Offset del transito della luna rispetto a Nijel, in secondi DELL'OROLOGIO
        # L'elongazione qui è la differenza di longitudine, una frazione di 2*pi
        moon_transit_offset_clock_seconds = (elongation_rad / (2.0 * math.pi)) * ATHDateTimeInterface.SXD_CALENDAR
        
        transit_nijel_true_abs_sec_A_epoch_calendar = transit_true_dt_nijel.seconds_since_A_epoch
        
        moon_transit_abs_sec_A_epoch_calendar = transit_nijel_true_abs_sec_A_epoch_calendar + moon_transit_offset_clock_seconds
        
        moon_transit_earth_ts = ATHDateTimeInterface.EPOCH + moon_transit_abs_sec_A_epoch_calendar
        moon_transit_dt = ATHDateTime(datetime.fromtimestamp(moon_transit_earth_ts, tz=timezone.utc), ath_timezone_obj=ref_timezone_for_output)
        results_moon["transit_approx"] = moon_transit_dt
        
        # Calcolo levata/tramonto usando _calculate_event_times_for_body_internal
        angular_radius_moon_rad_approx = R_phys_m_moon / a_m_moon if a_m_moon > 0 else 0.0 # Raggio angolare approssimato
        H0_MOON_DEG = - (REFRACTION_DEG_COMMON + math.degrees(angular_radius_moon_rad_approx))
        
        mr, ms, notes_m_srss = _calculate_event_times_for_body_internal(
            H0_MOON_DEG, delta_rad_moon, moon_transit_dt, lat_rad_observer, # Passa lat_rad_observer
            moon_name, ref_timezone_for_output
        )
        results_moon["rise"] = mr
        results_moon["set"] = ms
        if not results_moon.get("notes"): results_moon["notes"] = []
        results_moon["notes"].extend(notes_m_srss)
    else: # transit_true_dt_nijel è None
        results_moon["notes"].append(f"Transito di Nijel non disponibile, impossibile calcolare transito/levata/tramonto per {moon_name}.")
        results_moon["transit_approx"] = None
        results_moon["rise"] = None
        results_moon["set"] = None
        
    results_moon["notes"] = sorted(list(set(results_moon["notes"]))) # Rimuovi duplicati e ordina
    
    return results_moon

def find_next_moon_apsis(
    moon_name: str,
    start_date: ATHDateTimeInterface,
    moon_params_dict: Dict[str, Dict[str, Any]], # Es. {"Leea": LEEA_PARAMS, ...}
    atz_timezone: ATHDateTimeZoneInterface       # Istanza di ATHDateTimeZone("ATZ")
) -> Tuple[str, ATHDateTimeInterface, float]:    # Nome evento, Data evento (in ATZ), Distanza (m)
    """
    Trova il prossimo apside orbitale (Perianthal o Apoanthal) per una data luna
    a partire da una specifica data/ora di inizio.
    Utilizza una ricerca a due fasi (prima oraria, poi al minuto) per determinare
    il momento dell'evento con una buona precisione.
    Args:
        moon_name: Il nome della luna (es. "Leea", "Mirahn").
        start_date: L'oggetto ATHDateTimeInterface da cui iniziare la ricerca.
        moon_params_dict: Dizionario che mappa i nomi delle lune ai loro parametri orbitali.
                        Deve contenere "a_m" (semiasse maggiore) e "e" (eccentricità)
                        per la luna specificata, oltre ai parametri usati da
                        _get_moon_true_anomaly_at_moment.
        atz_timezone: L'istanza del fuso orario ATZ, usata per impostare il fuso
                    orario dell'oggetto ATHDateTimeInterface restituito.
    Returns:
        Tuple[str, ATHDateTimeInterface, float]:
            - Nome dell'evento apside ("Perianthal" o "Apoanthal").
            - Oggetto ATHDateTimeInterface (nel fuso ATZ) che rappresenta la data e l'ora
            approssimata (al minuto) dell'apside.
            - Distanza teorica della luna da Anthal (in metri) al momento dell'apside.
    Raises:
        ValueError: Se i parametri orbitali per la luna non sono trovati.
        RuntimeError: Se l'apside non viene trovato entro i limiti di ricerca.
    """
    moon_orbital_params = moon_params_dict.get(moon_name)
    if not moon_orbital_params:
        raise ValueError(f"Parametri orbitali non trovati per la luna '{moon_name}' in moon_params_dict.")

    # Parametri orbitali per il calcolo della distanza all'apside
    a_m_moon = moon_orbital_params["a_m"] # Semiasse maggiore in metri
    e_moon = moon_orbital_params["e"]     # Eccentricità

    # --- FASE 1: Ricerca Grossolana (a passi di 1 ora del calendario) ---
    # Calcola l'anomalia vera (ν) della luna alla data di partenza
    current_true_anomaly_deg_coarse = _get_moon_true_anomaly_at_moment(moon_name, start_date, moon_params_dict)
    
    next_target_anomaly_val: float
    next_event_name: str
    expected_distance_at_apsis_m: float

    # Determina il prossimo target di anomalia vera e il nome dell'evento.
    # Perianthal (ν ≈ 0°/360°), Apoanthal (ν ≈ 180°).
    # Se l'anomalia corrente è < 179.9° (leggero buffer), cerchiamo l'Apoanthal a 180°.
    # Altrimenti (se è >= 179.9°), cerchiamo il Perianthal successivo (passaggio per 0°/360°).
    if 0 <= current_true_anomaly_deg_coarse < 179.9:
        next_target_anomaly_val = 180.0
        next_event_name = "Apoanthal"
        expected_distance_at_apsis_m = a_m_moon * (1 + e_moon) # Distanza all'apoasse
    else:
        next_target_anomaly_val = 360.0 # Target tecnico per il passaggio a 0° (Perianthal)
        next_event_name = "Perianthal"
        expected_distance_at_apsis_m = a_m_moon * (1 - e_moon) # Distanza al periasse

    search_date_coarse = start_date
    coarse_search_interval = ATHDateInterval(hours=1) # Intervallo di ricerca grossolana
    
    # Stima del numero massimo di iterazioni per la ricerca grossolana:
    # Circa 0.75 del periodo orbitale della luna, in passi orari.
    period_seconds_sidereal = moon_orbital_params["P_s"]
    seconds_per_calendar_hour = ATHDateTimeInterface.IXH * ATHDateTimeInterface.SXI
    max_coarse_iterations = int(((period_seconds_sidereal / 2.0) * 1.2) / seconds_per_calendar_hour) # ~60% di un periodo orbitale
    if max_coarse_iterations < 24: max_coarse_iterations = 24 # Minimo di 24 passi orari
    if max_coarse_iterations > (ATHDateTimeInterface.DXY_CALENDAR * ATHDateTimeInterface.HXD_CALENDAR // 4) : # Limite superiore generoso
        max_coarse_iterations = (ATHDateTimeInterface.DXY_CALENDAR * ATHDateTimeInterface.HXD_CALENDAR // 4)


    previous_anomaly_deg_coarse = current_true_anomaly_deg_coarse
    start_of_fine_search_window: Optional[ATHDateTimeInterface] = None

    for _ in range(max_coarse_iterations):
        search_date_coarse_next_step = search_date_coarse.add(coarse_search_interval)
        current_true_anomaly_deg_coarse_val = _get_moon_true_anomaly_at_moment(moon_name, search_date_coarse_next_step, moon_params_dict)
        
        crossed_target = False
        if next_event_name == "Perianthal": # Target è 0°/360°
            # L'attraversamento avviene quando si passa da >180° (es. 350°) a <180° (es. 10°)
            if previous_anomaly_deg_coarse >= 180.0 and current_true_anomaly_deg_coarse_val < 180.0:
                crossed_target = True
        elif next_event_name == "Apoanthal": # Target è 180°
            # L'attraversamento avviene quando si passa da <180° a >=180°
            if previous_anomaly_deg_coarse < 180.0 and current_true_anomaly_deg_coarse_val >= 180.0:
                crossed_target = True
        
        if crossed_target:
            start_of_fine_search_window = search_date_coarse # Memorizza l'ora *prima* dell'attraversamento
            break 
        
        previous_anomaly_deg_coarse = current_true_anomaly_deg_coarse_val
        search_date_coarse = search_date_coarse_next_step

    if not start_of_fine_search_window:
        raise RuntimeError(f"Apside ({next_event_name}) per {moon_name} non trovato nella ricerca oraria grossolana (max iter: {max_coarse_iterations}). Anomalia iniziale: {current_true_anomaly_deg_coarse}, Anomalia finale: {previous_anomaly_deg_coarse}")

    # --- FASE 2: Ricerca Fine (a passi di 1 minuto) nell'ora individuata ---
    search_date_fine = start_of_fine_search_window # Inizia dall'inizio dell'ora identificata
    fine_search_interval = ATHDateInterval(minutes=1)
    # Ricalcola l'anomalia per l'inizio esatto della finestra di ricerca fine
    previous_anomaly_deg_fine = _get_moon_true_anomaly_at_moment(moon_name, search_date_fine, moon_params_dict) 
    
    max_fine_iterations = ATHDateTimeInterface.IXH + 5 # Numero di minuti in un'ora del calendario + buffer

    for _ in range(max_fine_iterations):
        search_date_fine_next_step = search_date_fine.add(fine_search_interval)
        current_true_anomaly_deg_fine_val = _get_moon_true_anomaly_at_moment(moon_name, search_date_fine_next_step, moon_params_dict)

        crossed_target_fine = False
        if next_event_name == "Perianthal":
            if previous_anomaly_deg_fine >= 180.0 and current_true_anomaly_deg_fine_val < 180.0:
                crossed_target_fine = True
        elif next_event_name == "Apoanthal":
            if previous_anomaly_deg_fine < 180.0 and current_true_anomaly_deg_fine_val >= 180.0:
                crossed_target_fine = True
        
        if crossed_target_fine:
            # search_date_fine_next_step è il primo minuto in cui la condizione è soddisfatta.
            # L'evento è avvenuto tra search_date_fine e search_date_fine_next_step.
            # Per una precisione al minuto, search_date_fine_next_step è una buona approssimazione.
            event_dt_atz = search_date_fine_next_step.set_timezone(atz_timezone)
            return (next_event_name, event_dt_atz, expected_distance_at_apsis_m)

        previous_anomaly_deg_fine = current_true_anomaly_deg_fine_val
        search_date_fine = search_date_fine_next_step
        
    # Se la ricerca fine non ha "migliorato" o è arrivata alla fine dell'ora,
    # significa che l'evento è molto vicino all'inizio dell'ora successiva a start_of_fine_search_window.
    # Restituiamo l'ora identificata dalla ricerca grossolana come approssimazione.
    # (search_date_coarse all'uscita del primo loop è l'ora *prima* dell'attraversamento)
    # Quindi, l'evento è nell'ora successiva.
    event_dt_atz_approx = start_of_fine_search_window.add(coarse_search_interval).set_timezone(atz_timezone)
    return (next_event_name, event_dt_atz_approx, expected_distance_at_apsis_m)

def find_next_moon_major_phase(
    moon_name: str,
    start_date: ATHDateTimeInterface,
    anthal_params: Dict[str, Any],
    moon_params_dict: Dict[str, Dict[str, Any]],
    atz_timezone: ATHDateTimeZoneInterface
) -> Tuple[str, ATHDateTimeInterface]:
    """
    Trova la prossima fase lunare principale (Nuova, Primo Quarto, Piena, Ultimo Quarto)
    per una data luna, a partire da una specifica data/ora di inizio.
    La funzione utilizza una ricerca a due fasi:
    1. Ricerca Grossolana: a passi orari per identificare l'ora approssimativa dell'evento.
    2. Ricerca Fine: a passi di un minuto all'interno dell'ora identificata per affinare il risultato.
    L'elongazione (differenza di longitudine eclittica tra la luna e Nijel)
    determina la fase:
    - Luna Nuova (🌑): Elongazione ≈ 0° (o 360°)
    - Primo Quarto (🌓): Elongazione ≈ 90°
    - Luna Piena (🌕): Elongazione ≈ 180°
    - Ultimo Quarto (🌗): Elongazione ≈ 270°
    Args:
        moon_name: Il nome della luna (es. "Leea", "Mirahn").
        start_date: L'oggetto ATHDateTimeInterface da cui iniziare la ricerca.
        moon_params_dict: Un dizionario che mappa i nomi delle lune ai loro
                        rispettivi dizionari di parametri orbitali.
        atz_timezone: L'istanza del fuso orario ATZ, usata per impostare il fuso
                    orario dell'oggetto ATHDateTimeInterface restituito.
    Returns:
        Tuple[str, ATHDateTimeInterface]:
            - Nome della prossima fase lunare principale (stringa).
            - Oggetto ATHDateTimeInterface (nel fuso ATZ) che rappresenta la data e l'ora
            approssimata (al minuto) della fase.
    Raises:
        RuntimeError: Se la fase lunare non viene trovata entro i limiti di ricerca stabiliti.
        ValueError: Se i parametri orbitali per la luna specificata non sono in moon_params_dict.
    """
    # Mappa dei nomi delle fasi e delle loro elongazioni target in gradi
    phase_targets_map = {
        "Luna Nuova": 0.0,
        "Primo Quarto": 90.0,
        "Luna Piena": 180.0,
        "Ultimo Quarto": 270.0,
    }
    # Lista ordinata per facilitare la ricerca sequenziale del prossimo target.
    # Include un target tecnico di 360° per "Luna Nuova" per gestire correttamente
    # il passaggio dell'elongazione da valori alti (vicino a 270°) a valori bassi (vicino a 0°).
    sorted_phases_with_targets = [
        ("Luna Nuova", 0.0),    # Target effettivo per Luna Nuova
        ("Primo Quarto", 90.0),
        ("Luna Piena", 180.0),
        ("Ultimo Quarto", 270.0),
        ("Luna Nuova ", 360.0)  # Target tecnico per il "giro" oltre 270°, il nome ha uno spazio per distinguerlo
                            # se necessario, ma .strip() lo rimuoverà nel risultato.
    ]

    # Calcola l'elongazione della luna alla data di partenza
    current_elongation_deg = _get_moon_elongation_at_moment(
        moon_name, start_date, moon_params_dict, anthal_params # <--- PASSA anthal_params
    )

    next_phase_name = ""
    target_elongation_for_search = 0.0 # L'elongazione target che stiamo cercando

    # Determina la prossima fase principale e la sua elongazione target
    for phase_n, target_e in sorted_phases_with_targets:
        if current_elongation_deg < target_e:
            # Condizione per evitare di selezionare subito "Luna Nuova" (target 0.0 o 360.0)
            # se l'elongazione corrente è già alta (es. > 270, cioè dopo l'Ultimo Quarto).
            # In tal caso, il vero prossimo target è la Luna Nuova a 360.0.
            if not (target_e == phase_targets_map["Luna Nuova"] and \
                    current_elongation_deg > phase_targets_map["Ultimo Quarto"]):
                next_phase_name = phase_n.strip() # Rimuove spazi extra dal nome
                target_elongation_for_search = target_e
                break
    
    if not next_phase_name: # Se non è stato trovato un target (es. current_elongation > 270°)
        next_phase_name = "Luna Nuova" # Il prossimo evento è la Luna Nuova
        target_elongation_for_search = 360.0 # Il target tecnico per il "giro"

    # --- FASE 1: Ricerca Grossolana (a passi di 1 ora del calendario) ---
    search_date_coarse = start_date
    coarse_search_interval = ATHDateInterval(hours=1) # Intervallo di 1 ora
    
    moon_orbital_params = moon_params_dict.get(moon_name, {}) # Parametri specifici della luna
    # Stima del periodo sinodico (tempo tra due fasi uguali) per il limite di iterazioni.
    # P_s è il periodo sidereo; il sinodico è leggermente più lungo. Usiamo P_s * 1.15 come stima.
    approx_synodic_period_seconds = moon_orbital_params.get("P_s", 28 * ATHDateTimeInterface.SXD_CALENDAR) * 1.15
    seconds_per_calendar_hour = ATHDateTimeInterface.IXH * ATHDateTimeInterface.SXI
    
    # Max iterazioni per coprire circa 1/4 del ciclo sinodico (per trovare la prossima delle 4 fasi principali).
    max_coarse_iterations = int((approx_synodic_period_seconds / 4.0) / seconds_per_calendar_hour)
    if max_coarse_iterations < (24 * 3): max_coarse_iterations = (24 * 3) # Minimo 3 giorni di ricerca oraria
    if max_coarse_iterations > (24 * 10): max_coarse_iterations = (24 * 10) # Massimo 10 giorni per sicurezza

    previous_elongation_deg_coarse = current_elongation_deg
    start_of_fine_search_window: Optional[ATHDateTimeInterface] = None # Ora in cui iniziare la ricerca fine

    for _ in range(max_coarse_iterations):
        search_date_coarse_next_step = search_date_coarse.add(coarse_search_interval)
        current_elongation_deg_coarse_next = _get_moon_elongation_at_moment(
            moon_name, search_date_coarse_next_step, moon_params_dict, anthal_params)
        
        crossed_target = False
        if target_elongation_for_search == 360.0: # Caso speciale: ricerca Luna Nuova (passaggio da ~270-359 a ~0-90)
            if previous_elongation_deg_coarse >= phase_targets_map["Ultimo Quarto"] and \
            current_elongation_deg_coarse_next < phase_targets_map["Primo Quarto"] and \
            previous_elongation_deg_coarse > current_elongation_deg_coarse_next: # L'angolo deve "saltare indietro"
                crossed_target = True
        else: # Per le altre fasi (Primo Quarto, Piena, Ultimo Quarto)
            if previous_elongation_deg_coarse < target_elongation_for_search and \
            current_elongation_deg_coarse_next >= target_elongation_for_search:
                crossed_target = True
        
        if crossed_target:
            start_of_fine_search_window = search_date_coarse # Memorizza l'ora *prima* dell'attraversamento
            break 
        
        previous_elongation_deg_coarse = current_elongation_deg_coarse_next
        search_date_coarse = search_date_coarse_next_step

    if not start_of_fine_search_window:
        raise RuntimeError(f"Fase lunare ({next_phase_name}) per {moon_name} non trovata nella ricerca oraria grossolana. "
                        f"Max iter: {max_coarse_iterations}. Elong. iniziale: {current_elongation_deg:.2f}, "
                        f"Elong. finale ricerca: {previous_elongation_deg_coarse:.2f}, Target: {target_elongation_for_search:.2f}")

    # --- FASE 2: Ricerca Fine (a passi di 1 minuto) nell'ora individuata ---
    search_date_fine = start_of_fine_search_window # Inizia dall'inizio dell'ora identificata
    fine_search_interval = ATHDateInterval(minutes=1)
    # Ricalcola l'elongazione all'inizio della finestra oraria per la ricerca fine
    previous_elongation_deg_fine = _get_moon_elongation_at_moment(moon_name, search_date_fine, moon_params_dict, anthal_params) 
    
    max_fine_iterations = ATHDateTimeInterface.IXH + 5 # Max minuti in un'ora del calendario + buffer

    for _ in range(max_fine_iterations):
        search_date_fine_next_step = search_date_fine.add(fine_search_interval)
        current_elongation_deg_fine_next = _get_moon_elongation_at_moment(moon_name, search_date_fine_next_step, moon_params_dict, anthal_params)

        crossed_target_fine = False
        if target_elongation_for_search == 360.0: 
            if previous_elongation_deg_fine >= phase_targets_map["Ultimo Quarto"] and \
            current_elongation_deg_fine_next < phase_targets_map["Primo Quarto"] and \
            previous_elongation_deg_fine > current_elongation_deg_fine_next:
                crossed_target_fine = True
        else:
            if previous_elongation_deg_fine < target_elongation_for_search and \
            current_elongation_deg_fine_next >= target_elongation_for_search:
                crossed_target_fine = True
        
        if crossed_target_fine:
            # search_date_fine_next_step è il primo minuto in cui la condizione è soddisfatta.
            # L'evento è avvenuto tra search_date_fine e search_date_fine_next_step.
            event_dt_atz = search_date_fine_next_step.set_timezone(atz_timezone)
            return (next_phase_name.strip(), event_dt_atz)

        previous_elongation_deg_fine = current_elongation_deg_fine_next
        search_date_fine = search_date_fine_next_step
        
    # Se la ricerca fine non "affina" il risultato (es. l'evento è nel primo minuto dell'ora successiva),
    # restituisci il risultato della ricerca grossolana (l'ora successiva a start_of_fine_search_window).
    event_dt_atz_approx = start_of_fine_search_window.add(coarse_search_interval).set_timezone(atz_timezone)
    return (next_phase_name.strip(), event_dt_atz_approx)

## --- Funzioni Helper per Eventi Stagionali e Anno Tropicale --- ##
def find_next_solstice_or_equinox(start_date: ATHDateTimeInterface) -> Tuple[str, ATHDateTimeInterface]:
    """
    Trova il prossimo solstizio o equinozio a partire da una data.
    Restituisce una tupla (nome_evento, ATHDateTime_evento).
    L'iterazione avviene sul tempo del calendario, ma la longitudine è calcolata fisicamente.
    """
    targets = {
        "Equinozio di Primavera": 0.0, # Longitudine eclittica target
        "Solstizio d'Estate": 90.0,
        "Equinozio d'Autunno": 180.0,
        "Solstizio d'Inverno": 270.0,
    }

    # _get_true_ecliptic_longitude_at_moment usa le costanti astronomiche per il calcolo
    current_lon = _get_true_ecliptic_longitude_at_moment(start_date, NIJEL_PARAMS)

    next_target_lon_val = 0.0
    next_event_name = ""
    
    # Determina il prossimo target di longitudine
    # Ordina i target per assicurare la corretta sequenza
    sorted_targets = sorted(targets.items(), key=lambda item: item[1])

    for name, lon_target in sorted_targets:
        if current_lon < lon_target:
            next_target_lon_val = lon_target
            next_event_name = name
            break
    
    if not next_event_name: # Se current_lon è > 270, il prossimo è 0 (Equinozio Primavera)
        next_target_lon_val = 360.0 # Obiettivo tecnico 360 per gestire il "giro" a 0
        next_event_name = "Equinozio di Primavera"

    # Stima approssimativa per iniziare la ricerca (usa giorni del CALENDARIO)
    # La velocità angolare media è circa 360 gradi / EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS
    # Questo è un calcolo approssimativo, la ricerca fine farà il resto.
    degrees_to_go = (next_target_lon_val if next_target_lon_val < 360 else 360.0) - current_lon
    if degrees_to_go < 0: # Caso in cui current_lon > 270 e next_target è 360 (per 0)
        degrees_to_go += 360.0
        
    # Usiamo il periodo orbitale effettivo per una stima migliore dei giorni
    avg_degrees_per_calendar_day_approx = 360.0 / ATHDateTimeInterface.EFFECTIVE_ORBITAL_PERIOD_ANTHALEJA_DAYS
    days_to_estimate = degrees_to_go / avg_degrees_per_calendar_day_approx
    
    search_date = start_date
    if days_to_estimate > 5: # Solo se la stima è significativamente avanti
        search_date = start_date.add(ATHDateInterval(days=int(days_to_estimate) - 5))
    
    # Intervallo di ricerca fine (1 secondo del CALENDARIO)
    one_second_calendar_interval = ATHDateInterval(seconds=1)
    
    # Limite di iterazioni per sicurezza (es. 15 giorni calendariali * secondi in un giorno calendariale)
    max_iterations = 15 * ATHDateTimeInterface.SXD_CALENDAR 
    iterations = 0

    previous_lon = current_lon

    for iterations in range(int(max_iterations)):
        lon = _get_true_ecliptic_longitude_at_moment(start_date, NIJEL_PARAMS)
        
        # Gestione del passaggio da >270 a 0 (Equinozio di Primavera)
        is_spring_equinox_target = (next_event_name == "Equinozio di Primavera" and next_target_lon_val == 360.0)
        
        crossed_target = False
        if is_spring_equinox_target:
            # Se il target è l'equinozio di primavera (0/360), e la longitudine precedente era alta (es. >270)
            # e la longitudine attuale è bassa (es. <90), allora abbiamo attraversato 0.
            if previous_lon > 270.0 and lon < 90.0: # Attraversamento dello 0/360
                crossed_target = True
        elif lon >= next_target_lon_val:
            crossed_target = True

        if crossed_target:
            # Potremmo voler fare un passo indietro di un secondo per essere sicuri
            # di essere sull'ultimo secondo *prima* o *esattamente sul* target,
            # o usare una ricerca binaria per maggiore precisione se necessario.
            # Per ora, questo ci dà il primo secondo in cui la condizione è soddisfatta.
            return (next_event_name, search_date)
        
        previous_lon = lon
        search_date = search_date.add(one_second_calendar_interval)

    # Fallback nel caso non trovi nulla (non dovrebbe succedere con max_iterations ampio)
    # o potremmo sollevare un'eccezione
    return (f"Evento ({next_event_name}) non trovato entro il limite di ricerca", start_date)

def calculate_tropical_year_duration(
    target_year: int,
    atz_timezone: ATHDateTimeZoneInterface
) -> ATHDateInterval:
    """
    Calcola la durata precisa dell'anno tropicale Anthaleja per un dato anno
    di riferimento. L'anno tropicale è definito come il tempo che intercorre
    tra due passaggi consecutivi di Nijel all'equinozio di primavera
    del pianeta Anthal.
    Tutti i calcoli e le date intermedie sono gestiti nel fuso orario ATZ
    (Anthalys Time Zero) per garantire coerenza e un riferimento astronomico standard.
    Args:
        target_year: L'anno Anthaleja (come intero) da cui iniziare la ricerca
                    del primo equinozio di primavera. La funzione calcolerà
                    l'anno tropicale che include questo equinozio.
        atz_timezone: Un'istanza di ATHDateTimeZoneInterface rappresentante ATZ.
    Returns:
        ATHDateInterval: Un oggetto ATHDateInterval che rappresenta la durata
                        precisa dell'anno tropicale.
    Raises:
        RuntimeError: Se non riesce a trovare gli equinozi necessari entro
                    un limite di ricerca ragionevole (gestito implicitamente da
                    find_next_solstice_or_equinox o dai loop di sicurezza).
    """
    # 1. Determina una data di partenza sicura all'inizio dell'anno target, nel fuso ATZ.
    #    Usiamo from_components per assicurarci che l'oggetto sia correttamente in ATZ.
    start_search_date = ATHDateTime.from_components(
        year=target_year,
        month_name="Arejal", # Primo mese del calendario Anthaleja
        day=1,               # Primo giorno del mese
        hour=0, minute=0, second=0,
        ath_timezone_obj=atz_timezone
    )
    
    # 2. Trova il primo Equinozio di Primavera (E1) a partire dalla data di inizio.
    #    La funzione find_next_solstice_or_equinox restituisce il *prossimo* evento stagionale.
    #    Dobbiamo ciclare finché non troviamo specificamente l'Equinozio di Primavera.
    event_name_e1: str
    dt_e1: ATHDateTimeInterface
    
    current_dt_for_e1_search = start_search_date
    max_searches_for_event = 8 # Limite di sicurezza: cerca al massimo per 8 eventi stagionali (~2 anni)
    
    for _ in range(max_searches_for_event):
        event_name_e1, dt_e1 = find_next_solstice_or_equinox(current_dt_for_e1_search)
        if event_name_e1 == "Equinozio di Primavera":
            break
        # Avanza la data di ricerca al giorno dopo l'evento trovato per continuare la ricerca
        current_dt_for_e1_search = dt_e1.add(ATHDateInterval(days=1))
    else: # Eseguito se il loop for finisce senza un break
        raise RuntimeError(f"Primo Equinozio di Primavera non trovato per l'anno {target_year} entro {max_searches_for_event} tentativi.")
        
    # 3. Trova il secondo Equinozio di Primavera (E2), quello successivo a E1.
    #    Inizia la ricerca dal giorno *dopo* il primo equinozio trovato (dt_e1).
    start_for_e2_search = dt_e1.add(ATHDateInterval(days=1))
    
    event_name_e2: str
    dt_e2: ATHDateTimeInterface
    current_dt_for_e2_search = start_for_e2_search

    for _ in range(max_searches_for_event): # Usa lo stesso limite di sicurezza
        event_name_e2, dt_e2 = find_next_solstice_or_equinox(current_dt_for_e2_search)
        if event_name_e2 == "Equinozio di Primavera":
            # Assicurati che dt_e2 sia effettivamente dopo dt_e1
            if dt_e2.get_earth_timestamp() > dt_e1.get_earth_timestamp():
                break
        current_dt_for_e2_search = dt_e2.add(ATHDateInterval(days=1))
    else: # Eseguito se il loop for finisce senza un break
        raise RuntimeError(f"Secondo Equinozio di Primavera non trovato dopo {dt_e1.format('YYYY-MM-DD')} entro {max_searches_for_event} tentativi.")
        
    # 4. Calcola la differenza di tempo tra i due equinozi.
    #    dt_e1.diff(dt_e2) calcola (dt_e1 - dt_e2).
    #    Dato che dt_e2 è successivo a dt_e1, vogliamo (dt_e2 - dt_e1).
    #    Il metodo diff gestisce questo e il flag 'invert'.
    #    Se dt_e1.diff(dt_e2), l'intervallo avrà invert=True.
    #    Se vogliamo una durata positiva, invertiamo la differenza o usiamo il valore assoluto.
    #    Tuttavia, ATHDateInterval dovrebbe rappresentare la durata correttamente.
    #    Verifichiamo la logica di ATHDateTime.diff
    #    Se self > target, intervallo positivo. Se self < target, intervallo con invert=True.
    #    Quindi dt_e1.diff(dt_e2) darà un intervallo "negativo" (invert=True).
    #    Per ottenere la durata, possiamo fare dt_e2.diff(dt_e1)
    tropical_year_interval = dt_e2.diff(dt_e1) # Questo dovrebbe dare dt_e2 - dt_e1
    
    # Assicuriamoci che l'intervallo non sia invertito, o gestiamolo.
    # Se la logica di diff è (self - target), allora dt_e2.diff(dt_e1) è corretta.
    # Se, per qualche motivo, l'intervallo risultasse invertito, lo correggiamo.
    if tropical_year_interval.invert:
        tropical_year_interval.invert = False # Vogliamo una durata positiva
        # Potrebbe essere necessario ricalcolare i total_seconds se invert li modifica.
        # È meglio assicurarsi che diff restituisca un intervallo "direzionale" coerente.
        # Assumendo che ATHDateInterval(..., invert=True) gestisca correttamente i suoi valori:
        # la durata è la stessa, solo il "segno" logico cambia.
        # Per una "durata", vogliamo sempre il valore positivo.
        # La classe ATHDateInterval che abbiamo non ha un metodo 'abs()'.
        # La chiamata dt_e2.diff(dt_e1) dovrebbe già restituire un intervallo
        # che rappresenta la durata da dt_e1 a dt_e2.

    return tropical_year_interval

def calculate_cross_quarter_days(
    seasonal_markers: Dict[str, ATHDateTimeInterface], # Date dei solstizi/equinozi
    atz_timezone: ATHDateTimeZoneInterface           # Istanza di ATHDateTimeZone("ATZ")
    ) -> Dict[str, ATHDateTimeInterface]:
    """
    Calcola i "cross-quarter days" (giorni di mezzo quarto), che sono i punti
    a metà strada temporale tra i solstizi e gli equinozi.
    Tutti i calcoli e gli oggetti ATHDateTimeInterface restituiti sono nel fuso orario ATZ.
    Args:
        seasonal_markers: Un dizionario dove le chiavi sono i nomi degli eventi
                        stagionali principali (es. "Equinozio di Primavera",
                        "Solstizio d'Estate", "Equinozio d'Autunno", "Solstizio d'Inverno")
                        e i valori sono gli oggetti ATHDateTimeInterface corrispondenti
                        (idealmente già in fuso ATZ e ordinati cronologicamente
                        per un dato ciclo stagionale).
        atz_timezone: L'istanza del fuso orario ATZ, usata per creare i nuovi
                    oggetti ATHDateTimeInterface per i cross-quarter days.
    Returns:
        Dict[str, ATHDateTimeInterface]: Un dizionario dove le chiavi sono i nomi
        descrittivi dei cross-quarter days (es. "Inverno/Primavera Cross-Quarter")
        e i valori sono gli oggetti ATHDateTimeInterface (in ATZ) che
        rappresentano la data e l'ora di questi punti intermedi.
    """
    cross_quarters: Dict[str, ATHDateTimeInterface] = {}
    
    # Definizione degli intervalli tra i marker stagionali principali per i cross-quarter.
    # (Nome Evento Inizio, Nome Evento Fine, Nome Base per il Cross-Quarter)
    # Questo ordine assume un ciclo stagionale che inizia con l'Equinozio di Primavera.
    # L'ultimo intervallo (Inverno -> Primavera) è quello che tipicamente attraversa
    # il cambio di anno calendariale per i marker stagionali.
    event_intervals_for_cq = [
        ("Equinozio di Primavera", "Solstizio d'Estate", "Primavera-Estate"),
        ("Solstizio d'Estate", "Equinozio d'Autunno", "Estate-Autunno"),
        ("Equinozio d'Autunno", "Solstizio d'Inverno", "Autunno-Inverno"),
        ("Solstizio d'Inverno", "Equinozio di Primavera", "Inverno-Primavera") 
    ]

    for start_event_key, end_event_key, cq_base_name in event_intervals_for_cq:
        dt_start = seasonal_markers.get(start_event_key)
        dt_end_initial = seasonal_markers.get(end_event_key) # Potrebbe essere dell'anno precedente per il ciclo Inverno->Primavera

        if not dt_start or not dt_end_initial:
            # print(f"Attenzione: Marker stagionali mancanti per calcolare {cq_base_name} Cross-Quarter. "
            #       f"Start: '{start_event_key}' (Trovato: {'Sì' if dt_start else 'No'}), "
            #       f"End: '{end_event_key}' (Trovato: {'Sì' if dt_end_initial else 'No'}).")
            continue # Salta questo cross-quarter se mancano i dati

        ts_start_earth = dt_start.get_earth_timestamp()
        ts_end_earth_initial = dt_end_initial.get_earth_timestamp()

        dt_end_corrected = dt_end_initial # Inizializza con il marker trovato

        # Gestione cruciale: se l'evento finale nel dizionario 'seasonal_markers'
        # è cronologicamente *prima* dell'evento iniziale (es. Equinozio di Primavera 5794
        # rispetto a Solstizio d'Inverno 5793), dobbiamo trovare l'istanza
        # dell'evento finale che segue *effettivamente* l'evento iniziale.
        if ts_end_earth_initial < ts_start_earth:
            # print(f"Debug CQ {cq_base_name}: Evento finale '{end_event_key}' ({dt_end_initial.format('Y-M-D')}) è prima di quello iniziale '{start_event_key}' ({dt_start.format('Y-M-D')}). Cerco il successivo.")
            # Cerca la *prossima* occorrenza dell'evento finale partendo da dopo dt_start.
            search_after_dt_start = dt_start.add(ATHDateInterval(days=1))
            
            # find_next_solstice_or_equinox troverà il prossimo evento in assoluto.
            # Dobbiamo ciclare finché non troviamo specificamente 'end_event_key'.
            temp_search_date = search_after_dt_start
            found_corrected_end = False
            for _ in range(5): # Cerca al massimo i prossimi 5 eventi stagionali (più di 1 anno)
                next_event_name_found, next_event_dt_found = find_next_solstice_or_equinox(temp_search_date)
                if next_event_name_found == end_event_key:
                    dt_end_corrected = next_event_dt_found
                    found_corrected_end = True
                    break
                temp_search_date = next_event_dt_found.add(ATHDateInterval(days=1))
                # Limite per evitare di cercare troppo lontano se c'è un problema
                if temp_search_date.year > dt_start.year + 2 : break 

            if not found_corrected_end:
                # print(f"Attenzione: Impossibile trovare l'istanza successiva corretta di '{end_event_key}' per {cq_base_name} Cross-Quarter.")
                continue # Salta questo cross-quarter
            
            ts_end_earth = dt_end_corrected.get_earth_timestamp()
            # print(f"Debug CQ {cq_base_name}: Evento finale corretto: {dt_end_corrected.format('Y-M-D')}")
        else:
            ts_end_earth = ts_end_earth_initial

        # Ora ts_start_earth e ts_end_earth dovrebbero essere cronologicamente corretti
        if ts_end_earth < ts_start_earth: # Controllo di sicurezza finale
            # print(f"Attenzione: Logica di correzione data finale fallita per {cq_base_name}.")
            continue

        # Calcola il punto medio temporale tra i due eventi
        midpoint_earth_ts = ts_start_earth + (ts_end_earth - ts_start_earth) / 2.0
        
        # Converte il timestamp mediano in un oggetto datetime UTC terrestre
        midpoint_utc_dt = datetime.fromtimestamp(midpoint_earth_ts, tz=timezone.utc)
        
        # Crea l'oggetto ATHDateTime nel fuso orario ATZ specificato
        midpoint_ath_dt = ATHDateTime(midpoint_utc_dt, ath_timezone_obj=atz_timezone)
        
        cross_quarters[f"{cq_base_name} Cross-Quarter"] = midpoint_ath_dt
        
    return cross_quarters

def find_seasonal_markers(
    target_year: int,
    atz_timezone: ATHDateTimeZoneInterface
) -> Dict[str, ATHDateTimeInterface]:
    """
    Trova le date e gli orari esatti (nel fuso orario ATZ) dei quattro marker
    stagionali principali (solstizi ed equinozi) per un dato anno Anthaleja.

    Questa funzione cerca in sequenza l'Equinozio di Primavera, il Solstizio d'Estate,
    l'Equinozio d'Autunno e il Solstizio d'Inverno che si verificano a partire
    dall'inizio dell'anno specificato.

    Args:
        target_year: L'anno Anthaleja (come intero) per cui calcolare i marker stagionali.
                     La ricerca inizierà dal primo giorno di quest'anno.
        atz_timezone: Un'istanza di ATHDateTimeZoneInterface rappresentante il fuso ATZ,
                      utilizzato per creare la data di inizio della ricerca e per
                      garantire che le date restituite siano in ATZ.

    Returns:
        Dict[str, ATHDateTimeInterface]: Un dizionario dove le chiavi sono i nomi
        degli eventi stagionali (es. "Equinozio di Primavera") e i valori sono
        gli oggetti ATHDateTimeInterface corrispondenti (in fuso ATZ).
        Il dizionario conterrà i quattro eventi principali che si verificano
        sequenzialmente a partire dall'inizio dell'anno target.

    Raises:
        RuntimeError: Se non è possibile trovare tutti e quattro i marker stagionali
                      entro un periodo di ricerca ragionevole (circa 2 anni),
                      il che potrebbe indicare un problema con la funzione sottostante
                      `find_next_solstice_or_equinox` o con i parametri orbitali.
    """
    markers: Dict[str, ATHDateTimeInterface] = {}
    
    # Inizia la ricerca dal primo giorno dell'anno target, nel fuso orario ATZ.
    current_search_date = ATHDateTime.from_components(
        year=target_year,
        month_name="Arejal", # Primo mese del calendario Anthaleja
        day=1,
        hour=0, minute=0, second=0,
        ath_timezone_obj=atz_timezone
    )
    
    # Elenco ordinato dei nomi degli eventi stagionali che ci aspettiamo di trovare.
    # Questo è solo per riferimento, la funzione find_next_solstice_or_equinox
    # determinerà l'ordine effettivo in base alla data di partenza.
    # event_names_in_cycle = [
    #     "Equinozio di Primavera", 
    #     "Solstizio d'Estate", 
    #     "Equinozio d'Autunno", 
    #     "Solstizio d'Inverno"
    # ]
    
    found_events_count = 0
    # Ciclo per trovare i 4 eventi principali, assicurandosi che siano in ordine cronologico.
    for _ in range(4): # Ci aspettiamo 4 eventi distinti per completare un ciclo
        try:
            event_name, event_dt = find_next_solstice_or_equinox(current_search_date)
            
            # Verifica per evitare di aggiungere lo stesso evento più volte se la ricerca
            # non avanzasse correttamente o se ci fossero eventi molto ravvicinati.
            if event_name not in markers:
                markers[event_name] = event_dt
                found_events_count += 1
            
            # Avanza la data di ricerca al giorno dopo l'evento appena trovato
            # per assicurarsi che la prossima chiamata a find_next_solstice_or_equinox
            # cerchi l'evento *successivo*.
            current_search_date = event_dt.add(ATHDateInterval(days=1))

            # Limite di sicurezza per evitare loop eccessivamente lunghi se la logica di find_next_solstice_or_equinox
            # avesse problemi o se i parametri orbitali fossero estremi.
            if current_search_date.year > target_year + 2: # Se la ricerca si estende per più di 2 anni
                # print(f"Attenzione (find_seasonal_markers): La ricerca si è estesa oltre l'anno {target_year + 2} per l'anno target {target_year}.")
                break 
        
        except RuntimeError as e:
            # print(f"Errore Runtime durante la ricerca dell'evento stagionale {found_events_count + 1} per l'anno {target_year}: {e}")
            # Potremmo voler interrompere o continuare a seconda della gravità.
            # Per ora, interrompiamo se find_next_solstice_or_equinox solleva un errore.
            raise RuntimeError(f"Impossibile trovare tutti i marker stagionali per l'anno {target_year} a causa di: {e}") from e
        except Exception as e_gen: # Cattura altre eccezioni impreviste
            # print(f"Errore generico imprevisto in find_seasonal_markers: {e_gen}")
            raise RuntimeError(f"Errore generico in find_seasonal_markers per l'anno {target_year}: {e_gen}") from e_gen


    if found_events_count < 4:
        # Questo avviso è utile se il loop termina a causa del limite di sicurezza sull'anno.
        # print(f"Attenzione (find_seasonal_markers): Trovati solo {found_events_count}/4 marker stagionali per l'anno target {target_year}.")
        # Potrebbe essere normale se target_year è vicino alla fine di un ciclo di precessione lungo,
        # ma generalmente dovremmo trovarli tutti.
        # Non solleviamo un errore qui, ma restituiamo ciò che è stato trovato.
        pass
            
    return markers


## --- Funzioni di Ricerca Eclissi --- ##
def find_next_solar_eclipse(
    moon_name: str,
    start_date: ATHDateTimeInterface,
    moon_params_dict: Dict[str, Dict[str, Any]],
    anthal_params: Dict[str, Any],
    nijel_params: Dict[str, Any],
    atz_timezone: ATHDateTimeZoneInterface
) -> Optional[Dict[str, Any]]:
    """
    Trova la prossima eclissi solare di Nijel causata dalla luna specificata,
    a partire da una data fornita. L'eclissi è calcolata dal punto di vista
    geocentrico di Anthal (centro del pianeta).
    Funzionamento:
    1.  Identifica la prossima Luna Nuova per la luna data, poiché le eclissi solari
        possono avvenire solo in prossimità di questa fase (congiunzione in longitudine
        tra la luna e Nijel).
    2.  Esamina una finestra temporale ristretta (es. +/- 6 ore calendariali)
        attorno al momento stimato della Luna Nuova.
    3.  All'interno di questa finestra, itera con passi di un minuto, calcolando ad ogni
        passo la posizione 3D di Nijel e della luna (longitudine ed latitudine eclittiche),
        le loro distanze, i loro raggi angolari, e la separazione angolare tra i loro centri.
    4.  Verifica le condizioni per un'eclissi:
        a.  La latitudine eclittica della luna deve essere molto vicina a zero (luna vicina al nodo).
        b.  La separazione angolare tra i dischi deve essere inferiore alla somma dei loro raggi angolari.
    5.  Se un'eclissi è rilevata, determina il momento di massimo oscuramento e il tipo
        di eclissi (parziale, anulare, totale) in quell'istante.
    Args:
        moon_name (str): Il nome della luna che causa l'eclissi (es. "Leea", "Mirahn").
        start_date (ATHDateTimeInterface): L'oggetto ATHDateTimeInterface da cui iniziare la ricerca.
        moon_params_dict (Dict[str, Dict[str, Any]]): Dizionario che mappa i nomi delle lune
                                                    ai loro parametri orbitali.
        NIJEL_PARAMS (Dict[str, Any]): Dizionario dei parametri orbitali e fisici di Nijel
                                    e del sistema Anthal (inclusi "physical_radius_m",
                                    "semi_major_axis_m", "eccentricity", "axial_tilt_deg").
        atz_timezone (ATHDateTimeZoneInterface): Istanza del fuso orario ATZ, usata per
                                                restituire gli orari degli eventi.
    Returns:
        Optional[Dict[str, Any]]: Un dizionario contenente i dettagli dell'eclissi
        al momento del suo massimo oscuramento, se un'eclissi significativa viene trovata.
        Il dizionario include chiavi come:
            - "moon_name": (str) Nome della luna.
            - "eclipse_type": (str) Tipo di eclissi ("parziale", "anulare", "totale").
            - "time_max_obscuration_atz": (ATHDateTimeInterface) Istante del massimo oscuramento (in ATZ).
            - "max_obscuration_percent": (float) Percentuale massima di oscuramento del DIAMETRO di Nijel.
            - "details_at_max" (Dict): Dati astronomici al momento del massimo oscuramento:
                - "angular_separation_deg": (float) Separazione angolare tra i centri.
                - "alpha_nijel_deg": (float) Raggio angolare di Nijel.
                - "alpha_moon_deg": (float) Raggio angolare della luna.
                - "moon_ecliptic_latitude_deg": (float) Latitudine eclittica della luna.
                - "moon_longitude_deg": (float) Longitudine eclittica della luna.
                - "nijel_longitude_deg": (float) Longitudine eclittica di Nijel.
            - "partial_begin_atz": (NoneType) Placeholder per implementazione futura.
            - "partial_end_atz": (NoneType) Placeholder.
            - "central_phase_begin_atz": (NoneType) Placeholder.
            - "central_phase_end_atz": (NoneType) Placeholder.
        Restituisce None se nessuna eclissi (con oscuramento > 0) viene trovata
        nella finestra di ricerca o se si verifica un errore nel trovare la Luna Nuova preliminare.
    Raises:
        ValueError: Se parametri cruciali (es. raggio fisico di Nijel o parametri della luna)
                    non sono nei dizionari forniti.
    """
    # Inizializzazione della variabile per la data della Luna Nuova
    new_moon_approx_date_atz: Optional[ATHDateTimeInterface] = None
    found_new_moon_for_eclipse_search = False

    # --- Fase 1: Trovare la prossima Luna Nuova ---
    # Questo è il momento approssimativo in cui può verificarsi un'eclissi solare.
    try:
        temp_search_date_for_new_moon = start_date
        # Numero massimo di tentativi per trovare la "Luna Nuova" attraverso le fasi principali.
        # find_next_moon_major_phase avanza di circa 1/4 di ciclo sinodico.
        max_phase_finding_attempts = 8 # Dovrebbe coprire fino a 2 cicli sinodici.
        
        for _ in range(max_phase_finding_attempts):
            # Chiama la funzione per trovare la prossima fase principale.
            # Questa funzione necessita di anthal_params per permettere a _get_moon_elongation_at_moment
            # di calcolare la longitudine di Nijel (tramite _get_true_ecliptic_longitude_at_moment).
            phase_name_at_conjunction, new_moon_date_found = find_next_moon_major_phase(
                 moon_name, 
                 temp_search_date_for_new_moon, 
                 anthal_params, # Parametri di Anthal per la posizione di Nijel
                 moon_params_dict, 
                 atz_timezone
            )
            if phase_name_at_conjunction == "Luna Nuova":
                new_moon_approx_date_atz = new_moon_date_found
                found_new_moon_for_eclipse_search = True
                break 
            # Se non è Luna Nuova, avanza la data di ricerca per la prossima iterazione.
            # Avanziamo di 12 ore calendariali per superare ampiamente la fase appena trovata.
            temp_search_date_for_new_moon = new_moon_date_found.add(ATHDateInterval(hours=12))
            
            # Limite di sicurezza per evitare loop troppo lunghi.
            # Controlla se abbiamo cercato per più di ~2.5 periodi orbitali siderei della luna.
            current_moon_P_s = moon_params_dict.get(moon_name, {}).get("P_s", ATHDateTimeInterface.DXY_CALENDAR * ATHDateTimeInterface.SXD_CALENDAR)
            if temp_search_date_for_new_moon.get_earth_timestamp() > start_date.get_earth_timestamp() + (current_moon_P_s * 2.5):
                return None # Luna Nuova non trovata entro un limite ragionevole
        
        if not found_new_moon_for_eclipse_search:
            return None # Luna Nuova non trovata dopo i tentativi
                
    except RuntimeError: # Sollevato da find_next_moon_major_phase se non trova la fase
        return None 
    except Exception: # Altre eccezioni impreviste
        # Per debug, potresti voler loggare e_gen
        # import traceback; traceback.print_exc()
        return None

    # Controllo cruciale: se non abbiamo una data valida per la Luna Nuova, non possiamo procedere.
    if not new_moon_approx_date_atz:
        return None 

    # --- Fase 2: Ricerca Dettagliata dell'Eclissi attorno alla Luna Nuova ---
    search_window_hours_calendar = 6 # Ore del CALENDARIO prima e dopo la Luna Nuova
    search_window_start = new_moon_approx_date_atz.sub(ATHDateInterval(hours=search_window_hours_calendar))
    search_window_end = new_moon_approx_date_atz.add(ATHDateInterval(hours=search_window_hours_calendar))
    
    search_interval_fine = ATHDateInterval(minutes=1) # Passo di ricerca di 1 minuto del CALENDARIO
    
    max_eclipse_details: Optional[Dict[str, Any]] = None
    current_max_obscuration = -1.0 # Inizializza per trovare il primo oscuramento > 0

    # Estrai parametri necessari una sola volta prima del loop
    moon_orbital_params = moon_params_dict.get(moon_name)
    if not moon_orbital_params: # Dovrebbe essere già stato gestito da funzioni precedenti
        raise ValueError(f"Parametri orbitali per {moon_name} mancanti in find_next_solar_eclipse.")
    r_moon_physical_m = moon_orbital_params["R_phys_m"] # Raggio fisico della luna
    
    # Raggio fisico di Nijel (dalla nuova struttura dei parametri)
    nijel_physical_r_m = nijel_params.get("physical_radius_m")
    if nijel_physical_r_m is None: 
        raise ValueError("Raggio fisico di Nijel ('physical_radius_m') mancante in nijel_star_params.")

    current_search_time = search_window_start
    # Calcola il numero di iterazioni per la ricerca fine
    duration_fine_search_earth_seconds = search_window_end.get_earth_timestamp() - search_window_start.get_earth_timestamp()
    interval_fine_search_earth_seconds = abs(search_interval_fine.total_earth_seconds()) # Assicura positivo
    if interval_fine_search_earth_seconds < 1e-6: # Evita divisione per zero
        interval_fine_search_earth_seconds = float(ATHDateTimeInterface.SXI) # Fallback
    num_iterations_fine = int(duration_fine_search_earth_seconds / interval_fine_search_earth_seconds) + 1

    # --- Fase 3: Iterazione nella finestra di ricerca fine per i dettagli dell'eclissi ---
    for _ in range(num_iterations_fine):
        # Condizione di uscita se si supera la finestra temporale
        if current_search_time.get_earth_timestamp() > search_window_end.get_earth_timestamp():
            break
        
        # a. Dati di Nijel per l'istante corrente (longitudine, raggio angolare dinamico)
        #    _internal_calculate_nijel_info usa ANTHAL_PARAMS e NIJEL_PARAMS globalmente/di modulo
        current_nijel_data = _internal_calculate_nijel_info(
            current_search_time, 
            0.0, 0.0, # Lat/Lon osservatore geocentrico
            # anthal_params, nijel_star_params, # Se _internal_calculate_nijel_info li richiede esplicitamente
            atz_timezone # Fuso per eventuali date interne
        )
        nijel_internals = current_nijel_data.get("internals", {})
        nijel_lon_deg = math.degrees(nijel_internals.get("true_ecliptic_longitude_rad_nijel", 0.0))
        nijel_lat_deg = 0.0 # Nijel è per definizione sull'eclittica
        alpha_nijel_deg = nijel_internals.get("dynamic_angular_radius_nijel_deg")
        if alpha_nijel_deg is None: 
            raise ValueError(f"Raggio angolare dinamico di Nijel non calcolato per {current_search_time.format('HH:II:SS')}")

        # b. Dati della Luna per l'istante corrente (longitudine, latitudine, distanza, raggio angolare)
        #    _internal_calculate_moon_info usa ANTHAL_PARAMS["axial_tilt_deg"] tramite il suo argomento.
        moon_data = _internal_calculate_moon_info(
            moon_name, current_search_time,
            0.0, # Latitudine osservatore (geocentrica)
            anthal_params["axial_tilt_deg"], # Inclinazione assiale del pianeta Anthal
            nijel_internals, # Passa i dati interni di Nijel (longitudine λ_Nijel, transito di Nijel)
            moon_orbital_params, # Parametri specifici della luna in esame
            atz_timezone
        )
        
        moon_lon_deg = moon_data.get("true_ecliptic_longitude_degrees", 0.0)
        moon_lat_deg = moon_data.get("ecliptic_latitude_deg", 0.0)       # β_moon
        moon_distance_m = moon_data.get("current_distance_meters", moon_orbital_params["a_m"]) # r_moon
        alpha_moon_deg = calculate_angular_radius_deg(r_moon_physical_m, moon_distance_m) # α_moon
        
        # c. Condizione di Latitudine Eclittica per il Contatto dei Dischi
        #    Se la latitudine della luna è maggiore della somma dei raggi, non può esserci contatto.
        max_allowable_ecliptic_latitude_for_contact_deg = alpha_nijel_deg + alpha_moon_deg
        if abs(moon_lat_deg) > max_allowable_ecliptic_latitude_for_contact_deg:
            current_search_time = current_search_time.add(search_interval_fine)
            continue # Luna troppo "alta" o "bassa" sull'eclittica; nessuna eclissi.
        
        # d. Calcola la Separazione Angolare (θ) tra i centri di Nijel e della Luna
        angular_sep_deg = calculate_ecliptic_angular_separation_deg(
            nijel_lon_deg, nijel_lat_deg, # Coordinate di Nijel
            moon_lon_deg, moon_lat_deg    # Coordinate della Luna
        )
        
        # e. Verifica se c'è sovrapposizione dei dischi (condizione per eclissi parziale o migliore)
        if angular_sep_deg < (alpha_nijel_deg + alpha_moon_deg):
            # Eclissi (almeno parziale) in corso.
            
            # Calcola una metrica di oscuramento (magnitudine del diametro).
            # Valore da 0 (nessun contatto) a 1 (Nijel completamente coperto o al massimo possibile).
            if alpha_nijel_deg < 1e-7: # Evita divisione per zero se Nijel avesse raggio angolare nullo
                current_obscuration_value = 1.0 if angular_sep_deg < alpha_moon_deg else 0.0
            else:
                # Frazione del diametro di Nijel coperta: (R_N + R_L - Sep) / (2 * R_N)
                current_obscuration_value = (alpha_nijel_deg + alpha_moon_deg - angular_sep_deg) / (2.0 * alpha_nijel_deg)
            current_obscuration_value = max(0.0, min(1.0, current_obscuration_value)) # Clamp [0,1]

            # Se questo è l'oscuramento maggiore trovato finora, o il primo con oscuramento > 0
            if current_obscuration_value > current_max_obscuration or \
            (abs(current_obscuration_value - current_max_obscuration) < 1e-6 and max_eclipse_details is None and current_obscuration_value > 1e-6):
                current_max_obscuration = current_obscuration_value
                
                # Determina il tipo di eclissi al momento di massimo oscuramento
                eclipse_type_at_max = "parziale"
                # Condizione per fase centrale (totale o anulare):
                # la separazione dei centri è minore o uguale alla differenza dei raggi.
                if angular_sep_deg <= abs(alpha_nijel_deg - alpha_moon_deg):
                    if alpha_moon_deg >= alpha_nijel_deg: # Luna appare più grande o uguale a Nijel
                        eclipse_type_at_max = "totale"
                    else: # Luna appare più piccola di Nijel
                        eclipse_type_at_max = "anulare"
                
                # Aggiorna/Crea i dettagli dell'eclissi di massimo oscuramento
                max_eclipse_details = {
                    "moon_name": moon_name, 
                    "eclipse_type": eclipse_type_at_max, 
                    "time_max_obscuration_atz": current_search_time.set_timezone(atz_timezone), 
                    "max_obscuration_percent": current_max_obscuration * 100.0, # Come % del diametro
                    "details_at_max": { # Dati astronomici al momento del massimo
                        "angular_separation_deg": angular_sep_deg,      # θ
                        "alpha_nijel_deg": alpha_nijel_deg,             # α_N
                        "alpha_moon_deg": alpha_moon_deg,               # α_M
                        "moon_ecliptic_latitude_deg": moon_lat_deg,     # β_M
                        "moon_longitude_deg": moon_lon_deg,             # λ_M (per debug)
                        "nijel_longitude_deg": nijel_lon_deg            # λ_N (per debug)
                    },
                    # I tempi di contatto C1,C2,C3,C4 (inizio/fine delle fasi)
                    # richiedono una logica di ricerca più complessa e sono placeholder.
                    "partial_begin_atz": None, 
                    "partial_end_atz": None,
                    "central_phase_begin_atz": None, 
                    "central_phase_end_atz": None
                }
        
        current_search_time = current_search_time.add(search_interval_fine)
            
    return max_eclipse_details


## --- Funzione Pratica di Visualizzazione --- ##
def format_ath_celestial_dashboard(
    current_time_ath: Optional[ATHDateTimeInterface], # Ora corrente per alcuni display
    target_date_ath: ATHDateTimeInterface,         # Data principale per cui sono i calcoli
    latitude_A: float,                             # Latitudine dell'osservatore
    longitude_A: float,                            # Longitudine dell'osservatore
    celestial_data: Dict[str, Any],                # Dati astronomici pre-calcolati
    display_options: int                           # Opzioni per mostrare/nascondere sezioni
) -> str:
    """
    Costruisce una dashboard testuale ASCII ben formattata che riassume le principali
    informazioni astronomiche per il pianeta Anthal e i suoi corpi celesti (Nijel, Leea, Mirahn)
    per una data e una posizione specificate.
    La dashboard è strutturata per sezioni:
    1.  Intestazione: Data target, ora della rilevazione (se fornita), posizione.
    2.  Ora Attuale Dettagliata: Ora di sistema, ora duodecimale Anthaleja, ora ATZ,
        Local Mean Time (LMT) e Apparent Solar Time (AST) approssimati.
    3.  Dati di Nijel ed Eventi Stagionali: Orari di alba/tramonto/mezzogiorno/mezzanotte solare,
        Equazione del Tempo, declinazione, durata dell'anno tropicale, date dei
        solstizi, equinozi e cross-quarter days (con tempo relativo).
    4.  Dati Lunari (per Leea e Mirahn, se richieste):
        - Fase attuale (con glifo e percentuale).
        - Declinazione.
        - Distanza attuale e distanze teoriche agli apsidi.
        - Orari di levata, transito e tramonto.
        - Prossimo apside (Perianthal/Apoanthal) con data, distanza e tempo relativo.
        - Prossime 4 fasi lunari principali con data e tempo relativo.
        - Informazioni sulla prossima eclissi solare causata dalla luna (se trovata).
    5.  Note e Avvisi: Eventuali messaggi generati durante i calcoli.
    Args:
        current_time_ath: Oggetto ATHDateTimeInterface opzionale per l'ora corrente
                        a cui si riferiscono alcuni display (es. "Ora Rilevazione").
        target_date_ath: L'oggetto ATHDateTimeInterface per cui la maggior parte dei
                        calcoli astronomici sono stati effettuati.
        latitude_A: Latitudine dell'osservatore in gradi.
        longitude_A: Longitudine dell'osservatore in gradi.
        celestial_data: Un dizionario (solitamente prodotto da `ath_date_astronomy_info`)
                        contenente sotto-dizionari per "nijel", "leea", "mirahn"
                        e altre chiavi con i dati calcolati.
        display_options: Un intero (bitmask) che specifica quali sezioni
                        (es. dati di Leea, dati di Mirahn) visualizzare.
    Returns:
        str: Una stringa multi-linea formattata rappresentante la dashboard testuale.
    """
    
    # --- Funzioni Helper Interne per la Formattazione Specifica della Dashboard ---
    def _int_to_roman_1_14(num: int) -> str:
        """Converte un intero (1-14) nel suo numerale romano corrispondente."""
        if not 1 <= num <= 14: return str(num) # Fallback
        roman_map = {
            1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 
            8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII", 14: "XIV"
        }
        return roman_map.get(num, str(num))

    def _int_to_duodecimal(num: int) -> str:
        """Converte un intero nella sua rappresentazione stringa in base 12 (0-9, Ʌ, Ƹ)."""
        if num == 0: return "0"
        duo_digits = "0123456789ɅƸ" # Simboli per 10 (Ʌ) e 11 (Ƹ)
        if num < 0: return "-" + _int_to_duodecimal(abs(num)) # Gestione negativi (non per H,M,S)
        res = ""
        n = num
        while n > 0:
            remainder = n % 12
            res = duo_digits[remainder] + res
            n //= 12
        return res if res else "0" # Assicura "0" se num era 0

    def format_time(dt_obj: Optional[ATHDateTimeInterface]) -> str:
        """Formatta un oggetto ATHDateTimeInterface come HH:MM:SS o placeholder."""
        if dt_obj and hasattr(dt_obj, 'hour') and hasattr(dt_obj, 'minute') and hasattr(dt_obj, 'second'):
            return f"{dt_obj.hour:02d}:{dt_obj.minute:02d}:{dt_obj.second:02d}"
        return " --:--:-- " # Placeholder per orari non disponibili

    def format_phase(moon_info: Optional[Dict[str, Any]]) -> str:
        """Formatta le informazioni sulla fase lunare in una stringa con glifo."""
        if not moon_info: return "N/A"
        phase_percent = moon_info.get("phase_percent")
        elongation_deg = moon_info.get("elongation_degrees")

        if phase_percent is None or elongation_deg is None: return "N/A"
        
        name, glyph = "Sconosciuta", "❓" # Default
        # Mappatura elongazione -> nome fase e glifo
        if 0 <= elongation_deg < 22.5 or 337.5 <= elongation_deg <= 360: name, glyph = "Nuova", "🌑"
        elif 22.5 <= elongation_deg < 67.5: name, glyph = "Crescente", "🌒"
        elif 67.5 <= elongation_deg < 112.5: name, glyph = "Primo Quarto", "🌓"
        elif 112.5 <= elongation_deg < 157.5: name, glyph = "Gibbosa Crescente", "🌔"
        elif 157.5 <= elongation_deg < 202.5: name, glyph = "Piena", "🌕"
        elif 202.5 <= elongation_deg < 247.5: name, glyph = "Gibbosa Calante", "🌖"
        elif 247.5 <= elongation_deg < 292.5: name, glyph = "Ultimo Quarto", "🌗"
        elif 292.5 <= elongation_deg < 337.5: name, glyph = "Calante", "🌘"
            
        return f"{glyph} {name} ({phase_percent:.0f}%)"

    def format_interval_relative(diff_interval: Optional[ATHDateInterval], is_event_in_future: bool) -> str:
        """Formatta un ATHDateInterval in una stringa relativa (es. "fra 3g 5h", "2M 10g fa")."""
        if not diff_interval: return "N/A"

        parts = []
        # Usa i valori assoluti per i componenti; il segno è dato da is_event_in_future.
        # ATHDateInterval memorizza y,m,d,h,i,s come positivi; 'invert' indica la direzione.
        if abs(diff_interval.y) > 0: parts.append(f"{abs(diff_interval.y)}a") # 'a' per anni
        if abs(diff_interval.m) > 0: parts.append(f"{abs(diff_interval.m)}M") # 'M' per Mesi
        if abs(diff_interval.d) > 0: parts.append(f"{abs(diff_interval.d)}g") # 'g' per giorni
        
        # Mostra ore e minuti solo per intervalli brevi (es. < 3 giorni) o se sono gli unici componenti.
        if abs(diff_interval.y) == 0 and abs(diff_interval.m) == 0 and abs(diff_interval.d) < 3:
            if abs(diff_interval.h) > 0: parts.append(f"{abs(diff_interval.h)}h")
            if abs(diff_interval.i) > 0: parts.append(f"{abs(diff_interval.i)}m")
        
        if not parts: # Se l'intervallo è molto breve (es. solo minuti o secondi)
            total_abs_seconds_calendar = abs(diff_interval.total_earth_seconds()) # Usa total_earth_seconds che è già basato su _CALENDAR
            sxi_calendar = ATHDateTimeInterface.SXI # Secondi per minuto del CALENDARIO
            ixh_calendar = ATHDateTimeInterface.IXH # Minuti per ora del CALENDARIO

            if total_abs_seconds_calendar < sxi_calendar: # Meno di un minuto calendariale
                return "Imminente" if is_event_in_future else "Adesso/Poco Fa"
            elif total_abs_seconds_calendar < ixh_calendar * sxi_calendar : # Meno di un'ora calendariale
                # Calcola i minuti totali dall'intervallo se non ci sono componenti maggiori
                minutes_only = math.floor(total_abs_seconds_calendar / sxi_calendar)
                parts.append(f"{minutes_only}m")
                # Opzionale: aggiungere secondi se i minuti sono l'unica parte grande
                # if abs(diff_interval.s) > 0 and abs(diff_interval.h) == 0 and abs(diff_interval.d) == 0 : 
                #     parts.append(f"{abs(diff_interval.s)}s")
            elif abs(diff_interval.d) == 0 and abs(diff_interval.m) == 0 and abs(diff_interval.y) == 0: # Se è lo stesso giorno ma più di un'ora
                if abs(diff_interval.h) > 0 : parts.append(f"{abs(diff_interval.h)}h")
                if abs(diff_interval.i) > 0 : parts.append(f"{abs(diff_interval.i)}m")


        if not parts: return "N/A" # Fallback se, per qualche motivo, non ci sono parti (non dovrebbe succedere)

        display_str = " ".join(parts[:3]) # Limita a un massimo di 3 parti per brevità (es. "1a 2M 3g")
        
        # 'is_event_in_future' è True se l'evento è dopo target_date_ath
        # (basato su come target_date_ath.diff(event_dt).invert è stato impostato)
        return f"fra {display_str}" if is_event_in_future else f"{display_str} fa"

    # --- Inizio Costruzione Output Dashboard ---
    nijel_info = celestial_data.get("nijel") # Dati calcolati per Nijel
    output_lines = []
    line_width = 78 # Larghezza desiderata per la dashboard testuale
    
    # --- SEZIONE 1: Intestazione ---
    header_date_target = target_date_ath.format("DAY, JJ MONTH<y_bin_46>") # Formato completo per la data target
    header_loc = f"Lat: {latitude_A:.2f}, Lon: {longitude_A:.2f}"
    output_lines.append("=" * line_width)
    output_lines.append(f"== DASHBOARD CELESTE ANTHALEJA - {header_date_target.upper()} ==") # Titolo principale
    
    moment_of_day_str = ""
    if current_time_ath: # Se è fornita un'ora di "rilevazione"
        # get_ath_moment_of_day è una funzione helper esterna
        moment_of_day_str = f" ({get_ath_moment_of_day(current_time_ath)})" 
        output_lines.append(f"== Ora Rilevazione: {current_time_ath.format('HH:II:SS TZN')}{moment_of_day_str} | Posizione: {header_loc} ==")
        output_lines.append("-" * line_width)
        output_lines.append("  Ora Attuale Dettagliata:")
        output_lines.append(f"    {'Sistema (come fornita)':<30}: {current_time_ath.format('HH:II:SS TZN')}")
        
        # Ora Duodecimale
        h_cal_curr = current_time_ath.hour; m_cal_curr = current_time_ath.minute; s_cal_curr = current_time_ath.second
        h_duo_str = _int_to_duodecimal(h_cal_curr).zfill(2)
        m_duo_str = _int_to_duodecimal(m_cal_curr).zfill(2)
        s_duo_str = _int_to_duodecimal(s_cal_curr).zfill(2)
        hms_duo_str = f"{h_duo_str}:{m_duo_str}:{s_duo_str}"
        output_lines.append(f"    {'Ora Anthaleja (Duodecimale)':<30}: {hms_duo_str} (base 12)")
        
        # Ora Ciclica Romana (Opzionale)
        ora_romana_str = _int_to_roman_1_14(14 if h_cal_curr % 14 == 0 else h_cal_curr % 14)
        label_giorno_notte = "del Giorno" if 7 <= h_cal_curr <= 25 else "della Notte"
        output_lines.append(f"    {'Ora Ciclica (Romana)':<30}: Ora {ora_romana_str} {label_giorno_notte}")

        # Ora in ATZ
        atz_timezone = ATHDateTimeZone("ATZ") # Istanza di ATZ
        current_time_in_atz = current_time_ath.set_timezone(atz_timezone)
        output_lines.append(f"    {'ATZ (Anthalys Time Zero)':<30}: {current_time_in_atz.format('HH:II:SS TZN')}")
        
        # Local Mean Time (LMT) e Apparent Solar Time (AST)
        if nijel_info: # Richiedono dati di Nijel (EoT)
            gradi_per_ora_calendar = 360.0 / ATHDateTimeInterface.HXD_CALENDAR
            long_offset_hours_calendar = longitude_A / gradi_per_ora_calendar
            long_offset_total_seconds_float = long_offset_hours_calendar * ATHDateTimeInterface.IXH * ATHDateTimeInterface.SXI
            
            long_offset_s_int = int(long_offset_total_seconds_float)
            long_offset_us_int = int((long_offset_total_seconds_float - long_offset_s_int) * 1_000_000)
            offset_interval = ATHDateInterval(
                seconds=long_offset_s_int, microseconds=long_offset_us_int,
                invert=(long_offset_total_seconds_float < 0)
            )
            lmt_dt = current_time_in_atz.add(offset_interval) # LMT approssimato
            output_lines.append(f"    {'Local Mean Time (LMT)':<30}: {lmt_dt.format('HH:II:SS')} (Appross.)")

            eot_seconds_for_current_float = nijel_info.get('equation_of_time_minutes_ATH', 0.0) * ATHDateTimeInterface.SXI
            eot_s_int = int(eot_seconds_for_current_float)
            eot_us_int = int((eot_seconds_for_current_float - eot_s_int) * 1_000_000)
            eot_interval = ATHDateInterval(
                seconds=abs(eot_s_int), microseconds=abs(eot_us_int), invert=False
            )
            ast_dt: ATHDateTimeInterface
            if eot_seconds_for_current_float >= 0: # EoT positiva (sole vero in ritardo), AST = LMT - EoT
                ast_dt = lmt_dt.sub(eot_interval)
            else: # EoT negativa (sole vero in anticipo), AST = LMT + |EoT|
                ast_dt = lmt_dt.add(eot_interval)
            output_lines.append(f"    {'Apparent Solar Time (AST)':<30}: {ast_dt.format('HH:II:SS')}")
        else:
            output_lines.append(f"    {'Local Mean Time (LMT)':<30}: (Dati Nijel non disp.)")
            output_lines.append(f"    {'Apparent Solar Time (AST)':<30}: (Dati Nijel non disp.)")
        output_lines.append("-" * line_width)
    else: # Se current_time_ath non è fornito
        output_lines.append(f"== Posizione: {header_loc} ==")
        output_lines.append("-" * line_width)
    
    # --- SEZIONE 2: Dati di Nijel e Eventi Stagionali ---
    if nijel_info:
        output_lines.append("\n-- NIJEL (Stella) & Eventi Stagionali --")
        # Titoli colonne per eventi del giorno di Nijel
        output_lines.append(f"  {'Evento Solare del Giorno':<32} | {'Orario (fuso target)':<20} | {'Declinazione':<12}")
        output_lines.append(f"  {'-'*32} | {'-'*20} | {'-'*12}")
        
        decl_nijel_str = f"{nijel_info.get('declination_degrees', 0.0):+.2f}°" # Declinazione attuale
        
        # Eventi principali del giorno target
        if nijel_info.get("sunrise_actual"): output_lines.append(f"  {'Alba (effettiva)':<32} | {format_time(nijel_info.get('sunrise_actual')):^20} |")
        if nijel_info.get("transit_true_local"):
            # _calculate_nijel_altitude_at_solar_noon è una funzione helper esterna
            alt_noon = _calculate_nijel_altitude_at_solar_noon(latitude_A, nijel_info.get('declination_degrees',0.0))
            output_lines.append(f"  {'Mezzogiorno Solare (transito)':<32} | {format_time(nijel_info.get('transit_true_local')):^20} | {decl_nijel_str:^12} (Alt: {alt_noon:.1f}°)")
        else: # Stampa la declinazione se il transito non è disponibile
            output_lines.append(f"  {'Declinazione Attuale Nijel':<32} | {' ':^20} | {decl_nijel_str:^12}")

        if nijel_info.get("sunset_actual"): output_lines.append(f"  {'Tramonto (effettivo)':<32} | {format_time(nijel_info.get('sunset_actual')):^20} |")
        if nijel_info.get("solar_midnight"): output_lines.append(f"  {'Mezzanotte Solare':<32} | {format_time(nijel_info.get('solar_midnight')):^20} |")
        
        # Altre informazioni su Nijel
        eot_min = nijel_info.get('equation_of_time_minutes_ATH', 0.0)
        output_lines.append(f"  {'Equazione del Tempo':<32} | {f'{eot_min:.2f} min':^20} |")
        
        tropical_interval = nijel_info.get("tropical_year_duration_interval")
        if tropical_interval and isinstance(tropical_interval, ATHDateInterval):
            total_days_ty = tropical_interval.total_earth_seconds() / ATHDateTimeInterface.SXD_ASTRONOMICAL # Durata in giorni fisici
            ty_str_decimal = f"{total_days_ty:.4f} giorni fisici"
            output_lines.append(f"  {'Durata Anno Tropicale (ca.)':<32} | {ty_str_decimal:^20} |")
        
        # Eventi Stagionali dell'Anno (Solstizi ed Equinozi)
        output_lines.append("\n  Eventi Stagionali Chiave (Date in ATZ):")
        seasonal_markers = nijel_info.get("seasonal_markers", {})
        event_order = ["Equinozio di Primavera", "Solstizio d'Estate", "Equinozio d'Autunno", "Solstizio d'Inverno"]
        for event_name in event_order:
            event_dt = seasonal_markers.get(event_name)
            if event_dt and isinstance(event_dt, ATHDateTimeInterface):
                time_diff = target_date_ath.diff(event_dt)
                is_future = time_diff.invert # diff(target, event) -> invert=True se event è futuro
                rel_time_str = format_interval_relative(time_diff, is_future)
                output_lines.append(f"    {event_name:<30}: {event_dt.format('JJ MONTH, HH:II')} ({rel_time_str})")

        # Cross-Quarter Days
        cross_quarters = nijel_info.get("cross_quarter_days", {})
        if cross_quarters:
            output_lines.append("  Cross-Quarter Days (Date in ATZ):")
            cq_order = ["Inverno/Primavera Cross-Quarter", "Primavera/Estate Cross-Quarter",
                        "Estate/Autunno Cross-Quarter", "Autunno/Inverno Cross-Quarter"]
            for cq_name_key in cq_order:
                event_dt = cross_quarters.get(cq_name_key)
                if event_dt and isinstance(event_dt, ATHDateTimeInterface):
                    time_diff = target_date_ath.diff(event_dt)
                    is_future = time_diff.invert
                    rel_time_str = format_interval_relative(time_diff, is_future)
                    output_lines.append(f"    {cq_name_key:<30}: {event_dt.format('JJ MONTH, HH:II')} ({rel_time_str})")
        
        # Prossimo Evento Stagionale Globale (calcolato da ath_date_astronomy_info)
        next_solstice_event_data = celestial_data.get("next_solstice_event") 
        if next_solstice_event_data and isinstance(next_solstice_event_data, tuple) and len(next_solstice_event_data) == 2:
            solstice_name, solstice_date = next_solstice_event_data
            if solstice_date and isinstance(solstice_date, ATHDateTimeInterface):
                time_diff = target_date_ath.diff(solstice_date)
                is_future = time_diff.invert
                rel_time_str = format_interval_relative(time_diff, is_future)
                output_lines.append(f"  Prossimo Evento Stag. Globale: {solstice_name} - {solstice_date.format('JJ MONTH<y_bin_46>, HH:II')} ({rel_time_str})")

    else: # Se nijel_info non è disponibile
        output_lines.append("\n  Dati di Nijel non disponibili.")

    # --- SEZIONE 3: Dati Lunari ---
    output_lines.append("\n" + "=" * line_width)
    output_lines.append(f"== DATI LUNARI (per {header_date_target.upper()}) ==")
    output_lines.append("=" * line_width)

    for moon_name_iter, moon_data_dict_ref_key in [("Leea", "leea"), ("Mirahn", "mirahn")]:
        moon_data = celestial_data.get(moon_data_dict_ref_key) # Dati specifici della luna
        
        display_this_moon = False # Determina se visualizzare questa luna
        if moon_name_iter == "Leea" and (display_options & LEEA_INFO): display_this_moon = True
        if moon_name_iter == "Mirahn" and (display_options & MIRAHN_INFO): display_this_moon = True

        if display_this_moon and moon_data and isinstance(moon_data, dict):
            output_lines.append(f"\n  --- {moon_name_iter.upper()} ---")
            output_lines.append(f"    {'Fase Attuale':<28} : {format_phase(moon_data)}")
            output_lines.append(f"    {'Declinazione':<28} : {moon_data.get('declination_degrees', 0.0):+.2f}°")
            
            current_dist_km = moon_data.get('current_distance_meters', 0.0) / 1000.0
            output_lines.append(f"    {'Distanza Attuale':<28} : {current_dist_km:,.0f} km")
            
            perianthal_dist_km = moon_data.get('distance_perianthal_meters',0.0) / 1000.0
            apoanthal_dist_km = moon_data.get('distance_apoanthal_meters',0.0) / 1000.0
            output_lines.append(f"    {'Dist. Perianthal (teorica)':<28} : {perianthal_dist_km:,.0f} km")
            output_lines.append(f"    {'Dist. Apoanthal (teorica)':<28} : {apoanthal_dist_km:,.0f} km")

            output_lines.append(f"    Eventi Giornalieri (Ora Locale Oggetto Input):") # Fuso orario di target_date_ath
            output_lines.append(f"      {'Levata':<24} : {format_time(moon_data.get('rise'))}")
            output_lines.append(f"      {'Transito':<24} : {format_time(moon_data.get('transit_approx'))}")
            output_lines.append(f"      {'Tramonto':<24} : {format_time(moon_data.get('set'))}")

            # Visualizzazione Prossimo Apside
            next_apsis_info = moon_data.get("next_apsis")
            if next_apsis_info and isinstance(next_apsis_info, dict):
                apsis_name = next_apsis_info.get('name', 'Apside Sconosciuto')
                apsis_dt = next_apsis_info.get('date_atz') # Questo è un ATHDateTimeInterface
                apsis_dist_m = next_apsis_info.get('distance_m', 0.0)
                if apsis_dt and isinstance(apsis_dt, ATHDateTimeInterface): 
                    time_diff = target_date_ath.diff(apsis_dt)
                    is_future = time_diff.invert # diff(target, event_futuro) -> invert=True
                    rel_time_str = format_interval_relative(time_diff, is_future)
                    output_lines.append(f"    Prossimo {apsis_name}:")
                    output_lines.append(f"      {'Data (ATZ)':<22} : {apsis_dt.format('JJ MONTH, HH:II')} ({rel_time_str})")
                    output_lines.append(f"      {'Distanza':<22} : {apsis_dist_m / 1000.0:,.0f} km")
            
            # --- VISUALIZZAZIONE FASI LUNARI FUTURE ---
            upcoming_phases = moon_data.get("upcoming_phases", [])
            if upcoming_phases and isinstance(upcoming_phases, list) and len(upcoming_phases) > 0:
                first_phase_entry = upcoming_phases[0] # Controlla il primo elemento per errori
                if not (isinstance(first_phase_entry, dict) and "Errore" in first_phase_entry.get("name", "")):
                    output_lines.append(f"    Prossime Fasi Principali (Date in ATZ):")
                    for phase_info in upcoming_phases: # Itera sulle fasi calcolate
                        if isinstance(phase_info, dict):
                            phase_name = phase_info.get("name")
                            phase_dt = phase_info.get("date_atz") # Questo è un ATHDateTimeInterface
                            if phase_name and phase_dt and isinstance(phase_dt, ATHDateTimeInterface):
                                time_diff = target_date_ath.diff(phase_dt)
                                is_future = time_diff.invert
                                rel_time_str = format_interval_relative(time_diff, is_future)
                                output_lines.append(f"      {phase_name:<22} : {phase_dt.format('JJ MONTH, HH:II')} ({rel_time_str})")
                elif isinstance(first_phase_entry, dict) and "Errore" in first_phase_entry.get("name", ""):
                    output_lines.append(f"    Prossime Fasi Principali (ATZ): {first_phase_entry.get('name')}")
            # --- FINE VISUALIZZAZIONE FASI LUNARI ---
            
            # --- VISUALIZZAZIONE ECLISSI SOLARE (sezione aggiunta) ---
            solar_eclipse_info = moon_data.get("next_solar_eclipse_by_this_moon")
            if solar_eclipse_info and isinstance(solar_eclipse_info, dict):
                output_lines.append(f"    Prossima Eclissi Solare da {moon_name_iter}:")
                eclipse_type = str(solar_eclipse_info.get("eclipse_type", "N/D")).capitalize()
                max_time_dt = solar_eclipse_info.get("time_max_obscuration_atz") # ATHDateTimeInterface
                max_obsc_perc = solar_eclipse_info.get("max_obscuration_percent", 0.0)
                
                if max_time_dt and isinstance(max_time_dt, ATHDateTimeInterface):
                    time_diff = target_date_ath.diff(max_time_dt)
                    is_future = time_diff.invert
                    rel_time_str = format_interval_relative(time_diff, is_future)
                    output_lines.append(f"      {'Tipo':<22} : {eclipse_type}")
                    output_lines.append(f"      {'Massimo (ATZ)':<22} : {max_time_dt.format('JJ MONTH<y_bin_46>, HH:II')} ({rel_time_str})")
                    output_lines.append(f"      {'Oscuramento Max':<22} : {max_obsc_perc:.1f}% diam. Nijel")

                    details_at_max = solar_eclipse_info.get("details_at_max", {})
                    if isinstance(details_at_max, dict):
                        output_lines.append(f"      {'  Sep. Ang. (max)':<20} : {details_at_max.get('angular_separation_deg', 0.0):.4f}°")
                        output_lines.append(f"      {'  Lat. Luna (max)':<20} : {details_at_max.get('moon_ecliptic_latitude_deg', 0.0):.4f}°")
                        output_lines.append(f"      {'  R.Ang.Nijel (max)':<20} : {details_at_max.get('alpha_nijel_deg', 0.0):.4f}°")
                        output_lines.append(f"      {'  R.Ang.Luna (max)':<20} : {details_at_max.get('alpha_moon_deg', 0.0):.4f}°")
                else: # Se max_time_dt non è valido
                    output_lines.append(f"      Dati sul tempo del massimo oscuramento non disponibili.")
            elif solar_eclipse_info is None: # Se find_next_solar_eclipse ha restituito None
                output_lines.append(f"    Prossima Eclissi Solare da {moon_name_iter}: Nessuna trovata.")
            # --- FINE VISUALIZZAZIONE ECLISSI SOLARE ---

        elif display_this_moon: # Se moon_data è None ma doveva essere visualizzata
            output_lines.append(f"\n  --- {moon_name_iter.upper()} ---")
            output_lines.append("    Dati lunari non disponibili o non richiesti per la visualizzazione.")

    # --- SEZIONE 4: Note e Avvisi ---
    output_lines.append("\n" + "=" * line_width)
    all_notes = set() # Usa un set per evitare note duplicate
    if nijel_info and isinstance(nijel_info.get("notes"), list): 
        all_notes.update(nijel_info["notes"])
    
    leea_data_dict = celestial_data.get("leea", {})
    if isinstance(leea_data_dict.get("notes"), list): all_notes.update(leea_data_dict["notes"])
    
    mirahn_data_dict = celestial_data.get("mirahn", {})
    if isinstance(mirahn_data_dict.get("notes"), list): all_notes.update(mirahn_data_dict["notes"])
    
    if all_notes:
        output_lines.append("NOTE E AVVISI:")
        for note in sorted(list(all_notes)): # Ordina le note per una visualizzazione consistente
            output_lines.append(f"- {note}")
    else:
        output_lines.append("Nessuna nota o avviso specifico.")
    output_lines.append("=" * line_width)

    return "\n".join(output_lines)

## --- Funzioni Helper Aggiuntive --- ##
def _parse_earth_datestring(datetime_string: str) -> datetime:
    """
    Interpreta una stringa di data/ora terrestre in formati comuni, senza
    dipendenze esterne come 'dateutil'.
    La funzione tenta il parsing in due fasi:
    1. Prova a interpretare la stringa usando `datetime.fromisoformat()`,
    che gestisce i formati ISO 8601 standard e può restituire un oggetto
    `datetime` timezone-aware se l'informazione sul fuso è presente.
    (Sostituisce gli spazi con 'T' per una maggiore compatibilità).
    2. Se il parsing ISO fallisce, tenta una lista predefinita di formati comuni
    utilizzando `datetime.strptime()`. Questi formati generalmente producono
    oggetti `datetime` naive (senza fuso orario).
    Args:
        datetime_string: La stringa di data/ora terrestre da interpretare.
    Returns:
        datetime: Un oggetto `datetime`. Può essere timezone-aware (se parsato
                con successo da `fromisoformat` e la stringa conteneva info TZ)
                o naive (se parsato da `strptime` con i formati predefiniti).
                La gestione del fuso orario (es. assunzione di UTC per oggetti naive)
                è responsabilità della funzione chiamante.
    Raises:
        ValueError: Se la stringa non corrisponde a nessuno dei formati riconosciuti.
    """
    # Tentativo 1: Parsing con fromisoformat (gestisce ISO 8601 e fusi orari)
    try:
        # Sostituisce lo spazio con 'T' per permettere a fromisoformat di parsare
        # formati come "YYYY-MM-DD HH:MM:SS" come se fossero "YYYY-MM-DDTHH:MM:SS".
        iso_compatible_string = datetime_string.strip().replace(" ", "T")
        
        # Gestione del caso in cui la stringa termina con 'Z' ma fromisoformat
        # di versioni Python più vecchie potrebbe non gestirlo implicitamente come UTC.
        # Python 3.11+ gestisce 'Z' correttamente. Per retrocompatibilità più ampia:
        # if iso_compatible_string.upper().endswith('Z'):
        #     iso_compatible_string = iso_compatible_string[:-1] + "+00:00"
            
        return datetime.fromisoformat(iso_compatible_string)
    except ValueError:
        # Il formato non è ISO 8601 standard o contiene elementi non riconosciuti.
        # Passa al tentativo successivo con strptime.
        pass

    # Tentativo 2: Parsing con strptime e una lista di formati comuni
    # Questi formati produrranno oggetti datetime NAIVE.
    common_formats = [
        "%Y-%m-%d %H:%M:%S",    # Es. 2023-10-26 14:30:55
        "%Y-%m-%d %H:%M",       # Es. 2023-10-26 14:30
        "%Y-%m-%d",             # Es. 2023-10-26
        "%d/%m/%Y %H:%M:%S",    # Es. 26/10/2023 14:30:55
        "%d/%m/%Y %H:%M",       # Es. 26/10/2023 14:30
        "%d/%m/%Y",             # Es. 26/10/2023
        # Aggiungi altri formati comuni se necessario
    ]

    for fmt in common_formats:
        try:
            # strptime crea oggetti datetime naive se il formato non include info TZ.
            return datetime.strptime(datetime_string.strip(), fmt)
        except ValueError:
            continue # Formato non corrispondente, prova il successivo

    # Se nessun formato ha funzionato, solleva un'eccezione.
    raise ValueError(f"Formato data/ora Terrestre non riconosciuto o non supportato: '{datetime_string}'")

def get_default_ath_timezone() -> ATHDateTimeZoneInterface: # Cambiato il tipo di ritorno all'interfaccia
    """
    Restituisce l'oggetto fuso orario Anthaleja di default del sistema.
    Questa funzione accede a una variabile di modulo (`_current_default_ath_timezone_obj`)
    che memorizza l'istanza del fuso orario di default. Idealmente, questa variabile
    è inizializzata ad ATHDateTimeZone("ATZ") al caricamento del modulo
    (es. in 'ath_timezone_config.py').
    La funzione include un meccanismo di fallback per garantire che venga sempre
    restituita un'istanza valida: se il default globale non è un'istanza
    valida di ATHDateTimeZoneInterface, tenta di creare e impostare
    ATHDateTimeZone("ATZ") come nuovo default.
    Returns:
        ATHDateTimeZoneInterface: Un'istanza valida del fuso orario di default
                                (tipicamente ATZ).
    Raises:
        RuntimeError: Se non è possibile creare nemmeno l'istanza di fallback
                    ATHDateTimeZone("ATZ"), indicando un problema critico
                    nella configurazione dei fusi orari.
    """
    global _current_default_ath_timezone_obj # Necessario per modificare la variabile di modulo

    # Controlla se l'oggetto globale è un'istanza valida dell'interfaccia.
    # Questo è più flessibile che controllare ATHDateTimeZone direttamente,
    # nel caso si introducessero altre implementazioni dell'interfaccia.
    if not isinstance(_current_default_ath_timezone_obj, ATHDateTimeZoneInterface):
        # Avviso o log opzionale che il default globale non era valido o non inizializzato.
        # print("Attenzione: _current_default_ath_timezone_obj non è un'istanza valida o non inizializzata. Tento il fallback ad ATZ.")
        try:
            # Tenta di creare e impostare ATZ come default.
            # Importa ATHDateTimeZone qui se necessario per evitare problemi di import circolare
            # o se questa funzione è in un modulo diverso da dove _current_default_ath_timezone_obj è definito.
            # Se _current_default_ath_timezone_obj è definito nello stesso modulo, ATHDateTimeZone dovrebbe essere già importato.
            if 'ATHDateTimeZone' not in globals() or ATHDateTimeZone is None : from .ATHDateTimeZone import ATHDateTimeZone # type: ignore
            _current_default_ath_timezone_obj = ATHDateTimeZone("ATZ") # type: ignore
        except ValueError as ve:
            # Sollevato da ATHDateTimeZone.__init__ se "ATZ" non è un ID valido.
            raise RuntimeError(f"Impossibile definire il fuso orario di default ATZ: ID non valido. Errore originale: {ve}")
        except Exception as e:
            # Per altri errori imprevisti durante l'istanza di ATHDateTimeZone("ATZ")
            raise RuntimeError(f"Errore critico imprevisto durante l'inizializzazione del fuso orario di default ATZ: {e}")
            
    assert _current_default_ath_timezone_obj is not None
    assert isinstance(_current_default_ath_timezone_obj, ATHDateTimeZoneInterface)
    return _current_default_ath_timezone_obj

def get_ath_moment_of_day(
    current_time_ath: ATHDateTimeInterface,
    nijel_info_for_current_day: Optional[Dict[str, Any]] = None
) -> str:
    """
    Determina e restituisce una descrizione testuale sfumata del "momento del giorno"
    nel sistema Anthaleja. Si basa sull'ora dell'oggetto ATHDateTimeInterface fornito
    e, se disponibili, sugli orari degli eventi astronomici di Nijel (alba, tramonto,
    vari crepuscoli, mezzogiorno solare) per quel giorno specifico.
    La funzione tenta prima di classificare il momento usando gli orari precisi degli
    eventi astronomici. Se questi dati non sono disponibili o l'ora corrente
    non rientra in una delle fasce sfumate definite, ricade su una logica più
    semplice basata su intervalli di ore fisse del calendario Anthaleja.
    Le etichette includono nomi specifici del lore di Anthalys (Nahr, Nalmek, Daja, San, Kelth).
    Args:
        current_time_ath: L'oggetto ATHDateTimeInterface che rappresenta l'ora
                        corrente nel calendario Anthaleja per cui determinare
                        il momento del giorno.
        nijel_info_for_current_day: Un dizionario opzionale contenente i dati
                                    astronomici calcolati per Nijel (come quelli
                                    restituiti da `_internal_calculate_nijel_info`)
                                    relativi al giorno specifico di `current_time_ath`.
                                    Se `None` o incompleto, la funzione userà il fallback.
    Returns:
        str: Una stringa descrittiva del momento del giorno, ad esempio:
            "Notte Profonda (Nahr)", "Crepuscolo Astronomico (Mattina)",
            "Ora Blu Profonda (Mattina)", "Ora Blu Chiara (Alba)", "Ora d'Oro (Alba)",
            "Mattino Pieno (Nalmek)", "Tarda Mattina (Nalmek)",
            "Mezzogiorno Pieno (Daja)", "Primo Pomeriggio (Daja)",
            "Tardo Pomeriggio (Daja)", "Ora d'Oro (Pre-Tramonto)",
            "Ora d'Oro (Tramonto)", "Ora Blu Chiara (Tramonto)",
            "Ora Blu Profonda (Sera)", "Crepuscolo Nautico (Sera)",
            o le versioni del fallback "Alba (Kelth)", "Notte (Nahr)", ecc.
    """
    # Ottieni il timestamp terrestre (fisico) dell'ora corrente per confronti precisi.
    # Convertito a float per consistenza con i timestamp degli eventi.
    current_ts = float(current_time_ath.get_earth_timestamp())
    
    # Ottieni l'ora del CALENDARIO Anthaleja (0-27, se HXD_CALENDAR=28) per la logica di fallback.
    hour_of_day_calendar = current_time_ath.hour
    
    # Abbreviazioni per le costanti di durata del CALENDARIO (per leggibilità)
    ixh_cal = ATHDateTimeInterface.IXH # Minuti per ora (calendariale)
    sxi_cal = ATHDateTimeInterface.SXI # Secondi per minuto (calendariale)

    # Funzione helper interna per estrarre i timestamp degli eventi (in secondi terrestri)
    # dal dizionario nijel_info_for_current_day. È definita qui per avere accesso
    # a nijel_info_for_current_day tramite closure.
    def get_ts(event_name: str) -> Optional[float]:
        """Estrae e converte il timestamp di un evento da nijel_info."""
        if nijel_info_for_current_day and isinstance(nijel_info_for_current_day, dict):
            event_dt = nijel_info_for_current_day.get(event_name)
            if event_dt and isinstance(event_dt, ATHDateTimeInterface):
                ts_val = event_dt.get_earth_timestamp() # Questo è un int (Unix TS)
                return float(ts_val) if ts_val is not None else None
        return None # Se nijel_info non è valido o l'evento manca

    # Tenta di usare la logica sfumata se i dati astronomici di Nijel sono disponibili
    if nijel_info_for_current_day and isinstance(nijel_info_for_current_day, dict):
        # Estrai i timestamp (in secondi terrestri) per tutti gli eventi rilevanti del giorno.
        # Mattina (eventi in ordine cronologico approssimativo dall'oscurità alla luce)
        ts_astro_mrn_end = get_ts("astronomical_twilight_morning_end")      # Sole a -21° (o tuo valore) e sale
        ts_naut_mrn_end = get_ts("nautical_twilight_morning_end")           # Sole a -14° e sale
        ts_bdeep_mrn_end = get_ts("blue_hour_deep_morning_end")             # Fine Blu Profonda (Sole a -7.0° e sale)
        ts_bclear_mrn_end = get_ts("blue_hour_clear_morning_end")           # Fine Blu Chiara (Sole a -4.67° e sale)
                                                                            # (Coincide con Inizio Golden Hour Mattutina)
        ts_sunrise_actual = get_ts("sunrise_actual")                        # Levata effettiva del disco solare
        ts_golden_mrn_end = get_ts("golden_hour_morning_end")               # Fine Golden Hour Mattutina (Sole a +7.0° e sale)
        
        # Mezzogiorno
        ts_solar_noon = get_ts("transit_true_local")                        # Transito di Nijel (Mezzogiorno Solare Vero)

        # Sera (eventi in ordine cronologico approssimativo dalla luce all'oscurità)
        ts_golden_evn_begin = get_ts("golden_hour_evening_begin")           # Inizio Golden Hour Serale (Sole a +7.0° e scende)
        ts_sunset_actual = get_ts("sunset_actual")                          # Tramonto effettivo del disco solare
        ts_bclear_evn_begin = get_ts("blue_hour_clear_evening_begin")       # Inizio Blu Chiara Serale (Sole a -4.67° e scende)
                                                                            # (Coincide con Fine Golden Hour Serale)
        ts_bdeep_evn_begin = get_ts("blue_hour_deep_evening_begin")         # Inizio Blu Profonda Serale (Sole a -7.0° e scende)
        ts_naut_evn_begin = get_ts("nautical_twilight_evening_begin")       # Inizio Crepuscolo Nautico Serale (Sole a -14° e scende)
        ts_astro_evn_begin = get_ts("astronomical_twilight_evening_begin")  # Inizio Crepuscolo Astronomico Serale (Sole a -21° e scende)

        # Logica condizionale per determinare il momento del giorno.
        # L'ordine dei controlli è importante per la corretta classificazione.

        # 1. NOTTE PROFONDA: Dopo l'inizio del crepuscolo astronomico serale o prima della fine di quello mattutino.
        if (ts_astro_evn_begin is not None and current_ts >= ts_astro_evn_begin) or \
        (ts_astro_mrn_end is not None and current_ts < ts_astro_mrn_end):
            return "Notte Profonda (Nahr)"
        
        # 2. FASI DEL CREPUSCOLO MATTUTINO (dal più scuro al più chiaro)
        if ts_astro_mrn_end is not None and ts_naut_mrn_end is not None and \
        ts_astro_mrn_end <= current_ts < ts_naut_mrn_end:
            return "Crepuscolo Astronomico (Mattina)"
        if ts_naut_mrn_end is not None and ts_bdeep_mrn_end is not None and \
        ts_naut_mrn_end <= current_ts < ts_bdeep_mrn_end: return "Crepuscolo Nautico (Mattina)"
        if ts_bdeep_mrn_end is not None and ts_bclear_mrn_end is not None and \
        ts_bdeep_mrn_end <= current_ts < ts_bclear_mrn_end:
            return "Ora Blu Profonda (Mattina)" # Sole tra -9.33° e -7.0° (secondo le tue H_ costanti)
        if ts_bclear_mrn_end is not None and ts_sunrise_actual is not None and \
        ts_bclear_mrn_end <= current_ts < ts_sunrise_actual: # Sole tra -4.67° e l'alba effettiva
            return "Ora Blu Chiara (Alba)"
        
        # 3. ALBA e ORA D'ORO MATTUTINA
        # Questo intervallo copre dal momento dell'alba effettiva fino alla fine della Golden Hour.
        if ts_sunrise_actual is not None and ts_golden_mrn_end is not None and \
        ts_sunrise_actual <= current_ts < ts_golden_mrn_end:
            return "Ora d'Oro (Alba)" # Include il momento dell'alba e la successiva golden hour

        # 4. GIORNO: MATTINO
        # Dopo la fine della Golden Hour mattutina e prima di avvicinarsi al mezzogiorno solare.
        if ts_golden_mrn_end is not None and ts_solar_noon is not None and \
        ts_golden_mrn_end <= current_ts < ts_solar_noon:
            # Suddivisione ulteriore del mattino
            if (ts_solar_noon - current_ts) < (1.5 * ixh_cal * sxi_cal): # Meno di 1.5 ore calendariali da mezzogiorno
                return "Tarda Mattina (Nalmek)"
            else:
                return "Mattino Pieno (Nalmek)"

        # 5. GIORNO: MEZZOGIORNO
        if ts_solar_noon is not None and \
           abs(current_ts - ts_solar_noon) < (1.0 * ixh_cal * sxi_cal): # Entro +/- 1 ora calendariale dal mezzogiorno solare
            return "Mezzogiorno Pieno (Daja)"

        # 6. GIORNO: POMERIGGIO
        # Dopo il mezzogiorno solare (o la sua finestra) e prima dell'inizio della Golden Hour serale.
        if ts_solar_noon is not None and ts_golden_evn_begin is not None and \
        ts_solar_noon < current_ts < ts_golden_evn_begin: # Implicito current_ts > ts_solar_noon (o la sua finestra)
            if (current_ts - ts_solar_noon) < (3.0 * ixh_cal * sxi_cal): # Entro 3 ore calendariali da mezzogiorno
                return "Primo Pomeriggio (Daja)"
            else:
                return "Tardo Pomeriggio (Daja)"

        # 7. ORA D'ORO SERALE e TRAMONTO
        # Questo intervallo copre dall'inizio della Golden Hour serale fino al tramonto effettivo.
        if ts_golden_evn_begin is not None and ts_sunset_actual is not None and \
            ts_golden_evn_begin <= current_ts < ts_sunset_actual:
            return "Ora d'Oro (Pre-Tramonto)"
        # Questo intervallo copre dal tramonto effettivo fino alla fine della Golden Hour serale (inizio Blue Clear Evening).
        if ts_sunset_actual is not None and ts_bclear_evn_begin is not None and \
            ts_sunset_actual <= current_ts < ts_bclear_evn_begin:
            return "Ora d'Oro (Tramonto)"

        # 8. FASI DEL CREPUSCOLO SERALE (dal più chiaro al più scuro)
        if ts_bclear_evn_begin is not None and ts_bdeep_evn_begin is not None and \
        ts_bclear_evn_begin <= current_ts < ts_bdeep_evn_begin: # Sole tra -4.67° e -7.0°
            return "Ora Blu Chiara (Tramonto)" # O "Crepuscolo Civile Serale"
        if ts_bdeep_evn_begin is not None and ts_naut_evn_begin is not None and \
        ts_bdeep_evn_begin <= current_ts < ts_naut_evn_begin: # Sole tra -7.0° e -14°
            return "Ora Blu Profonda (Sera)"
        if ts_naut_evn_begin is not None and ts_astro_evn_begin is not None and \
        ts_naut_evn_begin <= current_ts < ts_astro_evn_begin: # Sole tra -14° e -21°
            return "Crepuscolo Nautico (Sera)"
        # Se current_ts >= ts_astro_evn_begin, è già gestito dalla prima condizione di "Notte Profonda".
        # Se, nonostante tutto, non si rientra in nessuna fascia specifica ma nijel_info era presente,
        # si passerà al fallback basato sull'ora qui sotto, ma con la possibilità di
        # usare ancora i timestamp specifici di alba/mezzogiorno/tramonto se disponibili.
    
    # --- Fallback alla logica basata sull'ora del CALENDARIO ---
    # Questo blocco viene eseguito se nijel_info_for_current_day non era valido
    # o se l'ora corrente non è rientrata in una delle fasce sfumate sopra.
    # Le fasce orarie del calendario Anthaleja (HXD_CALENDAR = 28 ore, da 0 a 27):
    # Notte (Nahr):    26, 27, 00, 01, 02, 03, 04, 05, 06
    # Mattino (Nalmek): 07, 08, 09, 10, 11, 12, 13
    # Pomeriggio (Daja):14, 15, 16, 17, 18, 19, 20
    # Sera (San):      21, 22, 23, 24, 25
    
    if hour_of_day_calendar >= 26 or hour_of_day_calendar < 7:
        # Se abbiamo nijel_info, possiamo ancora provare a identificare il "Crepuscolo Pre-Alba"
        ts_sra_fb = get_ts("sunrise_actual") # get_ts è definita e sicura anche se nijel_info è None
        if ts_sra_fb is not None and \
           abs(current_ts - ts_sra_fb) < (1.5 * ixh_cal * sxi_cal) and \
        current_ts < ts_sra_fb : # È prima dell'alba effettiva ma entro 1.5 ore calendariali
            return "Crepuscolo Pre-Alba (Nahr)"
        return "Notte (Nahr)"
    elif hour_of_day_calendar < 14: # Fascia mattutina (ore calendariali 7-13)
        ts_sra_fb = get_ts("sunrise_actual")
        # Se siamo vicini all'alba (+/- 1 ora calendariale)
        if ts_sra_fb is not None and \
           abs(current_ts - ts_sra_fb) < (1.0 * ixh_cal * sxi_cal) :
            return "Alba (Kelth)" # Nome del lore per l'alba
        return "Mattino (Nalmek)"
    elif hour_of_day_calendar < 21: # Fascia pomeridiana (ore calendariali 14-20)
        ts_sn_fb = get_ts("transit_true_local")
        # Se siamo vicini al mezzogiorno solare (+/- 1 ora calendariale)
        if ts_sn_fb is not None and \
           abs(current_ts - ts_sn_fb) < (1.0 * ixh_cal * sxi_cal) :
            return "Mezzogiorno (Daja)"
        return "Pomeriggio (Daja)"
    else: # Fascia serale (ore calendariali 21-25)
        ts_ssa_fb = get_ts("sunset_actual")
        # Se siamo vicini al tramonto (+/- 1 ora calendariale)
        if ts_ssa_fb is not None and \
           abs(current_ts - ts_ssa_fb) < (1.0 * ixh_cal * sxi_cal) :
            return "Tramonto (San)"
        return "Sera (San)"

def format_interval_relative(
    diff_interval: Optional[ATHDateInterval], # L'intervallo calcolato, es. da base_date.diff(event_date)
    # base_date: ATHDateTimeInterface, # Non usata direttamente se diff_interval.invert è affidabile
    # event_date: Optional[ATHDateTimeInterface], # Non usata direttamente se diff_interval è già calcolato
    is_event_in_future: bool # Indica esplicitamente la direzione
) -> str:
    """
    Formatta un oggetto ATHDateInterval in una stringa di tempo relativo leggibile,
    indicando se l'evento è nel futuro ("fra...") o nel passato ("...fa")
    rispetto a una data di riferimento.
    Args:
        diff_interval: L'oggetto ATHDateInterval che rappresenta la differenza
                    di tempo. Si assume che i suoi componenti (y, m, d, h, i, s)
                    siano sempre positivi e che il flag 'invert' o il parametro
                    'is_event_in_future' indichi la direzione.
        is_event_in_future: Booleano che indica se l'evento a cui si riferisce
                            l'intervallo è nel futuro (True) o nel passato (False)
                            rispetto alla data di riferimento implicita.

    Returns:
        str: Una stringa formattata come "fra Xg Yh", "Xg Yh fa", "Imminente",
            "Adesso/Poco Fa", o "N/A" se l'intervallo non è valido.
    """
    if not diff_interval:
        return "N/A"

    # Il flag 'is_event_in_future' determina il prefisso/suffisso.
    # Assumiamo che i componenti dell'intervallo (y,m,d,h,i,s) siano sempre valori assoluti.
    # Il metodo ATHDateInterval.diff() dovrebbe impostare interval.invert=True
    # se datetime1.diff(datetime2) e datetime2 è nel futuro di datetime1.
    # Quindi, is_event_in_future può essere direttamente interval.invert.

    parts = []
    # Componenti dell'intervallo (assunti positivi)
    y, m, d, h, i, s, f_us = diff_interval.y, diff_interval.m, diff_interval.d, \
                            diff_interval.h, diff_interval.i, diff_interval.s, \
                            diff_interval.f

    if y > 0: parts.append(f"{y}a")
    if m > 0: parts.append(f"{m}M") # M per Mesi (Months)
    if d > 0: parts.append(f"{d}g") # g per giorni (giornate)
    
    # Mostra ore e minuti solo se l'intervallo è relativamente breve (es. meno di 3 giorni)
    # o se sono gli unici componenti significativi.
    if y == 0 and m == 0 and d < 3:
        if h > 0: parts.append(f"{h}h")
        if i > 0: parts.append(f"{i}m")
        # Considera di aggiungere i secondi se l'intervallo è solo di secondi e minuti,
        # e non ci sono giorni/ore.
        if y == 0 and m == 0 and d == 0 and h == 0 and i > 0 and s > 0:
            parts.append(f"{s}s")

    if not parts: # Se l'intervallo è molto breve (nessuna parte y, m, d, h, i (significativa) è stata aggiunta)
        # Calcola i secondi totali dell'intervallo per decidere l'output.
        # total_earth_seconds() in ATHDateInterval dovrebbe restituire la durata fisica assoluta.
        # Se diff_interval è stato creato da .diff(), il suo .invert flag dovrebbe essere
        # già impostato, ma total_earth_seconds() potrebbe non tenerne conto direttamente
        # a meno che non sia `abs(interval.total_earth_seconds())`.
        # Per questa logica, ci serve la durata assoluta.
        
        # Ricostruiamo i secondi totali calendariali assoluti per confronto
        abs_total_seconds_calendar = float(s) + f_us
        abs_total_seconds_calendar += float(i) * ATHDateTimeInterface.SXI 
        abs_total_seconds_calendar += float(h) * ATHDateTimeInterface.IXH * ATHDateTimeInterface.SXI
        # Non aggiungiamo giorni, mesi, anni qui perché 'parts' sarebbe già popolata.

        if abs_total_seconds_calendar < ATHDateTimeInterface.SXI: # Meno di un minuto calendariale
            return "Imminente" if is_event_in_future else "Adesso/Poco Fa"
        elif abs_total_seconds_calendar < (ATHDateTimeInterface.IXH * ATHDateTimeInterface.SXI): # Meno di un'ora calendariale
            minutes_only = math.floor(abs_total_seconds_calendar / ATHDateTimeInterface.SXI)
            if minutes_only > 0 : # Mostra solo minuti se è l'unica unità significativa
                parts.append(f"{minutes_only}m")
            # Potremmo aggiungere i secondi se i minuti sono 0 ma ci sono secondi.
            elif s > 0 or f_us > 0:
                parts.append(f"{s + math.floor(f_us)}s")

    if not parts: # Se, nonostante tutto, 'parts' è ancora vuota (es. intervallo esattamente 0)
        return "Adesso" # O "N/A" se si preferisce non dire "Adesso" per intervalli nulli

    # Limita il numero di "parti" visualizzate per leggibilità (es. le prime 2 o 3 più significative)
    display_str = " ".join(parts[:2]) # Mostra al massimo 2 parti (es. "1a 2M", "2g 3h", "10m 5s")
    
    if is_event_in_future:
        return f"fra {display_str}"
    else:
        return f"{display_str} fa"
