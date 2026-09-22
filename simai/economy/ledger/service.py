"""LedgerService — API unificata per la partita doppia.

Invarianti:
  - Ogni `JournalEntry` ha almeno 2 `Posting`.
  - Per ogni entry, `Σ DEBIT == Σ CREDIT`.
  - `Posting.amount > 0` (vincolo DB).
  - Nessun posting su un `Account.is_active == False`.

Il ledger è **append-only**: non esistono update/delete di `Posting`.
Le rettifiche si fanno con una nuova `JournalEntry` di tipo `ADJUSTMENT`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from simai.core.anthalys_datetime import AnthalysDateTime
from simai.economy.ledger.enums import (
    SYSTEM_ACCOUNT_CONSUMPTION,
    SYSTEM_ACCOUNT_MINT,
    AccountKind,
    AccountOwnerType,
    JournalEntryKind,
    PostingDirection,
    character_account_code,
    signed_amount,
)
from simai.economy.ledger.models import Account, JournalEntry, Posting


class LedgerError(Exception):
    """Errore di validazione o invariante sul ledger."""


# ---------------------------------------------------------------------------
# Spec di posting (input per `post`)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PostingSpec:
    """Specifica di un posting da creare.

    `account` può essere:
      - un oggetto `Account` già risolto
      - un `code` (str) — il service lo risolverà
    """

    account: Account | str
    direction: PostingDirection
    amount: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise LedgerError(f"PostingSpec.amount deve essere > 0, ricevuto {self.amount}")


# ---------------------------------------------------------------------------
# LedgerService
# ---------------------------------------------------------------------------


class LedgerService:
    """Servizio stateless di gestione del ledger."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def get_account(session: Session, code: str) -> Account | None:
        """Ritorna il conto con il `code` dato, o ``None``."""
        return session.scalars(select(Account).where(Account.code == code)).first()

    @staticmethod
    def get_account_by_id(session: Session, account_id: int) -> Account | None:
        return session.get(Account, account_id)

    @staticmethod
    def all_accounts(
        session: Session,
        *,
        owner_type: AccountOwnerType | None = None,
        owner_id: int | None = None,
        kind: AccountKind | None = None,
        only_active: bool = True,
    ) -> list[Account]:
        """Elenca i conti, opzionalmente filtrati."""
        stmt = select(Account)
        if owner_type is not None:
            stmt = stmt.where(Account.owner_type == owner_type.value)
        if owner_id is not None:
            stmt = stmt.where(Account.owner_id == owner_id)
        if kind is not None:
            stmt = stmt.where(Account.kind == kind.value)
        if only_active:
            stmt = stmt.where(Account.is_active.is_(True))
        stmt = stmt.order_by(Account.code)
        return list(session.scalars(stmt))

    # ------------------------------------------------------------------
    # Apertura / chiusura conti
    # ------------------------------------------------------------------

    @staticmethod
    def open_account(
        session: Session,
        *,
        code: str,
        kind: AccountKind,
        owner_type: AccountOwnerType,
        name: str,
        owner_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Account:
        """Crea un nuovo conto. Solleva `LedgerError` se il `code` esiste già."""
        if not code:
            raise LedgerError("code non può essere vuoto")
        if not name:
            raise LedgerError("name non può essere vuoto")

        existing = LedgerService.get_account(session, code)
        if existing is not None:
            raise LedgerError(f"Conto già esistente: {code!r}")

        account = Account(
            code=code,
            kind=kind.value,
            owner_type=owner_type.value,
            owner_id=owner_id,
            name=name,
            is_active=True,
            metadata_json=dict(metadata or {}),
        )
        session.add(account)
        session.flush()
        logger.debug(
            "Ledger: aperto conto {} (kind={}, owner={}:{})",
            code,
            kind.value,
            owner_type.value,
            owner_id,
        )
        return account

    @staticmethod
    def get_or_create_account(
        session: Session,
        *,
        code: str,
        kind: AccountKind,
        owner_type: AccountOwnerType,
        name: str,
        owner_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Account:
        """Come `open_account`, ma ritorna il conto esistente se già presente."""
        existing = LedgerService.get_account(session, code)
        if existing is not None:
            return existing
        return LedgerService.open_account(
            session,
            code=code,
            kind=kind,
            owner_type=owner_type,
            name=name,
            owner_id=owner_id,
            metadata=metadata,
        )

    @staticmethod
    def close_account(session: Session, account: Account) -> None:
        """Disattiva il conto. Non è reversibile in-place (usare `open_account`)."""
        if not account.is_active:
            return
        account.is_active = False
        session.flush()
        logger.debug("Ledger: chiuso conto {}", account.code)

    # ------------------------------------------------------------------
    # Registrazione (post)
    # ------------------------------------------------------------------

    @staticmethod
    def post(
        session: Session,
        *,
        kind: JournalEntryKind,
        description: str,
        postings: Iterable[PostingSpec],
        current_dt: AnthalysDateTime,
        reference_type: str | None = None,
        reference_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """Registra una nuova `JournalEntry`.

        Validazioni:
          - almeno 2 postings
          - ogni account esiste ed è attivo
          - `Σ DEBIT == Σ CREDIT`

        Ritorna l'entry creata (postings già flush-ati).
        """
        specs = list(postings)
        if len(specs) < 2:
            raise LedgerError(f"Una JournalEntry richiede almeno 2 postings, ricevuti {len(specs)}")

        resolved: list[tuple[Account, PostingSpec]] = []
        total_debit = 0
        total_credit = 0

        for spec in specs:
            account = LedgerService._resolve_account(session, spec.account)
            if not account.is_active:
                raise LedgerError(f"Conto chiuso: {account.code!r}")
            resolved.append((account, spec))
            if spec.direction is PostingDirection.DEBIT:
                total_debit += spec.amount
            else:
                total_credit += spec.amount

        if total_debit != total_credit:
            raise LedgerError(f"Entry non bilanciata: DEBIT={total_debit} ≠ CREDIT={total_credit}")
        if total_debit == 0:
            raise LedgerError("Entry con importo totale zero")

        entry = JournalEntry(
            kind=kind.value,
            description=description,
            at_total_seconds=current_dt.to_total_seconds(),
            reference_type=reference_type,
            reference_id=reference_id,
            metadata_json=dict(metadata or {}),
        )
        session.add(entry)
        session.flush()

        for account, spec in resolved:
            posting = Posting(
                entry_id=entry.id,
                account_id=account.id,
                direction=spec.direction.value,
                amount=spec.amount,
                metadata_json=dict(spec.metadata),
            )
            session.add(posting)
        session.flush()

        logger.debug(
            "Ledger: entry {} (kind={}) — {} postings, totale {}",
            entry.id,
            kind.value,
            len(resolved),
            total_debit,
        )
        return entry

    # ------------------------------------------------------------------
    # Saldo
    # ------------------------------------------------------------------

    @staticmethod
    def get_signed_balance(
        session: Session,
        account: Account,
        *,
        as_of: AnthalysDateTime | None = None,
    ) -> int:
        """Saldo **con segno** del conto (positivo se "in attivo" per il suo `kind`).

        Formula: `Σ signed_amount(kind, direction, amount)` su tutti i posting
        del conto. `signed_amount` è +amount se il posting aumenta il valore,
        -amount se lo diminuisce.
        """
        kind = AccountKind(account.kind)
        stmt = (
            select(Posting.direction, Posting.amount)
            .join(JournalEntry, JournalEntry.id == Posting.entry_id)
            .where(Posting.account_id == account.id)
        )
        if as_of is not None:
            stmt = stmt.where(JournalEntry.at_total_seconds <= as_of.to_total_seconds())

        total = 0
        for direction, amount in session.execute(stmt).all():
            total += signed_amount(kind, PostingDirection(direction), int(amount))
        return total

    @staticmethod
    def get_signed_balance_by_code(
        session: Session,
        code: str,
        *,
        as_of: AnthalysDateTime | None = None,
    ) -> int:
        """Come `get_signed_balance` ma per codice. Solleva se il conto non esiste."""
        account = LedgerService.get_account(session, code)
        if account is None:
            raise LedgerError(f"Conto non trovato: {code!r}")
        return LedgerService.get_signed_balance(session, account, as_of=as_of)

    # ------------------------------------------------------------------
    # Storico
    # ------------------------------------------------------------------

    @staticmethod
    def history(
        session: Session,
        account: Account,
        *,
        limit: int = 50,
        as_of: AnthalysDateTime | None = None,
    ) -> list[tuple[JournalEntry, Posting]]:
        """Ritorna `[(entry, posting), ...]` dal più recente al più vecchio."""
        if limit < 1:
            raise LedgerError(f"limit deve essere >= 1, ricevuto {limit}")

        stmt = (
            select(JournalEntry, Posting)
            .join(Posting, Posting.entry_id == JournalEntry.id)
            .where(Posting.account_id == account.id)
            .order_by(JournalEntry.at_total_seconds.desc(), JournalEntry.id.desc())
            .limit(limit)
        )
        if as_of is not None:
            stmt = stmt.where(JournalEntry.at_total_seconds <= as_of.to_total_seconds())
        return [(e, p) for e, p in session.execute(stmt).all()]

    # ------------------------------------------------------------------
    # Conti di sistema
    # ------------------------------------------------------------------

    @staticmethod
    def system_mint_account(session: Session) -> Account:
        """Conto di equity `system:mint` (creato on-demand)."""
        return LedgerService.get_or_create_account(
            session,
            code=SYSTEM_ACCOUNT_MINT,
            kind=AccountKind.EQUITY,
            owner_type=AccountOwnerType.SYSTEM,
            name="Moneta emessa (Mint)",
        )

    @staticmethod
    def system_consumption_account(session: Session) -> Account:
        """Conto di expense `system:consumption` (creato on-demand)."""
        return LedgerService.get_or_create_account(
            session,
            code=SYSTEM_ACCOUNT_CONSUMPTION,
            kind=AccountKind.EXPENSE,
            owner_type=AccountOwnerType.SYSTEM,
            name="Moneta distrutta (Consumption)",
        )

    @staticmethod
    def character_athel_account(
        session: Session,
        character_id: int,
        *,
        character_name: str | None = None,
    ) -> Account:
        """Conto ASSET `char:<id>:athel` di un Character (creato on-demand)."""
        code = character_account_code(character_id)
        name = f"Cassa di {character_name}" if character_name else f"Cassa di char#{character_id}"
        return LedgerService.get_or_create_account(
            session,
            code=code,
            kind=AccountKind.ASSET,
            owner_type=AccountOwnerType.CHARACTER,
            owner_id=character_id,
            name=name,
        )

    # ------------------------------------------------------------------
    # Riconciliazione (dev tool)
    # ------------------------------------------------------------------

    @staticmethod
    def total_balance_check(session: Session) -> int:
        """Somma dei saldi con segno di **tutti** i conti.

        Per l'invariante della partita doppia, il totale deve essere **0**
        (perché ogni entry somma a 0). Ritorna il totale: se ≠ 0, il ledger
        ha un problema.
        """
        total = 0
        for account in LedgerService.all_accounts(session, only_active=False):
            total += LedgerService.get_signed_balance(session, account)
        return total

    @staticmethod
    def entry_count(session: Session) -> int:
        """Numero totale di `JournalEntry` registrate."""
        return int(session.scalar(select(func.count()).select_from(JournalEntry)) or 0)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_account(session: Session, ref: Account | str) -> Account:
        """Risolve un riferimento a un `Account` esistente."""
        if isinstance(ref, Account):
            return ref
        account = LedgerService.get_account(session, ref)
        if account is None:
            raise LedgerError(f"Conto non trovato: {ref!r}")
        return account


__all__ = ["LedgerError", "LedgerService", "PostingSpec"]
