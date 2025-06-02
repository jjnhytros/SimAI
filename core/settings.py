# core/settings.py
"""
File centrale per le costanti globali e le impostazioni di base del gioco SimAI.
"""

# --- Impostazioni Generali del Gioco ---
GAME_NAME = "SimAI"
GAME_VERSION = "0.2.49-alpha_71"
DEBUG_MODE = False

# --- II. CALENDARIO E TEMPO DI ANTHALYS (Nomi variabili ESATTI come da config utente) ---
HXD = 28        # Ore per Giorno
DXM = 24        # Giorni per Mese
MXY = 18        # Mesi per Anno
DXW = 7         # Giorni per Settimana
DXY = MXY * DXM # Giorni per Anno (432)

IXH = 60        # mInuti per Ora
SXI = 60        # secondi per mInuto

# Costanti Derivate (Minuti)
IXD = IXH * HXD       # Minuti per Giorno
IXW = IXD * DXW       # Minuti per Settimana
IXM = IXD * DXM       # Minuti per Mese
IXY = IXD * DXY       # Minuti per Anno

# Costanti Derivate (Secondi)
SXH = SXI * IXH       # Secondi per Ora
SXD = SXH * HXD       # Secondi per Giorno
SXW = SXD * DXW       # Secondi per Settimana
SXM = SXD * DXM       # Secondi per Mese
SXY = SXD * DXY       # Secondi per Anno

# Costanti Lore e di Epoca
ATH_DATE_FORMAT = "Y, d/m G:i:s"
RDN = 951584400
RY = 5775
DXC = DXY * 100
ADN = RY * DXY

# Nomi Mesi e Giorni
MONTH_NAMES = [
    'Arejal', 'Brukom', 'Ĉelal', 'Kebor', 'Duvol', 'Elumag',
    'Fydrin', 'Ĝinuril', 'Itrekos', 'Jebrax', 'Letranat', 'Mulfus',
    'Nylumer', 'Otlevat', 'Prax', 'Retlixen', 'Sajep', 'Xetul'
]
DAY_NAMES = ['Nijahr', 'Majahr', 'Bejahr', 'Ĉejahr', 'Dyjahr', 'Fejahr', 'Ĝejahr'] # Nijahr=Giorno 0

MONTH_ABBR = {name: (name[:2] + 'x' if name == "Prax" else name[:3]) for name in MONTH_NAMES}
DAY_ABBR = {name: name[:2] for name in DAY_NAMES}

WEEKEND_DAY_NUMBERS = [6, 0] # Indici per Ĝejahr (Sabato) e Nijahr (Domenica/Giorno 0)

# Costante per i tick di simulazione (usata in vari calcoli di durata)
# Ipotizziamo 1 tick = 1 minuto di gioco, quindi 60 ticks per ora.
SIMULATION_TICKS_PER_HOUR = IXH

# --- Costanti Lavorative (Rif. TODO XXII.1) ---
STANDARD_WORK_HOURS_PER_DAY = 9
WORK_DAYS_PER_WEEK = DXW - len(WEEKEND_DAY_NUMBERS) # 5
# WORK_MONTHS_PER_YEAR e BREAK_MONTHS_PER_YEAR sono definiti come PRODUCTIVE_MONTHS_PER_YEAR
# e BREAK_MONTHS_PER_YEAR nella sezione SISTEMA REGOLAMENTARE GLOBALE più avanti.

# --- Costanti relative agli NPC (Rif. TODO IV) ---
MIN_TRAITS_PER_NPC = 3
MAX_TRAITS_PER_NPC = 5
MAX_NPC_ACTIVE_INTERESTS = 3

LIFE_STAGE_AGE_THRESHOLDS_DAYS = {
    "INFANCY": 0,
    "TODDLERHOOD": DXY * 1,
    "EARLY_CHILDHOOD": DXY * 3,
    "MIDDLE_CHILDHOOD": DXY * 6,
    "ADOLESCENCE": DXY * 12,
    "EARLY_ADULTHOOD": DXY * 20,
    "MIDDLE_ADULTHOOD": DXY * 40,
    "LATE_ADULTHOOD": DXY * 60,
    "ELDERLY": DXY * 80
}

