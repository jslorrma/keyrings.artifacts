# Keyring for Azure DevOps Artifacts

[![GitHub branch check runs](https://img.shields.io/github/check-runs/jslorrma/keyrings.artifacts/main?style=flat-square&logo=GitHub&label=CI)](https://github.com/jslorrma/keyrings.artifacts/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/keyrings.artifacts.svg?label=PyPi%20version&style=flat-square)](https://badge.fury.io/py/keyrings.artifacts)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/keyrings.artifacts?label=PyPi%20downloads&style=flat-square)](https://pypi.org/project/keyrings.artifacts/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/keyrings.artifacts?style=flat-square&label=Conda%20version&color=104F8B
)](https://prefix.dev/channels/conda-forge/packages/keyrings.artifacts)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/keyrings.artifacts.svg?label=Conda%20downloads&color=104F8B&style=flat-square)](
https://prefix.dev/channels/conda-forge/packages/keyrings.artifacts)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/keyrings.artifacts?style=flat-square)](https://pypi.org/project/keyrings.artifacts/)
[![License](https://img.shields.io/github/license/jslorrma/keyrings.artifacts?style=flat-square)](LICENSE)
[![Pixi Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json&style=flat-square)](https://pixi.sh)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)

## Overview

The `keyrings.artifacts` backend integrates with the `keyring` library to provide authentication for publishing or consuming Python packages to or from Azure Artifacts feeds within [Azure DevOps](https://azure.com/devops). The package is a platform-agnostic, plain Python implementation of the original [artifact-keyring](https://github.com/Microsoft/artifacts-keyring) package leverageging [azure-identity](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python), without its dependency on `DotNet`.

The package is designed to be used with the [`pixi`](https://pixi.sh/latest/), [`uv`](https://docs.astral.sh/uv/) or [`pip`](https://pip.pypa.io/en/stable/) package manager to authenticate with Azure DevOps Artifacts. It provides a secure and convenient way to store and retrieve credentials without exposing them in the source code or local configuration files.

## Disclaimer

**Warning:** This package is in an early development stage and may contain bugs or other issues. It is recommended to use this package for local development and testing purposes only, and not in production environments or CI pipelines. Please report any issues or bugs you encounter to help us improve the package.

## Acknowledgements

This package was heavily inspired by a pull request of [tomporaer](https://github.com/temporaer) and [javuc1](https://github.com/javuc1) in Microsoft's `artifacts-keyring` repository and their [idea of a plain Python version]((https://github.com/microsoft/artifacts-keyring/pull/56)). Since the PR has not been merged since February 2023, it seems unlikely that it will be merged, which led to the decision to create this package.

## Installation

Detailed documentation on how to setup the usage can be found in the respective package manager documentation:

> **Note:** As the `keyrings.artifacts` package is a drop-in replacement for the original `artifact-keyring` package and it supports the same methods (and more). To use the `keyrings.artifacts` package, follow the same installation and configuration instructions provided in the listed documentations below, but replace the package name accordingly.

- `pip` is available in the [pip documentation](https://pip.pypa.io/en/stable/topics/authentication/#using-keyring-as-a-command-line-application).
- `pixi` is available in the [Pixi documentation](https://pixi.sh/latest/advanced/authentication/#installing-keyring) section.
- `uv` is available in the [uv documentation](https://docs.astral.sh/uv/guides/integration/alternative-indexes/#using-keyring).


### System-Wide Installation

Following the installation and configuration instructions in the pip documentation, keyring and third-party backends should best be installed system-wide. The simplest way to install the `keyring` with `keyrings.artifacts`-backend system-wide is to use `uv` (If don't know `uv` yet, I suggest you to check it out [here](https://docs.astral.sh/uv/)), `pipx` and `pixi` (not yet supported - see notes below):

### uv
```bash
# Install keyring and the keyrings.artifacts from PyPI using uv
uv tool install keyring --with keyrings.artifacts
```

### pipx
```bash
# Install keyring from PyPI using pipx
$ pipx install keyring --index-url https://pypi.org/simple

# Inject the keyrings.artifacts package
$ pipx inject keyring keyrings.artifacts --index-url https://pypi.org/simple
```

### pixi

> **Note:** `pixi` cannot be used yet because the `keyrings.artifacts` package is not available from conda-forge channel yet and `pixi global install` does not support installations from PyPI yet.

> **Note:** `pixi` does not yet support global multi-package installations (it's planned for the future, see the [Pixi Global Manifest](https://pixi.sh/dev/design_proposals/pixi_global_manifest/)). To work around this, since `keyrings.artifacts` depends on `keyring`, you need to globally install `keyrings.artifacts` and then link the `keyring` executable to the `pixi` bin directory.

```bash
# Install keyrings.artifacts globally and link the keyring executable
pixi global install keyrings.artifacts && ln -s ~/.pixi/envs/artifacts-keyring/bin/keyring ~/.pixi/bin/
```

## Usage

### Command Line

If you don't have a token stored in the system keyring, you can fetch and store it interactively using the `keyring` command line tool:

```bash
$ keyring get https://pkgs.dev.azure.com/{organization}/{project}/_packaging/{feed}/pypi/simple/ VssSessionToken
```

If you already have a token stored in the system keyring and want to update it, you can use the `keyring` command line tool:

```bash
# first delete the existing token
$ keyring del https://pkgs.dev.azure.com/{organization}/{project}/_packaging/{feed}/pypi/simple/ VssSessionToken
# then fetch and store the new token
$ keyring get https://pkgs.dev.azure.com/{organization}/{project}/_packaging/{feed}/pypi/simple/ VssSessionToken
```

> **Note:** `keyrings.artifacts` package handles the token refresh of expired tokens automatically, so you don't need to worry about it. 🤓

## How It Works

The `keyrings.artifacts` package extends the `keyring` library to securely manage credentials for Azure DevOps Artifacts. It supports authentication using either bearer tokens or personal access tokens (PATs), configurable via the `KEYRINGS_ARTIFACTS_USE_BEARER_TOKEN` environment variable (default is `False`).

#### Authentication Methods

The package supports two authentication methods:

1. **Bearer Token Authentication**:
    Set `KEYRINGS_ARTIFACTS_USE_BEARER_TOKEN` to `True` to use bearer tokens.
    Authentication methods for obtaining a bearer token include:
    - Using environment variables for the `EnvironmentCredential` provider. This provider is capable of authenticating as a service principal using a client secret or a certificate, or as a user with a username and password, and requires setting a few environment variables. [Learn more](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.environmentcredential?view=azure-python)
    - Requesting a token from the Azure CLI (requires prior `az login`). [Learn more](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.azureclicredential?view=azure-python)
    - Shared token cache. [Learn more](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.sharedtokencachecredential?view=azure-python)
    - Interactive browser-based authentication. [Learn more](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python)
    - Device code authentication. [Learn more](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.devicecodecredential?view=azure-python)


2. **Personal Access Token (PAT) Authentication**:
    To use a personal access token (PAT), set `KEYRINGS_ARTIFACTS_USE_BEARER_TOKEN` to `False`. The package will automatically manage the PAT as follows:
    - If the `AZURE_DEVOPS_EXT_PAT` environment variable is set, this token will be used.
    - If `AZURE_DEVOPS_EXT_PAT` is not set, the package will look for a stored PAT in the system keyring.
    - If no PAT is found, a new PAT will be generated and stored in the system keyring. The duration of the PAT can be configured using the `AZURE_DEVOPS_PAT_DURATION` environment variable (default is 365 days).

      > **Note:** To generate a new PAT, an intermediate bearer token authentication is required. The bearer token can be obtained using any of the methods mentioned [above](#authentication-methods).

    Any new PAT will be stored in the system keyring for future use. Depending on the operating system, the following keyrings are used:
    - **Windows**: Stored in Windows Credential Manager.
    - **macOS**: Stored in macOS Keychain.
    - **Linux**: Stored in the Secret Service API via `dbus` or in an encrypted file using `keyrings.alt.EncryptedKeyring`.

    > **Note:** For more information on setting up and configuring system keyrings, refer to the [keyring documentation](https://keyring.readthedocs.io/en/latest/).

### Configuration Guidelines

#### Environment Variables

1. General Configuration:

   - `KEYRINGS_ARTIFACTS_USE_BEARER_TOKEN`: Set to `True` to use bearer tokens, `False` to use PATs (default is `False`).

2. Personal Access Token (PAT) Configuration:

   - `AZURE_DEVOPS_EXT_PAT`: This environment variable can be used to set a PAT for the package to use.
   - `AZURE_DEVOPS_PAT_DURATION`: If a new PAT is generated, this environment variable sets the duration of the PAT in days (default is 365 days).

3. Bearer Token Configuration:

   - Details about the environment variables required for the `EnvironmentCredential` provider can be found in the [Azure Identity documentation](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.environmentcredential?view=azure-python).


---

## Contributing

We welcome contributions to this project. Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get involved.


### Pixi package manager

We use `pixi` as our project and package manager. `pixi` is a cross-platform, multi-language package manager and workflow tool built on the foundation of the conda ecosystem. It provides developers with an experience similar to popular package managers like cargo or yarn, but for any language. Some of its key features include:

- Support for conda and PyPi packages, with global dependency resolution.
- Always includes an up-to-date lock file.
- Entirely written in Rust, making it super fast.

For more information on doing Python development with `pixi`, please refer to this [tutorial](https://pixi.sh/latest/tutorials/python/).

### Installing requirements

Once you've cloned the repository, you can prepare the project by executing:

```bash
pixi install -e dev
pixi run post-install
```

These commands install the necessary packages, set up the pre-commit hooks, and prepare the project for development. Verify the installation by running

```bash
pixi list
```

You should see the packages installed in the list.

For more detailed instructions on setting up your environment, including the use of the `pixi` package manager, refer to the [Setting Up Your Development Environment](CONTRIBUTING.md#setting-up-your-development-environment) section in `CONTRIBUTING.md`.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
