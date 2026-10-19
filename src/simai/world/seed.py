from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.needs.service import ensure_initial_needs
from simai.relationships.enums import RelationshipKind
from simai.relationships.service import ensure_relationship
from simai.world.enums import LocationKind
from simai.world.models import Character, Location

LOCATION_SPECS: list[dict[str, Any]] = [
    {
        "key": "casa",
        "name": "Casa",
        "kind": LocationKind.RESIDENTIAL,
        "description": "L'abitazione del giocatore.",
        "capacity": 6,
    },
    {
        "key": "piazza",
        "name": "Piazza delle Muse",
        "kind": LocationKind.SOCIAL,
        "description": "Il cuore pulsante del quartiere.",
        "capacity": 20,
    },
    {
        "key": "caffe",
        "name": "Caffè delle Muse",
        "kind": LocationKind.LEISURE,
        "description": "Un locale accogliente.",
        "capacity": 12,
    },
]

CHARACTER_SPECS: list[dict[str, Any]] = [
    {
        "key": "player",
        "name": "Giocatore",
        "age_years": 30,
        "is_player": True,
        "location_key": "casa",
    },
    {
        "key": "erika",
        "name": "Erika Lamborghetti",
        "age_years": 14,
        "is_player": False,
        "location_key": "casa",
    },
    {
        "key": "max",
        "name": "Max Volpi",
        "age_years": 14,
        "is_player": False,
        "location_key": "piazza",
    },
    {
        "key": "luca",
        "name": "Luca Ferretti",
        "age_years": 42,
        "is_player": False,
        "location_key": "caffe",
    },
    {
        "key": "giulia",
        "name": "Giulia Marchetti",
        "age_years": 37,
        "is_player": False,
        "location_key": "piazza",
    },
]


def seed_muse_core(session: Session) -> dict[str, int]:
    """Crea i dati del Quartiere delle Muse se mancanti.

    Idempotente: chiavi già presenti non vengono toccate.
    """
    locations_created = 0
    characters_created = 0
    needs_created = 0
    relationships_created = 0

    by_key: dict[str, Location] = {}
    for spec in LOCATION_SPECS:
        existing_location = session.scalar(select(Location).where(Location.key == spec["key"]))
        if existing_location is not None:
            by_key[spec["key"]] = existing_location
            continue
        loc = Location(**spec)
        session.add(loc)
        by_key[spec["key"]] = loc
        locations_created += 1

    session.flush()

    characters: list[Character] = []
    for char_spec in CHARACTER_SPECS:
        existing_character = session.scalar(
            select(Character).where(Character.key == char_spec["key"])
        )
        if existing_character is not None:
            characters.append(existing_character)
            continue
        data = {k: v for k, v in char_spec.items() if k != "location_key"}
        data["location_id"] = by_key[char_spec["location_key"]].id
        new_char = Character(**data)
        session.add(new_char)
        characters.append(new_char)
        characters_created += 1

    session.flush()

    for char in characters:
        needs_created += ensure_initial_needs(session, char.id)

    by_char_key = {c.key: c for c in characters}
    erika = by_char_key.get("erika")
    max_char = by_char_key.get("max")
    if erika is not None and max_char is not None:
        rel1 = ensure_relationship(
            session,
            erika.id,
            max_char.id,
            kind=RelationshipKind.FRIEND,
            strength=60.0,
        )
        if rel1 is not None:
            relationships_created += 1
        rel2 = ensure_relationship(
            session,
            max_char.id,
            erika.id,
            kind=RelationshipKind.FRIEND,
            strength=60.0,
        )
        if rel2 is not None:
            relationships_created += 1

    session.flush()

    return {
        "locations_created": locations_created,
        "characters_created": characters_created,
        "needs_created": needs_created,
        "relationships_created": relationships_created,
    }
