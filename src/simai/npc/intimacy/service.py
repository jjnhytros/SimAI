from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.mood.enums import MoodletKind
from simai.mood.models import Moodlet
from simai.mood.moodlets import SPECS, apply_moodlet
from simai.relationships.models import Relationship

# Soglie di `intimacy_level`: [0, 20, 40, 60, 80, 95].
# `level` è l'indice della soglia più alta <= strength.
_INTIMACY_THRESHOLDS: tuple[float, ...] = (20.0, 40.0, 60.0, 80.0, 95.0)

# Moodlet per livello. level 4 -> ROMANTIC, level 5 -> DEVOTED.
_INTIMACY_MOODLETS: dict[int, MoodletKind] = {
    4: MoodletKind.ROMANTIC,
    5: MoodletKind.DEVOTED,
}


def intimacy_level(strength: float) -> int:
    """Livello 0–5 da strength 0–100. Pura, deterministica.

    Soglie: <20 → 0, <40 → 1, <60 → 2, <80 → 3, <95 → 4, >=95 → 5.
    """
    level = 0
    for threshold in _INTIMACY_THRESHOLDS:
        if strength < threshold:
            return level
        level += 1
    return level


def _strengths_of(session: Session, character_id: int) -> list[float]:
    """Strength di tutte le relazioni in uscita e in entrata."""
    out = session.scalars(
        select(Relationship.strength).where(Relationship.from_character_id == character_id)
    ).all()
    incoming = session.scalars(
        select(Relationship.strength).where(Relationship.to_character_id == character_id)
    ).all()
    return [float(s) for s in out] + [float(s) for s in incoming]


def best_intimacy_level(session: Session, character_id: int) -> int:
    """Livello del legame più forte (out + in). 0 se nessuna relazione."""
    strengths = _strengths_of(session, character_id)
    if not strengths:
        return 0
    return max(intimacy_level(s) for s in strengths)


def intimacy_levels_of(session: Session, character_id: int) -> dict[str, int]:
    """Mappa `other_key -> level` per le relazioni in uscita.

    Solo out: la CLI mostra "le mie relazioni verso gli altri".
    """
    rows = session.scalars(
        select(Relationship)
        .where(Relationship.from_character_id == character_id)
        .order_by(Relationship.id)
    ).all()
    result: dict[str, int] = {}
    for rel in rows:
        from simai.world.models import Character

        other = session.get(Character, rel.to_character_id)
        if other is None:
            continue
        result[other.key] = intimacy_level(float(rel.strength))
    return result


def apply_intimacy_moodlets(session: Session, character_id: int, tick: int) -> MoodletKind | None:
    """Applica ROMANTIC/DEVOTED in base al miglior livello di legame.

    - level >= 5: DEVOTED
    - level >= 4: ROMANTIC
    - altrimenti: nessuna applicazione (i moodlet scadono da soli).

    Ritorna il kind applicato, o None.
    """
    level = best_intimacy_level(session, character_id)
    kind = _INTIMACY_MOODLETS.get(level)
    if kind is None:
        return None
    apply_moodlet(session, character_id, kind, tick)
    return kind


def apply_intimacy_moodlets_many(
    session: Session,
    char_ids: list[int],
    tick: int,
) -> dict[int, MoodletKind]:
    """Batch di `apply_intimacy_moodlets` per tutti i char.

    2 query invece di N: strength (out+in) in una, moodlet attivi in
    una. Applica ROMANTIC/DEVOTED solo se il moodlet non è già attivo
    o sta per scadere. Ritorna `{char_id: kind}` per chi ha ricevuto.
    """
    if not char_ids:
        return {}

    # 1. Strength di tutte le relazioni out+in, per tutti i char.
    rows = session.execute(
        select(Relationship.from_character_id, Relationship.strength).where(
            Relationship.from_character_id.in_(char_ids)
        )
    ).all()
    strengths: dict[int, list[float]] = {cid: [] for cid in char_ids}
    for from_id, strength in rows:
        strengths[from_id].append(float(strength))
    rows_in = session.execute(
        select(Relationship.to_character_id, Relationship.strength).where(
            Relationship.to_character_id.in_(char_ids)
        )
    ).all()
    for to_id, strength in rows_in:
        strengths[to_id].append(float(strength))

    # 2. Livello per char.
    levels: dict[int, int] = {}
    for cid, values in strengths.items():
        levels[cid] = max((intimacy_level(v) for v in values), default=0)

    # 3. Moodlet attivi (ROMANTIC/DEVOTED) per tutti.
    active_rows = session.scalars(
        select(Moodlet).where(
            Moodlet.character_id.in_(char_ids),
            Moodlet.kind.in_((MoodletKind.ROMANTIC, MoodletKind.DEVOTED)),
            Moodlet.expires_at_tick > tick,
        )
    ).all()
    active_by_char: dict[int, Moodlet] = {m.character_id: m for m in active_rows}

    # 4. Applica per chi ha level >= 4.
    applied: dict[int, MoodletKind] = {}
    for cid, level in levels.items():
        desired = _INTIMACY_MOODLETS.get(level)
        if desired is None:
            continue
        current = active_by_char.get(cid)
        if current is not None and current.kind == desired:
            # Stesso moodlet: refresh solo se vicino alla scadenza.
            if current.expires_at_tick - tick <= 1:
                spec = SPECS[current.kind]
                current.started_at_tick = tick
                current.expires_at_tick = tick + spec.duration_ticks
            applied[cid] = desired
            continue
        # Transizione: cancella vecchio, applica nuovo.
        if current is not None:
            session.delete(current)
        spec = SPECS[desired]
        session.add(
            Moodlet(
                character_id=cid,
                kind=desired,
                need=None,
                started_at_tick=tick,
                expires_at_tick=tick + spec.duration_ticks,
            )
        )
        applied[cid] = desired
    return applied
