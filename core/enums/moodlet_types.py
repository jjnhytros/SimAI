# core/enums/moodlet_types.py
from enum import Enum, auto

from core.enums.genders import Gender

class MoodletType(Enum):
    """Tipi di modificatori di umore (Moodlet) che un NPC può avere."""
    
    # === Categoria 1: Bisogni Fisiologici ===
    ATHLETIC = auto()                # Atletico/a
    BATHROOM_URGENCY = auto()        # Urgenza bagno
    BLADDER_FULL = auto()            # Vescica piena
    BLADDER_RELIEF = auto()          # Sollievo vescicale
    CLEAN = auto()                   # Pulito/a
    DEHYDRATED = auto()              # Disidratato/a
    DIRTY = auto()                   # Sporco/a
    DISEASED = auto()                # Malato/a
    ENERGETIC = auto()               # Energico/a
    EXHAUSTED = auto()               # Esausto/a
    FAMISHED = auto()                # Famélice
    FULLY_HYDRATED = auto()          # Completamente idratato/a
    HUNGRY = auto()                  # Affamato/a
    MALNOURISHED = auto()            # Denutrito/a
    NOCTURNAL = auto()               # Notturno/a
    OVERFED = auto()                 # Sovralimentato/a
    OVERSLEPT = auto()               # Dormito troppo
    PHYSICALLY_FIT = auto()          # In forma fisica
    REFRESHED = auto()               # Rinfrescato/a
    RESTED = auto()                  # Riposato/a
    SLEEPY = auto()                  # Assonnato/a
    SLEEP_DEPRIVED = auto()          # Privo/a di sonno
    STARVING = auto()                # Morendo di fame
    THIRSTY = auto()                 # Assetato/a
    TIRED = auto()                   # Stanco/a
    UNDER_RESTED = auto()            # Poco riposato/a
    UNHYGIENIC = auto()              # Poco igienico/a
    UNQUENCHABLE_THIRST = auto()     # Sete inestinguibile
    WELL_FED = auto()                # Ben nutrito/a
    WIRED = auto()                   # Carico/a
    
    # === Categoria 2: Stati Emozionali ===
    AFFECTIONATE = auto()            # Affettuoso/a
    AGITATED = auto()                # Agitato/a
    AMUSED = auto()                  # Divertito/a
    ANXIOUS = auto()                 # Ansioso/a
    BLISSFUL = auto()                # Beato/a
    BORED = auto()                   # Annoiato/a
    CALM = auto()                    # Calmo/a
    CONFIDENT = auto()               # Sicuro/a di sé
    CONTENT = auto()                 # Contento/a
    DEPRESSED = auto()               # Depresso/a
    DESPONDENT = auto()              # Sconsolato/a
    ECSTATIC = auto()                # Estatico/a
    EMBARRASSED = auto()             # Imbarazzato/a
    EMOTIONAL = auto()               # Emotivo/a
    ENRAGED = auto()                 # Furioso/a
    ENTHUSIASTIC = auto()            # Entusiasta
    EXCITED = auto()                 # Eccitato/a
    FULFILLED = auto()               # Realizzato/a
    GLOOMY = auto()                  # Malinconico/a
    GRATEFUL = auto()                # Grato/a
    HAPPY = auto()                   # Felice
    INDIFFERENT = auto()             # Indifferente
    INSPIRED = auto()                # Ispirato/a
    IRRITATED = auto()               # Irritato/a
    NOSTALGIC = auto()               # Nostalgico/a
    OPTIMISTIC = auto()              # Ottimista
    OVERJOYED = auto()               # Oltremodo felice
    PESSIMISTIC = auto()             # Pessimista
    RELAXED = auto()                 # Rilassato/a
    SAD = auto()                     # Triste
    STRESSED = auto()                # Stressato/a
    VULNERABLE = auto()              # Vulnerabile
    
    # === Categoria 3: Interazioni Sociali ===
    ABANDONED = auto()               # Abbandonato/a
    BELONGING = auto()               # Senso di appartenenza
    BETRAYED = auto()                # Tradito/a
    CHARISMATIC = auto()             # Carismatico/a
    CONNECTED = auto()               # Connesso/a
    DISRESPECTED = auto()            # Sminuito/a
    EMPATHETIC = auto()              # Empatico/a
    FRIENDLY = auto()                # Amichevole
    GUILTY = auto()                  # In colpa
    HOSTILE = auto()                 # Ostile
    IGNORED = auto()                 # Ignorato/a
    INCLUDED = auto()                # Incluso/a
    JEALOUS = auto()                 # Geloso/a
    LONELY = auto()                  # Solitario/a
    LOVED = auto()                   # Amato/a
    POPULAR = auto()                 # Popolare
    REJECTED = auto()                # Rifiutato/a
    RESPECTED = auto()               # Rispettato/a
    ROMANTIC = auto()                # Romantico/a
    SHY = auto()                     # Timido/a
    SOCIABLE = auto()                # Socievole
    SUPPORTED = auto()               # Supportato/a
    TRUSTING = auto()                # Fiducioso/a
    UNLOVED = auto()                 # Non amato/a
    UNPOPULAR = auto()               # Impopolare
    WELCOMED = auto()                # Ben accolto/a
    WORSHIPED = auto()               # Adorato/a
    
    # === Categoria 4: Attività e Intrattenimento ===
    CHALLENGED = auto()              # Stimolato/a
    CREATIVE = auto()                # Creativo/a
    CURIOUS = auto()                 # Curioso/a
    DISTRACTED = auto()              # Distratto/a
    EDUCATED = auto()                # Istruito/a
    ENGAGED = auto()                 # Coinvolto/a
    ENTERTAINED = auto()             # Divertito/a
    EXPLORATIVE = auto()             # Esplorativo/a
    FOCUSED = auto()                 # Concentrato/a
    GAMIFIED = auto()                # Gamificato/a
    INTELLECTUAL = auto()            # Intellettuale
    LEARNING = auto()                # In apprendimento
    MOTIVATED = auto()               # Motivato/a
    OVERSTIMULATED = auto()          # Sovrastimolato/a
    PLAYFUL = auto()                 # Giocoso/a
    PRODUCTIVE = auto()              # Produttivo/a
    TEDIOUS = auto()                 # Tedioso/a
    UNMOTIVATED = auto()             # Demotivato/a
    VICTORIOUS = auto()              # Vittorioso/a
    
    # === Categoria 5: Romantico/Sessuale ===
    AFFAIR = auto()                  # Relazione extraconiugale
    AFTERGLOW = auto()               # Euforia post-amore
    AROUSED = auto()                 # Eccitato/a
    ATTRACTED = auto()               # Attratto/a
    BASHFUL = auto()                 # Timido/a romantico
    BROKEN_HEARTED = auto()          # Cuore spezzato
    COMMITTED = auto()               # Impegnato/a sentimentalmente
    CRAVING = auto()                 # Bramosia
    DEVOTED = auto()                 # Devoto/a
    EROTIC = auto()                  # Erotico/a
    EXCITED_SEXUALLY = auto()        # Sessualmente eccitato/a
    FLIRTATIOUS = auto()             # Flirtante
    FRUSTRATED_SEXUALLY = auto()     # Sessualmente frustrato/a
    IMPASSIONED = auto()             # Appassionato/a
    INFATUATED = auto()              # Infatuato/a
    INTIMATE = auto()                # Intimo/a
    LIBIDINOUS = auto()              # Libidinoso/a
    LUSTFUL = auto()                 # Lussurioso/a
    MONOGAMOUS = auto()              # Monogamo/a
    PASSIONATE = auto()              # Passionale
    PLATONIC = auto()                # Platonico/a
    POLYAMOROUS = auto()             # Poliamoroso/a
    SENSUAL = auto()                 # Sensuale
    SEXUALLY_ABUSED = auto()         # Sessualmente abusato/a
    SEXUALLY_LIBERATED = auto()      # Sessualmente liberato/a
    SMITTEN = auto()                 # Innamorato/a
    SOULMATED = auto()               # Anima gemella
    UNATTRACTED = auto()             # Non attratto/a
    UNCOMMITTED = auto()             # Non impegnato/a
    UNDESIRED = auto()               # Non desiderato/a
    UNLOVED_ROMANTIC = auto()        # Non amato/a romanticamente
    UNREQUITED_LOVE = auto()         # Amore non corrisposto
    WARY_OF_LOVE = auto()            # Diffidente in amore

    # Metodo per ottenere il nome visualizzato in italiano
    def display_name_it(self, gender: Gender) -> str:
        """Restituisce un nome leggibile e declinato in base al genere per il moodlet."""
        mapping = {
            # === Categoria 1: Bisogni Fisiologici ===
            MoodletType.ATHLETIC: {Gender.MALE: "Atletico", Gender.FEMALE: "Atletica"},
            MoodletType.BATHROOM_URGENCY: "Urgenza bagno",
            MoodletType.BLADDER_FULL: "Vescica piena",
            MoodletType.BLADDER_RELIEF: "Sollievo vescicale",
            MoodletType.CLEAN: {Gender.MALE: "Pulito", Gender.FEMALE: "Pulita"},
            MoodletType.DEHYDRATED: {Gender.MALE: "Disidratato", Gender.FEMALE: "Disidratata"},
            MoodletType.DIRTY: {Gender.MALE: "Sporco", Gender.FEMALE: "Sporca"},
            MoodletType.DISEASED: {Gender.MALE: "Malato", Gender.FEMALE: "Malata"},
            MoodletType.ENERGETIC: {Gender.MALE: "Energico", Gender.FEMALE: "Energica"},
            MoodletType.EXHAUSTED: {Gender.MALE: "Esausto", Gender.FEMALE: "Esausta"},
            MoodletType.FAMISHED: {Gender.MALE: "Famelico", Gender.FEMALE: "Famelica"},
            MoodletType.FULLY_HYDRATED: {Gender.MALE: "Completamente idratato", Gender.FEMALE: "Completamente idratata"},
            MoodletType.HUNGRY: {Gender.MALE: "Affamato", Gender.FEMALE: "Affamata"},
            MoodletType.MALNOURISHED: {Gender.MALE: "Denutrito", Gender.FEMALE: "Denutrita"},
            MoodletType.NOCTURNAL: {Gender.MALE: "Notturno", Gender.FEMALE: "Notturna"},
            MoodletType.OVERFED: {Gender.MALE: "Sovralimentato", Gender.FEMALE: "Sovralimentata"},
            MoodletType.OVERSLEPT: "Dormito troppo",
            MoodletType.PHYSICALLY_FIT: "In forma fisica",
            MoodletType.REFRESHED: {Gender.MALE: "Rinfrescato", Gender.FEMALE: "Rinfrescata"},
            MoodletType.RESTED: {Gender.MALE: "Riposato", Gender.FEMALE: "Riposata"},
            MoodletType.SLEEP_DEPRIVED: {Gender.MALE: "Privo di sonno", Gender.FEMALE: "Priva di sonno"},
            MoodletType.SLEEPY: {Gender.MALE: "Assonnato", Gender.FEMALE: "Assonnata"},
            MoodletType.STARVING: {Gender.MALE: "Morendo di fame", Gender.FEMALE: "Morendo di fame"},
            MoodletType.THIRSTY: {Gender.MALE: "Assetato", Gender.FEMALE: "Assetata"},
            MoodletType.TIRED: {Gender.MALE: "Stanco", Gender.FEMALE: "Stanca"},
            MoodletType.UNDER_RESTED: {Gender.MALE: "Poco riposato", Gender.FEMALE: "Poco riposata"},
            MoodletType.UNHYGIENIC: {Gender.MALE: "Poco igienico", Gender.FEMALE: "Poco igienica"},
            MoodletType.UNQUENCHABLE_THIRST: "Sete inestinguibile",
            MoodletType.WELL_FED: {Gender.MALE: "Ben nutrito", Gender.FEMALE: "Ben nutrita"},
            MoodletType.WIRED: {Gender.MALE: "Carico", Gender.FEMALE: "Carica"},
            
            # === Categoria 2: Stati Emozionali ===
            MoodletType.AFFECTIONATE: {Gender.MALE: "Affettuoso", Gender.FEMALE: "Affettuosa"},
            MoodletType.AGITATED: {Gender.MALE: "Agitato", Gender.FEMALE: "Agitata"},
            MoodletType.AMUSED: {Gender.MALE: "Divertito", Gender.FEMALE: "Divertita"},
            MoodletType.ANXIOUS: {Gender.MALE: "Ansioso", Gender.FEMALE: "Ansiosa"},
            MoodletType.BLISSFUL: {Gender.MALE: "Beato", Gender.FEMALE: "Beata"},
            MoodletType.BORED: {Gender.MALE: "Annoiato", Gender.FEMALE: "Annoiata"},
            MoodletType.CALM: {Gender.MALE: "Calmo", Gender.FEMALE: "Calma"},
            MoodletType.CONFIDENT: {Gender.MALE: "Sicuro di sé", Gender.FEMALE: "Sicura di sé"},
            MoodletType.CONTENT: {Gender.MALE: "Contento", Gender.FEMALE: "Contenta"},
            MoodletType.DEPRESSED: {Gender.MALE: "Depresso", Gender.FEMALE: "Depressa"},
            MoodletType.DESPONDENT: {Gender.MALE: "Sconsolato", Gender.FEMALE: "Sconsolata"},
            MoodletType.ECSTATIC: {Gender.MALE: "Estatico", Gender.FEMALE: "Estatica"},
            MoodletType.EMBARRASSED: {Gender.MALE: "Imbarazzato", Gender.FEMALE: "Imbarazzata"},
            MoodletType.EMOTIONAL: {Gender.MALE: "Emotivo", Gender.FEMALE: "Emotiva"},
            MoodletType.ENRAGED: {Gender.MALE: "Furioso", Gender.FEMALE: "Furiosa"},
            MoodletType.ENTHUSIASTIC: "Entusiasta",
            MoodletType.EXCITED: {Gender.MALE: "Eccitato", Gender.FEMALE: "Eccitata"},
            MoodletType.FULFILLED: {Gender.MALE: "Realizzato", Gender.FEMALE: "Realizzata"},
            MoodletType.GLOOMY: {Gender.MALE: "Malinconico", Gender.FEMALE: "Malinconica"},
            MoodletType.GRATEFUL: {Gender.MALE: "Grato", Gender.FEMALE: "Grata"},
            MoodletType.HAPPY: "Felice",
            MoodletType.INDIFFERENT: "Indifferente",
            MoodletType.INSPIRED: {Gender.MALE: "Ispirato", Gender.FEMALE: "Ispirata"},
            MoodletType.IRRITATED: {Gender.MALE: "Irritato", Gender.FEMALE: "Irritata"},
            MoodletType.NOSTALGIC: {Gender.MALE: "Nostalgico", Gender.FEMALE: "Nostalgica"},
            MoodletType.OPTIMISTIC: "Ottimista",
            MoodletType.OVERJOYED: "Oltremodo felice",
            MoodletType.PESSIMISTIC: "Pessimista",
            MoodletType.RELAXED: {Gender.MALE: "Rilassato", Gender.FEMALE: "Rilassata"},
            MoodletType.SAD: "Triste",
            MoodletType.STRESSED: {Gender.MALE: "Stressato", Gender.FEMALE: "Stressata"},
            MoodletType.VULNERABLE: {Gender.MALE: "Vulnerabile", Gender.FEMALE: "Vulnerabile"},
            
            # === Categoria 3: Interazioni Sociali ===
            MoodletType.ABANDONED: {Gender.MALE: "Abbandonato", Gender.FEMALE: "Abbandonata"},
            MoodletType.BELONGING: "Senso di appartenenza",
            MoodletType.BETRAYED: {Gender.MALE: "Tradito", Gender.FEMALE: "Tradita"},
            MoodletType.CHARISMATIC: {Gender.MALE: "Carismatico", Gender.FEMALE: "Carismatica"},
            MoodletType.CONNECTED: {Gender.MALE: "Connesso", Gender.FEMALE: "Connessa"},
            MoodletType.DISRESPECTED: {Gender.MALE: "Sminuito", Gender.FEMALE: "Sminuita"},
            MoodletType.EMPATHETIC: {Gender.MALE: "Empatico", Gender.FEMALE: "Empatica"},
            MoodletType.FRIENDLY: "Amichevole",
            MoodletType.GUILTY: {Gender.MALE: "In colpa", Gender.FEMALE: "In colpa"},
            MoodletType.HOSTILE: "Ostile",
            MoodletType.IGNORED: {Gender.MALE: "Ignorato", Gender.FEMALE: "Ignorata"},
            MoodletType.INCLUDED: {Gender.MALE: "Incluso", Gender.FEMALE: "Inclusa"},
            MoodletType.JEALOUS: {Gender.MALE: "Geloso", Gender.FEMALE: "Gelosa"},
            MoodletType.LONELY: {Gender.MALE: "Solo", Gender.FEMALE: "Sola"},
            MoodletType.LOVED: {Gender.MALE: "Amato", Gender.FEMALE: "Amata"},
            MoodletType.POPULAR: "Popolare",
            MoodletType.REJECTED: {Gender.MALE: "Rifiutato", Gender.FEMALE: "Rifiutata"},
            MoodletType.RESPECTED: {Gender.MALE: "Rispettato", Gender.FEMALE: "Rispettata"},
            MoodletType.ROMANTIC: {Gender.MALE: "Romantico", Gender.FEMALE: "Romantica"},
            MoodletType.SHY: {Gender.MALE: "Timido", Gender.FEMALE: "Timida"},
            MoodletType.SOCIABLE: "Socievole",
            MoodletType.SUPPORTED: {Gender.MALE: "Supportato", Gender.FEMALE: "Supportata"},
            MoodletType.TRUSTING: {Gender.MALE: "Fiducioso", Gender.FEMALE: "Fiduciosa"},
            MoodletType.UNLOVED: {Gender.MALE: "Non amato", Gender.FEMALE: "Non amata"},
            MoodletType.UNPOPULAR: "Impopolare",
            MoodletType.WELCOMED: {Gender.MALE: "Ben accolto", Gender.FEMALE: "Ben accolta"},
            MoodletType.WORSHIPED: {Gender.MALE: "Adorato", Gender.FEMALE: "Adorata"},
            
            # === Categoria 4: Attività e Intrattenimento ===
            MoodletType.CHALLENGED: {Gender.MALE: "Stimolato", Gender.FEMALE: "Stimolata"},
            MoodletType.CREATIVE: {Gender.MALE: "Creativo", Gender.FEMALE: "Creativa"},
            MoodletType.CURIOUS: {Gender.MALE: "Curioso", Gender.FEMALE: "Curiosa"},
            MoodletType.DISTRACTED: {Gender.MALE: "Distratto", Gender.FEMALE: "Distratta"},
            MoodletType.EDUCATED: {Gender.MALE: "Istruito", Gender.FEMALE: "Istruita"},
            MoodletType.ENGAGED: {Gender.MALE: "Coinvolto", Gender.FEMALE: "Coinvolta"},
            MoodletType.ENTERTAINED: {Gender.MALE: "Divertito", Gender.FEMALE: "Divertita"},
            MoodletType.EXPLORATIVE: {Gender.MALE: "Esplorativo", Gender.FEMALE: "Esplorativa"},
            MoodletType.FOCUSED: {Gender.MALE: "Concentrato", Gender.FEMALE: "Concentrata"},
            MoodletType.GAMIFIED: {Gender.MALE: "Gamificato", Gender.FEMALE: "Gamificata"},
            MoodletType.INTELLECTUAL: "Intellettuale",
            MoodletType.LEARNING: "In apprendimento",
            MoodletType.MOTIVATED: {Gender.MALE: "Motivato", Gender.FEMALE: "Motivata"},
            MoodletType.OVERSTIMULATED: {Gender.MALE: "Sovrastimolato", Gender.FEMALE: "Sovrastimolata"},
            MoodletType.PLAYFUL: {Gender.MALE: "Giocoso", Gender.FEMALE: "Giocosa"},
            MoodletType.PRODUCTIVE: {Gender.MALE: "Produttivo", Gender.FEMALE: "Produttiva"},
            MoodletType.TEDIOUS: {Gender.MALE: "Tedioso", Gender.FEMALE: "Tediosa"},
            MoodletType.UNMOTIVATED: {Gender.MALE: "Demotivato", Gender.FEMALE: "Demotivata"},
            MoodletType.VICTORIOUS: {Gender.MALE: "Vittorioso", Gender.FEMALE: "Vittoriosa"},
            
            # === Categoria 5: Romantico/Sessuale ===
            MoodletType.AFFAIR: "Relazione extraconiugale",
            MoodletType.AFTERGLOW: "Euforia post-amore",
            MoodletType.AROUSED: {Gender.MALE: "Eccitato", Gender.FEMALE: "Eccitata"},
            MoodletType.ATTRACTED: {Gender.MALE: "Attratto", Gender.FEMALE: "Attratta"},
            MoodletType.BASHFUL: {Gender.MALE: "Timido romantico", Gender.FEMALE: "Timida romantica"},
            MoodletType.BROKEN_HEARTED: {Gender.MALE: "Cuore spezzato", Gender.FEMALE: "Cuore spezzato"},
            MoodletType.COMMITTED: {Gender.MALE: "Impegnato sentimentalmente", Gender.FEMALE: "Impegnata sentimentalmente"},
            MoodletType.CRAVING: "Bramosia",
            MoodletType.DEVOTED: {Gender.MALE: "Devoto", Gender.FEMALE: "Devota"},
            MoodletType.EROTIC: {Gender.MALE: "Erotico", Gender.FEMALE: "Erotica"},
            MoodletType.EXCITED_SEXUALLY: {Gender.MALE: "Sessualmente eccitato", Gender.FEMALE: "Sessualmente eccitata"},
            MoodletType.FLIRTATIOUS: "Flirtante",
            MoodletType.FRUSTRATED_SEXUALLY: {Gender.MALE: "Sessualmente frustrato", Gender.FEMALE: "Sessualmente frustrata"},
            MoodletType.IMPASSIONED: {Gender.MALE: "Appassionato", Gender.FEMALE: "Appassionata"},
            MoodletType.INFATUATED: {Gender.MALE: "Infatuato", Gender.FEMALE: "Infatuata"},
            MoodletType.INTIMATE: {Gender.MALE: "Intimo", Gender.FEMALE: "Intima"},
            MoodletType.LIBIDINOUS: {Gender.MALE: "Libidinoso", Gender.FEMALE: "Libidinosa"},
            MoodletType.LUSTFUL: {Gender.MALE: "Lussurioso", Gender.FEMALE: "Lussuriosa"},
            MoodletType.MONOGAMOUS: {Gender.MALE: "Monogamo", Gender.FEMALE: "Monogama"},
            MoodletType.PASSIONATE: {Gender.MALE: "Passionale", Gender.FEMALE: "Passionale"},
            MoodletType.PLATONIC: {Gender.MALE: "Platonico", Gender.FEMALE: "Platonica"},
            MoodletType.POLYAMOROUS: {Gender.MALE: "Poliamoroso", Gender.FEMALE: "Poliamorosa"},
            MoodletType.SEXUALLY_ABUSED: {Gender.MALE: "Sessualmente abusato", Gender.FEMALE: "Sessualmente abusata"},
            MoodletType.SENSUAL: {Gender.MALE: "Sensuale", Gender.FEMALE: "Sensuale"},
            MoodletType.SEXUALLY_LIBERATED: {Gender.MALE: "Sessualmente liberato", Gender.FEMALE: "Sessualmente liberata"},
            MoodletType.SMITTEN: {Gender.MALE: "Innamorato", Gender.FEMALE: "Innamorata"},
            MoodletType.SOULMATED: "Anima gemella",
            MoodletType.UNATTRACTED: {Gender.MALE: "Non attratto", Gender.FEMALE: "Non attratta"},
            MoodletType.UNCOMMITTED: {Gender.MALE: "Non impegnato", Gender.FEMALE: "Non impegnata"},
            MoodletType.UNDESIRED: {Gender.MALE: "Non desiderato", Gender.FEMALE: "Non desiderata"},
            MoodletType.UNLOVED_ROMANTIC: {Gender.MALE: "Non amato romanticamente", Gender.FEMALE: "Non amata romanticamente"},
            MoodletType.UNREQUITED_LOVE: "Amore non corrisposto",
            MoodletType.WARY_OF_LOVE: {Gender.MALE: "Diffidente in amore", Gender.FEMALE: "Diffidente in amore"},
        }
        
        value = mapping.get(self)

        if isinstance(value, dict):
            return value.get(gender, value.get(Gender.MALE, "N/D"))
        elif isinstance(value, str):
            return value
        else:
            # Fallback se non trovato
            return self.name.replace("_", " ").title()        
