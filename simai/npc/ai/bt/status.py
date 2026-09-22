"""Stato di un nodo Behaviour Tree."""

from enum import StrEnum


class BTStatus(StrEnum):
    """Esito di un tick di un nodo BT."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


__all__ = ["BTStatus"]
