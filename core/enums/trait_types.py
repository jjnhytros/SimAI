# core/enums/trait_types.py
from enum import Enum, auto

from core.enums.genders import Gender
"""
Definizione dell'Enum TraitType per i tipi di tratti di personalità degli NPC.
Riferimento TODO: IV.3.b
"""

class TraitType(Enum):
    """Enum per i diversi tratti di personalità."""
    # --- Categoria: Personalità ---
    AMBITIOUS = auto()          # Ambizioso
    CHARMER = auto()            # Charmante
    CONSERVATIVE = auto()       # Conservativo
    DARING = auto()             # Dardoso
    DETERMINED = auto()         # Determinato
    EMBARRASSING = auto()       # Embarrassante
    EMBRACER = auto()           # Embracante
    ENTHUSIAST = auto()         # Entusiasta
    EVIL = auto()               # Malvagio
    FAMOUS = auto()             # Noto
    FAVORABLE = auto()          # Favorito
    FRIENDLY = auto()           # Amabile
    GOOD = auto()               # Buono
    LAZY = auto()               # Pigro
    NEAT = auto()               # Ordinato
    OPTIMIST = auto()           # Ottimista
    PESSIMIST = auto()          # Pessimista
    SLOB = auto()               # Disordinato
    CHILDISH = auto()           # Infantile
    PLAYFUL = auto()            # Giocherellone
    UNINHIBITED = auto()        # Disinibito


    # --- Categoria: Sociale ---
    JEALOUS = auto()            # Geloso
    LONER = auto()              # Solitario
    LOYAL = auto()              # Leale
    ROMANTIC = auto()           # Romantico
    SHY = auto()                # Timido
    SOCIAL = auto()             # Socievole
    UNFLIRTY = auto()           # Non portato per il flirt
    CHARISMATIC = auto()        # Carismatico
    CONVERSATIONALIST = auto()  # Conversatore
    DIPLOMATIC = auto()         # Diplomatico
    EMPATHETIC = auto()         # Empatico
    GOSSIPER = auto()           # Pettegolo
    HONEST = auto()             # Onesto
    HUMBLE = auto()             # Umile
    MANIPULATIVE = auto()       # Manipolatore
    PERSUASIVE = auto()         # Persuasivo
    RESERVED = auto()           # Riservato
    SELFISH = auto()            # Egoista
    TACTFUL = auto()            # Discreto
    TRUSTING = auto()           # Fiducioso
    WITTY = auto()              # Spiritoso
    PATRIOTIC = auto()          # Patriottico
    CYNICAL = auto()            # Cinico
    FLAMBOYANT = auto()         # Eccentrico

    # --- Categoria: Lifestyle e Hobby ---
    ACTIVE = auto()             # Attivo
    ADVENTUROUS = auto()        # Avventuroso
    ART_LOVER = auto()          # Amante dell'arte
    BOOKWORM = auto()           # Topo di biblioteca
    CAFE_LOVER = auto()         # Amante del caffè
    CREATIVE = auto()           # Creativo
    FAMILY_ORIENTED = auto()    # Orientato alla famiglia
    FARMER = auto()             # Agricoltore
    FASHIONABLE = auto()        # Alla moda
    FESTIVE = auto()            # Festaiolo
    FOLKLORE_LOVER = auto()     # Amante del folklore
    FOODIE = auto()             # Buongustaio
    FRUGAL = auto()             # Frugale
    FUNNY = auto()              # Divertente
    GEEK = auto()               # Geek
    GIFTED = auto()             # Talentuoso
    GLUTTON = auto()            # Goloso
    HATES_CHILDREN = auto()     # Odia i bambini
    HATE_FOOD = auto()          # Schizzinoso
    HUNGRY = auto()             # Affamato
    INDEPENDENT = auto()        # Indipendente
    INTELLIGENT = auto()        # Intelligente
    JOKER = auto()              # Burlone
    LOGICAL = auto()            # Logico
    LUCKY = auto()              # Fortunato
    MACHO = auto()              # Machista
    MELANCHOLIC = auto()        # Malinconico
    MUSICAL = auto()            # Musicale
    NERD = auto()               # Nerd
    PARTY_ANIMAL = auto()       # Animale da festa
    PHILOSOPHER = auto()        # Filosofo
    PLEASANT = auto()           # Piacevole
    PREDATOR = auto()           # Predatore
    RICH = auto()               # Ricco
    SAD = auto()                # Triste
    SCIENTIFIC = auto()         # Scientifico
    SENSUAL = auto()            # Sensuale
    SILENT = auto()             # Silenzioso
    SLEEPY = auto()             # Sonnolento
    ANIMAL_LOVER = auto()       # Amante degli animali
    BEACH_BUM = auto()          # Amante della spiaggia
    COFFEE_ADDICT = auto()      # Dipendente dal caffè
    COLLECTOR = auto()          # Collezionista
    COOK = auto()               # Cuoco
    DANCER = auto()             # Ballerino
    DIY_ENTHUSIAST = auto()     # Appassionato di fai-da-te
    EARLY_BIRD = auto()         # Mattiniero
    ENVIRONMENTALIST = auto()   # Ambientalista
    FITNESS_FANATIC = auto()    # Fanatico del fitness
    GAMER = auto()              # Giocatore
    GARDENER = auto()           # Giardiniere
    HANDYMAN = auto()           # Tuttofare
    HISTORY_BUFF = auto()       # Appassionato di storia
    MOVIE_LOVER = auto()        # Cinefilo
    MUSIC_LOVER = auto()        # Amante della musica
    NATURE_LOVER = auto()       # Amante della natura
    NIGHT_OWL = auto()          # Nottambulo
    OUTDOORSY = auto()          # Amante dell'aria aperta
    TRAVELER = auto()           # Viaggiatore
    PHOTOGRAPHER = auto()       # Fotografo
    SHOPPER = auto()            # Acquirente compulsivo
    SPORTS_FAN = auto()         # Tifoso sportivo
    TECH_SAVVY = auto()         # Esperto di tecnologia
    TV_ADDICT = auto()          # Dipendente dalla TV
    VEGETARIAN = auto()         # Vegetariano
    VOLUNTEER = auto()          # Volontario

    # --- Categoria: Emotivo ---
    AFFECTIONATE = auto()       # Affettuoso
    AGGRESSIVE = auto()         # Aggressivo
    ANXIOUS = auto()            # Ansioso
    CALM = auto()               # Calmo
    COMPASSIONATE = auto()      # Compassionevole
    CONFIDENT = auto()          # Sicuro di sé
    CONTENT = auto()            # Appagato
    EMOTIONALLY_STABLE = auto() # Emotivamente stabile
    EXCITABLE = auto()          # Eccitabile
    FEARFUL = auto()            # Pauroso
    FRAGILE = auto()            # Fragile
    GRUMPY = auto()             # Scontroso
    HAPPY_GO_LUCKY = auto()     # Spensierato
    HOT_HEADED = auto()         # Irascibile
    IMPATIENT = auto()          # Impaziente
    INSECURE = auto()           # Insicuro
    IRRITABLE = auto()          # Irritabile
    LIGHT_HEARTED = auto()      # Allegro
    MOODY = auto()              # Lunatico
    NERVOUS = auto()            # Nervoso
    PASSIONATE = auto()         # Appassionato
    PATIENT = auto()            # Paziente
    SENSITIVE = auto()          # Sensibile
    STRESSED = auto()           # Stressato
    TEMPERAMENTAL = auto()      # Temperamentale
    UNPREDICTABLE = auto()      # Imprevedibile
    VOLATILE = auto()           # Volatile

    # --- Categoria: Intellettuale ---
    ANALYTICAL = auto()         # Analitico
    ARTISTIC = auto()           # Artistico
    CURIOUS = auto()            # Curioso
    DETAIL_ORIENTED = auto()    # Attento ai dettagli
    EDUCATED = auto()           # Istruito
    INQUISITIVE = auto()        # Inquisitivo
    KNOWLEDGEABLE = auto()      # Conoscitore
    PERCEPTIVE = auto()         # Perspicace
    REFLECTIVE = auto()         # Riflessivo
    SCHOLARLY = auto()          # Erudito
    STRATEGIC = auto()          # Strategico
    THEORETICAL = auto()        # Teorico
    WISE = auto()               # Saggio
    OBSERVANT = auto()          # Osservatore
    QUICK_LEARNER = auto()      # Impara in fretta
    CRITICAL_THINKER = auto()   # Pensatore critico
    ABSTRACT_THINKER = auto()   # Pensatore astratto
    LINGUISTIC = auto()         # Linguistico
    NUMERATE = auto()           # Numerato

    # --- Categoria: Morale ---
    ALTRUISTIC = auto()         # Altruista
    COMPLIANT = auto()          # Rispettoso delle regole
    CORRUPT = auto()            # Corrotto
    DECEITFUL = auto()          # Ingannevole
    ETHICAL = auto()            # Etico
    FAIR = auto()               # Giusto
    GENEROUS = auto()           # Generoso
    HONORABLE = auto()          # Onorevole
    HUMANE = auto()             # Umanitario
    IMPARTIAL = auto()          # Imparziale
    PRINCIPLED = auto()         # Di princìpi
    MERCIFUL = auto()           # Misericordioso
    NOBLE = auto()              # Nobile
    RIGHTEOUS = auto()          # Rettitudine
    TRUSTWORTHY = auto()        # Affidabile
    UNSCRUPULOUS = auto()       # Senza scrupoli
    VIRTUOUS = auto()           # Virtuoso
    FORGIVING = auto()          # Perdonatore
    JUDGMENTAL = auto()         # Giudicante

    # --- Categoria: Attitudine al Lavoro ---
    CAREFUL = auto()            # Attento
    DEDICATED = auto()          # Dedicato
    DELIGENT = auto()           # Diligente
    DISCIPLINED = auto()        # Disciplinato
    EFFICIENT = auto()          # Efficiente
    FLEXIBLE = auto()           # Flessibile
    FOCUSED = auto()            # Concentrato
    HARDWORKING = auto()        # Lavoratore
    METHODICAL = auto()         # Metodico
    ORGANIZED = auto()          # Organizzato
    PERFECTIONIST = auto()      # Perfezionista
    PRAGMATIC = auto()          # Pragmatico
    PROCRASTINATOR = auto()     # Procrastinatore
    PRODUCTIVE = auto()         # Produttivo
    PUNCTUAL = auto()           # Puntuale
    RESOURCEFUL = auto()        # Ricco di risorse
    THOROUGH = auto()           # Scrupoloso

    # --- Categoria: Fisico ---
    ATHLETIC = auto()           # Atletico
    BEAUTIFUL = auto()          # Bella presenza
    CLUMSY = auto()             # Maldestro
    FRAIL = auto()              # Fragile fisicamente
    GRACEFUL = auto()           # Aggraziato
    HEALTH_CONSCIOUS = auto()   # Attento alla salute
    HEFTY = auto()              # Robusto
    SEDENTARY = auto()          # Sedentario
    SICKLY = auto()             # Cagionevole
    STRONG = auto()             # Forte
    TOUGH = auto()              # Resistente
    UNATTRACTIVE = auto()       # Poco attraente
    WEAK = auto()               # Debole
    AGILE = auto()              # Agile
    ENDURANT = auto()           # Resistente
    DEXTEROUS = auto()          # Abile manualmente
    PAIN_TOLERANT = auto()      # Tollerante al dolore

    # --- Categoria: Comportamentale ---
    ADAPTABLE = auto()          # Adattabile
    CAUTIOUS = auto()           # Cauto
    COMPETITIVE = auto()        # Competitivo
    CONSISTENT = auto()         # Coerente
    DECISIVE = auto()           # Deciso
    EXTRAVAGANT = auto()        # Stravagante
    FORGETFUL = auto()          # Smemorato
    HABITUAL = auto()           # Abitudinario
    IMPULSIVE = auto()          # Impulsivo
    INDECISIVE = auto()         # Indeciso
    MATURE = auto()             # Maturo
    OBSESSIVE = auto()          # Ossessivo
    OPEN_MINDED = auto()        # Mente aperta
    PERSEVERANT = auto()        # Perseverante
    QUIRKY = auto()             # Bizzarro
    RECKLESS = auto()           # Spericolato
    SPONTANEOUS = auto()        # Spontaneo
    STUBBORN = auto()           # Testardo
    THOUGHTFUL = auto()         # Premuroso

    # --- Categoria: Ambizioni e Obiettivi ---
    ASPIRING = auto()           # Aspirante
    CAREER_DRIVEN = auto()      # Orientato alla carriera
    ENTREPRENEURIAL = auto()    # Imprenditoriale
    FAME_SEEKER = auto()        # Cercatore di fama
    GOAL_ORIENTED = auto()      # Orientato agli obiettivi
    LEGACY_BUILDER = auto()     # Costruttore di eredità
    POWER_HUNGRY = auto()       # Affamato di potere
    STATUS_SEEKER = auto()      # Cercatore di status
    SUCCESS_ORIENTED = auto()   # Orientato al successo
    WEALTH_SEEKER = auto()      # Cercatore di ricchezza

    # --- Categoria: Relazioni ---
    COMMITTED = auto()          # Impegnato
    DEPENDENT = auto()          # Dipendente
    DOMINANT = auto()           # Dominante
    FAITHFUL = auto()           # Fedele
    NEEDY = auto()              # Bisognoso
    NON_COMMITTAL = auto()      # Non impegnativo
    PARTNER_FOCUSED = auto()   # Focalizzato sul partner
    POSSESSIVE = auto()         # Possessivo
    SUBMISSIVE = auto()         # Sottomesso
    SUPPORTIVE = auto()         # Di supporto

    # --- Categoria: Salute e Benessere ---
    ADDICTED = auto()           # Dipendente
    DIET_CONSCIOUS = auto()     # Attento alla dieta
    HEALTH_FANATIC = auto()     # Fanatico della salute
    HYPOCHONDRIAC = auto()      # Ipocondriaco
    MEDITATION_PRACTITIONER = auto() # Praticante di meditazione
    RECOVERING_ADDICT = auto()  # Ex tossicodipendente
    STRESS_MANAGER = auto()     # Gestore dello stress
    UNHEALTHY = auto()          # Malsano
    WELLNESS_ADVOCATE = auto()  # Sostenitore del benessere
    HEALTH_IGNORER = auto()     # Trascurato della salute

    # --- Categoria: Spirituale ---
    ATHEIST = auto()            # Ateo
    BELIEVER = auto()           # Credente
    DEVOUT = auto()             # Devoto
    DOGMATIC = auto()           # Dogmatico
    MYSTICAL = auto()           # Mistico
    RELIGIOUS = auto()          # Religioso
    RITUALISTIC = auto()        # Ritualista
    SPIRITUAL = auto()          # Spirituale
    SUPERSTITIOUS = auto()      # Superstizioso
    TOLERANT = auto()           # Tollerante

    def display_name_it(self, gender: Gender) -> str:
        """
        Restituisce un nome leggibile e declinato in base al genere per il tratto.
        """
        mapping = {
            # Traduzioni esistenti
            TraitType.ACTIVE: "Attivo",
            TraitType.ADVENTUROUS: "Avventuroso",
            TraitType.AMBITIOUS: "Ambizioso",
            TraitType.ART_LOVER: "Amante dell'Arte",
            TraitType.BOOKWORM: "Topo di Biblioteca",
            TraitType.CHARMER: "Charmante",
            TraitType.CREATIVE: "Creativo",
            TraitType.EVIL: "Malvagio",
            TraitType.FAMILY_ORIENTED: "Orientato alla Famiglia",
            TraitType.FOODIE: "Buongustaio",
            TraitType.FRUGAL: "Frugale",
            TraitType.UNINHIBITED: {Gender.MALE: "Disinibito", Gender.FEMALE: "Disinibita"},
            TraitType.GLUTTON: "Ghiottone",
            TraitType.GOOD: "Buono",
            TraitType.HATES_CHILDREN: "Odia i Bambini",
            TraitType.JEALOUS: "Geloso",
            TraitType.LAZY: "Pigro",
            TraitType.LOGICAL: "Logico",
            TraitType.LONER: "Solitario",
            TraitType.LOYAL: "Leale",
            TraitType.NEAT: "Ordinato",
            TraitType.OPTIMIST: "Ottimista",
            TraitType.PARTY_ANIMAL: "Animale da Festa",
            TraitType.PESSIMIST: "Pessimista",
            TraitType.PHILOSOPHER: "Filosofo",
            TraitType.ROMANTIC: "Romantico",
            TraitType.SHY: "Timido",
            TraitType.SOCIAL: "Socievole",
            TraitType.UNFLIRTY: "Non flirtante",
            TraitType.CHILDISH: "Infantile",
            TraitType.PLAYFUL: {Gender.MALE: "Giocherellone", Gender.FEMALE: "Giocherellona"},
            TraitType.SLOB: {Gender.MALE: "Disordinato", Gender.FEMALE: "Disordinata"},
            
            # Nuove traduzioni (organizzate per categoria)
            # Sociale
            TraitType.CHARISMATIC: "Carismatico",
            TraitType.CONVERSATIONALIST: "Conversatore",
            TraitType.DIPLOMATIC: "Diplomatico",
            TraitType.EMPATHETIC: "Empatico",
            TraitType.GOSSIPER: "Pettegolo",
            TraitType.HONEST: "Onesto",
            TraitType.HUMBLE: "Umile",
            TraitType.MANIPULATIVE: "Manipolatore",
            TraitType.PERSUASIVE: "Persuasivo",
            TraitType.RESERVED: "Riservato",
            TraitType.SELFISH: "Egoista",
            TraitType.TACTFUL: "Discreto",
            TraitType.TRUSTING: "Fiducioso",
            TraitType.WITTY: "Spiritoso",
            TraitType.PATRIOTIC: "Patriottico",
            TraitType.CYNICAL: "Cinico",
            TraitType.FLAMBOYANT: "Eccentrico",
            
            # Lifestyle e Hobby
            TraitType.ANIMAL_LOVER: "Amante degli Animali",
            TraitType.BEACH_BUM: "Amante della Spiaggia",
            TraitType.COFFEE_ADDICT: "Dipendente dal Caffè",
            TraitType.COLLECTOR: "Collezionista",
            TraitType.COOK: "Cuoco",
            TraitType.DANCER: "Ballerino",
            TraitType.DIY_ENTHUSIAST: "Appassionato di Fai-da-te",
            TraitType.EARLY_BIRD: "Mattiniero",
            TraitType.ENVIRONMENTALIST: "Ambientalista",
            TraitType.FITNESS_FANATIC: "Fanatico del Fitness",
            TraitType.GAMER: "Giocatore",
            TraitType.GARDENER: "Giardiniere",
            TraitType.HANDYMAN: "Tuttofare",
            TraitType.HISTORY_BUFF: "Appassionato di Storia",
            TraitType.MOVIE_LOVER: "Cinefilo",
            TraitType.MUSIC_LOVER: "Amante della Musica",
            TraitType.NATURE_LOVER: "Amante della Natura",
            TraitType.NIGHT_OWL: "Nottambulo",
            TraitType.OUTDOORSY: "Amante dell'Aria Aperta",
            TraitType.TRAVELER: "Viaggiatore",
            TraitType.PHOTOGRAPHER: "Fotografo",
            TraitType.SHOPPER: "Shopaholic",
            TraitType.SPORTS_FAN: "Tifoso Sportivo",
            TraitType.TECH_SAVVY: "Esperto di Tecnologia",
            TraitType.TV_ADDICT: "Dipendente dalla TV",
            TraitType.VEGETARIAN: "Vegetariano",
            TraitType.VOLUNTEER: "Volontario",
            
            # Emotivo
            TraitType.AFFECTIONATE: "Affettuoso",
            TraitType.AGGRESSIVE: "Aggressivo",
            TraitType.ANXIOUS: "Ansioso",
            TraitType.CALM: "Calmo",
            TraitType.COMPASSIONATE: "Compassionevole",
            TraitType.CONFIDENT: "Sicuro di Sè",
            TraitType.CONTENT: "Appagato",
            TraitType.EMOTIONALLY_STABLE: "Emotivamente Stabile",
            TraitType.EXCITABLE: "Eccitabile",
            TraitType.FEARFUL: "Pauroso",
            TraitType.FRAGILE: "Fragile",
            TraitType.GRUMPY: "Scontroso",
            TraitType.HAPPY_GO_LUCKY: "Spensierato",
            TraitType.HOT_HEADED: "Irascibile",
            TraitType.IMPATIENT: "Impaziente",
            TraitType.INSECURE: "Insicuro",
            TraitType.IRRITABLE: "Irritabile",
            TraitType.LIGHT_HEARTED: "Allegro",
            TraitType.MOODY: "Lunatico",
            TraitType.NERVOUS: "Nervoso",
            TraitType.PASSIONATE: "Appassionato",
            TraitType.PATIENT: "Paziente",
            TraitType.SENSITIVE: "Sensibile",
            TraitType.STRESSED: "Stressato",
            TraitType.TEMPERAMENTAL: "Temperamentale",
            TraitType.UNPREDICTABLE: "Imprevedibile",
            TraitType.VOLATILE: "Volatile",
            
            # Intellettuale
            TraitType.ANALYTICAL: "Analitico",
            TraitType.CURIOUS: "Curioso",
            TraitType.DETAIL_ORIENTED: "Attento ai Dettagli",
            TraitType.EDUCATED: "Istruito",
            TraitType.INQUISITIVE: "Inquisitivo",
            TraitType.KNOWLEDGEABLE: "Conoscitore",
            TraitType.PERCEPTIVE: "Perspicace",
            TraitType.REFLECTIVE: "Riflessivo",
            TraitType.SCHOLARLY: "Erudito",
            TraitType.STRATEGIC: "Strategico",
            TraitType.THEORETICAL: "Teorico",
            TraitType.WISE: "Saggio",
            TraitType.OBSERVANT: "Osservatore",
            TraitType.QUICK_LEARNER: "Impara in Fretta",
            TraitType.CRITICAL_THINKER: "Pensatore Critico",
            TraitType.ABSTRACT_THINKER: "Pensatore Astratto",
            TraitType.LINGUISTIC: "Linguistico",
            TraitType.NUMERATE: "Numerato",
            
            # Morale
            TraitType.ALTRUISTIC: "Altruista",
            TraitType.COMPLIANT: "Rispettoso delle Regole",
            TraitType.CORRUPT: "Corrotto",
            TraitType.DECEITFUL: "Ingannevole",
            TraitType.ETHICAL: "Etico",
            TraitType.FAIR: "Giusto",
            TraitType.GENEROUS: "Generoso",
            TraitType.HONORABLE: "Onorevole",
            TraitType.HUMANE: "Umanitario",
            TraitType.IMPARTIAL: "Imparziale",
            TraitType.PRINCIPLED: "Di Princìpi",
            TraitType.MERCIFUL: "Misericordioso",
            TraitType.NOBLE: "Nobile",
            TraitType.RIGHTEOUS: "Rettitudine",
            TraitType.TRUSTWORTHY: "Affidabile",
            TraitType.UNSCRUPULOUS: "Senza Scrupoli",
            TraitType.VIRTUOUS: "Virtuoso",
            TraitType.FORGIVING: "Perdonatore",
            TraitType.JUDGMENTAL: "Giudicante",
            
            # Attitudine al Lavoro
            TraitType.CAREFUL: "Attento",
            TraitType.DEDICATED: "Dedicato",
            TraitType.DELIGENT: "Diligente",
            TraitType.DISCIPLINED: "Disciplinato",
            TraitType.EFFICIENT: "Efficiente",
            TraitType.FLEXIBLE: "Flessibile",
            TraitType.FOCUSED: "Concentrato",
            TraitType.HARDWORKING: "Lavoratore",
            TraitType.METHODICAL: "Metodico",
            TraitType.ORGANIZED: "Organizzato",
            TraitType.PERFECTIONIST: "Perfezionista",
            TraitType.PRAGMATIC: "Pragmatico",
            TraitType.PROCRASTINATOR: "Procrastinatore",
            TraitType.PRODUCTIVE: "Produttivo",
            TraitType.PUNCTUAL: "Puntuale",
            TraitType.RESOURCEFUL: "Ricco di Risorse",
            TraitType.THOROUGH: "Scrupoloso",
            
            # Fisico
            TraitType.ATHLETIC: "Atletico",
            TraitType.BEAUTIFUL: "Bella Presenza",
            TraitType.CLUMSY: "Maldestro",
            TraitType.FRAIL: "Fragile Fisicamente",
            TraitType.GRACEFUL: "Aggraziato",
            TraitType.HEALTH_CONSCIOUS: "Attento alla Salute",
            TraitType.HEFTY: "Robusto",
            TraitType.SEDENTARY: "Sedentario",
            TraitType.SICKLY: "Cagionevole",
            TraitType.STRONG: "Forte",
            TraitType.TOUGH: "Resistente",
            TraitType.UNATTRACTIVE: "Poco Attraente",
            TraitType.WEAK: "Debole",
            TraitType.AGILE: "Agile",
            TraitType.ENDURANT: "Resistente",
            TraitType.DEXTEROUS: "Abile Manualmente",
            TraitType.PAIN_TOLERANT: "Tollerante al Dolore",
            
            # Comportamentale
            TraitType.ADAPTABLE: "Adattabile",
            TraitType.CAUTIOUS: "Cauto",
            TraitType.COMPETITIVE: "Competitivo",
            TraitType.CONSISTENT: "Coerente",
            TraitType.DECISIVE: "Deciso",
            TraitType.EXTRAVAGANT: "Stravagante",
            TraitType.FORGETFUL: "Smemorato",
            TraitType.HABITUAL: "Abitudinario",
            TraitType.IMPULSIVE: "Impulsivo",
            TraitType.INDECISIVE: "Indeciso",
            TraitType.MATURE: "Maturo",
            TraitType.OBSESSIVE: "Ossessivo",
            TraitType.OPEN_MINDED: "Mente Aperta",
            TraitType.PERSEVERANT: "Perseverante",
            TraitType.QUIRKY: "Bizzarro",
            TraitType.RECKLESS: "Spericolato",
            TraitType.SPONTANEOUS: "Spontaneo",
            TraitType.STUBBORN: "Testardo",
            TraitType.THOUGHTFUL: "Premuroso",
            
            # Ambizioni e Obiettivi
            TraitType.ASPIRING: "Aspirante",
            TraitType.CAREER_DRIVEN: "Orientato alla Carriera",
            TraitType.ENTREPRENEURIAL: "Imprenditoriale",
            TraitType.FAME_SEEKER: "Cercatore di Fama",
            TraitType.GOAL_ORIENTED: "Orientato agli Obiettivi",
            TraitType.LEGACY_BUILDER: "Costruttore di Eredità",
            TraitType.POWER_HUNGRY: "Affamato di Potere",
            TraitType.STATUS_SEEKER: "Cercatore di Status",
            TraitType.SUCCESS_ORIENTED: "Orientato al Successo",
            TraitType.WEALTH_SEEKER: "Cercatore di Ricchezza",
            
            # Relazioni
            TraitType.COMMITTED: "Impegnato",
            TraitType.DEPENDENT: "Dipendente",
            TraitType.DOMINANT: "Dominante",
            TraitType.FAITHFUL: "Fedele",
            TraitType.NEEDY: "Bisognoso",
            TraitType.NON_COMMITTAL: "Non Impegnativo",
            TraitType.PARTNER_FOCUSED: "Focalizzato sul Partner",
            TraitType.POSSESSIVE: "Possessivo",
            TraitType.SUBMISSIVE: "Sottomesso",
            TraitType.SUPPORTIVE: "Di Supporto",
            
            # Salute e Benessere
            TraitType.ADDICTED: "Dipendente",
            TraitType.DIET_CONSCIOUS: "Attento alla Dieta",
            TraitType.HEALTH_FANATIC: "Fanatico della Salute",
            TraitType.HYPOCHONDRIAC: "Ipocondriaco",
            TraitType.MEDITATION_PRACTITIONER: "Praticante di Meditazione",
            TraitType.RECOVERING_ADDICT: "Ex Tossicodipendente",
            TraitType.STRESS_MANAGER: "Gestore dello Stress",
            TraitType.UNHEALTHY: "Malsano",
            TraitType.WELLNESS_ADVOCATE: "Sostenitore del Benessere",
            TraitType.HEALTH_IGNORER: "Trascurato della Salute",
            
            # Spirituale
            TraitType.ATHEIST: "Ateo",
            TraitType.BELIEVER: "Credente",
            TraitType.DEVOUT: "Devoto",
            TraitType.DOGMATIC: "Dogmatico",
            TraitType.MYSTICAL: "Mistico",
            TraitType.RELIGIOUS: "Religioso",
            TraitType.RITUALISTIC: "Ritualista",
            TraitType.SPIRITUAL: "Spirituale",
            TraitType.SUPERSTITIOUS: "Superstizioso",
            TraitType.TOLERANT: "Tollerante",
        }

        value = mapping.get(self)

        if isinstance(value, dict):
            # Se il valore è un dizionario, restituisci la chiave per il genere corretto.
            # Se il genere non è nel dizionario, usa il maschile come fallback.
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            # Se è una stringa, è invariabile, restituiscila direttamente.
            return value
        else:
            # Fallback se il tratto non è nella mappa
            return self.name.replace("_", " ").capitalize()
