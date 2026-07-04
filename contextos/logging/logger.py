"""Central logging setup for ContextOS Core."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

from contextos.config import SETTINGS


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOGGER_NAME = "contextos"


def configure_logging(
    *,
    debug: bool | None = None,
    log_file: str | Path | None = None,
    console: bool = True,
) -> logging.Logger:
    """Configure ContextOS logging with rotating file and optional console output."""

    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()
    logger.propagate = False

    debug_enabled = SETTINGS.logging.debug if debug is None else debug
    level = logging.DEBUG if debug_enabled else getattr(logging, SETTINGS.logging.level.upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)
    file_path = Path(log_file) if log_file is not None else SETTINGS.logging.file_path
    if str(file_path) != "":
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=SETTINGS.logging.max_bytes,
            backupCount=SETTINGS.logging.backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a ContextOS child logger."""

    logger_name = LOGGER_NAME if name is None else f"{LOGGER_NAME}.{name}"
    logger = logging.getLogger(logger_name)
    if not logging.getLogger(LOGGER_NAME).handlers:
        configure_logging(console=False)
    return logger
