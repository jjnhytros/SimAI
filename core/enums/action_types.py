# core/enums/action_types.py
from enum import Enum, auto
"""
Definizione dell'Enum ActionType per rappresentare tutti i tipi di azioni
eseguibili dagli NPC in SimAI.
"""

class ActionType(Enum):
    """Enum per tutti i tipi di azione, raggruppati per categoria."""
    
    # --- Azioni Generiche / Idle ---
    ACTION_IDLE = auto()                    # Non sta facendo nulla di specifico
    ACTION_MOVE_TO = auto()                 # Si sta spostando verso una destinazione
    ACTION_SHELTER_FROM_RAIN = auto()       # Cerca riparo dalla pioggia

    # --- Azioni per Bisogni Base ---
    ACTION_DISINFECT_HANDS = auto()
    ACTION_DRINK = auto()
    ACTION_EAT = auto()
    ACTION_SLEEP = auto()
    ACTION_TAKE_SHOWER_BATH = auto()
    ACTION_USE_BATHROOM = auto()            # Enum generico, usato internamente dalle classi azione
    ACTION_USE_TOILET = auto()
    
    # --- Azioni Sociali / Relazionali ---
    ACTION_ENGAGE_INTIMACY = auto()
    ACTION_HOST_PARTY = auto()              # Es. HOST_EXCLUSIVE_DINNER_PARTY, HOST_NEIGHBORHOOD_BBQ
    ACTION_SOCIALIZE = auto()               # Enum generico per SocializeAction
    ACTION_SOCIALIZE_ARGUE = auto()
    ACTION_SOCIALIZE_CHAT_CASUAL = auto()
    ACTION_SOCIALIZE_CHAT_WITH_NEIGHBOR = auto()
    ACTION_SOCIALIZE_COMPLIMENT = auto()
    ACTION_SOCIALIZE_DEEP_CONVERSATION = auto()
    ACTION_SOCIALIZE_DISCUSS_ART = auto()
    ACTION_SOCIALIZE_FLIRT = auto()
    ACTION_SOCIALIZE_INSULT = auto()
    ACTION_SOCIALIZE_OFFER_COMFORT = auto()
    ACTION_SOCIALIZE_PROPOSE_INTIMACY = auto()
    ACTION_SOCIALIZE_TELL_JOKE = auto()
    ACTION_VISIT_NPC = auto()
    ACTION_VISIT_SICK_NPC = auto()

    # --- Azioni per Svago, Hobby e Skill ---
    ACTION_HAVE_FUN = auto()                # Enum generico per HaveFunAction
    # Sotto-tipi per attività specifiche (esempi)
    ACTION_HAVE_FUN_ADMIRE_THE_VIEW = auto()
    ACTION_HAVE_FUN_ATTEND_CONCERT = auto()
    ACTION_HAVE_FUN_ATTEND_SPORTS_MATCH = auto()
    ACTION_HAVE_FUN_BROWSE_MARKET = auto()
    ACTION_HAVE_FUN_DANCE = auto()
    ACTION_HAVE_FUN_DAYDREAM = auto()
    ACTION_HAVE_FUN_DO_YOGA_IN_THE_PARK = auto()
    ACTION_HAVE_FUN_GO_FOR_A_JOG = auto()
    ACTION_HAVE_FUN_GO_FOR_A_SCENIC_DRIVE = auto()
    ACTION_HAVE_FUN_HAVE_A_PICNIC = auto()
    ACTION_HAVE_FUN_PAINT = auto()
    ACTION_HAVE_FUN_PLAY_GUITAR = auto()
    ACTION_HAVE_FUN_READ_BOOK_FOR_FUN = auto()
    ACTION_HAVE_FUN_RENT_A_ROWBOAT = auto()
    ACTION_HAVE_FUN_TRY_STREET_FOOD = auto()
    ACTION_HAVE_FUN_VISIT_MUSEUM = auto()
    ACTION_HAVE_FUN_WATCH_PLAY = auto()
    ACTION_HAVE_FUN_WATCH_TV = auto()
    
    ACTION_CRAFT_ITEM = auto()
    ACTION_GO_FISHING_IN_RIVER = auto()
    ACTION_POST_POEM = auto()          # "Affiggi Poesia" sull'Albero dei Poeti
    ACTION_PRACTICE_SKILL = auto()
    ACTION_SKETCH_IN_NOTEBOOK = auto()
    ACTION_STUDY_SKILL = auto()
    ACTION_TEND_COMMUNITY_GARDEN_PLOT = auto()
    
    # --- Azioni Lavoro e Carriera ---
    ACTION_ATTEND_BUSINESS_MEETING = auto()
    ACTION_GO_TO_WORK = auto()
    ACTION_INSPECT_CONTAINER = auto()
    ACTION_LOAD_CARGO = auto()
    ACTION_MANAGE_INVENTORY = auto()
    ACTION_NETWORK_AT_BAR = auto()
    ACTION_OPERATE_CRANE = auto()
    ACTION_PERFORM_ON_STREET = auto()       # Per musicisti/artisti di strada
    ACTION_REPAIR_SHIP = auto()
    ACTION_SEEK_JOB = auto()
    ACTION_SELL_WARES = auto()              # Per mercanti/artigiani
    ACTION_TRAIN_PROFESSIONALLY = auto()    # Per atleti
    ACTION_WORK = auto()
    ACTION_WORK_HARD = auto()
    
    # --- Azioni Scuola ed Educazione ---
    ACTION_ATTEND_LECTURE = auto()
    ACTION_DO_HOMEWORK = auto()
    ACTION_GIVE_LECTURE = auto()            # Per professori
    ACTION_GO_TO_SCHOOL = auto()
    ACTION_JOIN_STUDY_GROUP = auto()
    ACTION_PULL_ALL_NIGHTER = auto()        # Studiare tutta la notte
    ACTION_STUDY = auto()
    ACTION_STUDY_AT_LIBRARY = auto()

    # --- Azioni Civiche / Governative / Legali ---
    ACTION_ATTEND_PUBLIC_HEARING = auto()
    ACTION_FILE_OFFICIAL_DOCUMENT = auto()
    ACTION_PAY_RESPECTS_AT_MONUMENT = auto()
    ACTION_PROTEST = auto()
    ACTION_RESEARCH_HISTORICAL_RECORDS = auto()
    ACTION_SEARCH_FOR_SECRET_PASSAGES = auto()
    ACTION_TAKE_CASTLE_TOUR = auto()
    ACTION_VIEW_MEDALLIONS_OF_POWER = auto()
    ACTION_VOTE = auto()

    # --- Azioni Economiche / Acquisti ---
    ACTION_BUY_TEAM_MERCHANDISE = auto()
    ACTION_GO_SHOPPING_SPREE = auto()
    ACTION_HAGGLE_PRICE = auto()
    ACTION_WINDOW_SHOPPING = auto()
    
    # --- Azioni Sanitarie ---
    ACTION_ATTEND_THERAPY_SESSION = auto()
    ACTION_BE_HOSPITALIZED = auto()
    ACTION_DONATE_BLOOD = auto()
    ACTION_GET_MEDICAL_CHECKUP = auto()
    ACTION_GET_TREATMENT = auto()
    ACTION_PICK_UP_PRESCRIPTION = auto()
    
    # --- Azioni Domestiche / Manutenzione ---
    ACTION_CLEAN_HOUSE = auto()
    ACTION_COOK_MEAL = auto()
    ACTION_DO_GARDENING = auto()
    ACTION_REPAIR_OBJECT = auto()

    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di azione."""
        name_without_prefix = self.name.replace("ACTION_", "", 1)
        return name_without_prefix.replace("_", " ").capitalize()
