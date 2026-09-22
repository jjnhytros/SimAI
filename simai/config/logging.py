"""Configurazione Loguru per SimAI."""

import sys

from loguru import logger

from simai.config.settings import Settings

_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)


def configure_logging(settings: Settings) -> None:
    """Configura Loguru: sink su file sempre attivo, stderr solo se debug."""
    logger.remove()

    if settings.debug:
        logger.add(
            sys.stderr,
            level=settings.log_level,
            format=_LOG_FORMAT,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    log_dir = settings.logs_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "simai.log"

    logger.add(
        log_file,
        level=settings.log_level,
        format=_LOG_FORMAT,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        backtrace=settings.debug,
        diagnose=settings.debug,
    )
