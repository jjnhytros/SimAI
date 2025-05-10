# simai/game/config.py
import os
import datetime

# --- Nome Gioco e Versioning ---
GAME_NAME = "SimAI"
CORE_VERSION = "0.3.0" # La versione MAJOR.MINOR.PATCH visibile

# Metadati di build per tracciamento interno (timestamp attuale)
# Il timestamp viene generato quando il gioco parte (o meglio, quando config.py viene caricato)
# Esempio: 20250510002347 (per il 10 Maggio 2025, 00:23:47)
BUILD_METADATA = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 

# Versione completa per uso interno (es. logging, schermata "About" futura)
FULL_VERSION_INTERNAL = f"{CORE_VERSION}+{BUILD_METADATA}" 

# Titolo della finestra userà solo la CORE_VERSION per un aspetto più pulito
WINDOW_TITLE = f"{GAME_NAME} v{CORE_VERSION}" 
# Risulterà in qualcosa tipo: "SimAI v0.3.0"

# --- Impostazioni Generali ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# --- IMPOSTAZIONI GENERALI BISOGNI ---
DEFAULT_MAX_NEED_VALUE = 100.0

# --- FAME (0=non affamato, 100=affamatissimo) ---
HUNGER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HUNGER_INITIAL_MIN_PCT = 0.0  # 0% affamato
HUNGER_INITIAL_MAX_PCT = 0.6  # 60% affamato
HUNGER_BASE_RATE = 2.0  # Punti di fame che aumentano all'ora
HUNGER_HIGH_IS_GOOD = False # Un valore alto di fame è male
HUNGER_RATE_MULTIPLIERS = {"Notte": 0.5, "Mattino": 1.2, "Mezzogiorno": 1.5, "Sera": 1.3}

# --- ENERGIA (0=scarico, 100=pieno) ---
ENERGY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
ENERGY_INITIAL_MIN_PCT = 0.4 # 40% energia
ENERGY_INITIAL_MAX_PCT = 1.0 # 100% energia
ENERGY_BASE_DECAY_RATE = 5.5 # Punti energia persi all'ora
ENERGY_HIGH_IS_GOOD = True
ENERGY_DECAY_MULTIPLIERS = {"Notte": 0.3, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 0.8}
ENERGY_RECOVERY_RATE_PER_HOUR = 15.0

# --- SOCIALITÀ (0=solo, 100=appagato) ---
SOCIAL_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
SOCIAL_INITIAL_MIN_PCT = 0.4
SOCIAL_INITIAL_MAX_PCT = 1.0
SOCIAL_BASE_DECAY_RATE = 1.4
SOCIAL_HIGH_IS_GOOD = True
SOCIAL_DECAY_MULTIPLIERS = {"Notte": 0.7, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.5}
SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE = 30.0

# --- VESCICA (0=vuota, 100=piena/male) ---
BLADDER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
BLADDER_INITIAL_MIN_PCT = 0.0
BLADDER_INITIAL_MAX_PCT = 0.65
BLADDER_BASE_FILL_RATE = 3.0 # Punti con cui si riempie all'ora
BLADDER_HIGH_IS_GOOD = False
BLADDER_FILL_MULTIPLIERS = {"Notte": 0.4, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.0}

# --- DIVERTIMENTO (0=annoiato, 100=divertito) ---
FUN_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
FUN_INITIAL_MIN_PCT = 0.3
FUN_INITIAL_MAX_PCT = 1.0
FUN_BASE_DECAY_RATE = 2.5
FUN_HIGH_IS_GOOD = True
FUN_DECAY_MULTIPLIERS = {"Notte": 0.6, "Mattino": 1.0, "Mezzogiorno": 1.3, "Sera": 1.1}

# --- IGIENE (0=sporco, 100=pulito) ---
HYGIENE_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HYGIENE_INITIAL_MIN_PCT = 0.5
HYGIENE_INITIAL_MAX_PCT = 1.0
HYGIENE_BASE_DECAY_RATE = 1.8
HYGIENE_HIGH_IS_GOOD = True
HYGIENE_DECAY_MULTIPLIERS = {"Notte": 0.5, "Mattino": 1.0, "Mezzogiorno": 1.2, "Sera": 1.0}

# --- INTIMITÀ (Pulsione: 0=bassa, 100=alta/bisogno urgente) ---
INTIMACY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE # Max pulsione
INTIMACY_INITIAL_MIN_PCT = 0.0
INTIMACY_INITIAL_MAX_PCT = 0.3
INTIMACY_BASE_INCREASE_RATE = 0.8 # Tasso a cui la pulsione AUMENTA
INTIMACY_HIGH_IS_GOOD = False # Una pulsione alta è uno "stato negativo" da risolvere
INTIMACY_INCREASE_RATE_MULTIPLIERS = {"Notte": 1.0, "Mattino": 1.0, "Mezzogiorno": 1.0, "Sera": 1.2} # Esempio

