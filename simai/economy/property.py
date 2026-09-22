"""Proprietà immobiliare, mutui e tasse sulla proprietà."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from loguru import logger
from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    select,
)
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.types import JSON

from simai.config.anthalys import DAYS_PER_MONTH, MONTHS_PER_YEAR
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.db.base import Base, IdMixin, TimestampMixin
from simai.economy.enums import MortgageStatus
from simai.economy.ledger import JournalEntryKind
from simai.npc.economy.service import EconomyError, WealthService
from simai.npc.models import Character
from simai.world.district import District
from simai.world.lot import Lot

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

#: Tasso di interesse annuale di default per i mutui.
DEFAULT_ANNUAL_INTEREST_RATE: Final[float] = 0.05  # 5%

#: Durata di default del mutuo in mesi Anthalys.
DEFAULT_MORTGAGE_TERM_MONTHS: Final[int] = 120  # 10 anni Anthalys

#: Giorni Anthalys tra due rate (1 mese = 24 giorni).
MORTGAGE_INTERVAL_DAYS: Final[int] = DAYS_PER_MONTH

#: Numero di rate mancate prima della bancarotta.
MAX_MISSED_PAYMENTS: Final[int] = 3

#: Giorni Anthalys tra due esazioni di tasse proprietà.
PROPERTY_TAX_INTERVAL_DAYS: Final[int] = DAYS_PER_MONTH

#: Giorni Anthalys tra due eventi di mercato immobiliare.
MARKET_UPDATE_INTERVAL_DAYS: Final[int] = 90


# ---------------------------------------------------------------------------
# Modelli
# ---------------------------------------------------------------------------


class LotOwnership(IdMixin, TimestampMixin, Base):
    """Proprietà di un Lot da parte di un Character."""

    __tablename__ = "lot_ownership"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lot.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    share: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    purchase_price: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("character_id", "lot_id", name="uq_lot_ownership_pair"),)

    def __repr__(self) -> str:
        return f"LotOwnership(char={self.character_id}, lot={self.lot_id}, share={self.share:.2f})"


class Mortgage(IdMixin, TimestampMixin, Base):
    """Mutuo ipotecario su un Lot."""

    __tablename__ = "mortgage"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lot.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    principal: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_principal: Mapped[float] = mapped_column(Float, nullable=False)
    annual_interest_rate: Mapped[float] = mapped_column(Float, nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_payment: Mapped[int] = mapped_column(Integer, nullable=False)
    payments_made: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    payments_missed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_payment_at_total_seconds: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True
    )
    started_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=MortgageStatus.ACTIVE.value,
        index=True,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"Mortgage(id={self.id}, char={self.character_id}, "
            f"lot={self.lot_id}, rem={self.remaining_principal:.0f}, "
            f"status={self.status})"
        )


# ---------------------------------------------------------------------------
# Payment formula
# ---------------------------------------------------------------------------


def compute_monthly_payment(
    principal: int,
    annual_interest_rate: float,
    term_months: int,
) -> int:
    """Calcola la rata mensile standard (formula mutuo francese).

    M = P * r * (1+r)^n / ((1+r)^n - 1)
    dove r = tasso mensile, n = numero rate.
    """
    if principal <= 0:
        raise ValueError(f"principal deve essere > 0, ricevuto {principal}")
    if term_months <= 0:
        raise ValueError(f"term_months deve essere > 0, ricevuto {term_months}")
    if annual_interest_rate < 0:
        raise ValueError(f"annual_interest_rate deve essere >= 0, ricevuto {annual_interest_rate}")
    if annual_interest_rate == 0:
        return int(principal / term_months) + 1
    monthly_rate = annual_interest_rate / MONTHS_PER_YEAR
    factor = (1 + monthly_rate) ** term_months
    payment = principal * monthly_rate * factor / (factor - 1)
    return int(payment) + 1  # ceil to avoid rounding down


# ---------------------------------------------------------------------------
# LotOwnershipService
# ---------------------------------------------------------------------------


class LotOwnershipService:
    """Servizio stateless per gestire la proprietà dei lotti."""

    @staticmethod
    def owned_by(session: Session, character_id: int) -> list[LotOwnership]:
        return list(
            session.scalars(
                select(LotOwnership)
                .where(LotOwnership.character_id == character_id)
                .order_by(LotOwnership.lot_id)
            )
        )

    @staticmethod
    def owners_of(session: Session, lot_id: int) -> list[LotOwnership]:
        return list(session.scalars(select(LotOwnership).where(LotOwnership.lot_id == lot_id)))

    @staticmethod
    def owner_character(session: Session, lot_id: int) -> Character | None:
        ownership = session.scalars(
            select(LotOwnership)
            .where(LotOwnership.lot_id == lot_id)
            .order_by(LotOwnership.share.desc())
        ).first()
        if ownership is None:
            return None
        return session.get(Character, ownership.character_id)

    @staticmethod
    def has_owner(session: Session, lot_id: int) -> bool:
        return (
            session.scalars(select(LotOwnership).where(LotOwnership.lot_id == lot_id)).first()
            is not None
        )

    @staticmethod
    def assign(
        session: Session,
        *,
        character: Character,
        lot: Lot,
        share: float,
        purchase_price: int,
        current_dt: AnthalysDateTime,
    ) -> LotOwnership:
        """Assegna la proprietà del lotto (crea o aggiorna)."""
        if not (0.0 < share <= 1.0):
            raise EconomyError(f"share deve essere in (0, 1], ricevuto {share}")
        existing = session.scalars(
            select(LotOwnership).where(
                LotOwnership.character_id == character.id,
                LotOwnership.lot_id == lot.id,
            )
        ).first()
        if existing is not None:
            existing.share = min(1.0, existing.share + share)
            session.flush()
            return existing
        ownership = LotOwnership(
            character_id=character.id,
            lot_id=lot.id,
            share=share,
            purchase_price=purchase_price,
            purchase_at_total_seconds=current_dt.to_total_seconds(),
            metadata_json={},
        )
        session.add(ownership)
        session.flush()
        return ownership

    @staticmethod
    def release(session: Session, *, character_id: int, lot_id: int) -> bool:
        """Rimuove la proprietà. Ritorna True se c'era."""
        row = session.scalars(
            select(LotOwnership).where(
                LotOwnership.character_id == character_id,
                LotOwnership.lot_id == lot_id,
            )
        ).first()
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True

    @staticmethod
    def release_all(session: Session, lot_id: int) -> int:
        """Rimuove tutti i proprietari. Ritorna quanti rimossi."""
        rows = LotOwnershipService.owners_of(session, lot_id)
        for r in rows:
            session.delete(r)
        session.flush()
        return len(rows)


