"""Comandi `npc`: gestione personaggi."""

from __future__ import annotations

import random

import typer
from rich.table import Table
from sqlalchemy import select

from simai.cli._console import console
from simai.cli._helpers import build_starting_datetime, check_migrations_applied
from simai.config.anthalys import (
    LIFESTAGE_PEDIATRIC_THRESHOLDS,
    LIFESTAGE_PSYCHOSOCIAL_THRESHOLDS,
    SECONDS_PER_DAY,
    SECONDS_PER_YEAR,
)
from simai.config.settings import get_settings
from simai.core.event_bus import EventBus
from simai.db.session import get_session_factory
from simai.npc import (
    ASPIRATION_WEIGHTS,
    INTIMACY_CATALOG,
    MAX_SKILL_LEVEL,
    OPINION_NEGATIVE_THRESHOLD,
    OPINION_POSITIVE_THRESHOLD,
    PARTIAL_THRESHOLD,
    RESOURCE_NAMES,
    STRESS_WEIGHTS,
    TRAIT_DEFS,
    TRAIT_VISIBILITY,
    ActionType,
    AddictionKind,
    AddictionService,
    AICoordinator,
    BackgroundService,
    Blackboard,
    BoredomService,
    BreakupService,
    BTActionExecutor,
    BTStatus,
    Character,
    CharacterGenerator,
    CompatibilityService,
    Condition,
    ConnectionService,
    CraftingError,
    CraftingService,
    CrisisService,
    DesireService,
    EconomyError,
    FamilyAI,
    FamilyTreeService,
    FormativeEventKind,
    GossipTopic,
    IdentityService,
    InfidelityService,
    InheritanceService,
    IntergenerationalService,
    IntimacyAction,
    IntimacyOutcome,
    IntimacyService,
    InventoryService,
    LGBTQService,
    LibidoService,
    LifecycleManager,
    LifeNarrativeService,
    LifeStageService,
    MemoryKind,
    MemoryService,
    MentorshipService,
    MoodState,
    Needs,
    NeedState,
    NeedType,
    PolyamoryService,
    Pregnancy,
    PregnancyService,
    PregnancyStatus,
    PropertyService,
    ReflectionKind,
    ReflectionService,
    Relationship,
    RelationshipKind,
    ReputationService,
    Selector,
    Sequence,
    Sex,
    SkillService,
    SkillType,
    SocialAwarenessService,
    StressService,
    SuccessionService,
    TeenDynamicsService,
    WealthService,
    action_of,
    all_recipes,
    build_bt_for_action,
    create_relationship,
    delete_relationship,
    kinship_coefficient,
    names_to_traits,
    relationship_coefficient,
    relationship_name,
    relationships_of,
    render_tree,
    seed_characters,
)
from simai.npc.ai.bt import ActionLeaf
from simai.npc.genetics import (
    LOCI_LAYOUT,
    TOTAL_ALLELES,
    TOTAL_LOCI,
    Genome,
    GenomeCategory,
    generate_from_parents,
    phenotype_from_genome,
    roll_twins,
)
from simai.npc.personality.enums import ValueAxis
from simai.npc.personality.service import PersonalityService
from simai.npc.skills import SKILL_TALENT_FAMILY
from simai.world import get_location

