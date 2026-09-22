"""CompanyService — gestione aziende, dipendenti, movimenti, tick giornaliero.

Ogni operazione posta una `JournalEntry` sul ledger double-entry
(`simai.economy.ledger`). Il campo `Company.athel_balance` è una cache
materializzata, riconciliabile via `CompanyService.reconcile`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.companies.enums import (
    DEFAULT_DAILY_COST,
    DEFAULT_DAILY_REVENUE,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_ROLE_WAGE,
    DIVIDEND_SHARE,
    DIVIDEND_THRESHOLD,
    CompanyKind,
    CompanyStatus,
    CompanyTransactionKind,
    EmployeeRole,
    company_athel_code,
)
from simai.economy.companies.models import (
    Company,
    CompanyEmployee,
    CompanyTransaction,
)
from simai.economy.ledger import (
    Account,
    AccountKind,
    AccountOwnerType,
    JournalEntryKind,
    LedgerService,
    PostingDirection,
    PostingSpec,
)
from simai.npc.models import Character


class CompanyError(Exception):
    """Errore di validazione o invariante sul dominio companies."""


# ---------------------------------------------------------------------------
# Dataclass di esito
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class SalaryReport:
    """Esito del pagamento stipendi di un'azienda."""

    company_id: int
    paid: int = 0
    failed: int = 0
    total_paid: int = 0
    character_ids: list[int] = field(default_factory=list)


@dataclass(slots=True)
class DailyTickReport:
    """Esito del tick giornaliero di un'azienda."""

    company_id: int
    revenue_earned: int = 0
    operating_cost_paid: int = 0
    salaries_paid: int = 0
    total_salaries: int = 0
    salaries_failed: int = 0
    dividend_paid: int = 0
    declared_bankrupt: bool = False


@dataclass(frozen=True, slots=True)
class CompanyReconcileResult:
    """Esito della riconciliazione cache ↔ ledger."""

    company_id: int
    cache_balance: int
    ledger_balance: int
    ok: bool


# ---------------------------------------------------------------------------
# CompanyService
# ---------------------------------------------------------------------------


