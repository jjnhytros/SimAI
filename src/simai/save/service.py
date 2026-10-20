import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from simai.config.settings import Settings
from simai.mood.enums import MoodletKind
from simai.mood.models import Moodlet
from simai.needs.enums import NeedKind
from simai.needs.models import Need
from simai.relationships.enums import RelationshipKind
from simai.relationships.models import Relationship
from simai.save.errors import (
    SaveError,
    SaveFormatError,
    SaveNotFoundError,
)
from simai.save.format import SaveHeader, decode, encode
from simai.sim.models import SimState
from simai.world.enums import LocationKind
from simai.world.models import Character, Location

NAME_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")


@dataclass(frozen=True)
class SaveInfo:
    name: str
    path: Path
    header: SaveHeader
    size_bytes: int


def _saves_dir() -> Path:
    return Settings().saves_dir


def validate_name(name: str) -> str:
    if not NAME_RE.match(name):
        raise SaveError(
            f"Nome salvataggio non valido: {name!r}. "
            "Usa solo lettere, cifre, '_' e '-', max 64 caratteri."
        )
    return name


def _path_for(name: str) -> Path:
    return _saves_dir() / f"{name}.sav"


def _schema_revision(session: Session) -> str | None:
    from alembic.runtime.migration import MigrationContext

    conn = session.connection()
    return MigrationContext.configure(conn).get_current_revision()


def _serialize_state(session: Session) -> dict[str, Any]:
    from simai.economy.models import Job, Transaction

    locations = session.scalars(select(Location)).all()
    characters = session.scalars(select(Character)).all()
    needs = session.scalars(select(Need)).all()
    relationships = session.scalars(select(Relationship)).all()
    moodlets = session.scalars(select(Moodlet).order_by(Moodlet.id)).all()
    jobs = session.scalars(select(Job).order_by(Job.id)).all()
    transactions = session.scalars(select(Transaction).order_by(Transaction.id)).all()
    sim_state = session.get(SimState, 1)

    return {
        "locations": [
            {
                "id": loc.id,
                "key": loc.key,
                "name": loc.name,
                "kind": loc.kind.value,
                "description": loc.description,
                "capacity": loc.capacity,
            }
            for loc in locations
        ],
        "characters": [
            {
                "id": c.id,
                "key": c.key,
                "name": c.name,
                "age_years": c.age_years,
                "is_player": c.is_player,
                "location_id": c.location_id,
                "mood": c.mood,
                "low_intimacy_streak": c.low_intimacy_streak,
                "balance": c.balance,
            }
            for c in characters
        ],
        "needs": [
            {
                "id": n.id,
                "character_id": n.character_id,
                "kind": n.kind.value,
                "value": n.value,
            }
            for n in needs
        ],
        "relationships": [
            {
                "id": r.id,
                "from_character_id": r.from_character_id,
                "to_character_id": r.to_character_id,
                "kind": r.kind.value,
                "strength": r.strength,
            }
            for r in relationships
        ],
        "moodlets": [
            {
                "character_id": m.character_id,
                "kind": m.kind.value,
                "started_at_tick": m.started_at_tick,
                "expires_at_tick": m.expires_at_tick,
            }
            for m in moodlets
        ],
        "jobs": [
            {
                "character_id": j.character_id,
                "title": j.title.value,
                "location_key": j.location_key,
                "daily_wage": j.daily_wage,
                "schedule_start_tick": j.schedule_start_tick,
                "schedule_end_tick": j.schedule_end_tick,
            }
            for j in jobs
        ],
        "transactions": [
            {
                "tick_index": t.tick_index,
                "from_character_id": t.from_character_id,
                "to_character_id": t.to_character_id,
                "amount": t.amount,
                "kind": t.kind.value,
                "note": t.note,
            }
            for t in transactions
        ],
        "sim_state": (
            {
                "tick_index": sim_state.tick_index,
                "master_seed": sim_state.master_seed,
            }
            if sim_state is not None
            else {"tick_index": 0, "master_seed": 42}
        ),
    }


