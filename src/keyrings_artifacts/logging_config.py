"""
keyrings_artifacts/logging_config.py

Logging configuration for keyrings_artifacts package.

Respects environment variables:
- KEYRINGS_ARTIFACTS_LOGLEVEL: set log level (e.g., DEBUG, INFO, WARNING)
- KEYRINGS_ARTIFACTS_LOGFILE: set log file path (if not set, logs to stderr)
"""

import logging
import os

_LOGGER_INITIALIZED = False


def configure_logging() -> None:
    """Configure logging for the keyrings_artifacts package.

    Respects environment variables:
    - KEYRINGS_ARTIFACTS_LOGLEVEL: set log level (e.g., DEBUG, INFO, WARNING)
    - KEYRINGS_ARTIFACTS_LOGFILE: set log file path (if not set, logs to stderr)
    """
    if globals().get("_LOGGER_INITIALIZED", False):
        return
    loglevel = os.getenv("KEYRINGS_ARTIFACTS_LOGLEVEL", "WARNING").upper()
    logfile = os.getenv("KEYRINGS_ARTIFACTS_LOGFILE")
    handlers = [logging.StreamHandler()] if not logfile else [logging.FileHandler(logfile)]
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=handlers,
    )
    globals()["_LOGGER_INITIALIZED"] = True
