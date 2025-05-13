# simai/game/config.py
# Last Updated: 2025-05-12 (English translation, consolidation for review)

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
# Set to True to initialize NPCs with needs that trigger specific behaviors for testing
# Set to False for standard random initialization of needs
DEBUG_MODE_ACTIVE = True # <--- IMPOSTA A True PER TESTARE, False PER GIOCO NORMALE

# (Opzionale) Valori specifici per il debug mode, se DEBUG_MODE_ACTIVE è True
DEBUG_ENERGY_INITIAL_MIN_PCT = 0.05 # For example, very low energy
DEBUG_ENERGY_INITIAL_MAX_PCT = 0.15
DEBUG_HUNGER_INITIAL_MIN_PCT = 0.70 # For example, very high hunger (remember high is bad for hunger)
DEBUG_HUNGER_INITIAL_MAX_PCT = 0.85 


# --- Screen and General Settings ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
PANEL_UI_HEIGHT = 150

# --- Grid and Tiles ---
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# --- Time System ---
GAME_HOURS_IN_DAY = 28
INITIAL_START_HOUR = 7.0 
DAYS_PER_MONTH = 24    
MONTHS_PER_YEAR = 18   
GAME_DAYS_PER_YEAR = DAYS_PER_MONTH * MONTHS_PER_YEAR
TIME_SPEED_SETTINGS = { # SECONDS_PER_GAME_HOUR for each level
    0: float('inf'), 1: 240.0, 2: 120.0, 3: 60.0, 4: 30.0, 5: 15.0
}

# --- Colors ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
NEED_COLOR_VERY_BAD = (255, 0, 0)     # Rosso Scuro
NEED_COLOR_BAD = (255, 120, 0)    # Arancione
NEED_COLOR_MEDIUM = (255, 255, 0)   # Giallo
NEED_COLOR_OKAY = (120, 255, 0)   # Verde Chiaro
NEED_COLOR_GOOD = (0, 200, 0)     # Verde

TEXT_COLOR_LIGHT = (220, 220, 220)
TEXT_COLOR_DARK = (30, 30, 50)
DEBUG_GRID_COLOR = (50, 50, 50)
DEBUG_OBSTACLE_COLOR = (100, 0, 0)

# NPC Specific Colors
NPC_ALPHA_COLOR_MALE = (100, 149, 237)  # Cornflower Blue
NPC_BETA_COLOR_FEMALE = (255, 105, 180) # Hot Pink

# Sky Colors and Keyframes
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

SKY_KEYFRAMES = [ # List of tuples (hour, color_tuple)
    (0, DEEP_NIGHT_COLOR), (4, PRE_DAWN_COLOR), (6, VIVID_DAWN_COLOR),
    (8, EARLY_MORNING_COLOR), (11, FULL_MORNING_COLOR), (14, BRIGHT_DAY_COLOR),
    (17, WARM_AFTERNOON_COLOR), (19, EARLY_SUNSET_COLOR), (21, VIVID_SUNSET_COLOR),
    (23, RED_SUNSET_COLOR), (25, TWILIGHT_COLOR), (28, DEEP_NIGHT_COLOR) 
]

# --- Asset Paths ---
# Get the directory where this config.py file is located (should be 'simai/game/')
GAME_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

BASE_ASSET_PATH = os.path.join(GAME_DIR_PATH, "assets") 
IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "images")
ICON_PATH = os.path.join(IMAGE_PATH, "icons") 
FURNITURE_IMAGE_PATH = os.path.join(IMAGE_PATH, "furnitures") # NUOVA o MODIFICATA
CHARACTER_SPRITE_PATH = os.path.join(IMAGE_PATH, "characters")

