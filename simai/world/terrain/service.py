"""TerrainService — applicazione di terreno e elevazione."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from simai.world.terrain.enums import (
    FLAT_ONLY,
    MAX_HEIGHT,
    TerrainType,
)
from simai.world.terrain.models import TerrainTile

if TYPE_CHECKING:
    from simai.core.anthalys_datetime import AnthalysDateTime
    from simai.npc.models import Character
    from simai.world.lot import Lot


#: Costo base per cella di terreno (Athel).
TERRAIN_BASE_COST: int = 3

#: Costo extra per livello di elevazione.
TERRAIN_ELEVATION_COST: int = 5


@dataclass(frozen=True, slots=True)
class TerrainApplyResult:
    ok: bool
    reason: str
    cost_paid: int = 0


class TerrainService:
    """Servizio stateless di terrain mode."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def tiles_of(session: Session, lot_id: int) -> list[TerrainTile]:
        return list(
            session.scalars(
                select(TerrainTile)
                .where(TerrainTile.lot_id == lot_id)
                .order_by(TerrainTile.y, TerrainTile.x)
            )
        )

    @staticmethod
    def get_tile(session: Session, *, lot_id: int, x: int, y: int) -> TerrainTile | None:
        return session.scalars(
            select(TerrainTile).where(
                TerrainTile.lot_id == lot_id,
                TerrainTile.x == x,
                TerrainTile.y == y,
            )
        ).first()

    # ------------------------------------------------------------------
    # Cost
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_cost(terrain_type: TerrainType, elevation: int) -> int:
        base = TERRAIN_BASE_COST
        if (
            terrain_type in (TerrainType.STONE, TerrainType.ROCK)
            or terrain_type is TerrainType.PAVEMENT
        ):
            base *= 2
        elif terrain_type is TerrainType.WATER:
            base *= 5
        base += elevation * TERRAIN_ELEVATION_COST
        return base

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    @staticmethod
    def set_terrain(
        session: Session,
        *,
        lot: Lot,
        x: int,
        y: int,
        terrain_type: TerrainType,
        elevation: int = 0,
        buyer: Character | None = None,
        current_dt: AnthalysDateTime | None = None,
    ) -> TerrainApplyResult:
        if not (0 <= x < lot.bounds_w and 0 <= y < lot.bounds_h):
            return TerrainApplyResult(False, f"cella ({x},{y}) fuori griglia")
        if not (0 <= elevation <= MAX_HEIGHT):
            return TerrainApplyResult(False, f"elevazione {elevation} fuori [0, {MAX_HEIGHT}]")
        if terrain_type in FLAT_ONLY and elevation > 0:
            return TerrainApplyResult(False, f"{terrain_type.value} richiede elevazione 0")

        cost = TerrainService._compute_cost(terrain_type, elevation)
        if buyer is not None:
            if int(buyer.athel_balance) < cost:
                return TerrainApplyResult(
                    False,
                    f"fondi insufficienti: {buyer.athel_balance} < {cost}",
                )
            from simai.npc.economy.service import WealthService

            WealthService.add(session, buyer, -cost)

        existing = TerrainService.get_tile(session, lot_id=lot.id, x=x, y=y)
        now_secs = current_dt.to_total_seconds() if current_dt else 0

        if existing is not None:
            existing.terrain_type = terrain_type.value
            existing.elevation = elevation
            existing.applied_at_total_seconds = now_secs
        else:
            session.add(
                TerrainTile(
                    lot_id=lot.id,
                    x=x,
                    y=y,
                    terrain_type=terrain_type.value,
                    elevation=elevation,
                    applied_at_total_seconds=now_secs,
                )
            )
        session.flush()
        return TerrainApplyResult(True, "ok", cost)

    @staticmethod
    def clear_tile(session: Session, *, lot_id: int, x: int, y: int) -> bool:
        tile = TerrainService.get_tile(session, lot_id=lot_id, x=x, y=y)
        if tile is None:
            return False
        session.delete(tile)
        session.flush()
        return True

    @staticmethod
    def clear_all(session: Session, *, lot_id: int) -> int:
        rows = TerrainService.tiles_of(session, lot_id)
        n = len(rows)
        session.execute(delete(TerrainTile).where(TerrainTile.lot_id == lot_id))
        session.flush()
        return n


__all__ = [
    "TERRAIN_BASE_COST",
    "TERRAIN_ELEVATION_COST",
    "TerrainApplyResult",
    "TerrainService",
]
