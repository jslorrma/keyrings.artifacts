# Keyring for Azure DevOps Artifacts

[![Build Status](https://dev.azure.com/bitcraze/Bitcraze/_apis/build/status/bitcraze.keyrings.artifacts?branchName=main)](https://dev.azure.com/bitcraze/Bitcraze/_build/latest?definitionId=1&branchName=main)
[![PyPI version](https://badge.fury.io/py/keyrings.artifacts.svg)](https://badge.fury.io/py/keyrings.artifacts)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/keyrings.artifacts)](https://pypi.org/project/keyrings.artifacts/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/keyrings.artifacts)](https://pypi.org/project/keyrings.artifacts/)
[![PyPI - License](https://img.shields.io/pypi/l/keyrings.artifacts)](https://pypi.org/project/keyrings.artifacts/)

## Overview

The `keyrings.artifacts` package provides a secure and efficient way to manage credentials for Azure DevOps Artifacts. It includes a keyring backend that supports various authentication methods and stores credentials in an encrypted file. The package is a platform-agnostic, plain Python implementation of the original [artifact-keyring](https://github.com/Microsoft/artifacts-keyring) package, without its dependency on `DotNet`.

The package is designed to be used with the [`pixi`](https://pixi.sh/latest/), [`uv`](https://docs.astral.sh/uv/) or [`pip`](https://pip.pypa.io/en/stable/)package manager to authenticate with Azure DevOps Artifacts. It provides a secure and convenient way to store and retrieve credentials without exposing them in the source code or local configuration files.

Detailed documentation on how to setup the usage can be found in the respective package manager documentation:

> **Note:** As the `keyrings.artifacts` package is a drop-in replacement for the original `artifact-keyring` package, the usage is the same. The only difference is the package name and the installation method (see [below](#installation)).

- `pip` is available in the [pip documentation](https://pip.pypa.io/en/stable/topics/authentication/#using-keyring-as-a-command-line-application).
- `pixi` is available in the [Pixi documentation](https://pixi.sh/latest/advanced/authentication/#installing-keyring) section.
- `uv` is available in the [uv documentation](https://docs.astral.sh/uv/guides/integration/alternative-indexes/#using-keyring).


# Installation

Following the installation and configuration instructions in the pip documentation, keyring and third-party backends should best be installed system-wide. The simplest way to install the `keyrings.artifacts` package system-wide is to use `uv` (If don't know `uv` yet, I suggest you to check it out [here](https://docs.astral.sh/uv/)) or `pipx`:

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


----

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