# --- Oggetti Interattivi, Sistema di Tempo, Costanti AI NPC 
NPC_SPEED = 80
NPC_HUNGER_THRESHOLD = 70
NPC_ENERGY_THRESHOLD = 30
NPC_SOCIAL_THRESHOLD = 40
NPC_BLADDER_THRESHOLD = 75 
NPC_FUN_THRESHOLD = 30     
NPC_HYGIENE_THRESHOLD = 25 
NPC_INTIMACY_THRESHOLD = 10
NPC_EAT_REACH_DISTANCE = 15 
NPC_BED_REACH_DISTANCE = 25
NPC_TOILET_REACH_DISTANCE = 15
NPC_FUN_OBJECT_REACH_DISTANCE = 15
NPC_SHOWER_REACH_DISTANCE = 15
INTIMACY_SATISFACTION_ON_MEET = 0
NPC_PARTNER_INTERACTION_DISTANCE = 40
INTIMACY_INTERACTION_DURATION_HOURS = 1.0
NPC_IDLE_WANDER_CHANCE = 0.02  # Es: 2% di probabilità per tick AI di iniziare a gironzolare se idle
NPC_WANDER_MIN_DIST_TILES = 3  # Distanza minima di gironzolamento in numero di tile
NPC_WANDER_MAX_DIST_TILES = 8  # Distanza massima di gironzolamento in numero di tile


FIKI_FIKI_CHANCE = 0.99 # NUOVO: 60% di probabilità che avvenga Fiki Fiki
INTIMACY_SATISFACTION_FIKI_FIKI = 60 # NUOVO: Soddisfazione se Fiki Fiki avviene
INTIMACY_SATISFACTION_FLIRT = 15   # NUOVO: Soddisfazione se avviene solo un flirt/nulla
SOCIAL_SATISFACTION_FLIRT = 10     # NUOVO: Piccolo bonus sociale per un flirt


# --- FOOD_VALUE, ENERGY_RECOVERY_RATE_PER_HOUR, SOCIAL_RECOVERY_RATE_PER_HOUR_PHONE, ecc.)
BLADDER_RELIEF_AMOUNT = 85      # Quanto si svuota la vescica per uso
TOILET_USE_DURATION_HOURS = 0.20 # Durata dell'uso del WC in ore di gioco (es. 12 min di gioco)
FUN_GAINED_AMOUNT = 40
HYGIENE_GAINED_AMOUNT = 70

# --- Sistema di Tempo ---
GAME_HOURS_IN_DAY = 28
INITIAL_START_HOUR = 7.0 # <--- ASSICURATI CHE QUESTA RIGA SIA PRESENTE E NON COMMENTATA
DAYS_PER_MONTH = 24    
MONTHS_PER_YEAR = 18   
GAME_DAYS_PER_YEAR = DAYS_PER_MONTH * MONTHS_PER_YEAR 

TIME_SPEED_SETTINGS = { 
    0: float('inf'), 1: 240.0, 2: 120.0, 3: 60.0, 4: 30.0, 5: 15.0
}

# --- Griglia e Tiles ---
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE # Ora userà SCREEN_WIDTH definito sopra
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE # Ora userà SCREEN_HEIGHT definito sopra

# --- Colori ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)   # <--- ASSICURATI CHE QUESTA RIGA SIA PRESENTE E NON COMMENTATA
GREEN = (0, 255, 0) 
BLUE = (0, 0, 255)  # Usato per NPC Alpha prima, ora config.NPC_ALPHA_COLOR_MALE
CYAN = (0, 255, 255) # Usato per NPC Beta prima, ora config.NPC_BETA_COLOR_FEMALE
TEXT_COLOR_LIGHT = (220, 220, 220)
TEXT_COLOR_DARK = (30, 30, 50)
DEBUG_GRID_COLOR = (50, 50, 50)
DEBUG_OBSTACLE_COLOR = (100, 0, 0)
# Colori specifici NPC (già presenti dalla modifica precedente)
NPC_ALPHA_COLOR_MALE = (100, 149, 237)
NPC_BETA_COLOR_FEMALE = (255, 105, 180)
HEART_COLOR_FIKI_FIKI = (255, 0, 0) # Rosso per i cuori del Fiki Fiki
HEART_COLOR_FLIRT = (255, 105, 180) # Rosa per i cuori di un flirt

# --- COLORI BARRE BISOGNI GRADIENTE (ASSICURATI SIANO PRESENTI) ---
GRADIENT_COLOR_BAD = (200, 0, 0)    # Rosso (Stato negativo del bisogno)
GRADIENT_COLOR_GOOD = (0, 200, 0)   # Verde (Stato positivo del bisogno)
NEED_BAR_BG_COLOR = (50, 50, 50)    # Colore di sfondo per la barra piena
NEED_BAR_BORDER_COLOR = (150, 150, 150) # Colore del bordo della barra

