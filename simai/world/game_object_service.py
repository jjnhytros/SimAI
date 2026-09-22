"""Operazioni di alto livello su GameObject."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from simai.world.enums import GameObjectState
from simai.world.models import GameObject


def create_object(
    session: Session,
    *,
    name: str,
    type_: str,
    location_id: int | None = None,
    container_capacity: int | None = None,
    interactions: list[str] | None = None,
    metadata: dict[str, object] | None = None,
) -> GameObject:
    """Crea e persiste un GameObject. Ritorna l'istanza con `id` popolato."""
    obj = GameObject(
        name=name,
        type=type_,
        location_id=location_id,
        state=str(GameObjectState.NEW),
        condition=1.0,
        container_capacity=container_capacity,
        container_contents_json=[],
        interactions_json=list(interactions or []),
        metadata_json=dict(metadata or {}),
    )
    session.add(obj)
    session.flush()
    return obj


def get_object(session: Session, object_id: int) -> GameObject | None:
    return session.get(GameObject, object_id)


def list_objects(session: Session) -> list[GameObject]:
    return list(session.scalars(select(GameObject).order_by(GameObject.id)))


def apply_wear(obj: GameObject, amount: float) -> float:
    """Consuma `condition` di `amount` (0..1). A 0 lo stato diventa BROKEN.

    Ritorna la nuova `condition`.
    """
    if amount < 0:
        raise ValueError(f"amount deve essere >= 0, ricevuto {amount}")
    obj.condition = max(0.0, obj.condition - amount)
    if obj.condition <= 0.0 and obj.state != str(GameObjectState.BROKEN):
        obj.state = str(GameObjectState.BROKEN)
    elif obj.state == str(GameObjectState.NEW):
        obj.state = str(GameObjectState.USED)
    return obj.condition


def repair(obj: GameObject, target: float = 0.9) -> float:
    """Ripristina `condition` a `target` (default 0.9). Ritorna il nuovo valore."""
    if not (0.0 < target <= 1.0):
        raise ValueError(f"target deve essere in (0, 1], ricevuto {target}")
    if obj.state == str(GameObjectState.BROKEN):
        obj.state = str(GameObjectState.USED)
    obj.condition = target
    return obj.condition


def add_to_container(session: Session, container: GameObject, item_id: int) -> None:
    """Aggiunge un item al container se c'è spazio. Altrimenti solleva ValueError."""
    if container.container_capacity is None:
        raise ValueError(f"'{container.name}' non è un container")
    contents: list[int] = list(container.container_contents_json or [])
    if item_id in contents:
        raise ValueError(f"item id={item_id} già presente nel container")
    if len(contents) >= container.container_capacity:
        raise ValueError(
            f"container '{container.name}' pieno ({len(contents)}/{container.container_capacity})"
        )
    contents.append(item_id)
    container.container_contents_json = contents
    session.flush()


def remove_from_container(session: Session, container: GameObject, item_id: int) -> None:
    contents: list[int] = list(container.container_contents_json or [])
    if item_id not in contents:
        raise ValueError(f"item id={item_id} non presente nel container")
    contents.remove(item_id)
    container.container_contents_json = contents
    session.flush()
