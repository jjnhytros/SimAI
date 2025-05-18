# simai/game/config.py
import pygame
import os
import datetime

# --- I. Informazioni Generali del Gioco ---
GAME_NAME = "SimAI"
CORE_VERSION = "0.3.0"  # Aggiorna questa versione man mano
BUILD_METADATA = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
FULL_VERSION_INTERNAL = f"{CORE_VERSION}+{BUILD_METADATA}"
WINDOW_TITLE = f"{GAME_NAME} v{CORE_VERSION} - Anthalys"

# --- II. Impostazioni di Debug ---
DEBUG_MODE_ACTIVE = True      # Flag generale per logiche di debug (es. randomizzazione bisogni)
DEBUG_AI_ACTIVE = True        # Flag per stampe di debug verbose (IA, Pathfinding, Componenti, ecc.)

# Valori specifici se DEBUG_MODE_ACTIVE = True (per testare stati specifici dei bisogni)
DEBUG_ENERGY_INITIAL_MIN_PCT = 0.05 # 5%
DEBUG_ENERGY_INITIAL_MAX_PCT = 0.15 # 15%
DEBUG_HUNGER_INITIAL_MIN_PCT = 0.70 # 70% (alto è male per la fame)
DEBUG_HUNGER_INITIAL_MAX_PCT = 0.85 # 85%

# --- III. Impostazioni Percorsi File (Paths) ---
GAME_DIR_PATH = os.path.dirname(os.path.abspath(__file__)) # Directory del gioco (dove si trova questo file)
ASSETS_PATH = os.path.join(GAME_DIR_PATH, "assets")
IMAGE_PATH = os.path.join(ASSETS_PATH, "images")
CHARACTER_SPRITE_PATH = os.path.join(IMAGE_PATH, "characters")
FURNITURE_IMAGE_PATH = os.path.join(IMAGE_PATH, "furnitures")
UI_ICON_PATH = os.path.join(IMAGE_PATH, "ui_icons") # Potresti voler separare le icone UI
TILE_IMAGE_PATH = os.path.join(IMAGE_PATH, "tiles") # Per le tile della mappa
FONT_ASSETS_PATH = os.path.join(ASSETS_PATH, "fonts") # Rinominato per chiarezza
DATA_PATH = os.path.join(ASSETS_PATH, "data")
SAVE_GAME_DIR = "saves" # Relativo alla directory da cui esegui il gioco, o usa os.path.join(GAME_DIR_PATH, "saves")

# --- IV. Impostazioni Schermo e Grafica Base ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 30 # Abbassato leggermente per potenziale risparmio CPU, 60 è ok se le performance lo permettono
TILE_SIZE = 32

# Font di default (specifica il percorso o None per il font di sistema)
FONT_NAME = None # Esempio: os.path.join(FONT_ASSETS_PATH, "YourPixelFont.ttf")
UI_FONT_SIZE = 18 # Dimensione per la maggior parte del testo UI
DEBUG_FONT_SIZE = 15

# Font per Icone Unicode (se usato)
UI_UNICODE_ICON_FONT_PATH = os.path.join(FONT_ASSETS_PATH, "EasyReading.ttf")
UI_UNICODE_ICON_FONT_SIZE = 22 # Aggiusta per la resa desiderata
UI_UNICODE_ICON_COLOR = (50, 50, 50) # Colore per le icone renderizzate da font

# --- V. Mondo di Gioco ---
WORLD_TILE_WIDTH = 32   # Larghezza del mondo in numero di tile (es. piccola mappa di test 32x24)
WORLD_TILE_HEIGHT = 24  # Altezza del mondo in numero di tile
GRID_WIDTH = WORLD_TILE_WIDTH  # La griglia di pathfinding copre l'intero mondo
GRID_HEIGHT = WORLD_TILE_HEIGHT

# Dati mappa temporanei (esempio, dovrai popolarli)
TEMP_WORLD_MAP_DATA = [[1 for _ in range(WORLD_TILE_WIDTH)] for _ in range(WORLD_TILE_HEIGHT)]
# Esempio per rendere alcune aree camminabili (0) e altre no (1)
if WORLD_TILE_WIDTH > 5 and WORLD_TILE_HEIGHT > 5:
    for r in range(1, WORLD_TILE_HEIGHT - 1):
        for c in range(1, WORLD_TILE_WIDTH - 1):
            TEMP_WORLD_MAP_DATA[r][c] = 0 # Camminabile
