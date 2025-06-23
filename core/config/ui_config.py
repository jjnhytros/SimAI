"""
Configurazioni specifiche per la TUI (Textual User Interface).
"""
from core.enums import (
    NeedType, Gender, ObjectType, TimeOfDay
)
from core.enums.relationship_types import RelationshipType

FONT_PATH = "assets/fonts/EasyReading.otf"
FONT_FALLBACK_SYSTEM = "arial" # Un font comune che potrebbe essere sul sistema

# Definiamo le dimensioni che useremo
FONT_SIZE_LARGE = 22
FONT_SIZE_MEDIUM_BOLD = 18
FONT_SIZE_SMALL = 16
FONT_SIZE_DEBUG = 14
FONT_SIZE_CLAIRE = 19

# --- LAYOUT ---
PANEL_WIDTH = 320
TILE_SIZE = 32 # Dimensione base in pixel di una mattonella
NPC_RADIUS_OFFSET = 3 # Raggio dell'NPC = TILE_SIZE / 2 - OFFSET
LINE_HEIGHT = 20 # Altezza di una linea di testo nel pannello

# --- ZOOM ---
MIN_ZOOM = 0.5
MAX_ZOOM = 3.0

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
    Gender.MALE: (100, 150, 255),        # Blu
    Gender.FEMALE: (255, 100, 150),      # Rosa (HotPink)
    Gender.NON_BINARY: (150, 100, 255),  # Viola
    Gender.OTHER: (100, 100, 100),       # Grigio
    Gender.UNKNOWN: (200, 200, 200)      # Grigio chiaro
}
DEFAULT_NPC_COLOR = (128, 128, 128) # Un grigio neutro

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

# --- COLORI INTERFACCIA ---
# Colori base
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEXT_COLOR = (230, 230, 230) # Colore di default per il testo del pannello

# Pannello UI
PANEL_BG_COLOR = (40, 40, 60) # Sfondo del pannello laterale

# Elementi di Gioco
SELECTION_COLOR = (255, 255, 0) # Giallo per l'anello di selezione

# --- COLORI PER BARRE DI STATO CON GRADIENTE ---
NEED_BAR_GREEN = (20, 200, 120)
NEED_BAR_YELLOW = (255, 220, 50)
NEED_BAR_ORANGE = (255, 140, 50)
NEED_BAR_RED = (220, 40, 40)
NEED_BAR_DARK_RED = (150, 20, 20)
NPC_CRITICAL_NEED_INDICATOR_COLOR = (255, 20, 20) # Rosso acceso

# Mappa che associa ORE SPECIFICHE (su 28) a un colore (RGB).
# Questi sono i nostri "fotogrammi chiave". La sfumatura avverrà TRA questi punti.
DAY_NIGHT_COLOR_KEYFRAMES = {
    # Notte
    0:  (25, 25, 50),     # Blu quasi nero (mezzanotte del gioco)
    4:  (25, 25, 50),     # La notte rimane scura fino alle 4:00
    # Alba
    5:  (70, 70, 120),    # Inizio dell'alba, un tocco di viola
    7:  (135, 206, 235),  # Mattina piena, cielo azzurro chiaro
    # Giorno
    14: (100, 149, 237),  # Mezzogiorno / Primo pomeriggio, blu intenso e pieno
    18: (100, 149, 237),  # Il colore del pomeriggio rimane stabile fino alle 18:00
    # Tramonto
    19: (255, 165, 0),    # Inizio del tramonto, arancione
    21: (255, 69, 0),     # Tramonto profondo, rosso-arancio
    # Sera
    23: (40, 40, 80),     # Sera, blu notte scuro
    # Ritorno alla Notte
    26: (25, 25, 50),     # La notte è di nuovo completamente scura
}

DEFAULT_DAY_BG_COLOR = (128, 128, 128) # Grigio di fallback

