import typer
from sqlalchemy import select

from simai.cli._helpers import require_schema, resolve_character
from simai.db.session import get_engine, get_session_factory
from simai.economy.models import Job, Transaction
from simai.economy.service import all_jobs, job_of, transactions_of
from simai.economy.work import (
    WorkState,
    tick_in_day,
    work_state_for,
)
from simai.sim.state import get_state
from simai.world.models import Character

economy_app = typer.Typer(help="Comandi sull'economia.")


def _print_balance(char: Character, job: Job | None) -> None:
    marker = "★ " if char.is_player else "  "
    if job is not None:
        typer.echo(
            f"{marker}{char.key:<10} {char.balance:8.2f} Athel  "
            f"({job.title.value}, wage {job.daily_wage:.1f}/day)"
        )
    else:
        typer.echo(f"{marker}{char.key:<10} {char.balance:8.2f} Athel  (no job)")


def _print_tx(tx: Transaction, names: dict[int, str]) -> None:
    from_label = (
        names.get(tx.from_character_id, "world") if tx.from_character_id is not None else "world"
    )
    to_label = names.get(tx.to_character_id, "world") if tx.to_character_id is not None else "world"
    typer.echo(
        f"  t{tx.tick_index:<5} {tx.kind.value:<10} "
        f"{from_label:>10} → {to_label:<10} "
        f"{tx.amount:7.2f}  {tx.note}"
    )


@economy_app.command("balance")
def balance(
    character: str | None = typer.Option(None, "--character", "-c"),
    all_: bool = typer.Option(False, "--all", "-a"),
) -> None:
    """Mostra il balance di un personaggio o di tutti."""
    if character is None and not all_:
        typer.echo("Specifica --character <key> oppure --all", err=True)
        raise typer.Exit(code=1)

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)

    with factory() as session:
        if character is not None:
            char = resolve_character(session, character)
            job = job_of(session, char.id)
            _print_balance(char, job)
            return
        chars = session.scalars(select(Character).order_by(Character.id)).all()
        for char in chars:
            job = job_of(session, char.id)
            _print_balance(char, job)


@economy_app.command("ledger")
def ledger(
    character: str | None = typer.Option(None, "--character", "-c"),
    limit: int = typer.Option(20, "--limit", "-n"),
) -> None:
    """Mostra le transazioni recenti."""
    if limit <= 0:
        typer.echo("--limit deve essere > 0", err=True)
        raise typer.Exit(code=1)

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)

    with factory() as session:
        if character is not None:
            char = resolve_character(session, character)
            full = transactions_of(session, char.id)
            txs = full[-limit:]
            scope = f"di '{character}' ({len(txs)}/{len(full)})"
        else:
            txs = list(
                session.scalars(
                    select(Transaction).order_by(Transaction.id.desc()).limit(limit)
                ).all()
            )
            txs.reverse()
            scope = f"ultime {len(txs)}"

        names: dict[int, str] = {}
        for tx in txs:
            for cid in (
                tx.from_character_id,
                tx.to_character_id,
            ):
                if cid is not None and cid not in names:
                    c = session.get(Character, cid)
                    if c is not None:
                        names[cid] = c.key

    typer.echo(f"Transazioni {scope}:")
    for tx in txs:
        _print_tx(tx, names)


@economy_app.command("jobs")
def jobs() -> None:
    """Elenca i lavori con stato corrente."""
    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)

    with factory() as session:
        job_list = all_jobs(session)
        names: dict[int, str] = {}
        for job in job_list:
            c = session.get(Character, job.character_id)
            if c is not None:
                names[c.id] = c.key

        current_tick = get_state(session).tick_index
        t = tick_in_day(current_tick)

    typer.echo(f"Lavori ({len(job_list)}):")
    for job in job_list:
        key = names.get(job.character_id, f"id={job.character_id}")
        state = work_state_for(job, t)
        state_label = {
            WorkState.BEFORE_WORK: "in attesa",
            WorkState.WORKING: "al lavoro",
            WorkState.AFTER_WORK: "fuori orario",
            WorkState.NO_JOB: "—",
        }[state]
        typer.echo(
            f"  {key:<10} {job.title.value:<12} "
            f"@ {job.location_key:<8} "
            f"wage {job.daily_wage:.1f}/day  "
            f"{job.schedule_start_tick:02d}-"
            f"{job.schedule_end_tick:02d}  "
            f"[{state_label}]"
        )


@economy_app.command("seed")
def seed() -> None:
    """Popola i negozi del Quartiere delle Muse (idempotente)."""
    from simai.economy.seed import seed_demo_economy

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        report = seed_demo_economy(session)
        session.commit()
    typer.echo(f"Economia: {report['shop_items_created']} ShopItem creati.")


@economy_app.command("shops")
def shops() -> None:
    """Elenca i negozi (ShopItem) per location."""
    from simai.economy.models import ShopItem

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        items = session.scalars(
            select(ShopItem).order_by(ShopItem.location_key, ShopItem.action_kind)
        ).all()

    if not items:
        typer.echo("Nessun negozio. Esegui `simai economy seed`.")
        return

    typer.echo(f"Negozio ({len(items)} item):")
    for item in items:
        stock_label = "∞" if item.stock < 0 else str(item.stock)
        typer.echo(
            f"  {item.location_key:<8} {item.action_kind.value:<10} "
            f"{item.price:5.1f} Athel  stock={stock_label}"
        )


@economy_app.command("restock")
def restock() -> None:
    """Riporta lo stock ai valori dello spec."""
    from simai.economy.seed import restock_all

    engine = get_engine()
    require_schema(engine)
    factory = get_session_factory(engine)
    with factory() as session:
        touched = restock_all(session)
        session.commit()
    typer.echo(f"Restock: {touched} ShopItem aggiornati.")
