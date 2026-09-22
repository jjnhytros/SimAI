"""BankService — API unificata per banche, conti, prestiti, interessi.

Ogni operazione posta una `JournalEntry` sul ledger double-entry
(`simai.economy.ledger`). I campi `BankAccount.balance` e
`Loan.remaining_principal` sono **cache materializzate** e possono
essere riconciliate via `BankService.reconcile_bank()`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.config.anthalys import DAYS_PER_MONTH, MONTHS_PER_YEAR, SECONDS_PER_DAY
from simai.core.anthalys_datetime import AnthalysDateTime
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

#: Capitale iniziale iniettato nella banca primaria al bootstrap.
#: Postato via ledger come MINT da `system:mint` → `bank:<code>:reserve`.
PRIMARY_BANK_INITIAL_CAPITAL: Final[int] = 100_000


class BankingError(Exception):
    """Errore di validazione o invariante sul dominio banking."""


# ---------------------------------------------------------------------------
# Dataclass di esito
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LoanPaymentOutcome:
    loan_id: int
    paid: bool
    reason: str
    interest_paid: float = 0.0
    principal_paid: float = 0.0
    new_remaining: float = 0.0
    paid_off: bool = False


@dataclass(frozen=True, slots=True)
class BankReconcileResult:
    bank_id: int
    bank_code: str
    reserve_ledger: int
    deposits_ledger: int
    loans_ledger: int
    accounts_ledger_sum: int
    accounts_cache_sum: int
    loans_ledger_sum: int
    loans_cache_sum: int
    ok: bool


@dataclass(slots=True)
class MonthlyTickReport:
    """Esito di un `monthly_tick` sulla banca."""

    bank_id: int
    interest_paid_to_depositors: int = 0
    deposit_accounts_credited: int = 0
    loan_payments_attempted: int = 0
    loan_payments_succeeded: int = 0
    loan_payments_missed: int = 0
    loans_defaulted: int = 0
    loans_written_off: int = 0
    loan_ids_processed: list[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# BankService
# ---------------------------------------------------------------------------


class BankService:
    """Servizio stateless per il dominio bancario."""

    # ------------------------------------------------------------------
    # Costruttori conti ledger
    # ------------------------------------------------------------------

    @staticmethod
    def _reserve_account(session: Session, bank: Bank) -> Account:
        return LedgerService.get_or_create_account(
            session,
            code=bank_reserve_code(bank.code),
            kind=AccountKind.ASSET,
            owner_type=AccountOwnerType.BANK,
            owner_id=bank.id,
            name=f"Riserva di {bank.name}",
        )

    @staticmethod
    def _deposits_account(session: Session, bank: Bank) -> Account:
        return LedgerService.get_or_create_account(
            session,
            code=bank_deposits_code(bank.code),
            kind=AccountKind.LIABILITY,
            owner_type=AccountOwnerType.BANK,
            owner_id=bank.id,
            name=f"Depositi dei clienti di {bank.name}",
        )

    @staticmethod
    def _loans_account(session: Session, bank: Bank) -> Account:
        return LedgerService.get_or_create_account(
            session,
            code=bank_loans_code(bank.code),
            kind=AccountKind.ASSET,
            owner_type=AccountOwnerType.BANK,
            owner_id=bank.id,
            name=f"Prestiti erogati da {bank.name}",
        )

    @staticmethod
    def _interest_revenue_account(session: Session, bank: Bank) -> Account:
        return LedgerService.get_or_create_account(
            session,
            code=bank_interest_revenue_code(bank.code),
            kind=AccountKind.REVENUE,
            owner_type=AccountOwnerType.BANK,
            owner_id=bank.id,
            name=f"Ricavi da interessi di {bank.name}",
        )

    @staticmethod
    def _character_athel_account(session: Session, character: Character) -> Account:
        return LedgerService.character_athel_account(
            session, character.id, character_name=character.full_name
        )

    @staticmethod
    def _character_bank_account(session: Session, character: Character, bank: Bank) -> Account:
        code = character_bank_account_code(character.id, bank.code)
        return LedgerService.get_or_create_account(
            session,
            code=code,
            kind=AccountKind.ASSET,
            owner_type=AccountOwnerType.CHARACTER,
            owner_id=character.id,
            name=f"Deposito di {character.full_name} presso {bank.name}",
        )

    # ------------------------------------------------------------------
    # Banca primaria
    # ------------------------------------------------------------------

    @staticmethod
    def get_bank(session: Session, code: str) -> Bank | None:
        return session.scalars(select(Bank).where(Bank.code == code)).first()

    @staticmethod
    def all_banks(session: Session, *, only_active: bool = True) -> list[Bank]:
        stmt = select(Bank)
        if only_active:
            stmt = stmt.where(Bank.is_active.is_(True))
        return list(session.scalars(stmt.order_by(Bank.id)))

    @staticmethod
    def ensure_primary_bank(session: Session) -> Bank:
        """Crea (idempotente) la banca commerciale primaria di Anthalys.

        Al primo bootstrap, capitalizza la banca con `PRIMARY_BANK_INITIAL_CAPITAL`
        Athel postando una `JournalEntry MINT` da `system:mint` verso il conto
        `bank:<code>:reserve`. Questo è idempotente: se la reserve ha già
        saldo > 0, non ricapitalizza.
        """
        existing = BankService.get_bank(session, PRIMARY_BANK_CODE)
        if existing is None:
            existing = Bank(
                code=PRIMARY_BANK_CODE,
                name=PRIMARY_BANK_NAME,
                kind=BankKind.COMMERCIAL.value,
                is_active=True,
                owner_character_id=None,
                reserve_ratio=DEFAULT_RESERVE_RATIO,
                deposit_interest_rate=DEFAULT_DEPOSIT_INTEREST_RATE,
                loan_interest_rate=DEFAULT_LOAN_INTEREST_RATE,
                metadata_json={"system": True},
            )
            session.add(existing)
            session.flush()
            logger.info("Banca primaria creata: code={} id={}", existing.code, existing.id)

        # Assicura i 4 conti ledger (idempotente)
        reserve = BankService._reserve_account(session, existing)
        BankService._deposits_account(session, existing)
        BankService._loans_account(session, existing)
        BankService._interest_revenue_account(session, existing)

        # Capitalizzazione iniziale (idempotente: solo se reserve == 0)
        reserve_balance = LedgerService.get_signed_balance(session, reserve)
        if reserve_balance == 0 and PRIMARY_BANK_INITIAL_CAPITAL > 0:
            # NB: usiamo una data minima perché il chiamante potrebbe non
            # avere un `current_dt`. La capitalizzazione avviene una sola
            # volta nella vita del DB, non ha senso legarla a un tick.
            mint = LedgerService.system_mint_account(session)
            LedgerService.post(
                session,
                kind=JournalEntryKind.MINT,
                description=(
                    f"Capitalizzazione iniziale di {existing.name} "
                    f"({PRIMARY_BANK_INITIAL_CAPITAL} Athel)"
                ),
                postings=[
                    PostingSpec(
                        account=reserve,
                        direction=PostingDirection.DEBIT,
                        amount=PRIMARY_BANK_INITIAL_CAPITAL,
                    ),
                    PostingSpec(
                        account=mint,
                        direction=PostingDirection.CREDIT,
                        amount=PRIMARY_BANK_INITIAL_CAPITAL,
                    ),
                ],
                current_dt=AnthalysDateTime(1, 1, 1),
                reference_type="bank_capital",
                reference_id=existing.id,
                metadata={"initial_capital": PRIMARY_BANK_INITIAL_CAPITAL},
            )
            session.flush()
            logger.info(
                "Banca primaria capitalizzata: {} Athel",
                PRIMARY_BANK_INITIAL_CAPITAL,
            )

        return existing

    # ------------------------------------------------------------------
    # Conti
    # ------------------------------------------------------------------

    @staticmethod
    def get_account(
        session: Session,
        character_id: int,
        bank: Bank | None = None,
        *,
        kind: BankAccountKind = BankAccountKind.CHECKING,
    ) -> BankAccount | None:
        """Ritorna il conto del character, opzionalmente filtrato per banca/kind."""
        stmt = select(BankAccount).where(
            BankAccount.character_id == character_id,
            BankAccount.kind == kind.value,
        )
        if bank is not None:
            stmt = stmt.where(BankAccount.bank_id == bank.id)
        return session.scalars(stmt).first()

    @staticmethod
    def get_or_open_account(
        session: Session,
        *,
        character: Character,
        bank: Bank,
        kind: BankAccountKind = BankAccountKind.CHECKING,
        current_dt: AnthalysDateTime,
    ) -> BankAccount:
        """Ritorna il conto del character, creandolo se assente."""
        existing = BankService.get_account(session, character.id, bank, kind=kind)
        if existing is not None:
            return existing

        interest_rate = (
            bank.deposit_interest_rate
            if kind is BankAccountKind.SAVINGS
            else 0.0  # checking non frutta interessi
        )
        account = BankAccount(
            bank_id=bank.id,
            character_id=character.id,
            kind=kind.value,
            balance=0,
            interest_rate=interest_rate,
            opened_at_total_seconds=current_dt.to_total_seconds(),
            is_active=True,
            is_frozen=False,
            metadata_json={},
        )
        session.add(account)
        session.flush()
        # Crea il conto ledger corrispondente (ASSET del character)
        BankService._character_bank_account(session, character, bank)
        logger.debug(
            "BankAccount aperto: char={} bank={} kind={}",
            character.id,
            bank.code,
            kind.value,
        )
        return account

    @staticmethod
    def close_account(
        session: Session,
        account: BankAccount,
        *,
        current_dt: AnthalysDateTime,
        force: bool = False,
    ) -> None:
        """Chiude un conto. Se `force=False` e il saldo è > 0, solleva."""
        if account.balance > 0 and not force:
            raise BankingError(
                f"Conto {account.id} ha saldo {account.balance} > 0; preleva o usa force=True"
            )
        account.is_active = False
        account.balance = 0
        session.flush()

    # ------------------------------------------------------------------
    # Deposito / Prelievo
    # ------------------------------------------------------------------

    @staticmethod
    def deposit(
        session: Session,
        *,
        character: Character,
        bank: Bank,
        amount: int,
        current_dt: AnthalysDateTime,
        kind: BankAccountKind = BankAccountKind.CHECKING,
    ) -> BankAccount:
        """Deposita `amount` Athel dal cash del character al conto bancario.

        Posta una `JournalEntry` a 4 postings:

            DEBIT  char:<id>:bank:<bank>
            CREDIT char:<id>:athel
            DEBIT  bank:<bank>:reserve
            CREDIT bank:<bank>:deposits
        """
        if amount <= 0:
            raise BankingError(f"amount deve essere > 0, ricevuto {amount}")
        if int(character.athel_balance) < amount:
            raise BankingError(f"Cash insufficiente: {character.athel_balance} < {amount}")

        account = BankService.get_or_open_account(
            session, character=character, bank=bank, kind=kind, current_dt=current_dt
        )
        if not account.is_active:
            raise BankingError(f"Conto {account.id} chiuso")
        if account.is_frozen:
            raise BankingError(f"Conto {account.id} congelato")

        char_athel = BankService._character_athel_account(session, character)
        char_bank = BankService._character_bank_account(session, character, bank)
        reserve = BankService._reserve_account(session, bank)
        deposits = BankService._deposits_account(session, bank)

        LedgerService.post(
            session,
            kind=JournalEntryKind.DEPOSIT,
            description=f"Deposito {amount} Athel di {character.full_name}",
            postings=[
                PostingSpec(account=char_bank, direction=PostingDirection.DEBIT, amount=amount),
                PostingSpec(account=char_athel, direction=PostingDirection.CREDIT, amount=amount),
                PostingSpec(account=reserve, direction=PostingDirection.DEBIT, amount=amount),
                PostingSpec(account=deposits, direction=PostingDirection.CREDIT, amount=amount),
            ],
            current_dt=current_dt,
            reference_type="bank_account",
            reference_id=account.id,
            metadata={"character_id": character.id, "bank_id": bank.id, "kind": kind.value},
        )

        # Cache
        character.athel_balance = int(character.athel_balance) - amount
        account.balance = int(account.balance) + amount
        session.flush()
        return account

    @staticmethod
    def withdraw(
        session: Session,
        *,
        character: Character,
        bank: Bank,
        amount: int,
        current_dt: AnthalysDateTime,
        kind: BankAccountKind = BankAccountKind.CHECKING,
    ) -> BankAccount:
        """Preleva `amount` Athel dal conto al cash del character. Inverso di `deposit`."""
        if amount <= 0:
            raise BankingError(f"amount deve essere > 0, ricevuto {amount}")

        account = BankService.get_account(session, character.id, bank, kind=kind)
        if account is None:
            raise BankingError(f"Nessun conto {kind.value} per char={character.id}")
        if not account.is_active:
            raise BankingError(f"Conto {account.id} chiuso")
        if account.is_frozen:
            raise BankingError(f"Conto {account.id} congelato")
        if int(account.balance) < amount:
            raise BankingError(f"Saldo insufficiente: {account.balance} < {amount}")

        char_athel = BankService._character_athel_account(session, character)
        char_bank = BankService._character_bank_account(session, character, bank)
        reserve = BankService._reserve_account(session, bank)
        deposits = BankService._deposits_account(session, bank)

        LedgerService.post(
            session,
            kind=JournalEntryKind.WITHDRAWAL,
            description=f"Prelievo {amount} Athel di {character.full_name}",
            postings=[
                PostingSpec(account=char_athel, direction=PostingDirection.DEBIT, amount=amount),
                PostingSpec(account=char_bank, direction=PostingDirection.CREDIT, amount=amount),
                PostingSpec(account=reserve, direction=PostingDirection.CREDIT, amount=amount),
                PostingSpec(account=deposits, direction=PostingDirection.DEBIT, amount=amount),
            ],
            current_dt=current_dt,
            reference_type="bank_account",
            reference_id=account.id,
            metadata={"character_id": character.id, "bank_id": bank.id, "kind": kind.value},
        )

        character.athel_balance = int(character.athel_balance) + amount
        account.balance = int(account.balance) - amount
        session.flush()
        return account

    # ------------------------------------------------------------------
    # Prestiti
    # ------------------------------------------------------------------

    @staticmethod
    def compute_monthly_payment(
        principal: int,
        annual_interest_rate: float,
        term_months: int,
    ) -> int:
        """Rata mensile standard (formula mutuo francese).

        M = P * r * (1+r)^n / ((1+r)^n - 1), con r = tasso mensile.
        """
        if principal <= 0:
            raise BankingError(f"principal deve essere > 0, ricevuto {principal}")
        if term_months <= 0:
            raise BankingError(f"term_months deve essere > 0, ricevuto {term_months}")
        if annual_interest_rate < 0:
            raise BankingError(
                f"annual_interest_rate deve essere >= 0, ricevuto {annual_interest_rate}"
            )
        if annual_interest_rate == 0:
            return int(principal / term_months) + 1
        monthly_rate = annual_interest_rate / MONTHS_PER_YEAR
        factor = (1 + monthly_rate) ** term_months
        payment = principal * monthly_rate * factor / (factor - 1)
        return int(payment) + 1

    @staticmethod
    def issue_loan(
        session: Session,
        *,
        character: Character,
        bank: Bank,
        principal: int,
        current_dt: AnthalysDateTime,
        annual_interest_rate: float | None = None,
        term_months: int = DEFAULT_LOAN_TERM_MONTHS,
        collateral_lot_id: int | None = None,
    ) -> Loan:
        """Eroga un prestito. Accredita il principal sul cash del character.

        Posta una `JournalEntry` a 4 postings:

            DEBIT  bank:<bank>:loans       (asset bank)
            CREDIT bank:<bank>:reserve     (cash bank esce)
            DEBIT  char:<id>:athel         (cash char entra)
            CREDIT char:<id>:loan          (liability char)
        """
        if not character.is_alive:
            raise BankingError(f"Character {character.id} non è vivo")
        if principal < MIN_LOAN_PRINCIPAL:
            raise BankingError(f"principal < {MIN_LOAN_PRINCIPAL}")
        if principal > MAX_LOAN_PRINCIPAL:
            raise BankingError(f"principal > {MAX_LOAN_PRINCIPAL}")
        if term_months <= 0:
            raise BankingError(f"term_months deve essere > 0, ricevuto {term_months}")

        rate = annual_interest_rate if annual_interest_rate is not None else bank.loan_interest_rate
        if rate < 0:
            raise BankingError(f"rate deve essere >= 0, ricevuto {rate}")

        # Verifica liquidità: reserve >= principal? (semplice, senza riserva frazionaria)
        reserve = BankService._reserve_account(session, bank)
        reserve_balance = LedgerService.get_signed_balance(session, reserve)
        if reserve_balance < principal:
            raise BankingError(
                f"Banca senza liquidità sufficiente: {reserve_balance} < {principal}"
            )

        monthly = BankService.compute_monthly_payment(principal, rate, term_months)
        now_secs = current_dt.to_total_seconds()
        next_payment = now_secs + DAYS_PER_MONTH * SECONDS_PER_DAY

        loan = Loan(
            bank_id=bank.id,
            character_id=character.id,
            principal=principal,
            remaining_principal=float(principal),
            annual_interest_rate=rate,
            term_months=term_months,
            monthly_payment=monthly,
            payments_made=0,
            payments_missed=0,
            next_payment_at_total_seconds=next_payment,
            started_at_total_seconds=now_secs,
            status=LoanStatus.ACTIVE.value,
            collateral_lot_id=collateral_lot_id,
            metadata_json={},
        )
        session.add(loan)
        session.flush()

        char_athel = BankService._character_athel_account(session, character)
        char_loan = LedgerService.get_or_create_account(
            session,
            code=f"char:{character.id}:loan:{bank.code}",
            kind=AccountKind.LIABILITY,
            owner_type=AccountOwnerType.CHARACTER,
            owner_id=character.id,
            name=f"Debito di {character.full_name} verso {bank.name}",
        )
        bank_loans = BankService._loans_account(session, bank)
        reserve_acc = BankService._reserve_account(session, bank)

        LedgerService.post(
            session,
            kind=JournalEntryKind.LOAN_DISBURSEMENT,
            description=(
                f"Prestito {principal} Athel a {character.full_name} "
                f"(rate={monthly}/mese, term={term_months})"
            ),
            postings=[
                PostingSpec(account=bank_loans, direction=PostingDirection.DEBIT, amount=principal),
                PostingSpec(
                    account=reserve_acc, direction=PostingDirection.CREDIT, amount=principal
                ),
                PostingSpec(account=char_athel, direction=PostingDirection.DEBIT, amount=principal),
                PostingSpec(account=char_loan, direction=PostingDirection.CREDIT, amount=principal),
            ],
            current_dt=current_dt,
            reference_type="loan",
            reference_id=loan.id,
            metadata={
                "character_id": character.id,
                "bank_id": bank.id,
                "collateral_lot_id": collateral_lot_id,
            },
        )

        character.athel_balance = int(character.athel_balance) + principal
        session.flush()
        logger.info(
            "Loan issued: id={} char={} bank={} principal={} rate={:.2%} term={}m payment={}",
            loan.id,
            character.id,
            bank.code,
            principal,
            rate,
            term_months,
            monthly,
        )
        return loan

    @staticmethod
    def pay_loan_installment(
        session: Session,
        *,
        loan: Loan,
        current_dt: AnthalysDateTime,
    ) -> LoanPaymentOutcome:
        """Tenta di pagare una rata. Aggiorna lo stato del loan."""
        if loan.status != LoanStatus.ACTIVE.value:
            return LoanPaymentOutcome(
                loan_id=loan.id,
                paid=False,
                reason=f"status={loan.status}",
                new_remaining=loan.remaining_principal,
            )

        bank = session.get(Bank, loan.bank_id)
        character = session.get(Character, loan.character_id)
        if bank is None or character is None or not character.is_alive:
            return LoanPaymentOutcome(
                loan_id=loan.id,
                paid=False,
                reason="character_missing_or_bank_missing",
                new_remaining=loan.remaining_principal,
            )

        due = int(loan.monthly_payment)
        if int(character.athel_balance) < due:
            loan.payments_missed += 1
            payment = LoanPayment(
                loan_id=loan.id,
                amount=due,
                interest_part=0.0,
                principal_part=0.0,
                remaining_after=float(loan.remaining_principal),
                paid_at_total_seconds=current_dt.to_total_seconds(),
                success=False,
                reason="insufficient_funds",
                metadata_json={"missed_count": loan.payments_missed},
            )
            session.add(payment)
            if loan.payments_missed >= MAX_LOAN_MISSED_PAYMENTS:
                loan.status = LoanStatus.DEFAULTED.value
                logger.warning("Loan in default: id={} missed={}", loan.id, loan.payments_missed)
            session.flush()
            return LoanPaymentOutcome(
                loan_id=loan.id,
                paid=False,
                reason="insufficient_funds",
                new_remaining=loan.remaining_principal,
            )

        # Calcolo interesse + quota capitale
        monthly_rate = loan.annual_interest_rate / MONTHS_PER_YEAR
        interest = loan.remaining_principal * monthly_rate
        principal_part = max(0.0, due - interest)
        new_remaining = max(0.0, loan.remaining_principal - principal_part)

        # Posting
        char_athel = BankService._character_athel_account(session, character)
        char_loan = LedgerService.get_or_create_account(
            session,
            code=f"char:{character.id}:loan:{bank.code}",
            kind=AccountKind.LIABILITY,
            owner_type=AccountOwnerType.CHARACTER,
            owner_id=character.id,
            name=f"Debito di {character.full_name} verso {bank.name}",
        )
        bank_loans = BankService._loans_account(session, bank)
        reserve_acc = BankService._reserve_account(session, bank)
        interest_acc = BankService._interest_revenue_account(session, bank)

        principal_int = round(principal_part)
        interest_int = round(interest)

        postings: list[PostingSpec] = [
            # Char: riduce debito, paga cash
            PostingSpec(account=char_loan, direction=PostingDirection.DEBIT, amount=due),
            PostingSpec(account=char_athel, direction=PostingDirection.CREDIT, amount=due),
            # Bank: incassa cash, riduce asset-loans (principal), aumenta revenue (interest)
            PostingSpec(account=reserve_acc, direction=PostingDirection.DEBIT, amount=due),
        ]
        if principal_int > 0:
            postings.append(
                PostingSpec(
                    account=bank_loans,
                    direction=PostingDirection.CREDIT,
                    amount=principal_int,
                )
            )
        if interest_int > 0:
            postings.append(
                PostingSpec(
                    account=interest_acc,
                    direction=PostingDirection.CREDIT,
                    amount=interest_int,
                )
            )
        # Residuo di arrotondamento (1-2 Athel): aggiusta sul principal
        diff = due - principal_int - interest_int
        if diff != 0:
            direction = PostingDirection.CREDIT if diff > 0 else PostingDirection.DEBIT
            postings.append(PostingSpec(account=bank_loans, direction=direction, amount=abs(diff)))

        LedgerService.post(
            session,
            kind=JournalEntryKind.LOAN_PAYMENT,
            description=f"Rata prestito #{loan.id} ({due} Athel)",
            postings=postings,
            current_dt=current_dt,
            reference_type="loan",
            reference_id=loan.id,
            metadata={
                "interest": interest_int,
                "principal": principal_int,
                "remaining": round(new_remaining, 2),
            },
        )

        # Audit
        session.add(
            InterestAccrual(
                loan_id=loan.id,
                accrued_amount=float(interest_int),
                at_total_seconds=current_dt.to_total_seconds(),
                metadata_json={"payment_due": due, "principal_part": principal_int},
            )
        )

        # Aggiorna loan
        loan.remaining_principal = new_remaining
        loan.payments_made += 1
        loan.payments_missed = 0
        loan.next_payment_at_total_seconds = (
            current_dt.to_total_seconds() + DAYS_PER_MONTH * SECONDS_PER_DAY
        )

        paid_off = new_remaining <= 0.001
        if paid_off:
            loan.remaining_principal = 0.0
            loan.status = LoanStatus.PAID_OFF.value
            logger.info(
                "Loan paid off: id={} char={} bank={}",
                loan.id,
                character.id,
                bank.code,
            )

        # Cache char
        character.athel_balance = int(character.athel_balance) - due

        # Audit payment
        session.add(
            LoanPayment(
                loan_id=loan.id,
                amount=due,
                interest_part=float(interest_int),
                principal_part=float(principal_int),
                remaining_after=float(new_remaining),
                paid_at_total_seconds=current_dt.to_total_seconds(),
                success=True,
                reason="ok",
                metadata_json={},
            )
        )
        session.flush()

        return LoanPaymentOutcome(
            loan_id=loan.id,
            paid=True,
            reason="ok",
            interest_paid=float(interest_int),
            principal_paid=float(principal_int),
            new_remaining=new_remaining,
            paid_off=paid_off,
        )

    @staticmethod
    def should_write_off(loan: Loan) -> bool:
        """Un loan è write-off se è in DEFAULTED da almeno MAX_MISSED_PAYMENTS rate."""
        return (
            loan.status == LoanStatus.DEFAULTED.value
            and loan.payments_missed >= MAX_LOAN_MISSED_PAYMENTS * 2
        )

    @staticmethod
    def write_off(
        session: Session,
        *,
        loan: Loan,
        current_dt: AnthalysDateTime,
    ) -> None:
        """Stralcia un prestito irrecuperabile (marca WRITTEN_OFF)."""
        if loan.status not in (
            LoanStatus.DEFAULTED.value,
            LoanStatus.ACTIVE.value,
        ):
            return
        loan.status = LoanStatus.WRITTEN_OFF.value
        session.flush()
        logger.warning(
            "Loan written off: id={} char={} remaining={}",
            loan.id,
            loan.character_id,
            loan.remaining_principal,
        )

    @staticmethod
    def active_loans(session: Session) -> list[Loan]:
        return list(session.scalars(select(Loan).where(Loan.status == LoanStatus.ACTIVE.value)))

    @staticmethod
    def loans_of_character(session: Session, character_id: int) -> list[Loan]:
        return list(
            session.scalars(select(Loan).where(Loan.character_id == character_id).order_by(Loan.id))
        )

    # ------------------------------------------------------------------
    # Tick mensile
    # ------------------------------------------------------------------

    @staticmethod
    def monthly_tick(
        session: Session,
        *,
        current_dt: AnthalysDateTime,
        bank: Bank | None = None,
    ) -> MonthlyTickReport:
        """Esegue il tick mensile su una banca (o sulla primaria).

        1. Accredita interessi sui conti SAVINGS.
        2. Tenta il pagamento delle rate dei prestiti scadute.
        3. Marca DEFAULTED/WRITTEN_OFF.
        """
        if bank is None:
            bank = BankService.ensure_primary_bank(session)
        report = MonthlyTickReport(bank_id=bank.id)
        current_secs = current_dt.to_total_seconds()

        # 1. Interessi sui depositi SAVINGS
        savings_accounts = list(
            session.scalars(
                select(BankAccount).where(
                    BankAccount.bank_id == bank.id,
                    BankAccount.kind == BankAccountKind.SAVINGS.value,
                    BankAccount.is_active.is_(True),
                    BankAccount.balance > 0,
                )
            )
        )
        for acc in savings_accounts:
            # Interesse mensile = balance * annual_rate / 12
            monthly_rate = acc.interest_rate / MONTHS_PER_YEAR
            interest = round(int(acc.balance) * monthly_rate)
            if interest <= 0:
                continue
            char = session.get(Character, acc.character_id)
            if char is None:
                continue
            char_bank = BankService._character_bank_account(session, char, bank)
            reserve_acc = BankService._reserve_account(session, bank)
            deposits_acc = BankService._deposits_account(session, bank)
            LedgerService.post(
                session,
                kind=JournalEntryKind.INTEREST_ACCRUAL,
                description=f"Interessi deposito {interest} Athel su conto {acc.id}",
                postings=[
                    PostingSpec(
                        account=char_bank, direction=PostingDirection.DEBIT, amount=interest
                    ),
                    PostingSpec(
                        account=reserve_acc, direction=PostingDirection.CREDIT, amount=interest
                    ),
                    PostingSpec(
                        account=reserve_acc, direction=PostingDirection.DEBIT, amount=interest
                    ),
                    PostingSpec(
                        account=deposits_acc, direction=PostingDirection.CREDIT, amount=interest
                    ),
                ],
                current_dt=current_dt,
                reference_type="bank_account",
                reference_id=acc.id,
                metadata={"character_id": char.id},
            )
            acc.balance = int(acc.balance) + interest
            report.interest_paid_to_depositors += interest
            report.deposit_accounts_credited += 1

        # 2. Rate prestiti
        loans = list(
            session.scalars(
                select(Loan).where(
                    Loan.bank_id == bank.id,
                    Loan.status == LoanStatus.ACTIVE.value,
                    Loan.next_payment_at_total_seconds <= current_secs,
                )
            )
        )
        for loan in loans:
            report.loan_ids_processed.append(loan.id)
            report.loan_payments_attempted += 1
            outcome = BankService.pay_loan_installment(session, loan=loan, current_dt=current_dt)
            if outcome.paid:
                report.loan_payments_succeeded += 1
            else:
                report.loan_payments_missed += 1
                if loan.status == LoanStatus.DEFAULTED.value:
                    report.loans_defaulted += 1

        # 3. Write-off
        defaulted = list(
            session.scalars(
                select(Loan).where(
                    Loan.bank_id == bank.id,
                    Loan.status == LoanStatus.DEFAULTED.value,
                )
            )
        )
        for loan in defaulted:
            if BankService.should_write_off(loan):
                BankService.write_off(session, loan=loan, current_dt=current_dt)
                report.loans_written_off += 1

        session.flush()
        return report

    # ------------------------------------------------------------------
    # Riconciliazione
    # ------------------------------------------------------------------

    @staticmethod
    def reconcile_bank(session: Session, bank: Bank) -> BankReconcileResult:
        """Verifica che le cache (`BankAccount.balance`, `Loan.remaining_principal`)
        corrispondano ai saldi ledger.
        """
        reserve = BankService._reserve_account(session, bank)
        deposits = BankService._deposits_account(session, bank)
        loans_acc = BankService._loans_account(session, bank)

        reserve_bal = LedgerService.get_signed_balance(session, reserve)
        # signed_amount è flow-based: LIABILITY con CREDIT ha segno negativo
        deposits_bal = -LedgerService.get_signed_balance(session, deposits)
        # ASSET loans: DEBIT positivo
        loans_ledger_bal = LedgerService.get_signed_balance(session, loans_acc)

        # Cache: somma balance di tutti i BankAccount della banca
        cache_accounts_sum = int(
            session.scalar(
                select(func.coalesce(func.sum(BankAccount.balance), 0)).where(
                    BankAccount.bank_id == bank.id
                )
            )
            or 0
        )
        cache_loans_sum = int(
            session.scalar(
                select(func.coalesce(func.sum(Loan.remaining_principal), 0)).where(
                    Loan.bank_id == bank.id,
                    Loan.status.in_([LoanStatus.ACTIVE.value, LoanStatus.DEFAULTED.value]),
                )
            )
            or 0
        )

        ok = (
            deposits_bal == cache_accounts_sum
            and abs(loans_ledger_bal - cache_loans_sum) < 2  # tolleranza arrotondamenti
        )

        return BankReconcileResult(
            bank_id=bank.id,
            bank_code=bank.code,
            reserve_ledger=reserve_bal,
            deposits_ledger=deposits_bal,
            loans_ledger=loans_ledger_bal,
            accounts_ledger_sum=deposits_bal,
            accounts_cache_sum=cache_accounts_sum,
            loans_ledger_sum=loans_ledger_bal,
            loans_cache_sum=cache_loans_sum,
            ok=ok,
        )


__all__ = [
    "PRIMARY_BANK_INITIAL_CAPITAL",
    "BankReconcileResult",
    "BankService",
    "BankingError",
    "LoanPaymentOutcome",
    "MonthlyTickReport",
]
