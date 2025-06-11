# core/enums/fun_activity_types.py
from enum import Enum, auto

from core.enums.genders import Gender
"""
Definizione dell'Enum FunActivityType per le attività di svago degli NPC.
Questa è una versione fusa e dettagliata.
"""

class FunActivityType(Enum):
    """
    Enum per le diverse attività di svago (hobby, divertimento) che un NPC può compiere.
    """

    DANCE = auto()
    PRACTICE_PUBLIC_SPEAKING = auto()
    BROWSE_SOCIAL_MEDIA = auto()
    VISIT_MUSEUM = auto()
    DRINK_COFFEE = auto()

    # --- Attività Creative e Artigianali (Specifiche) ---
    PAINT = auto()
    PLAY_GUITAR = auto()
    PLAY_PIANO = auto()
    PLAY_VIOLIN = auto()
    SING = auto()
    WRITE_BOOK_FOR_FUN = auto()
    DJ_MIXING = auto()
    PHOTOGRAPHY = auto()
    KNITTING = auto()
    POTTERY = auto()
    WOODWORKING = auto()
    DIGITAL_ART = auto()
    SCULPTING = auto()
    PHOTO_EDITING = auto()
    CALLIGRAPHY = auto()
    JEWELRY_MAKING = auto()
    UPHOLSTERY = auto()
    GAME_DESIGN = auto()
    COMIC_DRAWING = auto()
    COSTUME_DESIGN = auto()
    GRAFFITI_ART = auto()
    ANIMATION = auto()
    LEATHERWORKING = auto()
    MODEL_BUILDING = auto()
    STENCIL_ART = auto()
    SONGWRITING = auto()
    POETRY = auto()
    FURNITURE_RESTORATION = auto()
    BEADWORK = auto()
    ORIGAMI = auto()
    BOTANICAL_ILLUSTRATION = auto()
    CERAMIC_GLAZING = auto()
    PUPPET_MAKING = auto()
    GLASS_ETCHING = auto()
    TEXTILE_DESIGN = auto()
    COSPLAY_CRAFTING = auto()

    # --- Attività Intellettuali / tranquille ---
    READ_BOOK_FOR_FUN = auto()
    PLAY_CHESS = auto()
    DO_CROSSWORD_PUZZLE = auto()
    RESEARCH_INTEREST_ONLINE = auto()
    DAYDREAM = auto()
    WATCH_CLOUDS = auto()
    PEOPLE_WATCH = auto()
    MEDITATE = auto()
    STUDY_PHILOSOPHY = auto()
    LEARN_LANGUAGE = auto()
    ASTRONOMY_OBSERVATION = auto()
    JOURNALING = auto()
    SUDOKU = auto()
    TAROT_READING = auto()
    BIRD_WATCHING = auto()
    GENEALOGY_RESEARCH = auto()
    PUZZLE_SOLVING = auto()
    ASTROLOGY_STUDY = auto()
    MINDFULNESS_PRACTICE = auto()
    STARGAZING = auto()
    CHEMISTRY_EXPERIMENTS = auto()
    BOTANY_STUDY = auto()
    HISTORY_DOCUMENTARY = auto()
    MAP_STUDY = auto()
    MEMORY_TRAINING = auto()
    PHILOSOPHICAL_DEBATE = auto()
    ECONOMICS_ANALYSIS = auto()
    PSYCHOLOGY_STUDY = auto()
    ARCHITECTURE_STUDY = auto()
    CRYPTOGRAPHY = auto()
    STRATEGY_GAME_SOLO = auto()
    MYTHOLOGY_STUDY = auto()
    POETRY_ANALYSIS = auto()
    AI_PROGRAMMING = auto()

    # --- Attività all'Aperto / Fisiche ---
    GO_FOR_A_JOG = auto()
    JOG_IN_PLACE = auto()
    GO_HIKING = auto()
    SWIMMING = auto()
    GARDENING = auto()
    FISHING = auto()
    PLAY_SPORTS_CASUAL = auto()
    EXPLORE_NEIGHBORHOOD = auto()

    # --- Attività sportive e outdoor (già presenti) ---
    ROCK_CLIMBING = auto()
    MOUNTAIN_BIKING = auto()
    SURFING = auto()
    KAYAKING = auto()
    ARCHERY = auto()
    PARKOUR = auto()
    SKATEBOARDING = auto()
    BEACH_VOLLEYBALL = auto()
    DISC_GOLF = auto()
    ORIENTEERING = auto()
    GEOCACHING = auto()
    TREE_CLIMBING = auto()
    SNOWSHOEING = auto()
    STARGAZING_HIKE = auto()
    BIRDING = auto()
    FOREST_BATHING = auto()
    NATURE_PHOTOGRAPHY = auto()
    BOTANICAL_FORAGING = auto()
    ROCK_HUNTING = auto()
    WATERFALL_EXPLORATION = auto()
    CAVING = auto()
    STANDUP_PADDLEBOARD = auto()
    ICE_SKATING = auto()
    SNOWBALL_FIGHT = auto()
    FRISBEE_GOLF = auto()
    CANYONING = auto()
    URBAN_EXPLORATION = auto()
    STONE_SKIPPING = auto()
    SUNRISE_YOGA = auto()

    # --- Attività domestiche e media (già presenti) ---
    WATCH_TV = auto()
    COOKING_SHOW = auto()
    PODCAST_LISTENING = auto()
    VIRTUAL_TOUR = auto()
    HOME_BAKING = auto()
    AQUARIUM_WATCHING = auto()
    HOME_BREWING = auto()
    PUZZLE_ASSEMBLY = auto()
    MODEL_TRAIN_SETUP = auto()
    HOME_DECORATING = auto()
    CANDLE_MAKING = auto()
    SOAP_CRAFTING = auto()
    INDOOR_GARDENING = auto()
    TERRARIUM_BUILDING = auto()
    HOME_WINE_TASTING = auto()
    VIRTUAL_CONCERT = auto()
    FAMILY_HISTORY_ALBUM = auto()
    HOME_SPA = auto()
    AUDIOBOOK_LISTENING = auto()
    INDOOR_PICNIC = auto()
    CHEESE_TASTING = auto()
    HOME_IMPROVEMENT = auto()
    INDOOR_CAMPING = auto()
    TEA_CEREMONY = auto()
    HOME_KARAOKE = auto()
    BATH_BOOK_READING = auto()
    HOME_ESCAPE_ROOM = auto()
    BALLOON_ART = auto()
    VIRTUAL_TRAVEL = auto()

    # --- Attività sociali e in città (già presenti) ---
    GO_TO_BAR = auto()
    COMEDY_CLUB = auto()
    ART_GALLERY_TOUR = auto()
    THEATER_PERFORMANCE = auto()
    KARAOKE_NIGHT = auto()
    FOOD_TRUCK_FESTIVAL = auto()
    STREET_PERFORMANCE = auto()
    PUB_QUIZ = auto()
    DANCE_CLUB = auto()
    BOARD_GAME_CAFE = auto()
    FARMERS_MARKET = auto()
    POETRY_SLAM = auto()
    CITY_PHOTO_WALK = auto()
    ARCADE_NIGHT = auto()
    LIVE_MUSIC_VENUE = auto()
    SPEED_DATING = auto()
    THEME_PARK = auto()
    STREET_FOOD_TOUR = auto()
    CITY_SCAVENGER_HUNT = auto()
    FESTIVAL_ATTENDANCE = auto()
    IMPROV_WORKSHOP = auto()
    MURDER_MYSTERY_DINNER = auto()
    ESCAPE_ROOM_CHALLENGE = auto()
    CITY_BIKE_TOUR = auto()
    STREET_ART_TOUR = auto()
    FOOD_COURT_SAMPLING = auto()
    NIGHT_MARKET = auto()
    ROOFTOP_BAR = auto()
    BOAT_PARTY = auto()
    LISTEN_TO_LIVE_JAZZ = auto()
    PERFORM_JAZZ = auto()
    PERFORM_ON_STREET=auto()
    JUMP_ON_BENCH = auto()
    
    # --- Attività romantiche e sensuali (già presenti) ---
    SUNSET_PICNIC = auto()
    COUPLES_MASSAGE = auto()
    CANDLELIGHT_DINNER = auto()
    STARGAZING_DATE = auto()
    SENSUAL_DANCE = auto()
    LOVE_LETTER_WRITING = auto()
    HOT_SPRINGS_VISIT = auto()
    TANGO_LESSONS = auto()
    CHOCOLATE_TASTING = auto()
    PRIVATE_WINE_CELLAR = auto()
    COUPLES_ART_CLASS = auto()
    MOONLIGHT_SWIM = auto()
    AROMATHERAPY_SESSION = auto()
    DOUBLE_MASSAGE = auto()
    PRIVATE_DANCE = auto()
    KISSING_CONTEST = auto()
    ROLEPLAYING_GAME = auto()
    SILK_ROBES_EVENING = auto()
    EROTIC_STORYTELLING = auto()
    SCENT_CREATION = auto()
    FANTASY_ROLEPLAY = auto()
    MASSAGE_OIL_MAKING = auto()
    INTIMATE_GAME_NIGHT = auto()
    SENSUAL_FEEDING = auto()
    TANTRIC_BREATHWORK = auto()
    LINGERIE_SHOPPING = auto()
    LOVE_POETRY_READING = auto()
    COUPLES_YOGA = auto()
    SENSUAL_COOKING = auto()
    AFTERGLOW_CUDDLING = auto()
    PRIVATE_CONCERT = auto()
    EROTIC_PHOTOGRAPHY = auto()

    def display_name_it(self, gender: 'Gender') -> str:
        """
        Restituisce un nome leggibile per l'attività.
        La firma accetta 'gender' per coerenza.
        """
        mapping = {
        # Attività Creative e Artigianali
        FunActivityType.PAINT: "Dipingere",
        FunActivityType.PLAY_GUITAR: "Suonare la Chitarra",
        FunActivityType.PLAY_PIANO: "Suonare il Pianoforte",
        FunActivityType.PLAY_VIOLIN: "Suonare il Violino",
        FunActivityType.SING: "Cantare",
        FunActivityType.WRITE_BOOK_FOR_FUN: "Scrivere per Piacere",
        FunActivityType.DJ_MIXING: "Fare il DJ",
        FunActivityType.PHOTOGRAPHY: "Fotografare",
        FunActivityType.KNITTING: "Lavorare a Maglia",
        FunActivityType.POTTERY: "Lavorare la Ceramica",
        FunActivityType.WOODWORKING: "Lavorare il Legno",
        FunActivityType.DIGITAL_ART: "Arte Digitale",
        FunActivityType.SCULPTING: "Scolpire",
        FunActivityType.PHOTO_EDITING: "Modificare Foto",
        FunActivityType.CALLIGRAPHY: "Calligrafia",
        FunActivityType.JEWELRY_MAKING: "Creare Gioielli",
        FunActivityType.UPHOLSTERY: "Tappezzeria",
        FunActivityType.GAME_DESIGN: "Progettare Giochi",
        FunActivityType.COMIC_DRAWING: "Disegnare Fumetti",
        FunActivityType.COSTUME_DESIGN: "Design di Costumi",
        FunActivityType.GRAFFITI_ART: "Arte di Gaffiti",
        FunActivityType.ANIMATION: "Animazione",
        FunActivityType.LEATHERWORKING: "Lavorare la Pelle",
        FunActivityType.MODEL_BUILDING: "Costruire Modelli",
        FunActivityType.STENCIL_ART: "Arte con Stencil",
        FunActivityType.SONGWRITING: "Scrivere Canzoni",
        FunActivityType.POETRY: "Scrivere Poesie",
        FunActivityType.FURNITURE_RESTORATION: "Restauro di Mobili",
        FunActivityType.BEADWORK: "Lavorare con Perline",
        FunActivityType.ORIGAMI: "Origami",
        FunActivityType.BOTANICAL_ILLUSTRATION: "Illustrazione Botanica",
        FunActivityType.CERAMIC_GLAZING: "Smaltatura di Ceramiche",
        FunActivityType.PUPPET_MAKING: "Realizzare Burattini",
        FunActivityType.GLASS_ETCHING: " Incisione su Vetro",
        FunActivityType.TEXTILE_DESIGN: "Design Tessile",
        FunActivityType.COSPLAY_CRAFTING: "Realizzazione Cosplay",

        # Attività Intellettuali e tranquille
        FunActivityType.READ_BOOK_FOR_FUN: "Leggere per Piacere",
        FunActivityType.PLAY_CHESS: "Giocare a Scacchi",
        FunActivityType.DO_CROSSWORD_PUZZLE: "Risolvere Parole Crociate",
        FunActivityType.RESEARCH_INTEREST_ONLINE: "Ricercare online",
        FunActivityType.DAYDREAM: "Sognare ad occhi aperti",
        FunActivityType.WATCH_CLOUDS: "Guardare le Nuvole",
        FunActivityType.PEOPLE_WATCH: "Osservare la gente",
        FunActivityType.MEDITATE: "Meditare",

        # Attività all'Aperto / Fisiche
        FunActivityType.GO_FOR_A_JOG: "Fare jogging",
        FunActivityType.JOG_IN_PLACE: "Corsa sul posto",
        FunActivityType.GO_HIKING: "Escursionismo",
        FunActivityType.SWIMMING: "Nuotare",
        FunActivityType.GARDENING: "Giardinaggio",
        FunActivityType.FISHING: "Pescare",
        FunActivityType.PLAY_SPORTS_CASUAL: "Sport informali",
        FunActivityType.EXPLORE_NEIGHBORHOOD: "Esplorare il quartiere",

        # Attività sportive e outdoor (già presenti)
        FunActivityType.ROCK_CLIMBING: "Arrampicata su roccia",
        FunActivityType.MOUNTAIN_BIKING: "Mountain biking",
        FunActivityType.SURFING: "Surf",
        FunActivityType.KAYAKING: "Kayak",
        FunActivityType.ARCHERY: "Tiro con l'arco",
        FunActivityType.PARKOUR: "Parkour",
        FunActivityType.SKATEBOARDING: "Skateboard",
        FunActivityType.BEACH_VOLLEYBALL: "Beach volley",
        FunActivityType.DISC_GOLF: "Disc golf",
        FunActivityType.ORIENTEERING: "Orientamento",
        FunActivityType.GEOCACHING: "Geocaching",
        FunActivityType.TREE_CLIMBING: "Arrampicata sugli alberi",
        FunActivityType.SNOWSHOEING: "ciaspolata",
        FunActivityType.STARGAZING_HIKE: "Escursione notturna",
        FunActivityType.BIRDING: "Birdwatching",
        FunActivityType.FOREST_BATHING: "Bagno nella foresta",
        FunActivityType.NATURE_PHOTOGRAPHY: "Fotografia naturalistica",
        FunActivityType.BOTANICAL_FORAGING: "Foraging botanico",
        FunActivityType.ROCK_HUNTING: "Caccia alle rocce",
        FunActivityType.WATERFALL_EXPLORATION: "Esplorazione di cascate",
        FunActivityType.CAVING: "Speleologia",
        FunActivityType.STANDUP_PADDLEBOARD: "Stand Up Paddle",
        FunActivityType.ICE_SKATING: " Pattinaggio su ghiaccio",
        FunActivityType.SNOWBALL_FIGHT: "Battaglia di palle di neve",
        FunActivityType.FRISBEE_GOLF: "Golf con frisbee",
        FunActivityType.CANYONING: "Canyoning",
        FunActivityType.URBAN_EXPLORATION: "Esplorazione urbana",
        FunActivityType.STONE_SKIPPING: "Lancio di pietre",
        FunActivityType.SUNRISE_YOGA: "Yoga all'alba",

        # Attività domestiche e media
        FunActivityType.WATCH_TV: "Guardare la TV",
        FunActivityType.COOKING_SHOW: "Programma di cucina",
        FunActivityType.PODCAST_LISTENING: "Ascoltare podcast",
        FunActivityType.VIRTUAL_TOUR: "Tour virtuale",
        FunActivityType.HOME_BAKING: "Fare dolci a casa",
        FunActivityType.AQUARIUM_WATCHING: "Guardare l'acquario",
        FunActivityType.HOME_BREWING: "Produrre birra casalinga",
        FunActivityType.PUZZLE_ASSEMBLY: "Assemblare puzzle",
        FunActivityType.MODEL_TRAIN_SETUP: "Configurare trenini in scala",
        FunActivityType.HOME_DECORATING: "Decorare casa",
        FunActivityType.CANDLE_MAKING: "Fare candele",
        FunActivityType.SOAP_CRAFTING: "Fare saponi",
        FunActivityType.INDOOR_GARDENING: "Giardinaggio indoor",
        FunActivityType.TERRARIUM_BUILDING: "Costruire terrari",
        FunActivityType.HOME_WINE_TASTING: "Degustazione di vini casalinga",
        FunActivityType.VIRTUAL_CONCERT: "Concerto virtuale",
        FunActivityType.FAMILY_HISTORY_ALBUM: "Album di storia familiare",
        FunActivityType.HOME_SPA: "Spa casalingo",
        FunActivityType.AUDIOBOOK_LISTENING: "Ascoltare audiolibri",
        FunActivityType.INDOOR_PICNIC: "Picnic al chiuso",
        FunActivityType.CHEESE_TASTING: "Degustazione di formaggi",
        FunActivityType.HOME_IMPROVEMENT: "Miglioramenti domestici",
        FunActivityType.INDOOR_CAMPING: "Camping indoor",
        FunActivityType.TEA_CEREMONY: "Cerimonia del tè",
        FunActivityType.HOME_KARAOKE: "Karaoke a casa",
        FunActivityType.BATH_BOOK_READING: "Lettura in vasca",
        FunActivityType.HOME_ESCAPE_ROOM: "Escape room casalinga",
        FunActivityType.BALLOON_ART: "Arte con palloncini",
        FunActivityType.VIRTUAL_TRAVEL: "Viaggi virtuali",

        # Attività sociali e in città
        FunActivityType.GO_TO_BAR: "Andare al bar",
        FunActivityType.COMEDY_CLUB: "Club di cabaret",
        FunActivityType.ART_GALLERY_TOUR: "Tour in galleria d'arte",
        FunActivityType.THEATER_PERFORMANCE: "Spettacolo teatrale",
        FunActivityType.KARAOKE_NIGHT: "Serata karaoke",
        FunActivityType.FOOD_TRUCK_FESTIVAL: "Festival di food truck",
        FunActivityType.STREET_PERFORMANCE: "Spettacolo di strada",
        FunActivityType.PUB_QUIZ: "Quiz al pub",
        FunActivityType.DANCE_CLUB: "Club di ballo",
        FunActivityType.BOARD_GAME_CAFE: "Caffè giochi da tavolo",
        FunActivityType.FARMERS_MARKET: "Mercato degli agricoltori",
        FunActivityType.POETRY_SLAM: "Slampo di poesia",
        FunActivityType.CITY_PHOTO_WALK: "Passeggiata fotografica in città",
        FunActivityType.ARCADE_NIGHT: "Serata arcade",
        FunActivityType.LIVE_MUSIC_VENUE: "Luogo di musica dal vivo",
        FunActivityType.SPEED_DATING: "Appuntamenti veloci",
        FunActivityType.THEME_PARK: "Parco a tema",
        FunActivityType.STREET_FOOD_TOUR: "Tour di street food",
        FunActivityType.CITY_SCAVENGER_HUNT: "Caccia al tesoro urbana",
        FunActivityType.FESTIVAL_ATTENDANCE: "Partecipare a festival",
        FunActivityType.IMPROV_WORKSHOP: "Workshop di improvvisazione",
        FunActivityType.MURDER_MYSTERY_DINNER: "Cena con mistero da uccidere",
        FunActivityType.ESCAPE_ROOM_CHALLENGE: "Sfida in escape room",
        FunActivityType.CITY_BIKE_TOUR: "Tour in bici in città",
        FunActivityType.STREET_ART_TOUR: "Tour di street art",
        FunActivityType.FOOD_COURT_SAMPLING: "Assaggi in food court",
        FunActivityType.NIGHT_MARKET: "Mercato notturno",
        FunActivityType.ROOFTOP_BAR: "Bar sul tetto",
        FunActivityType.BOAT_PARTY: "Festa in barca",
        FunActivityType.JUMP_ON_BENCH: "Saltare sulla panchina",
        

        # Attività romantiche e sensuali
        FunActivityType.SUNSET_PICNIC: "Picnic al tramonto",
        FunActivityType.COUPLES_MASSAGE: "Massaggio di coppia",
        FunActivityType.CANDLELIGHT_DINNER: "Cena a lume di candela",
        FunActivityType.STARGAZING_DATE: "Appuntamento ad osservare le stelle",
        FunActivityType.SENSUAL_DANCE: "Danza sensuale",
        FunActivityType.LOVE_LETTER_WRITING: "Scrivere lettere d’amore",
        FunActivityType.HOT_SPRINGS_VISIT: "Visita alle sorgenti calde",
        FunActivityType.TANGO_LESSONS: "Lezioni di tango",
        FunActivityType.CHOCOLATE_TASTING: "Degustazione di cioccolato",
        FunActivityType.PRIVATE_WINE_CELLAR: "Cantina privata",
        FunActivityType.COUPLES_ART_CLASS: "Corso d’arte di coppia",
        FunActivityType.MOONLIGHT_SWIM: "Bagno sotto la luna",
        FunActivityType.AROMATHERAPY_SESSION: "Sessione di aromaterapia",
        FunActivityType.DOUBLE_MASSAGE: "Massaggio doppio",
        FunActivityType.PRIVATE_DANCE: "Danza privata",
        FunActivityType.KISSING_CONTEST: "Concorso di baci",
        FunActivityType.ROLEPLAYING_GAME: "Gioco di ruolo",
        FunActivityType.SILK_ROBES_EVENING: "Serata in raso",
        FunActivityType.EROTIC_STORYTELLING: "Racconti erotici",
        FunActivityType.SCENT_CREATION: "Creazione di profumi",
        FunActivityType.FANTASY_ROLEPLAY: "Gioco di ruolo fantasy",
        FunActivityType.MASSAGE_OIL_MAKING: "Creare olio per massaggi",
        FunActivityType.INTIMATE_GAME_NIGHT: "Serata di giochi intimi",
        FunActivityType.SENSUAL_FEEDING: "Cibo sensuale",
        FunActivityType.TANTRIC_BREATHWORK: "Respirazione tantrica",
        FunActivityType.LINGERIE_SHOPPING: "Shopping di lingerie",
        FunActivityType.LOVE_POETRY_READING: "Lettura di poesia d’amore"
        }
        value = mapping.get(self)

        if isinstance(value, dict):
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            return value
        else:
            return self.name.replace("_", " ").title()
