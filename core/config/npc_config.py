# simai/core/config/npc_config.py
"""
Configurazione NPC, tratti, bisogni e ciclo di vita
"""

from enum import Enum

from core.enums.moodlet_types import MoodletType
from core.enums.service_types import ServiceType
from .time_config import DXY, DXM, IXH, SECONDS_PER_SIMULATION_TICK, SXH, SXI, TXH_SIMULATION
from core.enums import LifeStage, NeedType, TimeOfDay, TraitType

from core.config import time_config


# --- Soglie e Valori dei Bisogni (Adattati a 28 ore) ---
NEED_MIN_VALUE: float = 0.0
NEED_MAX_VALUE: float = 144.0
NEED_DEFAULT_START_MIN: float = 72.0
NEED_DEFAULT_START_MAX: float = 115.0
NEED_LOW_THRESHOLD: float = 36.0
NEED_HIGH_THRESHOLD: float = 108.0
NEED_CRITICAL_THRESHOLD: float = 18.0
CRITICAL_NEED_THRESHOLD_MODIFIER: float = 1.5
AI_URGENT_PROBLEM_THRESHOLD: float = 0.5
STRESS_HIGH_THRESHOLD = 108.0

# --- Tassi di Decadimento Bisogni (Punti all'ora di gioco) ---
# Questi sono i valori di bilanciamento che possiamo modificare facilmente.
# Un valore negativo indica un calo.
NEED_HOURLY_DECAY_RATES: dict[NeedType, float] = {
    NeedType.ENERGY: -5.76,
    NeedType.HUNGER: -4.536,
    NeedType.THIRST: -5.9328,
    NeedType.SOCIAL: -2.7072,
    NeedType.FUN: -3.24,
    NeedType.HYGIENE: -2.16,
    NeedType.BLADDER: -8.928,
    NeedType.INTIMACY: -1.6128,
    NeedType.COMFORT: -1.08,
    NeedType.ENVIRONMENT: -0.5472,
    NeedType.SAFETY: -0.5472,
    NeedType.CREATIVITY: -0.3168,
    NeedType.LEARNING: -0.216,
    NeedType.AUTONOMY: -0.3168,
    NeedType.ACHIEVEMENT: -0.216,
    NeedType.SPIRITUALITY: -0.432,
}

# --- Tassi di Decadimento calcolati per Tick di Simulazione ---
# NON TOCCARE QUESTA PARTE. Calcolarf                   automaticamente i valori corretti.
NEED_DECAY_RATES_PER_TICK: dict[NeedType, float] = {
    need: rate / TXH_SIMULATION
    for need, rate in NEED_HOURLY_DECAY_RATES.items()
}

# --- CONFIGURAZIONE DEI MOODLET ---
MOODLET_CONFIGS = {
    MoodletType.BORED: {
        "emotional_impact": -14.4,
        "duration_hours": 3,
    },
    MoodletType.LONELY: {
        "emotional_impact": -21.6,
        "duration_hours": 4,
    },
    MoodletType.STRESSED: {
        "emotional_impact": -28.8,
        "duration_hours": 5,
    },
    MoodletType.ENERGETIC: {
        "emotional_impact": 14.4, # +10 * 1.44
        "duration_hours": 3,
    },
    MoodletType.DEPRESSED: {
        "emotional_impact": -28.8, # -20 * 1.44
        "duration_hours": 8,
    },
    # Aggiungi qui gli altri moodlet...
}

# Convertiamo le durate in tick una sola volta
for moodlet_config in MOODLET_CONFIGS.values():
    moodlet_config["duration_ticks"] = int(moodlet_config["duration_hours"] * time_config.TXH_SIMULATION)

# --- MAPPA BISOGNI CRITICI -> MOODLET ---
# Mappa un bisogno critico al moodlet corrispondente
NEED_TO_MOODLET_MAP = {
    NeedType.HUNGER: MoodletType.STARVING,
    NeedType.ENERGY: MoodletType.EXHAUSTED,
    NeedType.FUN: MoodletType.BORED,
    NeedType.SOCIAL: MoodletType.LONELY,
    NeedType.STRESS: MoodletType.STRESSED,
    # ... e così via per gli altri bisogni critici
}