# Morte Naturale per Anziani (TODO IV.2.e)
# Convertiamo 75.0 anni in giorni per coerenza con le soglie LifeStage.
AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS = 75.0
AGE_SENIOR_STARTS_CONSIDER_DEATH_DAYS = round(AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS * DXY)
DAILY_DEATH_CHANCE_MULTIPLIER_SENIOR = 0.0005 # Probabilità giornaliera di morte (da affinare)

# --- Sessualità e Riproduzione (TODO IV.2) ---
MIN_AGE_PUBERTY_FERTILITY_YEARS = 13
MIN_AGE_PUBERTY_FERTILITY_DAYS = MIN_AGE_PUBERTY_FERTILITY_YEARS * DXY

MIN_AGE_FOR_INTIMACY_YEARS = 14
MIN_AGE_FOR_INTIMACY_DAYS = MIN_AGE_FOR_INTIMACY_YEARS * DXY
MAX_AGE_FOR_INTIMACY_YEARS = 70
MAX_AGE_FOR_INTIMACY_DAYS = MAX_AGE_FOR_INTIMACY_YEARS * DXY

PREGNANCY_CHANCE_FEMALE = 0.20
PREGNANCY_DURATION_MONTHS_GAME = 9
PREGNANCY_DURATION_DAYS_GAME = PREGNANCY_DURATION_MONTHS_GAME * DXM
PREGNANCY_DURATION_TICKS = PREGNANCY_DURATION_DAYS_GAME * HXD * SIMULATION_TICKS_PER_HOUR

MIN_AGE_START_PREGNANCY_FEMALE_YEARS = 14
MIN_AGE_START_PREGNANCY_FEMALE_DAYS = MIN_AGE_START_PREGNANCY_FEMALE_YEARS * DXY
MAX_AGE_FERTILE_FEMALE_YEARS = 48
MAX_AGE_FERTILE_FEMALE_DAYS = MAX_AGE_FERTILE_FEMALE_YEARS * DXY

AGE_START_MENSTRUAL_CYCLE_YEARS_SET = {11.0, 13.0}
AGE_START_MENSTRUAL_CYCLE_DAYS_SET = {round(year * DXY) for year in AGE_START_MENSTRUAL_CYCLE_YEARS_SET}
AGE_MENOPAUSE_YEARS_SET = {50.0, 60.0}
AGE_MENOPAUSE_DAYS_SET = {round(year * DXY) for year in AGE_MENOPAUSE_YEARS_SET}

# Orientamento Sessuale e Romantico (TODO IV.3.j)
CHANCE_NPC_IS_HETEROSEXUAL = 0.85
CHANCE_NPC_IS_HOMOSEXUAL = 0.07
CHANCE_NPC_IS_BISEXUAL = 0.03
CHANCE_NPC_IS_PANSEXUAL = 0.01
CHANCE_NPC_IS_ASEXUAL_SPECTRUM = 0.02
CHANCE_NPC_IS_AROMANTIC_SPECTRUM = 0.02
CHANCE_ROMANTIC_MATCHES_SEXUAL = 0.95
# AGE_ORIENTATION_SOLIDIFIES_START_TEEN_YEARS = 14.0 # Esempio per futuro sviluppo

# --- SISTEMA DEI BISOGNI (TODO IV.1) ---
# Tassi di Decadimento Base (punti persi per tick di simulazione)
HUNGER_DECAY_RATE = 0.08
ENERGY_DECAY_RATE = 0.05
SOCIAL_DECAY_RATE = 0.06
FUN_DECAY_RATE = 0.07
HYGIENE_DECAY_RATE = 0.1
BLADDER_DECAY_RATE = 0.12
INTIMACY_DECAY_RATE = 0.03
# Moltiplicatori specifici
TEEN_SOCIAL_DECAY_MULTIPLIER_IDLE = 1.5
TEEN_FUN_DECAY_MULTIPLIER_IDLE_OR_SCHOOL = 1.3

# Soglie Bisogni
CRITICAL_NEED_THRESHOLD = 20
LOW_NEED_THRESHOLD = 40
INTIMACY_LOW_THRESHOLD = 50
CHILD_FUN_SEEK_THRESHOLD = 55

