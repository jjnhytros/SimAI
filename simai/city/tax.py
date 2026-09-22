"""TaxService — raccolta tasse (income, sales, property) per la città."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from simai.city.enums import (
    INCOME_TAX_RATE,
    SALES_TAX_RATE,
    TaxKind,
)
from simai.city.models import TaxPayment
from simai.city.service import CityService
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.ledger import JournalEntryKind
from simai.npc.models import Character


@dataclass(frozen=True, slots=True)
class TaxCollectionResult:
    ok: bool
    amount: int
    kind: TaxKind
    reason: str = ""


class TaxService:
    """Servizio stateless di raccolta tasse."""

    @staticmethod
    def collect_income_tax(
        session: Session,
        *,
        character: Character,
        gross_income: int,
        current_dt: AnthalysDateTime,
        rate: float = INCOME_TAX_RATE,
    ) -> TaxCollectionResult:
        """Tassa sul reddito: `gross_income × rate`.

        Il chiamante ha già accreditato `gross_income` al character.
        Questo metodo scala la tassa (via ledger) e la versa alla città.
        """
        if gross_income <= 0:
            return TaxCollectionResult(False, 0, TaxKind.INCOME, "no_income")
        tax = int(gross_income * rate)
        if tax <= 0:
            return TaxCollectionResult(False, 0, TaxKind.INCOME, "zero_tax")
        if int(character.athel_balance) < tax:
            # Non ha abbastanza: paga quello che ha
            tax = max(0, int(character.athel_balance))
            if tax == 0:
                return TaxCollectionResult(False, 0, TaxKind.INCOME, "no_funds")

        from simai.npc.economy.service import WealthService

        WealthService.add(
            session,
            character,
            -tax,
            current_dt=current_dt,
            kind=JournalEntryKind.TAX,
            description=f"Imposta sul reddito ({rate:.0%})",
            reference_type="tax",
            metadata={"gross_income": gross_income, "rate": rate},
        )
        CityService.add_revenue(session, amount=tax, current_dt=current_dt)
        session.add(
            TaxPayment(
                character_id=character.id,
                kind=TaxKind.INCOME.value,
                amount=tax,
                at_total_seconds=current_dt.to_total_seconds(),
                metadata_json={"gross_income": gross_income, "rate": rate},
            )
        )
        session.flush()
        return TaxCollectionResult(True, tax, TaxKind.INCOME)

    @staticmethod
    def collect_sales_tax(
        session: Session,
        *,
        buyer: Character,
        purchase_amount: int,
        current_dt: AnthalysDateTime,
        rate: float = SALES_TAX_RATE,
    ) -> TaxCollectionResult:
        """Tassa sugli acquisti: `purchase_amount × rate`.

        Si presume che il prezzo del bene NON includa già la tassa.
        Il chiamante ha scalato `purchase_amount`; qui scaliamo l'extra.
        """
        if purchase_amount <= 0:
            return TaxCollectionResult(False, 0, TaxKind.SALES, "no_amount")
        tax = int(purchase_amount * rate)
        if tax <= 0:
            return TaxCollectionResult(False, 0, TaxKind.SALES, "zero_tax")
        if int(buyer.athel_balance) < tax:
            tax = max(0, int(buyer.athel_balance))
            if tax == 0:
                return TaxCollectionResult(False, 0, TaxKind.SALES, "no_funds")

        from simai.npc.economy.service import WealthService

        WealthService.add(
            session,
            buyer,
            -tax,
            current_dt=current_dt,
            kind=JournalEntryKind.TAX,
            description=f"Imposta sugli acquisti ({rate:.0%})",
            reference_type="tax",
            metadata={"purchase": purchase_amount, "rate": rate},
        )
        CityService.add_revenue(session, amount=tax, current_dt=current_dt)
        session.add(
            TaxPayment(
                character_id=buyer.id,
                kind=TaxKind.SALES.value,
                amount=tax,
                at_total_seconds=current_dt.to_total_seconds(),
                metadata_json={"purchase": purchase_amount, "rate": rate},
            )
        )
        session.flush()
        return TaxCollectionResult(True, tax, TaxKind.SALES)

    @staticmethod
    def collect_property_tax(
        session: Session,
        *,
        character: Character,
        amount: int,
        lot_id: int,
        current_dt: AnthalysDateTime,
    ) -> TaxCollectionResult:
        """Registra un pagamento di property tax già scalato dal character.

        **Nota**: la scalata avviene in `PropertyTaxService.collect_all`
        (chiamante). Qui registriamo solo l'entrata nel bilancio città e
        il `TaxPayment` legacy.
        """
        if amount <= 0:
            return TaxCollectionResult(False, 0, TaxKind.PROPERTY, "no_amount")
        CityService.add_revenue(session, amount=amount, current_dt=current_dt)
        session.add(
            TaxPayment(
                character_id=character.id,
                kind=TaxKind.PROPERTY.value,
                amount=amount,
                at_total_seconds=current_dt.to_total_seconds(),
                metadata_json={"lot_id": lot_id},
            )
        )
        session.flush()
        return TaxCollectionResult(True, amount, TaxKind.PROPERTY)

    @staticmethod
    def payments_of(session: Session, character_id: int, *, limit: int = 20) -> list[TaxPayment]:
        from sqlalchemy import select

        return list(
            session.scalars(
                select(TaxPayment)
                .where(TaxPayment.character_id == character_id)
                .order_by(TaxPayment.at_total_seconds.desc())
                .limit(limit)
            )
        )

    # ------------------------------------------------------------------
    # Preview helpers
    # ------------------------------------------------------------------

    @staticmethod
    def preview_sales_tax(amount: int, rate: float = SALES_TAX_RATE) -> int:
        """Ritorna la sales tax che verrebbe applicata su `amount`.

        Formula: `int(amount * rate)`, floor. Zero per `amount <= 0`.
        """
        if amount <= 0:
            return 0
        return int(amount * rate)

    @staticmethod
    def total_with_tax(amount: int, rate: float = SALES_TAX_RATE) -> int:
        """Ritorna `amount + sales_tax(amount)`."""
        if amount <= 0:
            return 0
        return amount + TaxService.preview_sales_tax(amount, rate)


__all__ = ["TaxCollectionResult", "TaxService"]
