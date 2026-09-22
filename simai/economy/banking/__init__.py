"""Package `simai.economy.banking` — banche commerciali, conti, prestiti.

Range migrazione: dentro `6000_XX` (Economy esteso).

Contenuto:
  - `Bank`, `BankAccount`, `Loan`, `LoanPayment`, `InterestAccrual` — modelli
  - `BankService` — API unificata (conti, depositi, prestiti, tick, reconcile)
  - `BankingError`, `LoanPaymentOutcome`, `MonthlyTickReport`,
    `BankReconcileResult` — dataclass ed errori
"""

from simai.economy.banking.enums import (
    DEFAULT_DEPOSIT_INTEREST_RATE,
    DEFAULT_LOAN_INTEREST_RATE,
    DEFAULT_LOAN_TERM_MONTHS,
    DEFAULT_RESERVE_RATIO,
    MAX_LOAN_MISSED_PAYMENTS,
    MAX_LOAN_PRINCIPAL,
    MIN_LOAN_PRINCIPAL,
    PRIMARY_BANK_CODE,
    PRIMARY_BANK_NAME,
    BankAccountKind,
    BankKind,
    LoanStatus,
    bank_deposits_code,
    bank_interest_revenue_code,
    bank_loans_code,
    bank_reserve_code,
    character_bank_account_code,
)
from simai.economy.banking.models import (
    Bank,
    BankAccount,
    InterestAccrual,
    Loan,
    LoanPayment,
)
from simai.economy.banking.service import (
    PRIMARY_BANK_INITIAL_CAPITAL,
    BankingError,
    BankReconcileResult,
    BankService,
    LoanPaymentOutcome,
    MonthlyTickReport,
)

__all__ = [
    "DEFAULT_DEPOSIT_INTEREST_RATE",
    "DEFAULT_LOAN_INTEREST_RATE",
    "DEFAULT_LOAN_TERM_MONTHS",
    "DEFAULT_RESERVE_RATIO",
    "MAX_LOAN_MISSED_PAYMENTS",
    "MAX_LOAN_PRINCIPAL",
    "MIN_LOAN_PRINCIPAL",
    "PRIMARY_BANK_CODE",
    "PRIMARY_BANK_INITIAL_CAPITAL",
    "PRIMARY_BANK_NAME",
    "Bank",
    "BankAccount",
    "BankAccountKind",
    "BankKind",
    "BankReconcileResult",
    "BankService",
    "BankingError",
    "InterestAccrual",
    "Loan",
    "LoanPayment",
    "LoanPaymentOutcome",
    "LoanStatus",
    "MonthlyTickReport",
    "bank_deposits_code",
    "bank_interest_revenue_code",
    "bank_loans_code",
    "bank_reserve_code",
    "character_bank_account_code",
]