# --- COLORI CIELO E KEYFRAMES (ASSICURATI SIANO PRESENTI) ---
COLOR_NOTTE_PROFONDA = (10, 10, 30)
COLOR_PRE_ALBA = (25, 25, 55)
COLOR_ALBA_VIVA = (100, 90, 140)
COLOR_MATTINO_INIZIO = (120, 140, 190)
COLOR_MATTINO_PIENO = (135, 206, 235)
COLOR_GIORNO_LUMINOSO = (170, 225, 255)
COLOR_POMERIGGIO_CALDO = (220, 200, 160)
COLOR_TRAMONTO_INIZIO = (255, 180, 100)
COLOR_TRAMONTO_VIVO = (255, 130, 70)
COLOR_TRAMONTO_ROSSO = (200, 80, 60)
COLOR_CREPUSCOLO = (70, 60, 90)
SKY_KEYFRAMES = [ # Lista di tuple (ora, colore_tuple)
    (0, COLOR_NOTTE_PROFONDA), 
    (4, COLOR_PRE_ALBA),
    (6, COLOR_ALBA_VIVA),
    (8, COLOR_MATTINO_INIZIO), 
    (11, COLOR_MATTINO_PIENO), 
    (14, COLOR_GIORNO_LUMINOSO),
    (17, COLOR_POMERIGGIO_CALDO), 
    (19, COLOR_TRAMONTO_INIZIO), 
    (21, COLOR_TRAMONTO_VIVO),
    (23, COLOR_TRAMONTO_ROSSO), 
    (25, COLOR_CREPUSCOLO), 
    (28, COLOR_NOTTE_PROFONDA) # Deve corrispondere all'ora 0 per un ciclo corretto
]

# --- PERCORSI ASSETS ---
GAME_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

BASE_ASSET_PATH = os.path.join(GAME_DIR_PATH, "assets") # Ora è /.../simai/game/assets
IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "images")
ICON_PATH = os.path.join(IMAGE_PATH, "icons") 
OBJECT_IMAGE_PATH = os.path.join(IMAGE_PATH, "objects")
CHARACTER_SPRITE_PATH = os.path.join(IMAGE_PATH, "characters") 

# --- Oggetti Interattivi: Proprietà Base ---
DESIRED_BED_X = SCREEN_WIDTH - 197 - 10 # Esempio di posizionamento basato sulla nuova larghezza
DESIRED_BED_Y = SCREEN_HEIGHT - 263 - 10 # Esempio di posizionamento basato sulla nuova altezza
DESIRED_BED_WIDTH = 197
DESIRED_BED_HEIGHT = 263
FOOD_POS = (100, 100) 
FOOD_RADIUS = min(10, TILE_SIZE // 2 - 2) if TILE_SIZE else 10
FOOD_COLOR = GREEN # Assicurati che GREEN sia definito
FOOD_VALUE = 30
FOOD_RESPAWN_TIME = 20.0 

# WC (Toilet)
TOILET_POS_X = SCREEN_WIDTH - 60  # Esempio: in alto a destra
TOILET_POS_Y = 60                 # Esempio: (le coordinate sono per il centro del Rect)
TOILET_SIZE_W = TILE_SIZE * 1     # Esempio: 1 tile di larghezza
TOILET_SIZE_H = TILE_SIZE * 2     # Esempio: 2 tile di altezza
TOILET_COLOR = (210, 210, 225)    # Esempio: un colore grigio-bianco per il WC

# Definizioni per futuri oggetti Divertimento e Igiene (puoi lasciarli come None per ora)
FUN_OBJECT_POS_OR_RECT = None # Esempio: config.FUN_OBJECT_RECT
SHOWER_POS_OR_RECT = None     # Esempio: config.SHOWER_RECT

# --- IMPOSTAZIONI SPRITE PERSONAGGI ---
# DOVRAI AGGIORNARE QUESTI VALORI CON QUELLI CORRETTI PER I TUOI SPRITESHEET!
SPRITE_FRAME_WIDTH = 64  # Esempio: larghezza di un singolo frame del personaggio
SPRITE_FRAME_HEIGHT = 64 # Esempio: altezza di un singolo frame del personaggio
SPRITE_WALK_ANIM_FRAMES = 9 # Esempio: numero di frame per le animazioni di camminata
SPRITE_IDLE_ANIM_FRAMES = 2 # Esempio: numero di frame per le animazioni idle (se >1, l'idle sarà animato)
DEFAULT_ANIMATION_SPEED = 0.15  # Secondi per frame dell'animazione

# Righe spritesheet (0-indexed) - Basate sulle tue indicazioni
ANIM_ROW_WALK_UP = 8
ANIM_ROW_WALK_LEFT = 9
ANIM_ROW_WALK_DOWN = 10
ANIM_ROW_WALK_RIGHT = 11
ANIM_ROW_IDLE_UP = 22
ANIM_ROW_IDLE_LEFT = 23
ANIM_ROW_IDLE_DOWN = 24
ANIM_ROW_IDLE_RIGHT = 25

# Per bundles.png
BUNDLE_FRAME_WIDTH = 32 # Esempio, da verificare!
BUNDLE_FRAME_HEIGHT = 32 # Esempio, da verificare!
BUNDLE_ANIM_ROW = 4
BUNDLE_ANIM_FRAMES = 3
