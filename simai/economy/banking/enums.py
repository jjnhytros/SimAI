"""Enum e costanti del dominio banking."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class BankKind(StrEnum):
    """Tipo di banca."""

    COMMERCIAL = "COMMERCIAL"
    COOPERATIVE = "COOPERATIVE"
    CENTRAL = "CENTRAL"  # riservato per evoluzioni future


class BankAccountKind(StrEnum):
    """Tipo di conto bancario."""

    CHECKING = "CHECKING"  # conto corrente
    SAVINGS = "SAVINGS"  # conto deposito


class LoanStatus(StrEnum):
    """Stato di un prestito."""

    ACTIVE = "ACTIVE"
    PAID_OFF = "PAID_OFF"
    DEFAULTED = "DEFAULTED"  # 3+ rate mancate
    WRITTEN_OFF = "WRITTEN_OFF"  # stralciato (irrecuperabile)


# --- Parametri di default ---------------------------------------------------

#: Riserva frazionaria minima (10%).
DEFAULT_RESERVE_RATIO: Final[float] = 0.10

#: Tasso di interesse annuale sui depositi (2%).
DEFAULT_DEPOSIT_INTEREST_RATE: Final[float] = 0.02

#: Tasso di interesse annuale sui prestiti (8%).
DEFAULT_LOAN_INTEREST_RATE: Final[float] = 0.08

#: Durata di default di un prestito (24 mesi Anthalys).
DEFAULT_LOAN_TERM_MONTHS: Final[int] = 24

#: Numero massimo di rate mancate prima del default.
MAX_LOAN_MISSED_PAYMENTS: Final[int] = 3

#: Capitale minimo/massimo erogabile in un prestito.
MIN_LOAN_PRINCIPAL: Final[int] = 100
MAX_LOAN_PRINCIPAL: Final[int] = 100_000

#: Codice della banca primaria creata di default.
PRIMARY_BANK_CODE: Final[str] = "anthal_primary"
PRIMARY_BANK_NAME: Final[str] = "Banca di Anthal"

#: Codici dei conti ledger per una banca (formattati con `bank_code`).
BANK_LEDGER_RESERVE: Final[str] = "bank:{code}:reserve"
BANK_LEDGER_DEPOSITS: Final[str] = "bank:{code}:deposits"
BANK_LEDGER_LOANS: Final[str] = "bank:{code}:loans"
BANK_LEDGER_INTEREST_REVENUE: Final[str] = "bank:{code}:interest_revenue"


def bank_reserve_code(bank_code: str) -> str:
    return BANK_LEDGER_RESERVE.format(code=bank_code)


def bank_deposits_code(bank_code: str) -> str:
    return BANK_LEDGER_DEPOSITS.format(code=bank_code)


def bank_loans_code(bank_code: str) -> str:
    return BANK_LEDGER_LOANS.format(code=bank_code)


def bank_interest_revenue_code(bank_code: str) -> str:
    return BANK_LEDGER_INTEREST_REVENUE.format(code=bank_code)


def character_bank_account_code(character_id: int, bank_code: str) -> str:
    """Codice canonico del conto ASSET di un Character presso una banca."""
    if character_id <= 0:
        raise ValueError(f"character_id deve essere > 0, ricevuto {character_id}")
    if not bank_code:
        raise ValueError("bank_code non può essere vuoto")
    return f"char:{character_id}:bank:{bank_code}"


__all__ = [
    "BANK_LEDGER_DEPOSITS",
    "BANK_LEDGER_INTEREST_REVENUE",
    "BANK_LEDGER_LOANS",
    "BANK_LEDGER_RESERVE",
    "DEFAULT_DEPOSIT_INTEREST_RATE",
    "DEFAULT_LOAN_INTEREST_RATE",
    "DEFAULT_LOAN_TERM_MONTHS",
    "DEFAULT_RESERVE_RATIO",
    "MAX_LOAN_MISSED_PAYMENTS",
    "MAX_LOAN_PRINCIPAL",
    "MIN_LOAN_PRINCIPAL",
    "PRIMARY_BANK_CODE",
    "PRIMARY_BANK_NAME",
    "BankAccountKind",
    "BankKind",
    "LoanStatus",
    "bank_deposits_code",
    "bank_interest_revenue_code",
    "bank_loans_code",
    "bank_reserve_code",
    "character_bank_account_code",
]