# Guadagni da Azioni Base (quanto un'azione soddisfa un bisogno)
EAT_GAIN = 75
SLEEP_GAIN = 80
SOCIALIZE_GAIN = 45
WATCH_TV_GAIN = 35
USE_BATHROOM_GAIN = 100
INTIMACY_ACTION_GAIN = 70
CHILD_PLAY_FUN_GAIN = 50

# Cura Infanti (TODO IV.4.e)
INFANT_CARE_HUNGER_THRESHOLD = 35
INFANT_CARE_HYGIENE_THRESHOLD = 30
INFANT_CARE_BLADDER_THRESHOLD = 30
INFANT_CARE_SOCIAL_THRESHOLD = 40
INFANT_CARE_MOOD_TRIGGER_NAME = "MISERABLE" # Assumendo che sia una stringa ID per un moodlet
PARENT_MIN_ENERGY_FOR_CARE = LOW_NEED_THRESHOLD + 5 # Es. 45
PARENT_ENERGY_COST_FEEDING = 8
# ... (altre costanti INFANT_CARE e PARENT_COST/GAIN andranno qui)
DURATION_FEEDING_INFANT_TICKS = SIMULATION_TICKS_PER_HOUR // 2 # Esempio: 30 minuti
# ... (altre DURATION_INFANT_CARE_..._TICKS andranno qui)

# --- Costanti relative alle Abilità (Skills) (Rif. TODO IX) ---
DEFAULT_MAX_SKILL_LEVEL = 12
MIN_SKILL_LEVEL_FOR_MENTORING = 7

# --- Costanti Economiche e Fiscali (Rif. TODO VIII, XIX, XXII) ---
CURRENCY_NAME = "Athel"
CURRENCY_SYMBOL = "Ꜳ"
CSC_C_STANDARD_RATE = 0.12
CSC_R_INCOME_EXEMPTION_THRESHOLD = 3000.0
CASINO_MAX_WIN_PER_PLAY = 10000.0
CASINO_WIN_TAX_EXEMPTION_THRESHOLD = 600.0
BETTING_AMOUNT_TAX_EXEMPTION_THRESHOLD = 6000.0

# --- SISTEMA SCOLASTICO (TODO V) ---
# Età di INIZIO per ogni livello scolastico (in ANNI, poi convertite in GIORNI)
SCHOOL_AGE_START_INFANCY_EDUCATION_YEARS = 1.0
SCHOOL_AGE_START_LOWER_ELEMENTARY_YEARS = 3.0
SCHOOL_AGE_START_UPPER_ELEMENTARY_YEARS = 6.0
SCHOOL_AGE_START_LOWER_MIDDLE_YEARS = 9.0
SCHOOL_AGE_START_UPPER_MIDDLE_YEARS = 12.0
SCHOOL_AGE_START_HIGH_SCHOOL_YEARS = 15.0
SCHOOL_AGE_START_PRE_UNIVERSITY_YEARS = 18.0
SCHOOL_AGE_START_UNIVERSITY_YEARS = 21.0

SCHOOL_AGE_START_INFANCY_EDUCATION_DAYS = round(SCHOOL_AGE_START_INFANCY_EDUCATION_YEARS * DXY)
SCHOOL_AGE_START_LOWER_ELEMENTARY_DAYS = round(SCHOOL_AGE_START_LOWER_ELEMENTARY_YEARS * DXY)
SCHOOL_AGE_START_UPPER_ELEMENTARY_DAYS = round(SCHOOL_AGE_START_UPPER_ELEMENTARY_YEARS * DXY)
SCHOOL_AGE_START_LOWER_MIDDLE_DAYS = round(SCHOOL_AGE_START_LOWER_MIDDLE_YEARS * DXY)
SCHOOL_AGE_START_UPPER_MIDDLE_DAYS = round(SCHOOL_AGE_START_UPPER_MIDDLE_YEARS * DXY)
SCHOOL_AGE_START_HIGH_SCHOOL_DAYS = round(SCHOOL_AGE_START_HIGH_SCHOOL_YEARS * DXY)
SCHOOL_AGE_START_PRE_UNIVERSITY_DAYS = round(SCHOOL_AGE_START_PRE_UNIVERSITY_YEARS * DXY)
SCHOOL_AGE_START_UNIVERSITY_DAYS = round(SCHOOL_AGE_START_UNIVERSITY_YEARS * DXY)

