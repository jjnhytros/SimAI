# simai/game/config.py
# MODIFIED: Added DEBUG_AI_ACTIVE, cleaned up comments.
# MODIFIED AGAIN: Added new constants for NPC behavior, needs, and save/load.

import pygame 
import os
import datetime 

# --- Game Name and Versioning ---
GAME_NAME = "SimAI"
CORE_VERSION = "0.3.0" 
BUILD_METADATA = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
FULL_VERSION_INTERNAL = f"{CORE_VERSION}+{BUILD_METADATA}" 
WINDOW_TITLE = f"{GAME_NAME} v{CORE_VERSION}" 
# --- End Game Name and Versioning ---

# --- DEBUG Settings ---
DEBUG_MODE_ACTIVE = True       # Flag generale per attivare logiche di debug specifiche (es. randomizzazione bisogni)
DEBUG_AI_ACTIVE = True         # Flag per attivare stampe di debug verbose (IA, Save/Load, Utils, etc.)

# Valori specifici per DEBUG_MODE_ACTIVE = True
DEBUG_ENERGY_INITIAL_MIN_PCT = 0.05 
DEBUG_ENERGY_INITIAL_MAX_PCT = 0.15
DEBUG_HUNGER_INITIAL_MIN_PCT = 0.70 
DEBUG_HUNGER_INITIAL_MAX_PCT = 0.85 

# --- Screen and General Settings ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
PANEL_UI_HEIGHT = 150 # Altezza del pannello UI inferiore
# FONT_NAME è usato in character.py e altrove, assicuriamoci che sia definito
# Se usi un font specifico, specifica il percorso del file .ttf, altrimenti None per il font di default di Pygame.
FONT_NAME = None  # Esempio: "assets/fonts/YourFont.ttf" o None per default
FONT_SIZE = 20    # Dimensione di default per il testo generico, UI_FONT_SIZE è per la UI principale

# --- Grid and Tiles ---
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - PANEL_UI_HEIGHT) // TILE_SIZE # Altezza della griglia di gioco effettiva

# --- Time System ---
GAME_HOURS_IN_DAY = 28
INITIAL_START_HOUR = 7.0 
DAYS_PER_MONTH = 24    
MONTHS_PER_YEAR = 18   
GAME_DAYS_PER_YEAR = DAYS_PER_MONTH * MONTHS_PER_YEAR
TIME_SPEED_SETTINGS = { 
    0: float('inf'), 1: 240.0, 2: 120.0, 3: 60.0, 4: 30.0, 5: 15.0
} # Secondi reali per passare un'ora di gioco
TIME_SPEED_SLEEP_ACCELERATED_INDEX = 5 # Indice della velocità massima quando tutti dormono
PERIOD_DEFINITIONS = [
    (0.0, "Tarda Notte", "night.svg"),        # Da 00:00 fino a (ma escluso) 6.0
    (6.0, "Alba", "dawn.svg"),              # Da 06:00 fino a 7.0
    (7.0, "Mattina", "sunrise.svg"),         # Da 07:00 fino a 12.0 (o sun.svg)
    (12.0, "Mezzogiorno", "sun.svg"),         # Da 12:00 fino a 14.0
    (14.0, "Pomeriggio", "sun.svg"),        # Da 14:00 fino a 19.0
    (19.0, "Tramonto", "sunset.svg"),       # Da 19:00 fino a 21.0
    (21.0, "Sera", "moon.svg"),             # Da 21:00 fino a 23.0
    (23.0, "Notte", "night.svg")            # Da 23:00 fino alla fine della giornata (GAME_HOURS_IN_DAY)
]

# --- Colors ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
NEED_COLOR_VERY_BAD = (255, 0, 0)    
NEED_COLOR_BAD = (255, 120, 0)   
NEED_COLOR_MEDIUM = (255, 255, 0)  
NEED_COLOR_OKAY = (120, 255, 0)  
NEED_COLOR_GOOD = (0, 200, 0)    

TEXT_COLOR_LIGHT = (220, 220, 220)
TEXT_COLOR_DARK = (30, 30, 50)
DEBUG_GRID_COLOR = (50, 50, 50)
DEBUG_OBSTACLE_COLOR = (100, 0, 0)