NEED_SCHEDULE_CONFIG = {
    NeedType.HUNGER: {
        # Lista di ore (su 28) in cui l'NPC "dovrebbe" avere fame
        "peak_times": [8, 15, 22], # Colazione, Pranzo, Cena
        "peak_influence": 36.0, # 36 Bonus di punteggio da aggiungere se siamo vicini all'ora di punta
    },
    NeedType.SOCIAL: {
        # La socialità è più importante la sera
        "peak_times": [19, 25], # Dalle 19:00 all'una di notte
        "peak_influence": 21.6, # 21.6 o 18?
    },
    # Aggiungi qui altri bisogni se necessario...
}

# --- Pesi per l'IA (Aggiornati con priorità circadiane) ---
NEED_WEIGHTS: dict[NeedType, float] = {
    NeedType.HUNGER: 1.6,
    NeedType.THIRST: 1.7, 
    NeedType.ENERGY: 1.5,
    NeedType.BLADDER: 1.4,
    NeedType.HYGIENE: 1.1,
    NeedType.FUN: 0.9,
    NeedType.SOCIAL: 0.8,
    NeedType.INTIMACY: 0.7,
}

# --- STRESS E CARICO COGNITIVO ---
# La soglia media dei bisogni sotto la quale lo stress inizia ad aumentare.
COGNITIVE_LOAD_THRESHOLD: float = 57.6

# Tasso di aumento dello stress per tick quando i bisogni sono bassi.
COGNITIVE_LOAD_GAIN_RATE: float = 0.005

# Tasso di calo (recupero) dello stress per tick quando i bisogni sono soddisfatti.
COGNITIVE_LOAD_DECAY_RATE: float = 0.002


# --- Generazione NPC ---
MIN_TRAITS_PER_NPC = 3
MAX_TRAITS_PER_NPC = 5
MAX_NPC_ACTIVE_INTERESTS = 3
IMPLEMENTED_TRAITS = [
    TraitType.ACTIVE, TraitType.BOOKWORM, TraitType.GLUTTON, TraitType.LONER,
    TraitType.AMBITIOUS, TraitType.LAZY, TraitType.SOCIAL, TraitType.CREATIVE,
    TraitType.ARTISTIC, TraitType.CHARMER, TraitType.SHY, TraitType.PLAYFUL,
    TraitType.CHILDISH, TraitType.UNINHIBITED, TraitType.GOOD,
]
# --- Conflitti tra Tratti ---
TRAIT_CONFLICTS = [
    {TraitType.ACTIVE, TraitType.LAZY},
    {TraitType.SOCIAL, TraitType.LONER},
    {TraitType.GLUTTON, TraitType.AMBITIOUS},
    {TraitType.SHY, TraitType.UNINHIBITED}
]

# --- Ciclo di Vita ---
LIFE_STAGE_AGE_THRESHOLDS_DAYS = {
    # Chiavi come stringhe dei membri dell'Enum LifeStage
    "NEWBORN": 0,                     # Dalla nascita
    "INFANT": round(DXM * 2),         # Da circa 2 mesi
    "TODDLER": DXY * 1,               # Da 1 anno
    "PRESCHOOLER": DXY * 3,           # Da 3 anni
    "CHILD": DXY * 6,                 # Da 6 anni
    "PRE_TEEN": DXY * 9,              # Da 9 anni
    "EARLY_ADOLESCENCE": DXY * 12,    # Da 12 anni
    "MID_ADOLESCENCE": DXY * 15,      # Da 15 anni
    "LATE_ADOLESCENCE": DXY * 18,     # Da 18 anni
    "YOUNG_ADULT": DXY * 20,          # Da 20 anni
    "ADULT": DXY * 30,                # Da 30 anni
    "MIDDLE_AGED": DXY * 40,          # Da 40 anni
    "MATURE_ADULT": DXY * 60,         # Da 60 anni
    "SENIOR": DXY * 75,               # Da 75 anni
    "ELDERLY": DXY * 90,              # Da 90 anni
}