# Durata "standard" in anni per ogni livello
DURATION_INFANCY_EDUCATION_YEARS = SCHOOL_AGE_START_LOWER_ELEMENTARY_YEARS - SCHOOL_AGE_START_INFANCY_EDUCATION_YEARS
DURATION_LOWER_ELEMENTARY_YEARS = SCHOOL_AGE_START_UPPER_ELEMENTARY_YEARS - SCHOOL_AGE_START_LOWER_ELEMENTARY_YEARS
DURATION_UPPER_ELEMENTARY_YEARS = SCHOOL_AGE_START_LOWER_MIDDLE_YEARS - SCHOOL_AGE_START_UPPER_ELEMENTARY_YEARS
DURATION_LOWER_MIDDLE_YEARS = SCHOOL_AGE_START_UPPER_MIDDLE_YEARS - SCHOOL_AGE_START_LOWER_MIDDLE_YEARS
DURATION_UPPER_MIDDLE_YEARS = SCHOOL_AGE_START_HIGH_SCHOOL_YEARS - SCHOOL_AGE_START_UPPER_MIDDLE_YEARS
DURATION_HIGH_SCHOOL_YEARS = SCHOOL_AGE_START_PRE_UNIVERSITY_YEARS - SCHOOL_AGE_START_HIGH_SCHOOL_YEARS
DURATION_PRE_UNIVERSITY_YEARS = SCHOOL_AGE_START_UNIVERSITY_YEARS - SCHOOL_AGE_START_PRE_UNIVERSITY_YEARS
DURATION_UNIVERSITY_YEARS_TYPICAL_DEGREE = 3
SCHOOL_AGE_MAX_UNIVERSITY_ENROLLMENT_YEARS = 28.0 # Esempio
SCHOOL_AGE_MAX_UNIVERSITY_ENROLLMENT_DAYS = round(SCHOOL_AGE_MAX_UNIVERSITY_ENROLLMENT_YEARS * DXY)

# Calendario Scolastico Annuale (TODO V.1.b)
SCHOOL_MONTHS_PERIOD_1_START = 1    # Primo mese del primo periodo scolastico (1-6)
SCHOOL_MONTHS_PERIOD_1_END = 6
SCHOOL_MONTHS_PERIOD_2_START = 10   # Primo mese del secondo periodo scolastico (10-15)
SCHOOL_MONTHS_PERIOD_2_END = 15
# Le pause sono i mesi intermedi (7-9 e 16-18)

# Orari e Compiti
SCHOOL_HOURS_START = 8  # Orario inizio lezioni
SCHOOL_HOURS_END = 15   # Orario fine lezioni
HOMEWORK_DURATION_TICKS = SIMULATION_TICKS_PER_HOUR * 1 # 1 ora di gioco per i compiti
HOMEWORK_HOURS_START = 16 # Orario tipico per iniziare i compiti
HOMEWORK_HOURS_END = 20   # Orario limite

# Performance Scolastica
INITIAL_SCHOOL_PERFORMANCE = 50.0
MAX_SCHOOL_PERFORMANCE = 100.0
MIN_SCHOOL_PERFORMANCE = 0.0
PERF_CHANGE_ATTEND_SCHOOL_BASE = 1.0
PERF_CHANGE_MOOD_HAPPY_BONUS = 0.5
PERF_CHANGE_MOOD_UNHAPPY_MALUS = -0.8
PERF_CHANGE_ENERGY_LOW_MALUS = -0.5
PERF_CHANGE_ENERGY_CRITICAL_MALUS = -1.0
PERF_CHANGE_HOMEWORK_DONE_BONUS = 3.0
PERF_CHANGE_HOMEWORK_MISSED_MALUS = -4.0
PERF_CHANGE_SKIPPED_SCHOOL_MALUS = -5.0
CHANCE_TO_SKIP_SCHOOL_BASE = 0.05
TRAIT_PERF_GAIN_MOD_AMBITIOUS = 1.2
TRAIT_PERF_GAIN_MOD_GENIUS = 1.5
TRAIT_PERF_GAIN_MOD_LAZY = 0.6
SCHOOL_PERF_EXCELLENT_THRESHOLD = 85
SCHOOL_PERF_POOR_THRESHOLD = 35
MOOD_BOOST_EXCELLENT_PERF = 15
MOOD_PENALTY_POOR_PERF = -15
MOODLET_DURATION_SCHOOL_PERF_DAYS = 3.0 # Durata del moodlet da performance scolastica