DEEP_NIGHT_COLOR = (10, 10, 30)
PRE_DAWN_COLOR = (25, 25, 55)
VIVID_DAWN_COLOR = (100, 90, 140)
EARLY_MORNING_COLOR = (120, 140, 190)
FULL_MORNING_COLOR = (135, 206, 235)
BRIGHT_DAY_COLOR = (170, 225, 255)
WARM_AFTERNOON_COLOR = (220, 200, 160)
EARLY_SUNSET_COLOR = (255, 180, 100)
VIVID_SUNSET_COLOR = (255, 130, 70)
RED_SUNSET_COLOR = (200, 80, 60)
TWILIGHT_COLOR = (70, 60, 90)

SKY_KEYFRAMES = [ 
    (0, DEEP_NIGHT_COLOR), (4, PRE_DAWN_COLOR), (6, VIVID_DAWN_COLOR),
    (8, EARLY_MORNING_COLOR), (11, FULL_MORNING_COLOR), (14, BRIGHT_DAY_COLOR),
    (17, WARM_AFTERNOON_COLOR), (19, EARLY_SUNSET_COLOR), (21, VIVID_SUNSET_COLOR),
    (23, RED_SUNSET_COLOR), (25, TWILIGHT_COLOR), (28, DEEP_NIGHT_COLOR) 
]

# --- Asset Paths ---
GAME_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_ASSET_PATH = os.path.join(GAME_DIR_PATH, "assets") 
IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "images")
ICON_PATH = os.path.join(IMAGE_PATH, "icons") 
FURNITURE_IMAGE_PATH = os.path.join(IMAGE_PATH, "furnitures") 
CHARACTER_SPRITE_PATH = os.path.join(IMAGE_PATH, "characters")
FONT_PATH = os.path.join(BASE_ASSET_PATH, "fonts") # Esempio
# FONT_NAME = os.path.join(FONT_PATH, "YourFontFile.ttf") # Se vuoi specificare un file

