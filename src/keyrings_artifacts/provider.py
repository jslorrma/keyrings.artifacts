#!/usr/bin/env python3
"""
keyrings_artifacts/provider.py
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
import re
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import requests
from azure.core.exceptions import ClientAuthenticationError
from requests.exceptions import HTTPError, RequestException

from .support import AzureCredentialWithDevicecode

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.getLogger("azure.identity._credentials.managed_identity").setLevel(logging.ERROR)
logging.getLogger("azure.identity._credentials.environment").setLevel(logging.ERROR)
logging.getLogger("azure.identity._credentials.vscode").setLevel(logging.ERROR)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)


class CredentialProvider:
    """
    Credential provider for Azure DevOps Artifacts.

    This plugin provides credentials for Azure DevOps Artifacts.
    """

    # Non-PAT, bearer token mode
    _USE_BEARER_TOKEN_VAR_NAME = "KEYRINGS_ARTIFACTS_USE_BEARER_TOKEN"

    # ADO global variables
    _PAT_ENV_VAR = "AZURE_DEVOPS_EXT_PAT"
    _ADO_USERNAME_ENV_VAR = "AZURE_DEVOPS_USERNAME"
    _PAT_SCOPE_ENV_VAR = "AZURE_DEVOPS_PAT_SCOPE"
    _PAT_DURATION_ENV_VAR = "AZURE_DEVOPS_PAT_DURATION"

    # Azure DevOps application default scope
    # from https://github.com/microsoft/artifacts-credprovider/blob/cdc427e8236212b33041b4276961855b39bbe98d/CredentialProvider.Microsoft/CredentialProviders/Vsts/MSAL/MsalTokenProviderFactory.cs#L11
    _OAUTH_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"

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

    @property
    def username(self) -> str | None:
        """Get the username."""
        return os.getenv(self._ADO_USERNAME_ENV_VAR, self._DEFAULT_USERNAME)

    def _is_upload_endpoint(self, url: str) -> bool:
        """Check if the given URL is the upload endpoint."""
        return url.rstrip('/').endswith("pypi/upload")

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

        # extract oauth authority and tenant_id
        match = re.search(r'Bearer authorization_uri=(https://[^/]+/)[^,]+', headers["WWW-Authenticate"])
        if match:
            bearer_authority = match.group(1)
            tenant_id = match.group(0).rsplit("/",1)[1]
        else:
            # the Azure DevOps endpoint seems to be linked to a personal Microsoft account
            # and only basic authentication or PAT is supported
            bearer_authority = ""
            tenant_id = ""
        return bearer_authority, tenant_id, headers["X-VSS-AuthorizationEndpoint"]

    def _get_bearer_token(
        self, authority: str, tenant_id: str, scope: str
    ) -> str:
        """
        Get the bearer token for the given URL.

        This method is used to get the bearer token for the given URL. The token is obtained
        using the AzureCredentialWithDevicecode class which tries to optain the token from:
        1) Environment variables
        2) Azure CLI
        3) Shared Token Cache
        4) Interactive Browser
        5) DeviceCode flow
        """
        try:
            token = (
                AzureCredentialWithDevicecode(
                    tenant_id=tenant_id,
                    authority=authority
                )
                .get_token(scope)
                .token
            )
        except ClientAuthenticationError as e:
            if "Azure Active Directory error" not in str(e):
                raise e
            # DefaultAzureCredential raises an exception when there is a token
            # found in the cache but the token has expired. In this case we catch the error and
            # initiate the an Interactive Browser flow if possible or fall back to the DeviceCode flow.
            logger.warning(f"Caught {e.__class__}: {e!s}! Falling back to Interactive Browser flow.")
            token = (
                AzureCredentialWithDevicecode(
                    authority=authority,
                    tenant_id=tenant_id,
                    with_az_cli=False
                )
                .get_token(scope)
                .token
            )
        return token

    def _exchange_bearer_for_pat(self, authority_endpoint: str, bearer_token: str) -> str:
        """Exchange the bearer token for a personal access token (PAT)."""
        try:
            # Build request headers
            request_headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
                "User-Agent": self._USER_AGENT,
            }

            # Build the request URL
            visual_studio_url = f"{authority_endpoint.rstrip('/')}/{self._TOKEN_API_ROUTE.lstrip('/')}"

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

                # Return the PAT token
                return response.json()["patToken"]["token"]

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

        # get username
        username = os.getenv(self._ADO_USERNAME_ENV_VAR, self._DEFAULT_USERNAME)
        # get authorities and tenant_id
        oauth_authority, tenant_id, vsts_authority = self._get_authorities(url)
        # get bearer token
        bearer_token = self._get_bearer_token(
            authority=oauth_authority,
            tenant_id=tenant_id,
            scope=self._OAUTH_SCOPE,
        )
        if os.getenv(self._USE_BEARER_TOKEN_VAR_NAME, "False").lower() == "true":
            return username, bearer_token

        # else exchange bearer token for PAT
        pat = self._exchange_bearer_for_pat(vsts_authority, bearer_token)
        return username, pat

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
        if os.environ.get(self._PAT_ENV_VAR) and os.getenv(self._USE_BEARER_TOKEN_VAR_NAME, "False").lower() == "false":
            # Return the username and password from the environment variables
            return os.getenv(self._ADO_USERNAME_ENV_VAR, self._DEFAULT_USERNAME), os.environ.get(self._PAT_ENV_VAR)

        # Getting credentials; the credentials may come from the cache
        username, password = self._get_credentials_from_credential_provider(url)

        # Do not attempt to validate if the credentials could not be obtained
        if username is None or password is None:
            return username, password

        # Make sure the credentials are still valid (i.e. not expired)
        if self._can_authenticate(url, (username, password)):
            return username, password

        # Return None if the credentials are invalid
        return None, None