# Guadagno Skill "Learning" (o skill accademiche)
BASE_SKILL_GAIN_PER_SCHOOL_DAY = 0.05
BASE_SKILL_GAIN_PER_HOMEWORK_DONE = 0.08
SKILL_GAIN_PERF_TIER_1_THRESHOLD = 25.0
SKILL_GAIN_PERF_TIER_2_THRESHOLD = 50.0
SKILL_GAIN_PERF_TIER_3_THRESHOLD = 75.0
LEARNING_SKILL_GAIN_MULTIPLIER_POOR = 0.2
LEARNING_SKILL_GAIN_MULTIPLIER_AVERAGE = 0.6
LEARNING_SKILL_GAIN_MULTIPLIER_GOOD = 1.0
LEARNING_SKILL_GAIN_MULTIPLIER_EXCELLENT = 1.5
# ... (Altri TRAIT_LEARNING_SPEED_MOD e TRAIT_SKIP_SCHOOL_MOD andranno qui)

# --- SISTEMA REGOLAMENTARE GLOBALE (TODO XXII) ---
# Orario di Lavoro
# STANDARD_WORK_HOURS_PER_DAY = 9 (già definito sopra)
# WORK_DAYS_PER_WEEK = 5 (già definito sopra)
PRODUCTIVE_MONTHS_PER_YEAR_REG = 15 # Rinominato per evitare conflitto con quello lavorativo, si riferisce a XXII.1.c.i
BREAK_MONTHS_PER_YEAR_REG = 3       # Rinominato, si riferisce a XXII.1.c.ii
WORK_DAYS_PER_YEAR_EFFECTIVE = 300  # Come da tua specifica (logica di calcolo da rivedere se necessario)
STANDARD_ANNUAL_WORK_HOURS = STANDARD_WORK_HOURS_PER_DAY * WORK_DAYS_PER_YEAR_EFFECTIVE # 2700 ore

# Lavoro Minorile (Medie Superiori: 13-15 anni, come da TODO XXII.1.d)
# Convertiamo età in giorni per coerenza
AGE_MINOR_UPPER_MIDDLE_START_YEARS = 12 # Inizio Medie Sup.
AGE_MINOR_UPPER_MIDDLE_END_YEARS = 15   # Fine Medie Sup. (non compiuti)
PART_TIME_MAX_HOURS_PER_DAY_MINOR = 5.25
PART_TIME_MIN_ANNUAL_HOURS_PERCENTAGE = 0.50
PART_TIME_MAX_ANNUAL_HOURS_PERCENTAGE = 0.666

# Politiche Retributive (TODO XXII.2)
SALARY_RANGES_ATHEL_ANNUAL = { # AA Annui
    "BASE_EMPLOYMENT": (18000, 36000),
    "SPECIALIZED_EMPLOYMENT": (36000, 72000),
    "HIGH_QUALIFICATION_EMPLOYMENT": (72000, 144000),
    "MANAGERIAL_POSITION": (144000, 288000)
}
YEARS_OF_SERVICE_FOR_SENIORITY_BONUS = 2
FIRST_SENIORITY_BONUS_PERCENTAGE = 0.01
SUBSEQUENT_SENIORITY_BONUS_FACTOR = 0.001
MAX_SENIORITY_BONUS_PERCENTAGE_PER_STEP = 0.025