# Definisci TILE_IMAGE_MAPPING se usi tile grafiche
# TILE_IMAGE_MAPPING = {
#     0: "grass_tile.png",  # Esempio: ID 0 -> file erba.png (da mettere in TILE_IMAGE_PATH)
#     1: "wall_tile.png",   # Esempio: ID 1 -> file muro.png
#     # Aggiungi altre mappature ID tile -> nome file immagine
# }


# --- VI. Sistema di Tempo ---
GAME_HOURS_IN_DAY = 28 # Come da tue specifiche
INITIAL_START_HOUR = 7.0
INITIAL_START_DAY = 1
INITIAL_START_MONTH = 1
INITIAL_START_YEAR = 1
DAYS_PER_MONTH = 24
MONTHS_PER_YEAR = 18
GAME_DAYS_PER_YEAR = DAYS_PER_MONTH * MONTHS_PER_YEAR

# TIME_SPEED_SETTINGS: chiave = indice velocità, valore = secondi REALI per far passare UN'ORA di GIOCO
TIME_SPEED_SETTINGS = {
    0: float('inf'),  # Pausa
    1: 240.0,         # 15x (3600/240) -> 4 minuti reali per un giorno di gioco
    2: 120.0,         # 30x
    3: 60.0,          # 60x (1 ora di gioco in 1 minuto reale)
    4: 30.0,          # 120x
    5: 15.0           # 240x (1 ora di gioco in 15 secondi reali) -> circa 7 min per un giorno
}
TIME_SPEED_NORMAL_INDEX = 2 # Indice di velocità di default (es. 30x)
TIME_SPEED_SLEEP_ACCELERATED_INDEX = 5 # Indice della velocità massima quando tutti dormono

# PERIOD_DEFINITIONS: (ora_inizio_float, nome_periodo_str, chiave_config_icona_char_unicode_str)
DEFAULT_PERIOD_ICON_CHAR_KEY = "ICON_CHAR_SUN" # Fallback se l'icona specifica non è trovata
PERIOD_DEFINITIONS = [
    (0.0, "Notte Profonda", "ICON_CHAR_MOON_STARS"),
    (5.0, "Alba", "ICON_CHAR_DAWN"),
    (7.0, "Mattina", "ICON_CHAR_SUNRISE"),
    (12.0, "Mezzogiorno", "ICON_CHAR_SUN_BRIGHT"),
    (14.0, "Pomeriggio", "ICON_CHAR_SUN_CLOUDS"),
    (18.0, "Tramonto", "ICON_CHAR_SUNSET_สวยงาม"), # (Esempio nome chiave)
    (20.0, "Sera", "ICON_CHAR_MOON_SIMPLE"),
    (23.0, "Notte", "ICON_CHAR_MOON_STARS_ALT")
]
# Colori per SKY_KEYFRAMES (definisci i colori qui)
DEEP_NIGHT_COLOR = (10, 10, 30); PRE_DAWN_COLOR = (25, 25, 55); VIVID_DAWN_COLOR = (100, 90, 140);
EARLY_MORNING_COLOR = (120, 140, 190); FULL_MORNING_COLOR = (135, 206, 235); BRIGHT_DAY_COLOR = (170, 225, 255);
WARM_AFTERNOON_COLOR = (220, 200, 160); EARLY_SUNSET_COLOR = (255, 180, 100); VIVID_SUNSET_COLOR = (255, 130, 70);
RED_SUNSET_COLOR = (200, 80, 60); TWILIGHT_COLOR = (70, 60, 90);
SKY_KEYFRAMES = [
    (0, DEEP_NIGHT_COLOR), (4, PRE_DAWN_COLOR), (6, VIVID_DAWN_COLOR), (8, EARLY_MORNING_COLOR),
    (11, FULL_MORNING_COLOR), (14, BRIGHT_DAY_COLOR), (17, WARM_AFTERNOON_COLOR), (19, EARLY_SUNSET_COLOR),
    (21, VIVID_SUNSET_COLOR), (23, RED_SUNSET_COLOR), (25, TWILIGHT_COLOR), (28, DEEP_NIGHT_COLOR)
]
UI_TEXT_BRIGHTNESS_THRESHOLD = 140 # Per cambiare colore testo UI

