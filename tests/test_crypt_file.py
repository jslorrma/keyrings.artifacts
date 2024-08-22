#!/usr/bin/env python3
"""
tests/test_crypt_file.py
------------------------

Unit tests for the EncryptedKeyring_ class in the artifacts_keyring package.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import pytest

from keyrings_artifacts.crypt_file import EncryptedKeyring_


@pytest.fixture(scope="module")
def keyring():
    return EncryptedKeyring_()

def test_encrypted_keyring_initialization(keyring):
    assert keyring is not None

@pytest.mark.parametrize("service, username, password", [
    ("service1", "username1", "password1"),
    ("service2", "username2", "password2"),
    ("service3", "username3", "password3"),
])
def test_encrypted_keyring_set_and_get_password(keyring, service, username, password):
    # Set the password
    keyring.set_password(service, username, password)
    # Retrieve the password
    retrieved_password = keyring.get_password(service, username)
    # Compare the set and retrieved passwords
    assert retrieved_password == password, f"Expected {password}, got {retrieved_password}"


@pytest.mark.parametrize("service, username", [
    ("service1", "username1"),
    ("service2", "username2"),
    ("service3", "username3"),
])
def test_encrypted_keyring_delete_password(keyring, service, username):
    # Delete the password
    keyring.delete_password(service, username)
    # Check that the password has been deleted
    deleted_password = keyring.get_password(service, username)
    assert deleted_password is None, f"Expected None, got {deleted_password}"
