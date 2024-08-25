#!/usr/bin/env python3
"""
keyrings_artifacts/support.py
---------------------------

It provides the AzureCredentialWithDevicecode class which extends ChainedTokenCredential to support
the following credential types:
    - AzureCliCredential
    - DefaultAzureCredential
    - ManagedIdentityCredential
    - SharedTokenCacheCredential
    - DeviceCodeCredential
"""

from __future__ import annotations

__author__ = "jslorrma"
__maintainer__ = "jslorrma"
__email__ = "jslorrma@gmail.com"

import os
import webbrowser
from typing import Any

from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    DeviceCodeCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
    SharedTokenCacheCredential,
)

# Azure DevOps application default scope
# from https://github.com/microsoft/artifacts-credprovider/blob/cdc427e8236212b33041b4276961855b39bbe98d/CredentialProvider.Microsoft/CredentialProviders/Vsts/MSAL/MsalTokenProviderFactory.cs#L11
DEFAULT_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"


class AzureCredentialWithDevicecode(ChainedTokenCredential):
    """
    A credential chain that is composed of multiple credentials.

    The following credential types are chained:
    - EnvironmentCredential
    - AzureCliCredential
    - SharedTokenCacheCredential
    - InteractiveBrowserCredential
    - DeviceCodeCredential

    Parameters
    ----------
    tenant_id : str, optional
        Tenant id to include in the token request.
    authority : str, optional
        Authority for the token request.
    additionally_allowed_tenants : list of str, optional
        Additional tenants to include in the token request.
    process_timeout : int, optional
        Timeout in seconds for the device code authentication process. Default is 90 seconds.
    scope : str, optional
        The scope for the token request. Default is "499b84ac-1321-427f-aa17-267ca6975798/.default".
        (From https://github.com/microsoft/artifacts-credprovider/blob/cdc427e8236212b33041b4276961855b39bbe98d/CredentialProvider.Microsoft/CredentialProviders/Vsts/MSAL/MsalTokenProviderFactory.cs#L11)
    with_az_cli : bool, optional
        Whether to include the Azure CLI credential in the chain. Default is True.
    """

    def __init__(  # noqa: PLR0913
        self,
        tenant_id: str = "",
        authority: str = "",
        additionally_allowed_tenants: list[str] | None = None,
        process_timeout: int = 180,
        scope: str = DEFAULT_SCOPE,
        with_az_cli: bool = True,
    ):
        self.scope = scope
        cred_chain = [
            *[
                # add environment credential if mandatory environment variable "AZURE_CLIENT_ID"
                # is set. EnvironmentCredential supports authenticating with service principal using
                # client secret, certificate, and managed identity. All three options require
                # AZURE_CLIENT_ID to be set.
                EnvironmentCredential() if os.getenv("AZURE_CLIENT_ID") else []
            ],
            *[
                AzureCliCredential(
                    tenant_id=tenant_id,
                    additionally_allowed_tenants=additionally_allowed_tenants,
                )
                # add Azure CLI credential if with_az_cli is True and tenant_id is set. If tenant_id
                # is not set, the Azure DevOps organization seems to a personal Microsoft account
                # without an Azure subscription, so the Azure CLI credential cannot be used.
                if with_az_cli and tenant_id
                else []
            ],
            SharedTokenCacheCredential(
                exclude_environment_credential=False,
                exclude_managed_identity_credential=True,
                authority=authority,
            ),
            *[
                InteractiveBrowserCredential(
                    tenant_id=tenant_id
                )
                # add interactive browser credential if a browser is available
                if self._is_interactive_browser_possible()
                else []
            ],
            DeviceCodeCredential(
                tenant_id=tenant_id,
                process_timeout=process_timeout,
            ),
        ]

        super().__init__(*(cred for cred in cred_chain if cred))

    def _is_interactive_browser_possible(self):
        """Check if the interactive browser credential is possible."""
        try:
            webbrowser.get()
            return True
        except webbrowser.Error:
            return False

    def get_token(self, *scopes: str, **kwargs):
        """
        Get an access token for the specified scopes.

        Parameters
        ----------
        scopes : str
            The scopes for the token request.
        kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        AccessToken
            The access token.
        """
        if not scopes:
            scopes = (self.scope,)
        return super().get_token(*scopes, **kwargs)

    def __enter__(self) -> AzureCredentialWithDevicecode:
        return self

    def __exit__(self, *args: Any) -> None:
        pass
