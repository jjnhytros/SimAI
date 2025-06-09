# core/enums/event_types.py
from enum import Enum, auto
"""
Definizione dell'Enum EventType per gli eventi speciali che accadono nel mondo di SimAI.
Contiene sia eventi specifici/nominati sia categorie di eventi generici.
"""

class EventType(Enum):
    """Enum per i diversi tipi di eventi, raggruppati per categoria."""
    
    # --- Categoria: Eventi Accademici Specifici ---
    ACADEMIC_CONFERENCE = auto()
    ALUMNI_REUNION = auto()
    CAREER_FAIR = auto()
    DEBATE_TOURNAMENT = auto()
    EXAM_PERIOD = auto()
    GRADUATION_CEREMONY = auto()
    HACKATHON = auto()
    LANGUAGE_IMMERSION_CAMP = auto()
    MATH_OLYMPIAD = auto()
    RESEARCH_SYMPOSIUM = auto()
    ROBOTICS_COMPETITION = auto()
    SCIENCE_FAIR = auto()
    SPELLING_BEE = auto()
    STUDENT_ELECTIONS = auto()
    TEACHER_CONFERENCE = auto()
    UNIVERSITY_OPEN_DAY = auto()

    # --- Categoria: Eventi Ambientali ---
    BEACH_CLEANUP = auto()
    COMMUNITY_GARDEN_OPENING = auto()
    EARTH_HOUR_EVENT = auto()
    ECOLOGICAL_RESTORATION_PROJECT = auto()
    ENVIRONMENTAL_PROTEST = auto()
    FOREST_PLANTATION_DAY = auto()
    GREEN_TECH_EXPO = auto()
    NATURE_PHOTOGRAPHY_WORKSHOP = auto()
    RECYCLING_AWARENESS_DAY = auto()
    RENEWABLE_ENERGY_FAIR = auto()
    SUSTAINABLE_LIVING_SEMINAR = auto()
    URBAN_GARDENING_COURSE = auto()
    WATER_CONSERVATION_WORKSHOP = auto()
    WILDLIFE_CONSERVATION_TALK = auto()

    # --- Categoria: Eventi Artistici ---
    ART_AUCTION = auto()
    ARTIST_TALK = auto()
    ARTIST_RESIDENCY_OPENING = auto()
    CHILDREN_ART_WORKSHOP = auto()
    COMMUNITY_MURAL_PROJECT = auto()
    CRAFT_FAIR = auto()
    DIGITAL_ART_SHOWCASE = auto()
    GRAFFITI_CONTEST = auto()
    IMPROV_THEATER_SHOW = auto()
    INTERACTIVE_ART_INSTALLATION = auto()
    JEWELRY_MAKING_CLASS = auto()
    LIGHT_ART_FESTIVAL = auto()
    MURAL_PAINTING_EVENT = auto()
    PERFORMANCE_ART_SHOW = auto()
    PHOTOGRAPHY_CONTEST = auto()
    POTTERY_WORKSHOP = auto()
    SCULPTURE_EXHIBITION = auto()
    STREET_ART_FESTIVAL = auto()
    TATTOO_CONVENTION = auto()
    VINTAGE_FASHION_SHOW = auto()

    # --- Categoria: Eventi Civici e Governativi ---
    CITY_COUNCIL_SESSION = auto()
    ELECTION_DAY = auto()
    FOUNDATION_DAY_CEREMONY = auto()
    GOVERNOR_SPEECH = auto()
    INFRASTRUCTURE_INAUGURATION = auto()
    LAW_CHANGE_ANNOUNCEMENT = auto()
    MILITARY_PARADE = auto()
    NATIONAL_HOLIDAY_CEREMONY = auto()
    PUBLIC_POLICY_FORUM = auto()
    TAX_REFERENDUM = auto()

    # --- Categoria: Eventi Commerciali Specifici ---
    ANNUAL_STOCKHOLDERS_MEETING = auto()
    BUSINESS_NETWORKING_EVENT = auto()
    E_COMMERCE_SUMMIT = auto()
    ENTREPRENEURSHIP_WORKSHOP = auto()
    EXPORT_FORUM = auto()
    FARMERS_MARKET = auto()
    FASHION_WEEK = auto()
    FOOD_TRUCK_FESTIVAL = auto()
    FRANCHISE_EXPO = auto()
    HOLIDAY_MARKET = auto()
    INDUSTRY_TRADE_SHOW = auto()
    INVESTMENT_SEMINAR = auto()
    LOCAL_ARTISAN_FAIR = auto()
    PRODUCT_LAUNCH = auto()
    SEASONAL_SALE = auto()
    SHOPPING_NIGHT = auto()
    STARTUP_PITCH_EVENT = auto()

    # --- Categoria: Eventi Comunitari Specifici ---
    BLOCK_PARTY = auto()
    CHARITY_BAKE_SALE = auto()
    CHARITY_RUN = auto()
    CITIZEN_SCIENCE_PROJECT = auto()
    COMMUNITY_BONFIRE = auto()
    COMMUNITY_GARDEN_POTLUCK = auto()
    COMMUNITY_THEATER_SHOW = auto()
    CROSS_CULTURAL_EXCHANGE_FAIR = auto()
    FALL_HARVEST_FESTIVAL = auto()
    HISTORICAL_REENACTMENT = auto()
    INTERGENERATIONAL_STORYTELLING = auto()
    MULTICULTURAL_FOOD_FAIR = auto()
    NEIGHBORHOOD_CLEANUP_DAY = auto()
    PUBLIC_ART_UNVEILING = auto()
    REPAIR_CAFE = auto()
    SENIOR_CENTER_SOCIAL = auto()
    SPRING_FLOWER_FESTIVAL = auto()
    TOWN_HALL_MEETING = auto()
    WINTER_SOLSTICE_CELEBRATION = auto()
    YOUTH_TALENT_SHOW = auto()

    # --- Categoria: Eventi Culturali Specifici ---
    ANIME_CONVENTION = auto()
    ANTIQUE_APPRAISAL_EVENT = auto()
    BOOK_LAUNCH_PARTY = auto()
    CARNIVAL_PARADE = auto()
    CLASSICAL_MUSIC_RECITAL = auto()
    COMIC_CON = auto()
    COSPLAY_CONTEST = auto()
    CULTURAL_HERITAGE_DAY = auto()
    DANCE_FESTIVAL = auto()
    FOLKLORE_FESTIVAL = auto()
    HISTORIC_HOME_TOUR = auto()
    INDEPENDENT_FILM_FESTIVAL = auto()
    JAZZ_FESTIVAL = auto()
    LANTERN_FESTIVAL = auto()
    LITERARY_FESTIVAL = auto()
    MUSEUM_SLEEPOVER = auto()
    OPERA_PERFORMANCE = auto()
    POETRY_SLAM = auto()
    THEATER_PREMIERE = auto()
    WORLD_MUSIC_CONCERT = auto()

    # --- Categoria: Eventi Gastronomici ---
    BARBECUE_COMPETITION = auto()
    BEER_FESTIVAL = auto()
    CHEESE_TASTING_EVENT = auto()
    CHOCOLATE_FESTIVAL = auto()
    COCKTAIL_MIXING_CLASS = auto()
    COFFEE_CUPPING_SESSION = auto()
    COOKING_MASTERCLASS = auto()
    FARM_TO_TABLE_DINNER = auto()
    FOOD_CRITIC_PANEL = auto()
    GOURMET_POPUP_RESTAURANT = auto()
    INTERNATIONAL_FOOD_FAIR = auto()
    MICROBREWERY_TOUR = auto()
    PASTRY_WORKSHOP = auto()
    PIZZA_MAKING_CONTEST = auto()
    RESTAURANT_WEEK = auto()
    SOMMELIER_WORKSHOP = auto()
    SPICE_MARKET = auto()
    STREET_FOOD_FESTIVAL = auto()
    SUSHI_ROLLING_CLASS = auto()
    VEGAN_FOOD_EXPO = auto()
    WINE_TASTING_TOUR = auto()

    # --- Categoria: Eventi Personali Specifici (Generati dagli NPC) ---
    ANNIVERSARY_DINNER = auto()
    BABY_SHOWER = auto()
    BACHELOR_PARTY = auto()
    BIRTHDAY_PARTY = auto()
    BRIDAL_SHOWER = auto()
    DORM_PARTY = auto()
    FAMILY_REUNION = auto()
    FUNERAL = auto()
    GENDER_REVEAL_PARTY = auto()
    GRADUATION_PARTY = auto()
    HOUSE_PARTY = auto()
    NEIGHBORHOOD_BBQ = auto()
    PET_FUNERAL = auto()
    PROM_NIGHT = auto()
    RETIREMENT_PARTY = auto()
    SURPRISE_PARTY = auto()
    WEDDING = auto()
    WEDDING_ANNIVERSARY = auto()

    # --- Categoria: Eventi Ricreativi ---
    AMATEUR_RADIO_MEETUP = auto()
    BINGO_NIGHT = auto()
    BOARD_GAME_TOURNAMENT = auto()
    CAMPING_TRIP = auto()
    CARD_GAME_CHAMPIONSHIP = auto()
    COSPLAY_PHOTOSHOOT = auto()
    DIY_CRAFT_CIRCLE = auto()
    DRONE_RACING_EVENT = auto()
    ESCAPE_ROOM_OPENING = auto()
    FISHING_TOURNAMENT = auto()
    GARDEN_TOUR = auto()
    KARAOKE_CONTEST = auto()
    KITE_FLYING_FESTIVAL = auto()
    MINIATURE_PAINTING_WORKSHOP = auto()
    MODEL_RAILROAD_EXHIBITION = auto()
    MYSTERY_DINNER_PARTY = auto()
    OBSERVATORY_OPEN_NIGHT = auto()
    PARANORMAL_INVESTIGATION_EVENT = auto()
    PUZZLE_COMPETITION = auto()
    QUILTING_BEE = auto()
    STARGAZING_PARTY = auto()
    TABLE_ROLEPLAYING_SESSION = auto()
    TEDDY_BEAR_PICNIC = auto()
    VIDEO_GAME_TOURNAMENT = auto()

    # --- Categoria: Eventi Religiosi ---
    BLESSING_OF_THE_ANIMALS = auto()
    CANDLELIGHT_VIGIL = auto()
    CHURCH_BAZAAR = auto()
    COMMUNION_CELEBRATION = auto()
    DIWALI_FESTIVAL = auto()
    EASTER_EGG_HUNT = auto()
    FEAST_DAY_PROCESSION = auto()
    GOSPEL_CONCERT = auto()
    HANUKKAH_MENORAH_LIGHTING = auto()
    MEDITATION_RETREAT = auto()
    NATIVITY_PLAY = auto()
    PRAYER_CIRCLE = auto()
    RAMADAN_IFTAR = auto()
    RELIGIOUS_PILGRIMAGE = auto()
    SIKH_PARADE = auto()
    TEMPLE_DEDICATION = auto()
    VESPERS_SERVICE = auto()
    YOGA_FESTIVAL = auto()

    # --- Categoria: Eventi Rari / Emergenze ---
    BUILDING_COLLAPSE = auto()
    CIVIL_UNREST = auto()
    CYBER_ATTACK = auto()
    DISEASE_OUTBREAK = auto()
    DROUGHT_EMERGENCY = auto()
    EARTHQUAKE = auto()
    FINANCIAL_CRISIS = auto()
    FLASH_FLOOD = auto()
    GAS_LEAK = auto()
    HAZARDOUS_MATERIAL_SPILL = auto()
    INDUSTRIAL_ACCIDENT = auto()
    MAJOR_ACCIDENT = auto()
    METEORITE_STRIKE = auto()
    POWER_OUTAGE = auto()
    RARE_ANIMAL_SIGHTING = auto()
    RECORD_HEATWAVE = auto()
    TERRORIST_ATTACK = auto()
    TRANSPORT_DISASTER = auto()
    VOLCANIC_ERUPTION = auto()

    # --- Categoria: Eventi Scientifici ---
    ASTRONOMY_LECTURE = auto()
    BIOHACKING_MEETUP = auto()
    BOTANY_EXPEDITION = auto()
    CHEMISTRY_DEMONSTRATION = auto()
    CLIMATE_CHANGE_FORUM = auto()
    GENETICS_CONFERENCE = auto()
    MARINE_BIOLOGY_TOUR = auto()
    MATH_CIRCLE = auto()
    NEUROSCIENCE_SYMPOSIUM = auto()
    OCEANOGRAPHY_EXHIBITION = auto()
    PALEO_EXCAVATION_OPEN_DAY = auto()
    PHYSICS_SHOW = auto()
    PSYCHOLOGY_WORKSHOP = auto()
    SCIENCE_PUB_NIGHT = auto()
    SPACE_EXPLORATION_TALK = auto()
    VIRTUAL_REALITY_SCIENCE_TOUR = auto()
    WEATHER_OBSERVATORY_VISIT = auto()
    ZOOLOGY_LECTURE = auto()

    # --- Categoria: Eventi Sportivi Specifici ---
    AMATEUR_BOXING_TOURNAMENT = auto()
    ARCHERY_COMPETITION = auto()
    ARENA_FUSION_FINAL = auto()
    ARENA_FUSION_MATCH = auto()
    BEACH_VOLLEYBALL_TOURNAMENT = auto()
    BICYCLE_RACE = auto()
    CLIMBING_COMPETITION = auto()
    DRAGON_BOAT_RACE = auto()
    E_SPORTS_CHAMPIONSHIP = auto()
    EXTREME_SPORTS_DEMO = auto()
    GOLF_TOURNAMENT = auto()
    HALF_MARATHON = auto()
    MAJOR_CONCERT = auto()
    PROFESSIONAL_WRESTLING_EVENT = auto()
    ROLLER_DERBY_MATCH = auto()
    SAILING_REGATTA = auto()
    SKATEBOARDING_CONTEST = auto()
    STADIUM_CONCERT = auto()
    SWIMMING_GALA = auto()
    TRIATHLON = auto()
    ULTIMATE_FRISBEE_TOURNAMENT = auto()
    YOGA_MARATHON = auto()

    # --- Categoria: Eventi Tecnologici ---
    AI_ETHICS_FORUM = auto()
    APP_DEVELOPMENT_WORKSHOP = auto()
    BLOCKCHAIN_SUMMIT = auto()
    CYBERSECURITY_DRILL = auto()
    DATA_SCIENCE_HACKATHON = auto()
    DIGITAL_NOMAD_MEETUP = auto()
    DRONE_DEMO_DAY = auto()
    ELECTRONICS_FAIR = auto()
    GAMING_CONVENTION = auto()
    IOT_INNOVATION_CHALLENGE = auto()
    MAKER_FESTIVAL = auto()
    ROBOTICS_SHOWCASE = auto()
    SMART_CITY_EXPO = auto()
    TECH_JOB_FAIR = auto()
    TECH_STARTUP_DEMO_DAY = auto()
    TELECOMMUNICATIONS_EXPO = auto()
    VR_ESCAPE_ROOM_LAUNCH = auto()
    WEARABLE_TECH_SHOW = auto()
    WIFI_MAPPING_PROJECT = auto()

    # --- Categoria: Tipi di Evento Generici / Ricorrenti ---
    ART_EXHIBITION = auto()
    COMMUNITY_GATHERING = auto()
    COWORKING_SPACE_EVENT = auto()
    EVENING_COURSE = auto()
    FESTIVAL = auto()
    FIXED_VENUE_FREE_ACTIVITY = auto()
    LIVE_CONCERT = auto()
    LOCAL_MARKET_DAY = auto()
    NETWORKING_MIXER = auto()
    OUTDOOR_CINEMA = auto()
    PUBLIC_LECTURE = auto()
    SEMINAR_LECTURE = auto()
    SPORTS_PRACTICE_MATCH = auto()
    VOLUNTEERING_OPPORTUNITY = auto()
    WEEKLY_MEETING = auto()
    WEEKEND_GROUP_ACTIVITY = auto()
    WORKSHOP = auto()
    
    def display_name_it(self) -> str:
        """Restituisce un nome leggibile in italiano per il tipo di evento."""
        mapping = {
            # Generici
            EventType.WEEKLY_MEETING: "Incontro Settimanale",
            EventType.ART_EXHIBITION: "Esposizione d'Arte",
            EventType.EVENING_COURSE: "Corso Serale",
            EventType.WEEKEND_GROUP_ACTIVITY: "Attività di Gruppo (Weekend)",
            EventType.FIXED_VENUE_FREE_ACTIVITY: "Attività Libera",
            EventType.LIVE_CONCERT: "Concerto dal Vivo",
            EventType.LOCAL_MARKET_DAY: "Mercato Locale",
            EventType.VOLUNTEERING_OPPORTUNITY: "Volontariato",
            EventType.SPORTS_PRACTICE_MATCH: "Partita/Allenamento Amatoriale",
            EventType.WORKSHOP: "Workshop",
            EventType.SEMINAR_LECTURE: "Seminario",
            EventType.COMMUNITY_GATHERING: "Raduno Comunitario",
            EventType.FESTIVAL: "Festival",
            # Specifici
            EventType.FOUNDATION_DAY_CEREMONY: "Cerimonia del Giorno della Fondazione",
            EventType.INDEPENDENT_FILM_FESTIVAL: "Festival del Cinema Indipendente",
            EventType.ARENA_FUSION_MATCH: "Partita di Arena Fusion",
            EventType.SPRING_FLOWER_FESTIVAL: "Festival dei Fiori di Primavera",
            EventType.REPAIR_CAFE: "Repair Café",
            EventType.POWER_OUTAGE: "Blackout",
            EventType.DISEASE_OUTBREAK: "Focolaio Epidemico",
            EventType.ELECTION_DAY: "Giorno delle Elezioni",
            EventType.GOVERNOR_SPEECH: "Discorso del Governatore",
            EventType.BIRTHDAY_PARTY: "Festa di Compleanno",
            EventType.WEDDING: "Matrimonio",
            EventType.FUNERAL: "Funerale",
            EventType.HOUSE_PARTY: "Festa in Casa",
            EventType.DORM_PARTY: "Festa nel Dormitorio",
            EventType.NEIGHBORHOOD_BBQ: "Barbecue di Quartiere",
            EventType.ACADEMIC_CONFERENCE: "Conferenza Accademica",
            EventType.GRADUATION_CEREMONY: "Cerimonia di Laurea",
            EventType.EXAM_PERIOD: "Sessione d'Esame",
            EventType.INDUSTRIAL_ACCIDENT: "Incidente Industriale",
            EventType.PRODUCT_LAUNCH: "Lancio di Prodotto",
            EventType.FASHION_WEEK: "Settimana della Moda",
            EventType.SEASONAL_SALE: "Saldi Stagionali",
            EventType.CHARITY_RUN: "Corsa di Beneficenza",
            EventType.POETRY_SLAM: "Poetry Slam",
            EventType.THEATER_PREMIERE: "Prima Teatrale",
        }
        # Fallback alla formattazione generica se non in mappa
        return mapping.get(self, self.name.replace("_", " ").title())