# --- Riproduzione e Sessualità (Aggiornato con fasi vita) ---
MIN_AGE_PUBERTY_FERTILITY_YEARS = 13
MIN_AGE_PUBERTY_FERTILITY_DAYS = MIN_AGE_PUBERTY_FERTILITY_YEARS * DXY
MIN_AGE_FOR_INTIMACY_YEARS = 14
MIN_AGE_FOR_INTIMACY_DAYS = MIN_AGE_FOR_INTIMACY_YEARS * DXY
MAX_AGE_FOR_INTIMACY_YEARS = 75
MAX_AGE_FOR_INTIMACY_DAYS = MAX_AGE_FOR_INTIMACY_YEARS * DXY
PREGNANCY_CHANCE_FEMALE = 0.18
PREGNANCY_DURATION_MONTHS_GAME = 9
PREGNANCY_DURATION_DAYS_GAME = PREGNANCY_DURATION_MONTHS_GAME * DXM
MIN_AGE_START_PREGNANCY_FEMALE_YEARS = 16
MIN_AGE_START_PREGNANCY_FEMALE_DAYS = MIN_AGE_START_PREGNANCY_FEMALE_YEARS * DXY
MAX_AGE_FERTILE_FEMALE_YEARS = 45
MAX_AGE_FERTILE_FEMALE_DAYS = MAX_AGE_FERTILE_FEMALE_YEARS * DXY
AGE_START_MENSTRUAL_CYCLE_YEARS_SET = {11.5, 13.5}
AGE_START_MENSTRUAL_CYCLE_DAYS_SET = {round(year * DXY) for year in AGE_START_MENSTRUAL_CYCLE_YEARS_SET}
AGE_MENOPAUSE_YEARS_SET = {48.0, 55.0}
AGE_MENOPAUSE_DAYS_SET = {round(year * DXY) for year in AGE_MENOPAUSE_YEARS_SET}

# --- SERVIZI SOCIALI E MATCHMAKING (SONET) ---
# Età minime di accesso ai servizi (in anni e giorni)
SERVICE_MIN_AGE_YEARS = {
    ServiceType.AMORI_CURATI_PHASE1: 18,
    ServiceType.AMORI_CURATI_PHASE2: 25,
    ServiceType.FRIEND_CONNECT: 14
}

SERVICE_MIN_AGE_DAYS = {
    service: years * DXY
    for service, years in SERVICE_MIN_AGE_YEARS.items()
}

# Differenze d'età massime per i servizi
SERVICE_MAX_AGE_DIFF_YEARS = {
    ServiceType.AMORI_CURATI_PHASE1: 10,
    ServiceType.AMORI_CURATI_PHASE2: 15,
    ServiceType.FRIEND_CONNECT: 8
}

# Fattori di compatibilità basati sui tratti
SERVICE_TRAIT_COMPATIBILITY_FACTORS = {
    ServiceType.AMORI_CURATI_PHASE1: {
        TraitType.CHARMER: 1.4,
        TraitType.SHY: 0.6,
        TraitType.UNINHIBITED: 1.3,
        TraitType.SOCIAL: 1.2
    },
    ServiceType.AMORI_CURATI_PHASE2: {
        TraitType.AMBITIOUS: 1.3,
        TraitType.CREATIVE: 1.2,
        TraitType.GOOD: 1.1,
        TraitType.LONER: 0.7
    },
    ServiceType.FRIEND_CONNECT: {
        TraitType.PLAYFUL: 1.4,
        TraitType.ARTISTIC: 1.3,
        TraitType.BOOKWORM: 1.2,
        TraitType.LONER: 0.5
    }
}

FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS = 14 # Come da tua indicazione (14-16)
FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS = FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS * DXY

# Soglie di necessità per l'utilizzo spontaneo
SERVICE_NEED_THRESHOLDS = {
    ServiceType.AMORI_CURATI_PHASE1: {
        NeedType.INTIMACY: 43.2,
        NeedType.SOCIAL: 57.6
    },
    ServiceType.AMORI_CURATI_PHASE2: {
        NeedType.INTIMACY: 36.0,
        NeedType.ACHIEVEMENT: 72.0
    },
    ServiceType.FRIEND_CONNECT: {
        NeedType.SOCIAL: 50.4,
        NeedType.FUN: 64.8
    }
}

