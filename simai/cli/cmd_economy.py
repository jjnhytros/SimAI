"""Comandi `economy`: lavori, negozi, transazioni, payday."""

from __future__ import annotations

import typer
from rich.table import Table
from sqlalchemy import select

from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.cli.cmd_aion import aion_app
from simai.config.settings import get_settings
from simai.db.session import get_session_factory
from simai.economy import (
    DEFAULT_WAGES,
    JobError,
    JobService,
    JobType,
    LotOwnershipService,
    LotPurchaseService,
    MarketService,
    MortgageService,
    PaydayService,
    PropertyTaxService,
    ShopItem,
    seed_demo_economy,
)
from simai.economy.banking import Bank, BankService
from simai.economy.banking.enums import BankAccountKind
from simai.economy.banking.service import BankingError
from simai.economy.companies import (
    Company,
    CompanyError,
    CompanyKind,
    CompanyService,
    seed_demo_companies,
)
from simai.economy.ledger import (
    JournalEntry,
    JournalEntryKind,
    LedgerService,
    Posting,
)
from simai.npc.housing import RealEstateAI
from simai.npc.models import Character
from simai.npc.skills import SkillService, SkillType
from simai.world.buy.supplier import SupplierService
from simai.world.enums import LocationType
from simai.world.lot import Lot
from simai.world.lot_service import get_lot
from simai.world.models import GameObject, Location

economy_app = typer.Typer(
    name="economy",
    help="Mercato, lavori, prezzi.",
    no_args_is_help=True,
)


def _require_migrated() -> None:
    if not check_migrations_applied():
        console.print("[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# seed
# ---------------------------------------------------------------------------


@economy_app.command("seed")
def economy_seed() -> None:
    """Assegna lavori demo a NPC adulti (idempotente)."""
    _require_migrated()
    start = build_starting_datetime()

    factory = get_session_factory()
    with factory() as session:
        result = seed_demo_economy(session, current_dt=start)
        session.commit()

    if result.shops_found == 0:
        console.print("[yellow]Nessun negozio trovato.[/] [bold]Esegui prima `world seed`.[/]")
        return

    console.print(
        f"[green]Seed economia:[/] jobs={result.jobs_assigned} shops={result.shops_found}"
    )


# ---------------------------------------------------------------------------
# jobs
# ---------------------------------------------------------------------------


@economy_app.command("jobs")
def economy_jobs() -> None:
    """Elenca tutti gli impieghi attivi."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        jobs = JobService.all_active_jobs(session)
        rows: list[tuple[int, str, str, int, str, str, str]] = []
        for j in jobs:
            c = session.get(Character, j.character_id)
            name = c.full_name if c is not None else "?"

            wp_name = "—"
            if j.workplace_id is not None:
                wp_loc = session.get(Location, j.workplace_id)
                if wp_loc is not None:
                    wp_name = wp_loc.name

            # Livello skill corrente
            skill_info = "—"
            if j.required_skill_type:
                try:
                    st = SkillType(j.required_skill_type)
                    skill = SkillService.get_skill(session, c.id, st) if c else None
                    lvl = skill.level if skill else 0
                    effective = j.effective_daily_wage(lvl)
                    skill_info = f"{st.value}={lvl} (wage eff. {effective})"
                except ValueError:
                    skill_info = j.required_skill_type

            rows.append(
                (j.id, name, j.title, j.daily_wage, wp_name, skill_info, j.promoted_title or "—")
            )

    if not rows:
        console.print("[yellow]Nessun impiego attivo.[/]")
        return

    table = Table(title="Impieghi attivi")
    table.add_column("ID", style="cyan")
    table.add_column("Lavoratore", style="magenta")
    table.add_column("Titolo", style="green")
    table.add_column("Wage/g", justify="right")
    table.add_column("Workplace", style="yellow")
    table.add_column("Skill req.", style="blue")
    table.add_column("Promoted to", style="dim")
    for jid, name, title, wage, wp, skill_info, promoted in rows:
        table.add_row(str(jid), name, title, f"{wage} Athel", wp, skill_info, promoted)
    console.print(table)


@economy_app.command("job-assign")
def economy_job_assign(
    character_id: int = typer.Argument(..., help="ID del character."),
    job_type: str = typer.Argument(..., help="JobType (FARMER, CRAFTSMAN, ...)."),
    title: str = typer.Argument(..., help="Titolo (es. 'Fabbro')."),
    workplace_id: int | None = typer.Option(
        None, "--workplace", "-w", help="ID della location di lavoro."
    ),
    daily_wage: int | None = typer.Option(
        None, "--wage", "-g", min=1, help="Salario/giorno (default: dal tipo)."
    ),
    required_skill: str | None = typer.Option(
        None,
        "--skill",
        "-k",
        help="SkillType richiesta (CRAFTING, FARMING, ...).",
    ),
    min_skill_level: int = typer.Option(
        0,
        "--min-level",
        min=0,
        max=20,
        help="Livello minimo della skill.",
    ),
    wage_skill_scale: float = typer.Option(
        0.05,
        "--scale",
        min=0.0,
        max=1.0,
        help="Scala del wage per skill level.",
    ),
    promoted_title: str | None = typer.Option(
        None, "--promote-to", help="Titolo dopo la promozione."
    ),
) -> None:
    """Assegna un lavoro a un character."""
    _require_migrated()
    try:
        jt = JobType(job_type.upper())
    except ValueError:
        valid = ", ".join(x.value for x in JobType)
        console.print(f"[red]JobType sconosciuto: {job_type!r}[/]\n[dim]Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    req_skill: SkillType | None = None
    if required_skill is not None:
        try:
            req_skill = SkillType(required_skill.upper())
        except ValueError:
            valid = ", ".join(x.value for x in SkillType)
            console.print(
                f"[red]SkillType sconosciuta: {required_skill!r}[/]\n[dim]Valide: {valid}[/]"
            )
            raise typer.Exit(code=1) from None

    start = build_starting_datetime()
    factory = get_session_factory()
    try:
        with factory() as session:
            c = session.get(Character, character_id)
            if c is None:
                console.print(f"[red]Character id={character_id} non trovato.[/]")
                raise typer.Exit(code=1)
            workplace = session.get(Location, workplace_id) if workplace_id is not None else None
            job = JobService.assign(
                session,
                character=c,
                job_type=jt,
                title=title,
                workplace=workplace,
                daily_wage=daily_wage,
                current_dt=start,
                required_skill_type=req_skill,
                min_skill_level=min_skill_level,
                wage_skill_scale=wage_skill_scale,
                promoted_title=promoted_title,
            )
            session.commit()
    except JobError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Lavoro assegnato:[/] {c.full_name} → {title} "
        f"({jt.value}, {job.daily_wage} Athel/g"
        + (f", skill={req_skill.value} min={min_skill_level}" if req_skill else "")
        + ")"
    )


@economy_app.command("job-quit")
def economy_job_quit(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Disattiva il lavoro di un character."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        ok = JobService.quit(session, character_id)
        session.commit()

    if not ok:
        console.print("[yellow]Nessun lavoro attivo da disattivare.[/]")
        return
    console.print(f"[green]Lavoro disattivato per char={character_id}.[/]")


@economy_app.command("wages")
def economy_wages() -> None:
    """Mostra i salari di default per tipo di lavoro."""
    table = Table(title="Salari di default (Athel/giorno)")
    table.add_column("JobType", style="cyan")
    table.add_column("Wage", justify="right", style="magenta")
    for jt, wage in DEFAULT_WAGES.items():
        table.add_row(jt.value, str(wage))
    console.print(table)


# ---------------------------------------------------------------------------
# shops
# ---------------------------------------------------------------------------


@economy_app.command("shops")
def economy_shops() -> None:
    """Elenca tutti i negozi (Location di tipo SHOP)."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        shops = list(
            session.scalars(select(Location).where(Location.type == LocationType.SHOP.value))
        )
        counts: dict[int, int] = {
            s.id: len(list(session.scalars(select(ShopItem).where(ShopItem.location_id == s.id))))
            for s in shops
        }
        rows: list[tuple[int, str, int, int]] = [
            (s.id, s.name, s.capacity, counts[s.id]) for s in shops
        ]

    if not rows:
        console.print("[yellow]Nessun negozio. Esegui `world seed`.[/]")
        return

    table = Table(title="Negozi")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Cap", justify="right")
    table.add_column("Items", justify="right")
    for sid, name, cap, n_items in rows:
        table.add_row(str(sid), name, str(cap), str(n_items))
    console.print(table)


