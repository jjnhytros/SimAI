import sys

from loguru import logger

from simai.config.settings import settings


def configure_logging() -> None:
    logger.remove()
    logger.add(sys.stderr, level=settings.log_level)

    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        settings.logs_dir / "simai.log",
        rotation="1 day",
        retention="30 days",
        level=settings.log_level,
    )
