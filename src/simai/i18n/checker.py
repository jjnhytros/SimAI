from pathlib import Path
from typing import Any

import yaml

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
BASE_LANGUAGE = "it"


def _flatten(data: dict[str, Any], prefix: str = "") -> set[str]:
    keys: set[str] = set()
    for k, v in data.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys |= _flatten(v, full)
        else:
            keys.add(full)
    return keys


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise TypeError(f"{path.name}: file locale non valido (atteso dict)")
    return data


def check() -> list[str]:
    """Ritorna la lista dei problemi. Lista vuota = OK."""
    if not LOCALES_DIR.exists():
        return [f"Directory locale mancante: {LOCALES_DIR}"]

    files = sorted(LOCALES_DIR.glob("*.yml"))
    if not files:
        return [f"Nessun file locale in {LOCALES_DIR}"]

    by_lang: dict[str, set[str]] = {}
    for path in files:
        try:
            by_lang[path.stem] = _flatten(_load(path))
        except (yaml.YAMLError, TypeError) as exc:
            return [f"{path.name}: {exc}"]

    if BASE_LANGUAGE not in by_lang:
        return [f"Lingua base '{BASE_LANGUAGE}' non trovata in {LOCALES_DIR}"]

    base = by_lang[BASE_LANGUAGE]
    problems: list[str] = []
    for lang, keys in by_lang.items():
        if lang == BASE_LANGUAGE:
            continue
        missing = sorted(base - keys)
        extra = sorted(keys - base)
        if missing:
            sample = missing[:5] + (["..."] if len(missing) > 5 else [])
            problems.append(f"{lang}: {len(missing)} chiavi mancanti: {sample}")
        if extra:
            sample = extra[:5] + (["..."] if len(extra) > 5 else [])
            problems.append(f"{lang}: {len(extra)} chiavi extra: {sample}")

    return problems
