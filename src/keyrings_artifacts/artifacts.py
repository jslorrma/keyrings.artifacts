#!/usr/bin/env python3
"""
# keyrings_artifacts/artifacts.py

Azure Artifacts keyring backend.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import logging
import os
import re
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

import keyring.credentials

from .provider import CredentialProvider

logger = logging.getLogger(__name__)


class ArtifactsKeyringBackend(keyring.backend.KeyringBackend):
    """
    Azure Artifacts keyring backend.

    This backend provides authentication for publishing or consuming Python packages to or from
    Azure Artifacts feeds within [Azure DevOps](https://azure.com/devops). Credentials are retrieved
    from environment variables, managed identity, the Azure CLI, shared token cache, or the device
    code flow.
    """

    SUPPORTED_NETLOC = (
        "pkgs.dev.azure.com",
        "pkgs.visualstudio.com",
        "pkgs.codedev.ms",
        "pkgs.vsts.me",
    )
    _PROVIDER = CredentialProvider

    __local_backend: keyring.backend.KeyringBackend | None = None

    priority = 9.9

    @property
    def _local_backend(self) -> keyring.backend.KeyringBackend:
        """Get the local keyring backend."""
        # if we fall back to the local backend, we don't want to loop infinitely
        # so we set the priority to -1 to prevent it from being selected again
        if self.__local_backend is not None:
            return self.__local_backend

        _self = next(
            kr
            for kr in keyring.backend.get_all_keyring()
            if kr.__class__.__name__ == "ArtifactsKeyringBackend"
        )
        _self.priority = -1
        self.__local_backend = keyring.get_keyring()
        return self.__local_backend

    def __init__(self):
        self._cache = {}
        logger.debug("ArtifactsKeyringBackend initialized.")

    def _normalize_service_url(self, service_url: str) -> str:
        logger.debug("Normalizing service URL: %r", service_url)
        """
        Normalize the service URL to Azure Artifacts PyPI feed pattern.

        Parameters
        ----------
        service_url : str
            The service URL to normalize.

        Returns
        -------
        str
            The normalized service URL if it matches the Azure Artifacts PyPI feed pattern,
            otherwise returns the original service URL.
        """
        try:
            parsed = urlsplit(service_url)
            netloc = parsed.netloc.rpartition("@")[-1]
            if not any(netloc.endswith(suffix) for suffix in self.SUPPORTED_NETLOC):
                logger.debug("Service URL %r not supported, returning as is.", service_url)
                return service_url
            # Regex to match the canonical Azure Artifacts PyPI feed URL with endpoint
            # Example: https://pkgs.dev.azure.com/ORG/PROJ/_packaging/FEED/pypi/upload or .../simple
            pattern = r"^/(?P<org>[^/]+)/(?P<proj>[^/]+)/_packaging/(?P<feed>[^/]+)/pypi/(?P<endpoint>upload|simple)"
            match = re.match(pattern, parsed.path)
            if match:
                new_path = (
                    f"/{match.group('org')}/"
                    f"{match.group('proj')}/_packaging/"
                    f"{match.group('feed')}/pypi/"
                    f"{match.group('endpoint')}"
                )
                normalized = f"{parsed.scheme}://{netloc}{new_path}"
                logger.debug("Normalized service URL: %r", normalized)
                return normalized
            logger.debug("Service URL %r did not match pattern, returning as is.", service_url)
            return service_url
        except Exception as exc:
            logger.exception("Exception normalizing service URL: %r", exc)
            return service_url

    def get_credential(
        self, service: str, username: str | None
    ) -> keyring.credentials.SimpleCredential | None:
        logger.debug("Requesting credentials for service=%r, username=%r", service, username)
        """
        Retrieve credentials for a given service.

        Parameters
        ----------
        service : str
            The service URL.
        username : Optional[str]
            The username for the service.

        Returns
        -------
        Optional[keyring.credentials.SimpleCredential]
            The credentials for the service, or None if not found.
        """
        try:
            parsed = urlsplit(service)
        except Exception as exc:
            logger.warning("Failed to parse service URL %r: %s", service, exc)
            return None
        netloc = parsed.netloc.rpartition("@")[-1]
        if netloc is None or not netloc.endswith(self.SUPPORTED_NETLOC):
            logger.debug("Netloc %r not supported.", netloc)
            return None
        provider = self._PROVIDER()
        use_bearer_token = os.getenv(provider._USE_BEARER_TOKEN_VAR_NAME, "False").lower() == "true"  # noqa: SLF001
        if not use_bearer_token and username:
            stored_password = self._local_backend.get_password(service, username)
            if stored_password and provider._can_authenticate(  # noqa: SLF001
                service, (self._PROVIDER.username, stored_password)
            ):
                logger.debug(
                    "Using stored credentials for service=%r, username=%r", service, username
                )
                return keyring.credentials.SimpleCredential(username, "***hidden***")
        username_prov, password_prov = provider.get_credentials(service)
        logger.debug(
            "Provisioned credentials for service=%r, username=%r (credential value hidden)",
            service,
            username_prov,
        )
        if username_prov and password_prov:
            if not use_bearer_token:
                self._local_backend.set_password(service, username_prov, password_prov)
                self._cache[service, username_prov] = password_prov
            return keyring.credentials.SimpleCredential(username_prov, "***hidden***")

    def get_password(self, service: str, username: str) -> str | None:
        logger.debug("Getting password for service=%r, username=%r", service, username)
        """
        Retrieve the password for a given service and username.

        Parameters
        ----------
        service : str
            The service URL.
        username : str
            The username for the service.

        Returns
        -------
        Optional[str]
            The password for the service, or None if not found.
        """
        normalized_service = self._normalize_service_url(service)
        password = self._cache.get((normalized_service, username), None)
        if password is not None:
            logger.debug(
                "Password found in cache for service=%r, username=%r", normalized_service, username
            )
            return password
        creds = self.get_credential(normalized_service, username)
        if creds and username == creds.username:
            logger.debug(
                "Password retrieved for service=%r, username=%r", normalized_service, username
            )
            return None if creds.password == "***hidden***" else creds.password
        logger.debug("No password found for service=%r, username=%r", normalized_service, username)
        return None

    def set_password(self, service: str, username: str, password: str) -> None:
        logger.debug(
            "set_password called for service=%r, username=%r (not implemented)", service, username
        )
        """
        Set the password for a given service and username.

        Parameters
        ----------
        service : str
            The service URL.
        username : str
            The username for the service.
        password : str
            The password to set.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        # Defer setting a password to the next backend
        raise NotImplementedError()

    def delete_password(self, service: str, username: str) -> None:
        logger.debug("delete_password called for service=%r, username=%r", service, username)
        """
        Delete the password for a given service and username.

        Parameters
        ----------
        service : str
            The service URL.
        username : str
            The username for the service.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        self._local_backend.delete_password(service, username)


if TYPE_CHECKING:
    ArtifactsKeyringBackend()
