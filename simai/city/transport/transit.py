"""TransitJob model + TransitService (transito temporale)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from loguru import logger
from sqlalchemy import (
    BigInteger,
    Float,
    ForeignKey,
    Integer,
    String,
    select,
)
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.types import JSON

from simai.config.settings import get_settings
from simai.core.anthalys_datetime import AnthalysDateTime
from simai.db.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from simai.npc.models import Character


class TransitStatus:
    """Stati di un TransitJob."""

    ACTIVE = "ACTIVE"
    ARRIVED = "ARRIVED"
    CANCELLED = "CANCELLED"


class TransitJob(IdMixin, TimestampMixin, Base):
    """Un viaggio in corso di un Character."""

    __tablename__ = "transit_job"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"),
        nullable=False,
    )
    to_location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode: Mapped[str] = mapped_column(String(8), nullable=False)
    started_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    arrives_at_total_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    route_id: Mapped[int | None] = mapped_column(
        ForeignKey("transport_route.id", ondelete="SET NULL"),
        nullable=True,
    )
    cost_paid: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fuel_consumed: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=TransitStatus.ACTIVE,
        index=True,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            f"TransitJob(id={self.id}, char={self.character_id}, "
            f"mode={self.mode}, status={self.status})"
        )


@dataclass(slots=True)
class TransitArrival:
    """Evento di arrivo di un Character."""

    job_id: int
    character_id: int
    to_location_id: int
    mode: str


class TransitService:
    """Servizio stateless di transito temporale."""

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def active_job(session: Session, character_id: int) -> TransitJob | None:
        return session.scalars(
            select(TransitJob).where(
                TransitJob.character_id == character_id,
                TransitJob.status == TransitStatus.ACTIVE,
            )
        ).first()

    @staticmethod
    def active_job_ids(session: Session) -> set[int]:
        """Set di `character_id` attualmente in transito."""
        return set(
            session.scalars(
                select(TransitJob.character_id).where(TransitJob.status == TransitStatus.ACTIVE)
            )
        )

    @staticmethod
    def is_in_transit(session: Session, character_id: int) -> bool:
        return TransitService.active_job(session, character_id) is not None

    # ------------------------------------------------------------------
    # Start
    # ------------------------------------------------------------------

    @staticmethod
    def start(
        session: Session,
        *,
        character: Character,
        plan: Any,  # TravelPlan | MultiLegPlan
        current_dt: AnthalysDateTime,
    ) -> TransitJob:
        """Avvia il transito (single o multi-leg)."""
        from simai.city.transport.multi_leg import MultiLegPlan

        multi = plan if isinstance(plan, MultiLegPlan) else MultiLegPlan.from_single(plan)

        existing = TransitService.active_job(session, character.id)
        if existing is not None:
            raise ValueError(f"character {character.id} già in transito (job {existing.id})")

        # Costi totali
        total_cost = multi.total_cost
        if total_cost > 0:
            from simai.economy.ledger import JournalEntryKind
            from simai.npc.economy.service import EconomyError, WealthService

            if int(character.athel_balance) < total_cost:
                raise EconomyError(f"fondi insufficienti: {character.athel_balance} < {total_cost}")
            WealthService.add(
                session,
                character,
                -total_cost,
                current_dt=current_dt,
                kind=JournalEntryKind.PURCHASE,
                description=f"Transito {multi.mode_label}",
                reference_type="transit",
                metadata={
                    "from_location_id": multi.from_location_id,
                    "to_location_id": multi.to_location_id,
                    "mode": multi.mode_label,
                },
            )

        # Fuel (auto)
        total_fuel = multi.total_fuel
        if total_fuel > 0:
            from simai.city.transport.enums import VehicleType
            from simai.city.transport.service import TransportService

            car = TransportService.vehicle_of(session, character.id, VehicleType.CAR)
            if car is None or car.fuel < total_fuel:
                raise ValueError("car_unavailable_or_no_fuel")
            car.fuel = max(0.0, car.fuel - total_fuel)

        settings = get_settings()
        seconds_per_tick = settings.tick_minutes * 60
        started = current_dt.to_total_seconds()
        arrives = started + multi.total_ticks * seconds_per_tick

        legs_json = [leg.to_dict() for leg in multi.legs]

        job = TransitJob(
            character_id=character.id,
            from_location_id=multi.from_location_id,
            to_location_id=multi.to_location_id,
            mode=multi.mode_label,
            started_at_total_seconds=started,
            arrives_at_total_seconds=arrives,
            route_id=multi.legs[-1].route_id if multi.legs else None,
            cost_paid=total_cost,
            fuel_consumed=total_fuel,
            status=TransitStatus.ACTIVE,
            metadata_json={
                "legs": legs_json,
                "description": multi.description,
            },
        )
        session.add(job)
        session.flush()
        logger.info(
            "Transit started: char={} {} -> {} legs={} ticks={}",
            character.id,
            multi.from_location_id,
            multi.to_location_id,
            len(multi.legs),
            multi.total_ticks,
        )
        return job

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    @staticmethod
    def tick(
        session: Session,
        current_dt: AnthalysDateTime,
    ) -> list[TransitArrival]:
        """Verifica arrivi. Ritorna la lista di arrivi effettuati."""
        now_secs = current_dt.to_total_seconds()
        jobs = list(
            session.scalars(
                select(TransitJob).where(
                    TransitJob.status == TransitStatus.ACTIVE,
                    TransitJob.arrives_at_total_seconds <= now_secs,
                )
            )
        )
        if not jobs:
            return []

        from simai.npc.models import Character

        arrivals: list[TransitArrival] = []
        for job in jobs:
            job.status = TransitStatus.ARRIVED
            c = session.get(Character, job.character_id)
            if c is not None:
                c.location_id = job.to_location_id
                # Se ha auto, sposta anche quella
                if job.mode == "CAR":
                    from simai.city.transport.enums import VehicleType
                    from simai.city.transport.service import TransportService

                    car = TransportService.vehicle_of(session, c.id, VehicleType.CAR)
                    if car is not None:
                        car.location_id = job.to_location_id

            arrivals.append(
                TransitArrival(
                    job_id=job.id,
                    character_id=job.character_id,
                    to_location_id=job.to_location_id,
                    mode=job.mode,
                )
            )

        if arrivals:
            session.flush()
            for a in arrivals:
                logger.info(
                    "Arrival: char={} at loc={} via {}",
                    a.character_id,
                    a.to_location_id,
                    a.mode,
                )
        return arrivals

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    @staticmethod
    def all_active(session: Session) -> list[TransitJob]:
        return list(
            session.scalars(
                select(TransitJob)
                .where(TransitJob.status == TransitStatus.ACTIVE)
                .order_by(TransitJob.id)
            )
        )

    @staticmethod
    def cancel(session: Session, job: TransitJob, current_dt: AnthalysDateTime) -> None:
        job.status = TransitStatus.CANCELLED
        job.metadata_json = {
            **(job.metadata_json or {}),
            "cancelled_at": current_dt.to_total_seconds(),
        }
        session.flush()

    @staticmethod
    def compute_progress(job: TransitJob, *, now_seconds: int) -> dict[str, object]:
        """Calcola progresso e leg corrente per un job."""
        start = job.started_at_total_seconds
        end = job.arrives_at_total_seconds
        total = max(1, end - start)
        elapsed = max(0, now_seconds - start)
        progress = min(1.0, elapsed / total)

        legs = job.metadata_json.get("legs", []) if job.metadata_json else []
        current_leg_index = 0
        cum_ticks = 0
        if legs:
            # Stimiamo il leg corrente proporzionalmente al progresso complessivo
            total_ticks = sum(int(leg.get("duration_ticks", 0)) for leg in legs)
            elapsed_ticks_est = int(progress * total_ticks)
            for i, leg in enumerate(legs):
                d = int(leg.get("duration_ticks", 0))
                if elapsed_ticks_est < cum_ticks + d:
                    current_leg_index = i
                    break
                cum_ticks += d
            else:
                current_leg_index = max(0, len(legs) - 1)

        return {
            "progress": progress,
            "elapsed_seconds": elapsed,
            "total_seconds": total,
            "current_leg_index": current_leg_index,
            "legs": legs,
        }


__all__ = [
    "TransitArrival",
    "TransitJob",
    "TransitService",
    "TransitStatus",
]