# --- VII. Colori Generali ---
WHITE = (255, 255, 255); BLACK = (0, 0, 0); RED = (255, 0, 0); GREEN = (0, 255, 0);
BLUE = (0, 0, 255); YELLOW = (255, 255, 0); ORANGE = (255, 165, 0); CYAN = (0, 255, 255);
MAGENTA = (255, 0, 255); PINK = (255, 192, 203); GREY = (128, 128, 128);
LIGHT_GREY = (200, 200, 200); DARK_GREY = (50, 50, 50);
TEXT_COLOR_LIGHT = WHITE
TEXT_COLOR_DARK = BLACK
DEBUG_GRID_COLOR = (50, 50, 50); DEBUG_OBSTACLE_COLOR = (100, 0, 0);

# --- VIII. Oggetti Interagibili del Mondo ---
# Chiavi per i blueprint degli oggetti principali
MAIN_BED_BLUEPRINT_KEY = "double_bed_blue"
MAIN_TOILET_BLUEPRINT_KEY = "toilet_standard"
# ... altri oggetti principali ...

# Posizioni di default per gli oggetti (se non caricate da salvataggio o definite diversamente)
DESIRED_BED_X = WORLD_TILE_WIDTH * TILE_SIZE // 2  # Esempio: centro del mondo
DESIRED_BED_Y = WORLD_TILE_HEIGHT * TILE_SIZE // 2
TOILET_RECT_PARAMS = {"x": int(WORLD_TILE_WIDTH * TILE_SIZE * 0.7), "y": int(WORLD_TILE_HEIGHT * TILE_SIZE * 0.3), "w": TILE_SIZE, "h": TILE_SIZE * 2}
TOILET_COLOR = (210, 210, 225) # Fallback se non c'è sprite

# Immagini Oggetti (se non usi spritesheet da blueprint per tutto)
BED_IMAGE_BASE_FILENAME = "bed_base.png" # Questi devono esistere in IMAGE_PATH
BED_IMAGE_COVER_FILENAME = "bed_cover.png"
BED_COVER_DRAW_OFFSET_Y = 26

# --- IX. NPC: Inizializzazione e Comportamento ---
INITIAL_NUM_NPCS = 2
NPC_NAME_LIST_MALE = ["Bob", "John", "Mike", "David", "Chris", "Paul", "Mark", "Steve", "James", "Andrew"]
NPC_NAME_LIST_FEMALE = ["Alice", "Eva", "Laura", "Sophia", "Chloe", "Emily", "Olivia", "Emma", "Mia", "Isabella"]
NPC_MALE_SPRITESHEET_KEYS = ["male_char"]
NPC_FEMALE_SPRITESHEET_KEYS = ["female_char"]
NPC_MALE_SLEEP_SPRITESHEET_KEYS = ["male_sleep"]
NPC_FEMALE_SLEEP_SPRITESHEET_KEYS = ["female_sleep"]
DEFAULT_HOUSEHOLD_ID_FOR_NEW_NPCS = "default_household_1" # Per inventario domestico

CHARACTER_SPEED = 80.0 # pixel/secondo
NPC_MOVEMENT_SPEED_MULTIPLIERS = {0: 0.0, 1: 0.75, 2: 1.0, 3: 1.5, 4: 2.0, 5: 2.5}
NPC_TARGET_REACH_THRESHOLD = TILE_SIZE / 2.8 # Distanza per considerare un target raggiunto
NPC_PARTNER_INTERACTION_DISTANCE = TILE_SIZE * 1.8 # Distanza per iniziare interazioni di coppia

# Soglie Bisogni per IA (ora tutte le soglie indicano "quando scende SOTTO questo, agisci")
NPC_HUNGER_THRESHOLD = 30    # Se la sazietà scende sotto 30, cerca cibo
NPC_ENERGY_THRESHOLD = 30    # Se l'energia scende sotto 30, cerca letto
NPC_SOCIAL_THRESHOLD = 40
NPC_BLADDER_THRESHOLD = 25   # Se lo "stato di sollievo" scende sotto 25 (vescica si sta riempiendo), cerca bagno
NPC_FUN_THRESHOLD = 30
NPC_HYGIENE_THRESHOLD = 25
NPC_INTIMACY_THRESHOLD = 35  # Se la soddisfazione da intimità scende sotto 35, cerca interazioni

# Comportamento IA
NPC_IDLE_WANDER_CHANCE = 0.02
NPC_WANDER_MIN_DIST_TILES = 2
NPC_WANDER_MAX_DIST_TILES = 6
ASTAR_MAX_ITERATIONS = 1500 # Aumentato leggermente

