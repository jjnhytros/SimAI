"""
Configurazioni specifiche per la TUI (Textual User Interface).
"""
from core.enums import NeedType, Gender, ObjectType

# Mappa che associa ogni NeedType a un dizionario di configurazione per la UI
NEED_UI_CONFIG = {
    NeedType.HUNGER: {
        "icon": "🍔", "color": "orange", "color_critical": "bright_red", "color_low": "yellow",
    },
    NeedType.ENERGY: {
        "icon": "⚡", "color": "yellow", "color_critical": "bright_red", "color_low": "gold3",
    },
    NeedType.SOCIAL: {
        "icon": "👥", "color": "green", "color_critical": "bright_red", "color_low": "yellow",
    },
    NeedType.FUN: {
        "icon": "🎉", "color": "magenta", "color_critical": "bright_red", "color_low": "yellow",
    },
    NeedType.HYGIENE: {
        "icon": "🧼", "color": "cyan", "color_critical": "bright_red", "color_low": "yellow",
    },
    NeedType.BLADDER: {
        "icon": "🚽", "color": "green_yellow", "color_critical": "bright_red", "color_low": "yellow",
    },
    NeedType.INTIMACY: {
        "icon": "💖", "color": "hot_pink", "color_critical": "bright_red", "color_low": "yellow",
    },
    NeedType.THIRST: {
        "icon": "💧", "color": "dodger_blue", "color_critical": "bright_red", "color_low": "yellow",
    },
}

# --- Colori per la Rappresentazione degli NPC per Genere ---
# Usiamo tuple RGB (0-255) per i colori Pygame
NPC_GENDER_COLORS = {
    Gender.MALE: (0, 128, 255),        # Blu
    Gender.FEMALE: (255, 105, 180),    # Rosa (HotPink)
    Gender.NON_BINARY: (128, 0, 128),  # Viola
    Gender.OTHER: (100, 100, 100),     # Grigio
    Gender.UNKNOWN: (200, 200, 200)    # Grigio chiaro
}

DEFAULT_NPC_COLOR = (50, 50, 50) # Grigio scuro per fallback
NPC_CRITICAL_NEED_INDICATOR_COLOR = (255, 0, 0) # Rosso per il bordo

# --- Colori per la Rappresentazione degli Oggetti per Tipo ---
# Usiamo tuple RGB (0-255) per i colori Pygame
GAME_OBJECT_TYPE_COLORS = {
    ObjectType.REFRIGERATOR: (220, 220, 220), # Grigio chiaro
    ObjectType.STOVE: (105, 105, 105),      # Grigio scuro (DimGray)
    ObjectType.SINK: (176, 224, 230),      # Azzurro polvere (PowderBlue)
    ObjectType.TOILET: (245, 245, 245),      # Bianco fumo (WhiteSmoke)
    ObjectType.SHOWER: (173, 216, 230),      # Azzurro chiaro (LightBlue)
    ObjectType.BED: (139, 69, 19),         # Marrone sella (SaddleBrown)
    ObjectType.BOOKSHELF: (160, 82, 45),    # Siena (Sienna)
    ObjectType.COMPUTER: (70, 130, 180),     # Blu acciaio (SteelBlue)
    ObjectType.TV: (50, 50, 50),           # Grigio molto scuro
    ObjectType.SOFA: (210, 105, 30),       # Cioccolato
    ObjectType.TABLE: (205, 133, 63),      # Peru (marrone chiaro)
    ObjectType.CHAIR: (222, 184, 135),      # BurlyWood (beige)
    ObjectType.PHONE: (119, 136, 153),     # Grigio ardesia chiaro (LightSlateGray)
    ObjectType.BOOK: (72, 61, 139),        # Blu ardesia scuro (DarkSlateBlue)
    ObjectType.GUITAR: (139, 0, 0),         # Rosso scuro (DarkRed)
    ObjectType.PIANO: (30, 30, 30),          # Quasi nero
    ObjectType.EASEL: (244, 164, 96),       # Sabbia marrone (SandyBrown)
    ObjectType.CHESS_TABLE: (0, 100, 0),    # Verde scuro
    ObjectType.CASH_REGISTER: (192, 192, 192), # Argento
    ObjectType.VENDING_MACHINE: (65, 105, 225),# Blu reale
    ObjectType.BAR_COUNTER: (123, 63, 0),    # Marrone scuro tipo legno
}
DEFAULT_GAME_OBJECT_COLOR = (150, 150, 150) # Grigio medio per fallback

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