# --- Interactive Objects: Base Properties ---
BED_SPRITESHEET_BASE_RECT_COORDS = (0, 0, 64, 81)  
BED_SPRITESHEET_COVER_RECT_COORDS = (0, 106, 64, 22) 
DESIRED_BED_WIDTH = 64 
DESIRED_BED_HEIGHT = 81 
BED_COLOR_FALLBACK = (100,70,30) 
# DESIRED_BED_X = SCREEN_WIDTH - DESIRED_BED_WIDTH - 10 
# DESIRED_BED_Y = SCREEN_HEIGHT - PANEL_UI_HEIGHT - DESIRED_BED_HEIGHT - 10 
DESIRED_BED_X = SCREEN_WIDTH // 2 
DESIRED_BED_Y = SCREEN_HEIGHT // 2
BED_COVER_DRAW_OFFSET_Y = 26 
BED_SLOT_1_OFFSET = (TILE_SIZE // 2, TILE_SIZE * 1.5) 
BED_SLOT_2_OFFSET = (TILE_SIZE * 1.5, TILE_SIZE * 1.5) 
BED_SLOT_1_INTERACTION_OFFSET = (-6, 97) 
BED_SLOT_2_INTERACTION_OFFSET = (26, 97)
BED_SLOT_1_SLEEP_POS_OFFSET = (TILE_SIZE * 0.5, TILE_SIZE * 0.8) 
BED_SLOT_2_SLEEP_POS_OFFSET = (TILE_SIZE * 1.5, TILE_SIZE * 0.8) 

TOILET_RECT_PARAMS = {"x": 800, "y": 100, "w": TILE_SIZE * 1, "h": TILE_SIZE * 2} 
TOILET_COLOR = (210, 210, 225) 

FOOD_POS = (100, 100) 
FOOD_RADIUS = min(10, TILE_SIZE // 2 - 2)
FOOD_COLOR = GREEN 
FOOD_VALUE = 30
FOOD_RESPAWN_TIME = 20.0 

# --- Action Values & Durations ---
SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE = 40.0 
ENERGY_RECOVERY_RATE_PER_HOUR = 15.0
BLADDER_RELIEF_AMOUNT = 85      
TOILET_USE_DURATION_HOURS = 0.20 
FUN_GAINED_AMOUNT = 40 
HYGIENE_GAINED_AMOUNT = 70 

ROMANTIC_INTERACTION_CHANCE = 0.60       
INTIMACY_SATISFACTION_ROMANTIC = 60    
INTIMACY_SATISFACTION_AFFECTIONATE = 15  
SOCIAL_SATISFACTION_AFFECTIONATE = 10  
INTIMACY_INTERACTION_DURATION_HOURS = 1.0 
HEART_COLOR_ROMANTIC = RED                
HEART_COLOR_AFFECTIONATE = (255,105,180)  
PREGNANCY_CHANCE_FEMALE = 0.25
# PREGNANCY_TERM_GAME_DAYS = DAYS_PER_MONTH # Questa è già definita, ma la sposto sotto per raggruppamento logico

# --- Need Bar Gradient Colors ---
NEED_BAR_BORDER_COLOR = (150, 150, 150) 

# --- UI Constants ---
UI_FONT_SIZE = 26 
# FONT_NAME è già definito sopra in "Screen and General Settings"

# --- NPC Configuration ---
# CHARACTER_SPEED rinominata da NPC_SPEED per coerenza e già presente sotto "NPC AI Constants"
# NPC_SPEED = 80 # Vecchia, ora CHARACTER_SPEED
CHARACTER_SPEED = 80.0  # Velocità base degli NPC in pixel/secondo (float per calcoli più precisi con dt)
#NPC_SPEED = CHARACTER_SPEED # Aggiunto per compatibilità

NPC_MOVEMENT_SPEED_MULTIPLIERS = { # Questi erano già presenti, li lascio
    0: 0.0, 1: 0.75, 2: 1.0, 3: 1.5, 4: 2.0, 5: 2.5   
}
# Soglie dei bisogni per l'IA (già presenti, le lascio per completezza di sezione)
NPC_HUNGER_THRESHOLD = 70
NPC_ENERGY_THRESHOLD = 30
NPC_SOCIAL_THRESHOLD = 40
NPC_BLADDER_THRESHOLD = 75 
NPC_FUN_THRESHOLD = 30     
NPC_HYGIENE_THRESHOLD = 25 
NPC_INTIMACY_THRESHOLD = 75 

NPC_EAT_REACH_DISTANCE = 15 
NPC_BED_REACH_DISTANCE = TILE_SIZE * 1.8 
NPC_PARTNER_INTERACTION_DISTANCE = TILE_SIZE * 1.5 
NPC_TOILET_REACH_DISTANCE = TILE_SIZE * 1.0 
NPC_FUN_OBJECT_REACH_DISTANCE = TILE_SIZE * 1.0 
NPC_SHOWER_REACH_DISTANCE = TILE_SIZE * 1.0  

NPC_IDLE_WANDER_CHANCE = 0.02
NPC_WANDER_MIN_DIST_TILES = 3
NPC_WANDER_MAX_DIST_TILES = 8

# Costanti relative alla gravidanza e al ciclo di vita degli NPC
NPC_PREGNANCY_DURATION_DAYS = DAYS_PER_MONTH # Durata della gravidanza in giorni di gioco (es. 1 mese di gioco)
PREGNANCY_TERM_GAME_DAYS = NPC_PREGNANCY_DURATION_DAYS # Sinonimo, se preferisci (era già qui)
NPC_POST_PREGNANCY_COOLDOWN_SECONDS = (GAME_HOURS_IN_DAY * 3600) * 7 # Cooldown post-parto in secondi di gioco (es. 7 giorni di gioco)

# --- Need System Base Rates & Initial Values & Update Logic ---
NEED_UPDATE_INTERVAL_SECONDS = 10.0 # Intervallo in secondi REALI per l'aggiornamento del decay dei bisogni

DEFAULT_MAX_NEED_VALUE = 100.0
HUNGER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HUNGER_INITIAL_MIN_PCT = 0.0  
HUNGER_INITIAL_MAX_PCT = 0.6  
HUNGER_BASE_RATE = 2.0        
HUNGER_HIGH_IS_GOOD = False   
HUNGER_RATE_MULTIPLIERS = {"Notte": 0.5, "Mattino": 1.2, "Mezzogiorno": 1.5, "Sera": 1.3}
ENERGY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
ENERGY_INITIAL_MIN_PCT = 0.4 
ENERGY_INITIAL_MAX_PCT = 1.0 
ENERGY_BASE_DECAY_RATE = 5.5 
ENERGY_HIGH_IS_GOOD = True
ENERGY_DECAY_MULTIPLIERS = {"Notte": 0.3, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 0.8}
SOCIAL_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
SOCIAL_INITIAL_MIN_PCT = 0.4
SOCIAL_INITIAL_MAX_PCT = 1.0
SOCIAL_BASE_DECAY_RATE = 1.4
SOCIAL_HIGH_IS_GOOD = True
SOCIAL_DECAY_MULTIPLIERS = {"Notte": 0.7, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.5}
BLADDER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
BLADDER_INITIAL_MIN_PCT = 0.0
BLADDER_INITIAL_MAX_PCT = 0.65
BLADDER_BASE_FILL_RATE = 3.0 
BLADDER_HIGH_IS_GOOD = False
BLADDER_FILL_MULTIPLIERS = {"Notte": 0.4, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.0}
FUN_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
FUN_INITIAL_MIN_PCT = 0.3
FUN_INITIAL_MAX_PCT = 1.0
FUN_BASE_DECAY_RATE = 2.5
FUN_HIGH_IS_GOOD = True
FUN_DECAY_MULTIPLIERS = {"Notte": 0.6, "Mattino": 1.0, "Mezzogiorno": 1.3, "Sera": 1.1}
HYGIENE_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HYGIENE_INITIAL_MIN_PCT = 0.5
HYGIENE_INITIAL_MAX_PCT = 1.0
HYGIENE_BASE_DECAY_RATE = 1.8
HYGIENE_HIGH_IS_GOOD = True
HYGIENE_DECAY_MULTIPLIERS = {"Notte": 0.5, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.0}
INTIMACY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE 
INTIMACY_INITIAL_MIN_PCT = 0.0
INTIMACY_INITIAL_MAX_PCT = 0.3
INTIMACY_BASE_INCREASE_RATE = 0.8 # Nota: questo è un tasso di AUMENTO, non di decadimento
INTIMACY_HIGH_IS_GOOD = False # Assumendo che Intimacy sia un bisogno da soddisfare (basso -> alto)
INTIMACY_INCREASE_RATE_MULTIPLIERS = {"Notte": 1.0, "Mattino": 1.0, "Mezzogiorno": 1.1, "Sera": 1.3}


# --- Sprite Settings (used by Character class) ---
SPRITE_FRAME_WIDTH = 64  
SPRITE_FRAME_HEIGHT = 64 
SPRITE_WALK_ANIM_FRAMES = 4 
SPRITE_IDLE_ANIM_FRAMES = 1 
DEFAULT_ANIMATION_SPEED = 0.15  

SLEEP_SPRITESHEET_MALE_FILENAME = "malewhitesleep.png"
SLEEP_SPRITESHEET_FEMALE_FILENAME = "femalewhitesleep.png"
SLEEP_SPRITE_FRAME_WIDTH = 64  
SLEEP_SPRITE_FRAME_HEIGHT = 64 
NUM_SLEEP_ANIM_FRAMES = 2 
ANIM_ROW_SLEEP_SIDE_RIGHT = 0 
ANIM_ROW_SLEEP_ON_BACK = 1    
ANIM_ROW_SLEEP_SIDE_LEFT = 2  

ANIM_ROW_WALK_UP = 8
ANIM_ROW_WALK_LEFT = 9
ANIM_ROW_WALK_DOWN = 10
ANIM_ROW_WALK_RIGHT = 11
ANIM_ROW_IDLE_UP = 22 # Sembra che queste non siano usate nel codice Character attuale, ma le lascio se servono
ANIM_ROW_IDLE_LEFT = 23
ANIM_ROW_IDLE_DOWN = 24
ANIM_ROW_IDLE_RIGHT = 25

BUNDLE_FRAME_WIDTH = 64 
BUNDLE_FRAME_HEIGHT = 64 
BUNDLE_ANIM_ROW = 4
BUNDLE_ANIM_FRAMES = 3

# --- Save/Load System ---
SAVE_GAME_DIR = "saves" # Directory per i file di salvataggio (o SAVE_GAME_DIR se preferisci)
DEFAULT_SAVE_FILENAME = "anthalys_save.json"
AUTO_SAVE_INTERVAL_SECONDS = 300  # Intervallo per l'auto-salvataggio in secondi (es. 5 minuti). Metti 0 per disabilitare.
