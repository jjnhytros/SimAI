"""Loader della configurazione YAML di simulazione (§1.7 del TODO).

Il file `simai/config/simulation.yaml` contiene i parametri di gameplay
(tick, LOD, save, futuri parametri economici/demografici/AI).

Override prioritari (dal più alto al più basso):
  1. Variabili d'ambiente `SIMAI_*` (gestite da `Settings` pydantic)
  2. File `.env`
  3. `simulation.yaml`
  4. Default hardcoded nel modello Pydantic

Hot-reload: la cache è invalidata quando il `mtime` del file cambia.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

# Path di default, relativo alla root del progetto.
DEFAULT_CONFIG_PATH: Path = Path(__file__).parent / "simulation.yaml"


# ---------------------------------------------------------------------------
# Modelli
# ---------------------------------------------------------------------------


class TickConfig(BaseModel):
    """Parametri del tick di simulazione."""

    minutes: int = Field(default=5, ge=1)
    perf_threshold_ms: float = Field(default=100.0, gt=0)
    history_max: int = Field(default=1000, ge=1)


class TimeConfig(BaseModel):
    """Parametri del tempo iniziale di simulazione."""

    starting_year: int = Field(default=5775, ge=1)
    starting_month: int = Field(default=1, ge=1, le=18)
    starting_day: int = Field(default=1, ge=1, le=24)


class SimulationSection(BaseModel):
    """Sezione `simulation`."""

    tick: TickConfig = Field(default_factory=TickConfig)
    time: TimeConfig = Field(default_factory=TimeConfig)


class LodConfig(BaseModel):
    """Sezione `lod`."""

    full_distance: int = Field(default=1, ge=0)
    reduced_distance: int = Field(default=3, ge=0)


class SaveConfig(BaseModel):
    """Sezione `save`."""

    compression_level: int = Field(default=10, ge=1, le=22)


class SimulationConfig(BaseModel):
    """Configurazione completa di simulazione."""

    simulation: SimulationSection = Field(default_factory=SimulationSection)
    lod: LodConfig = Field(default_factory=LodConfig)
    save: SaveConfig = Field(default_factory=SaveConfig)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _read_yaml(path: Path) -> dict[str, Any]:
    """Legge il file YAML. Ritorna `{}` se il file non esiste."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(
            f"Il file {path} deve contenere una mappatura YAML, trovato {type(data).__name__}"
        )
    return data


@lru_cache(maxsize=8)
def _load_cached(path_str: str, mtime: float) -> SimulationConfig:
    """Cache interna: chiave = (path, mtime). Cambiare il file invalida la cache."""
    del mtime  # usato solo come chiave di cache
    raw = _read_yaml(Path(path_str))
    return SimulationConfig.model_validate(raw)


def load_simulation_config(path: Path | None = None) -> SimulationConfig:
    """Carica la configurazione di simulazione con cache + hot-reload.

    Se il file non esiste, ritorna la configurazione di default (senza cache).
    Se il file cambia (mtime), la cache è invalidata automaticamente.
    """
    p = path or DEFAULT_CONFIG_PATH
    if not p.exists():
        return SimulationConfig()
    mtime = p.stat().st_mtime
    return _load_cached(str(p), mtime)