# --- Ritmo Circadiano (Ottimizzato per 28 ore) ---
CIRCADIAN_RHYTHM_CONFIG = {
    "SLEEP_WINDOW_START_HOUR": TimeOfDay.EVENING.start_hour,
    "SLEEP_WINDOW_END_HOUR": TimeOfDay.MORNING.start_hour - 2,
    "AWAKE_ENERGY_DECAY_MODIFIER": 1.0,
    "ASLEEP_ENERGY_DECAY_MODIFIER": 0.08,
    "SUMMER_LIGHT_MODIFIER": 1.2,
    "WINTER_LIGHT_MODIFIER": 0.8
}

# --- Parametri Circadiani per Fasi di Vita ---
LIFE_STAGE_CIRCADIAN_MODS = {
    LifeStage.INFANT: {
        "SLEEP_WINDOW_START_HOUR": 20,  # 20:00 Anthalys
        "SLEEP_WINDOW_END_HOUR": 8,     # 8:00 Anthalys (12 ore)
        "WAKE_CYCLES": 4
    },
    LifeStage.CHILD: {
        "SLEEP_WINDOW_START_HOUR": 21,  # 21:00 Anthalys
        "SLEEP_WINDOW_END_HOUR": 7,     # 7:00 Anthalys (10 ore)
        "ENERGY_DECAY_MOD": 0.85
    },
    LifeStage.MID_ADOLESCENCE: {
        "SLEEP_WINDOW_START_HOUR": 24,  # 24:00 Anthalys
        "SLEEP_WINDOW_END_HOUR": 10,    # 10:00 Anthalys (10 ore)
        "SOCIAL_MOD": 1.3
    },
    LifeStage.SENIOR: {
        "SLEEP_WINDOW_START_HOUR": 21,  # 21:00 Anthalys
        "SLEEP_WINDOW_END_HOUR": 5,     # 5:00 Anthalys (8 ore)
        "ENERGY_DECAY_MOD": 1.2
    }
}

# --- Soglie Comportamentali ---
SHY_NPC_CROWD_THRESHOLD: int = 3 # Un NPC timido si sente a disagio se ci sono più di 3 persone (incluso se stesso)

# Morte naturale (aggiornato con aspettativa di vita realistica)
AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS = 85.0
AGE_SENIOR_STARTS_CONSIDER_DEATH_DAYS = round(AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS * DXY)
DAILY_DEATH_CHANCE_MULTIPLIER_SENIOR = 0.0005

# --- Orientamenti Sessuali ---
CHANCE_NPC_IS_HETEROSEXUAL = 0.80
CHANCE_NPC_IS_HOMOSEXUAL = 0.08
CHANCE_NPC_IS_BISEXUAL = 0.05
CHANCE_NPC_IS_PANSEXUAL = 0.03
CHANCE_NPC_IS_ASEXUAL_SPECTRUM = 0.04
CHANCE_NPC_IS_AROMANTIC_SPECTRUM = 0.03
CHANCE_ROMANTIC_MATCHES_SEXUAL = 0.92

# --- SVILUPPO SESSUALE E IDENTITÀ ---
# Età in cui inizia il processo di solidificazione dell'orientamento sessuale
# (basato su studi di sviluppo adolescenziale)
AGE_ORIENTATION_SOLIDIFIES_START_YEARS = 14.0
AGE_ORIENTATION_SOLIDIFIES_START_DAYS = round(AGE_ORIENTATION_SOLIDIFIES_START_YEARS * DXY)

# Età in cui l'orientamento è tipicamente consolidato (range 18-25 anni)
AGE_ORIENTATION_SOLIDIFIES_END_YEARS = 21.0
AGE_ORIENTATION_SOLIDIFIES_END_DAYS = round(AGE_ORIENTATION_SOLIDIFIES_END_YEARS * DXY)

# Fattori che influenzano il processo
ORIENTATION_SOLIDIFICATION_FACTORS = {
    "GENETIC_HERITABILITY": 0.6,            # Componente genetica
    "EARLY_EXPERIENCES_IMPACT": 0.25,       # Esperienze infantili
    "SOCIAL_ENVIRONMENT_IMPACT": 0.15,      # Ambiente sociale
    "TRAIT_INFLUENCE": {                    # Influenza tratti personalità
        TraitType.CHILDISH: -0.3,
        TraitType.AMBITIOUS: 0.2,
        TraitType.SHY: -0.4,
        TraitType.UNINHIBITED: 0.3
    }
}

