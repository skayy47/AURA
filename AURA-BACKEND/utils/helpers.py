from __future__ import annotations

import logging

_LOGGER_CACHE: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Central logger factory with simple console formatting."""
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    _LOGGER_CACHE[name] = logger
    return logger
