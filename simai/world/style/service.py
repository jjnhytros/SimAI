"""StyleService — applicazione di stili a pavimenti e muri."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from simai.world.style.enums import StyleKind, WallSide
from simai.world.style.models import FloorTile, StyleCatalog, WallCovering

if TYPE_CHECKING:
    from simai.core.anthalys_datetime import AnthalysDateTime
    from simai.npc.models import Character
    from simai.world.build.models import Wall
    from simai.world.lot import Lot


class StyleError(Exception):
    """Errore di validazione style mode."""


@dataclass(frozen=True, slots=True)
class StyleApplyResult:
    """Esito di applicazione stile."""

    ok: bool
    reason: str
    cost_paid: int = 0


class StyleService:
    """Servizio stateless di stile."""

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    @staticmethod
    def list_catalog(session: Session, *, kind: StyleKind | None = None) -> list[StyleCatalog]:
        stmt = select(StyleCatalog).order_by(StyleCatalog.kind, StyleCatalog.name)
        if kind is not None:
            stmt = stmt.where(StyleCatalog.kind == kind.value)
        return list(session.scalars(stmt))

    @staticmethod
    def by_id(session: Session, style_id: int) -> StyleCatalog | None:
        return session.get(StyleCatalog, style_id)

    # ------------------------------------------------------------------
    # Query layout
    # ------------------------------------------------------------------

    @staticmethod
    def floors_of(session: Session, lot_id: int) -> list[FloorTile]:
        return list(session.scalars(select(FloorTile).where(FloorTile.lot_id == lot_id)))

    @staticmethod
    def wall_coverings_of(session: Session, lot_id: int) -> list[WallCovering]:
        """Ritorna i wall coverings per i muri di un lotto.

        Nota: richiede una sotto-query sui wall per filtrare per lotto.
        """
        from simai.world.build.models import Wall as _Wall

        wall_ids = [w.id for w in session.scalars(select(_Wall).where(_Wall.lot_id == lot_id))]
        if not wall_ids:
            return []
        return list(session.scalars(select(WallCovering).where(WallCovering.wall_id.in_(wall_ids))))

    # ------------------------------------------------------------------
    # Floor
    # ------------------------------------------------------------------

    @staticmethod
    def set_floor(
        session: Session,
        *,
        lot: Lot,
        x: int,
        y: int,
        style: StyleCatalog,
        buyer: Character | None = None,
        current_dt: AnthalysDateTime | None = None,
    ) -> StyleApplyResult:
        if style.kind != StyleKind.FLOOR.value:
            return StyleApplyResult(False, "style_kind_not_floor")
        if not (0 <= x < lot.bounds_w and 0 <= y < lot.bounds_h):
            return StyleApplyResult(False, f"cella ({x},{y}) fuori griglia")

        cost = int(style.base_price)
        if buyer is not None:
            if int(buyer.athel_balance) < cost:
                return StyleApplyResult(
                    False, f"fondi insufficienti: {buyer.athel_balance} < {cost}"
                )
            from simai.npc.economy.service import WealthService

            WealthService.add(session, buyer, -cost)

        existing = session.scalars(
            select(FloorTile).where(
                FloorTile.lot_id == lot.id,
                FloorTile.x == x,
                FloorTile.y == y,
            )
        ).first()
        now_secs = current_dt.to_total_seconds() if current_dt else 0

        if existing is not None:
            existing.style_id = style.id
            existing.applied_at_total_seconds = now_secs
        else:
            session.add(
                FloorTile(
                    lot_id=lot.id,
                    x=x,
                    y=y,
                    style_id=style.id,
                    applied_at_total_seconds=now_secs,
                )
            )
        session.flush()
        return StyleApplyResult(True, "ok", cost)

    @staticmethod
    def clear_floor(session: Session, *, lot_id: int, x: int, y: int) -> bool:
        row = session.scalars(
            select(FloorTile).where(
                FloorTile.lot_id == lot_id,
                FloorTile.x == x,
                FloorTile.y == y,
            )
        ).first()
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True

    # ------------------------------------------------------------------
    # Wall
    # ------------------------------------------------------------------

    @staticmethod
    def set_wall_style(
        session: Session,
        *,
        wall: Wall,
        style: StyleCatalog,
        side: WallSide = WallSide.INTERIOR,
        buyer: Character | None = None,
        current_dt: AnthalysDateTime | None = None,
    ) -> StyleApplyResult:
        if style.kind != StyleKind.WALL.value:
            return StyleApplyResult(False, "style_kind_not_wall")
        cost = int(style.base_price)
        if buyer is not None:
            if int(buyer.athel_balance) < cost:
                return StyleApplyResult(
                    False, f"fondi insufficienti: {buyer.athel_balance} < {cost}"
                )
            from simai.npc.economy.service import WealthService

            WealthService.add(session, buyer, -cost)

        existing = session.scalars(
            select(WallCovering).where(
                WallCovering.wall_id == wall.id,
                WallCovering.side == side.value,
            )
        ).first()
        now_secs = current_dt.to_total_seconds() if current_dt else 0

        if existing is not None:
            existing.style_id = style.id
            existing.applied_at_total_seconds = now_secs
        else:
            session.add(
                WallCovering(
                    wall_id=wall.id,
                    side=side.value,
                    style_id=style.id,
                    applied_at_total_seconds=now_secs,
                )
            )
        session.flush()
        return StyleApplyResult(True, "ok", cost)

    @staticmethod
    def clear_wall_style(
        session: Session, *, wall_id: int, side: WallSide = WallSide.INTERIOR
    ) -> bool:
        row = session.scalars(
            select(WallCovering).where(
                WallCovering.wall_id == wall_id,
                WallCovering.side == side.value,
            )
        ).first()
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True

    @staticmethod
    def clear_all(session: Session, *, lot_id: int) -> tuple[int, int]:
        """Rimuove floors + wall coverings di un lotto. Ritorna (floors, walls)."""
        from simai.world.build.models import Wall as _Wall

        n_floors = len(StyleService.floors_of(session, lot_id))
        wall_ids = [w.id for w in session.scalars(select(_Wall).where(_Wall.lot_id == lot_id))]
        n_walls = 0
        if wall_ids:
            n_walls = len(
                list(
                    session.scalars(select(WallCovering).where(WallCovering.wall_id.in_(wall_ids)))
                )
            )
            session.execute(delete(WallCovering).where(WallCovering.wall_id.in_(wall_ids)))
        session.execute(delete(FloorTile).where(FloorTile.lot_id == lot_id))
        session.flush()
        return n_floors, n_walls


__all__ = ["StyleApplyResult", "StyleError", "StyleService"]