# Probabilità di esplorazione durante l'adolescenza
CHANCE_ORIENTATION_EXPLORATION_TEEN = 0.65

# --- Cura degli Infanti (Aggiornato) ---
INFANT_CARE_HUNGER_THRESHOLD = 57.6
INFANT_CARE_HYGIENE_THRESHOLD = 50.4
INFANT_CARE_BLADDER_THRESHOLD = 43.2
INFANT_CARE_SOCIAL_THRESHOLD = 64.8
PARENT_MIN_ENERGY_FOR_CARE = 57.6
PARENT_ENERGY_COST_FEEDING = 10.08

# --- Matching e Relazioni ---
DATING_CANDIDATE_MAX_AGE_DIFFERENCE_YEARS = 12 
DATING_CANDIDATE_MIN_AGE_YEARS = 18
DATING_CANDIDATE_MIN_AGE_DAYS = DATING_CANDIDATE_MIN_AGE_YEARS * DXY
FRIEND_MAX_AGE_DIFFERENCE_YEARS = 8
MAX_MATCHMAKING_SUGGESTIONS = 3

# --- Livelli di Dettaglio ---
LOD_DISTANCE_HIGH = 50.0
LOD_DISTANCE_MEDIUM = 150.0

# --- Guadagni da Azioni (Per tick) ---
ACTION_SATISFACTION_GAINS_PER_TICK = {
    "EAT": {
        NeedType.HUNGER: (93.6 * SXH) / TXH_SIMULATION,
        NeedType.COMFORT: (21.6 * SXH) / TXH_SIMULATION
    },
    "SLEEP": {
        NeedType.ENERGY: (122.4 * SXH) / TXH_SIMULATION,
        NeedType.COMFORT: (28.8 * SXH) / TXH_SIMULATION
    },
    "SOCIALIZE": {
        NeedType.SOCIAL: (72 * SXH) / TXH_SIMULATION,
        NeedType.FUN: (43.2 * SXH) / TXH_SIMULATION
    },
    "INTIMACY": {
        NeedType.INTIMACY: (108 * SXH) / TXH_SIMULATION,
        NeedType.COMFORT: (36 * SXH) / TXH_SIMULATION
    }
}

# --- Calcolo Durata Azioni in Tick ---
INFANT_FEEDING_DURATION_TICKS = (30 * IXH * SXI) / SECONDS_PER_SIMULATION_TICK  # 30 minuti
STANDARD_SLEEP_DURATION_TICKS = (8 * SXH) / SECONDS_PER_SIMULATION_TICK         # 8 ore
SOCIAL_ACTIVITY_DURATION_TICKS = (2 * SXH) / SECONDS_PER_SIMULATION_TICK       # 2 ore

# --------------------------------

# --- Generazione Nomi Casuali ---
MALE_NAMES = ["Marco", "Alessandro", "Luca", "Davide", "Matteo", "Francesco", "Lorenzo", "Andrea"]
FEMALE_NAMES = ["Giulia", "Sofia", "Aurora", "Alice", "Ginevra", "Chiara", "Emma", "Sara"]
LAST_NAMES = ["Rossi", "Ferrari", "Russo", "Bianchi", "Romano", "Gallo", "Costa", "Fontana"]

