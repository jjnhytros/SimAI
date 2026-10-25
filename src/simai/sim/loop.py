from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session

from simai.save.service import create_save
from simai.sim.state import get_state
from simai.sim.tick import TickReport, run_tick


@dataclass(frozen=True)
class AutosaveRecord:
    tick: int
    path: Path | None
    error: str | None


@dataclass(frozen=True)
class RunReport:
    ticks_executed: int
    minutes_per_tick: int
    total_minutes: int
    started_at_tick: int
    ended_at_tick: int
    autosaves: tuple[AutosaveRecord, ...]
    failed_at_tick: int | None
    error_message: str | None
    total_paydays: int = 0


def _try_autosave(session: Session, *, base_name: str, executed_ticks: int) -> AutosaveRecord:
    try:
        info = create_save(session, name=f"{base_name}_t{executed_ticks}")
        return AutosaveRecord(tick=executed_ticks, path=info.path, error=None)
    except Exception as exc:  # noqa: BLE001 - l'autosave non deve fermare il loop
        logger.warning(f"Autosave fallito dopo {executed_ticks} tick: {exc}")
        return AutosaveRecord(tick=executed_ticks, path=None, error=str(exc))


def run_simulation(
    session: Session,
    *,
    ticks: int,
    minutes_per_tick: int,
    autosave_every: int = 0,
    autosave_name: str = "autosave",
    include_player: bool = False,
    on_tick: Callable[[TickReport], None] | None = None,
) -> RunReport:
    """Esegue `ticks` tick consecutivi, con autosave periodico opzionale."""
    if ticks <= 0:
        raise ValueError(f"ticks must be > 0, got {ticks}")
    if minutes_per_tick <= 0:
        raise ValueError(f"minutes_per_tick must be > 0, got {minutes_per_tick}")
    if autosave_every < 0:
        raise ValueError(f"autosave_every must be >= 0, got {autosave_every}")

    started_at = get_state(session).tick_index
    autosaves: list[AutosaveRecord] = []
    executed = 0
    failed_at: int | None = None
    error_message: str | None = None
    total_paydays = 0

    for _ in range(ticks):
        try:
            report = run_tick(
                session,
                minutes=minutes_per_tick,
                include_player=include_player,
            )
            session.commit()
        except Exception as exc:  # noqa: BLE001 - confine transazionale
            session.rollback()
            failed_at = started_at + executed
            error_message = f"{type(exc).__name__}: {exc}"
            logger.error(f"Tick fallito a {failed_at}: {error_message}")
            break

        executed += 1
        total_paydays += report.payday.paid
        if on_tick is not None:
            on_tick(report)

        if autosave_every > 0 and executed % autosave_every == 0:
            autosaves.append(
                _try_autosave(
                    session,
                    base_name=autosave_name,
                    executed_ticks=executed,
                )
            )

    return RunReport(
        ticks_executed=executed,
        minutes_per_tick=minutes_per_tick,
        total_minutes=executed * minutes_per_tick,
        started_at_tick=started_at,
        ended_at_tick=started_at + executed,
        autosaves=tuple(autosaves),
        failed_at_tick=failed_at,
        error_message=error_message,
        total_paydays=total_paydays,
    )
