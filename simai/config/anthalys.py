"""Costanti del calendario, stagioni, fasi giornaliere e cicli di vita Anthalys.

Fonti lore:
  - 432 giorni / 18 mesi / 24 giorni per mese / 28 ore per giorno
  - 4 stagioni da 108 giorni; l'inverno inizia il giorno 16 del mese 18
  - Aspettativa di vita: M 144-156, F 156-168
  - Fasce pediatriche e psicosociali (PARTE II del TODO)
"""

from typing import Final

# ---------------------------------------------------------------------------
# Calendario
# ---------------------------------------------------------------------------

DAYS_PER_YEAR: Final[int] = 432
MONTHS_PER_YEAR: Final[int] = 18
DAYS_PER_MONTH: Final[int] = 24
HOURS_PER_DAY: Final[int] = 28
MINUTES_PER_HOUR: Final[int] = 60
SECONDS_PER_MINUTE: Final[int] = 60

WEEKDAYS: Final[tuple[str, ...]] = (
    "Nijahr",
    "Majahr",
    "Bejahr",
    "Ĉejahr",
    "Dyjahr",
    "Fejahr",
    "Ĝejahr",
)

MONTHS: Final[tuple[str, ...]] = (
    "Arejal",
    "Brukom",
    "Ĉelal",
    "Kebor",
    "Duvol",
    "Elumag",
    "Fydrin",
    "Ĝinuril",
    "Itrekos",
    "Jebrax",
    "Letranat",
    "Mulfus",
    "Nylumer",
    "Otlevat",
    "Prax",
    "Retlixen",
    "Sajep",
    "Xetul",
)

STARTING_YEAR: Final[int] = 5775

# ---------------------------------------------------------------------------
# Stagioni — 4 stagioni da 108 giorni
# ---------------------------------------------------------------------------
#
# Convenzione day-of-year (1-based):
#   day_of_year = (month_1based - 1) * DAYS_PER_MONTH + day_1based
#
# L'inverno inizia il 16° giorno del 18° mese:
#   (18 - 1) * 24 + 16 = 424

SEASONS_PER_YEAR: Final[int] = 4
SEASON_LENGTH_DAYS: Final[int] = 108
WINTER_START_DAY_OF_YEAR: Final[int] = 17 * DAYS_PER_MONTH + 16  # = 424

SEASONS: Final[tuple[str, ...]] = (
    "Inverno",
    "Primavera",
    "Estate",
    "Autunno",
)

SEASON_START_DAY_OF_YEAR: Final[dict[str, int]] = {
    "Inverno": WINTER_START_DAY_OF_YEAR,  # 424
    "Primavera": 100,
    "Estate": 208,
    "Autunno": 316,
}

# ---------------------------------------------------------------------------
# Fasi giornaliere (DayPhase) — 7 fasi su 28 ore
# ---------------------------------------------------------------------------
# Range in ore intere [start, end) — l'ora 28 non esiste (0..27).
DAY_PHASE_BOUNDARIES: Final[dict[str, tuple[int, int]]] = {
    "DEEP_NIGHT": (0, 4),  # 00:00 - 03:59  (4h)
    "DAWN": (4, 7),  # 04:00 - 06:59  (3h)
    "MORNING": (7, 12),  # 07:00 - 11:59  (5h)
    "NOON": (12, 14),  # 12:00 - 13:59  (2h)
    "AFTERNOON": (14, 19),  # 14:00 - 18:59  (5h)
    "EVENING": (19, 23),  # 19:00 - 22:59  (4h)
    "NIGHT": (23, 28),  # 23:00 - 27:59  (5h)
}

# ---------------------------------------------------------------------------
# Unità temporali derivate
# ---------------------------------------------------------------------------

SECONDS_PER_HOUR: Final[int] = MINUTES_PER_HOUR * SECONDS_PER_MINUTE  # 3600
SECONDS_PER_DAY: Final[int] = HOURS_PER_DAY * SECONDS_PER_HOUR  # 100800
SECONDS_PER_YEAR: Final[int] = DAYS_PER_YEAR * SECONDS_PER_DAY  # 43545600

# ---------------------------------------------------------------------------
# Aspettativa di vita (anni Anthaliani)
# ---------------------------------------------------------------------------

LIFE_EXPECTANCY_MALE_MIN: Final[int] = 144
LIFE_EXPECTANCY_MALE_MAX: Final[int] = 156
LIFE_EXPECTANCY_FEMALE_MIN: Final[int] = 156
LIFE_EXPECTANCY_FEMALE_MAX: Final[int] = 168

# ---------------------------------------------------------------------------
# Fasce pediatriche (anni Anthalys -> soglie in secondi dall'anno 1)
# ---------------------------------------------------------------------------
#
# Interpretazione [min, max): "3-5 anni" = [3, 6).
# Le chiavi sono i valori dell'enum `LifeStagePediatric`.

LIFESTAGE_PEDIATRIC_THRESHOLDS: Final[dict[str, int]] = {
    "NEONATAL": 0,
    "INFANT": 28 * SECONDS_PER_DAY,
    "EARLY_CHILDHOOD": 1 * SECONDS_PER_YEAR,
    "MIDDLE_CHILDHOOD": 2 * SECONDS_PER_YEAR,
    "LATE_CHILDHOOD": 6 * SECONDS_PER_YEAR,
    "PUBERTY_ADOLESCENCE": 10 * SECONDS_PER_YEAR,
}

# ---------------------------------------------------------------------------
# Fasce psicosociali
# ---------------------------------------------------------------------------

LIFESTAGE_PSYCHOSOCIAL_THRESHOLDS: Final[dict[str, int]] = {
    "PRENATAL": 0,
    "EARLY_INFANCY": 2 * SECONDS_PER_YEAR,
    "INFANCY": 3 * SECONDS_PER_YEAR,
    "MIDDLE_INFANCY": 6 * SECONDS_PER_YEAR,
    "ADOLESCENCE": 12 * SECONDS_PER_YEAR,
    "YOUTH": 18 * SECONDS_PER_YEAR,
    "ADULTHOOD": 25 * SECONDS_PER_YEAR,
    "OLD_AGE": 60 * SECONDS_PER_YEAR,
}