LASTNAME_PREFIXES = [
        "'Giacal", "Abatantu", "Abbatantu", "Acc", "Acciai", "Acciar", "Acco", 
        "Accorn", "Ad", "Adin", "Ador", "Ag", "Air", "Al", "Albergh", 
        "Albert", "Aldi", "Alf", "Alvar", "Alvi", "Amad", "Amazzon", "Ambros", 
        "Amend", "Anconet", "And", "Andre", "Antracen", "Anton", "Antonazz", 
        "Antu", "Ar", "Ard", "Ari", "Aric", "Arm", "Arrigh", "Art", "Ast", 
        "Aut", "Av", "B", "Ba", "Baboli", "Bacc", "Baccar", "Bacciag", 
        "Badal", "Bagn", "Balda", "Bald", "Ballari", "Banf", "Bar", "Barb", 
        "Barbag", "Barbar", "Barbo", "Barcar", "Barill", "Barnazz", "Baron", 
        "Barr", "Barz", "Bass", "Bassan", "Battist", "Battisto", "Baud", 
        "Bazz", "Begh", "Bel", "Bell", "Bella", "Bellin", "Bellol", "Ben", 
        "Benagl", "Benev", "Beni", "Ber", "Bergam", "Berl", "Berlusc", "Bern", 
        "Bernard", "Bert", "Bertev", "Bertol", "Béth", "Bi", "Bidd", "Bin", 
        "Bion", "Biss", "Bizz", "Bl", "Bocc", "Bod", "Boll", "Bolocc", "Bon", 
        "Boncompa", "Bonf", "Bor", "Bordigno", "Borl", "Borne", "Borr", 
        "Bort", "Bortol", "Borz", "Bott", "Bov", "Br", "Brad", "Bramb", 
        "Bressan", "Bri", "Brugn", "Brum", "Bug", "Bur", "Burr", "Bus", 
        "Busce", "C", "Cacciap", "Cafedd", "Calabr", "Calif", "Caligi", 
        "Calvanes", "Calzav", "Cam", "Camp", "Campagn", "Campit", "Cana", 
        "Cand", "Cangel", "Cann", "Cannal", "Cannavacci", "Cannavacciuol", 
        "Cannistr", "Cap", "Capann", "Car", "Carch", "Card", "Carl", 
        "Carlevar", "Carnev", "Cartasio", "Cas", "Casci", "Casir", "Cassiou", 
        "Cass", "Cast", "Cat", "Catal", "Cattapa", "Cav", "Cavacchi", 
        "Cavatto", "Cazz", "Cecc", "Cer", "Cerc", "Ceri", "Cerign", "Cerq", 
        "Cev", "Chabl", "Chiambr", "Chi", "Ci", "Ciarav", "Ciard", "Ciarr", 
        "Ciccol", "Circ", "Cirinn", "Co", "Coassi", "Cod", "Col", "Com", 
        "Cond", "Conde", "Contess", "Corb", "Corg", "Coron", "Corrid", 
        "Cortinov", "Corvi", "Coss", "Cost", "Covi", "Cr", "Cri", "Criser à", 
        "Crist", "Croci", "Cros", "Crosign", "Cul", "Cuné", "Curt", "Cusi", 
        "Cusm", "Custon", "Cut", "D", "D-'", "Dan", "De C", "De M", "Del Gr", 
        "Del", "Diémo", "Don", "Dor", "Dr", "Drom", "Du", "Ein", "F", "Fa", 
        "Fabi", "Fabr", "Falc", "Falcon", "Falconi", "Fall", "Fanti", "Farco", 
        "Fauss", "Fav", "Faz", "Fed", "Felic", "Feltr", "Fer", "Ferr", 
        "Ferrar", "Fi", "Fich", "Figi", "Figlio", "Fin", "Fiorin", "Fisc", 
        "Fl", "Fontan", "Form", "Formis", "Fr", "Frab", "Fracc", "Franc", 
        "Frattar", "Furla", "Fus", "G", "Gabb", "Gal", "Gale", "Gall", 
        "Gand", "Gar", "Gardell", "Gargi", "Garib", "Gasp", "Gast", "Gatt", 
        "Gaud", "Gazz", "Gen", "Ger", "Geron", "Gess", "Gi", "Giangregori", 
        "Giann", "Giard", "Giardini", "Giar", "Gif", "Gil", "Gilor", "Gioc", 
        "Giord", "Giorg", "Giovan", "Gir", "Girard", "Giss", "Giugli", "Go", 
        "Goll", "Gonzal", "Gorr", "Gr", "Grand", "Gregor", "Grett", "Grib", 
        "Grim", "Gris", "Grum", "Gu", "Guarn", "Guerr", "Guid", "Gum", 
        "Guzz", "I", "Iacov", "Iervol", "Interl", "Ior", "Jann", "L", 
        "Lagan", "Lamo", "Lampar", "Lamp", "Lampit", "Lanz", "Lav", 
        "Lazzar", "Lecc", "Lett", "Li", "Libr", "Libral", "Licc", "Licci", 
        "Livon", "Luc", "Luci", "Lucian", "Lucc", "Lur", "M", "Ma", 
        "Mabral", "Machiav", "Macr", "Mad", "Maddal", "Madril", "Madrin", 
        "Maff", "Mag", "Magg", "Mai", "Main", "Mal", "Malg", "Maln", 
        "Malp", "Malvolt", "Mammuc", "Man", "Manc", "Mand", "Mandr", 
        "Mangiav", "Mani", "Manz", "Mar", "Marang", "Marc", "Marco", 
        "March", "Marchigi", "Margherit", "Marguerett", "Mari", "Marigli", 
        "Martin", "Marr", "Martar", "Maruzz", "Marz", "Marzor", "Mas", 
        "Masc", "Masci", "Mass", "Massar", "Maso", "Matar", "Matal", 
        "Matt", "Matti", "Mazz", "Mazzol", "Mazzon", "Mel", "Melchi", 
        "Meneg", "Mi", "Mia", "Mic", "Mich", "Migliacci", "Migno", "Minch", 
        "Minerv", "Mir", "Modan", "Moden", "Mol", "Moli", "Molin", "Mom", 
        "Mon", "Monic", "Mont", "Montel", "Mor", "Mord", "Mostacciuol", 
        "Mull", "Munaf", "Muni", "Mur", "Mus", "Muzz", "N", "Nannar", 
        "Nard", "Nast", "Negl", "Nib", "Nic", "Nich", "Nicol", "Niedd", 
        "Nistic", "Nov", "Nunzi", "Nuzz", "Oli", "Oliv", "On", "Org", 
        "Orop", "Orr", "Ors", "Oz", "P", "Pac", "Pach", "Paci", "Padoa", 
        "Pag", "Pagn", "Pagli", "Pagliar", "Pal", "Palm", "Pan", "Pana", 
        "Panar", "Panariell", "Pand", "Pandi", "Pann", "Pani", "Papal", 
        "Par", "Parad", "Paradol", "Pari", "Parl", "Parol", "Passar", 
        "Pasqual", "Pasquett", "Pastor", "Pat", "Pav", "Pava", "Pazz", 
        "Pazzagli", "Pecor", "Pedr", "Pegli", "Pel", "Pell", "Penn", "Per", 
        "Peri", "Perre", "Perr", "Petacc", "Petracci", "Pezz", "Pi", "Pian", 
        "Pic", "Picc", "Piccir", "Pichl", "Pier", "Pieri", "Pilo", "Pin", 
        "Pineid", "Pint", "Pir", "Piscit", "Pol", "Polid", "Pom", "Porc", 
        "Porr", "Porz", "Pozz", "Pozzobo", "Pr", "Prattic", "Prestifilipp", 
        "Prestigiacom", "Pret", "Pri", "Proi", "Pronest", "Provenz", "Pugl", 
        "Pulz", "Puscion", "Puzz", "Quadr", "Quarantiell", "R", "Rache", 
        "Raddav", "Raff", "Rain", "Ramb", "Ramp", "Ran", "Rand", "Rav", 
        "Ravi", "Re", "Red", "Reg", "Regin", "Ren", "Resc", "Rib", "Ric", 
        "Ricc", "Ricciard", "Rid", "Rigam", "Rip", "Rizz", "Rom", "Romani", 
        "Ron", "Ronc", "Ronn", "Ros", "Ross", "Rossi", "Russ", "S", 
        "Saffir", "Sal", "Sang", "Sant", "Sar", "Sarto", "Sav", "Savar", 
        "Savi", "Savo", "Scaramuz", "Scaramuzz", "Scar", "Schiavo", "Schi", 
        "Schif", "Schirr", "Scilip", "Scim", "Scongliamigli", "Scud", "Se", 
        "Semer", "Serrai", "Serv", "Sever", "Sgarb", "Sgr", "Sid", "Simon", 
        "Simonc", "Sol", "Solin", "Sor", "Sov", "Spezz", "Spit", "Spital", 
        "St", "Stanzi", "Star", "Stor", "Stopp", "Strazz", "T", "Tab", 
        "Taglialat", "Tard", "Tart", "Tass", "Tauf", "Tav", "Tavol", "Ted", 
        "Terz", "Test", "Tib", "Tip", "Titomanl", "Toff", "Tomm", "Tr", 
        "Trab", "Trem", "Tremad", "Trevisa", "Trezz", "Trip", "Tro", "Tros", 
        "Trov", "Ub", "Urci", "V", "Vald", "Vallar", "Var", "Varri", 
        "Varricchi", "Varres", "Vass", "Vedov", "Ven", "Vend", "Vendra", 
        "Vendramin", "Venie", "Vent", "Ver", "Verc", "Verm", "Vern", 
        "Veron", "Verr", "Verrazz", "Verz", "Vetr", "Vezz", "Vi", "Vicer", 
        "Vida", "Vign", "Viol", "Vird", "Vis", "Visc", "Visch", "Visci", 
        "Viscia", "Visenti", "Visinti", "Viss", "Vit", "Volp", "Volpat", 
        "Vuillerm", "Wagn", "Z", "Zac", "Zacc", "Zaccar", "Zan", "Zangr", 
        "Zani", "Zano", "Zanon", "Zanonc", "Zanz", "Zanzar", "Zapp", "Zarl", 
        "Zen", "Zenn", "Zicc", "Zingal", "Zoin", "Zorz", "Zu'"
    ]
