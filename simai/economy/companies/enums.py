"""Enum e costanti del dominio companies (aziende NPC)."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class CompanyKind(StrEnum):
    """Settore merceologico dell'azienda."""

    SHOP = "SHOP"  # negozio al dettaglio
    WORKSHOP = "WORKSHOP"  # bottega artigiana
    FARM = "FARM"  # azienda agricola
    SERVICE = "SERVICE"  # servizi (studio, ufficio)
    MANUFACTURE = "MANUFACTURE"  # manifattura
    TAVERN = "TAVERN"  # locanda / ristorazione


class CompanyStatus(StrEnum):
    """Stato operativo."""

    ACTIVE = "ACTIVE"
    BANKRUPT = "BANKRUPT"
    DISSOLVED = "DISSOLVED"


class EmployeeRole(StrEnum):
    """Ruolo del dipendente."""

    OWNER = "OWNER"
    MANAGER = "MANAGER"
    WORKER = "WORKER"
    APPRENTICE = "APPRENTICE"


class CompanyTransactionKind(StrEnum):
    """Tipi di transazione aziendale (audit locale)."""

    CAPITAL = "CAPITAL"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"
    SALARY = "SALARY"
    DIVIDEND = "DIVIDEND"
    TAX = "TAX"
    DISSOLUTION = "DISSOLUTION"


# --- Parametri di default ---------------------------------------------------

#: Capitale iniziale iniettato alla costituzione.
DEFAULT_INITIAL_CAPITAL: Final[int] = 5_000

#: Fatturato giornaliero di default per settore (Athel).
DEFAULT_DAILY_REVENUE: Final[dict[CompanyKind, int]] = {
    CompanyKind.SHOP: 120,
    CompanyKind.WORKSHOP: 80,
    CompanyKind.FARM: 60,
    CompanyKind.SERVICE: 100,
    CompanyKind.MANUFACTURE: 150,
    CompanyKind.TAVERN: 90,
}

#: Costi operativi giornalieri di default per settore (Athel).
#: Esclude gli stipendi (pagati separatamente).
DEFAULT_DAILY_COST: Final[dict[CompanyKind, int]] = {
    CompanyKind.SHOP: 40,
    CompanyKind.WORKSHOP: 30,
    CompanyKind.FARM: 20,
    CompanyKind.SERVICE: 35,
    CompanyKind.MANUFACTURE: 60,
    CompanyKind.TAVERN: 30,
}

#: Stipendio giornaliero di default per ruolo (Athel).
DEFAULT_ROLE_WAGE: Final[dict[EmployeeRole, int]] = {
    EmployeeRole.OWNER: 0,  # owner non percepisce stipendio fisso
    EmployeeRole.MANAGER: 20,
    EmployeeRole.WORKER: 12,
    EmployeeRole.APPRENTICE: 6,
}

#: Soglia di riserva minima: sotto questo saldo l'azienda non assume.
MIN_RESERVE_FOR_HIRING: Final[int] = 500

#: Soglia di saldo sotto cui l'azienda paga dividendi (profitto trattenuto).
DIVIDEND_THRESHOLD: Final[int] = 10_000

#: Percentuale di saldo distribuita come dividendo quando si supera la soglia.
DIVIDEND_SHARE: Final[float] = 0.50


# --- Codici ledger ----------------------------------------------------------


def company_athel_code(company_id: int) -> str:
    """Conto ASSET principale di un'azienda."""
    if company_id <= 0:
        raise ValueError(f"company_id deve essere > 0, ricevuto {company_id}")
    return f"company:{company_id}:athel"


def company_equity_code(company_id: int) -> str:
    """Conto EQUITY dell'azienda verso il suo owner."""
    if company_id <= 0:
        raise ValueError(f"company_id deve essere > 0, ricevuto {company_id}")
    return f"company:{company_id}:equity"


__all__ = [
    "DEFAULT_DAILY_COST",
    "DEFAULT_DAILY_REVENUE",
    "DEFAULT_INITIAL_CAPITAL",
    "DEFAULT_ROLE_WAGE",
    "DIVIDEND_SHARE",
    "DIVIDEND_THRESHOLD",
    "MIN_RESERVE_FOR_HIRING",
    "CompanyKind",
    "CompanyStatus",
    "CompanyTransactionKind",
    "EmployeeRole",
    "company_athel_code",
    "company_equity_code",
]
