from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SIMAI_",
        extra="ignore",
    )

    db_url: str = "sqlite:///data/simai.db"
    log_level: str = "INFO"
    debug: bool = False
    master_seed: int = 42
    tick_minutes: int = 60
    data_dir: Path = Path("data")
    saves_dir: Path = Path("data/saves")
    logs_dir: Path = Path("data/logs")


settings = Settings()