# --- Interactive Objects: Base Properties ---
# Bed
BED_SPRITESHEET_BASE_RECT = (0, 0, 64, 80) # (x_orig, y_orig, larghezza, altezza) - Esempio!
BED_SPRITESHEET_COVER_RECT = (0, 80, 64, 48) # Esempio!
DESIRED_BED_WIDTH = 64
DESIRED_BED_HEIGHT = 128
BED_COLOR_FALLBACK = (100,70,30) # Used if bed image fails to load
#DESIRED_BED_Y = SCREEN_HEIGHT - 128 - 10
DESIRED_BED_X = SCREEN_WIDTH - DESIRED_BED_WIDTH - 10 
DESIRED_BED_Y = SCREEN_HEIGHT - PANEL_UI_HEIGHT - DESIRED_BED_HEIGHT - 10
BED_SPRITESHEET_BASE_RECT_COORDS = (0, 0, 64, 81)  # Parte: letto senza NPC sotto le coperte
BED_SPRITESHEET_COVER_RECT_COORDS = (0, 106, 64, 22) # Parte: solo la coperta
BED_COVER_Y_OFFSET_ON_SPRITESHEET = 106 # Y di inizio della coperta sullo spritesheet
BED_COVER_HEIGHT_ON_SPRITESHEET = 22    # Altezza della coperta sullo spritesheet
NPC_IN_BED_OFFSET_X = 10 # Esempio: X pixel dal bordo sinistro del letto
NPC_IN_BED_OFFSET_Y = 20 # Esempio: Y pixel dal bordo superiore del letto (per la testa)

# Offset per disegnare la COPERTA sopra l'NPC, relativo a BED_RECT.topleft.
# Se la tua "base" del letto è alta 81px e la coperta nello spritesheet inizia
# a Y=106, significa che c'è uno spazio.
# La tua indicazione "coprirlo da 1,26" potrebbe significare che la coperta
# deve essere disegnata a BED_RECT.top + 26 (o una Y simile)
# oppure che lo sprite dell'NPC deve essere visibile fino a Y=26 della sua altezza.
# Per ora, calcoleremo la posizione della coperta in modo che si sovrapponga
# correttamente alla base, come se fosse naturalmente parte del letto.
# L'offset Y della coperta rispetto all'inizio del BED_RECT sarà BED_SPRITESHEET_BASE_RECT_COORDS[3] - ALTEZZA_CUSCINI_O_SIMILE
# Questo è il punto più complesso da generalizzare senza vedere l'asset NPC a letto.
# Semplifichiamo: assumiamo che la coperta si disegni a partire da una certa Y della base.
# Se la base è alta 81, e la coperta inizia a Y_spritesheet=106, non è direttamente sovrapponibile.
# Dobbiamo pensare a come "assemblare" il letto.

# Più semplice: disegniamo la base. Poi l'NPC. Poi la coperta.
# La coperta (alta 22px) andrà a coprire una porzione dell'NPC e della base.
# La sua Y di disegno sarà BED_RECT.top + (altezza_base - altezza_parte_visibile_base_sotto_coperta).
# O, se la tua immagine "base" è il letto vuoto, e la "coperta" è *solo* la coperta:
BED_COVER_DRAW_OFFSET_Y = 26 # Proviamo questo basato sulla tua indicazione "coprirlo da 1,26"
                             # Questo sarà BED_RECT.top + BED_COVER_DRAW_OFFSET_Y

# Toilet
TOILET_RECT_PARAMS = {"x": 800, "y": 100, "w": TILE_SIZE * 1, "h": TILE_SIZE * 2} # Esempio di posizione
TOILET_COLOR = (210, 210, 225) 

