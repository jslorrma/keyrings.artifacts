#!/usr/bin/env python3
"""
# keyrings_artifacts/crpyt_file.py

This module provides an encrypted keyring backend.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import contextlib
import pathlib
import subprocess
from typing import TYPE_CHECKING

from keyrings.alt.file import EncryptedKeyring

_KEYGEN_SCRIPT = """
# Gather CPU information
cpu_id=$(lscpu | grep "Model name" | awk -F: '{print $2}' | xargs)

# Gather MAC address using ifconfig (first network interface)
mac_address_if=$(ifconfig | grep ether | head -n 1 | awk '{print $2}')

# Gather MAC address using ip (first network interface)
mac_address_ip=$(ip addr | grep ether | head -n 1 | awk '{print $2}')

# Gather hostname
hostname=$(hostname)

# Gather operating system name
uname_o=$(uname -o)

# Gather machine hardware name
uname_m=$(uname -m)

# Gather current username
whoami=$(whoami)

# Combine the information
combined_info="${cpu_id}_${mb_serial}_${disk_serial}_${mac_address_if}_${mac_address_ip}_${hostname}_${uname_o}_${uname_m}_${whoami}"

# Generate a unique hashed key using SHA-256
unique_key=$(echo -n "$combined_info" | sha256sum | awk '{print $1}')

# Output the unique key
echo "$unique_key"
"""


class _EncryptedKeyring(EncryptedKeyring):
    """
    Encrypted keyring backend.

    This backend provides a keyring that stores credentials in an encrypted file. The file is
    encrypted using the Fernet symmetric encryption algorithm. The encryption key is derived from
    a password generated from system and hardware information.
    """

    filename = "artifacts_keyring.cfg"
    priority = 3

    @property
    def _password(self) -> str:
        _command = f"bash -c '{_KEYGEN_SCRIPT}'"
        return (
            subprocess.run(_command, shell=True, capture_output=True, check=False)
            .stdout.decode("utf-8")
            .strip()
        )

    def _get_new_password(self) -> str:
        return self._password

    def _unlock(self) -> None:
        """Unlock this keyring by getting the password for the keyring from the user.

        This method retrieves the password from the keyring using the `get_password` method.
        If the password reference does not match the expected value, it reinitializes the keyring
        by deleting the existing file and calling `_init_file()`.

        Raises
        ------
        ValueError
            If the password reference does not match the expected value, indicating a mismatch
            in the hardware information or an incorrect password.

        """
        self.keyring_key = self._password
        try:
            ref_pw = self.get_password("keyring-setting", "password reference")
            if ref_pw != "password reference value":
                # keyring_key is generated from system and hardware information, so this can
                # only happen if hardware information has changed, which is unlikely. But if it
                # does happen, we need to initialize the keyring again.

                with contextlib.suppress(FileNotFoundError):
                    pathlib.Path(self.file_path).unlink()
                self._init_file()
        except AssertionError:
            self._lock()
            raise ValueError("Incorrect Password")  # noqa: B904


if TYPE_CHECKING:
    _EncryptedKeyring()