@economy_app.command("shop")
def economy_shop(
    location_id: int = typer.Argument(..., help="ID del negozio."),
) -> None:
    """Mostra il catalogo di un negozio."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        loc = session.get(Location, location_id)
        if loc is None:
            console.print(f"[red]Location id={location_id} non trovata.[/]")
            raise typer.Exit(code=1)
        items = MarketService.items_in(session, location_id)

    if not items:
        console.print(f"[yellow]{loc.name} non ha un catalogo.[/]")
        return

    table = Table(title=f"Catalogo di {loc.name}")
    table.add_column("ItemType", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Prezzo", justify="right", style="green")
    table.add_column("Stock", justify="right")
    for it in items:
        stock = "∞" if it.stock < 0 else str(it.stock)
        table.add_row(it.item_type, it.item_name, f"{it.current_price} Athel", stock)
    console.print(table)


# ---------------------------------------------------------------------------
# buy / sell
# ---------------------------------------------------------------------------


@economy_app.command("buy")
def economy_buy(
    character_id: int = typer.Argument(..., help="ID del compratore."),
    location_id: int = typer.Argument(..., help="ID del negozio."),
    item_type: str = typer.Argument(..., help="Item type (es. 'bread')."),
) -> None:
    """Acquista un item da un negozio (con sales tax)."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        buyer = session.get(Character, character_id)
        shop = session.get(Location, location_id)
        if buyer is None or shop is None:
            console.print("[red]Character o location non trovati.[/]")
            raise typer.Exit(code=1)

        result = MarketService.buy(
            session,
            buyer=buyer,
            shop=shop,
            item_type=item_type,
            current_dt=start,
        )
        session.commit()

    if not result.success:
        console.print(f"[red]Acquisto fallito: {result.reason}[/]")
        raise typer.Exit(code=1)

    table = Table(title="Acquisto completato")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("object_id", str(result.object_id))
    table.add_row("item_price", str(result.item_price))
    table.add_row("sales_tax", str(result.tax_paid))
    table.add_row("total_paid", f"[bold]{result.price_paid}[/]")
    console.print(table)


