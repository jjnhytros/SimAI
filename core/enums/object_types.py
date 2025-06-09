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

    KILN = auto()
    BOOKSHELF = auto()
    CHEMISTRY_SET = auto()
    TV = auto()

    # --- Categoria 1: Arredamento (50) ---
    ARMCHAIR = auto()
    BAR_COUNTER = auto()
    BAR_STOOL = auto()
    BED = auto()
    BENCH = auto()
    BOOKCASE = auto()
    CABINET = auto()
    CHAIR = auto()
    CHAISE_LOUNGE = auto()
    CLOSET = auto()
    COFFEE_TABLE = auto()
    COUCH = auto()
    COUNTER = auto()
    CUPBOARD = auto()
    CURTAIN = auto()
    DESK = auto()
    DESK_CHAIR = auto()
    DINING_CHAIR = auto()
    DINING_TABLE = auto()
    DISPLAY_CABINET = auto()
    DIVIDER_SCREEN = auto()
    DRESSER = auto()
    DRESSING_TABLE = auto()
    END_TABLE = auto()
    FLOOR_LAMP = auto()
    FOOTSTOOL = auto()
    FUTON = auto()
    HAMMOCK = auto()
    HEADBOARD = auto()
    HIGH_CHAIR = auto()
    KITCHEN_ISLAND = auto()
    LAUNDRY_BASKET = auto()
    LOUNGE_CHAIR = auto()
    MANTELPIECE = auto()
    MATTRESS = auto()
    MIRROR_DRESSER = auto()
    NIGHTSTAND = auto()
    OTTOMAN = auto()
    PATIO_FURNITURE = auto()
    PEW = auto()
    PICTURE_FRAME = auto()
    POUF = auto()
    RECLINER = auto()
    ROOM_DIVIDER = auto()
    RUG = auto()
    SHELVING_UNIT = auto()
    SOFA = auto()
    SOFA_BED = auto()
    STOOL = auto()
    TABLE = auto()
    WARDROBE = auto()

    # --- Categoria 2: Tecnologia e Domotica (50) ---
    PRINTER_3D = auto()
    ARCADE_MACHINE = auto()
    ATM = auto()
    BLUEPRINT_PRINTER = auto()
    CAMERA = auto()
    CASH_REGISTER = auto()
    COMPUTER = auto()
    DIGITAL_FRAME = auto()
    DIGITAL_SIGNAGE = auto()
    DRONE_CHARGER = auto()
    FIBER_OPTIC_TERMINAL = auto()
    FIREWALL_SERVER = auto()
    FITNESS_TRACKER = auto()
    GAME_CONSOLE = auto()
    HOLO_DISPLAY = auto()
    HOME_AUTOMATION_HUB = auto()
    KINECT_SENSOR = auto()
    LAPTOP = auto()
    LASER_PRINTER = auto()
    MOBILE_CHARGER = auto()
    OVEN = auto()
    PHONE = auto()
    PROJECTOR = auto()
    REFRIGERATOR = auto()
    ROBOT_VACUUM = auto()
    SECURITY_CAM = auto()
    SMART_BIN = auto()
    SMART_MIRROR = auto()
    DIGITAL_PEN = auto()
    SMART_REFRIGERATOR = auto()
    SMART_TOILET = auto()
    SMART_WINDOW = auto()
    SONET_INFO_KIOSK = auto()
    SPEAKER = auto()
    STEREO = auto()
    SURVEILLANCE_DRONE = auto()
    TABLET = auto()
    TELEPRESENCE_ROBOT = auto()
    TELEVISION = auto()
    TOUCHSCREEN_TABLE = auto()
    TREADMILL = auto()
    TV_WALL = auto()
    VENDING_MACHINE = auto()
    VIRTUAL_PET = auto()
    VR_HEADSET = auto()
    WASHING_MACHINE = auto()
    WATER_COOLER = auto()
    WEARABLE_TECH = auto()

    # --- Categoria 3: Cucina e Dispensa (50) ---
    AIR_FRYER = auto()
    BLENDER = auto()
    BREAD_MAKER = auto()
    CAN_OPENER = auto()
    COFFEE_GRINDER = auto()
    COFFEE_MACHINE = auto()
    COFFEE_PRESS = auto()
    COOKBOOK_STAND = auto()
    COOKTOP = auto()
    CUTTING_BOARD = auto()
    DISHWASHER = auto()
    DOUGH_MIXER = auto()
    ELECTRIC_KETTLE = auto()
    ESPRESSO_MACHINE = auto()
    FOOD_PROCESSOR = auto()
    FRYER = auto()
    GARLIC_PRESS = auto()
    HERB_GRINDER = auto()
    ICE_MAKER = auto()
    JUICER = auto()
    KITCHEN_SCALE = auto()
    KITCHEN_TIMER = auto()
    KNIFE_BLOCK = auto()
    MICROWAVE = auto()
    MORTAR_PESTLE = auto()
    NUT_CRACKER = auto()
    OVEN_MITT = auto()
    PANINI_PRESS = auto()
    PASTA_MAKER = auto()
    PIZZA_STONE = auto()
    PRESSURE_COOKER = auto()
    RANGE_HOOD = auto()
    RICE_COOKER = auto()
    SALAD_SPINNER = auto()
    SALT_SHAKER = auto()
    SANDWICH_MAKER = auto()
    SLOW_COOKER = auto()
    SODA_STREAM = auto()
    SOUS_VIDE = auto()
    SPICE_RACK = auto()
    STEAMER = auto()
    STOVE = auto()
    TOASTER = auto()
    TORTILLA_PRESS = auto()
    UTENSIL_HOLDER = auto()
    WAFFLE_IRON = auto()
    WATER_FILTER = auto()
    WINE_COOLER = auto()
    WINE_RACK = auto()
    YOGURT_MAKER = auto()

    # --- Categoria 4: Bagno e Igiene (50) ---
    AIR_PURIFIER = auto()
    BATH_MAT = auto()
    BATHTUB = auto()
    BIDET = auto()
    BODY_MIST_DISPENSER = auto()
    COSMETIC_FRIDGE = auto()
    DENTAL_CARE_STATION = auto()
    DEODORIZER = auto()
    DOUCHE = auto()
    ELECTRIC_TOOTHBRUSH = auto()
    ESSENTIAL_OIL_DIFFUSER = auto()
    FACIAL_STEAMER = auto()
    FOOT_SPA = auto()
    HAIR_DRYER = auto()
    HAND_DRYER = auto()
    HUMIDIFIER = auto()
    HYGIENE_STATION = auto()
    JACUZZI = auto()
    MAKEUP_VANITY = auto()
    MASSAGE_SHOWER = auto()
    MEDICINE_CABINET = auto()
    PEDICURE_STATION = auto()
    PERFUME_ORGANIZER = auto()
    RAIN_SHOWER = auto()
    SAUNA = auto()
    SCALES = auto()
    SHAVING_STATION = auto()
    SHOWER = auto()
    SHOWER_CADDY = auto()
    SHOWER_GEL_DISP = auto()
    SINK = auto()
    SKINCARE_FRIDGE = auto()
    SOAP_DISPENSER = auto()
    STEAM_ROOM = auto()
    TISSUE_BOX = auto()
    TOILET = auto()
    TOILET_BRUSH = auto()
    TOILET_PAPER_HOLDER = auto()
    TOWEL_HEATER = auto()
    TOWEL_RACK = auto()
    TRASH_CAN = auto()
    TUMBLER_DRYER = auto()
    UV_SANITIZER = auto()
    VENTILATION_FAN = auto()
    WEIGHT_SCALE = auto()
    WHIRLPOOL = auto()
    YOGA_MAT_RACK = auto()

    # --- Categoria 5: Intrattenimento e Hobby (50) ---
    AERIAL_HOOP = auto()
    AQUARIUM = auto()
    ART_SUPPLIES = auto()
    BACKGAMMON = auto()
    BADMINTON_SET = auto()
    BILLIARDS_TABLE = auto()
    BOARD_GAME = auto()
    BOOK = auto()
    BOUNCY_CASTLE = auto()
    CAMPING_GEAR = auto()
    CARDS_TABLE = auto()
    CERAMIC_KILN = auto()
    CHESS_TABLE = auto()
    CRAFTING_TABLE = auto()
    DANCE_POLE = auto()
    DJ_TURNTABLE = auto()
    DARTBOARD = auto()
    DRUM_SET = auto()
    EASEL = auto()
    FIRE_SPINNING_TOOLS = auto()
    FITNESS_BALL = auto()
    FLOWER_ARRANGEMENT = auto()
    FOOSBALL_TABLE = auto()
    GAMING_RIG = auto()
    GARDENING_TOOLS = auto()
    GUITAR = auto()
    HAMMOCK_STAND = auto()
    HOME_THEATER = auto()
    INSTRUMENT_CASE = auto()
    JIGSAW_PUZZLE = auto()
    JOGGING_TRACK = auto()
    JUKEBOX = auto()
    JEWELRY_TOOLS = ()
    KARAOKE_MACHINE = auto()
    KNITTING_BASKET = auto()
    MEDITATION_CUSHION = auto()
    MICROPHONE = auto()
    PAINT_SET = auto()
    PIANO = auto()
    PINBALL = auto()
    POTTERY_WHEEL = auto()
    PUPPET_THEATER = auto()
    SCULPTING_TOOLS = auto()
    SEWING_MACHINE = auto()
    SOLAR_OBSERVATORY = auto()
    TELESCOPE = auto()
    TIE_DYE_KIT = auto()
    VIDEO_GAME = auto()
    VIOLIN = auto()
    VR_GAMING_ZONE = auto()
    YOGA_MAT = auto()

    # --- Categoria 6: Esterno e Pubblico (50) ---
    BIKE_RACK = auto()
    BUS_SHELTER = auto()
    CAMPFIRE_RING = auto()
    CAR_WASH = auto()
    CHILDREN_SWING = auto()
    COMMUNITY_GRILL = auto()
    DOG_PARK_AGILITY = auto()
    DRINKING_FOUNTAIN = auto()
    FARMERS_MARKET_STALL = auto()
    FIRE_HYDRANT = auto()
    FISHING_PIER = auto()
    FLAGPOLE = auto()
    FOUNTAIN = auto()
    FUNICULAR_STATION = auto()
    GARDEN_GNOME = auto()
    GAS_PUMP = auto()
    HORSE_TROUGH = auto()
    HOT_DOG_CART = auto()
    ICE_SKATING_RINK = auto()
    INFORMATION_BOOTH = auto()
    KIOSK_NEWSPAPER = auto()
    LIFEGUARD_CHAIR = auto()
    LITTER_BOX = auto()
    MAILBOX = auto()
    PARK_BENCH = auto()
    PARKING_METER = auto()
    PET_FOUNTAIN = auto()
    PICNIC_TABLE = auto()
    PLAYGROUND_SLIDE = auto()
    POOL_LADDER = auto()
    PUBLIC_ART = auto()
    PUBLIC_BBQ = auto()
    PUBLIC_BOOKCASE = auto()
    PUBLIC_CHARGER = auto()
    PUBLIC_CLOCK = auto()
    PUBLIC_GARDEN = auto()
    PUBLIC_MAP = auto()
    PUBLIC_SHOWER = auto()
    PUBLIC_TOILET = auto()
    RECYCLING_BIN = auto()
    SKATE_RAMP = auto()
    SOLAR_PANEL = auto()
    STATUE = auto()
    STREET_LAMP = auto()
    TAXI_STAND = auto()
    TRAFFIC_CONE = auto()
    TURNSTILE = auto()
    VERTICAL_GARDEN = auto()
    WATERING_HOLE = auto()
    WEATHER_STATION = auto()

    # --- Categoria 7: Romantico e Sensuale (50) ---
    AROMA_CANDLES = auto()
    BED_CANOPY = auto()
    BOUQUET_VASE = auto()
    CHAMPAGNE_BUCKET = auto()
    CHOCOLATE_FOUNTAIN = auto()
    COUPLE_MASSAGER = auto()
    DIAMOND_RING = auto()
    DOUBLE_HEADED_MASSAGER = auto()
    ENGRAVED_LOCK = auto()
    ERGONOMIC_LINGERIE = auto()
    ESSENTIAL_OIL_SET = auto()
    FIREPLACE_SCREEN = auto()
    FLIRTATION_COUCH = auto()
    HEART_SHAPED_TUB = auto()
    HOT_TUB = auto()
    INTIMATE_LUBRICANT = auto()
    KAMA_SUTRA_BOOK = auto()
    LOVE_LETTER_BOX = auto()
    LOVE_SEAT = auto()
    LOVE_SWING = auto()
    LUXURY_BEDDING = auto()
    MASSAGE_OIL_WARMER = auto()
    MATCHMAKING_KIOSK = auto()
    MOOD_LIGHTING = auto()
    MUSIC_BOX = auto()
    PERFUME_ATOMIZER = auto()
    PHEROMONE_DIFFUSER = auto()
    PILLOW_TALK_DEVICE = auto()
    PLUSH_ROBE = auto()
    ROMANCE_NOVEL = auto()
    ROMANTIC_BALCONY = auto()
    ROSE_PETAL_DISPENSER = auto()
    SCENTED_DRAWER_LINERS = auto()
    SEDUCTION_GAME = auto()
    SENSORY_DEPRIVATION_TANK = auto()
    SILK_SHEETS = auto()
    SKYLIGHT_BED = auto()
    SOUNDPROOF_WALL = auto()
    SPICE_RACK_ADULT = auto()
    STAGING_AREA = auto()
    STIMULATION_DEVICE = auto()
    TANTRIC_CHAIR = auto()
    VELVET_ROPE = auto()
    VIBRATING_MAT = auto()
    VOYEUR_MIRROR = auto()
    WEDDING_ARCH = auto()

    # --- Oggetto generico ---
    UNKNOWN_OBJECT = auto()

