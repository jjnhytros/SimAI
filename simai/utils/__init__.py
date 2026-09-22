"""Helper generici (no dipendenze da package SimAI specifici)."""

from simai.utils.coerce import (
    coerce_float,
    coerce_int,
    coerce_optional_int,
    coerce_optional_str,
    coerce_str,
)
from simai.utils.git import get_git_sha

__all__ = [
    "coerce_float",
    "coerce_int",
    "coerce_optional_int",
    "coerce_optional_str",
    "coerce_str",
    "get_git_sha",
]