# Interazioni e Durate Azioni
PHONING_DURATION_HOURS = 0.25
SOCIAL_RECOVERY_FROM_PHONE = 25.0
TOILET_USE_DURATION_HOURS = 0.15
BLADDER_RELIEF_AMOUNT = 90.0
HYGIENE_CHANGE_FROM_TOILET = 0 # Nessun impatto per ora

# Intimità
IMMEDIATE_INTIMACY_INTERACTION_DURATION_HOURS = 0.1 # Interazione breve
INTIMACY_SATISFACTION_AFFECTIONATE = 15
INTIMACY_SATISFACTION_ROMANTIC = 30 # Più basso dell'andare a letto
SOCIAL_SATISFACTION_AFFECTIONATE = 10
FUN_FROM_AFFECTIONATE_INTERACTION = 2
FUN_FROM_ROMANTIC_INTERACTION = 5
INTIMACY_WAITING_TIMEOUT_HOURS = 0.5 # Timeout per partner che arriva
INTIMACY_BED_WAITING_TIMEOUT_HOURS = 0.3 # Timeout per partner che arriva a letto
CUDDLING_DURATION_HOURS = 1.0
INTIMACY_FROM_CUDDLING = 50
SOCIAL_FROM_CUDDLING = 20
FUN_FROM_CUDDLING = 10
ENERGY_RECOVERY_WHILE_CUDDLING_RATE = 5.0 # Tasso orario, più basso del sonno normale

# --- X. NPC: Componenti (Valori Iniziali, Tassi, Soglie) ---
# X.1 Bisogni (NeedsComponent e classi BaseNeed)
DEFAULT_MAX_NEED_VALUE = 100.0
# Fame: Un valore ALTO significa "sazio", un valore BASSO significa "affamato"
HUNGER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HUNGER_INITIAL_MIN_PCT = 0.3  # Inizia un po' affamato
HUNGER_INITIAL_MAX_PCT = 0.7
HUNGER_BASE_DECAY_RATE = 2.0  # Tasso con cui la sazietà SCENDE (aumenta la fame)
HUNGER_HIGH_IS_GOOD = True   # <<<< MODIFICATO
HUNGER_RATE_MULTIPLIERS = {"Notte Profonda": 0.5, "Alba": 1.0, "Mattina": 1.2, "Mezzogiorno": 1.5, "Pomeriggio": 1.4, "Tramonto": 1.3, "Sera": 1.1, "Notte": 0.8}
DEBUG_HUNGER_INITIAL_MIN_PCT = 0.10 # Per testare la fame critica
DEBUG_HUNGER_INITIAL_MAX_PCT = 0.25

# Energia
ENERGY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
ENERGY_INITIAL_MIN_PCT = 0.4
ENERGY_INITIAL_MAX_PCT = 1.0
ENERGY_BASE_DECAY_RATE = 5.5 # Tasso con cui l'energia SCENDE
ENERGY_HIGH_IS_GOOD = True   # Già True
ENERGY_RECOVERY_RATE_PER_HOUR = 18.0
ENERGY_DECAY_MULTIPLIERS = {"Notte Profonda": 0.3, "Alba": 0.8, "Mattina": 1.0, "Mezzogiorno": 1.2, "Pomeriggio": 1.1, "Tramonto": 0.9, "Sera": 0.7, "Notte": 0.5}
DEBUG_ENERGY_INITIAL_MIN_PCT = 0.05
DEBUG_ENERGY_INITIAL_MAX_PCT = 0.15

# Socialità
SOCIAL_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
SOCIAL_INITIAL_MIN_PCT = 0.3
SOCIAL_INITIAL_MAX_PCT = 0.8
SOCIAL_BASE_DECAY_RATE = 1.4 # Tasso con cui la socialità SCENDE
SOCIAL_HIGH_IS_GOOD = True   # Già True
SOCIAL_DECAY_MULTIPLIERS = {}