# ---------------------------------------------------------------------------
# MortgageService
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class MortgagePaymentResult:
    """Esito di un tentativo di pagamento rata."""

    mortgage_id: int
    paid: bool
    reason: str
    new_remaining: float
    paid_off: bool


@dataclass(slots=True)
class ForeclosureReport:
    """Esito di una procedura di pignoramento."""

    mortgage_id: int
    lot_id: int
    former_owner_id: int
    ok: bool


class MortgageService:
    """Servizio stateless di gestione mutui."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get(session: Session, mortgage_id: int) -> Mortgage | None:
        return session.get(Mortgage, mortgage_id)

    @staticmethod
    def active_mortgages(session: Session) -> list[Mortgage]:
        return list(
            session.scalars(select(Mortgage).where(Mortgage.status == MortgageStatus.ACTIVE.value))
        )

    @staticmethod
    def of_character(session: Session, character_id: int) -> list[Mortgage]:
        return list(
            session.scalars(
                select(Mortgage).where(Mortgage.character_id == character_id).order_by(Mortgage.id)
            )
        )

    @staticmethod
    def of_lot(session: Session, lot_id: int) -> Mortgage | None:
        return session.scalars(
            select(Mortgage).where(
                Mortgage.lot_id == lot_id,
                Mortgage.status == MortgageStatus.ACTIVE.value,
            )
        ).first()

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @staticmethod
    def create(
        session: Session,
        *,
        character: Character,
        lot: Lot,
        principal: int,
        current_dt: AnthalysDateTime,
        annual_interest_rate: float = DEFAULT_ANNUAL_INTEREST_RATE,
        term_months: int = DEFAULT_MORTGAGE_TERM_MONTHS,
    ) -> Mortgage:
        """Crea un mutuo. Accredita il principal al character subito."""
        if principal <= 0:
            raise EconomyError(f"principal deve essere > 0, ricevuto {principal}")
        if annual_interest_rate < 0:
            raise EconomyError(
                f"annual_interest_rate deve essere >= 0, ricevuto {annual_interest_rate}"
            )
        if term_months <= 0:
            raise EconomyError(f"term_months deve essere > 0, ricevuto {term_months}")
        existing = MortgageService.of_lot(session, lot.id)
        if existing is not None:
            raise EconomyError(f"Esiste già un mutuo attivo per il lotto {lot.id}")

        from simai.config.anthalys import SECONDS_PER_DAY

        monthly = compute_monthly_payment(principal, annual_interest_rate, term_months)
        now_secs = current_dt.to_total_seconds()
        next_payment = now_secs + MORTGAGE_INTERVAL_DAYS * SECONDS_PER_DAY

        # Nota: MORTGAGE_INTERVAL_DAYS è in giorni Anthalys.
        # 1 giorno Anthalys = 28h = 28*3600 sec.
        # Uso 28*60*60 = 100800 secondi/giorno.
        from simai.config.anthalys import SECONDS_PER_DAY

        next_payment = now_secs + MORTGAGE_INTERVAL_DAYS * SECONDS_PER_DAY

        mortgage = Mortgage(
            character_id=character.id,
            lot_id=lot.id,
            principal=principal,
            remaining_principal=float(principal),
            annual_interest_rate=annual_interest_rate,
            term_months=term_months,
            monthly_payment=monthly,
            payments_made=0,
            payments_missed=0,
            next_payment_at_total_seconds=next_payment,
            started_at_total_seconds=now_secs,
            status=MortgageStatus.ACTIVE.value,
            metadata_json={},
        )
        session.add(mortgage)

        # Accredita il principal al character — via ledger
        # Nota: il segno è POSITIVO perché stiamo erogando il mutuo.
        # Il chiamante `LotPurchaseService.buy_with_mortgage` scalerà subito
        # il principal dal cash del buyer per pagare il lotto (netto: 0).
        WealthService.add(
            session,
            character,
            principal,
            current_dt=current_dt,
            kind=JournalEntryKind.MORTGAGE_DISBURSEMENT,
            description=(f"Erogazione mutuo #{mortgage.id} per lotto {lot.name}"),
            reference_type="mortgage",
            metadata={"lot_id": lot.id, "principal": principal},
        )
        session.flush()

        logger.info(
            "Mortgage created: char={} lot={} principal={} rate={:.2%} term={}m payment={}",
            character.id,
            lot.id,
            principal,
            annual_interest_rate,
            term_months,
            monthly,
        )
        return mortgage

    # ------------------------------------------------------------------
    # Payment
    # ------------------------------------------------------------------

    @staticmethod
    def pay_installment(
        session: Session,
        *,
        mortgage: Mortgage,
        current_dt: AnthalysDateTime,
    ) -> MortgagePaymentResult:
        """Prova a pagare la rata dovuta. Ritorna l'esito."""
        if mortgage.status != MortgageStatus.ACTIVE.value:
            return MortgagePaymentResult(
                mortgage_id=mortgage.id,
                paid=False,
                reason=f"status={mortgage.status}",
                new_remaining=mortgage.remaining_principal,
                paid_off=False,
            )
        character = session.get(Character, mortgage.character_id)
        if character is None or not character.is_alive:
            return MortgagePaymentResult(
                mortgage_id=mortgage.id,
                paid=False,
                reason="character_missing",
                new_remaining=mortgage.remaining_principal,
                paid_off=False,
            )

        balance = int(character.athel_balance)
        if balance < mortgage.monthly_payment:
            mortgage.payments_missed += 1
            logger.warning(
                "Mortgage payment missed: id={} char={} balance={} due={}",
                mortgage.id,
                character.id,
                balance,
                mortgage.monthly_payment,
            )
            session.flush()
            return MortgagePaymentResult(
                mortgage_id=mortgage.id,
                paid=False,
                reason="insufficient_funds",
                new_remaining=mortgage.remaining_principal,
                paid_off=False,
            )

        # Calcolo rata: interesse + quota capitale
        monthly_rate = mortgage.annual_interest_rate / MONTHS_PER_YEAR
        interest = mortgage.remaining_principal * monthly_rate
        principal_part = mortgage.monthly_payment - interest
        new_remaining = max(0.0, mortgage.remaining_principal - principal_part)

        # Addebita il character — via ledger
        WealthService.add(
            session,
            character,
            -mortgage.monthly_payment,
            current_dt=current_dt,
            kind=JournalEntryKind.MORTGAGE_PAYMENT,
            description=(f"Rata mutuo #{mortgage.id} per lotto {mortgage.lot_id}"),
            reference_type="mortgage",
            reference_id=mortgage.id,
            metadata={
                "interest": round(interest, 2),
                "principal": round(principal_part, 2),
                "remaining": round(new_remaining, 2),
            },
        )

        mortgage.remaining_principal = new_remaining
        mortgage.payments_made += 1
        mortgage.payments_missed = 0  # reset se era in ritardo
        from simai.config.anthalys import SECONDS_PER_DAY

        mortgage.next_payment_at_total_seconds = (
            current_dt.to_total_seconds() + MORTGAGE_INTERVAL_DAYS * SECONDS_PER_DAY
        )

        paid_off = new_remaining <= 0.001
        if paid_off:
            mortgage.remaining_principal = 0.0
            mortgage.status = MortgageStatus.PAID_OFF.value
            logger.info(
                "Mortgage paid off: id={} char={} lot={}",
                mortgage.id,
                character.id,
                mortgage.lot_id,
            )

        session.flush()

        return MortgagePaymentResult(
            mortgage_id=mortgage.id,
            paid=True,
            reason="ok",
            new_remaining=new_remaining,
            paid_off=paid_off,
        )

    # ------------------------------------------------------------------
    # Foreclosure
    # ------------------------------------------------------------------

    @staticmethod
    def should_foreclose(mortgage: Mortgage) -> bool:
        return (
            mortgage.status == MortgageStatus.ACTIVE.value
            and mortgage.payments_missed >= MAX_MISSED_PAYMENTS
        )

    @staticmethod
    def foreclose(
        session: Session,
        *,
        mortgage: Mortgage,
        current_dt: AnthalysDateTime,
    ) -> ForeclosureReport:
        """Pignora il lotto, rimuove proprietà, marca mutuo FORECLOSED."""
        lot = session.get(Lot, mortgage.lot_id)
        if lot is None:
            return ForeclosureReport(
                mortgage_id=mortgage.id,
                lot_id=mortgage.lot_id,
                former_owner_id=mortgage.character_id,
                ok=False,
            )
        owner_id = mortgage.character_id

        # Rilascia proprietà
        LotOwnershipService.release_all(session, lot.id)

        # Marca il lotto come vacante
        lot.is_developed = False
        lot.usage = "VACANT"

        # Chiudi il mutuo
        mortgage.status = MortgageStatus.FORECLOSED.value
        session.flush()

        session.flush()

        logger.warning(
            "Foreclosure: mortgage={} lot={} former_owner={}",
            mortgage.id,
            lot.id,
            owner_id,
        )
        return ForeclosureReport(
            mortgage_id=mortgage.id,
            lot_id=lot.id,
            former_owner_id=owner_id,
            ok=True,
        )