npc_app = typer.Typer(
    name="npc",
    help="Personaggi (Character) di Anthalys.",
    no_args_is_help=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_age(age_seconds: int) -> str:
    if age_seconds < 0:
        return "(non ancora nato)"
    years, days = LifeStageService.age_years_days(age_seconds)
    return f"{years}y {days}d"


def _age_seconds_of(character: Character, current_seconds: int) -> int:
    return current_seconds - character.birth_total_seconds


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@npc_app.command("list")
def npc_list(
    alive_only: bool = typer.Option(True, "--alive/--all", help="Solo vivi (default)."),
    at_tick: int = typer.Option(
        0,
        "--at-tick",
        "-t",
        min=0,
        help="Tick di riferimento per il calcolo dell'età (default: 0).",
    ),
) -> None:
    """Elenca i personaggi nel DB.

    L'età è calcolata al tick `--at-tick` (default: inizio simulazione).
    I personaggi con nascita successiva a quel tick sono mostrati come
    "(non ancora nato)".
    """
    if not check_migrations_applied():
        console.print("[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]")
        raise typer.Exit(code=1)

    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current_seconds = tm.current.to_total_seconds()

    factory = get_session_factory()
    with factory() as session:
        stmt = select(Character).order_by(Character.birth_total_seconds)
        if alive_only:
            stmt = stmt.where(Character.is_alive.is_(True))
        chars = list(session.scalars(stmt))

    if not chars:
        console.print("[yellow]Nessun personaggio. Esegui `npc seed`.[/]")
        return

    table = Table(title=f"SimAI — Personaggi @ tick {at_tick}")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Nome", style="magenta")
    table.add_column("Sesso", style="green")
    table.add_column("Età", justify="right")
    table.add_column("Pediatrica", style="yellow")
    table.add_column("Psicosociale", style="yellow")
    table.add_column("Vivo", justify="center")
    for c in chars:
        age = current_seconds - c.birth_total_seconds
        table.add_row(
            str(c.id),
            c.full_name,
            c.sex,
            _format_age(age),
            c.life_stage_pediatric,
            c.life_stage_psychosocial,
            "✓" if c.is_alive else "✗",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


@npc_app.command("show")
def npc_show(character_id: int = typer.Argument(..., help="ID del personaggio.")) -> None:
    """Mostra dettagli di un personaggio."""
    start = build_starting_datetime()
    current_seconds = start.to_total_seconds()

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(
                f"[red]Character id={character_id} non trovato.[/] "
                "[dim]Esegui `npc seed` se il DB è vuoto.[/]"
            )
            raise typer.Exit(code=1)

        age = _age_seconds_of(c, current_seconds)
        years, days = LifeStageService.age_years_days(age)
        exp_min, exp_max = LifeStageService.get_life_expectancy(c.sex)

        table = Table(title=f"Personaggio #{c.id} — {c.full_name}")
        table.add_column("Chiave", style="cyan", no_wrap=True)
        table.add_column("Valore", style="magenta")
        table.add_row("id", str(c.id))
        table.add_row("first_name", c.first_name)
        table.add_row("last_name", c.last_name)
        table.add_row("sex", c.sex)
        table.add_row("gender", c.gender)
        table.add_row("birth_iso", c.birth_iso)
        table.add_row("death_iso", c.death_iso or "—")
        table.add_row("is_alive", "✓" if c.is_alive else "✗")
        table.add_row("age", f"{years} anni, {days} giorni")
        table.add_row("age_seconds", str(age))
        table.add_row("life_stage_pediatric", c.life_stage_pediatric)
        table.add_row("life_stage_psychosocial", c.life_stage_psychosocial)
        table.add_row("life_expectancy", f"{exp_min}-{exp_max} anni")
        table.add_row("location_id", str(c.location_id) if c.location_id else "—")
        table.add_row("master_seed", str(c.master_seed))
        table.add_row("traits", ", ".join(c.traits_json) or "—")
        table.add_row("aspirations", ", ".join(c.aspirations_json) or "—")
        console.print(table)

        app_table = Table(title="Aspetto")
        app_table.add_column("Chiave", style="cyan", no_wrap=True)
        app_table.add_column("Valore", style="magenta")
        for k, v in sorted(c.appearance_json.items()):
            app_table.add_row(str(k), str(v))
        console.print(app_table)


# ---------------------------------------------------------------------------
# seed
# ---------------------------------------------------------------------------


def seed_npc_data(n_random: int = 4) -> tuple[int, list[Character]]:
    """Logica condivisa di seed NPC. Usata da `npc seed` e `db reset --seed`.

    Ritorna `(numero_creati, lista_character)`. Idempotente: ritorna `(0, [])`
    se il DB ha già character.
    """
    settings = get_settings()
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        created = seed_characters(
            session,
            current_datetime=start,
            master_seed=settings.master_seed,
            n_random=n_random,
        )
        session.commit()
    return len(created), created


@npc_app.command("seed")
def npc_seed(
    n_random: int = typer.Option(4, "--random", "-r", min=0, help="NPC random extra."),
) -> None:
    """Popola il DB con Erika, Max e N NPC random (idempotente)."""
    if not check_migrations_applied():
        console.print("[yellow]Database non migrato.[/] [bold]uv run python -m simai db upgrade[/]")
        raise typer.Exit(code=1)

    count, created = seed_npc_data(n_random)
    if count == 0:
        console.print("[yellow]Personaggi già presenti — nessuna azione.[/]")
        return

    console.print(f"[green]Seed completato:[/] {count} personaggi creati")
    table = Table(title="Creati")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Sesso")
    table.add_column("Birth")
    for c in created:
        table.add_row(str(c.id), c.full_name, c.sex, c.birth_iso)
    console.print(table)


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------


@npc_app.command("generate")
def npc_generate(
    n: int = typer.Option(1, "--n", "-n", min=1, help="Numero di NPC da generare."),
    persist: bool = typer.Option(True, "--save/--dry-run", help="Persisti o solo mostra."),
) -> None:
    """Genera N NPC random. Con `--dry-run` non li salva."""
    settings = get_settings()
    start = build_starting_datetime()
    gen = CharacterGenerator(master_seed=settings.master_seed)

    import random

    rng = random.Random(settings.master_seed + 999)
    created: list[Character] = []
    for _ in range(n):
        years = rng.randint(5, 70)
        days = rng.randint(0, 431)
        c = gen.generate_at_age(age_years=years, age_days=days, current_datetime=start)
        created.append(c)

    if persist:
        factory = get_session_factory()
        with factory() as session:
            for c in created:
                session.add(c)
            session.commit()

    table = Table(title=f"Generati {n} NPC{' (persistiti)' if persist else ' (dry-run)'}")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Sesso")
    table.add_column("Birth")
    table.add_column("Pediatrica")
    for c in created:
        table.add_row(
            str(c.id) if c.id else "—",
            c.full_name,
            c.sex,
            c.birth_iso,
            c.life_stage_pediatric,
        )
    console.print(table)


# ---------------------------------------------------------------------------
# stages
# ---------------------------------------------------------------------------


@npc_app.command("stages")
def npc_stages() -> None:
    """Mostra le soglie delle fasce di età."""

    def _format(years: int, days: int) -> str:
        return f"{years}y {days}d"

    ped_table = Table(title="Fasce pediatriche")
    ped_table.add_column("Fascia", style="cyan")
    ped_table.add_column("Soglia (Anthalys)", style="magenta")
    for name, secs in sorted(LIFESTAGE_PEDIATRIC_THRESHOLDS.items(), key=lambda kv: kv[1]):
        years, rem = divmod(secs, SECONDS_PER_YEAR)
        days = rem // SECONDS_PER_DAY
        ped_table.add_row(name, _format(years, days))
    console.print(ped_table)

    psy_table = Table(title="Fasce psicosociali")
    psy_table.add_column("Fascia", style="cyan")
    psy_table.add_column("Soglia (Anthalys)", style="magenta")
    for name, secs in sorted(LIFESTAGE_PSYCHOSOCIAL_THRESHOLDS.items(), key=lambda kv: kv[1]):
        years, rem = divmod(secs, SECONDS_PER_YEAR)
        days = rem // SECONDS_PER_DAY
        psy_table.add_row(name, _format(years, days))
    console.print(psy_table)


# ---------------------------------------------------------------------------
# age
# ---------------------------------------------------------------------------


@npc_app.command("age")
def npc_age(
    character_id: int = typer.Argument(..., help="ID del personaggio."),
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Calcola età e fasce a un certo tick della simulazione."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Personaggio id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)

        age = LifeStageService.age_seconds_at(c.birth_total_seconds, current)
        ped = LifeStageService.get_pediatric_stage(age)
        psy = LifeStageService.get_psychosocial_stage(age)

    years, days = LifeStageService.age_years_days(age)
    table = Table(title=f"Età di {c.full_name} @ {current}")
    table.add_column("Chiave", style="cyan", no_wrap=True)
    table.add_column("Valore", style="magenta")
    table.add_row("at_tick", str(at_tick))
    table.add_row("datetime", str(current))
    table.add_row("age", f"{years} anni, {days} giorni")
    table.add_row("age_seconds", str(age))
    table.add_row("pediatric", str(ped))
    table.add_row("psychosocial", str(psy))
    console.print(table)


# ---------------------------------------------------------------------------
# genome
# ---------------------------------------------------------------------------


@npc_app.command("genome")
def npc_genome(
    character_id: int = typer.Argument(..., help="ID del personaggio."),
    category: str = typer.Option("all", "--category", "-c", help="Categoria da mostrare o 'all'."),
    summary_only: bool = typer.Option(
        False, "--summary/--detail", help="Solo punteggi poligenici."
    ),
) -> None:
    """Ispeziona il genoma di un personaggio."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Personaggio id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        if not c.genome_json:
            console.print(
                f"[yellow]Personaggio #{c.id} non ha genoma (creato prima di Chunk 3.1).[/]"
            )
            raise typer.Exit(code=1)
        genome = Genome.from_dict(c.genome_json)

    if summary_only:
        table = Table(title=f"Genoma #{c.id} — {c.full_name} (riepilogo)")
        table.add_column("Categoria", style="cyan")
        table.add_column("Loci", justify="right")
        table.add_column("Score", justify="right")
        for cat in GenomeCategory:
            start, end = LOCI_LAYOUT[cat]
            score = genome.polygenic_score(cat)
            table.add_row(str(cat), f"{start}-{end}", f"{score:.3f}")
        console.print(table)
        console.print(f"[dim]Totale: {TOTAL_LOCI} loci × 2 = {TOTAL_ALLELES} alleli[/]")
        return

    if category == "all":
        table = Table(title=f"Genoma #{c.id} — {c.full_name}")
        table.add_column("Categoria", style="cyan")
        table.add_column("Loci", justify="right")
        table.add_column("Score", justify="right")
        for cat in GenomeCategory:
            start, end = LOCI_LAYOUT[cat]
            score = genome.polygenic_score(cat)
            table.add_row(str(cat), f"{start}-{end}", f"{score:.3f}")
        console.print(table)
        return

    # Mostra loci specifici di una categoria
    try:
        cat_enum = GenomeCategory(category.upper())
    except ValueError:
        console.print(f"[red]Categoria sconosciuta: {category!r}[/]")
        raise typer.Exit(code=1) from None

    start, end = LOCI_LAYOUT[cat_enum]
    table = Table(title=f"Genoma #{c.id} — {cat_enum}")
    table.add_column("Locus", style="cyan")
    table.add_column("Allele A", justify="right")
    table.add_column("Allele B", justify="right")
    for i in range(start, min(end, start + 40)):  # limite 40 righe per output
        a, b = genome.loci[i]
        table.add_row(str(i), str(a), str(b))
    console.print(table)
    if end - start > 40:
        console.print(f"[dim]... e altri {end - start - 40} loci[/]")


# ---------------------------------------------------------------------------
# phenotype
# ---------------------------------------------------------------------------


@npc_app.command("phenotype")
def npc_phenotype(
    character_id: int = typer.Argument(..., help="ID del personaggio."),
) -> None:
    """Mostra il fenotipo (aspetto) di un personaggio."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Personaggio id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        appearance = c.appearance_json

    table = Table(title=f"Fenotipo #{c.id} — {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    for k, v in sorted(appearance.items()):
        if k == "polygenic_scores":
            continue
        table.add_row(k, str(v))
    console.print(table)

    scores = appearance.get("polygenic_scores", {})
    if scores:
        st = Table(title="Punteggi poligenici")
        st.add_column("Tratto", style="cyan")
        st.add_column("Score", justify="right")
        for k, v in sorted(scores.items()):
            st.add_row(k, f"{float(v):.3f}")
        console.print(st)


# ---------------------------------------------------------------------------
# breed (test ereditarietà)
# ---------------------------------------------------------------------------


@npc_app.command("breed")
def npc_breed(
    father_id: int = typer.Argument(..., help="ID del padre."),
    mother_id: int = typer.Argument(..., help="ID della madre."),
    seed: int | None = typer.Option(None, "--seed", help="Seed RNG (default: master)."),
    dry_run: bool = typer.Option(True, "--dry-run/--save", help="Solo mostra (default) o salva."),
) -> None:
    """Simula una nascita da due genitori e mostra il genoma del figlio."""
    settings = get_settings()
    rng = random.Random(seed if seed is not None else settings.master_seed)

    factory = get_session_factory()
    with factory() as session:
        father = session.get(Character, father_id)
        mother = session.get(Character, mother_id)
        if father is None or mother is None:
            console.print("[red]Padre o madre non trovati.[/]")
            raise typer.Exit(code=1)

        father_g = Genome.from_dict(father.genome_json)
        mother_g = Genome.from_dict(mother.genome_json)
        child_g = generate_from_parents(father_g, mother_g, rng)

        # Fenotipo (sesso casuale per ora)
        child_sex = rng.choice([Sex.MALE, Sex.FEMALE])
        appearance = phenotype_from_genome(child_g, child_sex)

        is_twin, identical = roll_twins(rng)
        twin_info = ""
        if is_twin:
            twin_g = child_g if identical else generate_from_parents(father_g, mother_g, rng)
            twin_info = (
                f"gemelli {'identici' if identical else 'fraterni'} "
                f"(score gemello: {twin_g.polygenic_score(GenomeCategory.APPEARANCE_HEIGHT):.3f})"
            )

        # Persist (opzionale)
        if not dry_run:
            start = build_starting_datetime()
            gen = CharacterGenerator(master_seed=settings.master_seed)
            child = gen.generate(
                birth_datetime=start,
                current_datetime=start,
                sex=child_sex,
                genome=child_g,
                parents=(father, mother),
            )
            session.add(child)
            session.commit()
            console.print(f"[green]Figlio creato:[/] id={child.id} {child.full_name}")

    table = Table(title="Figlio (fenotipo)")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    for k, v in sorted(appearance.items()):
        if k == "polygenic_scores":
            continue
        table.add_row(k, str(v))
    console.print(table)

    if twin_info:
        console.print(f"[yellow]Nota:[/] {twin_info}")


# ---------------------------------------------------------------------------
# needs
# ---------------------------------------------------------------------------


def _ensure_initial_state(c: Character) -> None:
    """Inizializza needs/mood se il personaggio è stato creato prima del Chunk 3.2."""
    if not c.needs_json:
        c.needs_json = Needs.default().to_dict()
    if not c.mood_json:
        c.mood_json = MoodState.default().to_dict()


@npc_app.command("needs")
def npc_needs(character_id: int = typer.Argument(..., help="ID del personaggio.")) -> None:
    """Mostra bisogni e umore di un personaggio."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Personaggio id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        _ensure_initial_state(c)
        session.commit()

        needs = Needs.from_dict(c.needs_json)
        mood = MoodState.from_dict(c.mood_json)

    # Tabella bisogni
    table = Table(title=f"Bisogni di {c.full_name} (id={c.id})")
    table.add_column("Bisogno", style="cyan")
    table.add_column("Valore", justify="right")
    table.add_column("Stato", style="magenta")
    for need in NeedType:
        value = needs.get(need)
        state = needs.state(need)
        color = {
            NeedState.CRITICAL: "red",
            NeedState.LOW: "yellow",
            NeedState.OK: "white",
            NeedState.HIGH: "green",
        }.get(state, "white")
        table.add_row(need.value, f"{value:.1f}", f"[{color}]{state.value}[/]")
    console.print(table)

    # Umore
    mood_table = Table(title="Umore")
    mood_table.add_column("Chiave", style="cyan")
    mood_table.add_column("Valore", style="magenta")
    mood_table.add_row("happiness", f"{mood.happiness:.3f}")
    for m in mood.moodlets:
        mood_table.add_row(m.name, f"{m.happiness_delta:+.2f} ({m.remaining_ticks} tick)")
    console.print(mood_table)


# ---------------------------------------------------------------------------
# tick
# ---------------------------------------------------------------------------


@npc_app.command("tick")
def npc_tick(
    character_id: int = typer.Argument(..., help="ID del personaggio."),
    ticks: int = typer.Option(1, "--ticks", "-n", min=1),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    use_bt: bool = typer.Option(
        False,
        "--bt/--no-bt",
        help="Usa il Behaviour Tree per eseguire le azioni.",
    ),
) -> None:
    """Avanza di N tick un singolo personaggio (decay bisogni + AI)."""
    settings = get_settings()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Personaggio id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        _ensure_initial_state(c)

        coord = AICoordinator(
            seed=settings.master_seed + c.id,
            bt_executor=BTActionExecutor() if use_bt else None,
        )
        needs = Needs.from_dict(c.needs_json)
        mood = MoodState.from_dict(c.mood_json)
        traits = names_to_traits(c.traits_json)

        start_tick = c.last_ai_tick
        actions_started = 0
        for i in range(ticks):
            result = coord.tick(needs, mood, traits)
            needs = result.needs
            mood = result.mood
            if result.action_started is not None:
                actions_started += 1
                if verbose:
                    console.print(
                        f"[dim]tick {start_tick + i + 1}: inizio {result.action_started.label}[/]"
                    )
            if verbose and result.new_moodlets:
                for m in result.new_moodlets:
                    console.print(f"[yellow]+moodlet {m.name}[/]")

        c.needs_json = needs.to_dict()
        c.mood_json = mood.to_dict()
        c.current_action_json = (
            coord.current_progress.to_dict() if coord.current_progress is not None else None
        )
        c.last_ai_tick = start_tick + ticks
        session.commit()

    table = Table(title=f"Tick su {c.full_name} ({ticks}, bt={use_bt})")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("tick_range", f"{start_tick + 1}..{start_tick + ticks}")
    table.add_row("actions_started", str(actions_started))
    table.add_row("happiness", f"{mood.happiness:.3f}")
    table.add_row(
        "current_action",
        coord.current_progress.action.label if coord.current_progress is not None else "—",
    )
    console.print(table)


# ---------------------------------------------------------------------------
# autoplay
# ---------------------------------------------------------------------------


@npc_app.command("autoplay")
def npc_autoplay(
    character_id: int = typer.Argument(..., help="ID del personaggio."),
    ticks: int = typer.Option(500, "--ticks", "-n", min=1),
    trace_every: int = typer.Option(
        0, "--trace-every", help="Stampa ogni N tick (0 = disabilitato)."
    ),
    use_bt: bool = typer.Option(
        False,
        "--bt/--no-bt",
        help="Usa il Behaviour Tree.",
    ),
) -> None:
    """Avanza di N tick mostrando l'evoluzione."""
    settings = get_settings()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Personaggio id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        _ensure_initial_state(c)

        coord = AICoordinator(
            seed=settings.master_seed + c.id,
            bt_executor=BTActionExecutor() if use_bt else None,
        )
        needs = Needs.from_dict(c.needs_json)
        mood = MoodState.from_dict(c.mood_json)
        traits = names_to_traits(c.traits_json)

        rows: list[tuple[int, str, str]] = []
        for i in range(ticks):
            result = coord.tick(needs, mood, traits)
            needs = result.needs
            mood = result.mood
            if trace_every > 0 and (i + 1) % trace_every == 0:
                current_action = (
                    result.action_progress.action.label
                    if result.action_progress is not None
                    else "—"
                )
                critical = ",".join(n.value for n in needs.critical_needs()) or "—"
                rows.append((i + 1, current_action, f"h={mood.happiness:.2f} crit={critical}"))

        c.needs_json = needs.to_dict()
        c.mood_json = mood.to_dict()
        c.current_action_json = (
            coord.current_progress.to_dict() if coord.current_progress is not None else None
        )
        c.last_ai_tick += ticks
        session.commit()

    if rows:
        table = Table(title=f"Autoplay {c.full_name} ({ticks} tick, bt={use_bt})")
        table.add_column("Tick", justify="right")
        table.add_column("Azione", style="cyan")
        table.add_column("Stato", style="magenta")
        for tick, action, st in rows:
            table.add_row(str(tick), action, st)
        console.print(table)
    else:
        console.print(f"[green]Autoplay completato[/]: {ticks} tick")

    console.print(
        f"[green]Finale:[/] happiness={mood.happiness:.3f}, "
        f"critici={[n.value for n in needs.critical_needs()]}"
    )


# ---------------------------------------------------------------------------
# traits
# ---------------------------------------------------------------------------


@npc_app.command("traits")
def npc_traits(
    character_id: int = typer.Argument(..., help="ID del personaggio."),
    show_modifiers: bool = typer.Option(
        False, "--modifiers", help="Mostra i modificatori di utility."
    ),
) -> None:
    """Mostra i tratti e l'aspirazione di un personaggio."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Personaggio id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        traits = names_to_traits(c.traits_json)
        aspiration_names = c.aspirations_json
        mask_name = c.attributes_json.get("mask_trait")

    table = Table(title=f"Tratti di {c.full_name} (id={c.id})")
    table.add_column("Tratto", style="cyan")
    table.add_column("Categoria", style="yellow")
    table.add_column("Famiglia", style="green")
    table.add_column("Maschera", justify="center")
    for t in sorted(traits, key=lambda t: t.value):
        tdef = TRAIT_DEFS.get(t)
        if tdef is None:
            table.add_row(t.value, "?", "?", "?")
            continue
        is_mask = "✓" if (mask_name and t.value == mask_name) else ""
        table.add_row(t.value, tdef.category.value, tdef.family.value, is_mask)
    console.print(table)

    if show_modifiers:
        mod_table = Table(title="Modificatori di utility")
        mod_table.add_column("Tratto", style="cyan")
        mod_table.add_column("Azione", style="magenta")
        mod_table.add_column("Δ", justify="right")
        for t in sorted(traits, key=lambda t: t.value):
            tdef = TRAIT_DEFS.get(t)
            if tdef is None:
                continue
            for action, mod in sorted(tdef.utility_modifiers.items(), key=lambda kv: kv[0].value):
                mod_table.add_row(t.value, action.value, f"{mod:+.2f}")
        console.print(mod_table)

    asp_table = Table(title="Aspirazione")
    asp_table.add_column("Chiave", style="cyan")
    asp_table.add_column("Valore", style="magenta")
    asp_table.add_row("aspiration", ", ".join(aspiration_names) or "—")
    asp_table.add_row("mask_trait", str(mask_name) if mask_name else "—")
    console.print(asp_table)


@npc_app.command("traits-catalog")
def npc_traits_catalog() -> None:
    """Mostra il catalogo completo dei tratti e delle aspirazioni."""
    table = Table(title=f"Catalogo tratti ({len(TRAIT_DEFS)})")
    table.add_column("Tratto", style="cyan")
    table.add_column("Categoria", style="yellow")
    table.add_column("Famiglia", style="green")
    table.add_column("Soglia", justify="right")
    table.add_column("Modifiers")
    for t in sorted(TRAIT_DEFS.keys(), key=lambda t: t.value):
        tdef = TRAIT_DEFS[t]
        mods = ",".join(f"{a.value}{m:+.2f}" for a, m in tdef.utility_modifiers.items()) or "—"
        table.add_row(
            t.value,
            tdef.category.value,
            tdef.family.value,
            f"{tdef.min_score:.2f}",
            mods,
        )
    console.print(table)

    asp_table = Table(title="Pesi aspirazione")
    asp_table.add_column("Aspirazione", style="cyan")
    asp_table.add_column("Tratti pesati", style="magenta")
    for aspiration, weights in ASPIRATION_WEIGHTS.items():
        weights_str = ", ".join(f"{t.value}×{w:.1f}" for t, w in sorted(weights.items()))
        asp_table.add_row(aspiration.value, weights_str or "—")
    console.print(asp_table)


# ---------------------------------------------------------------------------
# relate / unrelate
# ---------------------------------------------------------------------------


@npc_app.command("relate")
def npc_relate(
    from_id: int = typer.Argument(..., help="ID del primo character."),
    to_id: int = typer.Argument(..., help="ID del secondo character."),
    kind: str = typer.Argument(..., help="Tipo relazione (vedi `npc relationship-kinds`)."),
    strength: float = typer.Option(0.5, "--strength", "-s", min=0.0, max=1.0),
) -> None:
    """Crea una relazione tra due character."""
    try:
        kind_enum = RelationshipKind(kind.upper())
    except ValueError:
        console.print(
            f"[red]Tipo relazione sconosciuto: {kind!r}. "
            f"Usa `npc relationship-kinds` per la lista.[/]"
        )
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    try:
        with factory() as session:
            created = create_relationship(
                session,
                from_id=from_id,
                to_id=to_id,
                kind=kind_enum,
                strength=strength,
            )
            session.commit()
    except Exception as exc:
        console.print(f"[red]Errore: {exc}[/]")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Creata relazione[/] {kind_enum.value} "
        f"{from_id}->{to_id} ({len(created)} righe, strength={strength:.2f})"
    )


@npc_app.command("unrelate")
def npc_unrelate(
    from_id: int = typer.Argument(..., help="ID del primo character."),
    to_id: int = typer.Argument(..., help="ID del secondo character."),
    kind: str = typer.Argument(..., help="Tipo relazione."),
) -> None:
    """Elimina una relazione tra due character."""
    try:
        kind_enum = RelationshipKind(kind.upper())
    except ValueError:
        console.print(f"[red]Tipo relazione sconosciuto: {kind!r}.[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        deleted = delete_relationship(session, from_id=from_id, to_id=to_id, kind=kind_enum)
        session.commit()

    if deleted == 0:
        console.print(f"[yellow]Nessuna relazione {kind_enum.value} {from_id}->{to_id} trovata.[/]")
        return
    console.print(f"[green]Eliminate {deleted} righe.[/]")


# ---------------------------------------------------------------------------
# relationships
# ---------------------------------------------------------------------------


@npc_app.command("relationships")
def npc_relationships(
    character_id: int = typer.Argument(..., help="ID del character."),
    kind: str | None = typer.Option(None, "--kind", "-k", help="Filtra per tipo."),
) -> None:
    """Elenca le relazioni di un character."""
    kind_enum: RelationshipKind | None = None
    if kind is not None:
        try:
            kind_enum = RelationshipKind(kind.upper())
        except ValueError:
            console.print(f"[red]Tipo relazione sconosciuto: {kind!r}.[/]")
            raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        rels = relationships_of(session, character_id, kind=kind_enum)
        from simai.npc.models import Character

        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)

        # Preload dei nomi per velocità
        ids = [r.to_id for r in rels]
        chars = (
            {ch.id: ch for ch in session.query(Character).filter(Character.id.in_(ids)).all()}
            if ids
            else {}
        )

    if not rels:
        console.print(f"[yellow]Nessuna relazione per {c.full_name}.[/]")
        return

    table = Table(title=f"Relazioni di {c.full_name} (id={c.id})")
    table.add_column("Tipo", style="cyan")
    table.add_column("Con", style="magenta")
    table.add_column("ID", justify="right")
    table.add_column("Strength", justify="right")
    for r in rels:
        other = chars.get(r.to_id)
        name = other.full_name if other else f"<id={r.to_id}>"
        table.add_row(r.kind, name, str(r.to_id), f"{r.strength:.2f}")
    console.print(table)


# ---------------------------------------------------------------------------
# family
# ---------------------------------------------------------------------------


@npc_app.command("family")
def npc_family(character_id: int = typer.Argument(..., help="ID del character.")) -> None:
    """Mostra genitori, figli e fratelli di un character."""
    factory = get_session_factory()
    with factory() as session:
        from simai.npc.models import Character

        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)

        parents = FamilyTreeService.parents_of(session, character_id)
        children = FamilyTreeService.children_of(session, character_id)
        siblings = FamilyTreeService.siblings_of(session, character_id)

    def _render(title: str, chars: list[Character]) -> None:
        if not chars:
            console.print(f"[dim]{title}: nessuno[/]")
            return
        t = Table(title=title)
        t.add_column("ID", style="cyan")
        t.add_column("Nome", style="magenta")
        t.add_column("Sesso")
        for ch in chars:
            t.add_row(str(ch.id), ch.full_name, ch.sex)
        console.print(t)

    console.print(f"[bold]{c.full_name}[/] (id={c.id})")
    _render("Genitori", parents)
    _render("Figli", children)
    _render("Fratelli/Sorelle", siblings)


# ---------------------------------------------------------------------------
# ancestors / descendants
# ---------------------------------------------------------------------------


@npc_app.command("ancestors")
def npc_ancestors(
    character_id: int = typer.Argument(..., help="ID del character."),
    max_gen: int = typer.Option(5, "--max-gen", min=1, max=10),
) -> None:
    """Elenca gli antenati di un character."""
    factory = get_session_factory()
    with factory() as session:
        from simai.npc.models import Character

        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)

        anc = FamilyTreeService.ancestors_of(session, character_id, max_gen=max_gen)
        if not anc:
            console.print(f"[yellow]Nessun antenato per {c.full_name}.[/]")
            return
        chars = {
            ch.id: ch
            for ch in session.query(Character).filter(Character.id.in_(list(anc.keys()))).all()
        }

    table = Table(title=f"Antenati di {c.full_name} (max {max_gen} gen.)")
    table.add_column("Gen", justify="right")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    for aid, dist in sorted(anc.items(), key=lambda x: (x[1], x[0])):
        ch = chars.get(aid)
        table.add_row(str(dist), str(aid), ch.full_name if ch else f"<id={aid}>")
    console.print(table)


@npc_app.command("descendants")
def npc_descendants(
    character_id: int = typer.Argument(..., help="ID del character."),
    max_gen: int = typer.Option(5, "--max-gen", min=1, max=10),
) -> None:
    """Elenca i discendenti di un character."""
    factory = get_session_factory()
    with factory() as session:
        from simai.npc.models import Character

        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)

        desc = FamilyTreeService.descendants_of(session, character_id, max_gen=max_gen)
        if not desc:
            console.print(f"[yellow]Nessun discendente per {c.full_name}.[/]")
            return
        chars = {
            ch.id: ch
            for ch in session.query(Character).filter(Character.id.in_(list(desc.keys()))).all()
        }

    table = Table(title=f"Discendenti di {c.full_name} (max {max_gen} gen.)")
    table.add_column("Gen", justify="right")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    for aid, dist in sorted(desc.items(), key=lambda x: (x[1], x[0])):
        ch = chars.get(aid)
        table.add_row(str(dist), str(aid), ch.full_name if ch else f"<id={aid}>")
    console.print(table)


# ---------------------------------------------------------------------------
# kinship
# ---------------------------------------------------------------------------


@npc_app.command("kinship")
def npc_kinship(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
    max_gen: int = typer.Option(6, "--max-gen", min=1, max=10),
) -> None:
    """Calcola il grado di parentela tra due character."""
    factory = get_session_factory()
    with factory() as session:
        from simai.npc.models import Character

        a = session.get(Character, a_id)
        b = session.get(Character, b_id)
        if a is None or b is None:
            console.print("[red]Uno dei due character non esiste.[/]")
            raise typer.Exit(code=1)

        r = relationship_coefficient(session, a_id, b_id, max_gen=max_gen)
        phi = kinship_coefficient(session, a_id, b_id, max_gen=max_gen)
        name = relationship_name(session, a_id, b_id, max_gen=max_gen)

    table = Table(title=f"Parentela: {a.full_name} ↔ {b.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("a", f"{a.full_name} (id={a_id})")
    table.add_row("b", f"{b.full_name} (id={b_id})")
    table.add_row("relazione (da a)", name)
    table.add_row("coefficiente r", f"{r:.4f}")
    table.add_row("coefficiente Φ", f"{phi:.4f}")
    console.print(table)


# ---------------------------------------------------------------------------
# relationship-kinds
# ---------------------------------------------------------------------------


@npc_app.command("relationship-kinds")
def npc_relationship_kinds() -> None:
    """Mostra l'elenco dei tipi di relazione disponibili."""
    table = Table(title="Tipi di relazione")
    table.add_column("Kind", style="cyan")
    table.add_column("Simmetrica", justify="center")
    table.add_column("Famiglia", justify="center")
    for k in RelationshipKind:
        table.add_row(k.value, "✓" if k.is_symmetric else "", "✓" if k.is_family else "")
    console.print(table)


# ---------------------------------------------------------------------------
# conceive
# ---------------------------------------------------------------------------


def _build_lifecycle() -> LifecycleManager:
    settings = get_settings()
    return LifecycleManager(
        session_factory=get_session_factory(),
        event_bus=EventBus(),
        seed=settings.master_seed + 1,
        master_seed=settings.master_seed,
    )


@npc_app.command("conceive")
def npc_conceive(
    mother_id: int = typer.Argument(..., help="ID della madre."),
    father_id: int = typer.Argument(..., help="ID del padre."),
    probability: float = typer.Option(
        0.10,
        "--probability",
        "-p",
        min=0.0,
        max=1.0,
        help="Probabilità di successo (0-1).",
    ),
) -> None:
    """Tenta un concepimento tra due character fertili."""
    start = build_starting_datetime()
    lifecycle = _build_lifecycle()
    pid = lifecycle.conceive(
        mother_id=mother_id,
        father_id=father_id,
        current_dt=start,
        probability=probability,
    )
    if pid is None:
        console.print("[yellow]Concepimento fallito (vedi log).[/]")
        return
    console.print(
        f"[green]Gravidanza creata:[/] pregnancy_id={pid} (madre={mother_id}, padre={father_id})"
    )


# ---------------------------------------------------------------------------
# pregnancies
# ---------------------------------------------------------------------------


@npc_app.command("pregnancies")
def npc_pregnancies(
    active_only: bool = typer.Option(True, "--active/--all", help="Solo gravidanze attive."),
) -> None:
    """Elenca le gravidanze."""
    factory = get_session_factory()
    with factory() as session:
        stmt = select(Pregnancy).order_by(Pregnancy.id)
        if active_only:
            stmt = stmt.where(Pregnancy.status == PregnancyStatus.ACTIVE.value)
        pregs = list(session.scalars(stmt))

    if not pregs:
        console.print("[yellow]Nessuna gravidanza.[/]")
        return

    table = Table(title="SimAI — Gravidanze")
    table.add_column("ID", style="cyan")
    table.add_column("Madre", justify="right")
    table.add_column("Padre", justify="right")
    table.add_column("Concezione", style="green")
    table.add_column("Due", style="magenta")
    table.add_column("Status", style="yellow")
    table.add_column("Figli", style="blue")
    for p in pregs:
        table.add_row(
            str(p.id),
            str(p.mother_id),
            str(p.father_id) if p.father_id else "—",
            str(p.conception_total_seconds),
            str(p.due_total_seconds),
            p.status,
            ",".join(str(c) for c in (p.child_ids_json or [])) or "—",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# deliver
# ---------------------------------------------------------------------------


@npc_app.command("deliver")
def npc_deliver(
    pregnancy_id: int = typer.Argument(..., help="ID della gravidanza."),
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza il parto di una gravidanza (solo se già dovuta)."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    import random

    with factory() as session:
        preg = session.get(Pregnancy, pregnancy_id)
        if preg is None:
            console.print(f"[red]Gravidanza id={pregnancy_id} non trovata.[/]")
            raise typer.Exit(code=1)

        children = PregnancyService.advance(
            session,
            preg,
            current,
            random.Random(settings.master_seed),
            master_seed=settings.master_seed,
        )
        session.commit()

    if not children:
        console.print("[yellow]Nessun parto: non ancora dovuta o già completata.[/]")
        return

    table = Table(title="Nati")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Sesso")
    for c in children:
        table.add_row(str(c.id), c.full_name, c.sex)
    console.print(table)


# ---------------------------------------------------------------------------
# kill
# ---------------------------------------------------------------------------


@npc_app.command("kill")
def npc_kill(
    character_id: int = typer.Argument(..., help="ID del character."),
    cause: str = typer.Option("UNKNOWN", "--cause", "-c"),
) -> None:
    """Registra la morte di un character (dev tool)."""
    start = build_starting_datetime()
    lifecycle = _build_lifecycle()
    ok = lifecycle.kill(character_id, start, cause)
    if not ok:
        console.print("[yellow]Morte non applicata (char assente o già morto).[/]")
        return
    console.print(f"[green]Morte registrata:[/] id={character_id} cause={cause}")


# ---------------------------------------------------------------------------
# lifecycle-tick
# ---------------------------------------------------------------------------


@npc_app.command("lifecycle-tick")
def npc_lifecycle_tick(
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza un tick di lifecycle (aging + mortalità + gravidanze)."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    lifecycle = _build_lifecycle()
    report = lifecycle.force_daily_work(current)

    table = Table(title=f"Lifecycle tick @ {current}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("daily_work_done", str(report.daily_work_done))
    table.add_row("dead_ids", ", ".join(map(str, report.dead_ids)) or "—")
    table.add_row("birth_ids", ", ".join(map(str, report.birth_ids)) or "—")
    table.add_row(
        "pregnancy_completed",
        ", ".join(map(str, report.pregnancy_completed_ids)) or "—",
    )
    table.add_row("age_transitions", str(len(report.age_transitions)))
    console.print(table)


# ---------------------------------------------------------------------------
# couples
# ---------------------------------------------------------------------------


@npc_app.command("couples")
def npc_couples(
    min_strength: float = typer.Option(0.0, "--min-strength", "-s", min=0.0, max=1.0),
) -> None:
    """Elenca le coppie (SPOUSE_OF / PARTNER_OF)."""
    kinds = (RelationshipKind.SPOUSE_OF.value, RelationshipKind.PARTNER_OF.value)
    factory = get_session_factory()
    with factory() as session:
        rows = list(
            session.scalars(
                select(Relationship).where(
                    Relationship.kind.in_(kinds),
                    Relationship.from_id < Relationship.to_id,
                    Relationship.strength >= min_strength,
                )
            )
        )
        pairs = []
        for r in rows:
            a = session.get(Character, r.from_id)
            b = session.get(Character, r.to_id)
            if a is None or b is None:
                continue
            pairs.append((r, a, b))

    if not pairs:
        console.print("[yellow]Nessuna coppia.[/]")
        return

    table = Table(title="Coppie")
    table.add_column("Kind", style="cyan")
    table.add_column("A", style="magenta")
    table.add_column("B", style="magenta")
    table.add_column("Strength", justify="right")
    table.add_column("Vivi", justify="center")
    for r, a, b in pairs:
        alive = "✓" if (a.is_alive and b.is_alive) else "✗"
        table.add_row(r.kind, a.full_name, b.full_name, f"{r.strength:.2f}", alive)
    console.print(table)


# ---------------------------------------------------------------------------
# try-conceive
# ---------------------------------------------------------------------------


@npc_app.command("try-conceive")
def npc_try_conceive(
    mother_id: int = typer.Argument(..., help="ID della madre."),
    father_id: int = typer.Argument(..., help="ID del padre."),
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza una valutazione della Family AI e ritorna l'esito (con eventuale Pregnancy)."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        mother = session.get(Character, mother_id)
        father = session.get(Character, father_id)
        if mother is None or father is None:
            console.print("[red]Mother o father non trovati.[/]")
            raise typer.Exit(code=1)

        ai = FamilyAI(seed=settings.master_seed + 2)
        eval_ = ai.evaluate_couple(session, mother, father, current)

    table = Table(title=f"Family AI @ {current}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("eligible", "✓" if eval_.eligible else "✗")
    table.add_row("probability", f"{eval_.probability:.4f}")
    table.add_row("reason", eval_.reason)
    for k, v in sorted(eval_.factors.items()):
        table.add_row(f"factor.{k}", f"{v:.4f}")
    console.print(table)


# ---------------------------------------------------------------------------
# family-ai-tick
# ---------------------------------------------------------------------------


@npc_app.command("family-ai-tick")
def npc_family_ai_tick(
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza un tick completo di lifecycle (include Family AI + successione)."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    lifecycle = _build_lifecycle()
    report = lifecycle.force_daily_work(current)

    table = Table(title=f"Lifecycle tick @ {current}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("daily_work_done", str(report.daily_work_done))
    table.add_row("dead_ids", ", ".join(map(str, report.dead_ids)) or "—")
    table.add_row("birth_ids", ", ".join(map(str, report.birth_ids)) or "—")
    table.add_row(
        "pregnancy_started",
        ", ".join(map(str, report.pregnancy_started_ids)) or "—",
    )
    table.add_row(
        "pregnancy_completed",
        ", ".join(map(str, report.pregnancy_completed_ids)) or "—",
    )
    table.add_row("conception_attempts", str(report.conception_attempts))
    table.add_row("orphan_ids", ", ".join(map(str, report.orphan_ids)) or "—")
    table.add_row(
        "guardian_assignments",
        ", ".join(f"{c}->{g}" for c, g in report.guardian_assignments) or "—",
    )
    table.add_row("age_transitions", str(len(report.age_transitions)))
    console.print(table)


# ---------------------------------------------------------------------------
# orphans / guardian
# ---------------------------------------------------------------------------


@npc_app.command("orphans")
def npc_orphans() -> None:
    """Elenca i character orfani (attributes_json.orphan == True)."""
    factory = get_session_factory()
    with factory() as session:
        orphans = SuccessionService.list_orphans(session)
        # Preload tutori
        guardian_ids = set()
        for o in orphans:
            gid = o.attributes_json.get("guardian_id")
            if isinstance(gid, int):
                guardian_ids.add(gid)
        guardians = (
            {c.id: c for c in session.query(Character).filter(Character.id.in_(guardian_ids)).all()}
            if guardian_ids
            else {}
        )

    if not orphans:
        console.print("[yellow]Nessun orfano.[/]")
        return

    table = Table(title=f"Orfani ({len(orphans)})")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Da", style="green")
    table.add_column("Tutore", style="yellow")
    for o in orphans:
        attrs = o.attributes_json or {}
        gid = attrs.get("guardian_id")
        g_name = guardians[gid].full_name if gid in guardians else "—"
        table.add_row(
            str(o.id),
            o.full_name,
            str(attrs.get("orphan_since", "—")),
            g_name,
        )
    console.print(table)


@npc_app.command("guardian")
def npc_guardian(
    child_id: int = typer.Argument(..., help="ID del minore."),
) -> None:
    """Mostra il tutore di un minore (se assegnato)."""
    factory = get_session_factory()
    with factory() as session:
        child = session.get(Character, child_id)
        if child is None:
            console.print(f"[red]Character id={child_id} non trovato.[/]")
            raise typer.Exit(code=1)
        attrs = child.attributes_json or {}
        gid = attrs.get("guardian_id")
        if gid is None:
            console.print(f"[yellow]{child.full_name} non ha tutore assegnato.[/]")
            return
        guardian = session.get(Character, gid)

    if guardian is None:
        console.print(f"[red]Tutore id={gid} non trovato nel DB.[/]")
        raise typer.Exit(code=1)

    table = Table(title=f"Tutore di {child.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("child_id", str(child.id))
    table.add_row("guardian_id", str(guardian.id))
    table.add_row("guardian_name", guardian.full_name)
    table.add_row("guardian_sex", guardian.sex)
    table.add_row("orphan_since", str(attrs.get("orphan_since", "—")))
    console.print(table)


# ---------------------------------------------------------------------------
# memory
# ---------------------------------------------------------------------------


@npc_app.command("memory")
def npc_memory(
    character_id: int = typer.Argument(..., help="ID del character."),
    limit: int = typer.Option(20, "--limit", "-l", min=1, max=200),
    kind: str | None = typer.Option(None, "--kind", "-k"),
) -> None:
    """Elenca le memorie di un character."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    current = tm.current

    kind_enum: MemoryKind | None = None
    if kind is not None:
        try:
            kind_enum = MemoryKind(kind.upper())
        except ValueError:
            console.print(f"[red]Kind sconosciuto: {kind!r}[/]")
            raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        from simai.npc import Character

        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        recalls = MemoryService.recall(
            session, character_id, limit=limit, kind=kind_enum, current_dt=current
        )

    if not recalls:
        console.print(f"[yellow]Nessuna memoria per {c.full_name}.[/]")
        return

    table = Table(title=f"Memorie di {c.full_name} (id={c.id})")
    table.add_column("ID", style="cyan")
    table.add_column("Kind", style="yellow")
    table.add_column("Score", justify="right")
    table.add_column("Sal.", justify="right")
    table.add_column("Val.", justify="right")
    table.add_column("Testo", style="magenta")
    for r in recalls:
        m = r.memory
        table.add_row(
            str(m.id),
            m.kind,
            f"{r.score:.3f}",
            f"{m.saliency:.2f}",
            f"{m.valence:+.2f}",
            m.text[:60] + ("..." if len(m.text) > 60 else ""),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# intimate
# ---------------------------------------------------------------------------


@npc_app.command("intimate")
def npc_intimate(
    initiator_id: int = typer.Argument(..., help="ID di chi inizia."),
    partner_id: int = typer.Argument(..., help="ID del partner."),
    action: str = typer.Argument(
        ...,
        help="Azione: CONFIDE, SHARE_MOMENT, INTIMATE_TALK, "
        "ROMANTIC_GESTURE, KISS, INTIMATE_ENCOUNTER.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Salta il consenso (dev tool).",
    ),
) -> None:
    """Esegue un'azione di intimità tra due character (con consenso)."""
    import random

    settings = get_settings()
    start = build_starting_datetime()

    try:
        action_enum = IntimacyAction(action.upper())
    except ValueError:
        console.print(f"[red]Azione sconosciuta: {action!r}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        from simai.npc import Character

        a = session.get(Character, initiator_id)
        b = session.get(Character, partner_id)
        if a is None or b is None:
            console.print("[red]Uno dei due character non trovato.[/]")
            raise typer.Exit(code=1)

        rng = random.Random(settings.master_seed)
        result = IntimacyService.perform(
            session,
            initiator=a,
            partner=b,
            action=action_enum,
            current_dt=start,
            rng=rng,
            force=force,
        )
        session.commit()

    table = Table(title="Intimità")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    outcome_color = {
        IntimacyOutcome.SUCCESS: "green",
        IntimacyOutcome.REJECTED: "yellow",
        IntimacyOutcome.NOT_ELIGIBLE: "red",
    }.get(result.outcome, "white")
    table.add_row("outcome", f"[{outcome_color}]{result.outcome.value}[/]")
    table.add_row("action", result.action.value)
    table.add_row("reason", result.reason)
    table.add_row("memory_id", str(result.memory_id) if result.memory_id else "—")
    if result.consent is not None:
        table.add_row("willingness", f"{result.consent.willingness:.3f}")
        for k, v in sorted(result.consent.factors.items()):
            table.add_row(f"factor.{k}", f"{v:.3f}")
    console.print(table)


@npc_app.command("consent")
def npc_consent(
    initiator_id: int = typer.Argument(..., help="ID di chi inizia."),
    partner_id: int = typer.Argument(..., help="ID del partner."),
    action: str = typer.Argument(..., help="Azione di intimità."),
) -> None:
    """Anteprima della willingness del partner (senza eseguire)."""
    from simai.npc import Character
    from simai.npc.intimacy import (
        ConsentService,
    )

    start = build_starting_datetime()

    try:
        action_enum = IntimacyAction(action.upper())
    except ValueError:
        console.print(f"[red]Azione sconosciuta: {action!r}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        a = session.get(Character, initiator_id)
        b = session.get(Character, partner_id)
        if a is None or b is None:
            console.print("[red]Uno dei due character non trovato.[/]")
            raise typer.Exit(code=1)

        # Pre-check
        ok, reason, rel, def_ = IntimacyService.can_perform(session, a, b, action_enum)
        if not ok or rel is None or def_ is None:
            console.print(f"[yellow]Precondizioni fallite:[/] {reason}")
            raise typer.Exit(code=1)

        willingness, factors = ConsentService.compute_willingness(
            session,
            initiator=a,
            partner=b,
            action_def=def_,
            rel=rel,
            current_dt=start,
        )

    table = Table(title=f"Consenso: {a.full_name} -> {b.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("action", action_enum.value)
    table.add_row("action_level", str(def_.level))
    table.add_row("willingness", f"{willingness:.3f}")
    for k, v in sorted(factors.items()):
        table.add_row(f"factor.{k}", f"{v:.3f}")
    console.print(table)
    console.print(
        f"[dim]La decisione finale è probabilistica: P(accettazione) = {willingness * 100:.1f}%[/]"
    )


# ---------------------------------------------------------------------------
# bt-demo
# ---------------------------------------------------------------------------


@npc_app.command("bt-demo")
def npc_bt_demo() -> None:
    """Demo del Behaviour Tree: Sequence[Condition, Action]."""

    def check_needs(bb: Blackboard) -> bool:
        hunger = bb.get("hunger", 0)
        if not isinstance(hunger, (int, float)):
            return False
        return hunger < 30

    def eat(bb: Blackboard) -> BTStatus:
        bb.set("hunger", bb.get("hunger", 0) + 50)
        return BTStatus.SUCCESS

    def relax(bb: Blackboard) -> BTStatus:
        bb.set("relax_count", bb.get("relax_count", 0) + 1)
        return BTStatus.SUCCESS

    tree = Selector(
        Sequence(
            Condition(check_needs, name="hungry"),
            ActionLeaf(eat, name="eat"),
            name="eat_when_hungry",
        ),
        ActionLeaf(relax, name="relax"),
        name="root",
    )

    bb = Blackboard()
    bb.set("hunger", 10)
    bb.set("relax_count", 0)

    table = Table(title="BT demo — 3 tick")
    table.add_column("Tick", justify="right")
    table.add_column("Hunger", justify="right")
    table.add_column("Relax count", justify="right")
    table.add_column("Status", style="cyan")
    for i in range(3):
        status = tree.tick(bb)
        table.add_row(
            str(i + 1),
            str(bb.get("hunger")),
            str(bb.get("relax_count")),
            status.value,
        )
    console.print(table)


# ---------------------------------------------------------------------------
# bt-tree
# ---------------------------------------------------------------------------


@npc_app.command("bt-tree")
def npc_bt_tree(
    action_type: str = typer.Argument(..., help="ActionType (EAT, DRINK, SLEEP, ...)."),
) -> None:
    """Visualizza il Behaviour Tree di un'azione."""
    try:
        at = ActionType(action_type.upper())
    except ValueError:
        valid = ", ".join(a.value for a in ActionType)
        console.print(f"[red]ActionType sconosciuto: {action_type!r}[/]\n[dim]Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    action = action_of(at)
    tree = build_bt_for_action(action)
    console.print(f"[bold]BT per {at.value}[/] ({action.label}, duration={action.duration_ticks}):")
    console.print(render_tree(tree))


# ---------------------------------------------------------------------------
# wealth / give / inventory / own / unown / inherit / legacy
# ---------------------------------------------------------------------------


@npc_app.command("wealth")
def npc_wealth(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra il bilancio in Athel di un character."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(
                f"[red]Character id={character_id} non trovato.[/] "
                "[dim]Esegui `npc seed` se il DB è vuoto.[/]"
            )
            raise typer.Exit(code=1)
        balance = WealthService.balance_of(c)
        n_objs = InventoryService.count(session, character_id)
        n_locs = len(PropertyService.owned_locations(session, character_id))

    table = Table(title=f"Patrimonio di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("athel_balance", f"{balance} Athel")
    table.add_row("owned_objects", str(n_objs))
    table.add_row("owned_locations", str(n_locs))
    console.print(table)


@npc_app.command("give")
def npc_give(
    sender_id: int = typer.Argument(..., help="ID del mittente."),
    receiver_id: int = typer.Argument(..., help="ID del destinatario."),
    amount: int = typer.Argument(..., min=1, help="Importo in Athel."),
) -> None:
    """Trasferisce Athel da un character a un altro."""
    factory = get_session_factory()
    try:
        with factory() as session:
            sender = session.get(Character, sender_id)
            receiver = session.get(Character, receiver_id)
            if sender is None or receiver is None:
                console.print("[red]Sender o receiver non trovati.[/]")
                raise typer.Exit(code=1)
            new_s, new_r = WealthService.transfer(
                session, sender=sender, receiver=receiver, amount=amount
            )
            session.commit()
    except EconomyError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[green]Trasferiti {amount} Athel:[/] "
        f"{sender.full_name} {new_s} | {receiver.full_name} {new_r}"
    )


@npc_app.command("inventory")
def npc_inventory(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Elenca gli oggetti posseduti."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        objs = InventoryService.owned_objects(session, character_id)

    if not objs:
        console.print(f"[yellow]Nessun oggetto posseduto da {c.full_name}.[/]")
        return

    table = Table(title=f"Inventario di {c.full_name}")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Tipo", style="green")
    table.add_column("Location", justify="right")
    for o in objs:
        table.add_row(
            str(o.id),
            o.name,
            o.type,
            str(o.location_id) if o.location_id else "—",
        )
    console.print(table)


@npc_app.command("own")
def npc_own(
    character_id: int = typer.Argument(..., help="ID del character."),
    location_id: int = typer.Argument(..., help="ID della location."),
    share: float = typer.Option(1.0, "--share", "-s", min=0.01, max=1.0),
) -> None:
    """Assegna la proprietà di una location a un character."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        loc = get_location(session, location_id)
        if c is None or loc is None:
            console.print("[red]Character o location non trovati.[/]")
            raise typer.Exit(code=1)
        try:
            PropertyService.grant(session, character=c, location=loc, share=share)
        except EconomyError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        session.commit()

    console.print(f"[green]Proprietà assegnata:[/] {c.full_name} -> {loc.name} (share={share:.2f})")


@npc_app.command("unown")
def npc_unown(
    character_id: int = typer.Argument(..., help="ID del character."),
    location_id: int = typer.Argument(..., help="ID della location."),
) -> None:
    """Rimuove la proprietà di una location da un character."""
    factory = get_session_factory()
    with factory() as session:
        # Pre-check: verifica esistenza character e location con
        # messaggi d'errore specifici (allineato a `npc_own`).
        c = session.get(Character, character_id)
        if c is None:
            console.print(
                f"[red]Character id={character_id} non trovato.[/] "
                "[dim]Esegui `npc seed` se il DB è vuoto.[/]"
            )
            raise typer.Exit(code=1)

        loc = get_location(session, location_id)
        if loc is None:
            console.print(
                f"[red]Location id={location_id} non trovata.[/] "
                "[dim]Esegui `world seed` se il mondo è vuoto.[/]"
            )
            raise typer.Exit(code=1)

        removed = PropertyService.revoke(
            session, character_id=character_id, location_id=location_id
        )
        session.commit()

    if not removed:
        console.print(f"[yellow]{c.full_name} non possiede '{loc.name}'.[/]")
        return
    console.print(f"[green]Proprietà rimossa:[/] {c.full_name} ✗ {loc.name}")


@npc_app.command("legacy")
def npc_legacy(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra gli eredi potenziali e i beni di un character."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        heirs = InheritanceService.find_heirs(session, character_id)
        n_objs = InventoryService.count(session, character_id)
        n_locs = len(PropertyService.owned_locations(session, character_id))
        balance = WealthService.balance_of(c)

        heir_rows: list[tuple[int, str, str]] = []
        for hid, tier in sorted(heirs.items(), key=lambda kv: kv[1].priority):
            h = session.get(Character, hid)
            if h is not None:
                heir_rows.append((hid, h.full_name, tier.value))

    table = Table(title=f"Eredità potenziale di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("athel_balance", f"{balance} Athel")
    table.add_row("owned_objects", str(n_objs))
    table.add_row("owned_locations", str(n_locs))
    table.add_row("heirs", str(len(heirs)))
    console.print(table)

    if heir_rows:
        ht = Table(title="Eredi (per priorità)")
        ht.add_column("ID", style="cyan")
        ht.add_column("Nome", style="magenta")
        ht.add_column("Tier", style="yellow")
        for hid, name, tier_name in heir_rows:
            ht.add_row(str(hid), name, tier_name)
        console.print(ht)


@npc_app.command("inherit")
def npc_inherit(
    character_id: int = typer.Argument(..., help="ID del defunto (deve essere morto)."),
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Forza la distribuzione dell'eredità di un character defunto."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        if c.is_alive:
            console.print("[yellow]Il character è ancora vivo. Usa `npc kill` prima.[/]")
            raise typer.Exit(code=1)
        report = InheritanceService.distribute(session, deceased=c, current_dt=current)
        session.commit()

    table = Table(title=f"Eredità di {c.full_name} (id={c.id})")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("heirs", str(len(report.heirs)))
    table.add_row("cash_distributed", f"{report.cash_distributed} Athel")
    table.add_row("locations_assigned", str(report.locations_assigned))
    table.add_row("objects_assigned", str(report.objects_assigned))
    table.add_row("unclaimed", str(report.unclaimed))
    console.print(table)


# ---------------------------------------------------------------------------
# skills
# ---------------------------------------------------------------------------


@npc_app.command("skills")
def npc_skills(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Elenca le abilità di un character (con talent derivato)."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(
                f"[red]Character id={character_id} non trovato.[/] "
                "[dim]Esegui `npc seed` se il DB è vuoto.[/]"
            )
            raise typer.Exit(code=1)

        skills = SkillService.all_skills(session, character_id)
        rows: list[tuple[str, int, float, float]] = [
            (s.skill_type, s.level, s.progress, s.talent) for s in skills
        ]

    if not rows:
        console.print(
            f"[yellow]{c.full_name} non ha ancora abilità.[/]\n"
            "[dim]Le skill si creano alla prima pratica.[/]"
        )
        return

    table = Table(title=f"Abilità di {c.full_name} (id={c.id})")
    table.add_column("Skill", style="cyan")
    table.add_column("Livello", justify="right", style="magenta")
    table.add_column("Progresso", justify="right")
    table.add_column("Talent", justify="right", style="green")
    for stype, level, progress, talent in rows:
        progress_bar = f"{progress * 100:5.1f}%"
        table.add_row(
            stype,
            f"{level} / {MAX_SKILL_LEVEL}",
            progress_bar,
            f"{talent:.2f}",
        )
    console.print(table)


@npc_app.command("talents")
def npc_talents(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra il talent derivato dal genoma per tutte le skill."""
    from simai.npc.genetics import Genome
    from simai.npc.skills import SkillType, talent_for_skill

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        if not c.genome_json:
            console.print(f"[yellow]{c.full_name} non ha genoma.[/]")
            raise typer.Exit(code=1)
        genome = Genome.from_dict(c.genome_json)

    table = Table(title=f"Talent di {c.full_name} (id={c.id})")
    table.add_column("Skill", style="cyan")
    table.add_column("Famiglia", style="yellow")
    table.add_column("Talent", justify="right", style="green")
    for st in SkillType:
        talent = talent_for_skill(genome, st)
        family = SKILL_TALENT_FAMILY.get(st, "?")
        table.add_row(st.value, family, f"{talent:.2f}")
    console.print(table)


@npc_app.command("skill-train")
def npc_skill_train(
    character_id: int = typer.Argument(..., help="ID del character."),
    skill_type: str = typer.Argument(..., help="Tipo di skill (FARMING, ...)."),
    xp: float = typer.Argument(..., min=0.01, help="XP da aggiungere."),
) -> None:
    """Dev tool: aggiunge XP a una skill del character."""
    start = build_starting_datetime()

    try:
        st = SkillType(skill_type.upper())
    except ValueError:
        valid = ", ".join(s.value for s in SkillType)
        console.print(f"[red]SkillType sconosciuto: {skill_type!r}[/]\n[dim]Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)

        skill = SkillService.get_or_create(
            session,
            character_id=character_id,
            skill_type=st,
            current_dt=start,
        )
        old_level = skill.level
        old_progress = skill.progress
        SkillService.add_progress(session, skill, xp_delta=xp, current_dt=start)
        session.commit()
        new_level = skill.level
        new_progress = skill.progress

    table = Table(title=f"Train {st.value} su {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("xp_added", f"{xp:.2f}")
    table.add_row(
        "level",
        f"{old_level} -> {new_level}" + (" [green](LEVEL UP!)[/]" if new_level > old_level else ""),
    )
    table.add_row("progress", f"{old_progress * 100:.1f}% -> {new_progress * 100:.1f}%")
    console.print(table)


@npc_app.command("skill-decay")
def npc_skill_decay(
    character_id: int = typer.Argument(..., help="ID del character."),
    at_tick: int = typer.Option(0, "--at-tick", "-t", min=0),
) -> None:
    """Dev tool: forza un ciclo di decay (1 giorno) su tutte le skill."""
    settings = get_settings()
    start = build_starting_datetime()
    from simai.core.time_manager import TimeManager

    tm = TimeManager(start=start, tick_minutes=settings.tick_minutes)
    tm.advance_ticks(at_tick)
    current = tm.current

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        decayed = SkillService.apply_daily_decay(session, character=c, current_dt=current)
        session.commit()

    if not decayed:
        console.print("[yellow]Nessuna skill decaduta (inattività < grazia o livello 0).[/]")
        return

    table = Table(title=f"Decay su {c.full_name} @ {current}")
    table.add_column("Skill", style="cyan")
    table.add_column("Livello", justify="right", style="magenta")
    table.add_column("Giorni inattivi", justify="right")
    for d in decayed:
        table.add_row(
            d.skill_type.value,
            f"{d.old_level} -> {d.new_level}",
            str(d.days_inactive),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------


@npc_app.command("identity")
def npc_identity(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra il profilo identità (orientamento, SEP, cultura)."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        profile = IdentityService.get_profile(c)

    console.print(f"[bold]Identità di {c.full_name} (id={c.id})[/]")

    # Sexuality
    sex = profile.sexuality
    t1 = Table(title="Orientamento sessuale")
    t1.add_column("Dimensione", style="cyan")
    t1.add_column("Valore", justify="right", style="magenta")
    t1.add_row("attrazione M", f"{sex.attraction_to_male:.3f}")
    t1.add_row("attrazione F", f"{sex.attraction_to_female:.3f}")
    t1.add_row("attrazione NB", f"{sex.attraction_to_nonbinary:.3f}")
    t1.add_row("romantico↔sessuale", f"{sex.romantic_vs_sexual:.3f}")
    t1.add_row("label", f"[bold]{sex.label()}[/]")
    console.print(t1)

    # SEP
    sep = profile.sep
    t2 = Table(title="SEP (Sexual Education Profile)")
    t2.add_column("Dimensione", style="cyan")
    t2.add_column("Valore", justify="right", style="magenta")
    t2.add_row("knowledge", f"{sep.knowledge:.1f} / 100")
    t2.add_row("comfort", f"{sep.comfort:.3f}")
    t2.add_row("inhibition", f"{sep.inhibition:.3f}")
    t2.add_row(
        "received_at_age",
        str(sep.received_at_age) if sep.received_at_age is not None else "—",
    )
    console.print(t2)

    # Cultura
    cul = profile.culture
    t3 = Table(title="Profilo culturale")
    t3.add_column("Dimensione", style="cyan")
    t3.add_column("Valore", justify="right", style="magenta")
    t3.add_row("permissiveness", f"{cul.permissiveness:.3f}")
    t3.add_row("modesty", f"{cul.modesty:.3f}")
    t3.add_row("gender_role_strict", f"{cul.gender_role_strict:.3f}")
    t3.add_row("reaction_to_taboo", cul.reaction_to_taboo.value)
    t3.add_row("tradition", cul.tradition.value)
    console.print(t3)


# ---------------------------------------------------------------------------
# addictions
# ---------------------------------------------------------------------------


@npc_app.command("addictions")
def npc_addictions(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Elenca le dipendenze di un character."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        addictions = AddictionService.all_of(session, character_id)
        rows = [
            (a.kind, a.dependence_level, a.tolerance, a.last_use_total_seconds) for a in addictions
        ]

    if not rows:
        console.print(f"[yellow]{c.full_name} non ha dipendenze.[/]")
        return

    table = Table(title=f"Dipendenze di {c.full_name}")
    table.add_column("Kind", style="cyan")
    table.add_column("Dipendenza", justify="right", style="magenta")
    table.add_column("Tolleranza", justify="right")
    table.add_column("Ultimo uso", style="dim")
    for kind, dep, tol, last in rows:
        table.add_row(kind, f"{dep:.1f}", f"{tol:.1f}", str(last))
    console.print(table)


@npc_app.command("addiction-start")
def npc_addiction_start(
    character_id: int = typer.Argument(..., help="ID del character."),
    kind: str = typer.Argument(..., help="Kind (ALCOHOL, TOBACCO, ...)."),
    dependence: float | None = typer.Option(
        None, "--dep", min=1.0, max=100.0, help="Dipendenza iniziale."
    ),
) -> None:
    """Avvia una dipendenza (dev tool)."""
    start = build_starting_datetime()
    try:
        ak = AddictionKind(kind.upper())
    except ValueError:
        valid = ", ".join(k.value for k in AddictionKind)
        console.print(f"[red]AddictionKind sconosciuto: {kind!r}[/]\n[dim]Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        a = AddictionService.start_addiction(
            session,
            character_id=character_id,
            kind=ak,
            current_dt=start,
            initial_dependence=dependence,
        )
        session.commit()

    console.print(
        f"[green]Addiction creata:[/] {c.full_name} -> {a.kind} (dep={a.dependence_level:.1f})"
    )


@npc_app.command("addiction-use")
def npc_addiction_use(
    character_id: int = typer.Argument(..., help="ID del character."),
    kind: str = typer.Argument(..., help="Kind."),
) -> None:
    """Simula un uso (per test iniziazione/incremento)."""
    import random

    settings = get_settings()
    start = build_starting_datetime()
    try:
        ak = AddictionKind(kind.upper())
    except ValueError:
        console.print(f"[red]AddictionKind sconosciuto: {kind!r}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        rng = random.Random(settings.master_seed + character_id)
        result = AddictionService.use(
            session,
            character_id=character_id,
            kind=ak,
            current_dt=start,
            rng=rng,
        )
        session.commit()

    table = Table(title="Uso")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("kind", result.kind.value)
    table.add_row("initiated", str(result.initiated))
    table.add_row("dependence_after", f"{result.dependence_after:.2f}")
    console.print(table)


# ---------------------------------------------------------------------------
# background
# ---------------------------------------------------------------------------


@npc_app.command("background")
def npc_background(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra gli eventi formativi del passato di un character."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        events = BackgroundService.all_of(session, character_id)

    if not events:
        console.print(f"[yellow]{c.full_name} non ha eventi formativi.[/]")
        return

    table = Table(title=f"Background di {c.full_name}")
    table.add_column("Età", justify="right", style="cyan")
    table.add_column("Kind", style="yellow")
    table.add_column("Severity", justify="right")
    table.add_column("Testo", style="magenta")
    for ev in events:
        sev_color = "red" if ev.severity >= 0.7 else ("yellow" if ev.severity >= 0.4 else "white")
        table.add_row(
            str(ev.occurred_at_age),
            ev.kind,
            f"[{sev_color}]{ev.severity:.2f}[/]",
            ev.text,
        )
    console.print(table)


@npc_app.command("background-add")
def npc_background_add(
    character_id: int = typer.Argument(..., help="ID del character."),
    kind: str = typer.Argument(..., help="FormativeEventKind."),
    age: int = typer.Option(..., "--age", "-a", min=0, help="Età al momento."),
    severity: float = typer.Option(0.5, "--sev", min=0.0, max=1.0, help="Severity."),
) -> None:
    """Aggiunge manualmente un evento formativo (dev tool)."""
    start = build_starting_datetime()
    try:
        k = FormativeEventKind(kind.upper())
    except ValueError:
        valid = ", ".join(x.value for x in FormativeEventKind)
        console.print(f"[red]FormativeEventKind sconosciuto: {kind!r}[/]\n[dim]Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        ev = BackgroundService.record_event(
            session,
            character=c,
            kind=k,
            occurred_at_age=age,
            severity=severity,
            current_dt=start,
        )
        session.commit()

    if ev is None:
        console.print("[yellow]Evento già esistente (duplicato).[/]")
        return
    console.print(
        f"[green]Evento creato:[/] {c.full_name} - {k.value} age={age} sev={severity:.2f}"
    )


# ---------------------------------------------------------------------------
# stress
# ---------------------------------------------------------------------------


@npc_app.command("stress")
def npc_stress(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra lo stress corrente e i fattori."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        stress, factors = StressService.compute(session, c, start)

    table = Table(title=f"Stress di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    color = "red" if stress > 0.7 else ("yellow" if stress > 0.4 else "green")
    table.add_row("stress", f"[{color}]{stress:.3f}[/]")
    for name, weight in STRESS_WEIGHTS.items():
        value = getattr(factors, name)
        contribution = value * weight
        table.add_row(
            f"{name} (×{weight:.2f})",
            f"{value:.3f} → {contribution:.3f}",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# desire
# ---------------------------------------------------------------------------


@npc_app.command("desire")
def npc_desire(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra lo stato del desiderio."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        # Recompute per avere il valore corrente aggiornato
        new_state = DesireService.recompute(session, c, current_dt=start)
        session.commit()

    table = Table(title=f"Desiderio di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("baseline", f"{new_state.baseline:.3f}")
    table.add_row("current", f"{new_state.current:.3f}")
    table.add_row("last_satisfied_at", str(new_state.last_satisfied_at) or "—")
    console.print(table)


# ---------------------------------------------------------------------------
# intimacy-list
# ---------------------------------------------------------------------------


@npc_app.command("intimacy-list")
def npc_intimacy_list() -> None:
    """Elenca tutte le azioni di intimità disponibili con i loro requisiti."""
    table = Table(title=f"Catalogo intimità ({len(INTIMACY_CATALOG)} azioni)")
    table.add_column("Azione", style="cyan")
    table.add_column("Lv", justify="right", style="yellow")
    table.add_column("Label", style="magenta")
    table.add_column("Bond min", justify="right")
    table.add_column("Strength min", justify="right")
    table.add_column("Kinds", style="green")
    table.add_column("Digital", justify="center")

    # Ordina per livello
    ordered = sorted(INTIMACY_CATALOG, key=lambda d: (d.level, d.action.value))
    for d in ordered:
        kinds = sorted(k.value for k in d.allowed_kinds)
        kinds_str = ", ".join(k[:3] for k in kinds)  # abbreviazione
        table.add_row(
            d.action.value,
            str(d.level),
            d.label,
            f"{d.min_bond:.2f}",
            f"{d.min_strength:.2f}",
            kinds_str,
            "✓" if d.is_digital else "",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# reputation
# ---------------------------------------------------------------------------


@npc_app.command("reputation")
def npc_reputation(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra la reputazione pubblica di un character."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        score = ReputationService.reputation_of(session, character_id)
        # Conta opinioni
        from sqlalchemy import func as _f
        from sqlalchemy import select as _sel

        from simai.npc.reputation import Opinion

        n_opinions = (
            session.scalar(
                _sel(_f.count()).select_from(Opinion).where(Opinion.target_id == character_id)
            )
            or 0
        )

    table = Table(title=f"Reputazione di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    color = (
        "green"
        if score > OPINION_POSITIVE_THRESHOLD
        else ("red" if score < OPINION_NEGATIVE_THRESHOLD else "yellow")
    )
    table.add_row("reputation", f"[{color}]{score:+.1f}[/]")
    table.add_row("opinions_count", str(n_opinions))
    console.print(table)


@npc_app.command("opinion")
def npc_opinion(
    observer_id: int = typer.Argument(..., help="ID dell'osservatore."),
    target_id: int = typer.Argument(..., help="ID del target."),
) -> None:
    """Mostra l'opinione di A su B."""
    factory = get_session_factory()
    with factory() as session:
        a = session.get(Character, observer_id)
        b = session.get(Character, target_id)
        if a is None or b is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        score = ReputationService.get_opinion(session, observer_id, target_id)

    table = Table(title=f"Opinione di {a.full_name} su {b.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    color = (
        "green"
        if score > OPINION_POSITIVE_THRESHOLD
        else ("red" if score < OPINION_NEGATIVE_THRESHOLD else "yellow")
    )
    table.add_row("score", f"[{color}]{score:+.1f}[/]")
    console.print(table)


@npc_app.command("gossip")
def npc_gossip(
    source_id: int = typer.Argument(..., help="ID di chi parla."),
    target_id: int = typer.Argument(..., help="ID del target."),
    listener_id: int = typer.Argument(..., help="ID di chi ascolta."),
    topic: str = typer.Argument(..., help="GossipTopic."),
    sentiment: float = typer.Option(0.5, "--sentiment", "-s", min=-1.0, max=1.0),
    strength: float = typer.Option(0.5, "--strength", "-p", min=0.0, max=1.0),
) -> None:
    """Propaga un pettegolezzo (dev tool)."""
    start = build_starting_datetime()
    try:
        t = GossipTopic(topic.upper())
    except ValueError:
        valid = ", ".join(x.value for x in GossipTopic)
        console.print(f"[red]Topic sconosciuto: {topic!r}. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        speaker = session.get(Character, source_id)
        target = session.get(Character, target_id)
        listener = session.get(Character, listener_id)
        if speaker is None or target is None or listener is None:
            console.print("[red]Uno dei character non trovato.[/]")
            raise typer.Exit(code=1)
        result = ReputationService.spread(
            session,
            speaker=speaker,
            listener=listener,
            target=target,
            topic=t,
            sentiment=sentiment,
            strength=strength,
            current_dt=start,
        )
        session.commit()

    table = Table(title="Gossip")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("propagated", str(result.propagated))
    table.add_row("topic", result.topic.value)
    table.add_row("delta_opinion", f"{result.delta_opinion:+.2f}")
    table.add_row("new_opinion", f"{result.new_opinion:+.2f}")
    console.print(table)


@npc_app.command("consanguinity")
def npc_consanguinity(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
) -> None:
    """Verifica consanguineità tra due character."""
    factory = get_session_factory()
    with factory() as session:
        a = session.get(Character, a_id)
        b = session.get(Character, b_id)
        if a is None or b is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        is_cons = ReputationService.is_consanguineous(session, a_id, b_id)
        severity = ReputationService.consanguinity_severity(session, a, b)

    table = Table(title=f"Consanguineità: {a.full_name} ↔ {b.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("is_consanguineous", "✓" if is_cons else "✗")
    table.add_row("severity", f"{severity:.3f}")
    console.print(table)


# ---------------------------------------------------------------------------
# boredom
# ---------------------------------------------------------------------------


@npc_app.command("boredom")
def npc_boredom(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
) -> None:
    """Mostra la noia relazionale tra due character."""
    factory = get_session_factory()
    with factory() as session:
        rel = session.scalars(
            select(Relationship).where(
                Relationship.from_id == a_id,
                Relationship.to_id == b_id,
            )
        ).first()
        if rel is None:
            console.print("[red]Nessuna relazione trovata.[/]")
            raise typer.Exit(code=1)
        boredom = BoredomService.get_boredom(rel)
        state = (
            "STALE"
            if BoredomService.is_stale(rel)
            else "WARNING"
            if BoredomService.is_warning(rel)
            else "OK"
        )
        md = rel.metadata_json or {}

    table = Table(title=f"Noia {a_id} → {b_id}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    color = {"STALE": "red", "WARNING": "yellow", "OK": "green"}[state]
    table.add_row("boredom", f"[{color}]{boredom:.3f}[/]")
    table.add_row("state", f"[{color}]{state}[/]")
    table.add_row("kind", rel.kind)
    table.add_row("strength", f"{rel.strength:.2f}")
    table.add_row(
        "actions_seen",
        str(len(md.get("actions_seen", []))),
    )
    console.print(table)


# ---------------------------------------------------------------------------
# breakup
# ---------------------------------------------------------------------------


@npc_app.command("breakup")
def npc_breakup(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
    kind: str = typer.Option(
        "PARTNER_OF",
        "--kind",
        "-k",
        help="RelationshipKind da rompere.",
    ),
    reason: str = typer.Option("manual", "--reason", "-r"),
) -> None:
    """Rompe una relazione (dev tool)."""
    start = build_starting_datetime()
    try:
        k = RelationshipKind(kind.upper())
    except ValueError:
        console.print(f"[red]Kind sconosciuto: {kind!r}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        rel = session.scalars(
            select(Relationship).where(
                Relationship.from_id == a_id,
                Relationship.to_id == b_id,
                Relationship.kind == k.value,
            )
        ).first()
        if rel is None:
            console.print("[red]Relazione non trovata.[/]")
            raise typer.Exit(code=1)
        result = BreakupService.breakup(session, rel=rel, reason=reason, current_dt=start)
        session.commit()

    table = Table(title="Breakup")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("occurred", str(result.occurred))
    table.add_row("kind", result.kind.value if result.kind else "—")
    table.add_row("reason", result.reason)
    table.add_row("residual_strength", f"{result.residual_strength:.2f}")
    console.print(table)


# ---------------------------------------------------------------------------
# infidelity-check
# ---------------------------------------------------------------------------


@npc_app.command("infidelity-check")
def npc_infidelity_check(
    actor_id: int = typer.Argument(..., help="ID dell'actor."),
    target_id: int = typer.Argument(..., help="ID del terzo."),
) -> None:
    """Verifica se l'actor considererebbe un'infedeltà con target."""
    import random

    settings = get_settings()
    factory = get_session_factory()
    with factory() as session:
        actor = session.get(Character, actor_id)
        target = session.get(Character, target_id)
        if actor is None or target is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        rng = random.Random(settings.master_seed)
        attempt = InfidelityService.should_consider(session, actor, target, rng)

    table = Table(title="Infidelity check")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("considered", str(attempt.considered))
    table.add_row("reason", attempt.reason)
    table.add_row("partner_id", str(attempt.partner_id) if attempt.partner_id else "—")
    table.add_row("target_id", str(attempt.target_id))
    console.print(table)


# ---------------------------------------------------------------------------
# compatibility
# ---------------------------------------------------------------------------


@npc_app.command("compatibility")
def npc_compatibility(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
) -> None:
    """Calcola la compatibilità intima tra due character."""
    factory = get_session_factory()
    with factory() as session:
        a = session.get(Character, a_id)
        b = session.get(Character, b_id)
        if a is None or b is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        score = CompatibilityService.compute(a, b)
        label = CompatibilityService.label(score)

    table = Table(title=f"Compatibilità: {a.full_name} ↔ {b.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    color = "green" if score >= 0.55 else ("yellow" if score >= 0.40 else "red")
    table.add_row("score", f"[{color}]{score:.3f}[/]")
    table.add_row("label", label)
    console.print(table)


# ---------------------------------------------------------------------------
# connection
# ---------------------------------------------------------------------------


@npc_app.command("connection")
def npc_connection(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
) -> None:
    """Mostra l'intesa cumulativa tra due character."""
    factory = get_session_factory()
    with factory() as session:
        rel = session.scalars(
            select(Relationship).where(
                Relationship.from_id == a_id,
                Relationship.to_id == b_id,
            )
        ).first()
        if rel is None:
            console.print("[red]Nessuna relazione trovata.[/]")
            raise typer.Exit(code=1)
        conn = ConnectionService.get(rel)
        label = ConnectionService.label(conn)

    table = Table(title=f"Intesa {a_id} → {b_id}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("connection", f"{conn:.3f}")
    table.add_row("label", label)
    table.add_row("kind", rel.kind)
    console.print(table)


# ---------------------------------------------------------------------------
# libido
# ---------------------------------------------------------------------------


@npc_app.command("libido")
def npc_libido(
    character_id: int = typer.Argument(..., help="ID del character."),
    with_partner: int | None = typer.Option(
        None, "--with", "-w", help="ID partner per effective libido."
    ),
) -> None:
    """Mostra la libido baseline (e effective se partner specificato)."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        baseline = LibidoService.get_baseline(c)

        effective_info = None
        if with_partner is not None:
            partner = session.get(Character, with_partner)
            rel = session.scalars(
                select(Relationship).where(
                    Relationship.from_id == character_id,
                    Relationship.to_id == with_partner,
                )
            ).first()
            if partner is None or rel is None:
                console.print("[yellow]Partner o relazione non trovati.[/]")
            else:
                eff_c, eff_p = LibidoService.effective(c, partner, rel)
                mismatch = LibidoService.mismatch_label(c, partner, rel)
                effective_info = (eff_c, eff_p, mismatch)

    table = Table(title=f"Libido di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("baseline", f"{baseline:.3f}")
    if effective_info is not None:
        eff_c, eff_p, mismatch = effective_info
        table.add_row("effective (self)", f"{eff_c:.3f}")
        table.add_row("effective (partner)", f"{eff_p:.3f}")
        table.add_row("mismatch", mismatch)
    console.print(table)


# ---------------------------------------------------------------------------
# mentor
# ---------------------------------------------------------------------------


@npc_app.command("mentor-eval")
def npc_mentor_eval(
    mentor_id: int = typer.Argument(..., help="ID del potenziale mentore."),
    student_id: int = typer.Argument(..., help="ID del potenziale studente."),
) -> None:
    """Valuta se il mentor può insegnare allo studente."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        mentor = session.get(Character, mentor_id)
        student = session.get(Character, student_id)
        if mentor is None or student is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        ev = MentorshipService.evaluate(session, mentor, student, current_dt=start)

    table = Table(title="Mentorship evaluation")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("eligible", "✓" if ev.eligible else "✗")
    table.add_row("reason", ev.reason)
    table.add_row("skill_type", ev.skill_type.value if ev.skill_type else "—")
    console.print(table)


@npc_app.command("mentor-start")
def npc_mentor_start(
    mentor_id: int = typer.Argument(..., help="ID del mentore."),
    student_id: int = typer.Argument(..., help="ID dello studente."),
) -> None:
    """Crea una relazione MENTOR_OF tra mentor e studente."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        mentor = session.get(Character, mentor_id)
        student = session.get(Character, student_id)
        if mentor is None or student is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)

        ev = MentorshipService.evaluate(session, mentor, student, current_dt=start)
        if not ev.eligible:
            console.print(f"[red]Non eleggibile: {ev.reason}[/]")
            raise typer.Exit(code=1)

        # Crea relazione (se non esiste)
        from sqlalchemy import select as _sel

        from simai.npc.relationships.models import Relationship

        existing = session.scalars(
            _sel(Relationship).where(
                Relationship.from_id == mentor_id,
                Relationship.to_id == student_id,
                Relationship.kind == "MENTOR_OF",
            )
        ).first()
        if existing is not None:
            console.print("[yellow]Mentorship già esistente.[/]")
            return

        rel = Relationship(
            from_id=mentor_id,
            to_id=student_id,
            kind="MENTOR_OF",
            strength=0.5,
            metadata_json={
                "skill_type": ev.skill_type.value if ev.skill_type else None,
                "sessions_completed": 0,
            },
        )
        session.add(rel)
        session.commit()

    console.print(
        f"[green]Mentorship creata:[/] {mentor.full_name} -> "
        f"{student.full_name} (skill: {ev.skill_type.value if ev.skill_type else '—'})"
    )


@npc_app.command("mentorship")
def npc_mentorship(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra lo stato di mentorship del character."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        as_student = MentorshipService.active_mentor_of(session, character_id)

        # Come mentor: relazioni uscenti MENTOR_OF
        from sqlalchemy import select as _sel

        from simai.npc.relationships.models import Relationship

        as_mentor_rels = list(
            session.scalars(
                _sel(Relationship).where(
                    Relationship.from_id == character_id,
                    Relationship.kind == "MENTOR_OF",
                )
            )
        )

    if as_student is None and not as_mentor_rels:
        console.print(f"[yellow]{c.full_name} non ha mentorship.[/]")
        return

    if as_student is not None:
        mentor = session.get(Character, as_student.from_id)
        md = as_student.metadata_json or {}
        table = Table(title=f"{c.full_name} come STUDENTE")
        table.add_column("Chiave", style="cyan")
        table.add_column("Valore", style="magenta")
        table.add_row("mentor", mentor.full_name if mentor else "?")
        table.add_row("skill", str(md.get("skill_type", "—")))
        table.add_row("sessions", str(md.get("sessions_completed", 0)))
        table.add_row("graduated", str(md.get("graduated", False)))
        console.print(table)

    if as_mentor_rels:
        table = Table(title=f"{c.full_name} come MENTORE")
        table.add_column("Studente", style="cyan")
        table.add_column("Skill", style="magenta")
        table.add_column("Sessions", justify="right")
        table.add_column("Graduated", justify="center")
        for rel in as_mentor_rels:
            student = session.get(Character, rel.to_id)
            md = rel.metadata_json or {}
            table.add_row(
                student.full_name if student else f"<id={rel.to_id}>",
                str(md.get("skill_type", "—")),
                str(md.get("sessions_completed", 0)),
                "✓" if md.get("graduated", False) else "",
            )
        console.print(table)


@npc_app.command("age-gap")
def npc_age_gap(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
) -> None:
    """Mostra il gap età e il bonus opinion intergenerazionale."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        a = session.get(Character, a_id)
        b = session.get(Character, b_id)
        if a is None or b is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        gap = IntergenerationalService.age_gap_years(a, b, start)
        bonus = IntergenerationalService.opinion_bonus(a, b, start)

    table = Table(title=f"Gap età: {a.full_name} ↔ {b.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("age_gap_years", str(gap))
    table.add_row("opinion_bonus", f"{bonus:+.1f}")
    console.print(table)


# ---------------------------------------------------------------------------
# lgbtq
# ---------------------------------------------------------------------------


@npc_app.command("lgbtq")
def npc_lgbtq(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra identità LGBTQ+ e disclosure level."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        is_lgbtq = LGBTQService.is_lgbtq(c)
        disclosure = LGBTQService.disclosure_level(c)
        is_public = LGBTQService.is_publicly_out(c)

    table = Table(title=f"LGBTQ status di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("gender", c.gender)
    table.add_row("sex", c.sex)
    table.add_row("is_lgbtq", "✓" if is_lgbtq else "✗")
    if is_lgbtq:
        table.add_row("disclosure", f"{disclosure:.2f}")
        table.add_row("is_publicly_out", "✓" if is_public else "✗")
    console.print(table)


# ---------------------------------------------------------------------------
# polyamory-check
# ---------------------------------------------------------------------------


@npc_app.command("polyamory-check")
def npc_polyamory_check(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Verifica se un character accetta poliamoria."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        accepts = PolyamoryService.accepts_polyamory(c)
        partners = PolyamoryService.current_partners(session, character_id)

    table = Table(title=f"Poliamoria di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("accepts_polyamory", "✓" if accepts else "✗")
    table.add_row("current_partners", str(len(partners)))
    for p in partners:
        table.add_row("  partner", p.full_name)
    console.print(table)


@npc_app.command("polyamory-add")
def npc_polyamory_add(
    actor_id: int = typer.Argument(..., help="ID dell'actor."),
    target_id: int = typer.Argument(..., help="ID del nuovo partner."),
) -> None:
    """Aggiunge un partner in regime poliamoroso."""
    factory = get_session_factory()
    with factory() as session:
        actor = session.get(Character, actor_id)
        target = session.get(Character, target_id)
        if actor is None or target is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        ok, reason = PolyamoryService.can_add_partner(session, actor=actor, target=target)
        if not ok:
            console.print(f"[red]Non consentito: {reason}[/]")
            raise typer.Exit(code=1)

        from simai.npc.relationships.enums import RelationshipKind
        from simai.npc.relationships.service import create_relationship

        rels = create_relationship(
            session,
            from_id=actor_id,
            to_id=target_id,
            kind=RelationshipKind.PARTNER_OF,
            strength=0.6,
        )
        for r in rels:
            PolyamoryService.mark_polyamorous(r)
        session.commit()

    console.print(
        f"[green]Partner aggiunto:[/] {actor.full_name} + {target.full_name} (polyamoroso)"
    )


# ---------------------------------------------------------------------------
# teen-check
# ---------------------------------------------------------------------------


@npc_app.command("teen-check")
def npc_teen_check(
    a_id: int = typer.Argument(..., help="ID del primo character."),
    b_id: int = typer.Argument(..., help="ID del secondo character."),
) -> None:
    """Verifica dinamiche adolescenti tra due character."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        a = session.get(Character, a_id)
        b = session.get(Character, b_id)
        if a is None or b is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        a_teen = TeenDynamicsService.is_teen(a, start)
        b_teen = TeenDynamicsService.is_teen(b, start)
        modifier = TeenDynamicsService.willingness_modifier(a, b, current_dt=start, action_level=3)
        factor, opposing = TeenDynamicsService.parental_opposition_factor(
            session, a, b, current_dt=start
        )

    table = Table(title=f"Teen dynamics: {a.full_name} ↔ {b.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta", justify="right")
    table.add_row("a_is_teen", "✓" if a_teen else "✗")
    table.add_row("b_is_teen", "✓" if b_teen else "✗")
    table.add_row("willingness_modifier", f"{modifier:.2f}")
    table.add_row("parental_factor", f"{factor:.2f}")
    table.add_row("opposing_parents", str(opposing))
    console.print(table)


# ---------------------------------------------------------------------------
# knows
# ---------------------------------------------------------------------------


@npc_app.command("knows")
def npc_knows(
    observer_id: int = typer.Argument(..., help="ID dell'osservatore."),
    target_id: int = typer.Argument(..., help="ID del target."),
    partial: bool = typer.Option(
        False, "--partial", help="Mostra anche i tratti parzialmente noti."
    ),
) -> None:
    """Mostra i tratti che observer conosce di target."""
    factory = get_session_factory()
    with factory() as session:
        obs = session.get(Character, observer_id)
        tgt = session.get(Character, target_id)
        if obs is None or tgt is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)
        threshold = PARTIAL_THRESHOLD if partial else 1.0
        known = SocialAwarenessService.known_traits(obs, target_id, threshold=threshold)

    if not known:
        console.print(f"[yellow]{obs.full_name} non conosce tratti di {tgt.full_name}.[/]")
        return

    table = Table(title=f"Cosa sa {obs.full_name} di {tgt.full_name}")
    table.add_column("Tratto", style="cyan")
    table.add_column("Confidence", justify="right", style="magenta")
    table.add_column("Visibilità", style="yellow")

    for trait, conf in sorted(known.items(), key=lambda kv: -kv[1]):
        vis = TRAIT_VISIBILITY.get(trait)
        table.add_row(
            trait.value,
            f"{conf:.2f}",
            vis.value if vis else "?",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# discover
# ---------------------------------------------------------------------------


@npc_app.command("discover")
def npc_discover(
    observer_id: int = typer.Argument(..., help="ID dell'osservatore."),
    target_id: int = typer.Argument(..., help="ID del target."),
    intensity: int = typer.Option(
        3,
        "--intensity",
        "-i",
        min=0,
        max=5,
        help="Intensità dell'interazione (0-5).",
    ),
    n: int = typer.Option(1, "--times", "-n", min=1, help="Ripetizioni."),
) -> None:
    """Simula N interazioni e mostra i tratti scoperti (dev tool)."""
    import random

    settings = get_settings()
    factory = get_session_factory()
    with factory() as session:
        obs = session.get(Character, observer_id)
        tgt = session.get(Character, target_id)
        if obs is None or tgt is None:
            console.print("[red]Character non trovato.[/]")
            raise typer.Exit(code=1)

        rng = random.Random(settings.master_seed + observer_id + target_id)
        all_new: list[str] = []
        all_adv: list[str] = []
        for _ in range(n):
            result = SocialAwarenessService.record_interaction(
                obs, tgt, action_level=intensity, rng=rng
            )
            all_new.extend(t.value for t in result.newly_discovered)
            all_adv.extend(t.value for t in result.partially_advanced)
        session.commit()

    table = Table(title=f"Discovery: {obs.full_name} → {tgt.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("interactions", str(n))
    table.add_row("intensity", str(intensity))
    table.add_row("newly_discovered", ", ".join(all_new) or "—")
    table.add_row("partially_advanced", ", ".join(all_adv) or "—")
    console.print(table)


# ---------------------------------------------------------------------------
# cultural-knowledge
# ---------------------------------------------------------------------------


@npc_app.command("cultural-knowledge")
def npc_cultural_knowledge(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra l'awareness delle tradizioni culturali."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        awareness = SocialAwarenessService.all_cultural_awareness(c)
        own = IdentityService.get_culture(c).tradition

    table = Table(title=f"Awareness culturale di {c.full_name}")
    table.add_column("Tradizione", style="cyan")
    table.add_column("Awareness", justify="right", style="magenta")
    table.add_column("Propria", justify="center")
    for trad, val in sorted(awareness.items(), key=lambda kv: -kv[1]):
        table.add_row(
            trad.value,
            f"{val:.2f}",
            "✓" if trad is own else "",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# reflections
# ---------------------------------------------------------------------------


@npc_app.command("reflections")
def npc_reflections(
    character_id: int = typer.Argument(..., help="ID del character."),
    limit: int = typer.Option(10, "--limit", "-l", min=1, max=100),
) -> None:
    """Mostra le ultime entry del diario."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        entries = ReflectionService.recent_entries(session, character_id, limit=limit)

    if not entries:
        console.print(f"[yellow]{c.full_name} non ha riflessioni.[/]")
        return

    table = Table(title=f"Riflessioni di {c.full_name}")
    table.add_column("Tick", justify="right", style="dim")
    table.add_column("Kind", style="cyan")
    table.add_column("Sent.", justify="right")
    table.add_column("Testo", style="magenta")
    for e in entries:
        color = "green" if e.sentiment > 0.3 else ("red" if e.sentiment < -0.3 else "white")
        table.add_row(
            str(e.at_total_seconds),
            e.kind,
            f"[{color}]{e.sentiment:+.2f}[/]",
            e.text,
        )
    console.print(table)


@npc_app.command("reflect")
def npc_reflect(
    character_id: int = typer.Argument(..., help="ID del character."),
    kind: str | None = typer.Option(
        None,
        "--kind",
        "-k",
        help="Forza un tipo di riflessione (auto-detect se omesso).",
    ),
) -> None:
    """Forza una riflessione (dev tool)."""
    import random

    settings = get_settings()
    start = build_starting_datetime()

    kind_enum: ReflectionKind | None = None
    if kind is not None:
        try:
            kind_enum = ReflectionKind(kind.upper())
        except ValueError:
            valid = ", ".join(x.value for x in ReflectionKind)
            console.print(f"[red]Kind sconosciuto. Validi: {valid}[/]")
            raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        rng = random.Random(settings.master_seed + character_id)
        result = ReflectionService.reflect(session, c, current_dt=start, rng=rng, kind=kind_enum)
        session.commit()

    table = Table(title="Riflessione")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("kind", result.kind.value)
    table.add_row("sentiment", f"{result.sentiment:+.2f}")
    table.add_row("text", result.text)
    console.print(table)


# ---------------------------------------------------------------------------
# narrative
# ---------------------------------------------------------------------------


@npc_app.command("narrative")
def npc_narrative(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra la storia di vita del character."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        narrative = LifeNarrativeService.compose(session, c, current_dt=start)

    console.print(f"[bold]{narrative.summary}[/]\n")
    for chapter in narrative.chapters:
        age_str = f"[dim]({chapter.at_age} anni)[/]" if chapter.at_age is not None else ""
        console.print(f"[cyan]{chapter.title}[/] {age_str}")
        console.print(f"  {chapter.text}")


# ---------------------------------------------------------------------------
# crisis
# ---------------------------------------------------------------------------


@npc_app.command("crisis")
def npc_crisis(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra lo stato di crisi."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        status = CrisisService.get_status(c)

    table = Table(title=f"Crisi di {c.full_name}")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    color = {
        "ACTIVE": "red",
        "RESOLVING": "yellow",
        "RESOLVED": "green",
    }.get(status.phase.value, "white")
    table.add_row("active", str(status.active))
    table.add_row("phase", f"[{color}]{status.phase.value}[/]")
    table.add_row("days_in_crisis", str(status.days_in_crisis))
    table.add_row("reason", status.reason or "—")
    console.print(table)


@npc_app.command("crisis-start")
def npc_crisis_start(
    character_id: int = typer.Argument(..., help="ID del character."),
    reason: str = typer.Option("manual", "--reason", "-r"),
) -> None:
    """Attiva forzatamente una crisi (dev tool)."""
    start = build_starting_datetime()
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        ok = CrisisService.start_crisis(c, reason=reason, current_dt=start)
        session.commit()

    if not ok:
        console.print("[yellow]Crisi già attiva.[/]")
        return
    console.print(f"[green]Crisi attivata per {c.full_name}.[/]")


# ---------------------------------------------------------------------------
# personality
# ---------------------------------------------------------------------------


@npc_app.command("personality")
def npc_personality(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra personalità dinamica (trait strength + values)."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        PersonalityService.initialize(c)
        summary = PersonalityService.summary(c)
        session.commit()

    # Active + dormant traits
    table = Table(title=f"Tratti di {c.full_name}")
    table.add_column("Tratto", style="cyan")
    table.add_column("Strength", justify="right", style="magenta")
    table.add_column("Stato", style="yellow")

    for name in sorted(summary["strength"].keys()):
        s = summary["strength"][name]
        state = "attivo" if s >= 0.30 else "dormiente"
        color = "green" if s >= 0.70 else ("yellow" if s >= 0.30 else "dim")
        table.add_row(name, f"[{color}]{s:.3f}[/]", state)
    console.print(table)


# ---------------------------------------------------------------------------
# values
# ---------------------------------------------------------------------------


@npc_app.command("values")
def npc_values(
    character_id: int = typer.Argument(..., help="ID del character."),
) -> None:
    """Mostra gli assi valoriali."""
    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        values = PersonalityService.get_values(c)

    table = Table(title=f"Valori di {c.full_name}")
    table.add_column("Asse", style="cyan")
    table.add_column("Valore", justify="right", style="magenta")
    table.add_column("Bar", style="green")

    for axis in ValueAxis:
        v = values[axis]
        bar = "█" * int(v * 20) + "░" * (20 - int(v * 20))
        table.add_row(axis.value, f"{v:.3f}", bar)
    console.print(table)


# ---------------------------------------------------------------------------
# reinforce
# ---------------------------------------------------------------------------


@npc_app.command("reinforce")
def npc_reinforce(
    character_id: int = typer.Argument(..., help="ID del character."),
    action: str = typer.Argument(..., help="ActionType da rinforzare."),
) -> None:
    """Applica un rinforzo di personalità (dev tool)."""
    from simai.npc import ActionType

    try:
        at = ActionType(action.upper())
    except ValueError:
        valid = ", ".join(x.value for x in ActionType)
        console.print(f"[red]ActionType sconosciuto. Validi: {valid}[/]")
        raise typer.Exit(code=1) from None

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)
        PersonalityService.initialize(c)
        PersonalityService.reinforce_character(c, at)
        session.commit()
        new_traits = list(c.traits_json or [])

    console.print(
        f"[green]Rinforzato {at.value}[/] su {c.full_name}.\n"
        f"[dim]Tratti attuali: {', '.join(new_traits)}[/]"
    )


# ---------------------------------------------------------------------------
# recipes / craft
# ---------------------------------------------------------------------------


@npc_app.command("recipes")
def npc_recipes(
    skill: str | None = typer.Option(
        None,
        "--skill",
        "-s",
        help="Filtra per skill (COOKING, CRAFTING, MEDICINE).",
    ),
    character_id: int | None = typer.Option(
        None, "--for", "-f", help="ID character per filtrare per skill."
    ),
) -> None:
    """Elenca le ricette di crafting."""
    recipes = all_recipes()
    if skill is not None:
        recipes = [r for r in recipes if r.required_skill.value == skill.upper()]

    if not recipes:
        console.print("[yellow]Nessuna ricetta trovata.[/]")
        return

    table = Table(title=f"Ricette ({len(recipes)})")
    table.add_column("Code", style="cyan")
    table.add_column("Output", style="magenta")
    table.add_column("Skill", style="green")
    table.add_column("Min lvl", justify="right")
    table.add_column("Inputs", style="yellow")
    table.add_column("Value", justify="right")
    for r in recipes:
        inputs = ", ".join(f"{k}×{v}" for k, v in sorted(r.inputs.items()))
        table.add_row(
            r.code,
            r.output_name,
            r.required_skill.value,
            str(r.min_skill_level),
            inputs,
            str(r.base_value),
        )
    console.print(table)


@npc_app.command("craft")
def npc_craft(
    character_id: int = typer.Argument(..., help="ID del character."),
    recipe_code: str = typer.Argument(..., help="Codice ricetta (es. make_bread)."),
) -> None:
    """Esegue un craft. Consuma input dall'inventario."""
    import random

    settings = get_settings()
    start = build_starting_datetime()

    factory = get_session_factory()
    with factory() as session:
        c = session.get(Character, character_id)
        if c is None:
            console.print(f"[red]Character id={character_id} non trovato.[/]")
            raise typer.Exit(code=1)

        rng = random.Random(settings.master_seed + character_id)
        try:
            result = CraftingService.craft(
                session,
                character=c,
                recipe_code=recipe_code,
                current_dt=start,
                rng=rng,
            )
        except CraftingError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(code=1) from exc
        if result.success:
            session.commit()

    table = Table(title="Craft")
    table.add_column("Chiave", style="cyan")
    table.add_column("Valore", style="magenta")
    table.add_row("success", str(result.success))
    table.add_row("reason", result.reason)
    if result.success:
        table.add_row("output", f"{result.output_quantity} × {result.output_type}")
        table.add_row("quality_label", result.quality_label.value)
        table.add_row("quality_value", f"{result.quality_value:.3f}")
        table.add_row("skill_gained", str(result.skill_gained))
        table.add_row("skill_level_after", str(result.skill_level_after))
    console.print(table)

    if not result.success:
        raise typer.Exit(code=1)


@npc_app.command("resources")
def npc_resources() -> None:
    """Elenca le risorse disponibili (materie prime)."""
    table = Table(title="Risorse")
    table.add_column("Code", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Prezzo base", justify="right")
    from simai.npc.crafting import RESOURCE_PRICES as _RP

    for code, name in RESOURCE_NAMES.items():
        table.add_row(code, name, str(_RP.get(code, 0)))
    console.print(table)


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


def register(app: typer.Typer) -> None:
    """Registra il sub-app `npc` sull'app root."""
    app.add_typer(npc_app, name="npc")