# --- ICONE UNICODE PER RELAZIONI ---
RELATIONSHIP_ICONS = {
    # === Relazioni Familiari Dirette ===
    RelationshipType.PARENT:                   ("👨‍👩‍👧", (205, 170, 51)),    # Famiglia (Oro)
    RelationshipType.CHILD:                    ("🧒", (255, 255, 102)),   # Bambino (Giallo)
    RelationshipType.GRANDPARENT:              ("👴", (192, 192, 192)),   # Anziano (Argento)
    RelationshipType.GRANDCHILD:               ("🧒", (255, 255, 102)),   # Bambino (Giallo)
    RelationshipType.SIBLING:                  ("🧑‍🤝‍🧑", (0, 206, 209)),     # Fratelli (Ciano)
    RelationshipType.SPOUSE:                   ("💍", (255, 215, 0)),     # Anello (Oro brillante)
    
    # === Relazioni Familiari Estese (usano la stessa icona per semplicità) ===
    RelationshipType.EXTENDED_FAMILY:          ("🏡", (107, 142, 35)),    # Casa (Verde Oliva)
    RelationshipType.AUNT_UNCLE:               ("🏡", (107, 142, 35)),
    RelationshipType.NEPHEW_NIECE:             ("🏡", (107, 142, 35)),
    RelationshipType.COUSIN:                   ("🏡", (107, 142, 35)),
    # Aggiungi qui gli altri tipi di parenti estesi con la stessa icona
    RelationshipType.GREAT_GRANDPARENT:        ("👴", (192, 192, 192)),
    RelationshipType.GREAT_GRANDCHILD:         ("🧒", (255, 255, 102)),
    # ... e così via ...

    # === Relazioni Sociali Non Familiari ===
    RelationshipType.CHILDHOOD_BEST_FRIEND:    ("🌟", (255, 223, 0)),     # Stella (Giallo oro)
    RelationshipType.FRIEND_CLOSE:             ("😊", (173, 255, 47)),      # Faccina felice (Verde brillante)
    RelationshipType.FRIEND_REGULAR:           ("🙂", (135, 206, 250)),   # Faccina normale (Celeste)
    RelationshipType.ACQUAINTANCE:             ("💬", (200, 200, 200)),   # Fumetto (Grigio)
    
    # === Relazioni Romantiche ===
    RelationshipType.ROMANTIC_PARTNER:         ("❤️", (255, 105, 180)),   # Cuore (Rosa)
    RelationshipType.CRUSH:                    ("🥰", (255, 182, 193)),   # Faccina con cuori (Rosa chiaro)
    RelationshipType.EX_PARTNER:               ("💔", (138, 121, 153)),   # Cuore spezzato (Viola spento)
    
    # === Relazioni Negative ===
    RelationshipType.ENEMY_RIVAL:              ("⚔️", (255, 140, 0)),       # Spade (Arancione)
    RelationshipType.ENEMY_DISLIKED:           ("😠", (255, 69, 0)),      # Faccina arrabbiata (Rosso-Arancio)
    
    # === Relazioni Professionali / Contestuali ===
    RelationshipType.COLLEAGUE:                ("💼", (70, 130, 180)),    # Valigetta (Blu acciaio)
    RelationshipType.NEIGHBOR:                 ("🏠", (139, 69, 19)),     # Casa (Marrone)
    RelationshipType.MENTOR:                   ("🧑‍🏫", (147, 112, 219)),  # Insegnante (Viola medio)
    RelationshipType.MENTEE:                   ("🎓", (176, 224, 230)),  # Tocco laurea (Azzurro polvere)
    RelationshipType.ROOMMATE:                 ("🔑", (184, 134, 11)),    # Chiave (Ocra)
    
    # Default per tipi non mappati
    "default":                                 ("⚫", (150, 150, 150))   # Punto nero (Grigio scuro)
}
# TODO: Aggiungere qui altre configurazioni UI come stili, layout, ecc.
