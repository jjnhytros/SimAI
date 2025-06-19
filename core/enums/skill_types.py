# core/enums/skill_types.py
from enum import Enum, auto

from core.enums.genders import Gender
"""
Definizione dell'Enum 'SkillType' per rappresentare i tipi di abilità
che gli NPC possono sviluppare in SimAI.
"""

class SkillType(Enum):
    # --- Da Categorizzare
    AI_DEVELOPMENT = auto()
    ART_KNOWLEDGE = auto()
    CANDLE_CRAFT = auto()
    CULINARY_KNOWLEDGE = auto()
    DESIGN = auto()
    DISC_SPORTS = auto()
    DJING = auto()
    DRAWING = auto()
    GAMING = auto()
    HIKING = auto()
    IMPROV = auto()
    LEATHERWORK = auto()
    MASSAGE = auto()
    MEDITATION = auto()
    MODELING = auto()
    MUSICIANSHIP = auto()
    PERFORMING = auto()
    PERFUMERY = auto()
    READING = auto()
    RESTORATION = auto()
    RHETORIC = auto()
    ROLEPLAYING = auto()
    SEWING = auto()
    SKATING = auto()
    SOAP_CRAFT = auto()
    SPELUNKING = auto()
    SPORTS = auto()
    TEA_CEREMONY = auto()
    WINE_KNOWLEDGE = auto()

    """Enum per i diversi tipi di abilità (skills)."""

    BOTANICAL_ART = auto()
    GLASS_ART = auto()
    TEXTILE_ART = auto()
    WRITING = auto()
    INTUITION = auto()
    ORNITHOLOGY = auto()
    PROBLEM_SOLVING = auto()
    ASTROLOGY = auto()
    ASTRONOMY = auto()
    RESEARCH = auto()
    CHEMISTRY = auto()
    BOTANY = auto()
    HISTORY = auto()
    GEOGRAPHY = auto()
    PSYCHOLOGY = auto()
    ARCHITECTURE = auto()
    MEMORY = auto()
    CRYPTOGRAPHY = auto()
    STRATEGY = auto()
    MYTHOLOGY = auto()
    LITERATURE = auto()
    AI_PROGRAMMING = auto()
    CYCLING = auto()
    KAYAKING = auto()
    VOLLEYBALL = auto()
    FRISBEE = auto()
    NAVIGATION = auto()
    GEOCACHING = auto()
    CLIMBING = auto()
    WINTER_SPORTS = auto()
    GEOLOGY = auto()
    EXPLORATION = auto()
    SPELEOLOGY = auto()
    PADDLEBOARDING = auto()
    CANYONING = auto()
    URBAN_EXPLORATION = auto()
    SKIPPING = auto()
    BREWING = auto()
    PATIENCE = auto()
    MODEL_BUILDING = auto()
    TERRARIUM_DESIGN = auto()
    WINE_APPRECIATION = auto()
    GENEALOGY = auto()
    CULINARY_ARTS = auto()
    ART_APPRECIATION = auto()
    TEA_APPRECIATION = auto()
    BALLOON_TWISTING = auto()
    COMEDY_APPRECIATION = auto()
    THEATER_APPRECIATION = auto()
    CULINARY_EXPLORATION = auto()
    PERFORMANCE_ART = auto()
    TRIVIA = auto()
    ARCADE_GAMING = auto()
    MUSIC_APPRECIATION = auto()
    SOCIALIZING = auto()
    ORIENTEERING = auto()
    DEDUCTION = auto()
    SENSUAL_DANCING = auto()
    ROMANTIC_WRITING = auto()
    SENSUAL_RELAXATION = auto()
    TANGO = auto()
    SENSUAL_TASTING = auto()
    ARTISTIC_EXPRESSION = auto()
    SENSUAL_SWIMMING = auto()
    MASSAGE_THERAPY = auto()
    SEDUCTIVE_DANCE = auto()
    KISSING_TECHNIQUE = auto()
    TANTRIC_YOGA = auto()
    SENSUAL_COOKING = auto()
    MUSIC_PERFORMANCE = auto()
    INTIMACY = auto()
    EROTIC_PHOTOGRAPHY = auto()
    PERFUME_CRAFTING = auto()
    IMAGINATION = auto()
    AROMATHERAPY = auto()
    ROMANTIC_EXPRESSION = auto()

    # ================= CATEGORIA 1: ABILITÀ MENTALI (50) =================
    ACADEMIC_WRITING = auto()
    ACTUARIAL_SCIENCE = auto()
    ARTIFICIAL_INTELLIGENCE = auto()
    ASTROPHYSICS = auto()
    BEHAVIORAL_PSYCHOLOGY = auto()
    BIOINFORMATICS = auto()
    BUDGETING = auto()
    CALCULUS = auto()
    COGNITIVE_BIAS_ANALYSIS = auto()
    COGNITIVE_SCIENCE = auto()
    COMPLEX_PROBLEM_SOLVING = auto()
    CRITICAL_THINKING = auto()
    CRYPTANALYSIS = auto()
    CRYPTOCURRENCY = auto()
    CYBERSECURITY = auto()
    DATA_ANALYSIS = auto()
    DEBATE = auto()
    ECONOMICS = auto()
    EPIDEMIOLOGY = auto()
    ETHICAL_HACKING = auto()
    FORENSIC_SCIENCE = auto()
    FUTURE_FORECASTING = auto()
    GAME_THEORY = auto()
    GENETICS = auto()
    GEOPOLITICS = auto()
    HISTORICAL_ANALYSIS = auto()
    LINGUISTICS = auto()
    LOGIC = auto()
    MARKET_ANALYSIS = auto()
    MEMORY_TRAINING = auto()
    MICROBIOLOGY = auto()
    NANOTECHNOLOGY = auto()
    NEUROSCIENCE = auto()
    PHILOSOPHY = auto()
    PROGRAMMING = auto()
    QUANTUM_COMPUTING = auto()
    QUANTUM_MECHANICS = auto()
    RESEARCH_DEBATE = auto()
    RESEARCH_METHODOLOGY = auto()
    ROBOTICS = auto()
    ROCKET_SCIENCE = auto()
    SCIENTIFIC_METHOD = auto()
    SEMIOTICS = auto()
    SOCIOLOGY = auto()
    STATISTICS = auto()
    STRATEGIC_PLANNING = auto()
    SYSTEMS_ANALYSIS = auto()
    TEACHING = auto()
    TECHNICAL_WRITING = auto()
    VIRTUAL_REALITY_DESIGN = auto()
    # ================= CATEGORIA 2: ABILITÀ FISICHE (50) =================
    ACROBATICS = auto()
    AERIAL_ARTS = auto()
    ARCHERY = auto()
    BALANCING = auto()
    BASEBALL = auto()
    BASKETBALL = auto()
    BOXING = auto()
    CALISTHENICS = auto()
    CAPOEIRA = auto()
    CIRQUE_SKILLS = auto()
    CROSSFIT = auto()
    DANCING = auto()
    DIVING = auto()
    ENDURANCE_TRAINING = auto()
    FENCING = auto()
    FITNESS = auto()
    FLEXIBILITY = auto()
    GYMNASTICS = auto()
    HORSE_RIDING = auto()
    ICE_SKATING = auto()
    JOGGING = auto()
    JUGGLING = auto()
    MARTIAL_ARTS = auto()
    MARTIAL_WEAPONS = auto()
    MOUNTAIN_CLIMBING = auto()
    PARKOUR = auto()
    PHYSICAL_THERAPY = auto()
    PILATES = auto()
    POLEDANCE = auto()
    POSTURE_CORRECTION = auto()
    ROCK_CLIMBING = auto()
    ROLLERBLADING = auto()
    RUGBY = auto()
    RUNNING = auto()
    SCUBA_DIVING = auto()
    SKATEBOARDING = auto()
    SKIING = auto()
    SNOWBOARDING = auto()
    SOCCER = auto()
    STRENGTH_TRAINING = auto()
    SURFING = auto()
    SWIMMING = auto()
    TAI_CHI = auto()
    TENNIS = auto()
    TRACK_FIELD = auto()
    TRAMPOLINING = auto()
    WEIGHTLIFTING = auto()
    WELLNESS = auto()
    YOGA = auto()

    # ================= CATEGORIA 3: ABILITÀ SOCIALI (50) =================
    ACTIVE_LISTENING = auto()
    CHARISMA = auto()
    CHARM = auto()
    COLLABORATION = auto()
    COMEDY = auto()
    COMMUNITY_ORGANIZING = auto()
    CONFLICT_RESOLUTION = auto()
    CROWD_MANAGEMENT = auto()
    CULTURAL_SENSITIVITY = auto()
    DECEPTION_DETECTION = auto()
    DIPLOMACY = auto()
    EMPATHY_DEVELOPMENT = auto()
    ETIQUETTE = auto()
    EVENT_PLANNING = auto()
    FAMILY_COUNSELING = auto()
    FRIENDSHIP_MAINTENANCE = auto()
    GROUP_FACILITATION = auto()
    HUMOR_TIMING = auto()
    INFLUENCE = auto()
    INTERCULTURAL_COMMUNICATION = auto()
    INTERVIEWING = auto()
    INTIMACY_BUILDING = auto()
    LEADERSHIP = auto()
    MEDIATION = auto()
    MENTORING = auto()
    MISCHIEF = auto()
    MOTIVATIONAL_SPEAKING = auto()
    NEGOTIATION = auto()
    NETWORKING = auto()
    NONVERBAL_COMMUNICATION = auto()
    PARENTING = auto()
    PERSONAL_BRANDING = auto()
    PERSUASION = auto()
    PERSUASIVE_WRITING = auto()
    POLITICAL_CAMPAIGNING = auto()
    PRESENTATION = auto()
    PUBLIC_SPEAKING = auto()
    RELATIONSHIP_BUILDING = auto()
    ROMANTIC_GESTURES = auto()
    SEDUCTION = auto()
    SELF_DISCLOSURE = auto()
    SOCIAL_INTELLIGENCE = auto()
    SOCIAL_MEDIA = auto()
    SOCIAL_PSYCHOLOGY = auto()
    STORYTELLING = auto()
    SUPPORTIVE_LISTENING = auto()
    TEAM_BUILDING = auto()
    THERAPEUTIC_COMMUNICATION = auto()
    TRUST_BUILDING = auto()
    VULNERABILITY_SHARING = auto()

    # ================= CATEGORIA 4: ABILITÀ CREATIVE (50) =================
    ACTING = auto()
    ANIMATION = auto()
    ARCHITECTURAL_DESIGN = auto()
    BODY_PAINTING = auto()
    CALLIGRAPHY = auto()
    CHARACTER_DESIGN = auto()
    CHOREOGRAPHY = auto()
    COMIC_ART = auto()
    COMPOSITION = auto()
    COSTUME_DESIGN = auto()
    CREATIVE_DIRECTION = auto()
    CREATIVE_WRITING = auto()
    DIGITAL_SCULPTING = auto()
    DIGITAL_ART = auto()
    DJ_MIXING = auto()
    DRUMS = auto()
    FABRICATION = auto()
    FABRIC_DYEING = auto()
    FASHION_DESIGN = auto()
    FILM_DIRECTING = auto()
    STREET_ART = auto()
    FLOWER_ARRANGING = auto()
    GAME_DESIGN = auto()
    GLASSBLOWING = auto()
    GRAPHIC_DESIGN = auto()
    GUITAR = auto()
    ILLUSTRATION = auto()
    IMPROVISATION = auto()
    INDUSTRIAL_DESIGN = auto()
    INTERIOR_DESIGN = auto()
    JEWELRY_MAKING = auto()
    LANDSCAPE_DESIGN = auto()
    LIGHT_DESIGN = auto()
    LYRICS_WRITING = auto()
    MAKEUP_ARTISTRY = auto()
    MUSIC_COMPOSITION = auto()
    PAINTING = auto()
    PHOTOGRAPHY = auto()
    PIANO = auto()
    POETRY = auto()
    POTTERY = auto()
    PRODUCT_DESIGN = auto()
    PUPPETRY = auto()
    SCULPTING = auto()
    SINGING = auto()
    SONGWRITING = auto()
    STORYBOARDING = auto()
    TATTOO_ART = auto()
    UX_UI_DESIGN = auto()
    VIOLIN = auto()
    VISUAL_EFFECTS = auto()
    WOOD_CARVING = auto()

    # ================= CATEGORIA 5: ABILITÀ PRATICHE (50) =================
    AGRICULTURE = auto()
    ANIMAL_HUSBANDRY = auto()
    AQUAPONICS = auto()
    AUTOMOTIVE_REPAIR = auto()
    BAKING = auto()
    BARTENDING = auto()
    BEEKEEPING = auto()
    CANDLE_MAKING = auto()
    CARPENTRY = auto()
    CHEESE_MAKING = auto()
    CLOCKMAKING = auto()
    CRAFTING = auto()
    COOKING = auto()
    ELECTRICAL_WORK = auto()
    EMBROIDERY = auto()
    FARMING = auto()
    FERMENTATION = auto()
    FIREWORK_CRAFTING = auto()
    FIRST_AID = auto()
    PAPER_CRAFT = auto()
    FISHING = auto()
    FORAGING = auto()
    GARDENING = auto()
    GOURMET_COOKING = auto()
    HANDINESS = auto()
    HERBALISM = auto()
    HOME_REPAIR = auto()
    HVAC = auto()
    HYDROPONICS = auto()
    KNITTING = auto()
    KNOT_TYING = auto()
    LEATHERWORKING = auto()
    MAPLE_SYRUP_PRODUCTION = auto()
    MECHANICS = auto()
    METALWORKING = auto()
    MIXOLOGY = auto()
    MUSHROOM_CULTIVATION = auto()
    ORGANIZING = auto()
    PERMACULTURE = auto()
    PLUMBING = auto()
    PRESERVATION = auto()
    QUILTING = auto()
    SAUSAGE_MAKING = auto()
    SOAP_MAKING = auto()
    STONE_MASONRY = auto()
    SURVIVAL_SKILLS = auto()
    TAILORING = auto()
    TIME_MANAGEMENT = auto()
    VINTNING = auto()
    WEAVING = auto()
    WINE_MAKING = auto()
    WOODWORKING = auto()

    # ================= CATEGORIA 6: ABILITÀ ROMANTICHE/SENSUALI (50) =================
    AFFECTION_EXPRESSION = auto()
    AFTERCARE_PROTOCOLS = auto()
    AROMA_THERAPY = auto()
    BDSM_SAFETY = auto()
    BODY_LANGUAGE_READING = auto()
    BREATHWORK_SYNC = auto()
    CANDLE_MASSAGE = auto()
    CONSENT_COMMUNICATION = auto()
    COURTSHIP_RITUALS = auto()
    DANCE_SENSUAL = auto()
    DESIRE_ARTICULATION = auto()
    DESIRE_FACILITATION = auto()
    EMOTIONAL_INTIMACY = auto()
    ENERGY_EXCHANGE = auto()
    EROTIC_DANCE = auto()
    EROTIC_MASSAGE = auto()
    EROTIC_STORYTELLING = auto()
    EYE_CONTACT_MASTERY = auto()
    FETISH_APPRECIATION = auto()
    FLIRTATION_TECHNIQUES = auto()
    FOREPLAY_MASTERY = auto()
    INTIMACY_CHOREOGRAPHY = auto()
    INTIMACY_COACHING = auto()
    KINK_NEGOTIATION = auto()
    LINGERIE_SELECTION = auto()
    LOVE_LANGUAGE_APPLICATION = auto()
    LOVE_LETTER_WRITING = auto()
    MOOD_CREATION = auto()
    MULTIPLE_ORGASM = auto()
    NON_MONOGAMY_NAVIGATION = auto()
    PARTNER_OBSERVATION = auto()
    PHYSICAL_INTIMACY = auto()
    PLEASURE_DELAY = auto()
    PLEASURE_MAPPING = auto()
    ROMANCE_PLANNING = auto()
    ROMANTIC_GESTURE = auto()
    SENSUAL_FEEDING = auto()
    SENSUAL_TOUCH = auto()
    SEXUAL_HEALTH = auto()
    SEXUAL_POSITIONS = auto()
    SEX_TOY_KNOWLEDGE = auto()
    SPONTANEITY_CULTIVATION = auto()
    TANTRIC_PRACTICES = auto()
    TEASING_TECHNIQUES = auto()
    TEMPERATURE_PLAY = auto()
    TOUCH_TYPING = auto()
    TRUST_DEEPENING = auto()
    VOYEURISM_CONSENT = auto()
    # VULNERABILITY_SHARING = auto()
    WHISPERING_TECHNIQUES = auto()

    # ================= CATEGORIA 7: ABILITÀ PER BAMBINI (50) =================
    ART_EXPRESSION_CHILD = auto()
    BASIC_COOKING_CHILD = auto()
    BASIC_HYGIENE_CHILD = auto()
    BICYCLE_RIDING_CHILD = auto()
    BUDGETING_CHILD = auto()
    CIVIC_RESPONSIBILITY = auto()
    CLIMBING_SAFETY = auto()
    COMPUTER_BASICS_CHILD = auto()
    CONFLICT_RESOLUTION_CHILD = auto()
    CRAFTING_CHILD = auto()
    CREATIVITY_CHILD = auto()
    CRITICAL_THINKING_CHILD = auto()
    DANCE_BASICS_CHILD = auto()
    DECISION_MAKING_CHILD = auto()
    EMOTION_REGULATION_CHILD = auto()
    ENVIRONMENTAL_AWARENESS = auto()
    FINE_MOTOR_CHILD = auto()
    FIRE_SAFETY = auto()
    FRIENDSHIP_SKILLS_CHILD = auto()
    GARDENING_CHILD = auto()
    GOAL_SETTING_CHILD = auto()
    GROSS_MOTOR_CHILD = auto()
    HOMEWORK_MANAGEMENT = auto()
    IMAGINATIVE_PLAY = auto()
    INTERNET_SAFETY = auto()
    LANGUAGE_DEVELOPMENT = auto()
    MAP_READING = auto()
    MATH_FOUNDATIONS = auto()
    MEMORY_GAMES = auto()
    MENTAL_CHILD = auto()
    MORAL_DEVELOPMENT = auto()
    MOTOR_CHILD = auto()
    MUSIC_APPRECIATION_CHILD = auto()
    NATURE_EXPLORATION = auto()
    PET_CARE_CHILD = auto()
    PLANT_CARE = auto()
    PROBLEM_SOLVING_CHILD = auto()
    PUBLIC_SPEAKING_CHILD = auto()
    PUZZLE_SOLVING = auto()
    READING_COMPREHENSION = auto()
    RESILIENCE_BUILDING = auto()
    SAFETY_RULES = auto()
    SCIENCE_CURIOSITY = auto()
    SELF_CARE_CHILD = auto()
    SHARING_PRACTICE = auto()
    SOCIAL_CHILD = auto()
    SPORTS_FUNDAMENTALS = auto()
    TEAM_SPORTS = auto()
    TIME_PERCEPTION = auto()
    WATER_SAFETY = auto()

    def display_name_it(self, gender: 'Gender') -> str:
        """
        Restituisce un nome leggibile per l'abilità.
        La firma accetta 'gender' per coerenza.
        """
        # La maggior parte dei nomi delle abilità sono sostantivi e invariabili
        mapping = {
        # --- Da categorizzare
            SkillType.DJING: "DJing",
            SkillType.DRAWING: "Disegno",
            SkillType.SEWING: "Cucito",
            SkillType.LEATHERWORK: "Lavoro cuoio",
            SkillType.MODELING: "Modellismo",
            SkillType.DESIGN: "Progettazione",
            SkillType.RESTORATION: "Restauro",
            SkillType.READING: "Lettura",
            SkillType.RHETORIC: "Retorica",
            SkillType.ART_KNOWLEDGE: "Conoscenza arte",
            SkillType.MEDITATION: "Meditazione",
            SkillType.ORNITHOLOGY: "Ornitologia",
            SkillType.AI_DEVELOPMENT: "Sviluppo AI",
            SkillType.HIKING: "Escursionismo",
            SkillType.SPORTS: "Sport",
            SkillType.CLIMBING: "Arrampicata",
            SkillType.CYCLING: "Ciclismo",
            SkillType.KAYAKING: "Kayak",
            SkillType.VOLLEYBALL: "Pallavolo",
            SkillType.DISC_SPORTS: "Sport con disco",
            SkillType.NAVIGATION: "Navigazione",
            SkillType.GEOCACHING: "Geocaching",
            SkillType.WINTER_SPORTS: "Sport invernali",
            SkillType.GEOLOGY: "Geologia",
            SkillType.SPELUNKING: "Speleologia",
            SkillType.PADDLEBOARDING: "Paddleboarding",
            SkillType.SKATING: "Pattinaggio",
            SkillType.BREWING: "Fermentazione",
            SkillType.PATIENCE: "Pazienza",
            SkillType.CANDLE_CRAFT: "Creazione candele",
            SkillType.SOAP_CRAFT: "Saponificazione",
            SkillType.WINE_KNOWLEDGE: "Conoscenza vini",
            SkillType.GENEALOGY: "Genealogia",
            SkillType.CULINARY_KNOWLEDGE: "Conoscenza culinaria",
            SkillType.TEA_CEREMONY: "Cerimonia del tè",
            SkillType.BALLOON_TWISTING: "Modellazione palloncini",
            SkillType.GAMING: "Gaming",
            SkillType.TRIVIA: "Curiosità",
            SkillType.IMPROV: "Improvvisazione",
            SkillType.ROLEPLAYING: "Interpretazione ruoli",
            SkillType.MUSICIANSHIP: "Musica",
            SkillType.PERFORMING: "Performance",
            SkillType.MASSAGE: "Massaggio",
            SkillType.PERFUMERY: "Profumeria",

            # ================= ABILITÀ MENTALI =================
            SkillType.ACADEMIC_WRITING: "Scrittura Accademica",
            SkillType.ACTUARIAL_SCIENCE: "Attuariale",
            SkillType.ARTIFICIAL_INTELLIGENCE: "Intelligenza Artificiale",
            SkillType.ASTROPHYSICS: "Astrofisica",
            SkillType.BEHAVIORAL_PSYCHOLOGY: "Psicologia Comportamentale",
            SkillType.BIOINFORMATICS: "Bioinformatica",
            SkillType.BUDGETING: "Bilancio",
            SkillType.CALCULUS: "Calcolo",
            SkillType.COGNITIVE_BIAS_ANALYSIS: "Analisi Pregiudizi Cognitivi",
            SkillType.COGNITIVE_SCIENCE: "Scienza Cognitiva",
            SkillType.COMPLEX_PROBLEM_SOLVING: "Risoluzione Problemi Complessi",
            SkillType.CRITICAL_THINKING: "Pensiero Critico",
            SkillType.CRYPTANALYSIS: "Crittoanalisi",
            SkillType.CRYPTOCURRENCY: "Criptovaluta",
            SkillType.CYBERSECURITY: "Cybersecurity",
            SkillType.DATA_ANALYSIS: "Analisi Dati",
            SkillType.DEBATE: "Dibattito",
            SkillType.ECONOMICS: "Economia",
            SkillType.EPIDEMIOLOGY: "Epidemiologia",
            SkillType.ETHICAL_HACKING: "Hacking Etico",
            SkillType.FORENSIC_SCIENCE: "Scienza Forense",
            SkillType.FUTURE_FORECASTING: "Previsione Futuro",
            SkillType.GAME_THEORY: "Teoria dei Giochi",
            SkillType.GENETICS: "Genetica",
            SkillType.GEOPOLITICS: "Geopolitica",
            SkillType.HISTORICAL_ANALYSIS: "Analisi Storica",
            SkillType.LINGUISTICS: "Linguistica",
            SkillType.LOGIC: "Logica",
            SkillType.MARKET_ANALYSIS: "Analisi di Mercato",
            SkillType.MEMORY_TRAINING: "Allenamento Memoria",
            SkillType.MICROBIOLOGY: "Microbiologia",
            SkillType.NANOTECHNOLOGY: "Nanotecnologia",
            SkillType.NEUROSCIENCE: "Neuroscienze",
            SkillType.PHILOSOPHY: "Filosofia",
            SkillType.PROGRAMMING: "Programmazione",
            SkillType.QUANTUM_COMPUTING: "Computazione Quantistica",
            SkillType.QUANTUM_MECHANICS: "Meccanica Quantistica",
            SkillType.RESEARCH_DEBATE: "Ricerca e Dibattito",
            SkillType.RESEARCH_METHODOLOGY: "Metodologia di Ricerca",
            SkillType.ROBOTICS: "Robotica",
            SkillType.ROCKET_SCIENCE: "Scienza Missilistica",
            SkillType.SCIENTIFIC_METHOD: "Metodo Scientifico",
            SkillType.SEMIOTICS: "Semiotica",
            SkillType.SOCIOLOGY: "Sociologia",
            SkillType.STATISTICS: "Statistica",
            SkillType.STRATEGIC_PLANNING: "Pianificazione Strategica",
            SkillType.SYSTEMS_ANALYSIS: "Analisi Sistemi",
            SkillType.TEACHING: "Insegnamento",
            SkillType.TECHNICAL_WRITING: "Scrittura Tecnica",
            SkillType.VIRTUAL_REALITY_DESIGN: "Design Realtà Virtuale",

            # ================= ABILITÀ FISICHE =================
            SkillType.ACROBATICS: "Acrobatica",
            SkillType.AERIAL_ARTS: "Arti Aeree",
            SkillType.ARCHERY: "Tiro con l'Arco",
            SkillType.BALANCING: "Equilibrio",
            SkillType.BASEBALL: "Baseball",
            SkillType.BASKETBALL: "Pallacanestro",
            SkillType.BOXING: "Boxe",
            SkillType.CALISTHENICS: "Calistenia",
            SkillType.CAPOEIRA: "Capoeira",
            SkillType.CIRQUE_SKILLS: "Arti Circensi",
            SkillType.CROSSFIT: "Crossfit",
            SkillType.DANCING: "Ballo",
            SkillType.DIVING: "Tuffi",
            SkillType.ENDURANCE_TRAINING: "Allenamento Resistenza",
            SkillType.FENCING: "Scherma",
            SkillType.FITNESS: "Fitness",
            SkillType.FLEXIBILITY: "Flessibilità",
            SkillType.GYMNASTICS: "Ginnastica",
            SkillType.HORSE_RIDING: "Equitazione",
            SkillType.ICE_SKATING: "Pattinaggio su Ghiaccio",
            SkillType.JOGGING: "Jogging",
            SkillType.JUGGLING: "Giocoleria",
            SkillType.MARTIAL_ARTS: "Arti Marziali",
            SkillType.MARTIAL_WEAPONS: "Armi Marziali",
            SkillType.MOUNTAIN_CLIMBING: "Arrampicata Montagna",
            SkillType.PARKOUR: "Parkour",
            SkillType.PHYSICAL_THERAPY: "Fisioterapia",
            SkillType.PILATES: "Pilates",
            SkillType.POLEDANCE: "Pole Dance",
            SkillType.POSTURE_CORRECTION: "Correzione Postura",
            SkillType.ROCK_CLIMBING: "Arrampicata",
            SkillType.ROLLERBLADING: "Pattinaggio a Rotelle",
            SkillType.RUGBY: "Rugby",
            SkillType.RUNNING: "Corsa",
            SkillType.SCUBA_DIVING: "Subacquea",
            SkillType.SKATEBOARDING: "Skateboard",
            SkillType.SKIING: "Sci",
            SkillType.SNOWBOARDING: "Snowboard",
            SkillType.SOCCER: "Calcio",
            SkillType.STRENGTH_TRAINING: "Allenamento Forza",
            SkillType.SURFING: "Surf",
            SkillType.SWIMMING: "Nuoto",
            SkillType.TAI_CHI: "Tai Chi",
            SkillType.TENNIS: "Tennis",
            SkillType.TRACK_FIELD: "Atletica Leggera",
            SkillType.TRAMPOLINING: "Trampolino",
            SkillType.WEIGHTLIFTING: "Sollevamento Pesi",
            SkillType.WELLNESS: "Benessere",
            SkillType.YOGA: "Yoga",

            # ================= ABILITÀ SOCIALI =================
            SkillType.ACTIVE_LISTENING: "Ascolto Attivo",
            SkillType.CHARISMA: "Carisma",
            SkillType.CHARM: "Fascino",
            SkillType.COLLABORATION: "Collaborazione",
            SkillType.COMEDY: "Commedia",
            SkillType.COMMUNITY_ORGANIZING: "Organizzazione Comunitaria",
            SkillType.CONFLICT_RESOLUTION: "Risoluzione Conflitti",
            SkillType.CROWD_MANAGEMENT: "Gestione Folla",
            SkillType.CULTURAL_SENSITIVITY: "Sensibilità Culturale",
            SkillType.DECEPTION_DETECTION: "Rilevamento Inganno",
            SkillType.DIPLOMACY: "Diplomazia",
            SkillType.EMPATHY_DEVELOPMENT: "Sviluppo Empatia",
            SkillType.ETIQUETTE: "Galateo",
            SkillType.EVENT_PLANNING: "Pianificazione Eventi",
            SkillType.FAMILY_COUNSELING: "Consulenza Familiare",
            SkillType.FRIENDSHIP_MAINTENANCE: "Mantenimento Amicizie",
            SkillType.GROUP_FACILITATION: "Facilitazione Gruppi",
            SkillType.HUMOR_TIMING: "Tempismo Comico",
            SkillType.INFLUENCE: "Influenza",
            SkillType.INTERCULTURAL_COMMUNICATION: "Comunicazione Interculturale",
            SkillType.INTERVIEWING: "Intervista",
            SkillType.INTIMACY_BUILDING: "Costruzione Intimità",
            SkillType.LEADERSHIP: "Leadership",
            SkillType.MEDIATION: "Mediazione",
            SkillType.MENTORING: "Mentoring",
            SkillType.MISCHIEF: "Malizia",
            SkillType.MOTIVATIONAL_SPEAKING: "Parlare Motivazionale",
            SkillType.NEGOTIATION: "Negoziazione",
            SkillType.NETWORKING: "Networking",
            SkillType.NONVERBAL_COMMUNICATION: "Comunicazione Non Verbale",
            SkillType.PARENTING: "Genitorialità",
            SkillType.PERSONAL_BRANDING: "Personal Branding",
            SkillType.PERSUASION: "Persuasione",
            SkillType.PERSUASIVE_WRITING: "Scrittura Persuasiva",
            SkillType.POLITICAL_CAMPAIGNING: "Campagne Politiche",
            SkillType.PRESENTATION: "Presentazione",
            SkillType.PUBLIC_SPEAKING: "Parlare in Pubblico",
            SkillType.RELATIONSHIP_BUILDING: "Costruzione Relazioni",
            SkillType.ROMANTIC_GESTURES: "Gestualità Romantica",
            SkillType.SEDUCTION: "Seduzione",
            SkillType.SELF_DISCLOSURE: "Autorivelazione",
            SkillType.SOCIAL_INTELLIGENCE: "Intelligenza Sociale",
            SkillType.SOCIAL_MEDIA: "Social Media",
            SkillType.SOCIAL_PSYCHOLOGY: "Psicologia Sociale",
            SkillType.STORYTELLING: "Storytelling",
            SkillType.SUPPORTIVE_LISTENING: "Ascolto Solidale",
            SkillType.TEAM_BUILDING: "Team Building",
            SkillType.THERAPEUTIC_COMMUNICATION: "Comunicazione Terapeutica",
            SkillType.TRUST_BUILDING: "Costruzione Fiducia",
            SkillType.VULNERABILITY_SHARING: "Condivisione Vulnerabilità",
            # ================= ABILITÀ CREATIVE =================
            SkillType.ACTING: "Recitazione",
            SkillType.ANIMATION: "Animazione",
            SkillType.ARCHITECTURAL_DESIGN: "Design Architettonico",
            SkillType.BODY_PAINTING: "Body Painting",
            SkillType.CALLIGRAPHY: "Calligrafia",
            SkillType.CHARACTER_DESIGN: "Design Personaggi",
            SkillType.CHOREOGRAPHY: "Coreografia",
            SkillType.COMIC_ART: "Arte Fumettistica",
            SkillType.COMPOSITION: "Composizione",
            SkillType.COSTUME_DESIGN: "Costume Design",
            SkillType.CREATIVE_DIRECTION: "Direzione Creativa",
            SkillType.CREATIVE_WRITING: "Scrittura Creativa",
            SkillType.DIGITAL_SCULPTING: "Scultura Digitale",
            SkillType.DJ_MIXING: "Mixaggio DJ",
            SkillType.DRUMS: "Batteria",
            SkillType.FABRICATION: "Fabbricazione Digitale",
            SkillType.FABRIC_DYEING: "Tintura Tessuti",
            SkillType.FASHION_DESIGN: "Fashion Design",
            SkillType.FILM_DIRECTING: "Regia Cinematografica",
            SkillType.FLOWER_ARRANGING: "Composizione Floreale",
            SkillType.GAME_DESIGN: "Game Design",
            SkillType.GLASSBLOWING: "Soffiatura Vetro",
            SkillType.GRAPHIC_DESIGN: "Graphic Design",
            SkillType.GUITAR: "Chitarra",
            SkillType.ILLUSTRATION: "Illustrazione",
            SkillType.IMPROVISATION: "Improvvisazione",
            SkillType.INDUSTRIAL_DESIGN: "Design Industriale",
            SkillType.INTERIOR_DESIGN: "Interior Design",
            SkillType.JEWELRY_MAKING: "Creazione Gioielli",
            SkillType.LANDSCAPE_DESIGN: "Design Paesaggistico",
            SkillType.LIGHT_DESIGN: "Light Design",
            SkillType.LYRICS_WRITING: "Scrittura Testi",
            SkillType.MAKEUP_ARTISTRY: "Trucco Artistico",
            SkillType.MUSIC_COMPOSITION: "Composizione Musicale",
            SkillType.PAINTING: "Pittura",
            SkillType.PHOTOGRAPHY: "Fotografia",
            SkillType.PIANO: "Pianoforte",
            SkillType.POETRY: "Poesia",
            SkillType.POTTERY: "Ceramica",
            SkillType.PRODUCT_DESIGN: "Product Design",
            SkillType.PUPPETRY: "Burattini",
            SkillType.SCULPTING: "Scultura",
            SkillType.SINGING: "Canto",
            SkillType.SONGWRITING: "Scrittura Canzoni",
            SkillType.STORYBOARDING: "Storyboarding",
            SkillType.TATTOO_ART: "Arte del Tatuaggio",
            SkillType.UX_UI_DESIGN: "UX/UI Design",
            SkillType.VIOLIN: "Violino",
            SkillType.VISUAL_EFFECTS: "Effetti Visivi",
            SkillType.WOOD_CARVING: "Intaglio Legno",

            # ================= ABILITÀ PRATICHE =================
            SkillType.AGRICULTURE: "Agricoltura",
            SkillType.ANIMAL_HUSBANDRY: "Allevamento Animale",
            SkillType.AQUAPONICS: "Acquaponica",
            SkillType.AUTOMOTIVE_REPAIR: "Riparazione Auto",
            SkillType.BAKING: "Pasticceria",
            SkillType.BARTENDING: "Barman",
            SkillType.BEEKEEPING: "Apicoltura",
            SkillType.CANDLE_MAKING: "Produzione Candele",
            SkillType.CARPENTRY: "Falegnameria",
            SkillType.CHEESE_MAKING: "Produzione Formaggio",
            SkillType.CLOCKMAKING: "Orologeria",
            SkillType.COOKING: "Cucina",
            SkillType.ELECTRICAL_WORK: "Lavori Elettrici",
            SkillType.EMBROIDERY: "Ricamo",
            SkillType.FARMING: "Coltivazione",
            SkillType.FERMENTATION: "Fermentazione",
            SkillType.FIREWORK_CRAFTING: "Pirotecnica",
            SkillType.FIRST_AID: "Primo Soccorso",
            SkillType.FISHING: "Pesca",
            SkillType.FORAGING: "Raccolta",
            SkillType.GARDENING: "Giardinaggio",
            SkillType.GOURMET_COOKING: "Cucina Gourmet",
            SkillType.HANDINESS: "Manualità",
            SkillType.HERBALISM: "Erboristeria",
            SkillType.HOME_REPAIR: "Riparazioni Domestiche",
            SkillType.HVAC: "Climatizzazione",
            SkillType.HYDROPONICS: "Idroponica",
            SkillType.KNITTING: "Lavoro a Maglia",
            SkillType.KNOT_TYING: "Annodatura",
            SkillType.LEATHERWORKING: "Lavorazione Pelle",
            SkillType.MAPLE_SYRUP_PRODUCTION: "Produzione Sciroppo d'Acero",
            SkillType.MECHANICS: "Meccanica",
            SkillType.METALWORKING: "Lavorazione Metalli",
            SkillType.MIXOLOGY: "Mixologia",
            SkillType.MUSHROOM_CULTIVATION: "Coltivazione Funghi",
            SkillType.ORGANIZING: "Organizzazione",
            SkillType.PERMACULTURE: "Permacultura",
            SkillType.PLUMBING: "Idraulica",
            SkillType.PRESERVATION: "Conservazione",
            SkillType.QUILTING: "Quilting",
            SkillType.SAUSAGE_MAKING: "Produzione Insaccati",
            SkillType.SOAP_MAKING: "Saponificazione",
            SkillType.STONE_MASONRY: "Muratura",
            SkillType.SURVIVAL_SKILLS: "Sopravvivenza",
            SkillType.TAILORING: "Sartoria",
            SkillType.TIME_MANAGEMENT: "Gestione del Tempo",
            SkillType.VINTNING: "Viticultura",
            SkillType.WEAVING: "Tessitura",
            SkillType.WINE_MAKING: "Produzione Vino",
            SkillType.WOODWORKING: "Lavorazione Legno",

            # ================= ABILITÀ ROMANTICHE/SENSUALI =================
            SkillType.AFFECTION_EXPRESSION: "Espressione Affetto",
            SkillType.AFTERCARE_PROTOCOLS: "Protocolli Aftercare",
            SkillType.AROMA_THERAPY: "Aromaterapia Sensuale",
            SkillType.BDSM_SAFETY: "Sicurezza BDSM",
            SkillType.BODY_LANGUAGE_READING: "Lettura Linguaggio Corporeo",
            SkillType.BREATHWORK_SYNC: "Sincronizzazione Respiro",
            SkillType.CANDLE_MASSAGE: "Massaggio Candele",
            SkillType.CONSENT_COMMUNICATION: "Comunicazione Consenso",
            SkillType.COURTSHIP_RITUALS: "Rituali Corteggiamento",
            SkillType.DANCE_SENSUAL: "Danza Sensuale",
            SkillType.DESIRE_ARTICULATION: "Articolazione Desideri",
            SkillType.DESIRE_FACILITATION: "Facilitazione Desideri",
            SkillType.EMOTIONAL_INTIMACY: "Intimità Emotiva",
            SkillType.ENERGY_EXCHANGE: "Scambio Energetico",
            SkillType.EROTIC_DANCE: "Danza Erotica",
            SkillType.EROTIC_MASSAGE: "Massaggio Erotico",
            SkillType.EROTIC_STORYTELLING: "Racconti Erotici",
            SkillType.EYE_CONTACT_MASTERY: "Padronanza Contatto Visivo",
            SkillType.FETISH_APPRECIATION: "Apprezzamento Feticismo",
            SkillType.FLIRTATION_TECHNIQUES: "Tecniche Flirt",
            SkillType.FOREPLAY_MASTERY: "Padronanza Preliminari",
            SkillType.INTIMACY_CHOREOGRAPHY: "Coreografia Intimità",
            SkillType.INTIMACY_COACHING: "Coaching Intimità",
            SkillType.KINK_NEGOTIATION: "Negoziazione Kink",
            SkillType.LINGERIE_SELECTION: "Selezione Lingerie",
            SkillType.LOVE_LANGUAGE_APPLICATION: "Applicazione Linguaggio Amore",
            SkillType.LOVE_LETTER_WRITING: "Scrittura Lettere d'Amore",
            SkillType.MOOD_CREATION: "Creazione Atmosfera",
            SkillType.MULTIPLE_ORGASM: "Multiplo Orgasmo",
            SkillType.NON_MONOGAMY_NAVIGATION: "Navigazione Non Monogamia",
            SkillType.PARTNER_OBSERVATION: "Osservazione Partner",
            SkillType.PHYSICAL_INTIMACY: "Intimità Fisica",
            SkillType.PLEASURE_DELAY: "Ritardo Piacere",
            SkillType.PLEASURE_MAPPING: "Mappatura Piacere",
            SkillType.ROMANCE_PLANNING: "Pianificazione Romantica",
            SkillType.ROMANTIC_GESTURE: "Gesti Romantici",
            SkillType.SENSUAL_FEEDING: "Alimentazione Sensuale",
            SkillType.SENSUAL_TOUCH: "Tocco Sensuale",
            SkillType.SEXUAL_HEALTH: "Salute Sessuale",
            SkillType.SEXUAL_POSITIONS: "Posizioni Sessuali",
            SkillType.SEX_TOY_KNOWLEDGE: "Conoscenza Sextoy",
            SkillType.SPONTANEITY_CULTIVATION: "Coltivazione Spontaneità",
            SkillType.TANTRIC_PRACTICES: "Pratiche Tantriche",
            SkillType.TEASING_TECHNIQUES: "Tecniche di Stuzzicamento",
            SkillType.TEMPERATURE_PLAY: "Gioco Temperature",
            SkillType.TOUCH_TYPING: "Tocco Digitale",
            SkillType.TRUST_DEEPENING: "Approfondimento Fiducia",
            SkillType.VOYEURISM_CONSENT: "Voyeurismo Consensuale",
            SkillType.VULNERABILITY_SHARING: "Condivisione Vulnerabilità",
            SkillType.WHISPERING_TECHNIQUES: "Tecniche Sussurro",

            # ================= ABILITÀ PER BAMBINI =================
            SkillType.ART_EXPRESSION_CHILD: "Espressione Artistica (Bambino)",
            SkillType.BASIC_COOKING_CHILD: "Cucina Base (Bambino)",
            SkillType.BASIC_HYGIENE_CHILD: "Igiene Base (Bambino)",
            SkillType.BICYCLE_RIDING_CHILD: "Andare in Bici (Bambino)",
            SkillType.BUDGETING_CHILD: "Bilancio (Bambino)",
            SkillType.CIVIC_RESPONSIBILITY: "Responsabilità Civica (Bambino)",
            SkillType.CLIMBING_SAFETY: "Sicurezza Arrampicata (Bambino)",
            SkillType.COMPUTER_BASICS_CHILD: "Informatica Base (Bambino)",
            SkillType.CONFLICT_RESOLUTION_CHILD: "Risoluzione Conflitti (Bambino)",
            SkillType.CRAFTING_CHILD: "Artigianato (Bambino)",
            SkillType.CREATIVITY_CHILD: "Creatività (Bambino)",
            SkillType.CRITICAL_THINKING_CHILD: "Pensiero Critico (Bambino)",
            SkillType.DANCE_BASICS_CHILD: "Ballo Base (Bambino)",
            SkillType.DECISION_MAKING_CHILD: "Decision Making (Bambino)",
            SkillType.EMOTION_REGULATION_CHILD: "Regolazione Emozioni (Bambino)",
            SkillType.ENVIRONMENTAL_AWARENESS: "Consapevolezza Ambientale (Bambino)",
            SkillType.FINE_MOTOR_CHILD: "Motricità Fine (Bambino)",
            SkillType.FIRE_SAFETY: "Sicurezza Antincendio (Bambino)",
            SkillType.FRIENDSHIP_SKILLS_CHILD: "Abilità Amicizia (Bambino)",
            SkillType.GARDENING_CHILD: "Giardinaggio (Bambino)",
            SkillType.GOAL_SETTING_CHILD: "Definizione Obiettivi (Bambino)",
            SkillType.GROSS_MOTOR_CHILD: "Motricità Globale (Bambino)",
            SkillType.HOMEWORK_MANAGEMENT: "Gestione Compiti (Bambino)",
            SkillType.IMAGINATIVE_PLAY: "Gioco Immaginativo (Bambino)",
            SkillType.INTERNET_SAFETY: "Sicurezza Internet (Bambino)",
            SkillType.LANGUAGE_DEVELOPMENT: "Sviluppo Linguistico (Bambino)",
            SkillType.MAP_READING: "Lettura Mappe (Bambino)",
            SkillType.MATH_FOUNDATIONS: "Fondamenti Matematica (Bambino)",
            SkillType.MEMORY_GAMES: "Giochi di Memoria (Bambino)",
            SkillType.MENTAL_CHILD: "Mentale (Bambino)",
            SkillType.MORAL_DEVELOPMENT: "Sviluppo Morale (Bambino)",
            SkillType.MOTOR_CHILD: "Abilità Motorie (Bambino)",
            SkillType.MUSIC_APPRECIATION_CHILD: "Apprezzamento Musicale (Bambino)",
            SkillType.NATURE_EXPLORATION: "Esplorazione Natura (Bambino)",
            SkillType.PET_CARE_CHILD: "Cura Animali (Bambino)",
            SkillType.PLANT_CARE: "Cura Piante (Bambino)",
            SkillType.PROBLEM_SOLVING_CHILD: "Risoluzione Problemi (Bambino)",
            SkillType.PUBLIC_SPEAKING_CHILD: "Parlare in Pubblico (Bambino)",
            SkillType.PUZZLE_SOLVING: "Risoluzione Puzzle (Bambino)",
            SkillType.READING_COMPREHENSION: "Comprensione Lettura (Bambino)",
            SkillType.RESILIENCE_BUILDING: "Costruzione Resilienza (Bambino)",
            SkillType.SAFETY_RULES: "Regole di Sicurezza (Bambino)",
            SkillType.SCIENCE_CURIOSITY: "Curiosità Scientifica (Bambino)",
            SkillType.SELF_CARE_CHILD: "Autocura (Bambino)",
            SkillType.SHARING_PRACTICE: "Pratica Condivisione (Bambino)",
            SkillType.SOCIAL_CHILD: "Sociale (Bambino)",
            SkillType.SPORTS_FUNDAMENTALS: "Fondamenti Sportivi (Bambino)",
            SkillType.TEAM_SPORTS: "Sport di Squadra (Bambino)",
            SkillType.TIME_PERCEPTION: "Percezione Tempo (Bambino)",
            SkillType.WATER_SAFETY: "Sicurezza Acquatica (Bambino)",
        }
        return mapping.get(self, self.name.replace("_", " ").title())



    # ... Aggiungi altre skill dalla tua lista TODO IX.e man mano ...

