from dataclasses import dataclass

from sqlalchemy.orm import Session

from simai.world.models import Character, Location


@dataclass(frozen=True)
class MoveResult:
    success: bool
    character_key: str
    from_location_key: str | None
    to_location_key: str | None
    error: str | None = None


def move_character(session: Session, character_key: str, location_key: str) -> MoveResult:
    """Sposta un personaggio in una location esistente.

    In 1.0 non c'è grafo né pathfinding: qualsiasi location è
    raggiungibile. Lo spostamento è istantaneo.
    """
    char = session.query(Character).filter_by(key=character_key).one_or_none()
    if char is None:
        return MoveResult(
            success=False,
            character_key=character_key,
            from_location_key=None,
            to_location_key=None,
            error=f"Personaggio non trovato: {character_key}",
        )

    target = session.query(Location).filter_by(key=location_key).one_or_none()
    if target is None:
        return MoveResult(
            success=False,
            character_key=character_key,
            from_location_key=None,
            to_location_key=location_key,
            error=f"Location non trovata: {location_key}",
        )

    current = session.get(Location, char.location_id)
    if current is not None and current.id == target.id:
        return MoveResult(
            success=True,
            character_key=character_key,
            from_location_key=current.key,
            to_location_key=target.key,
            error=None,
        )

    char.location_id = target.id
    session.flush()
    return MoveResult(
        success=True,
        character_key=character_key,
        from_location_key=current.key if current else None,
        to_location_key=target.key,
    )
