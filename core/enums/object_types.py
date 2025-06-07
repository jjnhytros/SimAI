# core/enums/object_types.py
from enum import Enum, auto
"""
Definizione dell'Enum ObjectType per rappresentare i tipi di oggetti
interagibili e non nel mondo di SimAI.
Riferimento TODO: I.4, XVIII.1
"""

class ObjectType(Enum):
    """
    Enum per i diversi tipi di oggetti, raggruppati per categoria funzionale.
    """
    # --- Categoria: Arredamento Base ---
    ARMCHAIR = auto()               # Poltrona
    BAR_COUNTER = auto()            # Bancone da bar
    BED = auto()                    # Letto
    CABINET = auto()                # Mobiletto da cucina/bagno
    CHAIR = auto()                  # Sedia generica
    COFFEE_TABLE = auto()           # Tavolino da caffè
    COUNTER = auto()                # Bancone da cucina
    DESK = auto()                   # Scrivania
    DESK_CHAIR = auto()             # Sedia da scrivania
    DINING_CHAIR = auto()           # Sedia da pranzo
    DINING_TABLE = auto()           # Tavolo da pranzo
    DRESSER = auto()                # Cassettiera
    SOFA = auto()                   # Divano
    TABLE = auto()                  # Tavolo generico
    WARDROBE = auto()               # Armadio per vestiti

    # --- Categoria: Elettrodomestici e Apparecchiature ---
    COFFEE_MACHINE = auto()
    DISHWASHER = auto()
    DOMESTIC_TRASH_COMPACTOR = auto() # Smaltitore Domestico
    MICROWAVE = auto()
    OVEN = auto()
    REFRIGERATOR = auto()
    STOVE = auto()                  # Fornelli
    WASHING_MACHINE = auto()
    
    # --- Categoria: Sanitari / Idraulica ---
    BATHTUB = auto()
    SHOWER = auto()
    SINK = auto()
    TOILET = auto()
    
    # --- Categoria: Elettronica di Consumo ---
    COMPUTER = auto()
    GAME_CONSOLE = auto()
    LAPTOP = auto()
    PHONE = auto()
    STEREO = auto()
    TV = auto()
    
    # --- Categoria: Svago, Hobby e Skill ---
    BOOK = auto()                   # Un libro singolo come oggetto
    BOOKSHELF = auto()
    CHEMISTRY_LAB_STATION = auto()  # Per Alchimia/Scienza
    CHESS_TABLE = auto()
    DJ_TURNTABLE = auto()
    EASEL = auto()                  # Cavalletto per pittura
    GRILL = auto()                  # Griglia per barbecue
    GUITAR = auto()                 # Chitarra
    PIANO = auto()                  # Pianoforte
    TELESCOPE = auto()              # Telesopio
    TREADMILL = auto()              # Tapis roulant
    VIOLIN = auto()                 # Violino
    WORKBENCH = auto()              # Banco da lavoro generico (Handiness)
    WORKOUT_MACHINE = auto()
    
    # --- Categoria: Decorazioni e Varie ---
    LAMP = auto()                   # Lampada generica
    MIRROR = auto()                 # Specchio
    PAINTING_OBJECT = auto()        # Un quadro appeso al muro
    PLANT_POT = auto()              # Vaso per piante da interno
    RUG = auto()                    # Tappeto
    SCULPTURE = auto()
    
    # --- Categoria: Oggetti Pubblici e Commerciali ---
    ARTISAN_WORKBENCH = auto()      # Banco da lavoro specifico per artigiani
    CASH_REGISTER = auto()          # Registratore di Cassa
    MARKET_STALL = auto()           # Bancarella del mercato
    PARK_BENCH = auto()
    PUBLIC_TRASH_CAN = auto()
    SMART_BIN = auto()
    SONET_INFO_KIOSK = auto()       # Chiosco informativo SoNet
    TURNSTILE = auto()              # Tornello (Stadio, Metro)
    VENDING_MACHINE = auto()

    # --- Categoria: Oggetti Unici / Monumenti ---
    CONSTITUTION_MONUMENT = auto()
    ETERNAL_FLAME_MONUMENT = auto()
    FOUNTAIN = auto()               # Fontana pubblica/ornamentale
    HISTORICAL_PLAQUE = auto()      # Placca storica
    STATUE = auto()

    # --- Categoria: Industriale / Portuale ---
    AUTOMATED_LOADING_ARM = auto()  # Braccio di carico
    CARGO_CONTAINER = auto()
    INDUSTRIAL_MACHINERY = auto()
    
    # --- Categoria: Veicoli (come oggetti di scena o interagibili) ---
    AUTONOMOUS_SHUTTLE = auto()
    FUNICULAR_CAR = auto()
    LUXURY_CAR_DECO = auto()
    ROWBOAT = auto()                # Barca a remi
    SCHOOL_BUS_STOP_SIGN = auto()   # La fermata dello scuolabus

    # --- Categoria: Risorse e Consumabili ---
    CRAFTING_MATERIAL = auto()      # Materiale generico per crafting
    DRINK_ITEM = auto()             # Una bevanda (es. bottiglia d'acqua, succo)
    FOOD_ITEM = auto()              # Un piatto di cibo pronto
    
    # --- Tipo Generico ---
    UNKNOWN_OBJECT = auto()

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di oggetto."""
        return self.name.replace("_", " ").title()