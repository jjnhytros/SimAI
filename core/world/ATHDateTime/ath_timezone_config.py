# simai/core/world/ath_timezone_config.py
from .ATHDateTimeZone import ATHDateTimeZone
from .ATHDateTimeZoneInterface import ATHDateTimeZoneInterface

# Variabile "privata" di modulo per contenere l'oggetto timezone di default.
# Viene inizializzata con ATZ come fallback.
_current_default_ath_timezone_obj: ATHDateTimeZoneInterface

try:
    _current_default_ath_timezone_obj = ATHDateTimeZone("ATZ")
except Exception as e:
    print(f"ATTENZIONE: Impossibile inizializzare il fuso orario di default globale. Errore: {e}")
    # Lasciamo _current_default_ath_timezone_obj non inizializzato,
    # la funzione get lo gestirà.

def get_default_ath_timezone() -> ATHDateTimeZoneInterface:
    """
    Funzione helper interna per accedere al fuso orario di default corrente.
    Restituisce sempre un'istanza valida (ATZ se il default non è valido).
    """
    global _current_default_ath_timezone_obj
    # Se l'oggetto non è un'istanza valida, tenta di ricrearlo.
    if not isinstance(_current_default_ath_timezone_obj, ATHDateTimeZoneInterface):
        try:
            _current_default_ath_timezone_obj = ATHDateTimeZone("ATZ")
        except ValueError:
            raise RuntimeError("CRITICO: Impossibile definire il fuso orario di default ATZ.")
    return _current_default_ath_timezone_obj

def set_default_ath_timezone(timezone_id: str) -> bool:
    """
    Imposta il fuso orario Anthalejano di default usato dalle funzioni data/ora.
    """
    global _current_default_ath_timezone_obj
    try:
        new_default_tz = ATHDateTimeZone(timezone_id)
        _current_default_ath_timezone_obj = new_default_tz
        return True
    except ValueError:
        return False