"""Package `simai.economy.companies` — aziende NPC.

Range migrazione: dentro `6000_XX` (Economy esteso).

Contenuto:
  - `Company`, `CompanyEmployee`, `CompanyTransaction` — modelli
  - `CompanyService` — API unificata (costituzione, dipendenti, movimenti, tick)
  - `CompanyError`, `SalaryReport`, `DailyTickReport`,
    `CompanyReconcileResult` — dataclass ed errori
"""

from simai.economy.companies.enums import (
    DEFAULT_DAILY_COST,
    DEFAULT_DAILY_REVENUE,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_ROLE_WAGE,
    DIVIDEND_SHARE,
    DIVIDEND_THRESHOLD,
    MIN_RESERVE_FOR_HIRING,
    CompanyKind,
    CompanyStatus,
    CompanyTransactionKind,
    EmployeeRole,
    company_athel_code,
    company_equity_code,
)
from simai.economy.companies.models import (
    Company,
    CompanyEmployee,
    CompanyTransaction,
)
from simai.economy.companies.seed import CompanySeedResult, seed_demo_companies
from simai.economy.companies.service import (
    CompanyError,
    CompanyReconcileResult,
    CompanyService,
    DailyTickReport,
    SalaryReport,
)

__all__ = [
    "DEFAULT_DAILY_COST",
    "DEFAULT_DAILY_REVENUE",
    "DEFAULT_INITIAL_CAPITAL",
    "DEFAULT_ROLE_WAGE",
    "DIVIDEND_SHARE",
    "DIVIDEND_THRESHOLD",
    "MIN_RESERVE_FOR_HIRING",
    "Company",
    "CompanyEmployee",
    "CompanyError",
    "CompanyKind",
    "CompanyReconcileResult",
    "CompanySeedResult",
    "CompanyService",
    "CompanyStatus",
    "CompanyTransaction",
    "CompanyTransactionKind",
    "DailyTickReport",
    "EmployeeRole",
    "SalaryReport",
    "company_athel_code",
    "company_equity_code",
    "seed_demo_companies",
]
