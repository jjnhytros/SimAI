"""Enum e costanti del dominio housing AI."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class HousingAction(StrEnum):
    """Azione immobiliare intrapresa."""

    BOUGHT_HOME_CASH = "BOUGHT_HOME_CASH"
    BOUGHT_HOME_MORTGAGE = "BOUGHT_HOME_MORTGAGE"
    BOUGHT_SHOP_CASH = "BOUGHT_SHOP_CASH"
    BOUGHT_SHOP_MORTGAGE = "BOUGHT_SHOP_MORTGAGE"
    SOLD_LOT = "SOLD_LOT"
    NO_ACTION = "NO_ACTION"


#: Età minima per comprare un immobile.
MIN_AGE_BUY: Final[int] = 18

#: Età minima per comprare senza co-firmatario.
MIN_AGE_INDEPENDENT: Final[int] = 20

#: Età oltre cui si tende a vendere (pensione).
SENIOR_AGE: Final[int] = 65

#: Riserva minima di liquidità dopo l'acquisto.
MIN_RESERVE: Final[int] = 200

#: Soglia di "povertà" sotto cui si considera vendere.
BROKE_THRESHOLD: Final[int] = 100

#: Down payment minimo (frazione del prezzo) per mutuo.
MIN_DOWN_PAYMENT_RATIO: Final[float] = 0.15

#: Down payment preferito (frazione del prezzo).
PREFERRED_DOWN_PAYMENT_RATIO: Final[float] = 0.20

#: Probabilità giornaliera di considerare acquisto casa.
BUY_HOME_PROBABILITY: Final[float] = 0.03

#: Probabilità giornaliera di considerare acquisto negozio.
BUY_SHOP_PROBABILITY: Final[float] = 0.01

#: Probabilità giornaliera di considerare vendita (se broke).
SELL_PROBABILITY: Final[float] = 0.10

#: Età minima per comprare un negozio.
MIN_AGE_BUY_SHOP: Final[int] = 22

#: Skill minima per comprare un negozio.
MIN_SKILL_FOR_SHOP: Final[int] = 5

#: Cap di acquisti al giorno (globale).
MAX_PURCHASES_PER_DAY: Final[int] = 2


__all__ = [
    "BROKE_THRESHOLD",
    "BUY_HOME_PROBABILITY",
    "BUY_SHOP_PROBABILITY",
    "MAX_PURCHASES_PER_DAY",
    "MIN_AGE_BUY",
    "MIN_AGE_BUY_SHOP",
    "MIN_AGE_INDEPENDENT",
    "MIN_DOWN_PAYMENT_RATIO",
    "MIN_RESERVE",
    "MIN_SKILL_FOR_SHOP",
    "PREFERRED_DOWN_PAYMENT_RATIO",
    "SELL_PROBABILITY",
    "SENIOR_AGE",
    "HousingAction",
]
