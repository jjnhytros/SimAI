"""Package `simai.economy.ledger` — partita doppia.

Range migrazioni: 5400–5419 (Economy/Ledger).

Contenuto:
  - `Account`, `JournalEntry`, `Posting` — modelli SQLAlchemy
  - `LedgerService` — API unificata (apertura conti, post, saldi, storico)
  - `PostingSpec` — input per `LedgerService.post`
  - Enum: `AccountKind`, `PostingDirection`, `AccountOwnerType`,
    `JournalEntryKind`
"""

from simai.economy.ledger.enums import (
    CHARACTER_ACCOUNT_CODE_PATTERN,
    SYSTEM_ACCOUNT_CONSUMPTION,
    SYSTEM_ACCOUNT_MINT,
    AccountKind,
    AccountOwnerType,
    JournalEntryKind,
    PostingDirection,
    character_account_code,
    is_debit_increase,
    natural_balance,
    signed_amount,
)
from simai.economy.ledger.models import Account, JournalEntry, Posting
from simai.economy.ledger.service import (
    LedgerError,
    LedgerService,
    PostingSpec,
)

__all__ = [
    "CHARACTER_ACCOUNT_CODE_PATTERN",
    "SYSTEM_ACCOUNT_CONSUMPTION",
    "SYSTEM_ACCOUNT_MINT",
    "Account",
    "AccountKind",
    "AccountOwnerType",
    "JournalEntry",
    "JournalEntryKind",
    "LedgerError",
    "LedgerService",
    "Posting",
    "PostingDirection",
    "PostingSpec",
    "character_account_code",
    "is_debit_increase",
    "natural_balance",
    "signed_amount",
]
