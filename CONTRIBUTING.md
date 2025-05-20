# Contributing to langchain-salesforce

First off, thank you for considering contributing to `langchain-salesforce`! Your help is greatly appreciated.

This document provides guidelines for contributing to this project. Please read it carefully to ensure a smooth and effective contribution process.

## Table of Contents

-   [How Can I Contribute?](#how-can-i-contribute)
    -   [Reporting Bugs](#reporting-bugs)
    -   [Suggesting Enhancements](#suggesting-enhancements)
    -   [Pull Requests](#pull-requests)
-   [Development Setup](#development-setup)
-   [Coding Standards](#coding-standards)
-   [Running Tests](#running-tests)
-   [Pull Request Process](#pull-request-process)
-   [Code of Conduct](#code-of-conduct)

## How Can I Contribute?

### Reporting Bugs

If you encounter a bug, please open an issue on our GitHub repository. When reporting a bug, please include:

-   A clear and descriptive title.
-   A detailed description of the problem, including steps to reproduce the bug.
-   The version of `langchain-salesforce` you are using.
-   Your Python version.
-   Any relevant error messages or stack traces.
-   Your operating system and version.

Providing as much information as possible will help us to quickly identify and fix the issue.

### Suggesting Enhancements

If you have an idea for a new feature or an improvement to an existing one, please open an issue on GitHub. Describe your suggestion in detail, including:

-   A clear and descriptive title.
-   A comprehensive explanation of the proposed enhancement.
-   The use case or problem this enhancement would solve.
-   Any potential drawbacks or alternative solutions.

We welcome all suggestions and will review them carefully.

### Pull Requests

We actively welcome your pull requests.

1.  Fork the repository and create your branch from `main` (or the relevant development branch).
2.  If you've added code that should be tested, add tests.
3.  If you've changed APIs, update the documentation.
4.  Ensure the test suite passes (`make test`).
5.  Make sure your code lints (`make lint`).
6.  Issue that pull request!

## Development Setup

Please refer to the [Development section in the README.md](README.md#development) for instructions on how to set up your development environment, install dependencies, and run linters/tests.

## Coding Standards

-   **Formatting**: Please ensure your code adheres to the project's formatting standards. Run `make lint` (which often includes formatters like Black and Flake8) before committing your changes.
-   **Type Hinting**: Use Python type hints for all function signatures and variables where appropriate.
-   **Docstrings**: Write clear and concise docstrings for all public modules, classes, and functions.
-   **Commit Messages**: Follow conventional commit message formats if possible (e.g., `feat: add new feature X`, `fix: resolve bug Y`).

## Running Tests

To ensure your changes haven't broken anything, please run the test suite:

```bash
make test
```

All tests must pass before a pull request can be merged.

## Pull Request Process

1.  Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2.  Update the `README.md` with details of changes to the interface, this includes new environment variables, new or changed command line arguments, new or changed API methods etc.
3.  Increase the version numbers in any examples files and the `README.md` to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4.  You may merge the Pull Request in once you have the sign-off of at least one other developer, or if you do not have permission to do that, you may request the reviewer to merge it for you.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md) (TODO: Create CODE_OF_CONDUCT.md or link to an existing one, e.g., Contributor Covenant). By participating, you are expected to uphold this code. Please report unacceptable behavior.

---

Thank you for your contribution! 