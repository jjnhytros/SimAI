"""Enum e costanti del dominio ledger double-entry.

Il ledger è la **sorgente di verità** contabile di SimAI: ogni movimento
di Athel è registrato come `JournalEntry` con almeno due `Posting`
(dare/avere) che bilanciano a zero.

Convenzioni:
  - `signed_amount(kind, direction, amount)` è **flow-based**: il segno
    dipende solo dalla direzione (DEBIT +, CREDIT -), non dal `kind`.
    Questo garantisce l'invariante `Σ signed_amount == 0` su un ledger
    ben formato.
  - `natural_balance(kind, direction, amount)` è **account-based**: il
    segno riflette se il posting aumenta il valore naturale del conto
    secondo il suo `kind`. Utile per display contabile.
  - `is_debit_increase(kind)` dice se DEBIT aumenta il valore naturale
    del conto per il `kind` dato.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class AccountKind(StrEnum):
    """Tipo di conto secondo la partita doppia."""

    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class PostingDirection(StrEnum):
    """Direzione di una riga di registrazione."""

    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class AccountOwnerType(StrEnum):
    """Chi possiede il conto (per query aggregate)."""

    CHARACTER = "CHARACTER"
    CITY = "CITY"
    BANK = "BANK"
    COMPANY = "COMPANY"
    SYSTEM = "SYSTEM"


class JournalEntryKind(StrEnum):
    """Natura di una registrazione.

    I primi valori sono allineati a `TransactionKind` esistente
    (retro-compatibilità per la dashboard). Gli altri coprono le
    operazioni introdotte in FASE 5.
    """

    # --- Generiche ---
    MINT = "MINT"  # creazione di moneta (contropartita: system:mint)
    SINK = "SINK"  # distruzione di moneta (contropartita: system:consumption)
    TRANSFER = "TRANSFER"  # trasferimento tra due conti dello stesso tipo
    ADJUSTMENT = "ADJUSTMENT"  # rettifica manuale (dev tool)

    # --- Operazioni di mercato ---
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    SALARY = "SALARY"
    GIFT = "GIFT"
    TAX = "TAX"
    MORTGAGE_PAYMENT = "MORTGAGE_PAYMENT"
    MORTGAGE_DISBURSEMENT = "MORTGAGE_DISBURSEMENT"
    PROPERTY_TAX = "PROPERTY_TAX"
    FORECLOSURE = "FORECLOSURE"

    # --- FASE 5 (banche, prestiti, investimenti, AION) ---
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    LOAN_PAYMENT = "LOAN_PAYMENT"
    INTEREST_ACCRUAL = "INTEREST_ACCRUAL"
    DIVIDEND = "DIVIDEND"
    STOCK_BUY = "STOCK_BUY"
    STOCK_SELL = "STOCK_SELL"
    AION_FEE = "AION_FEE"
    CARGO_FEE = "CARGO_FEE"


# ---------------------------------------------------------------------------
# Codici riservati dei conti di sistema
# ---------------------------------------------------------------------------

#: Conto di equity che rappresenta la moneta "creata dal nulla".
#: Contropartita di ogni MINT (stipendi, eredità, ecc.).
SYSTEM_ACCOUNT_MINT: Final[str] = "system:mint"

#: Conto di expense che rappresenta la moneta "distrutta" (consumo, tasse, ecc.).
SYSTEM_ACCOUNT_CONSUMPTION: Final[str] = "system:consumption"

#: Pattern del conto di cassa (ASSET) di un Character.
CHARACTER_ACCOUNT_CODE_PATTERN: Final[str] = "char:{character_id}:athel"


def character_account_code(character_id: int) -> str:
    """Codice canonico del conto `athel` di un Character."""
    if character_id <= 0:
        raise ValueError(f"character_id deve essere > 0, ricevuto {character_id}")
    return CHARACTER_ACCOUNT_CODE_PATTERN.format(character_id=character_id)


def is_debit_increase(kind: AccountKind) -> bool:
    """``True`` se DEBIT aumenta il valore del conto per il `kind` dato."""
    return kind in (AccountKind.ASSET, AccountKind.EXPENSE)


def signed_amount(
    kind: AccountKind,
    direction: PostingDirection,
    amount: int,
) -> int:
    """Ritorna `+amount` per DEBIT, `-amount` per CREDIT.

    Convenzione **flow-based**: il segno dipende solo dalla direzione,
    non dal `kind` del conto. Questo garantisce che per ogni entry
    bilanciata valga:

        Σ posting sulla entry di signed_amount == 0

    e di conseguenza `Σ over all postings == 0` su un ledger ben formato
    (vedi `LedgerService.total_balance_check`).

    Semantica per tipo di conto (in lettura):
      - ASSET, EXPENSE: il saldo positivo significa "il conto ha valore"
      - LIABILITY, EQUITY, REVENUE: il saldo positivo in partita doppia
        significa "il conto ha un saldo creditorio" (cioè aumenta quando
        si registra un CREDIT). Nel nostro ledger il segno è **flippato**:
        un EQUITY con `signed_balance == -100` indica che il sistema ha
        emesso 100 Athel. Usa `natural_balance` se vuoi il segno contabile.

    Solleva `ValueError` se `amount <= 0`.
    """
    if amount <= 0:
        raise ValueError(f"amount deve essere > 0, ricevuto {amount}")
    return amount if direction is PostingDirection.DEBIT else -amount


def natural_balance(
    kind: AccountKind,
    direction: PostingDirection,
    amount: int,
) -> int:
    """Ritorna `+amount` se il posting aumenta il valore **naturale** del conto.

    Utile per display contabile (es. una passività positiva se aumenta).
    Non usato per l'invariante di quadratura (che usa `signed_amount`).

    Convenzione:
      - ASSET, EXPENSE      → DEBIT aumenta, CREDIT diminuisce
      - LIABILITY, EQUITY, REVENUE → CREDIT aumenta, DEBIT diminuisce
    """
    if amount <= 0:
        raise ValueError(f"amount deve essere > 0, ricevuto {amount}")
    increases = (direction is PostingDirection.DEBIT) == is_debit_increase(kind)
    return amount if increases else -amount


__all__ = [
    "CHARACTER_ACCOUNT_CODE_PATTERN",
    "SYSTEM_ACCOUNT_CONSUMPTION",
    "SYSTEM_ACCOUNT_MINT",
    "AccountKind",
    "AccountOwnerType",
    "JournalEntryKind",
    "PostingDirection",
    "character_account_code",
    "is_debit_increase",
    "natural_balance",
    "signed_amount",
]