# Regolamentazione Fiscale (TODO XXII.3, VIII.2)
# TAX_EXEMPTION_INCOME_THRESHOLD = 3000 (già definito come CSC_R_INCOME_EXEMPTION_THRESHOLD)
TAX_BRACKETS_CSC_R = [ # (Limite Superiore Scaglione in Athel, Aliquota %)
    (3000, 0.0), (6000, 0.015), (12000, 0.03), (15000, 0.045), (18000, 0.06),
    (21000, 0.075), (24000, 0.09), (27000, 0.105), (30000, 0.12), (33000, 0.135),
    (36000, 0.15), (39000, 0.165), (42000, 0.18), (45000, 0.195), (48000, 0.21),
    (51000, 0.225), (144000, 0.24), (float('inf'), 0.26)
]
TAX_COLLECTION_PERIOD_DAYS = 216 # Ogni 9 mesi

# Benefici e Sicurezza Sociale (TODO XXII.4)
HEALTH_INSURANCE_CONTRIBUTION_HOURS_DIVISOR = 100.0
HEALTH_INSURANCE_MINOR_AGE_EXEMPTION_YEARS = 16
PENSION_MIN_YEARS_OF_SERVICE = 20
PENSION_MIN_HOURS_OF_SERVICE_EQUIVALENT = 54000 # Da verificare se questo è il modo corretto di calcolarlo
PENSION_BASE_PERCENTAGE = 0.50
PENSION_MAX_AGE_PLUS_SERVICE_SUM = 96
PENSION_MAX_PERCENTAGE = 1.00
PENSION_ANNUAL_ADJUSTMENT_PERCENTAGE = 0.01
PENSION_TAX_RATE = 0.015
LOW_INCOME_HEALTH_COVERAGE_THRESHOLD_ATHEL = 6000 # AA Annui
# ANNUAL_VACATION_DAYS è definito sopra come ANNUAL_VACATION_DAYS_STANDARD
# La regola "(9 ore ogni 192 lavorate)" è una logica di calcolo, non una costante singola.
# Potremmo definire:
HOURS_WORKED_PER_VACATION_HOUR = 192 / 9 # Circa 21.33 ore lavorate per 1 ora di vacanza.

# --- VII. CONFIGURAZIONE TRATTI DI PERSONALITÀ (TODO IV.3.b) ---
# Esempio di costante specifica per un tratto:
MOODLET_AMBITIOUS_CAREER_SUCCESS_ID = "ambitious_career_success" # ID del moodlet
AMBITIOUS_SUCCESS_MOOD_BOOST = 20                             # Valore del mood boost
# Costanti per effetti di background dei tratti (come da tue note)
BG_TRAIT_EFFECT_CHEERFUL_WELLBEING = 0.2
BG_TRAIT_EFFECT_GLOOMY_WELLBEING = -0.25 # Assumendo sia un malus
BG_TRAIT_EFFECT_JADED_WELLBEING = -0.15   # Assumendo sia un malus
BG_TRAIT_EFFECT_HIGH_MAINTENANCE_IRRITATION = 0.4 # Probabilità o intensità
BG_TRAIT_EFFECT_PARANOID_ANXIETY = 0.1
BG_TRAIT_EFFECT_SAD_SEASONAL = 0.2
BG_TRAIT_EFFECT_HATES_HEAT = 0.25
BG_TRAIT_EFFECT_CANT_STAND_COLD = 0.25
BG_TRAIT_EFFECT_CHRONIC_HEADACHE = 0.3
BG_TRAIT_EFFECT_CHRONIC_ILLNESS_MALAISE = 0.15
# Conflitti tra tratti (TODO IV.3.b.ix, IV.3.b.x.1)
# Usare stringhe dei nomi Enum dei tratti per evitare import circolari qui.
# La logica di gestione dei conflitti userà queste stringhe per confrontare.
TRAIT_CONFLICTS_AS_STRINGS = [
    {"FERTILE", "INFERTILE"}, # Esempio
    {"MONOGAMOUS", "POLYAMOROUS"}, # Esempio
    # ... (elenco completo dei set di tratti incompatibili)
]

# --- VIII. CONFIGURAZIONE METEO (Planetaria e Climatica) (TODO XXVI, I.3.e) ---
PLANET_AXIAL_TILT_DEGREES = 28.183239
PLANET_ORBITAL_ECCENTRICITY = 1 / 34.9930626953
DEFAULT_LATITUDE_ANTHALYS = 45.0
DEFAULT_ALTITUDE_ANTHALYS_METERS = 300
WEATHER_CALIBRATION_LOGFILE = "weather_calibration.log"
ENABLE_WEATHER_CALIBRATION_LOG = False