# ---------------------------------------------------------------------------
# PropertyTaxService
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class TaxCollectionReport:
    """Esito di una raccolta tasse immobiliari."""

    taxed: int
    failed: int
    total_collected: int


class PropertyTaxService:
    """Servizio stateless di tassazione immobiliare."""

    @staticmethod
    def monthly_tax_for(session: Session, lot: Lot) -> int:
        """Tassa mensile = `lot.current_value × district.tax_rate / 18`."""
        district = session.get(District, lot.district_id)
        if district is None:
            return 0
        value = float(lot.current_value or lot.base_price)
        rate = float(district.tax_rate)
        return max(0, int(value * rate / MONTHS_PER_YEAR))

    @staticmethod
    def collect_all(
        session: Session,
        *,
        current_dt: AnthalysDateTime,
    ) -> TaxCollectionReport:
        """Riscuote le tasse mensili da tutti i lotti con proprietari."""
        lots = list(session.scalars(select(Lot)))
        taxed = 0
        failed = 0
        total = 0

        for lot in lots:
            owner = LotOwnershipService.owner_character(session, lot.id)
            if owner is None:
                continue
            tax = PropertyTaxService.monthly_tax_for(session, lot)
            if tax <= 0:
                continue
            balance = int(owner.athel_balance)
            if balance < tax:
                failed += 1
                logger.debug(
                    "Property tax unpaid: char={} lot={} due={} bal={}",
                    owner.id,
                    lot.id,
                    tax,
                    balance,
                )
                continue
            WealthService.add(
                session,
                owner,
                -tax,
                current_dt=current_dt,
                kind=JournalEntryKind.PROPERTY_TAX,
                description=f"Tassa proprietà lotto {lot.name}",
                reference_type="lot",
                reference_id=lot.id,
                metadata={"lot_id": lot.id},
            )

            # Registra il pagamento alla città (Chunk 4.7)
            from simai.city.tax import TaxService

            TaxService.collect_property_tax(
                session,
                character=owner,
                amount=tax,
                lot_id=lot.id,
                current_dt=current_dt,
            )

            taxed += 1
            total += tax

        session.flush()
        return TaxCollectionReport(taxed=taxed, failed=failed, total_collected=total)


