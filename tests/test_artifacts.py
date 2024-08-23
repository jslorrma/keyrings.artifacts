#!/usr/bin/env python3
"""
tests/test_artifacts.py
------------------------

Unit tests for the ArtifactsKeyringBackend class in the keyrings_artifacts package.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import logging
import sys

import pytest

from keyrings_artifacts.artifacts import ArtifactsKeyringBackend


@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout)

@pytest.fixture(scope="module")
def keyring_backend():
    return ArtifactsKeyringBackend()

@pytest.fixture(autouse=True)
def get_credentials(mocker, username, password):
    """
    Mock the get_credentials method of the CredentialProvider class.
    """
    mocker.patch('keyrings_artifacts.provider.CredentialProvider.get_credentials', return_value=(username, password))

@pytest.mark.parametrize("service, username, password", [
    ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload", "username1", "password1"),
    ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload1", "username2", "password2"),
    ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload2", "username3", "password3"),
])
def test_get_password(keyring_backend, service, username, password):
    # Retrieve the password
    retrieved_password = keyring_backend.get_password(service, username)

    # Compare the set and retrieved passwords
    assert retrieved_password == password, f"Expected {password}, got {retrieved_password}"

@pytest.mark.parametrize("service, username, password", [
    ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload", "username1", "password1"),
    ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload1", "username2", "password2"),
    ("https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload2", "username3", "password3"),
])
def test_delete_password(keyring_backend, service, username, password):
    # Delete the password
    keyring_backend.delete_password(service, username)

    # Check that the password has been deleted
    deleted_password = keyring_backend._LOCAL_BACKEND.get_password(service, username)
    assert deleted_password is None, f"Expected None, got {deleted_password}"
