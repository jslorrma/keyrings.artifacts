#!/usr/bin/env python3
"""
artifacts_keyring/crpyt_file.py
---------------------------

This module provides an encrypted keyring backend.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import hashlib
import subprocess
from typing import TYPE_CHECKING

from keyrings.alt.file import EncryptedKeyring


def run_command(command: str) -> str:
    """
    Run a command and return the output.
    """
    return subprocess.check_output(command, shell=True).decode("utf-8").strip()


class EncryptedKeyring_(EncryptedKeyring):
    """
    Encrypted keyring backend.

    This backend provides a keyring that stores credentials in an encrypted file. The file is
    encrypted using the Fernet symmetric encryption algorithm. The encryption key is derived from
    a password generated from system and hardware information.
    """

    priority = 3

    @property
    def _password(self):
        _mac_address_if = run_command("ifconfig | grep ether | head -n 1 | awk '{print $2}'")
        _mac_address_ip = run_command("ip addr | grep ether | head -n 1 | awk '{print $2}'")
        _hostname = run_command("hostname")
        _uname = run_command("uname -a")
        _whoami = run_command("whoami")

        return hashlib.sha256(f"{_mac_address_if}{_mac_address_ip}{_hostname}{_uname}{_whoami}".encode()).digest()

    def _get_new_password(self):
        return self._password

    def _unlock(self):
        """
        Unlock this keyring by getting the password for the keyring from the
        user.
        """
        self.keyring_key = self._password
        try:
            ref_pw = self.get_password("keyring-setting", "password reference")
            assert ref_pw == "password reference value"
        except AssertionError:
            self._lock()
            raise ValueError("Incorrect Password")  # noqa: B904


if TYPE_CHECKING:
    EncryptedKeyring_()