# Vescica: Un valore ALTO significa "vescica vuota/soddisfatta", BASSO significa "vescica piena/critica"
BLADDER_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
BLADDER_INITIAL_MIN_PCT = 0.5 # Inizia con la vescica non completamente vuota
BLADDER_INITIAL_MAX_PCT = 0.9
BLADDER_BASE_DECAY_RATE = 3.0 # Tasso con cui lo "stato di sollievo" SCENDE (la vescica si riempie)
BLADDER_HIGH_IS_GOOD = True   # <<<< MODIFICATO
BLADDER_FILL_MULTIPLIERS = {} # Questi erano fill, ora sono decay del "sollievo"
# BLADDER_RELIEF_AMOUNT (definito in Action Values) è quanto si aggiunge quando si usa il bagno

# Divertimento
FUN_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
FUN_INITIAL_MIN_PCT = 0.2
FUN_INITIAL_MAX_PCT = 0.7
FUN_BASE_DECAY_RATE = 2.5
FUN_HIGH_IS_GOOD = True   # Già True
FUN_DECAY_MULTIPLIERS = {}

# Igiene
HYGIENE_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
HYGIENE_INITIAL_MIN_PCT = 0.4
HYGIENE_INITIAL_MAX_PCT = 0.9
HYGIENE_BASE_DECAY_RATE = 1.8
HYGIENE_HIGH_IS_GOOD = True   # Già True
HYGIENE_DECAY_MULTIPLIERS = {}

# Intimità: Un valore ALTO significa "soddisfazione da intimità", BASSO significa "bisogno di intimità"
INTIMACY_MAX_VALUE = DEFAULT_MAX_NEED_VALUE
INTIMACY_INITIAL_MIN_PCT = 0.0
INTIMACY_INITIAL_MAX_PCT = 0.3
INTIMACY_BASE_DECAY_RATE = 0.8 # Tasso con cui la soddisfazione da intimità SCENDE
INTIMACY_HIGH_IS_GOOD = True   # <<<< MODIFICATO
INTIMACY_INCREASE_RATE_MULTIPLIERS = {} # Questi erano increase, ora decay della soddisfazione
# Le costanti _SATISFACTION (es. INTIMACY_FROM_CUDDLING) sono quanto si aggiunge quando si soddisfa il bisogno

# X.2 Finanze (FinanceComponent)
NPC_INITIAL_MONEY_MIN = 500
NPC_INITIAL_MONEY_MAX = 2500
MAX_TRANSACTION_HISTORY = 30

# X.3 Umore (MoodComponent)
EMOTION_LIST = ["Neutro", "Felice", "Contento", "Triste", "Arrabbiato", "Stressato", "Annoiato", "Eccitato", "Ispirato", "Imbarazzato"]
MOOD_VALUE_MIN = -100.0
MOOD_VALUE_MAX = 100.0
MOOD_STARTING_MIN_PCT = 0.4 # Dal 40% al 60% del range (quindi da -20 a +20 se il range è -100 a 100)
MOOD_STARTING_MAX_PCT = 0.6
MAX_RECENT_EMOTIONS_LOG = 5
MOOD_DECAY_RATE_PER_SECOND = 0.005 # Tende a neutralizzarsi molto lentamente
# Modificatori umore da bisogni (valore aggiunto/sottratto al mood_value per secondo reale se condizione attiva)
HUNGER_CRITICAL_THRESHOLD_FOR_MOOD = 15 # Sotto questa % di fame -> malumore
MOOD_MODIFIER_HUNGER_CRITICAL = -0.2
ENERGY_CRITICAL_THRESHOLD_FOR_MOOD = 10 # Sotto questa % di energia -> malumore
MOOD_MODIFIER_ENERGY_CRITICAL = -0.3
FUN_HIGH_THRESHOLD_FOR_MOOD = 85 # Sopra questa % di divertimento -> buonumore
MOOD_MODIFIER_FUN_HIGH = 0.1
FUN_ACTIONS_FOR_MOOD_BOOST = ["playing_game", "socializing_fun_activity"] # Azioni che danno boost se il fun è alto

# X.4 Aspirazioni (AspirationComponent)
ASPIRATION_DEFINITIONS_LIST = ["Diventare Chef Stellato", "Scrivere un Bestseller", "Trovare il Vero Amore", "Maestro di Logica"]
ALLOW_CUSTOM_ASPIRATIONS = False
ASPIRATION_COMPLETION_REWARD_POINTS = 1000 # Punti "soddisfazione" o simili
MOOD_BOOST_NEW_ASPIRATION = 10.0
MOOD_BOOST_ASPIRATION_COMPLETED = 75.0

