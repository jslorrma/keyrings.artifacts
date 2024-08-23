#!/usr/bin/env python3
"""
keyrings_artifacts/artifacts.py
---------------------------

Azure Artifacts keyring backend.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import os
import warnings
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

import keyring.credentials

from .provider import CredentialProvider


class ArtifactsKeyringBackend(keyring.backend.KeyringBackend):
    """
    Azure Artifacts keyring backend.

    This backend provides authentication for publishing or consuming Python packages to or from
    Azure Artifacts feeds within [Azure DevOps](https://azure.com/devops). Credentials are retrieved
    from environment variables, managed identity, the Azure CLI, shared token cache, or the device
    code flow.
    """

    SUPPORTED_NETLOC = ("pkgs.dev.azure.com", "pkgs.visualstudio.com", "pkgs.codedev.ms", "pkgs.vsts.me")
    _PROVIDER = CredentialProvider

    __LOCAL_BACKEND = None

    priority = 9.9

    @property
    def _LOCAL_BACKEND(self):
        """
        Get the local keyring backend.
        """
        # if we fall back to the local backend, we don't want to loop infinitely
        # so we set the priority to -1 to prevent it from being selected again
        if self.__LOCAL_BACKEND is not None:
            return self.__LOCAL_BACKEND

        _self = next(
            kr for kr in keyring.backend.get_all_keyring() if kr.__class__.__name__ == "ArtifactsKeyringBackend"
        )
        _self.priority = -1
        self.__LOCAL_BACKEND = keyring.get_keyring()
        return self.__LOCAL_BACKEND

    def __init__(self):
        self._cache = {}

    def get_credential(self, service: str, username: str | None) -> keyring.credentials.SimpleCredential | None:
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
            warnings.warn(str(exc))  # noqa: B028
            return None

        netloc = parsed.netloc.rpartition("@")[-1]

        if netloc is None or not netloc.endswith(self.SUPPORTED_NETLOC):
            return None

        provider = self._PROVIDER()
        use_bearer_token = os.getenv(provider._USE_BEARER_TOKEN_VAR_NAME, "False").lower() == "true"

        if not use_bearer_token and username:
            # Check if credentials are already stored in the local keyring
            stored_password = self._LOCAL_BACKEND.get_password(service, username)

            if stored_password and provider._can_authenticate(service, (self._PROVIDER.username, stored_password)):
                return keyring.credentials.SimpleCredential(username, stored_password)

        # else or if the stored password is not valid, try to retrieve the credentials from the provider
        username, password = provider.get_credentials(service)

        if username and password:
            if not use_bearer_token:
                # Store the retrieved username and PAT in the local keyring
                self._LOCAL_BACKEND.set_password(service, username, password)
                self._cache[service, username] = password
            return keyring.credentials.SimpleCredential(username, password)

    def get_password(self, service: str, username: str) -> str | None:
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
        password = self._cache.get((service, username), None)
        if password is not None:
            return password

        creds = self.get_credential(service, username)
        if creds and username == creds.username:
            return creds.password

        return None

    def set_password(self, service: str, username: str, password: str) -> None:
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
        self._LOCAL_BACKEND.delete_password(service, username)


if TYPE_CHECKING:
    ArtifactsKeyringBackend()