def _deserialize_state(session: Session, payload: dict[str, Any]) -> None:
    """Svuota le tabelle di stato e reinserisce il payload.

    Va eseguito dentro una transazione: se qualcosa fallisce, il
    chiamante deve fare rollback.

    Ordine di delete: figli prima dei padri.
    Ordine di insert: padri prima dei figli.
    """

    from simai.economy.enums import JobTitle, TransactionKind
    from simai.economy.models import Job, Transaction

    session.execute(delete(Moodlet))
    session.execute(delete(Relationship))
    session.execute(delete(Need))
    session.execute(delete(Transaction))
    session.execute(delete(Job))
    session.execute(delete(Character))
    session.execute(delete(Location))
    session.execute(delete(SimState))
    session.flush()

    for row in payload["locations"]:
        session.add(
            Location(
                id=row["id"],
                key=row["key"],
                name=row["name"],
                kind=LocationKind(row["kind"]),
                description=row["description"],
                capacity=row["capacity"],
            )
        )
    session.flush()

    for row in payload["characters"]:
        session.add(
            Character(
                id=row["id"],
                key=row["key"],
                name=row["name"],
                age_years=row["age_years"],
                is_player=row["is_player"],
                location_id=row["location_id"],
                mood=row.get("mood", 100.0),
                low_intimacy_streak=row.get("low_intimacy_streak", 0),
                balance=row.get("balance", 100.0),
            )
        )
    session.flush()

    for row in payload["needs"]:
        session.add(
            Need(
                id=row["id"],
                character_id=row["character_id"],
                kind=NeedKind(row["kind"]),
                value=row["value"],
            )
        )

    for row in payload["relationships"]:
        session.add(
            Relationship(
                id=row["id"],
                from_character_id=row["from_character_id"],
                to_character_id=row["to_character_id"],
                kind=RelationshipKind(row["kind"]),
                strength=row["strength"],
            )
        )

    for row in payload.get("jobs", []):
        session.add(
            Job(
                character_id=row["character_id"],
                title=JobTitle(row["title"]),
                location_key=row["location_key"],
                daily_wage=row["daily_wage"],
                schedule_start_tick=row["schedule_start_tick"],
                schedule_end_tick=row["schedule_end_tick"],
            )
        )

    for row in payload.get("transactions", []):
        session.add(
            Transaction(
                tick_index=row["tick_index"],
                from_character_id=row["from_character_id"],
                to_character_id=row["to_character_id"],
                amount=row["amount"],
                kind=TransactionKind(row["kind"]),
                note=row["note"],
            )
        )

    for row in payload.get("moodlets", []):
        session.add(
            Moodlet(
                character_id=row["character_id"],
                kind=MoodletKind(row["kind"]),
                started_at_tick=row["started_at_tick"],
                expires_at_tick=row["expires_at_tick"],
            )
        )

    sim_state_row = payload["sim_state"]
    session.add(
        SimState(
            id=1,
            tick_index=sim_state_row["tick_index"],
            master_seed=sim_state_row["master_seed"],
        )
    )
    session.flush()


def create_save(
    session: Session,
    *,
    name: str | None = None,
    output: Path | None = None,
) -> SaveInfo:
    """Serializza lo stato corrente in un file .sav."""
    save_name = validate_name(name or datetime.now(UTC).strftime("save_%Y%m%dT%H%M%SZ"))
    payload = _serialize_state(session)
    sim_state = payload["sim_state"]
    data = encode(
        payload,
        tick_index=sim_state["tick_index"],
        master_seed=sim_state["master_seed"],
        schema_revision=_schema_revision(session),
    )

    target = output or _path_for(save_name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)

    header, _ = decode(data)
    return SaveInfo(
        name=save_name,
        path=target,
        header=header,
        size_bytes=len(data),
    )


def list_saves() -> list[SaveInfo]:
    saves_dir = _saves_dir()
    if not saves_dir.exists():
        return []
    infos: list[SaveInfo] = []
    for path in sorted(saves_dir.glob("*.sav")):
        try:
            data = path.read_bytes()
            header, _ = decode(data)
        except SaveError:
            continue
        infos.append(
            SaveInfo(
                name=path.stem,
                path=path,
                header=header,
                size_bytes=len(data),
            )
        )
    return infos


def _resolve_path(name_or_path: str) -> Path:
    as_path = Path(name_or_path)
    if as_path.exists() and as_path.is_file():
        return as_path
    candidate = _path_for(validate_name(name_or_path))
    if not candidate.exists():
        raise SaveNotFoundError(f"Salvataggio non trovato: {name_or_path}")
    return candidate


def load_save(session: Session, name_or_path: str) -> SaveHeader:
    """Carica un file .sav e sostituisce lo stato corrente."""
    path = _resolve_path(name_or_path)
    data = path.read_bytes()
    header, payload = decode(data)

    current_rev = _schema_revision(session)
    if (
        header.schema_revision is not None
        and current_rev is not None
        and header.schema_revision != current_rev
    ):
        raise SaveFormatError(
            f"Revisione schema incompatibile: save={header.schema_revision}, db={current_rev}"
        )

    _deserialize_state(session, payload)
    return header


def delete_save(name: str) -> Path:
    path = _resolve_path(name)
    path.unlink()
    return path