# X.5 Carriera (CareerComponent)
CAREER_DEFINITIONS_PATH = "careers_data.json" # File JSON in DATA_PATH che definisce le carriere
PERFORMANCE_CHANGE_PER_WORK_DAY = 7.0
PERFORMANCE_PENALTY_MISSED_WORK = -20.0
DAYS_TO_GET_FIRED = 3
MOOD_BOOST_PROMOTION = 30.0
MOOD_PENALTY_FIRED = -60.0

# X.6 Abilità (SkillComponent)
SKILL_DEFINITIONS_PATH = "skills_data.json" # File JSON in DATA_PATH
MOOD_BOOST_SKILL_UP = 15.0

# X.7 Relazioni (RelationshipComponent)
REL_INITIAL_FRIENDSHIP = 0.0; REL_INITIAL_ROMANCE = 0.0;
REL_FRIENDSHIP_MIN = -100.0; REL_FRIENDSHIP_MAX = 100.0;
REL_ROMANCE_MIN = -100.0; REL_ROMANCE_MAX = 100.0;
REL_THRESHOLD_ENEMY = -50; REL_THRESHOLD_ACQUAINTANCE = -10; REL_THRESHOLD_FRIEND = 20;
REL_THRESHOLD_GOOD_FRIEND = 50; REL_THRESHOLD_BEST_FRIEND = 80; REL_THRESHOLD_CRUSH = 30;
RELATIONSHIP_DECAY_FACTOR_PER_DAY = 0.05 # Quanto scende al giorno se non ci sono interazioni
REL_DECAY_INACTIVITY_THRESHOLD_HOURS = 28 * 2 # Dopo 2 giorni di gioco senza interazioni significative

# X.8 Inventario (InventoryComponent)
NPC_PERSONAL_INVENTORY_CAPACITY = 15
HOUSEHOLD_INVENTORY_CAPACITY = 50 # Per l'inventario domestico

# X.9 Stato (StatusComponent)
NPC_INITIAL_AGE_YEARS_MIN = 18
NPC_INITIAL_AGE_YEARS_MAX = 35
PREGNANCY_TERM_GAME_DAYS = DAYS_PER_MONTH * 2 # Esempio: 2 mesi di gioco
MIN_PREGNANCY_AGE_YEARS = 18
MAX_PREGNANCY_AGE_YEARS = 45 # Età massima per iniziare una gravidanza
MOOD_BOOST_PREGNANT = 25.0
MOOD_BOOST_BIRTH = 100.0


# --- XI. Sprite e Animazioni NPC ---
SPRITE_FRAME_WIDTH = 64; SPRITE_FRAME_HEIGHT = 64
SPRITE_WALK_ANIM_FRAMES = 4; SPRITE_IDLE_ANIM_FRAMES = 1
DEFAULT_ANIM_SPEED = 0.15 # Secondi per frame
# Righe animazioni standard (esempio, adatta al tuo spritesheet)
ANIM_ROW_IDLE_DOWN = 0; ANIM_ROW_IDLE_LEFT = 1; ANIM_ROW_IDLE_RIGHT = 2; ANIM_ROW_IDLE_UP = 3;
ANIM_ROW_WALK_DOWN = 4; ANIM_ROW_WALK_LEFT = 5; ANIM_ROW_WALK_RIGHT = 6; ANIM_ROW_WALK_UP = 7;
# Sleep Sprites
SLEEP_SPRITESHEET_MALE_FILENAME = "malewhitesleep.png"
SLEEP_SPRITESHEET_FEMALE_FILENAME = "femalewhitesleep.png"
SLEEP_SPRITE_FRAME_WIDTH = 64; SLEEP_SPRITE_FRAME_HEIGHT = 64
NUM_SLEEP_ANIM_FRAMES = 1 # Spesso le animazioni di sonno sono statiche o con pochi frame
ANIM_ROW_SLEEP_ON_BACK = 0 # Esempio: riga 0 per dormire sulla schiena
ANIM_ROW_SLEEP_SIDE_LEFT = 1 # Esempio: riga 1 per dormire su un fianco
ANIM_ROW_SLEEP_SIDE_RIGHT = 2 # Esempio
# Bundle (Neonato)
BUNDLE_FRAME_WIDTH = 32; BUNDLE_FRAME_HEIGHT = 32 # Adatta alle dimensioni del tuo sprite bundle
BUNDLE_ANIM_ROW = 0; BUNDLE_ANIM_FRAMES = 1;

