# core/enums/aspiration_types.py
from enum import Enum, auto

from core.enums.genders import Gender
"""
Definizione dell'Enum AspirationType per gli obiettivi a lungo termine degli NPC,
basato sulla fusione delle liste fornite.
Riferimento TODO: IV.3.a
"""

class AspirationType(Enum):
    """Enum per le diverse aspirazioni di vita degli NPC."""

    # --- Categoria: Creatività ---
    BESTSELLING_AUTHOR = auto()
    MASTER_ARTISAN = auto()
    MASTER_PAINTER = auto()
    RENOWNED_MUSICIAN = auto()
    AWARD_WINNING_DIRECTOR = auto()
    BROADWAY_STAR = auto()
    DIGITAL_ART_PIONEER = auto()
    FASHION_DESIGN_ICON = auto()
    GRAFFITI_LEGEND = auto()
    INSTRUMENT_VIRTUOSO = auto()
    POET_LAUREATE = auto()
    SCULPTURE_MASTER = auto()
    STREET_PERFORMER_ICON = auto()
    TATTOO_ARTIST_EXTRAORDINAIRE = auto()
    WORLD_FAMOUS_DJ = auto()

    # --- Categoria: Conoscenza ---
    ACADEMIC_EXCELLENCE = auto()
    LOREMASTER_OF_ANTHALYS = auto()
    SCIENTIFIC_BREAKTHROUGH = auto()
    SKILL_MASTER = auto()
    SKILL_POLYGLOT = auto()
    KNOWLEDGE_SEEKER = auto()
    ARCHAEOLOGY_EXPERT = auto()
    ASTROLOGY_MASTER = auto()
    CODING_GURU = auto()
    HISTORICAL_RESEARCHER = auto()
    LANGUAGE_AMBASSADOR = auto()
    MATH_GENIUS = auto()
    PHILOSOPHY_SCHOLAR = auto()
    QUANTUM_PHYSICIST = auto()
    ROBOTICS_INNOVATOR = auto()

    # --- Categoria: Fortuna ---
    FABULOUSLY_WEALTHY = auto()
    MANSION_BARON = auto()
    BUSINESS_TYCOON = auto()
    CRYPTO_MILLIONAIRE = auto()
    ESTATE_MAGNATE = auto()
    INVESTMENT_GURU = auto()
    LOTTERY_WINNER = auto()
    OIL_BARON = auto()
    REAL_ESTATE_MOGUL = auto()
    STOCK_MARKET_KING = auto()

    # --- Categoria: Famiglia ---
    FAMILY_LEGACY = auto()
    LARGE_FAMILY = auto()
    SUPER_PARENT = auto()
    ADOPTION_CHAMPION = auto()
    BLENDED_FAMILY_HARMONY = auto()
    FAMILY_REUNION_ORGANIZER = auto()
    FOSTER_PARENT_LEGEND = auto()
    GRANDPARENT_EXTRAORDINAIRE = auto()
    HAPPY_MARRIAGE_GURU = auto()
    LEGACY_KEEPER = auto()
    MULTIGENERATIONAL_HOUSEHOLD = auto()
    PET_BREEDER_EXPERT = auto()
    SINGLE_PARENT_HERO = auto()

    # --- Categoria: Sociale ---
    COMMUNITY_LEADER = auto()
    PERFECT_HOST = auto()
    SOCIAL_BUTTERFLY = auto()
    CHARITY_FOUNDER = auto()
    CLUB_ORGANIZER = auto()
    CULTURAL_AMBASSADOR = auto()
    EVENT_PLANNER = auto()
    INFLUENCER = auto()
    MAYOR = auto()
    MENTOR = auto()
    NETWORKING_GOD = auto()
    POLITICAL_LEADER = auto()
    SOCIAL_MEDIA_STAR = auto()
    TOWN_GOSSIP = auto()
    VOLUNTEER_COORDINATOR = auto()

    # --- Categoria: Sport e Corpo ---
    ARENA_FUSION_CHAMPION = auto()
    BODY_PERFECTIONIST = auto()
    EXTREME_SPORTS_PRO = auto()
    FITNESS_MODEL = auto()
    MARTIAL_ARTS_GRANDMASTER = auto()
    MOUNTAINEER = auto()
    OLYMPIC_ATHLETE = auto()
    PARKOUR_MASTER = auto()
    PROFESSIONAL_GAMER = auto()
    SPORTS_COACH = auto()
    SWIMMING_CHAMPION = auto()
    YOGA_INSTRUCTOR = auto()

    # --- Categoria: Natura ---
    ANGLING_ACE = auto()
    FREELANCE_BOTANIST = auto()
    MASTER_GARDENER = auto()
    ANIMAL_WHISPERER = auto()
    BEEKEEPING_EXPERT = auto()
    BIRD_WATCHER = auto()
    ECO_WARRIOR = auto()
    FOREST_GUARDIAN = auto()
    HERBALISM_MASTER = auto()
    HORSE_TRAINER = auto()
    LANDSCAPE_DESIGNER = auto()
    MARINE_BIOLOGIST = auto()
    MOUNTAIN_GUIDE = auto()
    SUSTAINABLE_LIVING = auto()

    # --- Categoria: Cibo ---
    MASTER_CHEF = auto()
    MASTER_MIXOLOGIST = auto()
    BAKING_CHAMPION = auto()
    BREWMASTER = auto()
    COFFEE_CONNOISSEUR = auto()
    FARM_TO_TABLE_PIONEER = auto()
    FOOD_CRITIC = auto()
    GOURMET_TRAVELER = auto()
    MICHELIN_STAR_CHEF = auto()
    RESTAURANT_OWNER = auto()
    STREET_FOOD_KING = auto()
    VEGAN_ACTIVIST = auto()
    WINE_EXPERT = auto()

    # --- Categoria: Stile di Vita ---
    HEDONIST_EPICUREAN = auto()
    PEACEFUL_EXISTENCE = auto()
    PHILANTHROPIST_ALTRUIST = auto()
    DIGITAL_NOMAD = auto()
    FIRE_MOVEMENT = auto()
    MINIMALIST_LIFESTYLE = auto()
    OFF_GRID_LIVING = auto()
    SLOW_LIFE_ADVOCATE = auto()
    SPIRITUAL_JOURNEY = auto()
    URBAN_EXPLORER = auto()
    VAN_LIFE = auto()
    WORK_LIFE_BALANCE = auto()

    # --- Categoria: Devianza ---
    MASTER_THIEF = auto()
    PUBLIC_ENEMY = auto()
    BLACK_MARKET_KINGPIN = auto()
    CON_ARTIST = auto()
    CORRUPT_OFFICIAL = auto()
    HACKTIVIST = auto()
    INFAMOUS_PIRATE = auto()
    PRISON_BREAK_MASTER = auto()
    SMUGGLER = auto()
    UNDERWORLD_BOSS = auto()
    VANDALISM_ARTIST = auto()

    # --- Categoria: Uniche / Lore ---
    THE_CURATOR = auto()
    WORLD_EXPLORER = auto()
    ANTHALYS_HISTORIAN = auto()
    ARTIFACT_HUNTER = auto()
    CULT_LEADER = auto()
    FORBIDDEN_KNOWLEDGE_SEEKER = auto()
    GHOST_WHISPERER = auto()
    LEGENDARY_TREASURE_HUNTER = auto()
    MYTH_DEBUNKER = auto()
    PARANORMAL_INVESTIGATOR = auto()
    PROPHECY_FULFILLER = auto()
    SECRET_SOCIETY_MASTER = auto()
    TIME_TRAVEL_PIONEER = auto()
    URBAN_LEGEND = auto()

    # --- Categoria: Carriera ---
    CEO = auto()
    CAREER_LADDER = auto()
    ENTREPRENEUR = auto()
    FREELANCE_SUCCESS = auto()
    INDUSTRY_LEADER = auto()
    INTERNSHIP_TO_EXECUTIVE = auto()
    JOB_HOPPER = auto()
    PROFESSIONAL_CERTIFICATION = auto()
    RETIREMENT_PLAN = auto()
    SIDE_HUSTLE_MOGUL = auto()
    STARTUP_FOUNDER = auto()
    UNION_LEADER = auto()
    WORK_FROM_HOME_GURU = auto()

    # --- Categoria: Romantiche ---
    SOULMATE = auto()
    CASUAL_DATING = auto()
    DIVORCE_SURVIVOR = auto()
    HAPPILY_SINGLE = auto()
    LOVE_TRIANGLE_RESOLVER = auto()
    MARRIAGE_OF_CONVENIENCE = auto()
    OPEN_RELATIONSHIP = auto()
    ROMANCE_NOVELIST = auto()
    SERIAL_MONOGAMIST = auto()
    SPEED_DATING_CHAMP = auto()
    SWEETHEART = auto()
    WEDDING_PLANNER = auto()

    # --- Categoria: Tecnologia ---
    AI_DEVELOPER = auto()
    APP_CREATOR = auto()
    CYBERSECURITY_EXPERT = auto()
    DRONE_RACER = auto()
    GADGET_COLLECTOR = auto()
    HARDWARE_HACKER = auto()
    ROBOT_COMPANION = auto()
    SMART_HOME_DESIGNER = auto()
    TECH_REPAIR_SPECIALIST = auto()
    VIRTUAL_REALITY_PIONEER = auto()

    # --- Categoria: Salute ---
    CENTENARIAN = auto()
    DISEASE_SURVIVOR = auto()
    FITNESS_TRANSFORMATION = auto()
    HEALTH_COACH = auto()
    MENTAL_HEALTH_ADVOCATE = auto()
    ORGAN_DONOR = auto()
    SPORTS_RECOVERY = auto()
    WEIGHT_LOSS_JOURNEY = auto()
    WELLNESS_INFLUENCER = auto()
    YOUTH_PRESERVATION = auto()

    # --- Categoria: Avventura ---
    DESERT_SURVIVALIST = auto()
    DEEP_SEA_EXPLORER = auto()
    JUNGLE_EXPEDITION = auto()
    PARANORMAL_ADVENTURER = auto()
    SPACE_TOURIST = auto()
    URBAN_EXPLORATION = auto()
    VOLCANO_CHASER = auto()
    WILDERNESS_SURVIVAL = auto()

    # --- Categoria: Arti Occulte ---
    ALCHEMY_MASTER = auto()
    CRYPTID_HUNTER = auto()
    CRYSTAL_HEALER = auto()
    DIVINATION_EXPERT = auto()
    FOLKLORE_RESEARCHER = auto()
    NECROMANCER = auto()
    POTION_MASTER = auto()
    RUNE_MASTER = auto()
    SPELLS_ARCHIVIST = auto()
    TAROT_READER = auto()
    VAMPIRE_HUNTER = auto()
    WITCH_COVEN_LEADER = auto()

    # --- Categoria: Educazione ---
    COLLEGE_GRADUATE = auto()
    EARLY_GRADUATION = auto()
    HOMESCHOOLING_PIONEER = auto()
    IVY_LEAGUE_SCHOLAR = auto()
    LIFELONG_LEARNER = auto()
    ONLINE_COURSE_CREATOR = auto()
    PROFESSOR_EMERITUS = auto()
    SCHOOL_DROPOUT_SUCCESS = auto()
    STUDY_ABROAD = auto()
    TEACHER_OF_THE_YEAR = auto()
    TUTORING_BUSINESS = auto()

    # --- Categoria: Viaggi ---
    AIRBNB_SUPERHOST = auto()
    BACKPACKER = auto()
    CRUISE_ENJOYER = auto()
    CULTURAL_IMMERSION = auto()
    GLOBE_TROTTER = auto()
    LUXURY_TRAVELER = auto()
    ROAD_TRIP_ADVENTURER = auto()
    SEVEN_WONDERS_VISITOR = auto()
    VOLUNTOURISM = auto()

    # --- Categoria: Divertimento ---
    CASINO_KING = auto()
    COMEDY_CLUB_OWNER = auto()
    ESCAPE_ROOM_DESIGNER = auto()
    FESTIVAL_GOER = auto()
    KARAOKE_CHAMPION = auto()
    MOVIE_BUFF = auto()
    PARTY_PLANNER = auto()
    THEME_PARK_FANATIC = auto()
    VIDEO_GAME_COLLECTOR = auto()
    ZOO_ENTHUSIAST = auto()

    def display_name_it(self, gender: Gender) -> str:
        """Restituisce un nome leggibile in italiano per l'aspirazione."""
        mapping = {
            # Creatività
            AspirationType.BESTSELLING_AUTHOR: {
                Gender.MALE: "Autore di Bestseller", 
                Gender.FEMALE: "Autrice di Bestseller"
            },
            AspirationType.MASTER_ARTISAN: {
                Gender.MALE: "Maestro Artigiano", 
                Gender.FEMALE: "Maestra Artigiana"
            },
            AspirationType.MASTER_PAINTER: {
                Gender.MALE: "Maestro Pittore", 
                Gender.FEMALE: "Maestra Pittrice"
            },
            AspirationType.RENOWNED_MUSICIAN: {
                Gender.MALE: "Musicista Famoso", 
                Gender.FEMALE: "Musicista Famosa"
            },
            AspirationType.AWARD_WINNING_DIRECTOR: {
                Gender.MALE: "Regista Premiato", 
                Gender.FEMALE: "Regista Premiata"
            },
            AspirationType.BROADWAY_STAR: {
                Gender.MALE: "Stella di Broadway", 
                Gender.FEMALE: "Stella di Broadway"
            },
            AspirationType.DIGITAL_ART_PIONEER: {
                Gender.MALE: "Pioniere dell'Arte Digitale", 
                Gender.FEMALE: "Pioniera dell'Arte Digitale"
            },
            AspirationType.FASHION_DESIGN_ICON: {
                Gender.MALE: "Icona del Design della Moda", 
                Gender.FEMALE: "Icona del Design della Moda"
            },
            AspirationType.GRAFFITI_LEGEND: {
                Gender.MALE: "Leggenda del Graffiti", 
                Gender.FEMALE: "Leggenda del Graffiti"
            },
            AspirationType.INSTRUMENT_VIRTUOSO: {
                Gender.MALE: "Virtuoso dello Strumento", 
                Gender.FEMALE: "Virtuosa dello Strumento"
            },
            AspirationType.POET_LAUREATE: {
                Gender.MALE: "Poeta Laureato", 
                Gender.FEMALE: "Poetessa Laureata"
            },
            AspirationType.SCULPTURE_MASTER: {
                Gender.MALE: "Maestro Scultore", 
                Gender.FEMALE: "Maestra Scultrice"
            },
            AspirationType.STREET_PERFORMER_ICON: {
                Gender.MALE: "Icona degli Artisti di Strada", 
                Gender.FEMALE: "Icona delle Artiste di Strada"
            },
            AspirationType.TATTOO_ARTIST_EXTRAORDINAIRE: {
                Gender.MALE: "Tatuatore Straordinario", 
                Gender.FEMALE: "Tatuatrice Straordinaria"
            },
            AspirationType.WORLD_FAMOUS_DJ: {
                Gender.MALE: "DJ di Fama Mondiale", 
                Gender.FEMALE: "DJ di Fama Mondiale"
            },
            
            # Conoscenza
            AspirationType.ACADEMIC_EXCELLENCE: {
                Gender.MALE: "Eccellenza Accademica", 
                Gender.FEMALE: "Eccellenza Accademica"
            },
            AspirationType.LOREMASTER_OF_ANTHALYS: {
                Gender.MALE: "Maestro del Sapere di Anthalys", 
                Gender.FEMALE: "Maestra del Sapere di Anthalys"
            },
            AspirationType.SCIENTIFIC_BREAKTHROUGH: {
                Gender.MALE: "Scoperta Scientifica", 
                Gender.FEMALE: "Scoperta Scientifica"
            },
            AspirationType.SKILL_MASTER: {
                Gender.MALE: "Maestro di un'Abilità", 
                Gender.FEMALE: "Maestra di un'Abilità"
            },
            AspirationType.SKILL_POLYGLOT: {
                Gender.MALE: "Tuttologo", 
                Gender.FEMALE: "Tuttologa"
            },
            AspirationType.KNOWLEDGE_SEEKER: {
                Gender.MALE: "Ricercatore di Conoscenza", 
                Gender.FEMALE: "Ricercatrice di Conoscenza"
            },
            AspirationType.ARCHAEOLOGY_EXPERT: {
                Gender.MALE: "Esperto di Archeologia", 
                Gender.FEMALE: "Esperta di Archeologia"
            },
            AspirationType.ASTROLOGY_MASTER: {
                Gender.MALE: "Maestro di Astrologia", 
                Gender.FEMALE: "Maestra di Astrologia"
            },
            AspirationType.CODING_GURU: {
                Gender.MALE: "Guru della Programmazione", 
                Gender.FEMALE: "Guru della Programmazione"
            },
            AspirationType.HISTORICAL_RESEARCHER: {
                Gender.MALE: "Ricercatore Storico", 
                Gender.FEMALE: "Ricercatrice Storica"
            },
            AspirationType.LANGUAGE_AMBASSADOR: {
                Gender.MALE: "Ambasciatore Linguistico", 
                Gender.FEMALE: "Ambasciatrice Linguistica"
            },
            AspirationType.MATH_GENIUS: {
                Gender.MALE: "Genio della Matematica", 
                Gender.FEMALE: "Genio della Matematica"
            },
            AspirationType.PHILOSOPHY_SCHOLAR: {
                Gender.MALE: "Studioso di Filosofia", 
                Gender.FEMALE: "Studiosa di Filosofia"
            },
            AspirationType.QUANTUM_PHYSICIST: {
                Gender.MALE: "Fisico Quantistico", 
                Gender.FEMALE: "Fisica Quantistica"
            },
            AspirationType.ROBOTICS_INNOVATOR: {
                Gender.MALE: "Innovatore nella Robotica", 
                Gender.FEMALE: "Innovatrice nella Robotica"
            },
            
            # Fortuna
            AspirationType.FABULOUSLY_WEALTHY: {
                Gender.MALE: "Favolosamente Ricco", 
                Gender.FEMALE: "Favolosamente Ricca"
            },
            AspirationType.MANSION_BARON: {
                Gender.MALE: "Barone delle Ville", 
                Gender.FEMALE: "Baronessa delle Ville"
            },
            AspirationType.BUSINESS_TYCOON: {
                Gender.MALE: "Magnate degli Affari", 
                Gender.FEMALE: "Magnate degli Affari"
            },
            AspirationType.CRYPTO_MILLIONAIRE: {
                Gender.MALE: "Milionario delle Criptovalute", 
                Gender.FEMALE: "Milionaria delle Criptovalute"
            },
            AspirationType.ESTATE_MAGNATE: {
                Gender.MALE: "Magnate Immobiliare", 
                Gender.FEMALE: "Magnate Immobiliare"
            },
            AspirationType.INVESTMENT_GURU: {
                Gender.MALE: "Guru degli Investimenti", 
                Gender.FEMALE: "Guru degli Investimenti"
            },
            AspirationType.LOTTERY_WINNER: {
                Gender.MALE: "Vincitore della Lotteria", 
                Gender.FEMALE: "Vincitrice della Lotteria"
            },
            AspirationType.OIL_BARON: {
                Gender.MALE: "Barone del Petrolio", 
                Gender.FEMALE: "Baronessa del Petrolio"
            },
            AspirationType.REAL_ESTATE_MOGUL: {
                Gender.MALE: "Mogul Immobiliare", 
                Gender.FEMALE: "Mogul Immobiliare"
            },
            AspirationType.STOCK_MARKET_KING: {
                Gender.MALE: "Re della Borsa", 
                Gender.FEMALE: "Regina della Borsa"
            },
            
            # Famiglia
            AspirationType.FAMILY_LEGACY: {
                Gender.MALE: "Eredità Familiare", 
                Gender.FEMALE: "Eredità Familiare"
            },
            AspirationType.LARGE_FAMILY: {
                Gender.MALE: "Famiglia Numerosa", 
                Gender.FEMALE: "Famiglia Numerosa"
            },
            AspirationType.SUPER_PARENT: {
                Gender.MALE: "Super Genitore", 
                Gender.FEMALE: "Super Genitore"
            },
            AspirationType.ADOPTION_CHAMPION: {
                Gender.MALE: "Campione dell'Adozione", 
                Gender.FEMALE: "Campionessa dell'Adozione"
            },
            AspirationType.BLENDED_FAMILY_HARMONY: {
                Gender.MALE: "Armonia Familiare Mista", 
                Gender.FEMALE: "Armonia Familiare Mista"
            },
            AspirationType.FAMILY_REUNION_ORGANIZER: {
                Gender.MALE: "Organizzatore di Riunioni Familiari", 
                Gender.FEMALE: "Organizzatrice di Riunioni Familiari"
            },
            AspirationType.FOSTER_PARENT_LEGEND: {
                Gender.MALE: "Leggenda dell'Affido", 
                Gender.FEMALE: "Leggenda dell'Affido"
            },
            AspirationType.GRANDPARENT_EXTRAORDINAIRE: {
                Gender.MALE: "Nonno Straordinario", 
                Gender.FEMALE: "Nonna Straordinaria"
            },
            AspirationType.HAPPY_MARRIAGE_GURU: {
                Gender.MALE: "Guru del Matrimonio Felice", 
                Gender.FEMALE: "Guru del Matrimonio Felice"
            },
            AspirationType.LEGACY_KEEPER: {
                Gender.MALE: "Custode dell'Eredità", 
                Gender.FEMALE: "Custode dell'Eredità"
            },
            AspirationType.MULTIGENERATIONAL_HOUSEHOLD: {
                Gender.MALE: "Famiglia Multigenerazionale", 
                Gender.FEMALE: "Famiglia Multigenerazionale"
            },
            AspirationType.PET_BREEDER_EXPERT: {
                Gender.MALE: "Esperto Allevatore di Animali", 
                Gender.FEMALE: "Esperta Allevatrice di Animali"
            },
            AspirationType.SINGLE_PARENT_HERO: {
                Gender.MALE: "Eroe Genitore Singolo", 
                Gender.FEMALE: "Eroina Genitore Singolo"
            },
            
            # Sociale
            AspirationType.COMMUNITY_LEADER: {
                Gender.MALE: "Leader della Comunità", 
                Gender.FEMALE: "Leader della Comunità"
            },
            AspirationType.PERFECT_HOST: {
                Gender.MALE: "Ospite Perfetto", 
                Gender.FEMALE: "Ospite Perfetta"
            },
            AspirationType.SOCIAL_BUTTERFLY: {
                Gender.MALE: "Anima della Festa", 
                Gender.FEMALE: "Anima della Festa"
            },
            AspirationType.CHARITY_FOUNDER: {
                Gender.MALE: "Fondatore di Beneficenza", 
                Gender.FEMALE: "Fondatrice di Beneficenza"
            },
            AspirationType.CLUB_ORGANIZER: {
                Gender.MALE: "Organizzatore di Club", 
                Gender.FEMALE: "Organizzatrice di Club"
            },
            AspirationType.CULTURAL_AMBASSADOR: {
                Gender.MALE: "Ambasciatore Culturale", 
                Gender.FEMALE: "Ambasciatrice Culturale"
            },
            AspirationType.EVENT_PLANNER: {
                Gender.MALE: "Organizzatore di Eventi", 
                Gender.FEMALE: "Organizzatrice di Eventi"
            },
            AspirationType.INFLUENCER: {
                Gender.MALE: "Influencer", 
                Gender.FEMALE: "Influencer"
            },
            AspirationType.MAYOR: {
                Gender.MALE: "Sindaco", 
                Gender.FEMALE: "Sindaca"
            },
            AspirationType.MENTOR: {
                Gender.MALE: "Mentore", 
                Gender.FEMALE: "Mentore"
            },
            AspirationType.NETWORKING_GOD: {
                Gender.MALE: "Dio del Networking", 
                Gender.FEMALE: "Dea del Networking"
            },
            AspirationType.POLITICAL_LEADER: {
                Gender.MALE: "Leader Politico", 
                Gender.FEMALE: "Leader Politica"
            },
            AspirationType.SOCIAL_MEDIA_STAR: {
                Gender.MALE: "Star dei Social Media", 
                Gender.FEMALE: "Star dei Social Media"
            },
            AspirationType.TOWN_GOSSIP: {
                Gender.MALE: "Pettegolo della Città", 
                Gender.FEMALE: "Pettegola della Città"
            },
            AspirationType.VOLUNTEER_COORDINATOR: {
                Gender.MALE: "Coordinatore di Volontariato", 
                Gender.FEMALE: "Coordinatrice di Volontariato"
            },
            
            # Sport e Corpo
            AspirationType.ARENA_FUSION_CHAMPION: {
                Gender.MALE: "Campione di Arena Fusion", 
                Gender.FEMALE: "Campionessa di Arena Fusion"
            },
            AspirationType.BODY_PERFECTIONIST: {
                Gender.MALE: "Perfezionista del Corpo", 
                Gender.FEMALE: "Perfezionista del Corpo"
            },
            AspirationType.EXTREME_SPORTS_PRO: {
                Gender.MALE: "Professionista di Sport Estremi", 
                Gender.FEMALE: "Professionista di Sport Estremi"
            },
            AspirationType.FITNESS_MODEL: {
                Gender.MALE: "Modello Fitness", 
                Gender.FEMALE: "Modella Fitness"
            },
            AspirationType.MARTIAL_ARTS_GRANDMASTER: {
                Gender.MALE: "Gran Maestro di Arti Marziali", 
                Gender.FEMALE: "Gran Maestra di Arti Marziali"
            },
            AspirationType.MOUNTAINEER: {
                Gender.MALE: "Alpinista", 
                Gender.FEMALE: "Alpinista"
            },
            AspirationType.OLYMPIC_ATHLETE: {
                Gender.MALE: "Atleta Olimpico", 
                Gender.FEMALE: "Atleta Olimpica"
            },
            AspirationType.PARKOUR_MASTER: {
                Gender.MALE: "Maestro di Parkour", 
                Gender.FEMALE: "Maestra di Parkour"
            },
            AspirationType.PROFESSIONAL_GAMER: {
                Gender.MALE: "Giocatore Professionista", 
                Gender.FEMALE: "Giocatrice Professionista"
            },
            AspirationType.SPORTS_COACH: {
                Gender.MALE: "Allenatore Sportivo", 
                Gender.FEMALE: "Allenatrice Sportiva"
            },
            AspirationType.SWIMMING_CHAMPION: {
                Gender.MALE: "Campione di Nuoto", 
                Gender.FEMALE: "Campionessa di Nuoto"
            },
            AspirationType.YOGA_INSTRUCTOR: {
                Gender.MALE: "Istruttore di Yoga", 
                Gender.FEMALE: "Istruttrice di Yoga"
            },
            
            # Natura
            AspirationType.ANGLING_ACE: {
                Gender.MALE: "Asso della Pesca", 
                Gender.FEMALE: "Asso della Pesca"
            },
            AspirationType.FREELANCE_BOTANIST: {
                Gender.MALE: "Botanico Indipendente", 
                Gender.FEMALE: "Botanica Indipendente"
            },
            AspirationType.MASTER_GARDENER: {
                Gender.MALE: "Maestro Giardiniere", 
                Gender.FEMALE: "Maestra Giardiniera"
            },
            AspirationType.ANIMAL_WHISPERER: {
                Gender.MALE: "Sussurratore di Animali", 
                Gender.FEMALE: "Sussurratrice di Animali"
            },
            AspirationType.BEEKEEPING_EXPERT: {
                Gender.MALE: "Esperto di Apicoltura", 
                Gender.FEMALE: "Esperta di Apicoltura"
            },
            AspirationType.BIRD_WATCHER: {
                Gender.MALE: "Birdwatcher", 
                Gender.FEMALE: "Birdwatcher"
            },
            AspirationType.ECO_WARRIOR: {
                Gender.MALE: "Guerriero Ecologico", 
                Gender.FEMALE: "Guerriera Ecologica"
            },
            AspirationType.FOREST_GUARDIAN: {
                Gender.MALE: "Guardiano della Foresta", 
                Gender.FEMALE: "Guardiana della Foresta"
            },
            AspirationType.HERBALISM_MASTER: {
                Gender.MALE: "Maestro di Erboristeria", 
                Gender.FEMALE: "Maestra di Erboristeria"
            },
            AspirationType.HORSE_TRAINER: {
                Gender.MALE: "Addestratore di Cavalli", 
                Gender.FEMALE: "Addestratrice di Cavalli"
            },
            AspirationType.LANDSCAPE_DESIGNER: {
                Gender.MALE: "Progettista di Paesaggi", 
                Gender.FEMALE: "Progettista di Paesaggi"
            },
            AspirationType.MARINE_BIOLOGIST: {
                Gender.MALE: "Biologo Marino", 
                Gender.FEMALE: "Biologa Marina"
            },
            AspirationType.MOUNTAIN_GUIDE: {
                Gender.MALE: "Guida Alpina", 
                Gender.FEMALE: "Guida Alpina"
            },
            AspirationType.SUSTAINABLE_LIVING: {
                Gender.MALE: "Vita Sostenibile", 
                Gender.FEMALE: "Vita Sostenibile"
            },
            
            # Cibo
            AspirationType.MASTER_CHEF: {
                Gender.MALE: "Master Chef", 
                Gender.FEMALE: "Master Chef"
            },
            AspirationType.MASTER_MIXOLOGIST: {
                Gender.MALE: "Maestro Mixologo", 
                Gender.FEMALE: "Maestra Mixologa"
            },
            AspirationType.BAKING_CHAMPION: {
                Gender.MALE: "Campione di Pasticceria", 
                Gender.FEMALE: "Campionessa di Pasticceria"
            },
            AspirationType.BREWMASTER: {
                Gender.MALE: "Maestro Birraio", 
                Gender.FEMALE: "Maestra Birraia"
            },
            AspirationType.COFFEE_CONNOISSEUR: {
                Gender.MALE: "Conoscitore di Caffè", 
                Gender.FEMALE: "Conoscitrice di Caffè"
            },
            AspirationType.FARM_TO_TABLE_PIONEER: {
                Gender.MALE: "Pioniere Filiera Corta", 
                Gender.FEMALE: "Pioniera Filiera Corta"
            },
            AspirationType.FOOD_CRITIC: {
                Gender.MALE: "Critico Gastronomico", 
                Gender.FEMALE: "Critica Gastronomica"
            },
            AspirationType.GOURMET_TRAVELER: {
                Gender.MALE: "Gourmet Viaggiatore", 
                Gender.FEMALE: "Gourmet Viaggiatrice"
            },
            AspirationType.MICHELIN_STAR_CHEF: {
                Gender.MALE: "Chef Stellato Michelin", 
                Gender.FEMALE: "Chef Stellata Michelin"
            },
            AspirationType.RESTAURANT_OWNER: {
                Gender.MALE: "Proprietario di Ristorante", 
                Gender.FEMALE: "Proprietaria di Ristorante"
            },
            AspirationType.STREET_FOOD_KING: {
                Gender.MALE: "Re del Cibo di Strada", 
                Gender.FEMALE: "Regina del Cibo di Strada"
            },
            AspirationType.VEGAN_ACTIVIST: {
                Gender.MALE: "Attivista Vegano", 
                Gender.FEMALE: "Attivista Vegana"
            },
            AspirationType.WINE_EXPERT: {
                Gender.MALE: "Esperto di Vini", 
                Gender.FEMALE: "Esperta di Vini"
            },
            
            # Stile di Vita
            AspirationType.HEDONIST_EPICUREAN: {
                Gender.MALE: "Edonista Epicureo", 
                Gender.FEMALE: "Edonista Epicurea"
            },
            AspirationType.PEACEFUL_EXISTENCE: {
                Gender.MALE: "Esistenza Pacifica", 
                Gender.FEMALE: "Esistenza Pacifica"
            },
            AspirationType.PHILANTHROPIST_ALTRUIST: {
                Gender.MALE: "Filantropo Altruista", 
                Gender.FEMALE: "Filantropa Altruista"
            },
            AspirationType.DIGITAL_NOMAD: {
                Gender.MALE: "Nomade Digitale", 
                Gender.FEMALE: "Nomade Digitale"
            },
            AspirationType.FIRE_MOVEMENT: {
                Gender.MALE: "Movimento FIRE (Financial Independence)", 
                Gender.FEMALE: "Movimento FIRE (Financial Independence)"
            },
            AspirationType.MINIMALIST_LIFESTYLE: {
                Gender.MALE: "Stile di Vita Minimalista", 
                Gender.FEMALE: "Stile di Vita Minimalista"
            },
            AspirationType.OFF_GRID_LIVING: {
                Gender.MALE: "Vita Off-Grid", 
                Gender.FEMALE: "Vita Off-Grid"
            },
            AspirationType.SLOW_LIFE_ADVOCATE: {
                Gender.MALE: "Sostenitore della Vita Lenta", 
                Gender.FEMALE: "Sostenitrice della Vita Lenta"
            },
            AspirationType.SPIRITUAL_JOURNEY: {
                Gender.MALE: "Viaggio Spirituale", 
                Gender.FEMALE: "Viaggio Spirituale"
            },
            AspirationType.URBAN_EXPLORER: {
                Gender.MALE: "Esploratore Urbano", 
                Gender.FEMALE: "Esploratrice Urbana"
            },
            AspirationType.VAN_LIFE: {
                Gender.MALE: "Vita in Camper", 
                Gender.FEMALE: "Vita in Camper"
            },
            AspirationType.WORK_LIFE_BALANCE: {
                Gender.MALE: "Equilibrio Vita-Lavoro", 
                Gender.FEMALE: "Equilibrio Vita-Lavoro"
            },
            
            # Devianza
            AspirationType.MASTER_THIEF: {
                Gender.MALE: "Maestro Ladro", 
                Gender.FEMALE: "Maestra Ladra"
            },
            AspirationType.PUBLIC_ENEMY: {
                Gender.MALE: "Nemico Pubblico", 
                Gender.FEMALE: "Nemica Pubblica"
            },
            AspirationType.BLACK_MARKET_KINGPIN: {
                Gender.MALE: "Re del Mercato Nero", 
                Gender.FEMALE: "Regina del Mercato Nero"
            },
            AspirationType.CON_ARTIST: {
                Gender.MALE: "Truffatore", 
                Gender.FEMALE: "Truffatrice"
            },
            AspirationType.CORRUPT_OFFICIAL: {
                Gender.MALE: "Funzionario Corrotto", 
                Gender.FEMALE: "Funzionaria Corrotta"
            },
            AspirationType.HACKTIVIST: {
                Gender.MALE: "Hacktivist", 
                Gender.FEMALE: "Hacktivist"
            },
            AspirationType.INFAMOUS_PIRATE: {
                Gender.MALE: "Pirata Infame", 
                Gender.FEMALE: "Pirata Infame"
            },
            AspirationType.PRISON_BREAK_MASTER: {
                Gender.MALE: "Maestro di Evasioni", 
                Gender.FEMALE: "Maestra di Evasioni"
            },
            AspirationType.SMUGGLER: {
                Gender.MALE: "Contrabbandiere", 
                Gender.FEMALE: "Contrabbandiera"
            },
            AspirationType.UNDERWORLD_BOSS: {
                Gender.MALE: "Boss della Malavita", 
                Gender.FEMALE: "Boss della Malavita"
            },
            AspirationType.VANDALISM_ARTIST: {
                Gender.MALE: "Artista del Vandalismo", 
                Gender.FEMALE: "Artista del Vandalismo"
            },
            
            # Uniche / Lore
            AspirationType.THE_CURATOR: {
                Gender.MALE: "Il Curatore", 
                Gender.FEMALE: "La Curatrice"
            },
            AspirationType.WORLD_EXPLORER: {
                Gender.MALE: "Esploratore del Mondo", 
                Gender.FEMALE: "Esploratrice del Mondo"
            },
            AspirationType.ANTHALYS_HISTORIAN: {
                Gender.MALE: "Storico di Anthalys", 
                Gender.FEMALE: "Storica di Anthalys"
            },
            AspirationType.ARTIFACT_HUNTER: {
                Gender.MALE: "Cacciatore di Manufatti", 
                Gender.FEMALE: "Cacciatrice di Manufatti"
            },
            AspirationType.CULT_LEADER: {
                Gender.MALE: "Leader di Culto", 
                Gender.FEMALE: "Leader di Culto"
            },
            AspirationType.FORBIDDEN_KNOWLEDGE_SEEKER: {
                Gender.MALE: "Cercatore di Conoscenza Proibita", 
                Gender.FEMALE: "Cercatrice di Conoscenza Proibita"
            },
            AspirationType.GHOST_WHISPERER: {
                Gender.MALE: "Sussurratore di Fantasmi", 
                Gender.FEMALE: "Sussurratrice di Fantasmi"
            },
            AspirationType.LEGENDARY_TREASURE_HUNTER: {
                Gender.MALE: "Cacciatore di Tesori Leggendari", 
                Gender.FEMALE: "Cacciatrice di Tesori Leggendari"
            },
            AspirationType.MYTH_DEBUNKER: {
                Gender.MALE: "Sfatatore di Miti", 
                Gender.FEMALE: "Sfatatrice di Miti"
            },
            AspirationType.PARANORMAL_INVESTIGATOR: {
                Gender.MALE: "Investigatore Paranormale", 
                Gender.FEMALE: "Investigatrice Paranormale"
            },
            AspirationType.PROPHECY_FULFILLER: {
                Gender.MALE: "Adempitore di Profezie", 
                Gender.FEMALE: "Adempitrice di Profezie"
            },
            AspirationType.SECRET_SOCIETY_MASTER: {
                Gender.MALE: "Maestro di Società Segreta", 
                Gender.FEMALE: "Maestra di Società Segreta"
            },
            AspirationType.TIME_TRAVEL_PIONEER: {
                Gender.MALE: "Pioniere del Viaggio nel Tempo", 
                Gender.FEMALE: "Pioniera del Viaggio nel Tempo"
            },
            AspirationType.URBAN_LEGEND: {
                Gender.MALE: "Leggenda Urbana", 
                Gender.FEMALE: "Leggenda Urbana"
            },
            
            # Carriera
            AspirationType.CEO: {
                Gender.MALE: "CEO", 
                Gender.FEMALE: "CEO"
            },
            AspirationType.CAREER_LADDER: {
                Gender.MALE: "Scalatore di Carriera", 
                Gender.FEMALE: "Scalatrice di Carriera"
            },
            AspirationType.ENTREPRENEUR: {
                Gender.MALE: "Imprenditore", 
                Gender.FEMALE: "Imprenditrice"
            },
            AspirationType.FREELANCE_SUCCESS: {
                Gender.MALE: "Successo da Freelance", 
                Gender.FEMALE: "Successo da Freelance"
            },
            AspirationType.INDUSTRY_LEADER: {
                Gender.MALE: "Leader del Settore", 
                Gender.FEMALE: "Leader del Settore"
            },
            AspirationType.INTERNSHIP_TO_EXECUTIVE: {
                Gender.MALE: "Da Stagista a Dirigente", 
                Gender.FEMALE: "Da Stagista a Dirigente"
            },
            AspirationType.JOB_HOPPER: {
                Gender.MALE: "Saltatore di Lavoro", 
                Gender.FEMALE: "Saltatrice di Lavoro"
            },
            AspirationType.PROFESSIONAL_CERTIFICATION: {
                Gender.MALE: "Certificazione Professionale", 
                Gender.FEMALE: "Certificazione Professionale"
            },
            AspirationType.RETIREMENT_PLAN: {
                Gender.MALE: "Piano di Pensionamento", 
                Gender.FEMALE: "Piano di Pensionamento"
            },
            AspirationType.SIDE_HUSTLE_MOGUL: {
                Gender.MALE: "Mogul degli Affari Collaterali", 
                Gender.FEMALE: "Mogul degli Affari Collaterali"
            },
            AspirationType.STARTUP_FOUNDER: {
                Gender.MALE: "Fondatore di Startup", 
                Gender.FEMALE: "Fondatrice di Startup"
            },
            AspirationType.UNION_LEADER: {
                Gender.MALE: "Leader Sindacale", 
                Gender.FEMALE: "Leader Sindacale"
            },
            AspirationType.WORK_FROM_HOME_GURU: {
                Gender.MALE: "Guru del Lavoro da Casa", 
                Gender.FEMALE: "Guru del Lavoro da Casa"
            },
            
            # Romantiche
            AspirationType.SOULMATE: {
                Gender.MALE: "Anima Gemella", 
                Gender.FEMALE: "Anima Gemella"
            },
            AspirationType.CASUAL_DATING: {
                Gender.MALE: "Appuntamenti Informali", 
                Gender.FEMALE: "Appuntamenti Informali"
            },
            AspirationType.DIVORCE_SURVIVOR: {
                Gender.MALE: "Sopravvissuto al Divorzio", 
                Gender.FEMALE: "Sopravvissuta al Divorzio"
            },
            AspirationType.HAPPILY_SINGLE: {
                Gender.MALE: "Felicemente Single", 
                Gender.FEMALE: "Felicemente Single"
            },
            AspirationType.LOVE_TRIANGLE_RESOLVER: {
                Gender.MALE: "Risolvitore di Triangoli Amorosi", 
                Gender.FEMALE: "Risolvitrice di Triangoli Amorosi"
            },
            AspirationType.MARRIAGE_OF_CONVENIENCE: {
                Gender.MALE: "Matrimonio di Convenienza", 
                Gender.FEMALE: "Matrimonio di Convenienza"
            },
            AspirationType.OPEN_RELATIONSHIP: {
                Gender.MALE: "Relazione Aperta", 
                Gender.FEMALE: "Relazione Aperta"
            },
            AspirationType.ROMANCE_NOVELIST: {
                Gender.MALE: "Scrittore di Romanzi Rosa", 
                Gender.FEMALE: "Scrittrice di Romanzi Rosa"
            },
            AspirationType.SERIAL_MONOGAMIST: {
                Gender.MALE: "Monogamo Seriale", 
                Gender.FEMALE: "Monogama Seriale"
            },
            AspirationType.SPEED_DATING_CHAMP: {
                Gender.MALE: "Campione di Speed Dating", 
                Gender.FEMALE: "Campionessa di Speed Dating"
            },
            AspirationType.SWEETHEART: {
                Gender.MALE: "Fidanzato Ideale", 
                Gender.FEMALE: "Fidanzata Ideale"
            },
            AspirationType.WEDDING_PLANNER: {
                Gender.MALE: "Organizzatore di Matrimoni", 
                Gender.FEMALE: "Organizzatrice di Matrimoni"
            },
            
            # Tecnologia
            AspirationType.AI_DEVELOPER: {
                Gender.MALE: "Sviluppatore di IA", 
                Gender.FEMALE: "Sviluppatrice di IA"
            },
            AspirationType.APP_CREATOR: {
                Gender.MALE: "Creatore di App", 
                Gender.FEMALE: "Creatrice di App"
            },
            AspirationType.CYBERSECURITY_EXPERT: {
                Gender.MALE: "Esperto di Sicurezza Informatica", 
                Gender.FEMALE: "Esperta di Sicurezza Informatica"
            },
            AspirationType.DRONE_RACER: {
                Gender.MALE: "Pilota di Droni", 
                Gender.FEMALE: "Pilota di Droni"
            },
            AspirationType.GADGET_COLLECTOR: {
                Gender.MALE: "Collezionista di Gadget", 
                Gender.FEMALE: "Collezionista di Gadget"
            },
            AspirationType.HARDWARE_HACKER: {
                Gender.MALE: "Hacker Hardware", 
                Gender.FEMALE: "Hacker Hardware"
            },
            AspirationType.ROBOT_COMPANION: {
                Gender.MALE: "Compagno Robotico", 
                Gender.FEMALE: "Compagna Robotica"
            },
            AspirationType.SMART_HOME_DESIGNER: {
                Gender.MALE: "Designer di Case Intelligenti", 
                Gender.FEMALE: "Designer di Case Intelligenti"
            },
            AspirationType.TECH_REPAIR_SPECIALIST: {
                Gender.MALE: "Specialista di Riparazioni Tech", 
                Gender.FEMALE: "Specialista di Riparazioni Tech"
            },
            AspirationType.VIRTUAL_REALITY_PIONEER: {
                Gender.MALE: "Pioniere della Realtà Virtuale", 
                Gender.FEMALE: "Pioniera della Realtà Virtuale"
            },
            
            # Salute
            AspirationType.CENTENARIAN: {
                Gender.MALE: "Centenario", 
                Gender.FEMALE: "Centenaria"
            },
            AspirationType.DISEASE_SURVIVOR: {
                Gender.MALE: "Sopravvissuto a Malattia", 
                Gender.FEMALE: "Sopravvissuta a Malattia"
            },
            AspirationType.FITNESS_TRANSFORMATION: {
                Gender.MALE: "Trasformazione Fisica", 
                Gender.FEMALE: "Trasformazione Fisica"
            },
            AspirationType.HEALTH_COACH: {
                Gender.MALE: "Coach della Salute", 
                Gender.FEMALE: "Coach della Salute"
            },
            AspirationType.MENTAL_HEALTH_ADVOCATE: {
                Gender.MALE: "Difensore della Salute Mentale", 
                Gender.FEMALE: "Difensore della Salute Mentale"
            },
            AspirationType.ORGAN_DONOR: {
                Gender.MALE: "Donatore di Organi", 
                Gender.FEMALE: "Donatrice di Organi"
            },
            AspirationType.SPORTS_RECOVERY: {
                Gender.MALE: "Recupero Sportivo", 
                Gender.FEMALE: "Recupero Sportivo"
            },
            AspirationType.WEIGHT_LOSS_JOURNEY: {
                Gender.MALE: "Percorso di Perdita di Peso", 
                Gender.FEMALE: "Percorso di Perdita di Peso"
            },
            AspirationType.WELLNESS_INFLUENCER: {
                Gender.MALE: "Influencer del Benessere", 
                Gender.FEMALE: "Influencer del Benessere"
            },
            AspirationType.YOUTH_PRESERVATION: {
                Gender.MALE: "Conservazione della Giovinezza", 
                Gender.FEMALE: "Conservazione della Giovinezza"
            },
            
            # Avventura
            AspirationType.DESERT_SURVIVALIST: {
                Gender.MALE: "Sopravvissuto del Deserto", 
                Gender.FEMALE: "Sopravvissuta del Deserto"
            },
            AspirationType.DEEP_SEA_EXPLORER: {
                Gender.MALE: "Esploratore degli Abissi", 
                Gender.FEMALE: "Esploratrice degli Abissi"
            },
            AspirationType.JUNGLE_EXPEDITION: {
                Gender.MALE: "Spedizione nella Giungla", 
                Gender.FEMALE: "Spedizione nella Giungla"
            },
            AspirationType.PARANORMAL_ADVENTURER: {
                Gender.MALE: "Avventuriero Paranormale", 
                Gender.FEMALE: "Avventuriera Paranormale"
            },
            AspirationType.SPACE_TOURIST: {
                Gender.MALE: "Turista Spaziale", 
                Gender.FEMALE: "Turista Spaziale"
            },
            AspirationType.URBAN_EXPLORATION: {
                Gender.MALE: "Esplorazione Urbana", 
                Gender.FEMALE: "Esplorazione Urbana"
            },
            AspirationType.VOLCANO_CHASER: {
                Gender.MALE: "Inseguitore di Vulcani", 
                Gender.FEMALE: "Inseguitrice di Vulcani"
            },
            AspirationType.WILDERNESS_SURVIVAL: {
                Gender.MALE: "Sopravvivenza Selvaggia", 
                Gender.FEMALE: "Sopravvivenza Selvaggia"
            },
            
            # Arti Occulte
            AspirationType.ALCHEMY_MASTER: {
                Gender.MALE: "Maestro di Alchimia", 
                Gender.FEMALE: "Maestra di Alchimia"
            },
            AspirationType.CRYPTID_HUNTER: {
                Gender.MALE: "Cacciatore di Criptidi", 
                Gender.FEMALE: "Cacciatrice di Criptidi"
            },
            AspirationType.CRYSTAL_HEALER: {
                Gender.MALE: "Guaritore con Cristalli", 
                Gender.FEMALE: "Guaritrice con Cristalli"
            },
            AspirationType.DIVINATION_EXPERT: {
                Gender.MALE: "Esperto di Divinazione", 
                Gender.FEMALE: "Esperta di Divinazione"
            },
            AspirationType.FOLKLORE_RESEARCHER: {
                Gender.MALE: "Ricercatore di Folclore", 
                Gender.FEMALE: "Ricercatrice di Folclore"
            },
            AspirationType.NECROMANCER: {
                Gender.MALE: "Negromante", 
                Gender.FEMALE: "Negromante"
            },
            AspirationType.POTION_MASTER: {
                Gender.MALE: "Maestro di Pozioni", 
                Gender.FEMALE: "Maestra di Pozioni"
            },
            AspirationType.RUNE_MASTER: {
                Gender.MALE: "Maestro di Rune", 
                Gender.FEMALE: "Maestra di Rune"
            },
            AspirationType.SPELLS_ARCHIVIST: {
                Gender.MALE: "Archivista di Incantesimi", 
                Gender.FEMALE: "Archivista di Incantesimi"
            },
            AspirationType.TAROT_READER: {
                Gender.MALE: "Lettore di Tarocchi", 
                Gender.FEMALE: "Lettrice di Tarocchi"
            },
            AspirationType.VAMPIRE_HUNTER: {
                Gender.MALE: "Cacciatore di Vampiri", 
                Gender.FEMALE: "Cacciatrice di Vampiri"
            },
            AspirationType.WITCH_COVEN_LEADER: {
                Gender.MALE: "Leader di Congrega di Streghe", 
                Gender.FEMALE: "Leader di Congrega di Streghe"
            },
            
            # Educazione
            AspirationType.COLLEGE_GRADUATE: {
                Gender.MALE: "Laureato", 
                Gender.FEMALE: "Laureata"
            },
            AspirationType.EARLY_GRADUATION: {
                Gender.MALE: "Laurea Anticipata", 
                Gender.FEMALE: "Laurea Anticipata"
            },
            AspirationType.HOMESCHOOLING_PIONEER: {
                Gender.MALE: "Pioniere dell'Homeschooling", 
                Gender.FEMALE: "Pioniera dell'Homeschooling"
            },
            AspirationType.IVY_LEAGUE_SCHOLAR: {
                Gender.MALE: "Studioso Ivy League", 
                Gender.FEMALE: "Studiosa Ivy League"
            },
            AspirationType.LIFELONG_LEARNER: {
                Gender.MALE: "Studente a Vita", 
                Gender.FEMALE: "Studentessa a Vita"
            },
            AspirationType.ONLINE_COURSE_CREATOR: {
                Gender.MALE: "Creatore di Corsi Online", 
                Gender.FEMALE: "Creatrice di Corsi Online"
            },
            AspirationType.PROFESSOR_EMERITUS: {
                Gender.MALE: "Professore Emerito", 
                Gender.FEMALE: "Professoressa Emerita"
            },
            AspirationType.SCHOOL_DROPOUT_SUCCESS: {
                Gender.MALE: "Successo da Dropout", 
                Gender.FEMALE: "Successo da Dropout"
            },
            AspirationType.STUDY_ABROAD: {
                Gender.MALE: "Studio all'Estero", 
                Gender.FEMALE: "Studio all'Estero"
            },
            AspirationType.TEACHER_OF_THE_YEAR: {
                Gender.MALE: "Insegnante dell'Anno", 
                Gender.FEMALE: "Insegnante dell'Anno"
            },
            AspirationType.TUTORING_BUSINESS: {
                Gender.MALE: "Business di Tutoraggio", 
                Gender.FEMALE: "Business di Tutoraggio"
            },
            
            # Viaggi
            AspirationType.AIRBNB_SUPERHOST: {
                Gender.MALE: "Superhost Airbnb", 
                Gender.FEMALE: "Superhost Airbnb"
            },
            AspirationType.BACKPACKER: {
                Gender.MALE: "Zainatore", 
                Gender.FEMALE: "Zainatrice"
            },
            AspirationType.CRUISE_ENJOYER: {
                Gender.MALE: "Amante delle Crociere", 
                Gender.FEMALE: "Amante delle Crociere"
            },
            AspirationType.CULTURAL_IMMERSION: {
                Gender.MALE: "Immersione Culturale", 
                Gender.FEMALE: "Immersione Culturale"
            },
            AspirationType.GLOBE_TROTTER: {
                Gender.MALE: "Globetrotter", 
                Gender.FEMALE: "Globetrotter"
            },
            AspirationType.LUXURY_TRAVELER: {
                Gender.MALE: "Viaggiatore di Lusso", 
                Gender.FEMALE: "Viaggiatrice di Lusso"
            },
            AspirationType.ROAD_TRIP_ADVENTURER: {
                Gender.MALE: "Avventuriero su Strada", 
                Gender.FEMALE: "Avventuriera su Strada"
            },
            AspirationType.SEVEN_WONDERS_VISITOR: {
                Gender.MALE: "Visitatore delle Sette Meraviglie", 
                Gender.FEMALE: "Visitatrice delle Sette Meraviglie"
            },
            AspirationType.VOLUNTOURISM: {
                Gender.MALE: "Volonturismo", 
                Gender.FEMALE: "Volonturismo"
            },
            
            # Divertimento
            AspirationType.CASINO_KING: {
                Gender.MALE: "Re del Casinò", 
                Gender.FEMALE: "Regina del Casinò"
            },
            AspirationType.COMEDY_CLUB_OWNER: {
                Gender.MALE: "Proprietario di Comedy Club", 
                Gender.FEMALE: "Proprietaria di Comedy Club"
            },
            AspirationType.ESCAPE_ROOM_DESIGNER: {
                Gender.MALE: "Designer di Escape Room", 
                Gender.FEMALE: "Designer di Escape Room"
            },
            AspirationType.FESTIVAL_GOER: {
                Gender.MALE: "Frequentatore di Festival", 
                Gender.FEMALE: "Frequentatrice di Festival"
            },
            AspirationType.KARAOKE_CHAMPION: {
                Gender.MALE: "Campione di Karaoke", 
                Gender.FEMALE: "Campionessa di Karaoke"
            },
            AspirationType.MOVIE_BUFF: {
                Gender.MALE: "Cinefilo", 
                Gender.FEMALE: "Cinefila"
            },
            AspirationType.PARTY_PLANNER: {
                Gender.MALE: "Organizzatore di Feste", 
                Gender.FEMALE: "Organizzatrice di Feste"
            },
            AspirationType.THEME_PARK_FANATIC: {
                Gender.MALE: "Fanatico di Parchi a Tema", 
                Gender.FEMALE: "Fanatica di Parchi a Tema"
            },
            AspirationType.VIDEO_GAME_COLLECTOR: {
                Gender.MALE: "Collezionista di Videogiochi", 
                Gender.FEMALE: "Collezionista di Videogiochi"
            },
            AspirationType.ZOO_ENTHUSIAST: {
                Gender.MALE: "Entusiasta dello Zoo", 
                Gender.FEMALE: "Entusiasta dello Zoo"
            }
        }
        value = mapping.get(self)

        if isinstance(value, dict):
            # Se il valore è un dizionario, restituisci la chiave per il genere corretto.
            # Se il genere NON_BINARY non è definito, usa una forma neutra o il maschile come fallback.
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            # Se è una stringa, è invariabile, restituiscila direttamente.
            return value
        else:
            # Fallback se l'aspirazione non è nella mappa
            return self.name.replace("_", " ").capitalize()

