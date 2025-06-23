#!/usr/bin/env python3
"""
# tests/test_artifacts.py

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
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


@pytest.fixture(scope="module")
def keyring_backend():
    return ArtifactsKeyringBackend()


@pytest.fixture(autouse=True)
def patch_get_credentials(mocker, request):  # noqa: ANN001
    # Patch get_credentials to return the username and password from the test parameters if available
    def _get_credentials(service, username=None, *_args, **_kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        # Try to get username/password from the test function's parameters
        params = getattr(request, "param", None)
        if params and isinstance(params, list | tuple) and len(params) >= 3:  # noqa: PLR2004
            return params[1], params[2]
        # Fallback: try to get from request.node.funcargs
        funcargs = getattr(request.node, "funcargs", {})
        u = funcargs.get("username", "username")
        p = funcargs.get("password", "password")
        return u, p

    mocker.patch(
        "keyrings_artifacts.provider.CredentialProvider.get_credentials",
        side_effect=_get_credentials,
    )


@pytest.mark.parametrize(
    "service, username, password",
    [
        (
            "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/simple",
            "username1",
            "password1",
        ),
        (
            "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload",
            "username2",
            "password2",
        ),
        (
            "https://pkgs.dev.azure.com/org1/project1/_packaging/feed/pypi/simple",
            "username3",
            "password3",
        ),
    ],
)
def test_get_password(keyring_backend, service, username, password):  # noqa: ANN001
    # Retrieve the password
    retrieved_password = keyring_backend.get_password(service, username)

    # Compare the set and retrieved passwords
    assert retrieved_password == password, f"Expected {password}, got {retrieved_password}"


@pytest.mark.parametrize(
    "service, username, password",
    [
        (
            "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/simple",
            "username1",
            "password1",
        ),
        (
            "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload",
            "username2",
            "password2",
        ),
        (
            "https://pkgs.dev.azure.com/org1/project1/_packaging/feed/pypi/simple",
            "username3",
            "password3",
        ),
    ],
)
def test_delete_password(keyring_backend, service, username, password):  # noqa: ANN001
    # Delete the password
    keyring_backend.delete_password(service, username)

    # Check that the password has been deleted
    deleted_password = keyring_backend._local_backend.get_password(service, username)  # noqa: SLF001
    assert deleted_password is None, f"Expected None, got {deleted_password}"


@pytest.mark.parametrize(
    "service_url",
    [
        "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/simple/pkg1.wheel-1.0.0-py3-none-any.whl",
        "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload/pkg1.wheel-1.0.0-py3-none-any.whl",
        "https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/simple/pkg2.wheel-1.1.0-py3-none-any.whl",
    ],
)
def test_normalize_service_url(keyring_backend, service_url, patch_get_credentials):  # noqa: ANN001
    # Canonical pattern
    m_url = keyring_backend._normalize_service_url(service_url)  # noqa: SLF001
    assert m_url.startswith("https://pkgs.dev.azure.com/"), (
        f"Expected URL to start with 'https://pkgs.dev.azure.com/', got {m_url}"
    )
    assert m_url.endswith(("/pypi/simple", "/pypi/upload")), (
        f"Expected URL to end with '/pypi/simple' or '/pypi/upload', got {m_url}"
    )
    assert all(p in m_url for p in ("org", "project", "feed")), (
        f"Expected URL to contain 'org', 'project', and 'feed', got {m_url}"
    )
