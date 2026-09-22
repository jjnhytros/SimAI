"""Settings applicative SimAI (pydantic-settings)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings globali di SimAI, caricate da `.env` + variabili d'ambiente."""

    model_config = SettingsConfigDict(
        env_prefix="SIMAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Applicazione ---
    env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    master_seed: int = 0

    # --- Database ---
    db_url: str = "sqlite:///./simai.db"

    # --- Simulazione ---
    tick_minutes: int = 5
    starting_year: int = 5775
    starting_day: int = 1
    starting_month: int = 1

    # --- Data dir ---
    data_dir: Path = Path("./data")
    saves_dir: Path = Path("./data/saves")
    logs_dir: Path = Path("./data/logs")
    exports_dir: Path = Path("./data/exports")

    # --- UI (opzionale, non in FASE 0) ---
    ui_enabled: bool = False
    ui_host: str = "127.0.0.1"
    ui_port: int = 8000

    # --- Save encryption (opzionale, FASE 1 §1.3) ---
    save_encryption_key: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Restituisce l'istanza singleton delle settings."""
    return Settings()