# --- FUNZIONALITÀ SPECIFICHE SONET (Es. Amori Curati) --- NUOVA SEZIONE
# Età minime di accesso per le diverse fasi del servizio "Amori Curati"
# Riferimento lore: Adolescenza (Fase 1 da 18 anni), Prima Età Adulta (Fase 2 da 25 anni)
AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS = 18
AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS = AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS * DXY

AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS = 25
AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_DAYS = AMORI_CURATI_PHASE2_ACCESS_MIN_AGE_YEARS * DXY

# NUOVA COSTANTE: Età minima per il servizio "Trova Amici"
FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS = 14 # Come da tua indicazione (14-16)
FRIEND_CONNECT_MIN_ACCESS_AGE_DAYS = FRIEND_CONNECT_MIN_ACCESS_AGE_YEARS * DXY

MAX_MATCHMAKING_SUGGESTIONS = 3

# Potremmo anche definire una differenza di età per la ricerca di amici,
# potrebbe essere diversa da quella per il dating.
FRIEND_MAX_AGE_DIFFERENCE_YEARS = 10 # Esempio, più stretta per coetanei o più larga?

# --- IX. INTERFACCIA UTENTE (TUI) (TODO XI) ---
# Esempio di costanti per la TUI, da popolare in base al design
# HEADER_HEIGHT_CURSES = 3
# LOG_WINDOW_HEIGHT_CURSES = 10
# ...

# --- X. SALVATAGGIO E REPORT (TODO XV, XIV.a) ---
AUTOSAVE_ON_DAY_END = True
ENABLE_CONSOLE_DAILY_REPORT = True
ENABLE_CONSOLE_MONTHLY_REPORT = True
ENABLE_CONSOLE_ANNUAL_REPORT = True
ENABLE_CONSOLE_HOURLY_SUMMARY_IN_CONTINUOUS = True
HOURLY_SUMMARY_INTERVAL = 3 # Ore
HOURLY_SUMMARY_INTERVAL_CONTINUOUS_MODE = 6 # Ore

ENABLE_FILE_REPORTS = True
REPORT_FILENAME = "simai_simulation_chronicles.log"
ENABLE_FILE_DAILY_REPORT = True
ENABLE_FILE_MONTHLY_REPORT = True
ENABLE_FILE_ANNUAL_REPORT = True

# --- XI. Colori ANSI (TODO XI.1.e) ---
class ANSIColors: # Classe per raggruppare i codici colore
    RESET = "\033[0m"; BOLD = "\033[1m"
    # Colori per genere (esempio)
    MALE_COLOR = "\033[96m"     # Ciano brillante
    FEMALE_COLOR = "\033[95m"   # Magenta brillante
    # Colori per bisogni (esempio)
    NEED_HUNGER_COLOR = "\033[31m"    # Rosso
    NEED_ENERGY_COLOR = "\033[34m"    # Blu
    NEED_SOCIAL_COLOR = "\033[32m"    # Verde
    NEED_FUN_COLOR = "\033[33m"       # Giallo
    NEED_HYGIENE_COLOR = "\033[36m"   # Ciano
    NEED_BLADDER_COLOR = "\033[35m"   # Magenta
    NEED_INTIMACY_COLOR = "\033[91m"  # Rosso brillante
    # Colori per eventi (esempio)
    EVENT_POSITIVE_COLOR = "\033[92m" # Verde brillante
    EVENT_NEGATIVE_COLOR = "\033[91m" # Rosso brillante
    EVENT_NEUTRAL_COLOR = "\033[94m"  # Blu brillante
    # Altri colori UI
    REPORT_TITLE_COLOR = "\033[1m\033[93m" # Giallo brillante grassetto
    DEBUG_COLOR = "\033[1m\033[93m"        # Giallo brillante grassetto

print("  [Settings] Modulo settings.py caricato.")

