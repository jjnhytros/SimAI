# core/enums/object_types.py
"""
Definizione dell'Enum 'ObjectType' per categorizzare i tipi di oggetti nel mondo.
"""
from enum import Enum, auto

class ObjectType(Enum):
    # Oggetti per il Divertimento
    TV = auto()
    COMPUTER = auto()
    BOOKSHELF = auto() # Potrebbe contenere più libri
    BOOK = auto()      # Un singolo libro (potrebbe avere generi)
    STEREO = auto()
    MUSICAL_INSTRUMENT_PIANO = auto()
    MUSICAL_INSTRUMENT_GUITAR = auto()
    GAME_CONSOLE = auto()
    BOARD_GAME_TABLE = auto() # Un tavolo con un gioco da tavolo specifico
    EASEL = auto() # Per dipingere (hobby artistico)
    DANCE_FLOOR = auto() # Oggetto o tipo di superficie in una location

    # Oggetti Personali
    PHONE = auto()              # <-- AGGIUNTO

    # Oggetti di svago
    GUITAR = auto()             # <-- AGGIUNTO
    PIANO = auto()              # <-- AGGIUNTO
    CHESS_TABLE = auto()        # <-- AGGIUNTO

    # Oggetti Commerciali / Comunitari
    CASH_REGISTER = auto()      # <-- AGGIUNTO
    VENDING_MACHINE = auto()    # <-- AGGIUNTO
    BAR_COUNTER = auto()        # <-- AGGIUNTO

    # Oggetti per il Comfort
    CHAIR_DINING = auto()
    CHAIR_OFFICE = auto()
    SOFA = auto()
    ARMCHAIR = auto()
    BED = auto()
    BED_SINGLE = auto()
    BED_DOUBLE = auto()
    TABLE = auto()
    CHAIR = auto()
    WATER_COOLER = auto()      # Distributore d'acqua (boccione)

    # Oggetti per l'Ambiente/Decorazione
    PLANT_DECORATIVE = auto()
    PAINTING_WALL = auto()
    SCULPTURE = auto()
    RUG = auto()
    WINDOW_LARGE = auto()
    LAMP = auto()

    # Oggetti per Bisogni Fisiologici / Cucina / Bagno
    REFRIGERATOR = auto()
    STOVE = auto() # Fornelli
    MICROWAVE = auto()
    COFFEE_MACHINE = auto()
    SINK_KITCHEN = auto()
    SINK_BATHROOM = auto()
    TOILET = auto()
    SHOWER = auto()
    BATHTUB = auto()
    TRASH_CAN = auto()
    SINK = auto()

    # Oggetti per Skill/Lavoro/Studio
    WORKBENCH_CRAFTING = auto()
    DESK = auto()
    BOOK_SKILL_PROGRAMMING = auto() # Esempio libro per skill
    TELESCOPE = auto() # Per interesse/skill Astronomia

    # Oggetti Vari
    DOOR = auto()
    WARDROBE = auto() # Guardaroba
    MIRROR = auto()

    # Oggetti specifici di Anthalys (da definire in base al lore)
    ASTRAL_CHARTING_TABLE = auto() # Esempio dal lore
    TECH_RELIC_DISPLAY = auto()    # Esempio dal lore

    # Oggetti "interattivi" ma non necessariamente posseduti
    PUBLIC_BENCH = auto()
    FOUNTAIN = auto()

    UNKNOWN = auto() # Oggetto generico o non specificato

    def display_name_it(self) -> str:
        # Potresti creare un mapping più specifico se necessario,
        # per ora usiamo una formattazione generica.
        return self.name.replace("_", " ").title()