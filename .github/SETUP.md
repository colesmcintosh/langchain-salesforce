# GitHub Actions CI/CD Setup

This repository uses GitHub Actions for continuous integration and deployment. This document explains how to configure and use the CI/CD system.

## 📋 Overview

The CI/CD system includes several workflows:

- **`ci.yml`** - Main CI workflow that runs on all pushes and pull requests
- **`pr-checks.yml`** - Pull request validation workflow with status checks
- **`pr-comments.yml`** - Adds helpful comments to new pull requests

## 🔧 Workflows Explained

### Main CI Workflow (`ci.yml`)

Runs on every push to `main` and all pull requests. Includes:

- **Lint and Format Job**: Runs on Python 3.9, 3.10, and 3.11
  - Code formatting check (`ruff format --check`)
  - Import sorting check (`ruff check --select I`)
  - Linting (`ruff check`)
  - Type checking (`mypy`)

- **Test Job**: Runs unit tests on all supported Python versions
  - Unit tests with coverage reporting
  - Uploads coverage to Codecov (optional)

- **Integration Test Job**: Runs integration tests
  - Only on pushes to `main` or PRs with `integration-tests` label
  - Requires Salesforce credentials as secrets

- **Spell Check Job**: Checks spelling with codespell

### Pull Request Checks (`pr-checks.yml`)

Provides clear status checks for branch protection:

- **Code Quality**: All linting, formatting, and type checks
- **Unit Tests**: Test execution across Python versions  
- **PR Validation**: Combines results for branch protection

### PR Comments (`pr-comments.yml`)

Adds a welcome comment to new pull requests with:
- Overview of what will be checked
- Instructions for fixing issues
- Links to documentation

## ⚙️ Repository Setup

### 1. Branch Protection Rules

Configure branch protection for the `main` branch:

1. Go to **Settings** → **Branches**
2. Click **Add rule** for the `main` branch
3. Configure these settings:

```yaml
Branch name pattern: main

☑️ Restrict pushes that create files larger than 100MB
☑️ Require a pull request before merging
  ☑️ Require approvals (1)
  ☑️ Dismiss stale PR approvals when new commits are pushed
  ☑️ Require review from code owners (if you have CODEOWNERS)

☑️ Require status checks to pass before merging
  ☑️ Require branches to be up to date before merging
  
  Required status checks:
  - pr-validation
  - code-quality  
  - unit-tests (Python 3.9)
  - unit-tests (Python 3.10)
  - unit-tests (Python 3.11)

☑️ Restrict who can push to matching branches
  - Include administrators: ☐ (recommended)
```

### 2. Repository Secrets

Add these secrets in **Settings** → **Secrets and variables** → **Actions**:

#### Required for Integration Tests (Optional)
- `SALESFORCE_USERNAME` - Your Salesforce username
- `SALESFORCE_PASSWORD` - Your Salesforce password  
- `SALESFORCE_SECURITY_TOKEN` - Your Salesforce security token
- `SALESFORCE_DOMAIN` - Salesforce domain (`login` or `test`)

#### Optional for Coverage Reporting
- `CODECOV_TOKEN` - Token from codecov.io (optional)

### 3. Labels Setup

Create these labels for enhanced functionality:

- `integration-tests` - Triggers integration tests on PRs
- `breaking-change` - Indicates breaking changes
- `documentation` - For documentation-only changes

## 🚀 Usage

### For Contributors

#### Before Creating a PR
```bash
# Format code
make format

# Check for issues
make lint

# Run tests
make test
```

#### PR Workflow
1. Create a pull request
2. Automatic comment will be added with instructions
3. CI checks will run automatically
4. Fix any failing checks by pushing new commits
5. Request review once all checks pass

#### Running Integration Tests
- Add the `integration-tests` label to your PR
- Or push to the `main` branch (after merging)

### For Maintainers

#### Monitoring CI
- Check the **Actions** tab for workflow runs
- Failed checks will block PR merging (if branch protection is enabled)
- Review coverage reports and test results

#### Managing Integration Tests
- Integration tests require Salesforce credentials
- Only run on trusted contributions
- Consider running manually for external contributors

## 🔍 Troubleshooting

### Common CI Failures

#### Code Formatting Issues
```bash
# Fix formatting
make format

# Check what would be changed
poetry run ruff format . --diff
```

#### Linting Errors
```bash
# See all linting issues
make lint

# Auto-fix some issues
poetry run ruff check . --fix
```

#### Type Checking Errors
```bash
# Run mypy locally
mkdir -p .mypy_cache
poetry run mypy . --cache-dir .mypy_cache
```

#### Test Failures
```bash
# Run specific test file
make test TEST_FILE=tests/unit_tests/test_specific.py

# Run with verbose output
poetry run pytest -v tests/unit_tests/
```

### Debugging Workflows

1. **Check workflow logs** in the Actions tab
2. **Look for specific error messages** in failed steps
3. **Reproduce locally** using the same commands
4. **Check Python version compatibility** if tests pass locally

### Cache Issues

If dependencies seem outdated:
1. Go to **Actions** → **Caches**
2. Delete relevant caches
3. Re-run the workflow

## 📈 Metrics and Reporting

### Coverage Reports
- Unit test coverage is tracked automatically
- Coverage reports are generated in XML format
- Can be uploaded to Codecov for tracking over time

### Test Results
- JUnit XML files are generated for test results
- Artifacts are uploaded for each Python version
- Can be downloaded from the Actions tab

## 🔄 Continuous Deployment (Future)

This setup is ready to be extended with CD capabilities:

- **Release automation** on git tags
- **Package publishing** to PyPI
- **Documentation deployment** to GitHub Pages
- **Docker image building** and publishing

## 📝 Customization

### Adding New Checks

To add a new check to the CI pipeline:

1. Add the command to your `Makefile`
2. Add a step to the appropriate workflow job
3. Update branch protection rules if it should be required

### Modifying Python Versions

Update the matrix in both `ci.yml` and `pr-checks.yml`:

```yaml
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12"]  # Add new versions
```

### Environment-Specific Configs

Different environments can have different configurations:
- Use different secrets for staging vs production
- Modify workflow triggers based on branch patterns
- Add environment-specific test suites

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/) 