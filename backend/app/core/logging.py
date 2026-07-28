from __future__ import annotations

import logging
import sys

from loguru import logger


def configure_logging() -> None:
    """Configure structured application logging with Loguru."""
    logging.getLogger().handlers.clear()
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
