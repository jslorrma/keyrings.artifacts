#!/usr/bin/env python3
"""
keyrings_artifacts/plugin.py
---------------------------

This module implements the CredentialProvider class which is a Azure credential providers for
authenticating with Azure DevOps Artifacts.
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import logging
import os
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import requests
from azure.core.exceptions import ClientAuthenticationError
from requests.exceptions import HTTPError, RequestException

from .support import AzureCredentialWithDevicecode

logging.getLogger("azure.identity._credentials.managed_identity").setLevel(logging.ERROR)
logging.getLogger("azure.identity._credentials.environment").setLevel(logging.ERROR)
logging.getLogger("azure.identity._credentials.vscode").setLevel(logging.ERROR)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)


class CredentialProvider:
    """
    Keyring plugin for Azure DevOps Artifacts.

    This plugin provides credentials for Azure DevOps Artifacts.
    """

    # Non-interactive mode global variable
    _NON_INTERACTIVE_VAR_NAME = "keyrings_artifacts_NONINTERACTIVE_MODE"

    # ADO global variables
    _PAT_ENV_VAR = "AZURE_DEVOPS_EXT_PAT"
    _ADO_USERNAME_ENV_VAR = "AZURE_DEVOPS_USERNAME"
    _PAT_SCOPE_ENV_VAR = "AZURE_DEVOPS_PAT_SCOPE"
    _PAT_DURATION_ENV_VAR = "AZURE_DEVOPS_PAT_DURATION"

    # from https://github.com/microsoft/artifacts-credprovider/blob/cdc427e8236212b33041b4276961855b39bbe98d/CredentialProvider.Microsoft/CredentialProviders/Vsts/MSAL/MsalTokenProviderFactory.cs#L11
    _OAUTH_CLIENT_ID = "872cd9fa-d31f-45e0-9eab-6e460a02d1f1"
    _OUATH_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"

    # PAT global variables
    # PAT API route
    _TOKEN_API_ROUTE = "/_apis/tokens/pats?api-version=7.1-preview.1"
    # User-Agent for the request
    _USER_AGENT = "PyMSALCredentialProvider"
    # Display name for the PAT
    _DISPLAY_NAME = "Azure DevOps Artifacts Credential Provider"
    # PAT duration in days
    _DEFAULT_PAT_DURATION = 365
    # Default username for the credentials
    _DEFAULT_USERNAME = "VssSessionToken"
    # Default PAT scope
    _DEFAULT_VSTS_SCOPE = "vso.packaging_write"

    def __init__(self) -> None:
        self._oauth_authority: str | None = None
        self._vsts_authority: str | None = None

    @property
    def username(self) -> str | None:
        """Get the username."""
        return os.getenv(self._ADO_USERNAME_ENV_VAR, self._DEFAULT_USERNAME)

    def _is_upload_endpoint(self, url: str) -> bool:
        """Check if the given URL is the upload endpoint."""
        url = url[:-1] if url[-1] == "/" else url
        return url.endswith("pypi/upload")

    def _can_authenticate(self, url: str, auth: tuple[str, str] | None) -> bool:
        """Check if the given URL can be authenticated with the given credentials."""
        response = requests.get(url, auth=auth)

        return response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR and response.status_code not in (
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.FORBIDDEN,
        )

    def _get_authorities(self, url: str) -> tuple[str, str]:
        """Send a GET to the url and parse the response header"""
        # send GET request
        response = requests.get(url)
        headers = response.headers

        # extract oauth authority
        bearer_authority = headers["WWW-Authenticate"].split(",")[0].replace("Bearer authorization_uri=", "")

        # extract Visual Studo authority
        pat_authority = headers["X-VSS-AuthorizationEndpoint"]
        return bearer_authority, pat_authority

    def _get_bearer_token(
        self, authority: str, client_id: str, tenant_id: str, exclude_shared_token_cache: bool, scope: str
    ) -> str:
        """
        Get the bearer token for the given URL.

        This method is used to get the bearer token for the given URL. The token is obtained
        using the AzureCredentialWithDevicecode class which tries to optain the token from:
        1) Azure CLI
        2) Shared Token Cache
        3) Interactive Browser
        4) DeviceCode flow
        """
        _non_interactive = (os.getenv(self._NON_INTERACTIVE_VAR_NAME, "False").lower() == "true",)
        try:
            token = (
                AzureCredentialWithDevicecode(
                    tenant_id=tenant_id,
                    authority=authority,
                    devicecode_client_id=client_id,
                    non_interactive=_non_interactive,
                )
                .get_token(scope)
                .token
            )
        except ClientAuthenticationError as e:
            if "Azure Active Directory error" not in str(e):
                raise e
            #
            # DefaultAzureCredential raises an exception when there is a token
            # found in the cache but the token has expired. This issue has
            # been raised https://github.com/Azure/azure-sdk-for-python/issues/21718#issuecomment-974225195
            # and it is a design choice of the azure-identity developers. However,
            # for our use case, the fallback below requires user intervention and therefore
            # the concerns about accidentally operating on the incorrect account are not
            # applicable. Hence we explicitly catch the error and initiate the
            # DeviceCode flow. This behaviour is the same as re-running the command
            # with `MSAL_EXCLUDE_SHARED_TOKEN_CACHE=True`, which has the same effect as
            # the suggestion linked in the GH issue above.
            #
            print(f"Caught {e.__class__}: {e!s}! Falling back to Interactive Browser flow.")
            token = (
                AzureCredentialWithDevicecode(
                    authority=authority,
                    tenant_id=tenant_id,
                    client_id=client_id,
                    with_az_cli=False,
                    non_interactive=_non_interactive,
                )
                .get_token(scope)
                .token
            )
        return token

    def _exchange_bearer_for_pat(self, bearer_token: str) -> str:
        """Exchange the bearer token for a personal access token (PAT)."""
        try:
            # Build request headers
            request_headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
                "User-Agent": self._USER_AGENT,
            }

            # Build the request URL
            visual_studio_url = f"{self._vsts_authority.rstrip('/')}/{self._TOKEN_API_ROUTE.lstrip('/')}"

            # Build the request payload
            _delta = timedelta(days=int(os.getenv(self._PAT_DURATION_ENV_VAR, self._DEFAULT_PAT_DURATION)))
            expiry = (datetime.now(timezone.utc) + _delta).strftime("%Y-%m-%dT%H:%M:%SZ")

            request_payload = {
                "displayName": self._DISPLAY_NAME,
                "scope": os.getenv(self._PAT_SCOPE_ENV_VAR, self._DEFAULT_VSTS_SCOPE),
                "validTo": expiry,
                "allOrgs": "false",
            }

            # Send request
            with requests.post(visual_studio_url, headers=request_headers, json=request_payload) as response:
                response.raise_for_status()  # Raise an HTTPError for bad responses
                response_data = response.json()

            return response_data["patToken"]["token"]

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            raise
        except RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            raise
        except KeyError as key_err:
            print(f"Key error occurred: {key_err}")
            raise
        except Exception as err:
            print(f"An error occurred: {err}")
            raise

    def _get_credentials_from_credential_provider(self, url: str) -> tuple[str | None, str | None]:
        """Get the credentials from the credential provider."""

        # get authorities
        self._oauth_authority, self._vsts_authority = self._get_authorities(url)
        # split oauth authority to get tenant_id
        authority, _, tenant_id = self._oauth_authority.rpartition("/")
        # exclude shared token cache
        self._exclude_shared_token_cache = str(os.getenv("MSAL_EXCLUDE_SHARED_TOKEN_CACHE", "False")).lower() == "true"

        bearer_token = self._get_bearer_token(
            authority=authority,
            client_id=self._OAUTH_CLIENT_ID,
            tenant_id=tenant_id,
            exclude_shared_token_cache=self._exclude_shared_token_cache,
            scope=self._OUATH_SCOPE,
        )
        pat = self._exchange_bearer_for_pat(bearer_token)

        username = os.getenv(self._ADO_USERNAME_ENV_VAR, self._DEFAULT_USERNAME)
        password = pat
        return username, password

    def get_credentials(self, url: str) -> tuple[str | None, str | None]:
        """
        Get the credentials for the given URL.

        Parameters
        ----------
        url : str
            The URL for which to get the credentials.

        Returns
        -------
        tuple[str | None, str | None]
            The username and password for the given URL.
        """
        # Public feed short circuit: return nothing if not getting credentials for the upload endpoint
        # (which always requires auth) and the endpoint is public (can authenticate without credentials).
        if not self._is_upload_endpoint(url) and self._can_authenticate(url, None):
            return None, None

        # Return personal access token if available
        if os.environ.get(self._PAT_ENV_VAR):
            return os.getenv(self._ADO_USERNAME_ENV_VAR, self._DEFAULT_USERNAME), os.environ.get(self._PAT_ENV_VAR)

        # Getting credentials with IsRetry=false; the credentials may come from the cache
        username, password = self._get_credentials_from_credential_provider(url)

        # Do not attempt to validate if the credentials could not be obtained
        if username is None or password is None:
            return username, password

        # Make sure the credentials are still valid (i.e. not expired)
        if self._can_authenticate(url, (username, password)):
            return username, password

        # Return None if the credentials are invalid
        return None, None
