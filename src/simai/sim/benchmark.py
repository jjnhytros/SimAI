import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from alembic import command
from sqlalchemy import func, select

from simai.db.alembic_utils import get_alembic_config
from simai.db.session import get_engine, get_session_factory
from simai.economy.calendar import TICKS_PER_DAY
from simai.economy.enums import TransactionKind
from simai.economy.models import Transaction
from simai.economy.seed import seed_demo_economy
from simai.economy.service import job_of
from simai.needs.enums import NeedKind
from simai.needs.service import needs_of
from simai.relationships.models import Relationship
from simai.sim.loop import run_simulation
from simai.sim.state import get_state, reset_state
from simai.sim.tick import TickReport
from simai.world.models import Character
from simai.world.seed import seed_muse_core

TICKS_PER_YEAR = 12096  # 28 tick × 432 giorni (calendario Anthalys)


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
    balance_final: float
    balance_min: float
    balance_max: float
    balance_mean: float
    job_attendance_rate: float = 0.0


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
    salary_transactions: int
    purchase_transactions: int
    invariants_ok: bool
    invariant_violations: list[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


@dataclass(frozen=True)
class _Aggregate:
    mood_mean: float
    mood_min: float
    mood_max: float
    needs_final: dict[str, float]
    needs_mean: dict[str, float]
    needs_min: dict[str, float]
    needs_max: dict[str, float]
    balance_mean: float
    balance_min: float
    balance_max: float


def _aggregate(
    samples: list[tuple[float, dict[str, float], float]],
    fallback_mood: float,
    fallback_balance: float,
    needs_keys: list[str],
) -> _Aggregate:
    if not samples:
        empty = {k: 0.0 for k in needs_keys}
        return _Aggregate(
            mood_mean=fallback_mood,
            mood_min=fallback_mood,
            mood_max=fallback_mood,
            needs_final=dict(empty),
            needs_mean=dict(empty),
            needs_min=dict(empty),
            needs_max=dict(empty),
            balance_mean=fallback_balance,
            balance_min=fallback_balance,
            balance_max=fallback_balance,
        )
    moods = [m for m, _, _ in samples]
    balances = [b for _, _, b in samples]
    needs_mean = {k: 0.0 for k in needs_keys}
    needs_min = {k: 100.0 for k in needs_keys}
    needs_max = {k: 0.0 for k in needs_keys}
    needs_final: dict[str, float] = {}
    for _, sample, _ in samples:
        for k, v in sample.items():
            needs_mean[k] += v
            needs_min[k] = min(needs_min[k], v)
            needs_max[k] = max(needs_max[k], v)
        needs_final = sample
    for k in needs_keys:
        needs_mean[k] /= len(samples)
    return _Aggregate(
        mood_mean=sum(moods) / len(moods),
        mood_min=min(moods),
        mood_max=max(moods),
        needs_final=needs_final,
        needs_mean=needs_mean,
        needs_min=needs_min,
        needs_max=needs_max,
        balance_mean=sum(balances) / len(balances),
        balance_min=min(balances),
        balance_max=max(balances),
    )


def run_benchmark(
    db_path: Path,
    *,
    years: float,
    minutes_per_tick: int = 60,
    seed: int = 42,
    include_player: bool = False,
    sample_every: int = 28,
) -> BenchmarkReport:
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
    samples: dict[str, list[tuple[float, dict[str, float], float]]] = {}
    violations: list[str] = []
    attendance: dict[str, list[bool]] = {}

    try:
        with factory() as session:
            seed_muse_core(session)
            seed_demo_economy(session)
            reset_state(session, master_seed=seed)
            session.commit()

            def on_tick(report: TickReport) -> None:
                # 1. Registra attendance al payday (solo chi ha
                #    un job con wage > 0).
                if report.payday.paid > 0 or report.payday.absent > 0:
                    t_in_day = report.tick_index % TICKS_PER_DAY
                    chars_at_payday = session.scalars(select(Character)).all()
                    for c in chars_at_payday:
                        if c.is_player and not include_player:
                            continue
                        job = job_of(session, c.id)
                        if job is None or job.daily_wage <= 0:
                            continue
                        # Conta solo se il turno di QUESTO
                        # personaggio finisce a questo tick.
                        if t_in_day != job.schedule_end_tick - 1:
                            continue
                        present = c.key not in report.payday.absent_keys
                        attendance.setdefault(c.key, []).append(present)

                # 2. Campionamento periodico di mood/bisogni/balance
                last = ticks - 1
                if report.tick_index % sample_every != 0 and report.tick_index != last:
                    return

                chars = session.scalars(select(Character)).all()
                for c in chars:
                    needs = needs_of(session, c.id)
                    sample = (
                        float(c.mood),
                        {k.value: float(v) for k, v in needs.items()},
                        float(c.balance),
                    )
                    samples.setdefault(c.key, []).append(sample)

                    # 3. Invarianti (mood, bisogni, balance)
                    if not (0.0 <= c.mood <= 100.0):
                        violations.append(f"tick {report.tick_index} {c.key}: mood={c.mood}")
                    if c.balance < 0.0:
                        violations.append(f"tick {report.tick_index} {c.key}: balance={c.balance}")
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

        char_metrics: list[CharacterMetrics] = []
        with factory() as session:
            chars = session.scalars(select(Character).order_by(Character.id)).all()
            rel_count = session.scalar(select(func.count()).select_from(Relationship)) or 0
            salary_count = (
                session.scalar(
                    select(func.count())
                    .select_from(Transaction)
                    .where(Transaction.kind == TransactionKind.SALARY)
                )
                or 0
            )
            purchase_count = (
                session.scalar(
                    select(func.count())
                    .select_from(Transaction)
                    .where(Transaction.kind == TransactionKind.PURCHASE)
                )
                or 0
            )
            final_state = get_state(session)
            if final_state.tick_index != ticks:
                violations.append(f"tick_index finale {final_state.tick_index} != {ticks}")

            for c in chars:
                if c.is_player and not include_player:
                    continue
                s = samples.get(c.key, [])
                agg = _aggregate(s, float(c.mood), float(c.balance), needs_keys)
                att = attendance.get(c.key, [])
                rate = sum(att) / len(att) if att else 0.0
                char_metrics.append(
                    CharacterMetrics(
                        character_key=c.key,
                        is_player=c.is_player,
                        mood_final=float(c.mood),
                        mood_min=agg.mood_min,
                        mood_max=agg.mood_max,
                        mood_mean=agg.mood_mean,
                        needs_final=agg.needs_final,
                        needs_mean=agg.needs_mean,
                        needs_min=agg.needs_min,
                        needs_max=agg.needs_max,
                        balance_final=float(c.balance),
                        balance_min=agg.balance_min,
                        balance_max=agg.balance_max,
                        balance_mean=agg.balance_mean,
                        job_attendance_rate=rate,
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
            characters=char_metrics,
            relationships_active=int(rel_count),
            salary_transactions=int(salary_count),
            purchase_transactions=int(purchase_count),
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
    lines.append(
        f"Transazioni: {report.salary_transactions} salary, {report.purchase_transactions} purchase"
    )
    lines.append("")
    header = (
        f"{'char':<10} {'mood':>18} {'balance':>18} "
        f"{'hunger':>18} {'thirst':>18} "
        f"{'fun':>18} {'intim':>18} {'att%':>6}"
    )
    lines.append(header)
    for c in report.characters:
        marker = "*" if c.is_player else " "
        lines.append(
            f"{marker}{c.character_key:<9} "
            f"{c.mood_mean:5.1f}/{c.mood_min:4.1f}/"
            f"{c.mood_max:4.1f} "
            f"{c.balance_mean:7.1f}/{c.balance_min:5.1f}/"
            f"{c.balance_max:6.1f} "
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
            f"{c.needs_max.get('intimacy', 0):4.1f} "
            f"{c.job_attendance_rate * 100:5.1f}%"
        )
    return "\n".join(lines)
