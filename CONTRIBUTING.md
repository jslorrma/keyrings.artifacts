# Contributing to this Project

We appreciate your interest in contributing to our project! This document provides guidelines to make the contribution process smooth and effective for everyone involved.

## Setting Up Your Development Environment

### Pixi package manager

We use [`pixi`](https://pixi.sh/latest/) as our project and package manager. `pixi` is a cross-platform, Python project and multi-language package manager as well as a workflow tool built on the foundation of the conda ecosystem. It provides developers with an experience similar to popular package managers like cargo or yarn, but for any language. Some of its key features include:

- Support for conda and PyPi packages, with global dependency resolution.
- Always includes an up-to-date lock file.
- Entirely written in Rust, making it super fast.

If you haven't installed `pixi` yet, either follow the installation instructions for your operating system:

- [Windows](https://pixi.sh/latest/#__tabbed_1_2)
- [Unix / MacOS](https://pixi.sh/latest/#__tabbed_1_1)

or use the provided installation scripts:

For more information on doing Python development with `pixi`, please refer to this [tutorial](https://pixi.sh/latest/tutorials/python/).


### Installing requirements

Pixi automatically manages virtual environments for this project, creating separate, incremental environments for default and development setups. Once you've cloned the repository and installed `pixi`, you can prepare the project by executing:

```bash
pixi install -e dev
pixi run post-install
```

> **Note**: The development environment is an incremental environment that includes the default environment (see the Pixi [documentation](https://pixi.sh/latest/reference/project_configuration/#the-environments-table) for more information).

for the development environment. You can run

```bash
pixi install
```

to install only the default environment.

> **Note**: In general you can also run `pixi install --all` to install all environments specified in the `pixi.toml` file (In this repository, it's the `default` and `dev` environment).

### Managing Python Dependencies with `Pixi`

`Pixi` streamlines the process of managing dependencies from both Conda and PyPI, ensuring a unified approach to dependency resolution across these ecosystems. Here's how you can efficiently manage your project's dependencies:

- **Adding Dependencies**: To add a new dependency to your project, use the command:

  ```bash
  pixi add <new-dependency>
  ```

  If you're specifying a dependency for development purposes, append `-f dev` to the command, like so: `pixi add -f dev <new-dependency>`.

- **Handling PyPI-Only Packages**: In cases where a required package is not available on Conda but is on PyPI, `Pixi` can still handle the addition seamlessly. Use the command:

  ```bash
  pixi add <new-dependency> --pypi
  ```

  to add PyPI dependencies.

## Contributing Code

We use the Gitflow Workflow for code contributions:

1. Clone the repository and create a new branch from `main` for your feature or fix.
2. Implement your changes and commit them, adhering to the commit message guidelines provided below.
3. Open a pull request to propose merging your branch into `main`.

Please note that the `main` branch is protected, meaning direct pushes are not allowed. All changes must be made through pull requests.

Here are some guidelines for naming your branches:

- **Descriptive Names**: Choose names that provide context for the branch's purpose. For example, use `feature/login` or `bugfix/navbar-overflow` instead of generic names.
- **Use Hyphens**: Separate words in the branch name with hyphens for readability. For example, `bugfix/fix-login-issue` is more readable than `bugfix/fixLoginIssue` or `bugfix/fix_login_issue`.
- **Alphanumeric Lowercase Characters**: Use only alphanumeric lowercase characters (a-z, 0–9) and hyphens. Avoid punctuation, spaces, underscores, or any special characters whenever possible.
- **Avoid Unnecessary Hyphens**: Do not use subsequent or trailing hyphens. For example, `feat/new--login-` is not recommended.
- **Short and Effective**: Keep branch names simple. While they should be descriptive, they should also be concise enough to convey the goal at a glance.

Some of the common branch type prefixes and their usage cases include:

- `feature/`: For developing new features.
- `bugfix/`: To fix bugs in the code. Often created associated with an issue.
- `hotfix/`: To fix critical bugs in production.
- `release/`: To prepare a new release, typically used to do tasks such as last touches and revisions.
- `docs/`: Used to write, modify, or correct documentation.

In addition, for larger features or changes that require a significant amount of time to develop, you can contribute to long-running development branches.

### Commit Best Practices

When making commits, please adhere to the following guidelines to maintain a clean and understandable commit history:

- **Commit Related Changes**: A commit should encapsulate related changes. If you're fixing two different bugs, for instance, produce two separate commits.
- **Commit Often**: Regular commits keep your changes small and ensure that each commit contains only related changes.
- **Don't Commit Half-Done Work**: Only commit code when a logical component is complete.
- **Test Before Committing**: Always test your code before committing. This helps ensure that the codebase remains stable and helps prevent the introduction of bugs.

#### Commit Messages

When crafting your commit messages, please follow these conventions:

- **Imperative Mood**: Create commit messages in the imperative mood (e.g., "Add feature", not "Added feature").
- **Type Prefix**: Use a type prefix in the subject line to represent the type of changes included in the commit. Some commonly used types are:
  - `feat:`: A new feature
  - `fix:`: A bug fix
  - `build:`, `chore:`, `ci:`, `style:`, `refactor:`: Other types of changes
- **Summary**: Begin your message with a short summary of your changes (up to 50 characters as a guideline). Separate it from the following body by including a blank line.

## Testing

We use `pytest` for testing our Python code. Here are some guidelines for writing and running tests:

- **Write Tests for New Code**: If you're adding a new feature or fixing a bug, please add corresponding tests. This helps ensure that your code works correctly and prevents future changes from unintentionally breaking your feature or fix.

- **Run Tests Before Submitting a Pull Request**: Before you submit a pull request, please run the test suite to make sure your changes didn't break any existing functionality. You can run the tests with the following command:

```bash
pixi run -e dev test
```

- **Include Detailed Test Descriptions**: Each test should include a description of what it's testing and what the expected results are.

- **Use Assertions**: Use assertions to validate that the code behaves as expected.

- **Keep Tests Simple and Focused**: Each test should focus on a single functionality or scenario.

If you're new to `pytest`, you might find the [official `pytest` documentation](https://docs.pytest.org/en/latest/) helpful. Additionally, you can watch this informative [PyConDE 2023 tutorial on `pytest`](https://www.youtube.com/watch?v=ofPHJrAOaTE) to learn more about writing and executing tests.

## Issue Reporting Guidelines

When reporting issues, please follow these guidelines to help maintain an effective and organized issue tracker:

- **Check Existing Issues**: Before creating a new issue, please check the existing issues to avoid duplicates. If an issue already exists for your problem or suggestion, feel free to add any additional information in the comments.

- **Use a Clear and Descriptive Title**: Issue titles should be descriptive and give a clear idea of what the issue is about. For example, "Application crashes on login" is more helpful than "Application crashes".

- **Describe the Issue in Detail**: In the issue description, include as much relevant information as possible. Explain the problem and include additional details to help maintainers reproduce the issue. If it's a bug, include steps to reproduce it, the expected behavior, and the actual behavior. If it's a feature request, explain what you're trying to achieve and why.

- **Include Screenshots or GIFs**: If applicable, add screenshots or GIFs to help explain your problem.

- **Include System Information**: If it's a bug, include information about your environment such as your OS, browser version, and any other relevant software versions.

- **Use Labels Appropriately**: If possible, use labels to categorize your issue. This helps maintainers and other contributors identify and prioritize issues.

Remember, the more information you provide, the easier it is for others to understand and resolve the issue.
