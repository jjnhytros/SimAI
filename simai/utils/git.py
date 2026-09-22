"""Helper Git (solo lettura, no side effects)."""

from __future__ import annotations

import subprocess


def get_git_sha(short: bool = False) -> str | None:
    """Restituisce lo SHA del commit corrente, o ``None`` se non disponibile.

    Non solleva eccezioni: fallback silenzioso a ``None`` se git non è
    installato, non c'è un repo, o il comando fallisce.
    """
    args = ["git", "rev-parse"]
    args.append("--short" if short else "HEAD")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=2.0,
            check=True,
        )
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return None
    out = result.stdout.strip()
    return out or None
