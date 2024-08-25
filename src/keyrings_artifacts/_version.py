#!/usr/bin/env python3
"""
artifacts-keyring version file
------------------------------
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

TYPE_CHECKING = False
if TYPE_CHECKING:
    VERSION_TUPLE = tuple[int | str, ...]

version: str
__version__: str
__version_tuple__: VERSION_TUPLE
version_tuple: VERSION_TUPLE

__version__ = "0.4.1"  # version string
vesion = __version__
__version_tuple__ = version_tuple = tuple(int(n) for n in __version__.split(".") if n.isdigit())