@economy_app.command("sell")
def economy_sell(
    character_id: int = typer.Argument(..., help="ID del venditore."),
    location_id: int = typer.Argument(..., help="ID del negozio."),
    object_id: int = typer.Argument(..., help="ID dell'oggetto."),
) -> None:
    """Vende un oggetto a un negozio (con quality-based pricing)."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        seller = session.get(Character, character_id)
        shop = session.get(Location, location_id)
        obj = session.get(GameObject, object_id)
        if seller is None or shop is None or obj is None:
            console.print("[red]Character, location o oggetto non trovati.[/]")
            raise typer.Exit(code=1)

        result = MarketService.sell(session, seller=seller, shop=shop, obj=obj, current_dt=start)
        session.commit()

    if not result.success:
        console.print(
            f"[red]Vendita fallita: {result.reason}[/]\n"
            "[dim]Verifica con `npc inventory <character_id>` che l'oggetto "
            "sia tuo e che il negozio lo compri.[/]"
        )
        raise typer.Exit(code=1)

    table = Table(title="Vendita completata")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("base_price", str(result.base_price))
    table.add_row("quality_label", result.quality_label or "—")
    table.add_row("price_received", f"[bold]+{result.price_received}[/]")
    console.print(table)


# ---------------------------------------------------------------------------
# payday
# ---------------------------------------------------------------------------


@economy_app.command("payday")
def economy_payday(
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza un payday (per test)."""
    _require_migrated()
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        report = PaydayService.process(session, current)
        session.commit()

    table = Table(title=f"Payday @ {current}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("paid_count", str(report.paid_count))
    table.add_row("total_paid", f"{report.total_paid} Athel")
    table.add_row("character_ids", ", ".join(map(str, report.character_ids)) or "—")
    console.print(table)


# ---------------------------------------------------------------------------
# transactions / stats
# ---------------------------------------------------------------------------


@economy_app.command("transactions")
def economy_transactions(
    character_id: int | None = typer.Option(
        None, "--character", "-c", help="Filtra per character."
    ),
    kind: str | None = typer.Option(None, "--kind", "-k"),
    limit: int = typer.Option(20, "--limit", "-l", min=1, max=200),
) -> None:
    """Elenca le transazioni dal ledger (audit trail).

    Con `--character`, mostra le `JournalEntry` che hanno un posting sul
    conto `char:<id>:athel`.
    """
    _require_migrated()

    kind_enum: JournalEntryKind | None = None
    if kind is not None:
        try:
            kind_enum = JournalEntryKind(kind.upper())
        except ValueError:
            valid = ", ".join(k.value for k in JournalEntryKind)
            console.print(f"[red]Kind sconosciuto: {kind!r}[/]\n[dim]Validi: {valid}[/]")
            raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        stmt = (
            select(JournalEntry)
            .order_by(JournalEntry.at_total_seconds.desc(), JournalEntry.id.desc())
            .limit(limit)
        )
        if kind_enum is not None:
            stmt = stmt.where(JournalEntry.kind == kind_enum.value)

        if character_id is not None:
            from simai.economy.ledger.enums import character_account_code
            from simai.economy.ledger.models import Account

            acc_code = character_account_code(character_id)
            acc = session.scalars(select(Account).where(Account.code == acc_code)).first()
            if acc is None:
                console.print(f"[yellow]Nessun conto ledger per char {character_id}.[/]")
                return
            sub = select(Posting.entry_id).where(Posting.account_id == acc.id)
            stmt = stmt.where(JournalEntry.id.in_(sub))

        entries = list(session.scalars(stmt))

        rows: list[tuple[int, str, str, int, int]] = []
        for e in entries:
            postings = list(session.scalars(select(Posting).where(Posting.entry_id == e.id)))
            # Somma i posting come "amount netto" (DEBIT +, CREDIT -)
            delta = sum(
                int(p.amount) if p.direction == "DEBIT" else -int(p.amount) for p in postings
            )
            rows.append(
                (
                    e.id,
                    e.kind,
                    e.description,
                    delta,
                    len(postings),
                )
            )

    if not rows:
        console.print("[yellow]Nessuna entry.[/]")
        return

    table = Table(title=f"Journal entries ({len(rows)})")
    table.add_column("ID", style="cyan")
    table.add_column("Kind", style="yellow")
    table.add_column("Descrizione", style="magenta")
    table.add_column("Δ signed", justify="right")
    table.add_column("#post", justify="right", style="dim")
    for eid, k, desc, delta, n_post in rows:
        color = "green" if delta >= 0 else "red"
        delta_str = f"{delta:+d}"
        table.add_row(str(eid), k, desc[:60], f"[{color}]{delta_str}[/]", str(n_post))
    console.print(table)


@economy_app.command("stats")
def economy_stats() -> None:
    """Statistiche aggregate sull'economia."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        n_jobs = len(JobService.all_active_jobs(session))
        n_shops = len(
            list(session.scalars(select(Location).where(Location.type == LocationType.SHOP.value)))
        )
        n_items = len(list(session.scalars(select(ShopItem))))
        n_tx = LedgerService.entry_count(session)

        # Bilancio totale della popolazione
        total_balance = sum(
            int(c.athel_balance)
            for c in session.scalars(select(Character).where(Character.is_alive.is_(True)))
        )

        # Ripartizione per kind (dal ledger)
        from sqlalchemy import func

        by_kind: dict[str, int] = {}
        rows = session.execute(
            select(JournalEntry.kind, func.count()).group_by(JournalEntry.kind)
        ).all()
        for k, n in rows:
            by_kind[str(k)] = int(n)

    table = Table(title="SimAI — Economia: statistiche")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("active_jobs", str(n_jobs))
    table.add_row("shops", str(n_shops))
    table.add_row("shop_items", str(n_items))
    table.add_row("journal_entries_total", str(n_tx))
    table.add_row("total_balance", f"{total_balance} Athel")
    for kind, count in sorted(by_kind.items()):
        table.add_row(f"entry.{kind}", str(count))
    console.print(table)


# ---------------------------------------------------------------------------
# lot-buy / lot-sell / lots-owned / mortgages / mortgage-pay
# ---------------------------------------------------------------------------


@economy_app.command("lots-owned")
def economy_lots_owned(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Lotti posseduti da un character."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        ownerships = LotOwnershipService.owned_by(session, character_id)
        rows: list[tuple[int, str, float, int, str]] = []
        for o in ownerships:
            lot = session.get(Lot, o.lot_id)
            if lot is None:
                continue
            mortgage = MortgageService.of_lot(session, lot.id)
            mort_str = (
                f"{mortgage.remaining_principal:.0f}/{mortgage.principal}" if mortgage else "—"
            )
            rows.append(
                (
                    lot.id,
                    lot.name,
                    o.share,
                    o.purchase_price,
                    mort_str,
                )
            )

    if not rows:
        console.print(f"[yellow]{c.full_name} non possiede lotti.[/]")
        return

    table = Table(title=f"Lotti di {c.full_name}")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Share", justify="right")
    table.add_column("Prezzo", justify="right")
    table.add_column("Mutuo (res/tot)")
    for lid, name, share, price, mort in rows:
        table.add_row(str(lid), name, f"{share:.2f}", str(price), mort)
    console.print(table)


@economy_app.command("lot-buy")
def economy_lot_buy(
    character_id: int = typer.Argument(..., help="ID del compratore."),
    lot_id: int = typer.Argument(..., help="ID del lotto."),
    mortgage: bool = typer.Option(False, "--mortgage", help="Acquisto con mutuo."),
    down_payment: int = typer.Option(
        0, "--down", "-d", min=0, help="Anticipo in contanti (solo con mutuo)."
    ),
    price: int | None = typer.Option(
        None, "--price", "-p", min=0, help="Prezzo (default: current_value)."
    ),
) -> None:
    """Acquista un lotto (cash o mutuo)."""
    _require_migrated()
    start = build_starting_datetime()

    factory = get_session_factory()
    with factory() as session:
        buyer = session.get(Character, character_id)
        lot = get_lot(session, lot_id)
        if buyer is None or lot is None:
            console.print("[red]Character o lotto non trovati.[/]")
            raise typer.Exit(code=1)

        if mortgage:
            outcome = LotPurchaseService.buy_with_mortgage(
                session,
                buyer=buyer,
                lot=lot,
                current_dt=start,
                down_payment=down_payment,
                price=price,
            )
        else:
            outcome = LotPurchaseService.buy_cash(
                session,
                buyer=buyer,
                lot=lot,
                current_dt=start,
                price=price,
            )
        if outcome.ok:
            session.commit()

    if not outcome.ok:
        console.print(f"[red]Acquisto fallito: {outcome.reason}[/]")
        raise typer.Exit(code=1)

    table = Table(title="Acquisto completato")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("ownership_id", str(outcome.ownership_id))
    table.add_row(
        "mortgage_id",
        str(outcome.mortgage_id) if outcome.mortgage_id else "—",
    )
    table.add_row("cash_paid", str(outcome.cash_paid))
    console.print(table)


@economy_app.command("lot-sell")
def economy_lot_sell(
    character_id: int = typer.Argument(..., help="ID del venditore."),
    lot_id: int = typer.Argument(..., help="ID del lotto."),
    price: int | None = typer.Option(None, "--price", "-p", min=0),
) -> None:
    """Vende un lotto (deve saldare il mutuo se attivo)."""
    _require_migrated()
    start = build_starting_datetime()

    factory = get_session_factory()
    with factory() as session:
        seller = session.get(Character, character_id)
        lot = get_lot(session, lot_id)
        if seller is None or lot is None:
            console.print("[red]Character o lotto non trovati.[/]")
            raise typer.Exit(code=1)
        outcome = LotPurchaseService.sell(
            session,
            seller=seller,
            lot=lot,
            current_dt=start,
            price=price,
        )
        if outcome.ok:
            session.commit()

    if not outcome.ok:
        console.print(f"[red]Vendita fallita: {outcome.reason}[/]")
        raise typer.Exit(code=1)

    console.print(f"[green]Lotto venduto:[/] +{outcome.cash_paid} Athel")


@economy_app.command("mortgages")
def economy_mortgages(
    character_id: int | None = typer.Option(
        None, "--character", "-c", help="Filtra per character."
    ),
) -> None:
    """Elenca i mutui."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        if character_id is not None:
            mortgages = MortgageService.of_character(session, character_id)
        else:
            mortgages = MortgageService.active_mortgages(session)

        rows: list[tuple[int, str, str, float, int, int, int, str]] = []
        for m in mortgages:
            c = session.get(Character, m.character_id)
            lot = session.get(Lot, m.lot_id)
            rows.append(
                (
                    m.id,
                    c.full_name if c else "?",
                    lot.name if lot else "?",
                    m.remaining_principal,
                    m.monthly_payment,
                    m.payments_made,
                    m.payments_missed,
                    m.status,
                )
            )

    if not rows:
        console.print("[yellow]Nessun mutuo.[/]")
        return

    table = Table(title="Mutui")
    table.add_column("ID", style="cyan")
    table.add_column("Character", style="magenta")
    table.add_column("Lotto", style="green")
    table.add_column("Residuo", justify="right")
    table.add_column("Rata", justify="right")
    table.add_column("Pagate", justify="right")
    table.add_column("Mancate", justify="right", style="red")
    table.add_column("Status", style="yellow")
    for mid, cname, lname, rem, pay, made, missed, status in rows:
        table.add_row(
            str(mid),
            cname,
            lname,
            f"{rem:.0f}",
            str(pay),
            str(made),
            str(missed),
            status,
        )
    console.print(table)


@economy_app.command("mortgage-pay")
def economy_mortgage_pay(
    mortgage_id: int = typer.Argument(..., help="ID del mutuo."),
) -> None:
    """Forza il pagamento di una rata."""
    _require_migrated()
    start = build_starting_datetime()

    factory = get_session_factory()
    with factory() as session:
        m = MortgageService.get(session, mortgage_id)
        if m is None:
            console.print(f"[red]Mutuo id={mortgage_id} non trovato.[/]")
            raise typer.Exit(code=1)
        result = MortgageService.pay_installment(session, mortgage=m, current_dt=start)
        session.commit()

    table = Table(title="Pagamento rata")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("paid", str(result.paid))
    table.add_row("reason", result.reason)
    table.add_row("new_remaining", f"{result.new_remaining:.2f}")
    table.add_row("paid_off", str(result.paid_off))
    console.print(table)


@economy_app.command("property-tax")
def economy_property_tax() -> None:
    """Forza la riscossione delle tasse immobiliari."""
    _require_migrated()
    start = build_starting_datetime()

    factory = get_session_factory()
    with factory() as session:
        report = PropertyTaxService.collect_all(session, current_dt=start)
        session.commit()

    table = Table(title="Tasse proprietà")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("tassati", str(report.taxed))
    table.add_row("falliti", str(report.failed))
    table.add_row("totale", f"{report.total_collected} Athel")
    console.print(table)


@economy_app.command("real-estate-tick")
def economy_real_estate_tick(
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza un tick di decisioni immobiliari AI su tutti gli NPC (dev tool)."""
    _require_migrated()
    import random

    from sqlalchemy import select as _sel

    from simai.config.settings import get_settings
    from simai.core.time_manager import TimeManager
    from simai.npc.models import Character

    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        chars = list(session.scalars(_sel(Character).where(Character.is_alive.is_(True))))
        rng = random.Random(settings.master_seed + at_tick)
        report = RealEstateAI.daily_tick(session, chars, current_dt=current, rng=rng)
        session.commit()

    table = Table(title=f"Housing AI @ {current}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("candidates_evaluated", str(report.candidates_evaluated))
    table.add_row("events", str(len(report.events)))
    console.print(table)

    if report.events:
        ev_table = Table(title="Eventi")
        ev_table.add_column("Char", justify="right", style="cyan")
        ev_table.add_column("Azione", style="magenta")
        ev_table.add_column("Lotto", justify="right")
        ev_table.add_column("Ragione", style="green")
        ev_table.add_column("Cash", justify="right")
        for ev in report.events:
            ev_table.add_row(
                str(ev.character_id),
                ev.action.value,
                str(ev.lot_id),
                ev.reason,
                str(ev.cash_paid),
            )
        console.print(ev_table)


@economy_app.command("suppliers")
def economy_suppliers(
    type_code: str = typer.Argument(..., help="Codice tipo oggetto (es. 'sofa')."),
) -> None:
    """Mostra i fornitori di un oggetto."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        offers = SupplierService.offers_of(session, type_code)

    if not offers:
        console.print(f"[yellow]Nessun fornitore per {type_code!r}.[/]")
        return

    table = Table(title=f"Fornitori di {type_code}")
    table.add_column("Loc ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Prezzo", justify="right")
    table.add_column("Stock", justify="right")
    for offer in offers:
        stock_str = "∞" if offer.stock < 0 else str(offer.stock)
        table.add_row(
            str(offer.location_id),
            offer.location_name,
            str(offer.current_price),
            stock_str,
        )
    console.print(table)


@economy_app.command("restock")
def economy_restock() -> None:
    """Forza il restock di tutti i fornitori (dev tool)."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        n = SupplierService.restock_all(session)
        session.commit()
    console.print(f"[green]Restock completato:[/] {n} item riforniti")


@economy_app.command("supplies")
def economy_supplies() -> None:
    """Elenca le risorse del fornitore di quartiere."""
    _require_migrated()
    from sqlalchemy import select as _sel

    from simai.economy.models import ShopItem
    from simai.world.models import Location as _Loc

    factory = get_session_factory()
    with factory() as session:
        shop = session.scalars(_sel(_Loc).where(_Loc.name == "Forniture del Quartiere")).first()
        if shop is None:
            console.print("[yellow]Fornitore non trovato.[/]")
            return
        items = list(session.scalars(_sel(ShopItem).where(ShopItem.location_id == shop.id)))

    table = Table(title=f"Forniture — {shop.name}")
    table.add_column("Code", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Prezzo", justify="right")
    for it in items:
        table.add_row(it.item_type, it.item_name, str(it.current_price))
    console.print(table)


# ---------------------------------------------------------------------------
# reconcile
# ---------------------------------------------------------------------------


@economy_app.command("reconcile")
def economy_reconcile(
    character_id: int | None = typer.Option(
        None,
        "--character",
        "-c",
        help="ID character da verificare.",
    ),
    all_: bool = typer.Option(False, "--all", help="Verifica tutti i character vivi."),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Correggi i mismatch con una entry ADJUSTMENT di rettifica.",
    ),
) -> None:
    """Verifica che `athel_balance` (cache) corrisponda al saldo ledger.

    Con `--fix`, i mismatch vengono corretti con una `JournalEntry`
    di tipo `ADJUSTMENT` che allinea la cache al ledger.
    """
    _require_migrated()
    from simai.economy.ledger import JournalEntryKind, LedgerService
    from simai.npc.economy import WealthService

    if character_id is None and not all_:
        console.print("[yellow]Specifica --character ID oppure --all.[/]")
        raise typer.Exit(code=1)

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        if character_id is not None:
            c = session.get(Character, character_id)
            if c is None:
                console.print(f"[red]Character id={character_id} non trovato.[/]")
                raise typer.Exit(code=1)
            chars = [c]
        else:
            chars = list(
                session.scalars(
                    select(Character).where(Character.is_alive.is_(True)).order_by(Character.id)
                )
            )

        mismatches = 0
        fixed = 0
        table = Table(title="Reconcile ledger")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Nome", style="magenta")
        table.add_column("Cache", justify="right")
        table.add_column("Ledger", justify="right")
        table.add_column("Stato", justify="center")

        for c in chars:
            r = WealthService.reconcile(session, c)
            if not r.ok and fix:
                diff = r.cache_balance - r.ledger_balance
                WealthService.add(
                    session,
                    c,
                    diff,
                    current_dt=start,
                    kind=JournalEntryKind.ADJUSTMENT,  # ← niente alias
                    description=f"Rettifica reconcile ({diff:+d} Athel)",
                    reference_type="reconcile",
                    reference_id=c.id,
                )
                fixed += 1
                r = WealthService.reconcile(session, c)

            status = "[green]OK[/]" if r.ok else "[red]MISMATCH[/]"
            if not r.ok:
                mismatches += 1
            table.add_row(
                str(c.id),
                c.full_name,
                str(r.cache_balance),
                str(r.ledger_balance),
                status,
            )

        if fix and fixed > 0:
            session.commit()

        console.print(table)

        total = LedgerService.total_balance_check(session)
        total_color = "green" if total == 0 else "red"
        console.print(f"Ledger total balance (atteso 0): [{total_color}]{total}[/]")

        if mismatches > 0 and not fix:
            console.print(
                f"[red]{mismatches} character con mismatch.[/] [dim]Usa --fix per correggere.[/]"
            )
            raise typer.Exit(code=1)

        if fixed > 0:
            console.print(f"[green]{fixed} character corretti.[/]")
        console.print(f"[green]Reconcile completato su {len(chars)} character.[/]")


# ---------------------------------------------------------------------------
# bank
# ---------------------------------------------------------------------------

bank_app = typer.Typer(
    name="bank",
    help="Banche: conti, depositi, prestiti.",
    no_args_is_help=True,
)
economy_app.add_typer(bank_app, name="bank")


@bank_app.command("list")
def bank_list() -> None:
    """Elenca le banche attive."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        BankService.ensure_primary_bank(session)
        session.commit()
        banks = BankService.all_banks(session)

    if not banks:
        console.print("[yellow]Nessuna banca.[/]")
        return

    table = Table(title=f"Banche attive ({len(banks)})")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Code", style="dim")
    table.add_column("Nome", style="magenta")
    table.add_column("Kind", style="green")
    table.add_column("Reserve", justify="right")
    table.add_column("Dep %", justify="right")
    table.add_column("Loan %", justify="right")
    for b in banks:
        table.add_row(
            str(b.id),
            b.code,
            b.name,
            b.kind,
            f"{b.reserve_ratio:.1%}",
            f"{b.deposit_interest_rate:.2%}",
            f"{b.loan_interest_rate:.2%}",
        )
    console.print(table)


@bank_app.command("show")
def bank_show(
    code: str = typer.Option("anthal_primary", "--code", "-c", help="Codice banca."),
) -> None:
    """Dettaglio banca + saldi ledger."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        BankService.ensure_primary_bank(session)
        session.commit()
        bank = BankService.get_bank(session, code)
        if bank is None:
            console.print(f"[red]Banca {code!r} non trovata.[/]")
            raise typer.Exit(code=1)
        rec = BankService.reconcile_bank(session, bank)

    table = Table(title=f"Banca {bank.name} ({bank.code})")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("id", str(bank.id))
    table.add_row("kind", bank.kind)
    table.add_row("reserve_ratio", f"{bank.reserve_ratio:.1%}")
    table.add_row("deposit_interest_rate", f"{bank.deposit_interest_rate:.2%}")
    table.add_row("loan_interest_rate", f"{bank.loan_interest_rate:.2%}")
    table.add_row("─── ledger ───", "")
    table.add_row("reserve_ledger", str(rec.reserve_ledger))
    table.add_row("deposits_ledger", str(rec.deposits_ledger))
    table.add_row("loans_ledger", str(rec.loans_ledger))
    table.add_row("─── cache ───", "")
    table.add_row("accounts_cache_sum", str(rec.accounts_cache_sum))
    table.add_row("loans_cache_sum", str(rec.loans_cache_sum))
    status = "[green]OK[/]" if rec.ok else "[red]MISMATCH[/]"
    table.add_row("reconcile", status)
    console.print(table)


@bank_app.command("open")
def bank_open(
    character_id: int = typer.Argument(..., help="ID del character."),
    code: str = typer.Option("anthal_primary", "--code", "-c", help="Codice banca."),
    kind: str = typer.Option("CHECKING", "--kind", "-k", help="CHECKING o SAVINGS."),
) -> None:
    """Apre un conto bancario per un character."""
    _require_migrated()

    try:
        ak = BankAccountKind(kind.upper())
    except ValueError:
        console.print(f"[red]Kind sconosciuto: {kind!r}[/]")
        raise typer.Exit(code=1) from None

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        bank = BankService.get_bank(session, code)
        if bank is None:
            BankService.ensure_primary_bank(session)
            bank = BankService.get_bank(session, code)
            if bank is None:
                console.print(f"[red]Banca {code!r} non trovata.[/]")
                raise typer.Exit(code=1)
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            acc = BankService.get_or_open_account(
                session,
                character=c,
                bank=bank,
                kind=ak,
                current_dt=start,
            )
        except BankingError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()
        acc_id = acc.id
        balance = acc.balance

    console.print(
        f"[green]Conto aperto:[/] id={acc_id} char={c.full_name} "
        f"bank={bank.code} kind={ak.value} balance={balance}"
    )


@bank_app.command("accounts")
def bank_accounts(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Elenca i conti bancari di un character."""
    _require_migrated()
    from sqlalchemy import select

    from simai.economy.banking import BankAccount

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        accs = list(
            session.scalars(
                select(BankAccount)
                .where(BankAccount.character_id == character_id)
                .order_by(BankAccount.id)
            )
        )
        banks = {b.id: b for b in BankService.all_banks(session, only_active=False)}

    if not accs:
        console.print(f"[yellow]{c.full_name} non ha conti bancari.[/]")
        return

    table = Table(title=f"Conti di {c.full_name}")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Banca", style="magenta")
    table.add_column("Kind", style="green")
    table.add_column("Balance", justify="right", style="yellow")
    table.add_column("Rate", justify="right")
    table.add_column("Attivo", justify="center")
    for a in accs:
        b = banks.get(a.bank_id)
        table.add_row(
            str(a.id),
            b.code if b else f"?{a.bank_id}",
            a.kind,
            str(a.balance),
            f"{a.interest_rate:.2%}",
            "✓" if a.is_active else "✗",
        )
    console.print(table)


@bank_app.command("deposit")
def bank_deposit(
    character_id: int = typer.Argument(..., help="ID del character."),
    amount: int = typer.Argument(..., min=1, help="Athel da depositare."),
    code: str = typer.Option("anthal_primary", "--code", "-c"),
    kind: str = typer.Option("CHECKING", "--kind", "-k"),
) -> None:
    """Deposita Athel dal cash del character al conto bancario."""
    _require_migrated()

    try:
        ak = BankAccountKind(kind.upper())
    except ValueError:
        console.print(f"[red]Kind sconosciuto: {kind!r}[/]")
        raise typer.Exit(code=1) from None

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        bank = BankService.get_bank(session, code)
        if bank is None:
            console.print(f"[red]Banca {code!r} non trovata.[/]")
            raise typer.Exit(code=1)
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            acc = BankService.deposit(
                session,
                character=c,
                bank=bank,
                amount=amount,
                current_dt=start,
                kind=ak,
            )
        except BankingError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()
        new_balance = acc.balance
        new_cash = int(c.athel_balance)

    console.print(
        f"[green]Deposito:[/] {amount} Athel su conto {acc.id} "
        f"(balance={new_balance}, cash={new_cash})"
    )


@bank_app.command("withdraw")
def bank_withdraw(
    character_id: int = typer.Argument(..., help="ID del character."),
    amount: int = typer.Argument(..., min=1, help="Athel da prelevare."),
    code: str = typer.Option("anthal_primary", "--code", "-c"),
    kind: str = typer.Option("CHECKING", "--kind", "-k"),
) -> None:
    """Preleva Athel dal conto bancario al cash del character."""
    _require_migrated()

    try:
        ak = BankAccountKind(kind.upper())
    except ValueError:
        console.print(f"[red]Kind sconosciuto: {kind!r}[/]")
        raise typer.Exit(code=1) from None

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        bank = BankService.get_bank(session, code)
        if bank is None:
            console.print(f"[red]Banca {code!r} non trovata.[/]")
            raise typer.Exit(code=1)
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            acc = BankService.withdraw(
                session,
                character=c,
                bank=bank,
                amount=amount,
                current_dt=start,
                kind=ak,
            )
        except BankingError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()
        new_balance = acc.balance
        new_cash = int(c.athel_balance)

    console.print(
        f"[green]Prelievo:[/] {amount} Athel da conto {acc.id} "
        f"(balance={new_balance}, cash={new_cash})"
    )


@bank_app.command("loans")
def bank_loans(
    code: str | None = typer.Option(None, "--code", "-c", help="Filtra per banca."),
    character_id: int | None = typer.Option(None, "--character", help="Filtra per character."),
) -> None:
    """Elenca i prestiti."""
    _require_migrated()
    from sqlalchemy import select

    from simai.economy.banking import Loan

    factory = get_session_factory()
    with factory() as session:
        stmt = select(Loan).order_by(Loan.id)
        if character_id is not None:
            stmt = stmt.where(Loan.character_id == character_id)
        if code is not None:
            bank = BankService.get_bank(session, code)
            if bank is None:
                console.print(f"[red]Banca {code!r} non trovata.[/]")
                raise typer.Exit(code=1)
            stmt = stmt.where(Loan.bank_id == bank.id)
        loans = list(session.scalars(stmt))
        rows: list[tuple[int, str, str, int, float, int, int, int, int, str]] = []
        for loan in loans:
            c = session.get(Character, loan.character_id)
            bank = session.get(Bank, loan.bank_id)
            rows.append(
                (
                    loan.id,
                    c.full_name if c else "?",
                    bank.code if bank else "?",
                    loan.principal,
                    loan.remaining_principal,
                    loan.monthly_payment,
                    loan.payments_made,
                    loan.payments_missed,
                    loan.term_months,
                    loan.status,
                )
            )

    if not rows:
        console.print("[yellow]Nessun prestito.[/]")
        return

    table = Table(title=f"Prestiti ({len(rows)})")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Character", style="magenta")
    table.add_column("Bank", style="dim")
    table.add_column("Principal", justify="right")
    table.add_column("Residuo", justify="right")
    table.add_column("Rata", justify="right")
    table.add_column("Pagate", justify="right")
    table.add_column("Manc.", justify="right", style="red")
    table.add_column("Term", justify="right")
    table.add_column("Status", style="yellow")
    for r in rows:
        table.add_row(
            str(r[0]),
            r[1],
            r[2],
            str(r[3]),
            f"{r[4]:.0f}",
            str(r[5]),
            str(r[6]),
            str(r[7]),
            f"{r[8]}m",
            r[9],
        )
    console.print(table)


@bank_app.command("issue-loan")
def bank_issue_loan(
    character_id: int = typer.Argument(..., help="ID del character."),
    principal: int = typer.Argument(..., min=100, help="Athel da prestare."),
    code: str = typer.Option("anthal_primary", "--code", "-c"),
    rate: float | None = typer.Option(
        None, "--rate", "-r", min=0.0, max=1.0, help="Tasso annuale (default: banca)."
    ),
    term: int = typer.Option(24, "--term", "-t", min=1, max=360, help="Mesi."),
    collateral: int | None = typer.Option(None, "--collateral", help="ID del lotto in garanzia."),
) -> None:
    """Eroga un prestito a un character."""
    _require_migrated()

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        bank = BankService.get_bank(session, code)
        if bank is None:
            BankService.ensure_primary_bank(session)
            bank = BankService.get_bank(session, code)
            if bank is None:
                console.print(f"[red]Banca {code!r} non trovata.[/]")
                raise typer.Exit(code=1)
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            loan = BankService.issue_loan(
                session,
                character=c,
                bank=bank,
                principal=principal,
                current_dt=start,
                annual_interest_rate=rate,
                term_months=term,
                collateral_lot_id=collateral,
            )
        except BankingError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()
        loan_id = loan.id
        monthly = loan.monthly_payment
        applied_rate = loan.annual_interest_rate

    console.print(
        f"[green]Prestito erogato:[/] id={loan_id} char={c.full_name} "
        f"principal={principal} rate={applied_rate:.2%} "
        f"term={term}m rata={monthly}"
    )


@bank_app.command("pay-loan")
def bank_pay_loan(
    loan_id: int = typer.Argument(..., help="ID del prestito."),
) -> None:
    """Forza il pagamento di una rata."""
    _require_migrated()
    from simai.economy.banking import Loan

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        loan = session.get(Loan, loan_id)
        if loan is None:
            console.print(f"[red]Prestito id={loan_id} non trovato.[/]")
            raise typer.Exit(code=1)
        outcome = BankService.pay_loan_installment(session, loan=loan, current_dt=start)
        session.commit()

    table = Table(title=f"Pagamento rata #{loan_id}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("paid", str(outcome.paid))
    table.add_row("reason", outcome.reason)
    table.add_row("interest_paid", f"{outcome.interest_paid:.2f}")
    table.add_row("principal_paid", f"{outcome.principal_paid:.2f}")
    table.add_row("new_remaining", f"{outcome.new_remaining:.2f}")
    table.add_row("paid_off", str(outcome.paid_off))
    console.print(table)


@bank_app.command("monthly-tick")
def bank_monthly_tick(
    code: str | None = typer.Option(None, "--code", "-c", help="Banca specifica."),
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza un tick mensile bancario (interessi + rate prestiti)."""
    _require_migrated()
    from simai.config.settings import get_settings
    from simai.core.time_manager import TimeManager

    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        BankService.ensure_primary_bank(session)
        if code is not None:
            bank = BankService.get_bank(session, code)
            if bank is None:
                console.print(f"[red]Banca {code!r} non trovata.[/]")
                raise typer.Exit(code=1)
            banks = [bank]
        else:
            banks = BankService.all_banks(session, only_active=True)

        rows: list[tuple[str, int, int, int, int, int]] = []
        for b in banks:
            rep = BankService.monthly_tick(session, current_dt=current, bank=b)
            rows.append(
                (
                    b.code,
                    rep.interest_paid_to_depositors,
                    rep.loan_payments_succeeded,
                    rep.loan_payments_missed,
                    rep.loans_defaulted,
                    rep.loans_written_off,
                )
            )
        session.commit()

    table = Table(title=f"Banking monthly tick @ {current}")
    table.add_column("Bank", style="cyan")
    table.add_column("Interessi", justify="right", style="yellow")
    table.add_column("Rate OK", justify="right", style="green")
    table.add_column("Rate miss", justify="right", style="red")
    table.add_column("Default", justify="right", style="red")
    table.add_column("Write-off", justify="right", style="red")
    for r in rows:
        table.add_row(r[0], str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5]))
    console.print(table)


@bank_app.command("reconcile")
def bank_reconcile(
    code: str = typer.Option("anthal_primary", "--code", "-c"),
) -> None:
    """Verifica coerenza cache ↔ ledger per una banca."""
    _require_migrated()

    factory = get_session_factory()
    with factory() as session:
        BankService.ensure_primary_bank(session)
        session.commit()
        bank = BankService.get_bank(session, code)
        if bank is None:
            console.print(f"[red]Banca {code!r} non trovata.[/]")
            raise typer.Exit(code=1)
        rec = BankService.reconcile_bank(session, bank)

    table = Table(title=f"Reconcile banca {rec.bank_code}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("reserve_ledger", str(rec.reserve_ledger))
    table.add_row("deposits_ledger", str(rec.deposits_ledger))
    table.add_row("loans_ledger", str(rec.loans_ledger))
    table.add_row("accounts_cache_sum", str(rec.accounts_cache_sum))
    table.add_row("loans_cache_sum", str(rec.loans_cache_sum))
    status = "[green]OK[/]" if rec.ok else "[red]MISMATCH[/]"
    table.add_row("verdetto", status)
    console.print(table)
    if not rec.ok:
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# company
# ---------------------------------------------------------------------------

company_app = typer.Typer(
    name="company",
    help="Aziende NPC: costituzione, dipendenti, movimenti.",
    no_args_is_help=True,
)
economy_app.add_typer(company_app, name="company")


@company_app.command("list")
def company_list(
    only_active: bool = typer.Option(True, "--active/--all", help="Solo aziende attive."),
) -> None:
    """Elenca le aziende."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        companies = CompanyService.all_companies(session, only_active=only_active)
        rows: list[dict[str, object]] = []
        for c in companies:
            owner = session.get(Character, c.owner_character_id)
            n_emp = len(CompanyService.employees_of(session, c.id, only_active=True))
            rows.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "kind": c.kind,
                    "owner": owner.full_name if owner else "?",
                    "balance": c.athel_balance,
                    "n_emp": n_emp,
                    "status": c.status,
                }
            )

    if not rows:
        console.print("[yellow]Nessuna azienda.[/]")
        return

    table = Table(title=f"Aziende ({len(rows)})")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Nome", style="magenta")
    table.add_column("Kind", style="green")
    table.add_column("Owner", style="yellow")
    table.add_column("Balance", justify="right", style="blue")
    table.add_column("Emp.", justify="right")
    table.add_column("Status", style="dim")
    for r in rows:
        table.add_row(
            str(r["id"]),
            str(r["name"]),
            str(r["kind"]),
            str(r["owner"]),
            str(r["balance"]),
            str(r["n_emp"]),
            str(r["status"]),
        )
    console.print(table)


@company_app.command("show")
def company_show(
    company_id: int = typer.Argument(..., help="ID azienda."),
) -> None:
    """Dettaglio azienda: dipendenti, movimenti, riconciliazione."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Company, company_id)
        if c is None:
            console.print(f"[red]Azienda id={company_id} non trovata.[/]")
            raise typer.Exit(code=1)
        owner = session.get(Character, c.owner_character_id)
        employees = CompanyService.employees_of(session, c.id, only_active=True)
        txs = CompanyService.transactions_of(session, c.id, limit=15)
        rec = CompanyService.reconcile(session, c)

        emp_rows: list[tuple[int, str, str, int]] = []
        for emp in employees:
            ch = session.get(Character, emp.character_id)
            emp_rows.append(
                (
                    emp.character_id,
                    ch.full_name if ch else "?",
                    emp.role,
                    emp.daily_wage,
                )
            )
        tx_rows: list[tuple[int, str, int, str]] = []
        for t in txs:
            tx_rows.append((t.id, t.kind, t.amount, t.description[:60]))

    table = Table(title=f"Azienda {c.name} (id={c.id})")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("kind", c.kind)
    table.add_row("owner", owner.full_name if owner else "?")
    table.add_row("balance (cache)", str(c.athel_balance))
    table.add_row("balance (ledger)", str(rec.ledger_balance))
    table.add_row(
        "reconcile",
        "[green]OK[/]" if rec.ok else "[red]MISMATCH[/]",
    )
    table.add_row("base_daily_revenue", str(c.base_daily_revenue))
    table.add_row("base_daily_cost", str(c.base_daily_cost))
    table.add_row("status", c.status)
    console.print(table)

    if emp_rows:
        et = Table(title=f"Dipendenti ({len(emp_rows)})")
        et.add_column("Char", justify="right", style="cyan")
        et.add_column("Nome", style="magenta")
        et.add_column("Ruolo", style="green")
        et.add_column("Wage/g", justify="right")
        for cid, name, role, wage in emp_rows:
            et.add_row(str(cid), name, role, str(wage))
        console.print(et)

    if tx_rows:
        tt = Table(title="Ultimi movimenti")
        tt.add_column("ID", justify="right", style="cyan")
        tt.add_column("Kind", style="green")
        tt.add_column("Amount", justify="right")
        tt.add_column("Descrizione", style="dim")
        for tid, kind, amount, desc in tx_rows:
            color = "green" if amount >= 0 else "red"
            tt.add_row(str(tid), kind, f"[{color}]{amount:+d}[/]", desc)
        console.print(tt)


@company_app.command("create")
def company_create(
    owner_id: int = typer.Argument(..., help="ID dell'owner."),
    name: str = typer.Argument(..., help="Nome azienda."),
    kind: str = typer.Option("SHOP", "--kind", "-k"),
    location_id: int | None = typer.Option(None, "--location", "-l", help="Location aziendale."),
    capital: int | None = typer.Option(None, "--capital", "-c", min=1, help="Capitale iniziale."),
) -> None:
    """Costituisce una nuova azienda."""
    _require_migrated()
    try:
        ck = CompanyKind(kind.upper())
    except ValueError:
        valid = ", ".join(k.value for k in CompanyKind)
        console.print(f"[red]Kind non valido. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        owner = session.get(Character, owner_id)
        if owner is None:
            console.print(f"[red]Owner id={owner_id} non trovato.[/]")
            raise typer.Exit(code=1)
        try:
            company = CompanyService.create(
                session,
                owner=owner,
                name=name,
                kind=ck,
                location_id=location_id,
                initial_capital=capital,
                current_dt=start,
            )
        except CompanyError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()
        cid = company.id

    console.print(
        f"[green]Azienda creata:[/] id={cid} name={name!r} owner={owner.full_name} kind={ck.value}"
    )


@company_app.command("hire")
def company_hire(
    company_id: int = typer.Argument(..., help="ID azienda."),
    character_id: int = typer.Argument(..., help="ID del dipendente."),
    role: str = typer.Option("WORKER", "--role", "-r"),
    wage: int | None = typer.Option(
        None, "--wage", "-w", min=0, help="Stipendio/giorno (default: role)."
    ),
) -> None:
    """Assume un dipendente."""
    _require_migrated()
    from simai.economy.companies.enums import EmployeeRole

    try:
        er = EmployeeRole(role.upper())
    except ValueError:
        valid = ", ".join(r.value for r in EmployeeRole)
        console.print(f"[red]Role non valido. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Company, company_id)
        ch = session.get(Character, character_id)
        if c is None or ch is None:
            console.print("[red]Azienda o character non trovati.[/]")
            raise typer.Exit(code=1)
        try:
            emp = CompanyService.hire(
                session,
                company=c,
                employee=ch,
                role=er,
                daily_wage=wage,
                current_dt=start,
            )
        except CompanyError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()
        wage_val = emp.daily_wage

    console.print(
        f"[green]Assunto:[/] {ch.full_name} in {c.name} come {er.value} ({wage_val}/giorno)"
    )


@company_app.command("fire")
def company_fire(
    company_id: int = typer.Argument(..., help="ID azienda."),
    character_id: int = typer.Argument(..., help="ID del dipendente."),
) -> None:
    """Licenzia un dipendente."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Company, company_id)
        ch = session.get(Character, character_id)
        if c is None or ch is None:
            console.print("[red]Azienda o character non trovati.[/]")
            raise typer.Exit(code=1)
        ok = CompanyService.fire(session, company=c, employee=ch, current_dt=start)
        session.commit()

    if not ok:
        console.print("[yellow]Nessun impiego attivo da terminare.[/]")
        return
    console.print(f"[green]Licenziato:[/] {ch.full_name} da {c.name}")


@company_app.command("tick")
def company_tick(
    company_id: int | None = typer.Argument(None, help="ID azienda (tutte se omesso)."),
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Esegue un tick giornaliero per una o tutte le aziende."""
    _require_migrated()
    from simai.config.settings import get_settings
    from simai.core.time_manager import TimeManager

    settings = get_settings()
    start = build_starting_datetime()
    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        if company_id is not None:
            c = session.get(Company, company_id)
            if c is None:
                console.print(f"[red]Azienda id={company_id} non trovata.[/]")
                raise typer.Exit(code=1)
            companies = [c]
        else:
            companies = CompanyService.all_companies(session, only_active=True)

        rows: list[tuple[str, int, int, int, int, int]] = []
        for c in companies:
            rep = CompanyService.daily_tick(session, company=c, current_dt=current)
            rows.append(
                (
                    c.name,
                    rep.revenue_earned,
                    rep.operating_cost_paid,
                    rep.salaries_paid,
                    rep.dividend_paid,
                    1 if rep.declared_bankrupt else 0,
                )
            )
        session.commit()

    table = Table(title=f"Company daily tick @ {current}")
    table.add_column("Azienda", style="magenta")
    table.add_column("Ricavo", justify="right", style="green")
    table.add_column("Costi", justify="right", style="red")
    table.add_column("Stipendi", justify="right", style="yellow")
    table.add_column("Dividendi", justify="right", style="blue")
    table.add_column("Bankrupt", justify="center", style="red")
    for name, rev, cost, sal, div, bk in rows:
        table.add_row(name, str(rev), str(cost), str(sal), str(div), "✗" if bk else "")
    console.print(table)


@company_app.command("seed")
def company_seed() -> None:
    """Crea aziende demo con dipendenti (idempotente)."""
    _require_migrated()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        result = seed_demo_companies(session, current_dt=start)
        session.commit()

    if result.reason == "already_seeded":
        console.print("[yellow]Aziende già presenti — nessuna azione.[/]")
        return
    if result.reason == "no_adults":
        console.print("[red]Nessun adulto vivo nel DB.[/] [dim]Esegui prima `npc seed`.[/]")
        raise typer.Exit(code=1)
    if result.companies_created == 0:
        console.print(f"[yellow]Nessuna azienda creata (adulti trovati: {result.adults_found}).[/]")
        raise typer.Exit(code=1)

    console.print(
        f"[green]Seed aziende:[/] {result.companies_created} create, "
        f"{result.employees_hired} dipendenti assunti "
        f"(pool: {result.adults_found} adulti)"
    )


@company_app.command("reconcile")
def company_reconcile(
    company_id: int | None = typer.Argument(None, help="ID azienda (tutte se omesso)."),
) -> None:
    """Verifica coerenza cache ↔ ledger per una o tutte le aziende."""
    _require_migrated()
    factory = get_session_factory()
    with factory() as session:
        if company_id is not None:
            c = session.get(Company, company_id)
            if c is None:
                console.print(f"[red]Azienda id={company_id} non trovata.[/]")
                raise typer.Exit(code=1)
            companies = [c]
        else:
            companies = CompanyService.all_companies(session, only_active=False)

        rows: list[tuple[int, str, int, int, bool]] = []
        for c in companies:
            rec = CompanyService.reconcile(session, c)
            rows.append((c.id, c.name, rec.cache_balance, rec.ledger_balance, rec.ok))

    table = Table(title="Reconcile companies")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Cache", justify="right")
    table.add_column("Ledger", justify="right")
    table.add_column("OK", justify="center")
    for cid, name, cache, ledger, ok in rows:
        table.add_row(
            str(cid),
            name,
            str(cache),
            str(ledger),
            "[green]✓[/]" if ok else "[red]✗[/]",
        )
    console.print(table)
    if any(not r[4] for r in rows):
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# aion — registra il sottocomando
# ---------------------------------------------------------------------------

economy_app.add_typer(aion_app, name="aion")


def register(app: typer.Typer) -> None:
    """Registra il sub-app `economy` sull'app root."""
    app.add_typer(economy_app, name="economy")