# --- XII. UI (Interfaccia Utente) ---
PANEL_UI_HEIGHT = 160 # Aumentata leggermente per più spazio
UI_BOTTOM_PANEL_PADDING = 8
UI_SECTION_SPACING = 10
UI_LEFT_SECTION_WIDTH_PERCENT = 0.26
UI_CENTER_SECTION_WIDTH_PERCENT = 0.28
UI_RIGHT_SECTION_WIDTH_PERCENT = 0.40 # (1.0 - 0.26 - 0.28 - (2*padding_tra_sezioni_se_diverso_da_spacing))

UI_ICON_SIZE = 20 # Dimensione generica per icone (es. periodo giorno)
UI_ICON_SIZE_TIME_BUTTONS = 28 # Per i pulsanti velocità
UI_ICON_SIZE_NEEDS = 18        # Per le icone dei bisogni

# Caratteri Unicode per Icone (DEVONO ESSERE SUPPORTATI DAL FONT UI_UNICODE_ICON_FONT_PATH)
ICON_CHAR_PAUSE = "\u23F8"; ICON_CHAR_PLAY = "\u25B6"; ICON_CHAR_FFWD = "\u23E9";
ICON_CHAR_FFWD2_FALLBACK = ">>"; ICON_CHAR_FFWD3_FALLBACK = ">>>"; ICON_CHAR_SLEEP_SPEED = "\U0001F4A4";
ICON_CHAR_HUNGER = "\U0001F35F"; ICON_CHAR_ENERGY = "\U0001F50B"; ICON_CHAR_SOCIAL = "\U0001F4AC";
ICON_CHAR_BLADDER = "\U0001F6BF"; ICON_CHAR_FUN = "\U0001F3AE"; ICON_CHAR_HYGIENE = "\U0001F9FC";
ICON_CHAR_INTIMACY = "\u2764"; # Cuore
ICON_CHAR_SUN = "\u2600"; ICON_CHAR_MOON_STARS = "\U0001F319"; ICON_CHAR_DAWN = "\U0001F305"; # Esempi periodo
ICON_CHAR_SUNRISE = "\U0001F304"; ICON_CHAR_SUN_BRIGHT = "\u2600"; ICON_CHAR_SUN_CLOUDS = "\u26C5";
ICON_CHAR_SUNSET_สวยงาม = "\U0001F307"; ICON_CHAR_MOON_SIMPLE = "\U0001F31C";

# Stringhe UI
UI_LABEL_ACTION = "Azione: "; UI_LABEL_FINANCE = "Denaro: "; UI_LABEL_MOOD = "Umore: ";
UI_LABEL_ASPIRATIONS = "Aspirazioni"; UI_LABEL_CAREER = "Carriera"; UI_LABEL_SKILLS = "Abilità";
UI_LABEL_RELATIONSHIPS = "Relazioni"; UI_LABEL_INVENTORY = "Inventario"; UI_LABEL_NEEDS_BUTTON = "Bisogni";
# Dimensioni/Padding UI Barre Bisogni
UI_RIGHT_SECTION_BUTTON_HEIGHT = 20; UI_RIGHT_SECTION_BUTTON_SPACING_Y = 3;
UI_NEEDS_BAR_WIDTH = 85; UI_NEEDS_BAR_HEIGHT = 12; UI_NEEDS_BAR_PADDING_Y = 2; UI_NEEDS_BAR_PADDING_X = 4;
UI_ICON_TEXT_SPACING = 2; UI_SHOW_NEED_VALUE_TEXT = True; UI_SHOW_NEED_LABEL_TEXT = False;
UI_NEEDS_BAR_BORDER_COLOR = DARK_GREY;
# Colori Barre Bisogni (se non definiti, usa fallback da game_utils.NEED_DISPLAY_ORDER_AND_INFO)
# HUNGER_BAR_COLOR = (200, 60, 60) # Esempio
# ENERGY_BAR_COLOR = (60, 100, 200) # Esempio

# --- XIII. Salvataggio e Caricamento ---
OBJECT_BLUEPRINTS_FILENAME = "object_blueprints.json" # Usato da game_utils
DEFAULT_SAVE_FILENAME = "anthalys_world.json" # Cambiato per riflettere meglio il contenuto
AUTO_SAVE_INTERVAL_SECONDS = 0 # 300 per 5 minuti, 0 per disabilitare
LOAD_GAME_ON_STARTUP = True
SAVE_GAME_ON_EXIT = True