# ---------------------------------------------------------------------------
# LotPurchaseService (orchestrazione: cash o mutuo)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class PurchaseOutcome:
    """Esito di un acquisto lotto."""

    ok: bool
    reason: str
    ownership_id: int | None
    mortgage_id: int | None
    cash_paid: int


class LotPurchaseService:
    """Servizio stateless di acquisto/vendita lotti."""

    @staticmethod
    def buy_cash(
        session: Session,
        *,
        buyer: Character,
        lot: Lot,
        current_dt: AnthalysDateTime,
        price: int | None = None,
    ) -> PurchaseOutcome:
        """Acquisto in contanti. Prezzo default = `lot.current_value`."""
        if not buyer.is_alive:
            return PurchaseOutcome(False, "buyer_not_alive", None, None, 0)
        if LotOwnershipService.has_owner(session, lot.id):
            return PurchaseOutcome(False, "already_owned", None, None, 0)

        final_price = int(price if price is not None else lot.current_value)
        if final_price <= 0:
            return PurchaseOutcome(False, "invalid_price", None, None, 0)

        if int(buyer.athel_balance) < final_price:
            return PurchaseOutcome(False, "insufficient_funds", None, None, 0)

        WealthService.add(
            session,
            buyer,
            -final_price,
            current_dt=current_dt,
            kind=JournalEntryKind.PURCHASE,
            description=f"Acquisto lotto {lot.name} (cash)",
            reference_type="lot",
            reference_id=lot.id,
            metadata={"lot_id": lot.id, "method": "cash"},
        )
        ownership = LotOwnershipService.assign(
            session,
            character=buyer,
            lot=lot,
            share=1.0,
            purchase_price=final_price,
            current_dt=current_dt,
        )

        session.flush()

        logger.info(
            "Lot purchased (cash): char={} lot={} price={}",
            buyer.id,
            lot.id,
            final_price,
        )
        return PurchaseOutcome(True, "ok", ownership.id, None, final_price)

    @staticmethod
    def buy_with_mortgage(
        session: Session,
        *,
        buyer: Character,
        lot: Lot,
        current_dt: AnthalysDateTime,
        down_payment: int = 0,
        annual_interest_rate: float = DEFAULT_ANNUAL_INTEREST_RATE,
        term_months: int = DEFAULT_MORTGAGE_TERM_MONTHS,
        price: int | None = None,
    ) -> PurchaseOutcome:
        """Acquisto con mutuo. `down_payment` è la quota cash iniziale."""
        if not buyer.is_alive:
            return PurchaseOutcome(False, "buyer_not_alive", None, None, 0)
        if LotOwnershipService.has_owner(session, lot.id):
            return PurchaseOutcome(False, "already_owned", None, None, 0)

        final_price = int(price if price is not None else lot.current_value)
        if final_price <= 0:
            return PurchaseOutcome(False, "invalid_price", None, None, 0)
        if down_payment < 0:
            return PurchaseOutcome(False, "invalid_down_payment", None, None, 0)
        if down_payment > final_price:
            return PurchaseOutcome(False, "down_payment_exceeds_price", None, None, 0)
        if int(buyer.athel_balance) < down_payment:
            return PurchaseOutcome(False, "insufficient_funds_for_down", None, None, 0)

        # 1. Down payment — via ledger
        if down_payment > 0:
            WealthService.add(
                session,
                buyer,
                -down_payment,
                current_dt=current_dt,
                kind=JournalEntryKind.PURCHASE,
                description=f"Anticipo acquisto lotto {lot.name}",
                reference_type="lot",
                reference_id=lot.id,
                metadata={"lot_id": lot.id, "method": "down_payment"},
            )

        # 2. Mortgage principal
        principal = final_price - down_payment
        if principal <= 0:
            # Equivale a un acquisto cash
            return LotPurchaseService.buy_cash(
                session,
                buyer=buyer,
                lot=lot,
                current_dt=current_dt,
                price=final_price,
            )
        mortgage = MortgageService.create(
            session,
            character=buyer,
            lot=lot,
            principal=principal,
            current_dt=current_dt,
            annual_interest_rate=annual_interest_rate,
            term_months=term_months,
        )
        # Nota: `MortgageService.create` accredita il principal al buyer.
        # Poi lo spendiamo subito per il lotto (netto: cash_in = 0).
        WealthService.add(session, buyer, -principal)

        ownership = LotOwnershipService.assign(
            session,
            character=buyer,
            lot=lot,
            share=1.0,
            purchase_price=final_price,
            current_dt=current_dt,
        )

        session.flush()

        logger.info(
            "Lot purchased (mortgage): char={} lot={} price={} down={} principal={}",
            buyer.id,
            lot.id,
            final_price,
            down_payment,
            principal,
        )
        return PurchaseOutcome(True, "ok", ownership.id, mortgage.id, down_payment)

    @staticmethod
    def sell(
        session: Session,
        *,
        seller: Character,
        lot: Lot,
        current_dt: AnthalysDateTime,
        price: int | None = None,
    ) -> PurchaseOutcome:
        """Vende il lotto al valore di mercato (meno mutuo residuo)."""
        if not LotOwnershipService.has_owner(session, lot.id):
            return PurchaseOutcome(False, "not_owned", None, None, 0)
        ownership = session.scalars(
            select(LotOwnership).where(
                LotOwnership.lot_id == lot.id,
                LotOwnership.character_id == seller.id,
            )
        ).first()
        if ownership is None:
            return PurchaseOutcome(False, "not_owner", None, None, 0)

        # Blocco se mutuo attivo
        mortgage = MortgageService.of_lot(session, lot.id)
        if mortgage is not None:
            if int(seller.athel_balance) < int(mortgage.remaining_principal):
                return PurchaseOutcome(False, "mortgage_not_paid", None, None, 0)
            WealthService.add(
                session,
                seller,
                -int(mortgage.remaining_principal),
                current_dt=current_dt,
                kind=JournalEntryKind.MORTGAGE_PAYMENT,
                description=f"Saldatura mutuo #{mortgage.id} (vendita lotto)",
                reference_type="mortgage",
                reference_id=mortgage.id,
            )
            mortgage.remaining_principal = 0.0
            mortgage.status = MortgageStatus.PAID_OFF.value

        final_price = int(price if price is not None else lot.current_value)
        WealthService.add(
            session,
            seller,
            final_price,
            current_dt=current_dt,
            kind=JournalEntryKind.SALE,
            description=f"Vendita lotto {lot.name}",
            reference_type="lot",
            reference_id=lot.id,
            metadata={"lot_id": lot.id},
        )
        LotOwnershipService.release_all(session, lot.id)
        lot.usage = "VACANT"
        lot.is_developed = False

        session.flush()

        return PurchaseOutcome(True, "ok", None, None, final_price)


__all__ = [
    "DEFAULT_ANNUAL_INTEREST_RATE",
    "DEFAULT_MORTGAGE_TERM_MONTHS",
    "MAX_MISSED_PAYMENTS",
    "MORTGAGE_INTERVAL_DAYS",
    "PROPERTY_TAX_INTERVAL_DAYS",
    "ForeclosureReport",
    "LotOwnership",
    "LotOwnershipService",
    "LotPurchaseService",
    "Mortgage",
    "MortgagePaymentResult",
    "MortgageService",
    "PropertyTaxService",
    "PurchaseOutcome",
    "TaxCollectionReport",
    "compute_monthly_payment",
]
