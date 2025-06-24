#!/usr/bin/env python3
"""
# artifacts-keyring library

Keyring extension, that automatically retrieves credentials for Azure Artifacts.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

# version
try:
    from ._version import __version__, __version_tuple__, version
except ImportError:
    __version__ = version = "0.0.0"
    __version_tuple__ = (0, 0, 0)

from .logging_config import configure_logging

configure_logging()
