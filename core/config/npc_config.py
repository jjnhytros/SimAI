# simai/core/config/npc_config.py
"""
Configurazione NPC, tratti, bisogni e ciclo di vita
"""

from .time_config import DXY, DXM
from core.enums import NeedType

# --- SOGLIE E VALORI GENERALI DEI BISOGNI ---
NEED_MIN_VALUE: float = 0.0
NEED_MAX_VALUE: float = 100.0
NEED_DEFAULT_START_MIN: float = 50.0    # Valore minimo all'inizializzazione dell'NPC
NEED_DEFAULT_START_MAX: float = 80.0    # Valore massimo all'inizializzazione
NEED_LOW_THRESHOLD: float = 25.0        # Sotto questa soglia, l'NPC considera di agire
NEED_HIGH_THRESHOLD = 75.0              # non fare questa azione se il bisogno è già quasi pieno
NEED_CRITICAL_THRESHOLD: float = 10.0   # Sotto questa soglia, il bisogno è critico

# --- Generazione NPC ---
MIN_TRAITS_PER_NPC = 3
MAX_TRAITS_PER_NPC = 5
MAX_NPC_ACTIVE_INTERESTS = 3

# --- PESI PER L'IA ---
# Pesi per i bisogni usati da AIDecisionMaker e NeedsProcessor
NEED_WEIGHTS: dict[NeedType, float] = {
    NeedType.HUNGER: 1.5,
    NeedType.THIRST: 1.6, 
    NeedType.ENERGY: 1.4,
    NeedType.BLADDER: 1.3,
    NeedType.HYGIENE: 1.0,
    NeedType.FUN: 0.8,
    NeedType.SOCIAL: 0.7,
    NeedType.INTIMACY: 0.6,
    # Aggiungere pesi per altri NeedType quando implementati
}

# Modificatore di urgenza per bisogni critici
CRITICAL_NEED_THRESHOLD_MODIFIER: float = 1.5

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

AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS = 75.0
AGE_SENIOR_STARTS_CONSIDER_DEATH_DAYS = round(AGE_SENIOR_STARTS_CONSIDER_DEATH_YEARS * DXY)
DAILY_DEATH_CHANCE_MULTIPLIER_SENIOR = 0.0005

# --- Riproduzione e Sessualità ---
MIN_AGE_PUBERTY_FERTILITY_YEARS = 13
MIN_AGE_PUBERTY_FERTILITY_DAYS = MIN_AGE_PUBERTY_FERTILITY_YEARS * DXY

MIN_AGE_FOR_INTIMACY_YEARS = 14
MIN_AGE_FOR_INTIMACY_DAYS = MIN_AGE_FOR_INTIMACY_YEARS * DXY
MAX_AGE_FOR_INTIMACY_YEARS = 70
MAX_AGE_FOR_INTIMACY_DAYS = MAX_AGE_FOR_INTIMACY_YEARS * DXY

PREGNANCY_CHANCE_FEMALE = 0.20
PREGNANCY_DURATION_MONTHS_GAME = 9
PREGNANCY_DURATION_DAYS_GAME = PREGNANCY_DURATION_MONTHS_GAME * DXM

MIN_AGE_START_PREGNANCY_FEMALE_YEARS = 14
MIN_AGE_START_PREGNANCY_FEMALE_DAYS = MIN_AGE_START_PREGNANCY_FEMALE_YEARS * DXY
MAX_AGE_FERTILE_FEMALE_YEARS = 48
MAX_AGE_FERTILE_FEMALE_DAYS = MAX_AGE_FERTILE_FEMALE_YEARS * DXY

AGE_START_MENSTRUAL_CYCLE_YEARS_SET = {11.0, 13.0}
AGE_START_MENSTRUAL_CYCLE_DAYS_SET = {round(year * DXY) for year in AGE_START_MENSTRUAL_CYCLE_YEARS_SET}
AGE_MENOPAUSE_YEARS_SET = {50.0, 60.0}
AGE_MENOPAUSE_DAYS_SET = {round(year * DXY) for year in AGE_MENOPAUSE_YEARS_SET}

CHANCE_NPC_IS_HETEROSEXUAL = 0.85
CHANCE_NPC_IS_HOMOSEXUAL = 0.07
CHANCE_NPC_IS_BISEXUAL = 0.05
CHANCE_NPC_IS_PANSEXUAL = 0.03
CHANCE_NPC_IS_ASEXUAL_SPECTRUM = 0.02
CHANCE_NPC_IS_AROMANTIC_SPECTRUM = 0.02
CHANCE_ROMANTIC_MATCHES_SEXUAL = 0.95

NEED_DECAY_RATES: dict[NeedType, float] = {
    NeedType.ACHIEVEMENT: -0.2,
    NeedType.AUTONOMY: -0.3,
    NeedType.BLADDER: -8.0,
    NeedType.COMFORT: -1.0,
    NeedType.CREATIVITY: -0.3,
    NeedType.ENERGY: -5.0,
    NeedType.ENVIRONMENT: -0.5,
    NeedType.FUN: -3.0,
    NeedType.HUNGER: -4.2,
    NeedType.HYGIENE: -2.0,
    NeedType.INTIMACY: -1.5,
    NeedType.LEARNING: -0.2,
    NeedType.SAFETY: -0.5,
    NeedType.SOCIAL: -2.5,
    NeedType.SPIRITUALITY: -0.4,
    NeedType.THIRST: -5.5, # Assicurati di avere THIRST qui
}

# Modificatore di urgenza per bisogni critici
CRITICAL_NEED_THRESHOLD_MODIFIER: float = 1.5

# Soglia di urgenza sopra la quale l'IA considera un problema per la decisione
AI_URGENT_PROBLEM_THRESHOLD: float = 0.5 # Esempio: considera problemi con urgenza > 50%
