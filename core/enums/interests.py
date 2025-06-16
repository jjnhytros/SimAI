# core/enums/interests.py
from enum import Enum, auto

from core.enums.genders import Gender
"""
Definizione dell'Enum Interest per gli interessi degli NPC.
Riferimento TODO: II.2.b, IV.3.b
"""

class Interest(Enum):
    ## --- Da categorizzare
    JOURNALING = auto()
    AUDIOBOOK_LISTENING = auto()


    """Enum per i diversi interessi e passioni degli NPC."""

    # --- Interessi Accademici / Conoscenza (30) ---
    HISTORY = auto()                # Storia e archeologia
    MEDICINE = auto()               # Medicina e salute
    PHILOSOPHY_DEBATE = auto()      # Filosofia e dibattito
    POLITICS = auto()               # Politica e attualità
    READING = auto()                # Lettura
    SCIENCE = auto()                # Scienza in generale
    TECHNOLOGY = auto()             # Tecnologia, robotica, IA
    MATHEMATICS = auto()            # Matematica e logica
    LINGUISTICS = auto()            # Studio delle lingue
    PSYCHOLOGY = auto()             # Psicologia umana
    ECONOMICS = auto()              # Economia e finanza
    LAW = auto()                    # Diritto e giurisprudenza
    EDUCATION = auto()              # Pedagogia e insegnamento
    ASTRONOMY = auto()              # Astronomia e spazio
    BIOLOGY = auto()                # Biologia e scienze naturali
    CHEMISTRY = auto()              # Chimica e materiali
    PHYSICS = auto()                # Fisica e meccanica
    GEOLOGY = auto()                # Geologia e scienze della Terra
    ANTHROPOLOGY = auto()           # Antropologia culturale
    SOCIOLOGY = auto()              # Sociologia e studi sociali
    ARCHAEOLOGY = auto()            # Archeologia e scavi
    ENGINEERING = auto()            # Ingegneria e progettazione
    COMPUTER_SCIENCE = auto()       # Informatica e programmazione
    ENVIRONMENTAL_SCIENCE = auto()  # Scienze ambientali
    NEUROSCIENCE = auto()           # Neuroscienze e cervello
    ROBOTICS = auto()               # Robotica e automazione
    ARTIFICIAL_INTELLIGENCE = auto()# Intelligenza artificiale
    CRYPTOGRAPHY = auto()           # Crittografia e sicurezza
    FUTUROLOGY = auto()             # Studio del futuro
    COGNITIVE_SCIENCE = auto()      # Scienze cognitive

    # --- Interessi Artistici e Culturali (40) ---
    ARCHITECTURE = auto()           # Architettura e design urbano
    FASHION = auto()                # Moda e design di abiti
    FILM_TV_THEATER = auto()        # Film, Serie TV e Teatro
    MUSIC_LISTENING = auto()        # Ascoltare musica
    MUSIC_PLAYING = auto()          # Suonare strumenti
    PAINTING = auto()               # Pittura
    PHOTOGRAPHY = auto()            # Fotografia
    VISUAL_ARTS = auto()            # Arti visive
    WRITING = auto()                # Scrittura
    SCULPTURE = auto()              # Scultura
    DANCE = auto()                  # Danza e coreografia
    OPERA = auto()                  # Opera lirica
    POETRY = auto()                 # Poesia
    CALLIGRAPHY = auto()            # Calligrafia
    GRAFFITI = auto()               # Graffiti e street art
    DIGITAL_ART = auto()            # Arte digitale
    POTTERY = auto()                # Ceramica
    THEATER_ACTING = auto()         # Recitazione teatrale
    MAGIC = auto()                  # Magia e illusionismo
    COMEDY = auto()                 # Commedia e umorismo
    STAND_UP = auto()               # Stand-up comedy
    CIRCUS_ARTS = auto()            # Arti circensi
    LITERATURE = auto()             # Letteratura
    GRAPHIC_DESIGN = auto()         # Graphic design
    INTERIOR_DESIGN = auto()        # Interior design
    ANIMATION = auto()              # Animazione
    CINEMATOGRAPHY = auto()         # Cinematografia
    ART_HISTORY = auto()            # Storia dell'arte
    MUSEUM_VISITING = auto()        # Visite museali
    ART_COLLECTING = auto()         # Collezionismo d'arte
    CULINARY_ARTS = auto()          # Arti culinarie
    JEWELRY_MAKING = auto()         # Creazione di gioielli
    WOOD_CARVING = auto()           # Intaglio del legno
    GLASSBLOWING = auto()           # Soffiatura del vetro
    METALWORKING = auto()           # Lavorazione dei metalli
    TEXTILE_ART = auto()            # Arte tessile
    PRINTMAKING = auto()            # Stampa artistica
    COLLAGE = auto()                # Collage
    PERFORMANCE_ART = auto()        # Arte performativa

    # --- Interessi Pratici / Hobby (40) ---
    BOARD_GAMES = auto()            # Giochi da tavolo
    COLLECTING = auto()             # Collezionismo
    COOKING_AND_FOOD = auto()       # Cucina e cibo
    CRAFTING = auto()               # Artigianato
    GAMING = auto()                 # Videogiochi
    GARDENING = auto()              # Giardinaggio
    TOYS_PLAYING = auto()           # Giocattoli
    WOODWORKING = auto()            # Falegnameria
    KNITTING = auto()               # Maglieria
    SEWING = auto()                 # Cucito
    MODEL_BUILDING = auto()         # Modellismo
    ELECTRONICS_TINKERING = auto()  # Elettronica
    HOME_IMPROVEMENT = auto()       # Fai da te casalingo
    CAR_MAINTENANCE = auto()        # Manutenzione auto
    FISHING = auto()                # Pesca
    HUNTING = auto()                # Caccia
    SURVIVAL_SKILLS = auto()        # Sopravvivenza
    SCRAPBOOKING = auto()           # Scrapbooking
    ORIGAMI = auto()                # Origami
    BREWING = auto()                # Produzione birra
    WINE_TASTING = auto()           # Degustazione vini
    BARBECUING = auto()             # Barbecue
    BAKING = auto()                 # Pasticceria
    CAKE_DECORATING = auto()        # Decorazione torte
    CANDLE_MAKING = auto()          # Produzione candele
    SOAP_MAKING = auto()            # Produzione saponi
    PERFUMERY = auto()              # Creazione profumi
    COMPOSTING = auto()             # Compostaggio
    BEEKEEPING = auto()             # Apicoltura
    AQUASCAPING = auto()            # Acquariofilia creativa
    LOCK_PICKING = auto()           # Scassinamento
    KNOT_TYING = auto()             # Nodi e cordame
    WHITTLING = auto()              # Intaglio del legno
    LEATHERWORKING = auto()         # Lavorazione cuoio
    BLACKSMITHING = auto()          # Forgiatura metalli
    URBAN_EXPLORATION = auto()      # Esplorazione urbana
    GEOCACHING = auto()             # Geocaching
    ASTROLOGY = auto()              # Astrologia
    TAROT = auto()                  # Lettura tarocchi

    # --- Interessi legati a Stile di Vita e Attività (50) ---
    ANIMALS = auto()                # Animali
    FITNESS_AND_WELLNESS = auto()   # Fitness e benessere
    NATURE_AND_OUTDOORS = auto()    # Natura ed escursioni
    SPORTS_PRACTICING = auto()      # Praticare sport
    SPORTS_WATCHING = auto()        # Seguire sport
    TRAVEL = auto()                 # Viaggi
    HIKING = auto()                 # Escursionismo
    CAMPING = auto()                # Campeggio
    CYCLING = auto()                # Ciclismo
    RUNNING = auto()                # Corsa
    SWIMMING = auto()               # Nuoto
    YOGA = auto()                   # Yoga
    MEDITATION = auto()             # Meditazione
    MARTIAL_ARTS = auto()           # Arti marziali
    SKIING = auto()                 # Sci
    SNOWBOARDING = auto()           # Snowboard
    SURFING = auto()                # Surf
    SKATING = auto()                # Pattinaggio
    CLIMBING = auto()               # Arrampicata
    PARAGLIDING = auto()            # Parapendio
    BIRD_WATCHING = auto()          # Birdwatching
    STARGAZING = auto()             # Osservazione stellare
    MINDFULNESS = auto()            # Consapevolezza
    PILATES = auto()                # Pilates
    CROSSFIT = auto()               # Crossfit
    WEIGHTLIFTING = auto()          # Sollevamento pesi
    PARKOUR = auto()                # Parkour
    CAVING = auto()                 # Speleologia
    KAYAKING = auto()               # Kayak
    ROCK_CLIMBING = auto()          # Arrampicata su roccia
    MOUNTAIN_BIKING = auto()        # Mountain bike
    SAILING = auto()                # Vela
    DIVING = auto()                 # Immersioni subacquee
    SNORKELING = auto()             # Snorkeling
    ZIPLINING = auto()              # Zip-line
    BUNGEE_JUMPING = auto()         # Bungee jumping
    PARASAILING = auto()            # Parasailing
    RAFTING = auto()                # Rafting
    MOTORSPORTS = auto()            # Motori
    HORSE_RIDING = auto()           # Equitazione
    DOG_TRAINING = auto()           # Addestramento cani
    BONSAI = auto()                 # Coltivazione bonsai
    FORAGING = auto()               # Raccolta piante selvatiche
    HERBALISM = auto()              # Erboristeria
    MINDFUL_EATING = auto()         # Alimentazione consapevole
    SLEEP_HYGIENE = auto()          # Igiene del sonno
    TEA_CEREMONY = auto()           # Cerimonia del tè
    FENG_SHUI = auto()              # Feng shui
    MINIMALISM = auto()             # Minimalismo
    ZERO_WASTE = auto()             # Rifiuti zero

    # --- Interessi Sociali (40) ---
    GOSSIP = auto()                 # Pettegolezzi
    MENTORING_AS_HOBBY = auto()     # Mentoring
    SOCIALIZING = auto()            # Socializzare
    SOCIAL_ACTIVISM = auto()        # Attivismo sociale
    NETWORKING = auto()             # Networking professionale
    COMMUNITY_SERVICE = auto()      # Servizio comunitario
    EVENT_PLANNING = auto()         # Organizzazione eventi
    BLOGGING = auto()               # Blogging
    VLOGGING = auto()               # Vlogging
    SOCIAL_MEDIA = auto()           # Social media
    PARENTING = auto()              # Genitorialità
    DATING = auto()                 # Appuntamenti
    LANGUAGE_EXCHANGE = auto()      # Scambio linguistico
    BOOK_CLUBS = auto()             # Club del libro
    DEBATE_CLUBS = auto()           # Club di dibattito
    VOLUNTEERING = auto()           # Volontariato
    FUNDRAISING = auto()            # Raccolta fondi
    POLITICAL_CAMPAIGNING = auto()  # Campagne politiche
    SUPPORT_GROUPS = auto()         # Gruppi di supporto
    CULTURAL_EXCHANGE = auto()      # Scambio culturale
    PEN_PALS = auto()               # Amici di penna
    FANDOM_COMMUNITIES = auto()     # Comunità di fan
    ONLINE_GAMING_COMMUNITIES = auto() # Comunità gaming
    COWORKING = auto()              # Coworking
    MEETUP_GROUPS = auto()          # Gruppi Meetup
    CLUB_MEMBERSHIPS = auto()       # Appartenenza a club
    NEIGHBORHOOD_WATCH = auto()     # Sorveglianza di quartiere
    PET_SITTING = auto()            # Pet sitting
    BABYSITTING = auto()            # Babysitting
    ELDERLY_CARE = auto()           # Cura anziani
    COMMUNITY_GARDENING = auto()    # Giardinaggio comunitario
    FOOD_BANKING = auto()           # Banche alimentari
    DISASTER_RELIEF = auto()        # Soccorso disastri
    ENVIRONMENTAL_ACTIVISM = auto() # Attivismo ambientale
    ANIMAL_RIGHTS = auto()          # Diritti animali
    HUMAN_RIGHTS = auto()           # Diritti umani
    PEACE_ACTIVISM = auto()         # Attivismo per la pace
    LOCAL_HISTORY_PRESERVATION = auto() # Preservazione storia locale
    GENEALOGY = auto()              # Genealogia

    def display_name_it(self, gender: 'Gender') -> str:
        """Restituisce un nome leggibile in italiano per l'interesse."""
        mapping = {
            # Da categorizzare
            Interest.JOURNALING: "Scrittura del diario",
            Interest.AUDIOBOOK_LISTENING: "Ascolto audiolibri",

            # Accademici (30)
            Interest.HISTORY: "Storia",
            Interest.MEDICINE: "Medicina",
            Interest.PHILOSOPHY_DEBATE: "Filosofia e Dibattito",
            Interest.POLITICS: "Politica",
            Interest.READING: "Lettura",
            Interest.SCIENCE: "Scienza",
            Interest.TECHNOLOGY: "Tecnologia",
            Interest.MATHEMATICS: "Matematica",
            Interest.LINGUISTICS: "Linguistica",
            Interest.PSYCHOLOGY: "Psicologia",
            Interest.ECONOMICS: "Economia",
            Interest.LAW: "Diritto",
            Interest.EDUCATION: "Educazione",
            Interest.ASTRONOMY: "Astronomia",
            Interest.BIOLOGY: "Biologia",
            Interest.CHEMISTRY: "Chimica",
            Interest.PHYSICS: "Fisica",
            Interest.GEOLOGY: "Geologia",
            Interest.ANTHROPOLOGY: "Antropologia",
            Interest.SOCIOLOGY: "Sociologia",
            Interest.ARCHAEOLOGY: "Archeologia",
            Interest.ENGINEERING: "Ingegneria",
            Interest.COMPUTER_SCIENCE: "Informatica",
            Interest.ENVIRONMENTAL_SCIENCE: "Scienze Ambientali",
            Interest.NEUROSCIENCE: "Neuroscienze",
            Interest.ROBOTICS: "Robotica",
            Interest.ARTIFICIAL_INTELLIGENCE: "Intelligenza Artificiale",
            Interest.CRYPTOGRAPHY: "Critografia",
            Interest.FUTUROLOGY: "Futurologia",
            Interest.COGNITIVE_SCIENCE: "Scienze Cognitive",

            # Artistici e Culturali (40)
            Interest.ARCHITECTURE: "Architettura",
            Interest.FASHION: "Moda",
            Interest.FILM_TV_THEATER: "Film, TV e Teatro",
            Interest.MUSIC_LISTENING: "Ascoltare Musica",
            Interest.MUSIC_PLAYING: "Suonare Strumenti",
            Interest.PAINTING: "Pittura",
            Interest.PHOTOGRAPHY: "Fotografia",
            Interest.VISUAL_ARTS: "Arti Visive",
            Interest.WRITING: "Scrittura",
            Interest.SCULPTURE: "Scultura",
            Interest.DANCE: "Danza",
            Interest.OPERA: "Opera Lirica",
            Interest.POETRY: "Poesia",
            Interest.CALLIGRAPHY: "Calligrafia",
            Interest.GRAFFITI: "Graffiti e Street Art",
            Interest.DIGITAL_ART: "Arte Digitale",
            Interest.POTTERY: "Ceramica",
            Interest.THEATER_ACTING: "Recitazione Teatrale",
            Interest.MAGIC: "Magia e Illusionismo",
            Interest.COMEDY: "Commedia",
            Interest.STAND_UP: "Stand-up Comedy",
            Interest.CIRCUS_ARTS: "Arti Circensi",
            Interest.LITERATURE: "Letteratura",
            Interest.GRAPHIC_DESIGN: "Graphic Design",
            Interest.INTERIOR_DESIGN: "Interior Design",
            Interest.ANIMATION: "Animazione",
            Interest.CINEMATOGRAPHY: "Cinematografia",
            Interest.ART_HISTORY: "Storia dell'Arte",
            Interest.MUSEUM_VISITING: "Visite Museali",
            Interest.ART_COLLECTING: "Collezionismo d'Arte",
            Interest.CULINARY_ARTS: "Arti Culinarie",
            Interest.JEWELRY_MAKING: "Creazione Gioielli",
            Interest.WOOD_CARVING: "Intaglio del Legno",
            Interest.GLASSBLOWING: "Soffiatura del Vetro",
            Interest.METALWORKING: "Lavorazione Metalli",
            Interest.TEXTILE_ART: "Arte Tessile",
            Interest.PRINTMAKING: "Stampa Artistica",
            Interest.COLLAGE: "Collage",
            Interest.PERFORMANCE_ART: "Arte Performativa",

            # Pratici / Hobby (40)
            Interest.BOARD_GAMES: "Giochi da Tavolo",
            Interest.COLLECTING: "Collezionismo",
            Interest.COOKING_AND_FOOD: "Cucina e Cibo",
            Interest.CRAFTING: "Artigianato",
            Interest.GAMING: "Gaming",
            Interest.GARDENING: "Giardinaggio",
            Interest.TOYS_PLAYING: "Giocare con Giocattoli",
            Interest.WOODWORKING: "Falegnameria",
            Interest.KNITTING: "Maglieria",
            Interest.SEWING: "Cucito",
            Interest.MODEL_BUILDING: "Modellismo",
            Interest.ELECTRONICS_TINKERING: "Elettronica",
            Interest.HOME_IMPROVEMENT: "Fai da Te Casalingo",
            Interest.CAR_MAINTENANCE: "Manutenzione Auto",
            Interest.FISHING: "Pesca",
            Interest.HUNTING: "Caccia",
            Interest.SURVIVAL_SKILLS: "Sopravvivenza",
            Interest.SCRAPBOOKING: "Scrapbooking",
            Interest.ORIGAMI: "Origami",
            Interest.BREWING: "Produzione Birra",
            Interest.WINE_TASTING: "Degustazione Vini",
            Interest.BARBECUING: "Barbecue",
            Interest.BAKING: "Pasticceria",
            Interest.CAKE_DECORATING: "Decorazione Torte",
            Interest.CANDLE_MAKING: "Produzione Candele",
            Interest.SOAP_MAKING: "Produzione Saponi",
            Interest.PERFUMERY: "Creazione Profumi",
            Interest.COMPOSTING: "Compostaggio",
            Interest.BEEKEEPING: "Apicoltura",
            Interest.AQUASCAPING: "Acquariofilia Creativa",
            Interest.LOCK_PICKING: "Scassinamento",
            Interest.KNOT_TYING: "Nodi e Cordame",
            Interest.WHITTLING: "Intaglio del Legno",
            Interest.LEATHERWORKING: "Lavorazione Cuoio",
            Interest.BLACKSMITHING: "Forgiatura Metalli",
            Interest.URBAN_EXPLORATION: "Esplorazione Urbana",
            Interest.GEOCACHING: "Geocaching",
            Interest.ASTROLOGY: "Astrologia",
            Interest.TAROT: "Lettura Tarocchi",

            # Stile di Vita e Attività (50)
            Interest.ANIMALS: "Animali",
            Interest.FITNESS_AND_WELLNESS: "Fitness e Benessere",
            Interest.NATURE_AND_OUTDOORS: "Natura ed Escursioni",
            Interest.SPORTS_PRACTICING: "Praticare Sport",
            Interest.SPORTS_WATCHING: "Seguire Sport",
            Interest.TRAVEL: "Viaggi",
            Interest.HIKING: "Escursionismo",
            Interest.CAMPING: "Campeggio",
            Interest.CYCLING: "Ciclismo",
            Interest.RUNNING: "Corsa",
            Interest.SWIMMING: "Nuoto",
            Interest.YOGA: "Yoga",
            Interest.MEDITATION: "Meditazione",
            Interest.MARTIAL_ARTS: "Arti Marziali",
            Interest.SKIING: "Sci",
            Interest.SNOWBOARDING: "Snowboard",
            Interest.SURFING: "Surf",
            Interest.SKATING: "Pattinaggio",
            Interest.CLIMBING: "Arrampicata",
            Interest.PARAGLIDING: "Parapendio",
            Interest.BIRD_WATCHING: "Birdwatching",
            Interest.STARGAZING: "Osservazione Stellare",
            Interest.MINDFULNESS: "Consapevolezza",
            Interest.PILATES: "Pilates",
            Interest.CROSSFIT: "Crossfit",
            Interest.WEIGHTLIFTING: "Sollevamento Pesi",
            Interest.PARKOUR: "Parkour",
            Interest.CAVING: "Speleologia",
            Interest.KAYAKING: "Kayak",
            Interest.ROCK_CLIMBING: "Arrampicata su Roccia",
            Interest.MOUNTAIN_BIKING: "Mountain Bike",
            Interest.SAILING: "Vela",
            Interest.DIVING: "Immersione Subacquea",
            Interest.SNORKELING: "Snorkeling",
            Interest.ZIPLINING: "Zip-line",
            Interest.BUNGEE_JUMPING: "Bungee Jumping",
            Interest.PARASAILING: "Parasailing",
            Interest.RAFTING: "Rafting",
            Interest.MOTORSPORTS: "Motori",
            Interest.HORSE_RIDING: "Equitazione",
            Interest.DOG_TRAINING: "Addestramento Cani",
            Interest.BONSAI: "Coltivazione Bonsai",
            Interest.FORAGING: "Raccolta Piante Selvatiche",
            Interest.HERBALISM: "Erboristeria",
            Interest.MINDFUL_EATING: "Alimentazione Consapevole",
            Interest.SLEEP_HYGIENE: "Igiene del Sonno",
            Interest.TEA_CEREMONY: "Cerimonia del Tè",
            Interest.FENG_SHUI: "Feng Shui",
            Interest.MINIMALISM: "Minimalismo",
            Interest.ZERO_WASTE: "Rifiuti Zero",

            # Sociali (40)
            Interest.GOSSIP: "Pettegolezzi",
            Interest.MENTORING_AS_HOBBY: "Fare da Mentore",
            Interest.SOCIALIZING: "Socializzare",
            Interest.SOCIAL_ACTIVISM: "Attivismo Sociale",
            Interest.NETWORKING: "Networking Professionale",
            Interest.COMMUNITY_SERVICE: "Servizio Comunitario",
            Interest.EVENT_PLANNING: "Organizzazione Eventi",
            Interest.BLOGGING: "Blogging",
            Interest.VLOGGING: "Vlogging",
            Interest.SOCIAL_MEDIA: "Social Media",
            Interest.PARENTING: "Genitorialità",
            Interest.DATING: "Appuntamenti",
            Interest.LANGUAGE_EXCHANGE: "Scambio Linguistico",
            Interest.BOOK_CLUBS: "Club del Libro",
            Interest.DEBATE_CLUBS: "Club di Dibattito",
            Interest.VOLUNTEERING: "Volontariato",
            Interest.FUNDRAISING: "Raccolta Fondi",
            Interest.POLITICAL_CAMPAIGNING: "Campagne Politiche",
            Interest.SUPPORT_GROUPS: "Gruppi di Supporto",
            Interest.CULTURAL_EXCHANGE: "Scambio Culturale",
            Interest.PEN_PALS: "Amici di Penna",
            Interest.FANDOM_COMMUNITIES: "Comunità di Fan",
            Interest.ONLINE_GAMING_COMMUNITIES: "Comunità Gaming",
            Interest.COWORKING: "Coworking",
            Interest.MEETUP_GROUPS: "Gruppi Meetup",
            Interest.CLUB_MEMBERSHIPS: "Appartenenza a Club",
            Interest.NEIGHBORHOOD_WATCH: "Sorveglianza di Quartiere",
            Interest.PET_SITTING: "Pet Sitting",
            Interest.BABYSITTING: "Babysitting",
            Interest.ELDERLY_CARE: "Cura Anziani",
            Interest.COMMUNITY_GARDENING: "Giardinaggio Comunitario",
            Interest.FOOD_BANKING: "Banche Alimentari",
            Interest.DISASTER_RELIEF: "Soccorso Disastri",
            Interest.ENVIRONMENTAL_ACTIVISM: "Attivismo Ambientale",
            Interest.ANIMAL_RIGHTS: "Diritti Animali",
            Interest.HUMAN_RIGHTS: "Diritti Umani",
            Interest.PEACE_ACTIVISM: "Attivismo per la Pace",
            Interest.LOCAL_HISTORY_PRESERVATION: "Preservazione Storia Locale",
            Interest.GENEALOGY: "Genealogia",
        }
        return mapping.get(self, self.name.replace("_", " ").title())
