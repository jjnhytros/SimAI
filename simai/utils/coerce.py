"""Coercion helpers per valori `object` da JSON/dict.

Uso tipico: parsing di dati deserializzati da `json.loads()` o da colonne
`sa.JSON`, dove i valori sono tipati `object` da mypy.

Filosofia:
  - **Strict**: falliscono se il tipo non è coerente (no magic conversion).
  - **Esplicite**: accettano solo i casi sensati (`int`, `float` intero,
    `str` parsabile).
  - **Errori contestuali**: il parametro `name` aiuta il debug.
"""

from __future__ import annotations


def coerce_int(value: object, *, name: str = "value") -> int:
    """Converte `value` in `int`, o solleva `ValueError`.

    Accetta:
      - `int` (incluso `bool`? **No**: bool è escluso per evitare ambiguità)
      - `float` intero (es. `2.0` → `2`)
      - `str` parsabile (`"42"`)

    Rifiuta: `bool`, `float` non intero, `None`, altri tipi.
    """
    if isinstance(value, bool):
        raise ValueError(f"{name}: bool non è un int valido")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise ValueError(f"{name}: {value!r} non è un intero")
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{name}: {value!r} non è un intero valido") from exc
    raise ValueError(f"{name}: tipo non valido {type(value).__name__} ({value!r})")


def coerce_float(value: object, *, name: str = "value") -> float:
    """Converte `value` in `float`, o solleva `ValueError`.

    Accetta: `int`, `float`, `str` parsabile. Rifiuta: `bool`, `None`, altri.
    """
    if isinstance(value, bool):
        raise ValueError(f"{name}: bool non è un float valido")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"{name}: {value!r} non è un float valido") from exc
    raise ValueError(f"{name}: tipo non valido {type(value).__name__} ({value!r})")


def coerce_str(value: object, *, name: str = "value") -> str:
    """Converte `value` in `str`. Accetta solo `str` (no `str(x)` silente)."""
    if isinstance(value, str):
        return value
    raise ValueError(f"{name}: atteso str, ricevuto {type(value).__name__} ({value!r})")


def coerce_optional_int(value: object, *, name: str = "value") -> int | None:
    """Come `coerce_int`, ma accetta anche `None`."""
    if value is None:
        return None
    return coerce_int(value, name=name)


def coerce_optional_str(value: object, *, name: str = "value") -> str | None:
    """Come `coerce_str`, ma accetta anche `None`."""
    if value is None:
        return None
    return coerce_str(value, name=name)


__all__ = [
    "coerce_float",
    "coerce_int",
    "coerce_optional_int",
    "coerce_optional_str",
    "coerce_str",
]
