import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select

from alembic import command
from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.needs.enums import NeedKind
from simai.needs.service import needs_of
from simai.relationships.models import Relationship
from simai.sim.loop import run_simulation
from simai.sim.state import get_state, reset_state
from simai.sim.tick import TickReport
from simai.world.models import Character
from simai.world.seed import seed_muse_core

# Convenzione 1.0: 1 anno = 365 giorni × 24 ore = 8760 tick da 60 min.
# Provvisoria, in attesa del calendario di Anthalys.
TICKS_PER_YEAR = 8760


@dataclass(frozen=True)
class CharacterMetrics:
    character_key: str
    is_player: bool
    mood_final: float
    mood_min: float
    mood_max: float
    mood_mean: float
    needs_final: dict[str, float]
    needs_mean: dict[str, float]
    needs_min: dict[str, float]
    needs_max: dict[str, float]


@dataclass(frozen=True)
class BenchmarkReport:
    years: float
    ticks: int
    minutes_per_tick: int
    total_minutes: int
    seed: int
    started_at: str
    finished_at: str
    elapsed_seconds: float
    ticks_per_second: float
    characters: list[CharacterMetrics]
    relationships_active: int
    invariants_ok: bool
    invariant_violations: list[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


def _aggregate_samples(
    samples: list[tuple[float, dict[str, float]]],
    fallback_mood: float,
    needs_keys: list[str],
) -> tuple[
    float, float, float, dict[str, float], dict[str, float], dict[str, float], dict[str, float]
]:
    if not samples:
        empty = {k: 0.0 for k in needs_keys}
        return (
            fallback_mood,
            fallback_mood,
            fallback_mood,
            {},
            empty,
            dict(empty),
            dict(empty),
        )
    moods = [m for m, _ in samples]
    mood_min = min(moods)
    mood_max = max(moods)
    mood_mean = sum(moods) / len(moods)

    needs_mean = {k: 0.0 for k in needs_keys}
    needs_min = {k: 100.0 for k in needs_keys}
    needs_max = {k: 0.0 for k in needs_keys}
    needs_final: dict[str, float] = {}
    for _, sample in samples:
        for k, v in sample.items():
            needs_mean[k] += v
            needs_min[k] = min(needs_min[k], v)
            needs_max[k] = max(needs_max[k], v)
        needs_final = sample
    for k in needs_keys:
        needs_mean[k] /= len(samples)
    return (
        mood_mean,
        mood_min,
        mood_max,
        needs_final,
        needs_mean,
        needs_min,
        needs_max,
    )


def run_benchmark(
    db_path: Path,
    *,
    years: float,
    minutes_per_tick: int = 60,
    seed: int = 42,
    include_player: bool = False,
    sample_every: int = 24,
) -> BenchmarkReport:
    """Esegue una simulazione accelerata su DB temporaneo e misura.

    Il DB viene creato da zero, popolato con il seed Muse Core, e
    simulato per `years * TICKS_PER_YEAR` tick. Il file DB resta su
    disco dopo l'esecuzione, per ispezione.
    """
    if years <= 0:
        raise ValueError(f"years must be > 0, got {years}")
    if minutes_per_tick <= 0:
        raise ValueError(f"minutes_per_tick must be > 0, got {minutes_per_tick}")
    if sample_every <= 0:
        raise ValueError(f"sample_every must be > 0, got {sample_every}")

    ticks = max(1, int(years * TICKS_PER_YEAR))
    started_at = datetime.now(UTC)
    t_start = time.perf_counter()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"
    command.upgrade(get_alembic_config(url=url), "head")
    engine = get_engine(url)
    factory = get_session_factory(engine)

    needs_keys = [k.value for k in NeedKind]
    samples: dict[str, list[tuple[float, dict[str, float]]]] = {}
    violations: list[str] = []

    try:
        with factory() as session:
            seed_muse_core(session)
            reset_state(session, master_seed=seed)
            session.commit()

            def on_tick(report: TickReport) -> None:
                last = ticks - 1
                if report.tick_index % sample_every != 0 and (report.tick_index != last):
                    return
                chars = session.scalars(select(Character)).all()
                for c in chars:
                    needs = needs_of(session, c.id)
                    sample = (
                        float(c.mood),
                        {k.value: float(v) for k, v in needs.items()},
                    )
                    samples.setdefault(c.key, []).append(sample)
                    if not (0.0 <= c.mood <= 100.0):
                        violations.append(f"tick {report.tick_index} {c.key}: mood={c.mood}")
                    for k, v in needs.items():
                        if not (0.0 <= v <= 100.0):
                            violations.append(f"tick {report.tick_index} {c.key}: {k.value}={v}")

            run_report = run_simulation(
                session,
                ticks=ticks,
                minutes_per_tick=minutes_per_tick,
                include_player=include_player,
                on_tick=on_tick,
            )

        if run_report.failed_at_tick is not None:
            violations.append(
                f"loop fallito al tick {run_report.failed_at_tick}: {run_report.error_message}"
            )

        finished_at = datetime.now(UTC)
        elapsed = time.perf_counter() - t_start
        tps = ticks / elapsed if elapsed > 0 else 0.0

        character_metrics: list[CharacterMetrics] = []
        with factory() as session:
            chars = session.scalars(select(Character).order_by(Character.id)).all()
            rel_count = session.scalar(select(func.count()).select_from(Relationship)) or 0
            final_state = get_state(session)
            if final_state.tick_index != ticks:
                violations.append(f"tick_index finale {final_state.tick_index} != {ticks}")

            for c in chars:
                s = samples.get(c.key, [])
                (
                    mood_mean,
                    mood_min,
                    mood_max,
                    needs_final,
                    needs_mean,
                    needs_min,
                    needs_max,
                ) = _aggregate_samples(s, float(c.mood), needs_keys)
                character_metrics.append(
                    CharacterMetrics(
                        character_key=c.key,
                        is_player=c.is_player,
                        mood_final=float(c.mood),
                        mood_min=mood_min,
                        mood_max=mood_max,
                        mood_mean=mood_mean,
                        needs_final=needs_final,
                        needs_mean=needs_mean,
                        needs_min=needs_min,
                        needs_max=needs_max,
                    )
                )

        return BenchmarkReport(
            years=years,
            ticks=ticks,
            minutes_per_tick=minutes_per_tick,
            total_minutes=ticks * minutes_per_tick,
            seed=seed,
            started_at=started_at.isoformat(),
            finished_at=finished_at.isoformat(),
            elapsed_seconds=elapsed,
            ticks_per_second=tps,
            characters=character_metrics,
            relationships_active=int(rel_count),
            invariants_ok=not violations,
            invariant_violations=violations,
        )
    finally:
        engine.dispose()


def format_report(report: BenchmarkReport) -> str:
    lines: list[str] = []
    lines.append(
        f"Benchmark {report.years} anni → {report.ticks} tick "
        f"({report.total_minutes} minuti, seed {report.seed})"
    )
    lines.append(f"Tempo: {report.elapsed_seconds:.1f}s ({report.ticks_per_second:.1f} tick/s)")
    lines.append(f"Invarianti: {'OK' if report.invariants_ok else 'VIOLATI'}")
    if report.invariant_violations:
        for v in report.invariant_violations[:10]:
            lines.append(f"  ! {v}")
        if len(report.invariant_violations) > 10:
            lines.append(f"  ... e altri {len(report.invariant_violations) - 10}")
    lines.append(f"Relazioni attive: {report.relationships_active}")
    lines.append("")
    lines.append(
        f"{'char':<10} {'mood':>18} {'hunger':>18} {'thirst':>18} {'fun':>18} {'intim':>18}"
    )
    for c in report.characters:
        marker = "*" if c.is_player else " "
        lines.append(
            f"{marker}{c.character_key:<9} "
            f"{c.mood_mean:5.1f}/{c.mood_min:4.1f}/{c.mood_max:4.1f} "
            f"{c.needs_mean.get('hunger', 0):5.1f}/"
            f"{c.needs_min.get('hunger', 0):4.1f}/"
            f"{c.needs_max.get('hunger', 0):4.1f} "
            f"{c.needs_mean.get('thirst', 0):5.1f}/"
            f"{c.needs_min.get('thirst', 0):4.1f}/"
            f"{c.needs_max.get('thirst', 0):4.1f} "
            f"{c.needs_mean.get('fun', 0):5.1f}/"
            f"{c.needs_min.get('fun', 0):4.1f}/"
            f"{c.needs_max.get('fun', 0):4.1f} "
            f"{c.needs_mean.get('intimacy', 0):5.1f}/"
            f"{c.needs_min.get('intimacy', 0):4.1f}/"
            f"{c.needs_max.get('intimacy', 0):4.1f}"
        )
    return "\n".join(lines)