# Food
FOOD_POS = (100, 100) 
FOOD_RADIUS = min(10, TILE_SIZE // 2 - 2)
FOOD_COLOR = GREEN # Fallback color for food
FOOD_VALUE = 30
FOOD_RESPAWN_TIME = 20.0 

# --- Action Values & Durations ---
SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE = 40.0 
ENERGY_RECOVERY_RATE_PER_HOUR = 15.0
BLADDER_RELIEF_AMOUNT = 85      
TOILET_USE_DURATION_HOURS = 0.20 
FUN_GAINED_AMOUNT = 40 # Placeholder for when fun objects are added
HYGIENE_GAINED_AMOUNT = 70 # Placeholder for when hygiene objects are added

# Intimacy / Romantic Interaction Constants
ROMANTIC_INTERACTION_CHANCE = 0.60       
INTIMACY_SATISFACTION_ROMANTIC = 60    
INTIMACY_SATISFACTION_AFFECTIONATE = 15  
SOCIAL_SATISFACTION_AFFECTIONATE = 10  
INTIMACY_INTERACTION_DURATION_HOURS = 1.0 
HEART_COLOR_ROMANTIC = RED                
HEART_COLOR_AFFECTIONATE = (255,105,180)  # Pink
PREGNANCY_CHANCE_FEMALE = 0.25
PREGNANCY_TERM_GAME_DAYS = DAYS_PER_MONTH # Example: one game month (24 days)

# --- Need Bar Gradient Colors ---
GRADIENT_COLOR_BAD = (200, 0, 0)    # Red (Negative state for need)
GRADIENT_COLOR_GOOD = (0, 200, 0)   # Green (Positive state for need)
NEED_BAR_BG_COLOR = (50, 50, 50)    # Background color for the full bar
NEED_BAR_BORDER_COLOR = (150, 150, 150) # Border color for the bar

# --- UI Constants ---
UI_FONT_SIZE = 26 
ICON_FONT_SIZE = 22 # For potential future use with unicode icons if needed
# Standard icon sizes defined in main.py/load_all_assets for now

# --- NPC AI Constants ---
NPC_SPEED = 80
NPC_MOVEMENT_SPEED_MULTIPLIERS = {
    0: 0.0,  # Fermo (anche se can_move_now dovrebbe già bloccare)
    1: 0.75, # Più lento della velocità base a velocità di gioco 1
    2: 1.0,  # Velocità base a velocità di gioco 2
    3: 1.5,  # Più veloce a velocità di gioco 3
    4: 2.0,  # Molto veloce
    5: 2.5   # Super veloce
}
NPC_HUNGER_THRESHOLD = 70
NPC_ENERGY_THRESHOLD = 30
NPC_SOCIAL_THRESHOLD = 40
NPC_BLADDER_THRESHOLD = 75 
NPC_FUN_THRESHOLD = 30     
NPC_HYGIENE_THRESHOLD = 25 
NPC_INTIMACY_THRESHOLD = 75 

NPC_EAT_REACH_DISTANCE = 15 
NPC_BED_REACH_DISTANCE = 100 # Adjusted to be relative to tile size
NPC_PARTNER_INTERACTION_DISTANCE = TILE_SIZE * 1.5 # Approx. 1.5 tiles
NPC_TOILET_REACH_DISTANCE = TILE_SIZE * 1.0 # Example, adjust as needed
NPC_FUN_OBJECT_REACH_DISTANCE = TILE_SIZE * 1.0 # Placeholder
NPC_SHOWER_REACH_DISTANCE = TILE_SIZE * 1.0  # Placeholder

NPC_IDLE_WANDER_CHANCE = 0.02
NPC_WANDER_MIN_DIST_TILES = 3
NPC_WANDER_MAX_DIST_TILES = 8

# Placeholder for positions of new objects (to be defined as Rects in main.py using params from here)
# FUN_OBJECT_RECT_PARAMS = {"x": ..., "y": ..., "w": ..., "h": ...}
# SHOWER_RECT_PARAMS = {"x": ..., "y": ..., "w": ..., "h": ...}

# --- Need System Base Rates & Initial Values ---
# Values for Character class to instantiate Need objects
# Format: NEEDNAME_CATEGORY = value
# Base rate is always positive, direction (increase/decrease) handled by Need's high_is_good flag.

DEFAULT_MAX_NEED_VALUE = 100.0

# Hunger (0=not hungry, 100=starving)
HUNGER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HUNGER_INITIAL_MIN_PCT = 0.0  # 0% hungry
HUNGER_INITIAL_MAX_PCT = 0.6  # up to 60% hungry
HUNGER_BASE_RATE = 2.0        # Points of hunger increase per game hour
HUNGER_HIGH_IS_GOOD = False   # High hunger value is bad
HUNGER_RATE_MULTIPLIERS = {"Notte": 0.5, "Mattino": 1.2, "Mezzogiorno": 1.5, "Sera": 1.3}

# Energy (0=exhausted, 100=full)
ENERGY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
ENERGY_INITIAL_MIN_PCT = 0.4 # 40% energy
ENERGY_INITIAL_MAX_PCT = 1.0 # up to 100% energy
ENERGY_BASE_DECAY_RATE = 5.5 # Points energy lost per game hour
ENERGY_HIGH_IS_GOOD = True
ENERGY_DECAY_MULTIPLIERS = {"Notte": 0.3, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 0.8}

# Social (0=lonely, 100=fulfilled)
SOCIAL_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
SOCIAL_INITIAL_MIN_PCT = 0.4
SOCIAL_INITIAL_MAX_PCT = 1.0
SOCIAL_BASE_DECAY_RATE = 1.4
SOCIAL_HIGH_IS_GOOD = True
SOCIAL_DECAY_MULTIPLIERS = {"Notte": 0.7, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.5}

# Bladder (0=empty, 100=full/urgent)
BLADDER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
BLADDER_INITIAL_MIN_PCT = 0.0
BLADDER_INITIAL_MAX_PCT = 0.65
BLADDER_BASE_FILL_RATE = 3.0 
BLADDER_HIGH_IS_GOOD = False
BLADDER_FILL_MULTIPLIERS = {"Notte": 0.4, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.0}

# Fun (0=bored, 100=entertained)
FUN_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
FUN_INITIAL_MIN_PCT = 0.3
FUN_INITIAL_MAX_PCT = 1.0
FUN_BASE_DECAY_RATE = 2.5
FUN_HIGH_IS_GOOD = True
FUN_DECAY_MULTIPLIERS = {"Notte": 0.6, "Mattino": 1.0, "Mezzogiorno": 1.3, "Sera": 1.1}

# Hygiene (0=dirty, 100=clean)
HYGIENE_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HYGIENE_INITIAL_MIN_PCT = 0.5
HYGIENE_INITIAL_MAX_PCT = 1.0
HYGIENE_BASE_DECAY_RATE = 1.8
HYGIENE_HIGH_IS_GOOD = True
HYGIENE_DECAY_MULTIPLIERS = {"Notte": 0.5, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.0}

# Intimacy (Drive: 0=low, 100=high/urgent)
INTIMACY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE 
INTIMACY_INITIAL_MIN_PCT = 0.0
INTIMACY_INITIAL_MAX_PCT = 0.3
INTIMACY_BASE_INCREASE_RATE = 0.8 
INTIMACY_HIGH_IS_GOOD = False 
INTIMACY_INCREASE_RATE_MULTIPLIERS = {"Notte": 1.0, "Mattino": 1.0, "Mezzogiorno": 1.1, "Sera": 1.3} # Example

# --- Sprite Settings (used by Character class) ---
SPRITE_FRAME_WIDTH = 64  
SPRITE_FRAME_HEIGHT = 64 
SPRITE_WALK_ANIM_FRAMES = 4 
SPRITE_IDLE_ANIM_FRAMES = 1 
DEFAULT_ANIMATION_SPEED = 0.15  

# NUOVO: Nomi file e parametri per Sprite Sonno
SLEEP_SPRITESHEET_MALE_FILENAME = "malewhitesleep.png"
SLEEP_SPRITESHEET_FEMALE_FILENAME = "femalewhitesleep.png"
SLEEP_SPRITE_FRAME_WIDTH = 64  # Confermato da te
SLEEP_SPRITE_FRAME_HEIGHT = 64 # Confermato da te
# Numero di frame per ogni animazione di sonno (da verificare sui tuoi file, assumo 2 o 4 per un leggero movimento)
NUM_SLEEP_ANIM_FRAMES = 2 # ESEMPIO: DA VERIFICARE E MODIFICARE!
ANIM_ROW_SLEEP_SIDE_RIGHT = 0 # Prima riga nello spritesheet del sonno
ANIM_ROW_SLEEP_ON_BACK = 1    # Seconda riga
ANIM_ROW_SLEEP_SIDE_LEFT = 2  # Terza riga~```````````````````````````````````

# Spritesheet Row Indices (0-indexed) - from user's input
ANIM_ROW_WALK_UP = 8
ANIM_ROW_WALK_LEFT = 9
ANIM_ROW_WALK_DOWN = 10
ANIM_ROW_WALK_RIGHT = 11
ANIM_ROW_IDLE_UP = 22
ANIM_ROW_IDLE_LEFT = 23
ANIM_ROW_IDLE_DOWN = 24
ANIM_ROW_IDLE_RIGHT = 25

# For bundles.png (newborns)
BUNDLE_FRAME_WIDTH = 64 
BUNDLE_FRAME_HEIGHT = 64 
BUNDLE_ANIM_ROW = 4
BUNDLE_ANIM_FRAMES = 3