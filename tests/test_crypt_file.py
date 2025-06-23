#!/usr/bin/env python3
"""
# tests/test_crypt_file.py

Unit tests for the EncryptedKeyring_ class in the keyrings_artifacts package.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import pytest

from keyrings_artifacts.crypt_file import _EncryptedKeyring


@pytest.fixture(scope="module")
def keyring():
    return _EncryptedKeyring()


def test_encrypted_keyring_initialization(keyring):  # noqa: ANN001
    assert keyring is not None


@pytest.mark.parametrize(
    "service, username, password",
    [
        (
            "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload",
            "username1",
            "password1",
        ),
        (
            "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload1",
            "username2",
            "password2",
        ),
        (
            "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload2",
            "username3",
            "password3",
        ),
    ],
)
def test_encrypted_keyring_set_and_get_password(keyring, service, username, password):  # noqa: ANN001
    # Set the password
    keyring.set_password(service, username, password)
    # Retrieve the password
    retrieved_password = keyring.get_password(service, username)
    # Compare the set and retrieved passwords
    assert retrieved_password == password, f"Expected {password}, got {retrieved_password}"


@pytest.mark.parametrize(
    "service, username",
    [
        ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload", "username1"),
        ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload1", "username2"),
        ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload2", "username3"),
    ],
)
def test_encrypted_keyring_delete_password(keyring, service, username):  # noqa: ANN001
    # Delete the password
    keyring.delete_password(service, username)
    # Check that the password has been deleted
    deleted_password = keyring.get_password(service, username)
    assert deleted_password is None, f"Expected None, got {deleted_password}"
