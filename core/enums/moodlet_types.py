# core/enums/moodlet_types.py
from enum import Enum, auto

class MoodletType(Enum):
    """Tipi di modificatori di umore (Moodlet) che un NPC può avere."""
    # Categoria 1: Bisogni Fisiologici (50 voci)
    ATHLETIC = auto()              # Atletico
    BATHROOM_URGENCY = auto()      # Urgenza bagno
    BLADDER_FULL = auto()          # Vescica piena
    BLADDER_RELIEF = auto()        # Sollievo vescicale
    CLEAN = auto()                 # Pulito
    DEHYDRATED = auto()            # Disidratato
    DIRTY = auto()                 # Sporco
    DISEASED = auto()              # Malato
    ENERGETIC = auto()             # Energico
    EXHAUSTED = auto()             # Esausto
    FAMISHED = auto()              # Famélice
    FRESH = auto()                 # Fresco
    FULL_BLADDER = auto()          # Vescica piena
    FULLY_HYDRATED = auto()        # Completamente idratato
    HUNGRY = auto()                # Affamato
    HYDRATED = auto()              # Idratato
    ILL = auto()                   # Indisposto
    MALNOURISHED = auto()          # Denutrito
    NOCTURNAL = auto()             # Notturno
    OVERFED = auto()               # Sovralimentato
    OVERSLEPT = auto()             # Dormito troppo
    PHYSICALLY_FIT = auto()        # In forma fisica
    QUENCHED = auto()              # Disseziato
    REFRESHED = auto()             # Rinfrescato
    RESTED = auto()                # Riposato
    SATIATED = auto()              # Saziato
    SLEEP_DEPRIVED = auto()        # Privo di sonno
    SLEEPY = auto()                # Assonnato
    STARVING = auto()              # Morendo di fame
    THIRSTY = auto()               # Assetato
    TIRED = auto()                 # Stanco
    UNDER_RESTED = auto()          # Poco riposato
    UNHYGIENIC = auto()            # Poco igienico
    UNQUENCHABLE_THIRST = auto()   # Sete inestinguibile
    WELL_FED = auto()              # Ben nutrito
    WELL_HYDRATED = auto()         # Ben idratato
    WELL_RESTED = auto()           # Ben riposato
    WIRED = auto()                 # Carico
    WORN_OUT = auto()              # Sfinito
    ZESTFUL = auto()               # Pieno di energia

    # Categoria 2: Stati Emozionali (50 voci)
    AFFECTIONATE = auto()          # Affettuoso
    AGITATED = auto()              # Agitato
    AMUSED = auto()                # Divertito
    ANXIOUS = auto()               # Ansioso
    APATHETIC = auto()             # Apatetico
    BLISSFUL = auto()              # Beato
    BORED = auto()                 # Annoiato
    CALM = auto()                  # Calmo
    CHEERFUL = auto()              # Allegro
    CONFIDENT = auto()             # Sicuro di sé
    CONTENT = auto()               # Contento
    CRANKY = auto()                # Irritabile
    DEPRESSED = auto()             # Depresso
    DESPONDENT = auto()            # Sconsolato
    ECSTATIC = auto()              # Estatico
    ELATED = auto()                # Euforico
    EMOTIONAL = auto()             # Emotivo
    ENRAGED = auto()               # Furioso
    ENTHUSIASTIC = auto()          # Entusiasta
    EUPHORIC = auto()              # Euforico
    EXCITED = auto()               # Eccitato
    FULFILLED = auto()             # Realizzato
    GLOOMY = auto()                # Malinconico
    GRATEFUL = auto()              # Grato
    HAPPY = auto()                 # Felice
    HOPEFUL = auto()               # Speranzoso
    INDIFFERENT = auto()           # Indifferente
    INSPIRED = auto()              # Ispirato
    IRRITATED = auto()             # Irritato
    JOYFUL = auto()                # Gioioso
    MELANCHOLIC = auto()           # Malinconico
    MOPEY = auto()                 # Depresso
    NOSTALGIC = auto()             # Nostalgico
    OPTIMISTIC = auto()            # Ottimista
    OVERJOYED = auto()             # Oltre modo felice
    PESSIMISTIC = auto()           # Pessimista
    PLEASED = auto()               # Soddisfatto
    RELAXED = auto()               # Rilassato
    SAD = auto()                   # Triste
    SATISFIED = auto()             # Soddisfatto
    SERENE = auto()                # Sereno
    STRESSED = auto()              # Stressato
    UNHAPPY = auto()               # Infelice
    UPBEAT = auto()                # Allegro
    VULNERABLE = auto()            # Vulnerabile
    WORRIED = auto()               # Preoccupato

    # Categoria 3: Interazioni Sociali (50 voci)
    ABANDONED = auto()             # Abbandonato
    ADMIRED = auto()               # Ammirato
    ALIENATED = auto()             # Alienato
    APPRECIATED = auto()           # Apprezzato
    BELONGING = auto()             # Senso di appartenenza
    BETRAYED = auto()              # Tradito
    CHARISMATIC = auto()           # Carismatico
    CONNECTED = auto()             # Connesso
    DISCONNECTED = auto()          # Disconnesso
    DISRESPECTED = auto()          # Sminuito
    EMPATHETIC = auto()            # Empatico
    ENVIOUS = auto()               # Invidioso
    EXCLUDED = auto()              # Escluso
    FRIENDLY = auto()              # Amichevole
    GUILTY = auto()                # In colpa
    HOSTILE = auto()               # Ostile
    IGNORED = auto()               # Ignorato
    INCLUDED = auto()              # Incluso
    ISOLATED = auto()              # Isolato
    JEALOUS = auto()               # Geloso
    LONELY = auto()                # Solitario
    LOVED = auto()                 # Amato
    NEGLECTED = auto()             # Trascurato
    POPULAR = auto()               # Popolare
    REJECTED = auto()              # Rifiutato
    RESPECTED = auto()             # Rispettato
    ROMANTIC = auto()              # Romantico
    SHY = auto()                   # Timido
    SOCIABLE = auto()              # Socievole
    SUPPORTED = auto()             # Supportato
    SYMPATHETIC = auto()           # Comprensivo
    TRUSTING = auto()              # Fiducioso
    UNLOVED = auto()               # Non amato
    UNPOPULAR = auto()             # Impopolare
    VALIDATED = auto()             # Convalidato
    WELCOMED = auto()              # Ben accolto
    WITHDRAWN = auto()             # Chiuso
    WORSHIPED = auto()             # Adorato

    # Categoria 4: Attività e Intrattenimento (50 voci)
    ACHIEVEMENT = auto()           # Realizzazione
    BOREDOM = auto()               # Noia
    CHALLENGED = auto()            # Stimolato
    CREATIVE = auto()              # Creativo
    CURIOUS = auto()               # Curioso
    DETERMINED = auto()            # Determinato
    DISTRACTED = auto()            # Distratto
    EDUCATED = auto()              # Istruito
    ENGAGED = auto()               # Coinvolto
    ENTERTAINED = auto()           # Divertito
    EXCITEMENT = auto()            # Eccitamento
    EXPLORATIVE = auto()           # Esplorativo
    FOCUSED = auto()               # Concentrato
    FUN = auto()                   # Divertimento
    GAMIFIED = auto()              # Gamificato
    HUMORED = auto()               # Di buon umore
    INTELLECTUAL = auto()          # Intellettuale
    INTERESTED = auto()            # Interessato
    LEARNING = auto()              # Apprendimento
    MOTIVATED = auto()             # Motivato
    OVERSTIMULATED = auto()        # Sovrastimolato
    PLAYFUL = auto()               # Giocoso
    PRODUCTIVE = auto()            # Produttivo
    RELAXED_LEISURE = auto()       # Relax ludico
    SATISFIED_WORK = auto()        # Soddisfazione lavorativa
    STIMULATED = auto()            # Stimolato
    TEDIOUS = auto()               # Tedioso
    UNENTERTAINED = auto()         # Non intrattenuto
    UNINSPIRED = auto()            # Senza ispirazione
    UNMOTIVATED = auto()           # Demotivato
    VICTORIOUS = auto()            # Vittorioso
    WEARY_WORK = auto()            # Stanco del lavoro

    # Categoria 5: Romantico/Sessuale
    AFFAIR = auto()                # Relazione extraconiugale
    AFTERGLOW = auto()             # Euforia dopo un amore
    ALOOF = auto()                 # Azzardato   
    AMOROUS = auto()               # Amoroso
    AROUSED = auto()               # Eccitato
    ATTRACTED = auto()             # Attratto
    BASHFUL = auto()               # Timido romantico
    BROKEN_HEARTED = auto()        # Cuore spezzato
    CHASTE = auto()                # Casto
    COMMITTED = auto()             # Impegnato sentimentalmente
    CRAVING = auto()               # Bramosia
    CRUSHING = auto()              # Infatuato
    DESIRING = auto()              # Desideroso
    DEVOTED = auto()               # Devoto
    DRAWN_TO = auto()              # Attratto da
    ENCHANTED = auto()             # Incantato
    EROTIC = auto()                # Erotico
    EXCITED_SEXUALLY = auto()      # Sessualmente eccitato
    FLIRTATIOUS = auto()           # Flirtante
    FRUSTRATED_SEXUALLY = auto()   # Sessualmente frustrato
    HEARTBREAK = auto()            # Angoscia amorosa
    HORNY = auto()                 # Eccitato sessualmente
    IMPASSIONED = auto()           # Appassionato
    INFATUATED = auto()            # Infatuato
    INTIMATE = auto()              # Intimo
    LIBIDINOUS = auto()            # Lubrico
    LONELY_HEART = auto()          # Cuore solitario
    LOVESTRUCK = auto()            # Colpito da Cupido
    LUSTFUL = auto()               # Lussurioso
    MONOGAMOUS = auto()            # Monogamo
    PASSIONATE = auto()            # Passionale
    PLATONIC = auto()              # Platonico
    POLYGAMOUS = auto()            # Poliagamo
    POLYAMOROUS = auto()           # Poliamoroso
    REJECTED_LOVE = auto()         # Amore respinto
    ROMANCE = auto()               # In stato romantico
    SATED_SEXUALLY = auto()        # Sessualmente soddisfatto
    SEXUALLY_ABUSED = auto()       # Sessualmente abusato
    SENSUAL = auto()               # Sensuale
    SEXUALLY_LIBERATED = auto()    # Sessualmente liberato
    SEDUCTIVE = auto()             # Seduttivo
    SMITTEN = auto()               # Innamorato
    SOULMATED = auto()             # Anima gemella
    SPURNED = auto()               # Respinto
    SWEETHEART = auto()            # Amorevole
    TENDER = auto()                # Tenero
    UNATTRACTED = auto()           # Non attratto
    UNCOMMITTED = auto()           # Non impegnato
    UNDESIRED = auto()             # Non desiderato
    UNLOVED_ROMANTIC = auto()      # Non amato romanticamente
    UNREQUITED_LOVE = auto()       # Amore non corrisposto
    WANTON = auto()                # Lascivo
    WARY_OF_LOVE = auto()          # Diffidente in amore
    YEARNING = auto()              # Bramoso

    # Metodo per ottenere il nome visualizzato in italiano
    def display_name_it(self, gender: Gender) -> str:
        """Restituisce un nome leggibile e declinato in base al genere per il moodlet."""
        mapping = {
            # --- Declinabili (Aggettivi) ---
            MoodletType.FEELING_ENERGIZED: {Gender.MALE: "Rinvigorito", Gender.FEMALE: "Rinvigorita"},
            MoodletType.FEELING_TIRED: {Gender.MALE: "Stanco", Gender.FEMALE: "Stanca"},
            MoodletType.FEELING_EXHAUSTED: {Gender.MALE: "Esausto", Gender.FEMALE: "Esausta"},
            MoodletType.FEELING_FULL: {Gender.MALE: "Sazio", Gender.FEMALE: "Sazia"},
            MoodletType.FEELING_HUNGRY: {Gender.MALE: "Affamato", Gender.FEMALE: "Affamata"},
            MoodletType.FEELING_STARVING: {Gender.MALE: "Morto di fame", Gender.FEMALE: "Morta di fame"},
            MoodletType.FEELING_REFRESHED: {Gender.MALE: "Rifocillato", Gender.FEMALE: "Rifocillata"},
            MoodletType.FEELING_THIRSTY: {Gender.MALE: "Assetato", Gender.FEMALE: "Assetata"},
            MoodletType.FEELING_DEHYDRATED: {Gender.MALE: "Disidratato", Gender.FEMALE: "Disidratata"},
            MoodletType.FEELING_HAPPY: {Gender.MALE: "Felice", Gender.FEMALE: "Felice"}, # Invariabile
            MoodletType.FEELING_SAD: {Gender.MALE: "Triste", Gender.FEMALE: "Triste"}, # Invariabile
            MoodletType.FEELING_ANGRY: {Gender.MALE: "Arrabbiato", Gender.FEMALE: "Arrabbiata"},
            MoodletType.FEELING_STRESSED: {Gender.MALE: "Stressato", Gender.FEMALE: "Stressata"},
            MoodletType.FEELING_BORED: {Gender.MALE: "Annoiato", Gender.FEMALE: "Annoiata"},
            MoodletType.FEELING_INSPIRED: {Gender.MALE: "Ispirato", Gender.FEMALE: "Ispirata"},
            MoodletType.FEELING_CONFIDENT: {Gender.MALE: "Sicuro di sé", Gender.FEMALE: "Sicura di sé"},
            MoodletType.FEELING_EMBARRASSED: {Gender.MALE: "Imbarazzato", Gender.FEMALE: "Imbarazzata"},
            MoodletType.FEELING_FLIRTY: {Gender.MALE: "Ammiccante", Gender.FEMALE: "Ammiccante"}, # Invariabile
            MoodletType.FEELING_LONELY: {Gender.MALE: "Solo", Gender.FEMALE: "Sola"},
            MoodletType.FEELING_LOVED: {Gender.MALE: "Amato", Gender.FEMALE: "Amata"},
            MoodletType.FEELING_CLEAN: {Gender.MALE: "Pulito", Gender.FEMALE: "Pulita"},
            MoodletType.FEELING_DIRTY: {Gender.MALE: "Sporco", Gender.FEMALE: "Sporca"},

            # --- Invariabili (Nomi) ---
            MoodletType.BLADDER_DISTRESS: "Vescica Piena",
            MoodletType.NEW_FRIEND: "Nuovo Amico",
            MoodletType.FIRST_KISS: "Primo Bacio",
            MoodletType.GOT_PROMOTED: "Promozione Ottenuta",
            MoodletType.GOT_FIRED: "Licenziamento Subito",
            MoodletType.DEATH_OF_A_LOVED_ONE: "Lutto",
            MoodletType.BEAUTIFUL_SURROUNDINGS: "Ambiente Magnifico",
            MoodletType.POOR_ENVIRONMENT: "Ambiente Scadente",
        }
        
        value = mapping.get(self)

        if isinstance(value, dict):
            # Usa il maschile come fallback se il genere non è specificato
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            return value
        else:
            return self.name.replace("_", " ").title()