def display_name_it(self) -> str:
    names = {
        # ================ CATEGORIA 1: ARREDAMENTO ================
        ObjectType.ARMCHAIR: "Poltrona",
        ObjectType.BAR_COUNTER: "Bancone da bar",
        ObjectType.BAR_STOOL: "Sgabello da bar",
        ObjectType.BED: "Letto",
        ObjectType.BENCH: "Panchina",
        ObjectType.BOOKCASE: "Libreria",
        ObjectType.CABINET: "Mobiletto",
        ObjectType.CHAIR: "Sedia",
        ObjectType.CHAISE_LOUNGE: "Chaise longue",
        ObjectType.CLOSET: "Armadio",
        ObjectType.COFFEE_TABLE: "Tavolino",
        ObjectType.COUCH: "Divano",
        ObjectType.COUNTER: "Bancone",
        ObjectType.CUPBOARD: "Credenza",
        ObjectType.CURTAIN: "Tenda",
        ObjectType.DESK: "Scrivania",
        ObjectType.DESK_CHAIR: "Sedia da ufficio",
        ObjectType.DINING_CHAIR: "Sedia da pranzo",
        ObjectType.DINING_TABLE: "Tavolo da pranzo",
        ObjectType.DISPLAY_CABINET: "Vetrina",
        ObjectType.DIVIDER_SCREEN: "Paravento",
        ObjectType.DRESSER: "Comò",
        ObjectType.DRESSING_TABLE: "Toeletta",
        ObjectType.END_TABLE: "Tavolino laterale",
        ObjectType.FLOOR_LAMP: "Lampada da terra",
        ObjectType.FOOTSTOOL: "Poggiapiedi",
        ObjectType.FUTON: "Futon",
        ObjectType.HAMMOCK: "Amaca",
        ObjectType.HEADBOARD: "Testiera",
        ObjectType.HIGH_CHAIR: "Seggiolone",
        ObjectType.KITCHEN_ISLAND: "Isola cucina",
        ObjectType.LAUNDRY_BASKET: "Cesto della biancheria",
        ObjectType.LOUNGE_CHAIR: "Sedia lounge",
        ObjectType.MANTELPIECE: "Camino",
        ObjectType.MATTRESS: "Materasso",
        ObjectType.MIRROR_DRESSER: "Toeletta con specchio",
        ObjectType.NIGHTSTAND: "Comodino",
        ObjectType.OTTOMAN: "Poggiapiedi",
        ObjectType.PATIO_FURNITURE: "Mobili da esterno",
        ObjectType.PEW: "Panca",
        ObjectType.PICTURE_FRAME: "Cornice",
        ObjectType.POUF: "Pouf",
        ObjectType.RECLINER: "Poltrona reclinabile",
        ObjectType.ROOM_DIVIDER: "Separè",
        ObjectType.RUG: "Tappeto",
        ObjectType.SHELVING_UNIT: "Scaffalatura",
        ObjectType.SOFA: "Divano",
        ObjectType.SOFA_BED: "Divano letto",
        ObjectType.STOOL: "Sgabello",
        ObjectType.TABLE: "Tavolo",
        ObjectType.WARDROBE: "Armadio",
        
        # ================ CATEGORIA 2: TECNOLOGIA E DOMOTICA ================
        ObjectType['3D_PRINTER']: "Stampante 3D",
        ObjectType.ARCADE_MACHINE: "Macchina arcade",
        ObjectType.ATM: "Bancomat",
        ObjectType.BLUEPRINT_PRINTER: "Stampante progetti",
        ObjectType.CAMERA: "Fotocamera",
        ObjectType.CASH_REGISTER: "Registratore di cassa",
        ObjectType.COMPUTER: "Computer",
        ObjectType.DIGITAL_FRAME: "Cornice digitale",
        ObjectType.DIGITAL_SIGNAGE: "Insegna digitale",
        ObjectType.DISHWASHER: "Lavastoviglie",
        ObjectType.DRONE_CHARGER: "Caricabatterie droni",
        ObjectType.FIBER_OPTIC_TERMINAL: "Terminale fibra ottica",
        ObjectType.FIREWALL_SERVER: "Server firewall",
        ObjectType.FITNESS_TRACKER: "Activity tracker",
        ObjectType.GAME_CONSOLE: "Console per giochi",
        ObjectType.HOLO_DISPLAY: "Ologramma",
        ObjectType.HOME_AUTOMATION_HUB: "Centralina domotica",
        ObjectType.KINECT_SENSOR: "Sensore Kinect",
        ObjectType.LAPTOP: "Laptop",
        ObjectType.LASER_PRINTER: "Stampante laser",
        ObjectType.MICROWAVE: "Microonde",
        ObjectType.MOBILE_CHARGER: "Caricabatterie mobile",
        ObjectType.OVEN: "Forno",
        ObjectType.PHONE: "Telefono",
        ObjectType.PROJECTOR: "Proiettore",
        ObjectType.REFRIGERATOR: "Frigorifero",
        ObjectType.ROBOT_VACUUM: "Robot aspirapolvere",
        ObjectType.SECURITY_CAM: "Telecamera sicurezza",
        ObjectType.SMART_BIN: "Cestino intelligente",
        ObjectType.SMART_MIRROR: "Specchio intelligente",
        ObjectType.SMART_REFRIGERATOR: "Frigo intelligente",
        ObjectType.SMART_TOILET: "Water intelligente",
        ObjectType.SMART_WINDOW: "Finestra intelligente",
        ObjectType.SONET_INFO_KIOSK: "Chiosco SoNet",
        ObjectType.SPEAKER: "Altoparlante",
        ObjectType.STEREO: "Stereo",
        ObjectType.STOVE: "Fornello",
        ObjectType.SURVEILLANCE_DRONE: "Drone sorveglianza",
        ObjectType.TABLET: "Tablet",
        ObjectType.TELEPRESENCE_ROBOT: "Robot telepresenza",
        ObjectType.TELEVISION: "Televisione",
        ObjectType.TOUCHSCREEN_TABLE: "Tavolo touchscreen",
        ObjectType.TREADMILL: "Tapis roulant",
        ObjectType.TV_WALL: "Parete TV",
        ObjectType.VENDING_MACHINE: "Distributore automatico",
        ObjectType.VIRTUAL_PET: "Animale virtuale",
        ObjectType.VR_HEADSET: "Visore VR",
        ObjectType.WASHING_MACHINE: "Lavatrice",
        ObjectType.WATER_COOLER: "Dispenser acqua",
        ObjectType.WEARABLE_TECH: "Tecnologia indossabile",
        
        # ================ CATEGORIA 3: CUCINA E DISPENSA ================
        ObjectType.AIR_FRYER: "Friggitrice ad aria",
        ObjectType.BLENDER: "Frullatore",
        ObjectType.BREAD_MAKER: "Macchina per il pane",
        ObjectType.CAN_OPENER: "Apri scatole",
        ObjectType.COFFEE_GRINDER: "Macinacaffè",
        ObjectType.COFFEE_MACHINE: "Macchina per caffè",
        ObjectType.COFFEE_PRESS: "Pressa francese",
        ObjectType.COOKBOOK_STAND: "Porta ricette",
        ObjectType.COOKTOP: "Piano cottura",
        ObjectType.CUTTING_BOARD: "Tagliere",
        ObjectType.DISHWASHER: "Lavastoviglie",
        ObjectType.DOUGH_MIXER: "Impastatrice",
        ObjectType.ELECTRIC_KETTLE: "Bollitore elettrico",
        ObjectType.ESPRESSO_MACHINE: "Macchina per espresso",
        ObjectType.FOOD_PROCESSOR: "Robot da cucina",
        ObjectType.FRYER: "Friggitrice",
        ObjectType.GARLIC_PRESS: "Schiaccia aglio",
        ObjectType.HERB_GRINDER: "Macina erbe",
        ObjectType.ICE_MAKER: "Macchina del ghiaccio",
        ObjectType.JUICER: "Spremi frutta",
        ObjectType.KITCHEN_SCALE: "Bilancia da cucina",
        ObjectType.KITCHEN_TIMER: "Timer da cucina",
        ObjectType.KNIFE_BLOCK: "Porta coltelli",
        ObjectType.MICROWAVE: "Microonde",
        ObjectType.MORTAR_PESTLE: "Mortaio e pestello",
        ObjectType.NUT_CRACKER: "Schiacciasnoci",
        ObjectType.OVEN_MITT: "Guanto da forno",
        ObjectType.PANINI_PRESS: "Pressa per panini",
        ObjectType.PASTA_MAKER: "Macchina per pasta",
        ObjectType.PIZZA_STONE: "Pietra per pizza",
        ObjectType.PRESSURE_COOKER: "Pentola a pressione",
        ObjectType.RANGE_HOOD: "Cappa aspirante",
        ObjectType.RICE_COOKER: "Cuoci riso",
        ObjectType.SALAD_SPINNER: "Centrifuga per insalata",
        ObjectType.SALT_SHAKER: "Saliera",
        ObjectType.SANDWICH_MAKER: "Tostapanini",
        ObjectType.SLOW_COOKER: "Cottura lenta",
        ObjectType.SODA_STREAM: "Gasatore d'acqua",
        ObjectType.SOUS_VIDE: "Cottura sottovuoto",
        ObjectType.SPICE_RACK: "Portaspezie",
        ObjectType.STEAMER: "Pentola a vapore",
        ObjectType.STOVE: "Fornello",
        ObjectType.TOASTER: "Tostapane",
        ObjectType.TORTILLA_PRESS: "Pressa per tortillas",
        ObjectType.UTENSIL_HOLDER: "Porta utensili",
        ObjectType.WAFFLE_IRON: "Macchina per waffle",
        ObjectType.WATER_FILTER: "Filtro acqua",
        ObjectType.WINE_COOLER: "Cantinetta vini",
        ObjectType.WINE_RACK: "Portabottiglie",
        ObjectType.YOGURT_MAKER: "Yogurtiera",
        
        # ================ CATEGORIA 4: BAGNO E IGIENE ================
        ObjectType.AIR_PURIFIER: "Depuratore d'aria",
        ObjectType.BATH_MAT: "Tappetino da bagno",
        ObjectType.BATHTUB: "Vasca da bagno",
        ObjectType.BIDET: "Bidet",
        ObjectType.BODY_MIST_DISPENSER: "Erogatore profumi",
        ObjectType.COSMETIC_FRIDGE: "Frigo cosmetici",
        ObjectType.DENTAL_CARE_STATION: "Postazione igiene dentale",
        ObjectType.DEODORIZER: "Deodorante ambiente",
        ObjectType.DOUCHE: "Doccia intima",
        ObjectType.ELECTRIC_TOOTHBRUSH: "Spazzolino elettrico",
        ObjectType.ESSENTIAL_OIL_DIFFUSER: "Diffusore oli essenziali",
        ObjectType.FACIAL_STEAMER: "Vaporizzatore viso",
        ObjectType.FOOT_SPA: "Idromassaggio piedi",
        ObjectType.HAIR_DRYER: "Asciugacapelli",
        ObjectType.HAND_DRYER: "Asciugamani ad aria",
        ObjectType.HUMIDIFIER: "Umidificatore",
        ObjectType.HYGIENE_STATION: "Postazione igiene",
        ObjectType.JACUZZI: "Idromassaggio",
        ObjectType.MAKEUP_VANITY: "Toeletta trucco",
        ObjectType.MASSAGE_SHOWER: "Doccia massaggiante",
        ObjectType.MEDICINE_CABINET: "Armadietto medicinali",
        ObjectType.PEDICURE_STATION: "Postazione pedicure",
        ObjectType.PERFUME_ORGANIZER: "Organizzatore profumi",
        ObjectType.RAIN_SHOWER: "Doccia a pioggia",
        ObjectType.SAUNA: "Sauna",
        ObjectType.SCALES: "Bilancia",
        ObjectType.SHAVING_STATION: "Postazione rasatura",
        ObjectType.SHOWER: "Doccia",
        ObjectType.SHOWER_CADDY: "Portaoggetti doccia",
        ObjectType.SHOWER_GEL_DISP: "Dispenser doccia schiuma",
        ObjectType.SINK: "Lavandino",
        ObjectType.SKINCARE_FRIDGE: "Frigo prodotti viso",
        ObjectType.SMART_MIRROR: "Specchio intelligente",
        ObjectType.SOAP_DISPENSER: "Dispenser sapone",
        ObjectType.STEAM_ROOM: "Bagno turco",
        ObjectType.TISSUE_BOX: "Portafazzoletti",
        ObjectType.TOILET: "Water",
        ObjectType.TOILET_BRUSH: "Scovolino",
        ObjectType.TOILET_PAPER_HOLDER: "Porta carta igienica",
        ObjectType.TOWEL_HEATER: "Scalda asciugamani",
        ObjectType.TOWEL_RACK: "Porta asciugamani",
        ObjectType.TRASH_CAN: "Cestino",
        ObjectType.TUMBLER_DRYER: "Asciugabiancheria",
        ObjectType.UV_SANITIZER: "Sanificatore UV",
        ObjectType.VENTILATION_FAN: "Ventilatore",
        ObjectType.WATER_FILTER: "Filtro acqua",
        ObjectType.WEIGHT_SCALE: "Bilancia pesapersone",
        ObjectType.WHIRLPOOL: "Vasca idromassaggio",
        ObjectType.YOGA_MAT_RACK: "Portatappetino yoga",
        
        # ================ CATEGORIA 5: INTRATTENIMENTO E HOBBY ================
        ObjectType.AERIAL_HOOP: "Ceresa aerea",
        ObjectType.AQUARIUM: "Acquario",
        ObjectType.ART_SUPPLIES: "Materiale artistico",
        ObjectType.BACKGAMMON: "Tavola reale",
        ObjectType.BADMINTON_SET: "Set badminton",
        ObjectType.BILLIARDS_TABLE: "Biliardo",
        ObjectType.BOARD_GAME: "Gioco da tavolo",
        ObjectType.BOOK: "Libro",
        ObjectType.BOUNCY_CASTLE: "Castello gonfiabile",
        ObjectType.CAMPING_GEAR: "Attrezzatura campeggio",
        ObjectType.CARDS_TABLE: "Tavolo carte",
        ObjectType.CERAMIC_KILN: "Fornace ceramica",
        ObjectType.CHESS_TABLE: "Scacchiera",
        ObjectType.CRAFTING_TABLE: "Banco da lavoro",
        ObjectType.DANCE_POLE: "Palo da ballo",
        ObjectType.DJ_TURNTABLE: "Giradischi DJ",
        ObjectType.DARTBOARD: "Bersaglio freccette",
        ObjectType.DRUM_SET: "Batteria",
        ObjectType.EASEL: "Cavalletto",
        ObjectType.FIRE_SPINNING_TOOLS: "Attrezzi giocoleria",
        ObjectType.FITNESS_BALL: "Palla ginnica",
        ObjectType.FLOWER_ARRANGEMENT: "Composizione floreale",
        ObjectType.FOOSBALL_TABLE: "Calcio balilla",
        ObjectType.GAMING_RIG: "Postazione gaming",
        ObjectType.GARDENING_TOOLS: "Attrezzi giardinaggio",
        ObjectType.GUITAR: "Chitarra",
        ObjectType.HAMMOCK_STAND: "Supporto amaca",
        ObjectType.HOME_THEATER: "Home theater",
        ObjectType.INSTRUMENT_CASE: "Custodia strumenti",
        ObjectType.JIGSAW_PUZZLE: "Puzzle",
        ObjectType.JOGGING_TRACK: "Pista jogging",
        ObjectType.JUKEBOX: "Jukebox",
        ObjectType.KARAOKE_MACHINE: "Macchina karaoke",
        ObjectType.KNITTING_BASKET: "Cestino maglieria",
        ObjectType.MEDITATION_CUSHION: "Cuscino meditazione",
        ObjectType.MICROPHONE: "Microfono",
        ObjectType.PAINT_SET: "Set pittura",
        ObjectType.PIANO: "Pianoforte",
        ObjectType.PINBALL: "Flipper",
        ObjectType.POTTERY_WHEEL: "Tornio vasaio",
        ObjectType.PUPPET_THEATER: "Teatro dei burattini",
        ObjectType.SEWING_MACHINE: "Macchina da cucire",
        ObjectType.SOLAR_OBSERVATORY: "Osservatorio solare",
        ObjectType.TELESCOPE: "Telescopio",
        ObjectType.TIE_DYE_KIT: "Kit tintura",
        ObjectType.VIDEO_GAME: "Videogioco",
        ObjectType.VIOLIN: "Violino",
        ObjectType.VR_GAMING_ZONE: "Zona VR gaming",
        ObjectType.YOGA_MAT: "Tappetino yoga",
        
        # ================ CATEGORIA 6: ESTERNO E PUBBLICO ================
        ObjectType.BIKE_RACK: "Rastrelliera bici",
        ObjectType.BUS_SHELTER: "Pensilina bus",
        ObjectType.CAMPFIRE_RING: "Cerchio fuoco",
        ObjectType.CAR_WASH: "Autolavaggio",
        ObjectType.CHILDREN_SWING: "Altalena bambini",
        ObjectType.COMMUNITY_GRILL: "Griglia comunitaria",
        ObjectType.DOG_PARK_AGILITY: "Parco cani",
        ObjectType.DRINKING_FOUNTAIN: "Fontana acqua",
        ObjectType.FARMERS_MARKET_STALL: "Bancarella mercato",
        ObjectType.FIRE_HYDRANT: "Idrante",
        ObjectType.FISHING_PIER: "Pontile pesca",
        ObjectType.FLAGPOLE: "Asta bandiera",
        ObjectType.FOUNTAIN: "Fontana",
        ObjectType.FUNICULAR_STATION: "Stazione funicolare",
        ObjectType.GARDEN_GNOME: "Nano da giardino",
        ObjectType.GAS_PUMP: "Pompa benzina",
        ObjectType.HORSE_TROUGH: "Abbeveratoio cavalli",
        ObjectType.HOT_DOG_CART: "Carretto hot dog",
        ObjectType.ICE_SKATING_RINK: "Pista pattinaggio",
        ObjectType.INFORMATION_BOOTH: "Info point",
        ObjectType.KIOSK_NEWSPAPER: "Edicola",
        ObjectType.LIFEGUARD_CHAIR: "Sedia bagnino",
        ObjectType.LITTER_BOX: "Cassetta rifiuti",
        ObjectType.MAILBOX: "Cassetta postale",
        ObjectType.PARK_BENCH: "Panchina parco",
        ObjectType.PARKING_METER: "Parcometro",
        ObjectType.PET_FOUNTAIN: "Fontana animali",
        ObjectType.PICNIC_TABLE: "Tavolo picnic",
        ObjectType.PLAYGROUND_SLIDE: "Scivolo parco giochi",
        ObjectType.POOL_LADDER: "Scala piscina",
        ObjectType.PUBLIC_ART: "Arte pubblica",
        ObjectType.PUBLIC_BBQ: "Barbecue pubblico",
        ObjectType.PUBLIC_BOOKCASE: "Libreria pubblica",
        ObjectType.PUBLIC_CHARGER: "Caricatore pubblico",
        ObjectType.PUBLIC_CLOCK: "Orologio pubblico",
        ObjectType.PUBLIC_GARDEN: "Giardino pubblico",
        ObjectType.PUBLIC_MAP: "Mappa pubblica",
        ObjectType.PUBLIC_SHOWER: "Doccia pubblica",
        ObjectType.PUBLIC_TOILET: "Bagno pubblico",
        ObjectType.RECYCLING_BIN: "Bidone riciclaggio",
        ObjectType.SKATE_RAMP: "Rampa skateboard",
        ObjectType.SOLAR_PANEL: "Pannello solare",
        ObjectType.STATUE: "Statua",
        ObjectType.STREET_LAMP: "Lampione",
        ObjectType.TAXI_STAND: "Fermata taxi",
        ObjectType.TRAFFIC_CONE: "Cono traffico",
        ObjectType.TURNSTILE: "Tornello",
        ObjectType.VERTICAL_GARDEN: "Giardino verticale",
        ObjectType.WATERING_HOLE: "Abbeveratoio",
        ObjectType.WEATHER_STATION: "Stazione meteo",
        
        # ================ CATEGORIA 7: ROMANTICO E SENSUALE ================
        ObjectType.AROMA_CANDLES: "Candele aromatiche",
        ObjectType.BED_CANOPY: "Baldacchino",
        ObjectType.BIDET: "Bidet",
        ObjectType.BOUQUET_VASE: "Vaso per bouquet",
        ObjectType.CHAMPAGNE_BUCKET: "Secchiello champagne",
        ObjectType.CHOCOLATE_FOUNTAIN: "Fontana di cioccolato",
        ObjectType.COUPLE_MASSAGER: "Massaggiatore coppie",
        ObjectType.DIAMOND_RING: "Anello di diamanti",
        ObjectType.DOUBLE_HEADED_MASSAGER: "Massaggiatore doppio",
        ObjectType.ENGRAVED_LOCK: "Lucchetto inciso",
        ObjectType.ERGONOMIC_LINGERIE: "Lingerie ergonomica",
        ObjectType.ESSENTIAL_OIL_SET: "Set oli essenziali",
        ObjectType.FIREPLACE_SCREEN: "Parafuoco",
        ObjectType.FLIRTATION_COUCH: "Divano per flirt",
        ObjectType.HEART_SHAPED_TUB: "Vasca a cuore",
        ObjectType.HOT_TUB: "Vasca idromassaggio",
        ObjectType.INTIMATE_LUBRICANT: "Lubrificante intimo",
        ObjectType.JACUZZI: "Idromassaggio",
        ObjectType.KAMA_SUTRA_BOOK: "Libro Kama Sutra",
        ObjectType.LOVE_LETTER_BOX: "Buca lettere d'amore",
        ObjectType.LOVE_SEAT: "Divanetto per due",
        ObjectType.LOVE_SWING: "Altalena per coppie",
        ObjectType.LUXURY_BEDDING: "Biancheria di lusso",
        ObjectType.MASSAGE_OIL_WARMER: "Scaldaolio massaggi",
        ObjectType.MATCHMAKING_KIOSK: "Chiosco incontri",
        ObjectType.MOOD_LIGHTING: "Luci atmosferiche",
        ObjectType.MUSIC_BOX: "Scatola musicale",
        ObjectType.PERFUME_ATOMIZER: "Atomizzatore profumo",
        ObjectType.PHEROMONE_DIFFUSER: "Diffusore feromoni",
        ObjectType.PILLOW_TALK_DEVICE: "Dispositivo intimità",
        ObjectType.PLUSH_ROBE: "Accappatoio di peluche",
        ObjectType.ROMANCE_NOVEL: "Romanzo rosa",
        ObjectType.ROMANTIC_BALCONY: "Balcone romantico",
        ObjectType.ROSE_PETAL_DISPENSER: "Erogatore petali",
        ObjectType.SCENTED_DRAWER_LINERS: "Fondini profumati",
        ObjectType.SEDUCTION_GAME: "Gioco di seduzione",
        ObjectType.SENSORY_DEPRIVATION_TANK: "Vasca sensoriale",
        ObjectType.SILK_SHEETS: "Lenzuola di seta",
        ObjectType.SKYLIGHT_BED: "Letto lucernario",
        ObjectType.SOUNDPROOF_WALL: "Parete fonoassorbente",
        ObjectType.SPICE_RACK_ADULT: "Portaspezie per adulti",
        ObjectType.STAGING_AREA: "Area di preparazione",
        ObjectType.STIMULATION_DEVICE: "Dispositivo stimolazione",
        ObjectType.TANTRIC_CHAIR: "Sedia tantrica",
        ObjectType.VELVET_ROPE: "Corda vellutata",
        ObjectType.VIBRATING_MAT: "Tappetino vibrante",
        ObjectType.VOYEUR_MIRROR: "Specchio voyeur",
        ObjectType.WEDDING_ARCH: "Arco nuziale",
        ObjectType.WINE_RACK: "Portabottiglie",
        
        # ================ OGGETTO GENERICO ================
        ObjectType.UNKNOWN_OBJECT: "Oggetto Sconosciuto"
    }
    return names.get(self, f"<Sconosciuto: {self.name}>")