# --- Impostazioni per Matching e Relazioni (Nuova Sezione o esistente) ---
# Differenza di età massima in anni per considerare un candidato per appuntamenti
DATING_CANDIDATE_MAX_AGE_DIFFERENCE_YEARS = 15 
DATING_CANDIDATE_MIN_AGE_YEARS = AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_YEARS # Devono almeno poter usare la fase 1
                                                                            # o l'età di inizio EARLY_ADULTHOOD
DATING_CANDIDATE_MIN_AGE_DAYS = DATING_CANDIDATE_MIN_AGE_YEARS * DXY


# --- Valori e Dinamiche dei Bisogni (Needs) ---
# Riferimento TODO: V.a.ii, V.a.iii
NEED_MIN_VALUE: float = 0.0     # Valore minimo che un bisogno può raggiungere (molto negativo)
NEED_MAX_VALUE: float = 100.0   # Valore massimo (completamente soddisfatto)
NEED_DEFAULT_START_MIN: float = 50.0 # Valore iniziale minimo per un nuovo NPC
NEED_DEFAULT_START_MAX: float = 80.0 # Valore iniziale massimo per un nuovo NPC

# Tassi di decadimento dei bisogni (punti persi PER ORA di gioco).
# Valori negativi indicano un decadimento.
# Le chiavi sono i nomi dei membri dell'Enum NeedType.
# Questi valori andranno bilanciati con il testing!
NEED_DECAY_RATES: dict[str, float] = {
    "ACHIEVEMENT": -0.2,   # Esempio, o potrebbe non decadere passivamente
    "AUTONOMY": -0.3,     # Esempio
    "BLADDER": -8.0,
    "COMFORT": -1.0,
    "CREATIVITY": -0.3,   # Esempio
    "ENERGY": -5.0,
    "ENVIRONMENT": -0.5,
    "FUN": -3.0,
    "HUNGER": -4.2,
    "HYGIENE": -2.0,
    "INTIMACY": -1.5,
    "LEARNING": -0.2,     # Esempio, potrebbe non decadere o dipendere da attività
    "SAFETY": -0.5,       # Esempio di tasso, da bilanciare
    "SOCIAL": -2.5,
    "SPIRITUALITY": -0.4, # Esempio
    "THIRST": -3.5
}

# Soglie di criticità per i bisogni (quando un bisogno diventa un problema serio)
NEED_CRITICAL_THRESHOLD: float = 10.0  # MODIFICATO: Sotto 10 è critico
NEED_LOW_THRESHOLD: float = 25.0     # MODIFICATO: Sotto 25 è basso
NEED_HIGH_THRESHOLD: float = 75.0    # Utile per bisogni come Comfort o Ambiente (bene stare sopra)

# --- Valori Bisogni al Risveglio ---
# Valori a cui i bisogni vengono impostati dopo un ciclo di sonno completo.
# Questi valori possono essere usati per calcolare il delta da applicare.
NEED_VALUE_ON_WAKE_HUNGER = 40.0  # L'NPC si sveglia affamato
NEED_VALUE_ON_WAKE_THIRST = 30.0  # L'NPC si sveglia assetato
NEED_VALUE_ON_WAKE_BLADDER = 20.0 # L'NPC si sveglia con la vescica piena

EAT_ACTION_DURATION_TICKS: int = 30
EAT_ACTION_HUNGER_GAIN: float = 75.0
DRINK_WATER_DURATION_TICKS: int = 10
DRINK_WATER_THIRST_GAIN: float = 80.0


# Moltiplicatori di decadimento (potrebbero essere usati per tratti, età, ecc. in futuro)
# Esempio: NEED_DECAY_MULTIPLIER_CHILD: float = 1.2 # I bambini potrebbero avere bisogni che decadono più velocemente
# MIN_AGE_FOR_INTIMACY_YEARS e MIN_AGE_FOR_INTIMACY_DAYS sono già in settings.py
# e verranno usati in Character.py per il decadimento condizionato di INTIMACY.
EAT_GAIN_ACTION: float = 75.0 # Guadagno da un pasto normale (su scala 0-100)
EAT_ACTION_DURATION_TICKS: int = 30   # 30 minuti di gioco per un pasto
EAT_ACTION_HUNGER_GAIN: float = 75.0  # Un pasto completo soddisfa di 75 punti fame (su 100)
