from __future__ import annotations

import logging
import os
import sys


def create_logger(level: str | None = None, logger_name: str = "atlas") -> None:

    format = "%(asctime)s %(levelname)s %(name)s:%(lineno)d - %(message)s"

    log_level = level or os.environ.get("LOG_LEVEL", "INFO")
    formatter = logging.Formatter(fmt=format, datefmt="%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger(logger_name)
    root_logger.setLevel(getattr(logging, log_level.upper()))
    if root_logger.handlers:
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.propagate = False