class CompanyService:
    """Servizio stateless di gestione aziende."""

    # ------------------------------------------------------------------
    # Conti ledger
    # ------------------------------------------------------------------

    @staticmethod
    def _athel_account(session: Session, company: Company) -> Account:
        return LedgerService.get_or_create_account(
            session,
            code=company_athel_code(company.id),
            kind=AccountKind.ASSET,
            owner_type=AccountOwnerType.COMPANY,
            owner_id=company.id,
            name=f"Cassa di {company.name}",
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get(session: Session, company_id: int) -> Company | None:
        return session.get(Company, company_id)

    @staticmethod
    def all_companies(session: Session, *, only_active: bool = True) -> list[Company]:
        stmt = select(Company)
        if only_active:
            stmt = stmt.where(Company.is_active.is_(True))
        return list(session.scalars(stmt.order_by(Company.id)))

    @staticmethod
    def companies_of_owner(session: Session, owner_character_id: int) -> list[Company]:
        return list(
            session.scalars(
                select(Company)
                .where(Company.owner_character_id == owner_character_id)
                .order_by(Company.id)
            )
        )

    @staticmethod
    def employees_of(
        session: Session, company_id: int, *, only_active: bool = True
    ) -> list[CompanyEmployee]:
        stmt = select(CompanyEmployee).where(CompanyEmployee.company_id == company_id)
        if only_active:
            stmt = stmt.where(CompanyEmployee.is_active.is_(True))
        return list(session.scalars(stmt.order_by(CompanyEmployee.id)))

    @staticmethod
    def transactions_of(
        session: Session, company_id: int, *, limit: int = 50
    ) -> list[CompanyTransaction]:
        return list(
            session.scalars(
                select(CompanyTransaction)
                .where(CompanyTransaction.company_id == company_id)
                .order_by(CompanyTransaction.at_total_seconds.desc())
                .limit(limit)
            )
        )

    # ------------------------------------------------------------------
    # Costituzione e scioglimento
    # ------------------------------------------------------------------

    @staticmethod
    def create(
        session: Session,
        *,
        owner: Character,
        name: str,
        kind: CompanyKind,
        location_id: int | None = None,
        initial_capital: int | None = None,
        current_dt: AnthalysDateTime,
    ) -> Company:
        """Costituisce un'azienda. L'owner è assunto automaticamente come OWNER.

        Posta una `JournalEntry MINT` da `system:mint` verso
        `company:<id>:athel` per il capitale iniziale.
        """
        if not owner.is_alive:
            raise CompanyError(f"Character {owner.id} non è vivo")
        if not name:
            raise CompanyError("name non può essere vuoto")

        capital = initial_capital if initial_capital is not None else DEFAULT_INITIAL_CAPITAL
        if capital <= 0:
            raise CompanyError(f"initial_capital deve essere > 0, ricevuto {capital}")

        revenue = DEFAULT_DAILY_REVENUE.get(kind, 100)
        cost = DEFAULT_DAILY_COST.get(kind, 30)

        company = Company(
            name=name,
            kind=kind.value,
            owner_character_id=owner.id,
            location_id=location_id,
            athel_balance=capital,
            base_daily_revenue=revenue,
            base_daily_cost=cost,
            status=CompanyStatus.ACTIVE.value,
            is_active=True,
            founded_at_total_seconds=current_dt.to_total_seconds(),
            metadata_json={},
        )
        session.add(company)
        session.flush()

        # Conto ledger + capitalizzazione (MINT)
        company_acc = CompanyService._athel_account(session, company)
        mint = LedgerService.system_mint_account(session)
        LedgerService.post(
            session,
            kind=JournalEntryKind.MINT,
            description=f"Costituzione di {name} ({capital} Athel)",
            postings=[
                PostingSpec(
                    account=company_acc,
                    direction=PostingDirection.DEBIT,
                    amount=capital,
                ),
                PostingSpec(
                    account=mint,
                    direction=PostingDirection.CREDIT,
                    amount=capital,
                ),
            ],
            current_dt=current_dt,
            reference_type="company",
            reference_id=company.id,
            metadata={"kind": kind.value, "initial_capital": capital},
        )

        # Audit
        session.add(
            CompanyTransaction(
                company_id=company.id,
                kind=CompanyTransactionKind.CAPITAL.value,
                amount=capital,
                character_id=owner.id,
                at_total_seconds=current_dt.to_total_seconds(),
                description=f"Capitale iniziale da {owner.full_name}",
                metadata_json={},
            )
        )

        # Owner come dipendente
        owner_emp = CompanyEmployee(
            company_id=company.id,
            character_id=owner.id,
            role=EmployeeRole.OWNER.value,
            daily_wage=DEFAULT_ROLE_WAGE[EmployeeRole.OWNER],
            hired_at_total_seconds=current_dt.to_total_seconds(),
            is_active=True,
            metadata_json={},
        )
        session.add(owner_emp)
        session.flush()

        logger.info(
            "Company creata: id={} name={!r} kind={} capital={} owner={}",
            company.id,
            name,
            kind.value,
            capital,
            owner.id,
        )
        return company

    @staticmethod
    def dissolve(
        session: Session,
        *,
        company: Company,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Scioglie l'azienda: paga i dipendenti in sospeso, chiude conti.

        - Le rimanenze di cassa sono **restituite all'owner** come dividendo.
        - I dipendenti vengono licenziati.
        - `status = DISSOLVED`, `is_active = False`.
        """
        if company.status == CompanyStatus.DISSOLVED.value:
            return

        # Paga eventuale residuo all'owner (dividendo finale)
        residual = int(company.athel_balance)
        if residual > 0:
            owner = session.get(Character, company.owner_character_id)
            if owner is not None:
                CompanyService.pay_dividend(
                    session,
                    company=company,
                    amount=residual,
                    current_dt=current_dt,
                )

        # Licenzia tutti i dipendenti
        employees = CompanyService.employees_of(session, company.id, only_active=True)
        for emp in employees:
            emp.is_active = False

        company.status = CompanyStatus.DISSOLVED.value
        company.is_active = False
        session.flush()

        session.add(
            CompanyTransaction(
                company_id=company.id,
                kind=CompanyTransactionKind.DISSOLUTION.value,
                amount=-residual if residual > 0 else 0,
                character_id=company.owner_character_id,
                at_total_seconds=current_dt.to_total_seconds(),
                description="Scioglimento",
                metadata_json={"residual_to_owner": residual},
            )
        )
        session.flush()
        logger.info(
            "Company dissolta: id={} name={!r} residual={}",
            company.id,
            company.name,
            residual,
        )

    # ------------------------------------------------------------------
    # Dipendenti
    # ------------------------------------------------------------------

    @staticmethod
    def hire(
        session: Session,
        *,
        company: Company,
        employee: Character,
        role: EmployeeRole = EmployeeRole.WORKER,
        daily_wage: int | None = None,
        current_dt: AnthalysDateTime,
    ) -> CompanyEmployee:
        """Assume un dipendente. Solleva se già attivo o se l'azienda non è attiva."""
        if company.status != CompanyStatus.ACTIVE.value:
            raise CompanyError(f"Azienda {company.id} non attiva (status={company.status})")
        if not employee.is_alive:
            raise CompanyError(f"Character {employee.id} non è vivo")

        existing = session.scalars(
            select(CompanyEmployee).where(
                CompanyEmployee.company_id == company.id,
                CompanyEmployee.character_id == employee.id,
                CompanyEmployee.is_active.is_(True),
            )
        ).first()
        if existing is not None:
            raise CompanyError(f"Character {employee.id} è già assunto in azienda {company.id}")

        wage = daily_wage if daily_wage is not None else DEFAULT_ROLE_WAGE.get(role, 12)
        if wage < 0:
            raise CompanyError(f"daily_wage deve essere >= 0, ricevuto {wage}")

        emp = CompanyEmployee(
            company_id=company.id,
            character_id=employee.id,
            role=role.value,
            daily_wage=wage,
            hired_at_total_seconds=current_dt.to_total_seconds(),
            is_active=True,
            metadata_json={},
        )
        session.add(emp)
        session.flush()
        logger.info(
            "Company hire: company={} char={} role={} wage={}",
            company.id,
            employee.id,
            role.value,
            wage,
        )
        return emp

    @staticmethod
    def fire(
        session: Session,
        *,
        company: Company,
        employee: Character,
        current_dt: AnthalysDateTime,
    ) -> bool:
        """Licenzia un dipendente attivo. Ritorna `True` se c'era."""
        emp = session.scalars(
            select(CompanyEmployee).where(
                CompanyEmployee.company_id == company.id,
                CompanyEmployee.character_id == employee.id,
                CompanyEmployee.is_active.is_(True),
            )
        ).first()
        if emp is None:
            return False
        emp.is_active = False
        session.flush()
        logger.info(
            "Company fire: company={} char={} role={}",
            company.id,
            employee.id,
            emp.role,
        )
        return True

    # ------------------------------------------------------------------
    # Movimenti
    # ------------------------------------------------------------------

    @staticmethod
    def record_revenue(
        session: Session,
        *,
        company: Company,
        amount: int,
        current_dt: AnthalysDateTime,
        description: str = "",
    ) -> None:
        """Ricavo: DEBIT company, CREDIT system:mint."""
        if amount <= 0:
            raise CompanyError(f"amount deve essere > 0, ricevuto {amount}")

        company_acc = CompanyService._athel_account(session, company)
        mint = LedgerService.system_mint_account(session)
        LedgerService.post(
            session,
            kind=JournalEntryKind.SALE,
            description=description or f"Ricavo di {company.name}",
            postings=[
                PostingSpec(
                    account=company_acc,
                    direction=PostingDirection.DEBIT,
                    amount=amount,
                ),
                PostingSpec(
                    account=mint,
                    direction=PostingDirection.CREDIT,
                    amount=amount,
                ),
            ],
            current_dt=current_dt,
            reference_type="company",
            reference_id=company.id,
        )
        company.athel_balance = int(company.athel_balance) + amount
        session.add(
            CompanyTransaction(
                company_id=company.id,
                kind=CompanyTransactionKind.REVENUE.value,
                amount=amount,
                character_id=None,
                at_total_seconds=current_dt.to_total_seconds(),
                description=description or "Ricavo",
                metadata_json={},
            )
        )
        session.flush()

    @staticmethod
    def record_expense(
        session: Session,
        *,
        company: Company,
        amount: int,
        current_dt: AnthalysDateTime,
        description: str = "",
    ) -> None:
        """Spesa: DEBIT system:consumption, CREDIT company. Richiede fondi."""
        if amount <= 0:
            raise CompanyError(f"amount deve essere > 0, ricevuto {amount}")
        if int(company.athel_balance) < amount:
            raise CompanyError(f"Fondi insufficienti: {company.athel_balance} < {amount}")

        company_acc = CompanyService._athel_account(session, company)
        sink = LedgerService.system_consumption_account(session)
        LedgerService.post(
            session,
            kind=JournalEntryKind.PURCHASE,
            description=description or f"Spesa di {company.name}",
            postings=[
                PostingSpec(
                    account=sink,
                    direction=PostingDirection.DEBIT,
                    amount=amount,
                ),
                PostingSpec(
                    account=company_acc,
                    direction=PostingDirection.CREDIT,
                    amount=amount,
                ),
            ],
            current_dt=current_dt,
            reference_type="company",
            reference_id=company.id,
        )
        company.athel_balance = int(company.athel_balance) - amount
        session.add(
            CompanyTransaction(
                company_id=company.id,
                kind=CompanyTransactionKind.EXPENSE.value,
                amount=-amount,
                character_id=None,
                at_total_seconds=current_dt.to_total_seconds(),
                description=description or "Spesa",
                metadata_json={},
            )
        )
        session.flush()

    @staticmethod
    def pay_salaries(
        session: Session,
        *,
        company: Company,
        current_dt: AnthalysDateTime,
    ) -> SalaryReport:
        """Paga lo stipendio giornaliero a tutti i dipendenti attivi.

        Un dipendente il cui pagamento fallisce (fondi insufficienti) non
        blocca gli altri: viene semplicemente saltato e conteggiato in
        `report.failed`.
        """
        report = SalaryReport(company_id=company.id)
        employees = CompanyService.employees_of(session, company.id, only_active=True)

        for emp in employees:
            wage = int(emp.daily_wage)
            if wage <= 0:
                continue
            if int(company.athel_balance) < wage:
                report.failed += 1
                continue

            char = session.get(Character, emp.character_id)
            if char is None or not char.is_alive:
                continue

            char_acc = LedgerService.character_athel_account(
                session, char.id, character_name=char.full_name
            )
            company_acc = CompanyService._athel_account(session, company)
            LedgerService.post(
                session,
                kind=JournalEntryKind.SALARY,
                description=f"Stipendio a {char.full_name} da {company.name}",
                postings=[
                    PostingSpec(
                        account=char_acc,
                        direction=PostingDirection.DEBIT,
                        amount=wage,
                    ),
                    PostingSpec(
                        account=company_acc,
                        direction=PostingDirection.CREDIT,
                        amount=wage,
                    ),
                ],
                current_dt=current_dt,
                reference_type="company",
                reference_id=company.id,
                metadata={"employee_id": emp.id, "character_id": char.id},
            )
            company.athel_balance = int(company.athel_balance) - wage
            char.athel_balance = int(char.athel_balance) + wage

            session.add(
                CompanyTransaction(
                    company_id=company.id,
                    kind=CompanyTransactionKind.SALARY.value,
                    amount=-wage,
                    character_id=char.id,
                    at_total_seconds=current_dt.to_total_seconds(),
                    description=f"Stipendio a {char.full_name}",
                    metadata_json={"role": emp.role},
                )
            )
            report.paid += 1
            report.total_paid += wage
            report.character_ids.append(char.id)

        session.flush()
        return report

    @staticmethod
    def pay_dividend(
        session: Session,
        *,
        company: Company,
        amount: int,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Distribuisce un dividendo all'owner: DEBIT char, CREDIT company."""
        if amount <= 0:
            raise CompanyError(f"amount deve essere > 0, ricevuto {amount}")
        if int(company.athel_balance) < amount:
            raise CompanyError(f"Fondi insufficienti: {company.athel_balance} < {amount}")

        owner = session.get(Character, company.owner_character_id)
        if owner is None or not owner.is_alive:
            raise CompanyError(f"Owner {company.owner_character_id} non disponibile")

        char_acc = LedgerService.character_athel_account(
            session, owner.id, character_name=owner.full_name
        )
        company_acc = CompanyService._athel_account(session, company)
        LedgerService.post(
            session,
            kind=JournalEntryKind.DIVIDEND,
            description=f"Dividendo {amount} Athel da {company.name}",
            postings=[
                PostingSpec(
                    account=char_acc,
                    direction=PostingDirection.DEBIT,
                    amount=amount,
                ),
                PostingSpec(
                    account=company_acc,
                    direction=PostingDirection.CREDIT,
                    amount=amount,
                ),
            ],
            current_dt=current_dt,
            reference_type="company",
            reference_id=company.id,
            metadata={"owner_id": owner.id},
        )
        company.athel_balance = int(company.athel_balance) - amount
        owner.athel_balance = int(owner.athel_balance) + amount

        session.add(
            CompanyTransaction(
                company_id=company.id,
                kind=CompanyTransactionKind.DIVIDEND.value,
                amount=-amount,
                character_id=owner.id,
                at_total_seconds=current_dt.to_total_seconds(),
                description=f"Dividendo a {owner.full_name}",
                metadata_json={},
            )
        )
        session.flush()

    # ------------------------------------------------------------------
    # Tick giornaliero
    # ------------------------------------------------------------------

    @staticmethod
    def daily_tick(
        session: Session,
        *,
        company: Company,
        current_dt: AnthalysDateTime,
    ) -> DailyTickReport:
        """Esegue il tick giornaliero di un'azienda.

        Ordine:
          1. Ricavo giornaliero (accoda revenue se `base_daily_revenue > 0`).
          2. Costi operativi (salta se fondi insufficienti).
          3. Stipendi (salta dipendenti se fondi insufficienti).
          4. Eventuale dividendo se il saldo supera `DIVIDEND_THRESHOLD`.

        Non solleva mai: gli errori vengono catturati e loggati.
        """
        report = DailyTickReport(company_id=company.id)

        if company.status != CompanyStatus.ACTIVE.value:
            return report

        # 1. Revenue
        revenue = int(company.base_daily_revenue)
        if revenue > 0:
            CompanyService.record_revenue(
                session,
                company=company,
                amount=revenue,
                current_dt=current_dt,
                description="Ricavo giornaliero",
            )
            report.revenue_earned = revenue

        # 2. Costi operativi
        cost = int(company.base_daily_cost)
        if cost > 0:
            if int(company.athel_balance) >= cost:
                CompanyService.record_expense(
                    session,
                    company=company,
                    amount=cost,
                    current_dt=current_dt,
                    description="Costi operativi",
                )
                report.operating_cost_paid = cost
            else:
                logger.warning(
                    "Company {} non può pagare costi operativi ({} < {})",
                    company.id,
                    company.athel_balance,
                    cost,
                )

        # 3. Stipendi
        salary_report = CompanyService.pay_salaries(session, company=company, current_dt=current_dt)
        report.salaries_paid = salary_report.paid
        report.total_salaries = salary_report.total_paid
        report.salaries_failed = salary_report.failed

        # 4. Dividendo (se il saldo supera la soglia)
        balance = int(company.athel_balance)
        if balance > DIVIDEND_THRESHOLD:
            dividend = int(balance * DIVIDEND_SHARE)
            if dividend > 0:
                try:
                    CompanyService.pay_dividend(
                        session,
                        company=company,
                        amount=dividend,
                        current_dt=current_dt,
                    )
                    report.dividend_paid = dividend
                except CompanyError as exc:
                    logger.warning("Dividendo company={} fallito: {}", company.id, exc)

        # 5. Bancarotta
        if int(company.athel_balance) <= 0 and report.salaries_failed > 0:
            company.status = CompanyStatus.BANKRUPT.value
            company.is_active = False
            report.declared_bankrupt = True
            logger.warning(
                "Company {} dichiarata BANKRUPT (balance={})",
                company.id,
                company.athel_balance,
            )

        session.flush()
        return report

    # ------------------------------------------------------------------
    # Riconciliazione
    # ------------------------------------------------------------------

    @staticmethod
    def reconcile(session: Session, company: Company) -> CompanyReconcileResult:
        """Verifica che `athel_balance` corrisponda al saldo ledger."""
        acc = CompanyService._athel_account(session, company)
        ledger_balance = LedgerService.get_signed_balance(session, acc)
        cache = int(company.athel_balance)
        return CompanyReconcileResult(
            company_id=company.id,
            cache_balance=cache,
            ledger_balance=ledger_balance,
            ok=cache == ledger_balance,
        )


__all__ = [
    "CompanyError",
    "CompanyReconcileResult",
    "CompanyService",
    "DailyTickReport",
    "SalaryReport",
]
