"""Servizi economici: denaro, inventario, proprietà terriere.

Il denaro è gestito tramite il **ledger double-entry**
(`simai.economy.ledger`): ogni movimento posta una `JournalEntry` con
almeno due `Posting`. Il campo `Character.athel_balance` è una **cache
materializzata** del saldo del conto `char:<id>:athel`; usare
`WealthService.reconcile()` per verificare la coerenza.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.ledger import (
    JournalEntryKind,
    LedgerService,
    PostingDirection,
    PostingSpec,
)
from simai.npc.economy.models import CharacterOwnedLocation
from simai.npc.models import Character
from simai.world.models import GameObject, Location

#: Costo giornaliero di sussistenza (Athel).
DEFAULT_LIVING_COST: Final[int] = 8


class EconomyError(Exception):
    """Errore su operazioni economiche."""


@dataclass(frozen=True, slots=True)
class ReconcileResult:
    """Esito di una riconciliazione `athel_balance` ↔ ledger."""

    character_id: int
    cache_balance: int
    ledger_balance: int
    ok: bool


# ---------------------------------------------------------------------------
# WealthService
# ---------------------------------------------------------------------------


class WealthService:
    """Gestione del bilancio in Athel, backed by ledger double-entry.

    Il campo `Character.athel_balance` è una cache. Ogni modifica posta
    una `JournalEntry` nel ledger e poi aggiorna la cache in modo atomico
    all'interno della stessa sessione.
    """

    @staticmethod
    def balance_of(character: Character) -> int:
        """Ritorna la cache `athel_balance` del character."""
        return int(character.athel_balance)

    @staticmethod
    def ledger_balance_of(
        session: Session,
        character: Character,
        *,
        as_of: AnthalysDateTime | None = None,
    ) -> int:
        """Ritorna il saldo ledger del conto `char:<id>:athel`."""
        account = LedgerService.character_athel_account(
            session,
            character.id,
            character_name=character.full_name,
        )
        return LedgerService.get_signed_balance(session, account, as_of=as_of)

    @staticmethod
    def reconcile(
        session: Session,
        character: Character,
    ) -> ReconcileResult:
        """Verifica che `athel_balance` corrisponda al saldo ledger.

        Ritorna `ReconcileResult.ok == True` se la cache è coerente.
        """
        cache = int(character.athel_balance)
        ledger = WealthService.ledger_balance_of(session, character)
        return ReconcileResult(
            character_id=character.id,
            cache_balance=cache,
            ledger_balance=ledger,
            ok=(cache == ledger),
        )

    @staticmethod
    def add(
        session: Session,
        character: Character,
        amount: int,
        *,
        current_dt: AnthalysDateTime | None = None,
        kind: JournalEntryKind | None = None,
        description: str | None = None,
        reference_type: str | None = None,
        reference_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Aggiunge `amount` (può essere negativo). Ritorna il nuovo bilancio.

        Solleva `EconomyError` se il bilancio andrebbe sotto zero.

        Contropartita:
          - `amount > 0`: `system:mint` (EQUITY)
          - `amount < 0`: `system:consumption` (EXPENSE)

        `kind` default: `MINT` / `SINK` in base al segno. Passa un `kind`
        esplicito (es. `SALARY`, `PURCHASE`) per classificare correttamente
        la causale; verrà registrato in `JournalEntry.kind`.
        """
        if amount == 0:
            return int(character.athel_balance)

        new_balance = int(character.athel_balance) + amount
        if new_balance < 0:
            raise EconomyError(f"Bilancio insufficiente: {character.athel_balance} + {amount} < 0")

        if current_dt is None:
            current_dt = AnthalysDateTime(1, 1, 1)
            logger.warning(
                "WealthService.add senza current_dt (char={}, amount={}). "
                "Uso AnthalysDateTime(1,1,1) come fallback.",
                character.id,
                amount,
            )

        char_account = LedgerService.character_athel_account(
            session,
            character.id,
            character_name=character.full_name,
        )

        if kind is None:
            kind = JournalEntryKind.MINT if amount > 0 else JournalEntryKind.SINK

        if amount > 0:
            counterparty = LedgerService.system_mint_account(session)
            postings = [
                PostingSpec(
                    account=char_account,
                    direction=PostingDirection.DEBIT,
                    amount=amount,
                ),
                PostingSpec(
                    account=counterparty,
                    direction=PostingDirection.CREDIT,
                    amount=amount,
                ),
            ]
        else:
            counterparty = LedgerService.system_consumption_account(session)
            postings = [
                PostingSpec(
                    account=char_account,
                    direction=PostingDirection.CREDIT,
                    amount=-amount,
                ),
                PostingSpec(
                    account=counterparty,
                    direction=PostingDirection.DEBIT,
                    amount=-amount,
                ),
            ]

        desc = description or f"Variazione {amount:+d} Athel per {character.full_name}"
        LedgerService.post(
            session,
            kind=kind,
            description=desc,
            postings=postings,
            current_dt=current_dt,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
        )

        character.athel_balance = new_balance
        session.flush()
        return new_balance

    @staticmethod
    def transfer(
        session: Session,
        *,
        sender: Character,
        receiver: Character,
        amount: int,
        current_dt: AnthalysDateTime | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[int, int]:
        """Trasferisce `amount` da `sender` a `receiver`.

        Ritorna `(new_sender_balance, new_receiver_balance)`. Solleva
        `EconomyError` se il sender non ha fondi sufficienti o se gli
        attori coincidono.
        """
        if amount <= 0:
            raise EconomyError(f"amount deve essere > 0, ricevuto {amount}")
        if sender.id == receiver.id:
            raise EconomyError("sender e receiver devono essere diversi")

        sender_new = int(sender.athel_balance) - amount
        if sender_new < 0:
            raise EconomyError(f"Sender ha fondi insufficienti: {sender.athel_balance} < {amount}")

        if current_dt is None:
            current_dt = AnthalysDateTime(1, 1, 1)
            logger.warning(
                "WealthService.transfer senza current_dt (sender={}, receiver={}, amount={}).",
                sender.id,
                receiver.id,
                amount,
            )

        sender_account = LedgerService.character_athel_account(
            session,
            sender.id,
            character_name=sender.full_name,
        )
        receiver_account = LedgerService.character_athel_account(
            session,
            receiver.id,
            character_name=receiver.full_name,
        )

        desc = description or (
            f"Trasferimento {amount} Athel: {sender.full_name} → {receiver.full_name}"
        )
        LedgerService.post(
            session,
            kind=JournalEntryKind.TRANSFER,
            description=desc,
            postings=[
                PostingSpec(
                    account=receiver_account,
                    direction=PostingDirection.DEBIT,
                    amount=amount,
                ),
                PostingSpec(
                    account=sender_account,
                    direction=PostingDirection.CREDIT,
                    amount=amount,
                ),
            ],
            current_dt=current_dt,
            reference_type="transfer",
            metadata=metadata,
        )

        sender.athel_balance = sender_new
        receiver.athel_balance = int(receiver.athel_balance) + amount
        session.flush()
        return int(sender.athel_balance), int(receiver.athel_balance)

    @staticmethod
    def apply_living_costs(
        session: Session,
        character: Character,
        *,
        daily_cost: int,
        current_dt: AnthalysDateTime,
    ) -> int:
        """Applica costo giornaliero di sussistenza. Ritorna il nuovo bilancio.

        Se il bilancio è insufficiente, paga solo quanto può (importo
        clampato a `balance`), coerentemente con il comportamento legacy.
        Posta una `JournalEntry` di tipo `SINK` per l'importo effettivo.
        """
        if daily_cost < 0:
            raise EconomyError(f"daily_cost deve essere >= 0, ricevuto {daily_cost}")
        current = int(character.athel_balance)
        actual_cost = min(current, daily_cost)
        if actual_cost == 0:
            return current
        WealthService.add(
            session,
            character,
            -actual_cost,
            current_dt=current_dt,
            kind=JournalEntryKind.SINK,
            description=(
                f"Costi di sussistenza giornalieri ({actual_cost} Athel, target {daily_cost})"
            ),
            reference_type="living_cost",
        )
        return int(character.athel_balance)


# ---------------------------------------------------------------------------
# InventoryService
# ---------------------------------------------------------------------------


class InventoryService:
    """Gestione degli oggetti posseduti da un Character."""

    @staticmethod
    def owned_objects(session: Session, character_id: int) -> list[GameObject]:
        """Tutti i GameObject posseduti dal Character (ordinati per id)."""
        return list(
            session.scalars(
                select(GameObject)
                .where(GameObject.owner_character_id == character_id)
                .order_by(GameObject.id)
            )
        )

    @staticmethod
    def give(
        session: Session,
        *,
        character: Character,
        obj: GameObject,
    ) -> None:
        """Assegna `obj` al Character. Sovrascrive eventuale owner precedente."""
        obj.owner_character_id = character.id
        session.flush()

    @staticmethod
    def take(
        session: Session,
        *,
        obj: GameObject,
    ) -> None:
        """Rimuove l'oggetto dall'inventario (owner = NULL)."""
        obj.owner_character_id = None
        session.flush()

    @staticmethod
    def count(session: Session, character_id: int) -> int:
        return len(InventoryService.owned_objects(session, character_id))


# ---------------------------------------------------------------------------
# PropertyService
# ---------------------------------------------------------------------------


class PropertyService:
    """Gestione delle proprietà terriere."""

    @staticmethod
    def owned_locations(session: Session, character_id: int) -> list[tuple[Location, float]]:
        """Lista di `(Location, share)` possedute dal Character."""
        rows = session.scalars(
            select(CharacterOwnedLocation).where(
                CharacterOwnedLocation.character_id == character_id
            )
        ).all()
        result: list[tuple[Location, float]] = []
        for r in rows:
            loc = session.get(Location, r.location_id)
            if loc is not None:
                result.append((loc, float(r.share)))
        return result

    @staticmethod
    def grant(
        session: Session,
        *,
        character: Character,
        location: Location,
        share: float = 1.0,
        current_dt: AnthalysDateTime | None = None,
    ) -> CharacterOwnedLocation:
        """Assegna (o aggiorna) la proprietà di `location` a `character`."""
        if not (0.0 < share <= 1.0):
            raise EconomyError(f"share deve essere in (0, 1], ricevuto {share}")
        existing = session.scalars(
            select(CharacterOwnedLocation).where(
                CharacterOwnedLocation.character_id == character.id,
                CharacterOwnedLocation.location_id == location.id,
            )
        ).first()
        if existing is not None:
            existing.share = share
            session.flush()
            return existing
        row = CharacterOwnedLocation(
            character_id=character.id,
            location_id=location.id,
            share=share,
            since_total_seconds=(current_dt.to_total_seconds() if current_dt is not None else None),
        )
        session.add(row)
        session.flush()
        return row

    @staticmethod
    def revoke(
        session: Session,
        *,
        character_id: int,
        location_id: int,
    ) -> bool:
        """Rimuove la proprietà. Ritorna True se c'era."""
        row = session.scalars(
            select(CharacterOwnedLocation).where(
                CharacterOwnedLocation.character_id == character_id,
                CharacterOwnedLocation.location_id == location_id,
            )
        ).first()
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


__all__ = [
    "DEFAULT_LIVING_COST",
    "EconomyError",
    "InventoryService",
    "PropertyService",
    "ReconcileResult",
    "WealthService",
]
