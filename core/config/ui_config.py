"""
Configurazioni specifiche per la TUI (Textual User Interface).
"""
from core.enums import NeedType

# Mappa che associa ogni NeedType a un dizionario di configurazione per la UI
NEED_UI_CONFIG = {
    NeedType.HUNGER: {
        "icon": "🍔",
        "color": "orange",
        "color_critical": "bright_red",
        "color_low": "yellow",
    },
    NeedType.ENERGY: {
        "icon": "⚡",
        "color": "yellow",
        "color_critical": "bright_red",
        "color_low": "gold3",
    },
    NeedType.SOCIAL: {
        "icon": "👥",
        "color": "green",
        "color_critical": "bright_red",
        "color_low": "yellow",
    },
    NeedType.FUN: {
        "icon": "🎉",
        "color": "magenta",
        "color_critical": "bright_red",
        "color_low": "yellow",
    },
    NeedType.HYGIENE: {
        "icon": "🧼",
        "color": "cyan",
        "color_critical": "bright_red",
        "color_low": "yellow",
    },
    NeedType.BLADDER: {
        "icon": "🚽",
        "color": "green_yellow",
        "color_critical": "bright_red",
        "color_low": "yellow",
    },
    NeedType.INTIMACY: {
        "icon": "💖",
        "color": "hot_pink",
        "color_critical": "bright_red",
        "color_low": "yellow",
    },
    # --- NUOVA VOCE PER THIRST ---
    NeedType.THIRST: {
        "icon": "💧",
        "color": "dodger_blue",
        "color_critical": "bright_red",
        "color_low": "yellow",
    },
    # --- FINE NUOVA VOCE ---
}

# --- Interfaccia Utente ---
HEADER_HEIGHT_CURSES = 3
LOG_WINDOW_HEIGHT_CURSES = 10
MAIN_WINDOW_HEIGHT_CURSES = 20
STATUS_BAR_HEIGHT_CURSES = 1

# --- Report e Salvataggi ---
AUTOSAVE_ON_DAY_END = True
ENABLE_CONSOLE_DAILY_REPORT = True
ENABLE_CONSOLE_MONTHLY_REPORT = True
ENABLE_CONSOLE_ANNUAL_REPORT = True
ENABLE_CONSOLE_HOURLY_SUMMARY_IN_CONTINUOUS = True
HOURLY_SUMMARY_INTERVAL = 3
HOURLY_SUMMARY_INTERVAL_CONTINUOUS_MODE = 6

ENABLE_FILE_REPORTS = True
REPORT_FILENAME = "simai_simulation_chronicles.log"
ENABLE_FILE_DAILY_REPORT = True
ENABLE_FILE_MONTHLY_REPORT = True
ENABLE_FILE_ANNUAL_REPORT = True

# --- Colori ANSI ---
class ANSIColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    MALE_COLOR = "\033[96m"
    FEMALE_COLOR = "\033[95m"
    NEED_HUNGER_COLOR = "\033[31m"
    NEED_ENERGY_COLOR = "\033[34m"
    NEED_SOCIAL_COLOR = "\033[32m"
    NEED_FUN_COLOR = "\033[33m"
    NEED_HYGIENE_COLOR = "\033[36m"
    NEED_BLADDER_COLOR = "\033[35m"
    NEED_INTIMACY_COLOR = "\033[91m"
    EVENT_POSITIVE_COLOR = "\033[92m"
    EVENT_NEGATIVE_COLOR = "\033[91m"
    EVENT_NEUTRAL_COLOR = "\033[94m"
    REPORT_TITLE_COLOR = "\033[1m\033[93m"
    DEBUG_COLOR = "\033[1m\033[93m"
    
# TODO: Aggiungere qui altre configurazioni UI come stili, layout, ecc.