LASTNAME_SUFFIXES = [
        "a", "acchi", "acchio", "acci", "ace", "aci", "adi", "ago", "aghi", "aglia", 
        "aglio", "ai", "al", "ala", "ale", "ali", "aldi", "aldo", "ale", "alfi", 
        "ali", "alli", "allo", "aloro", "aloru", "ana", "andi", "ando", "ani", "ante", 
        "anti", "anzi", "ao", "ara", "ardi", "ari", "aro", "arri", "as", "aschi", 
        "asco", "asi", "asio", "aso", "assa", "assi", "asso", "astro", "ata", "ate", 
        "ati", "ato", "atti", "atto", "au", "audi", "audo", "auri", "auro", "auti", 
        "avi", "az", "azzi", "azzo", "à", "e", "ecchi", "ecchio", "ecci", "edda", 
        "edi", "ego", "eggi", "egli", "ei", "ela", "ele", "elfi", "eli", "ella", 
        "elle", "elli", "ello", "enghi", "engo", "eni", "enti", "enzi", "eo", "er", 
        "era", "erli", "erlo", "ero", "erri", "es", "eschi", "ese", "esi", "esio", 
        "essa", "essi", "esso", "etta", "etti", "evi", "ez", "ezzi", "è", "gni", 
        "i", "ia", "icchi", "icchio", "icci", "iccio", "idi", "ieri", "iero", "iello", 
        "iella", "iggi", "igli", "igo", "illa", "illi", "illo", "ina", "inghi", "ingo", 
        "ini", "ino", "inzi", "io", "is", "ise", "isi", "issa", "issi", "isso", 
        "ita", "iti", "ito", "itti", "iuoli", "izzi", "izio", "ì", "meni", "mi", 
        "n", "o", "occhi", "occhio", "occi", "oci", "odi", "oggi", "ogli", "oi", 
        "ola", "oldi", "oldo", "olfi", "olfo", "oli", "olla", "olli", "ollo", "olo", 
        "ona", "ondi", "ondo", "one", "oni", "ono", "onti", "onzi", "ora", "ordi", 
        "ori", "orri", "oschi", "osi", "ossa", "ossi", "osso", "ota", "oti", "otta", 
        "otti", "otto", "ou", "ovi", "oz", "ozzi", "ò", "r", "t", "u", "ucchi", 
        "ucci", "ucco", "udi", "ulfo", "uli", "ulla", "ulli", "ullo", "ulo", "uni", 
        "unti", "uolo", "uoli", "uoti", "uoto", "uozzi", "uozzo", "uri", "us", "uso", 
        "ussa", "ussi", "usso", "ut", "uta", "uti", "uto", "utta", "utti", "uzzi", 
        "uzzo", "y", "z"
    ]

